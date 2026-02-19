"""
vcf_parser.py
Strict VCF v4.2 parser for pharmacogenomic variants.
Accepts raw bytes (from FastAPI UploadFile) or file path.
"""

import io
import os
import logging

logger = logging.getLogger("pharmaguard.vcf")

# Known pharmacogenomic rsID → gene mapping (fallback)
RSID_TO_GENE = {
    # CYP2D6
    "rs3892097": "CYP2D6",
    "rs1065852": "CYP2D6",
    "rs5030655": "CYP2D6",
    "rs16947": "CYP2D6",
    # CYP2C19
    "rs4244285": "CYP2C19",
    "rs4986893": "CYP2C19",
    "rs28399504": "CYP2C19",
    "rs56337013": "CYP2C19",
    # CYP2C9
    "rs1799853": "CYP2C9",
    "rs1057910": "CYP2C9",
    "rs28371686": "CYP2C9",
    "rs9923231": "CYP2C9",
    # SLCO1B1
    "rs4149056": "SLCO1B1",
    "rs2306283": "SLCO1B1",
    # TPMT
    "rs1800460": "TPMT",
    "rs1142345": "TPMT",
    "rs1800584": "TPMT",
    # DPYD
    "rs3918290": "DPYD",
    "rs55886062": "DPYD",
    "rs67376798": "DPYD",
    "rs1801160": "DPYD",
    "rs1801265": "DPYD",
}

SUPPORTED_GENES = {"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"}

VALID_GENOTYPES = {"0/1", "1/1", "0|1", "1|1", "0/0", "1/0", "1|0"}


def _parse_lines(lines):
    """
    Core parser: takes an iterable of text lines, returns result dict.
    """
    result = {
        "variants": [],
        "vcf_parsing_success": True,
        "vcf_version": None,
        "error": None,
    }

    version_found = False
    chrom_header_found = False

    for raw_line in lines:
        line = raw_line.rstrip("\n\r")

        # ── Meta lines ──
        if line.startswith("##"):
            if line.startswith("##fileformat="):
                version = line.split("=", 1)[1].strip()
                result["vcf_version"] = version
                # Accept VCFv4.1, VCFv4.2, VCFv4.3
                if version.startswith("VCFv4"):
                    version_found = True
                else:
                    result["vcf_parsing_success"] = False
                    result["error"] = (
                        f"Unsupported VCF version: {version}. Expected VCFv4.x"
                    )
                    return result
            continue

        # ── Column header ──
        if line.startswith("#CHROM"):
            if not version_found:
                result["vcf_parsing_success"] = False
                result["error"] = (
                    "VCF header missing ##fileformat line. Not a valid VCF file."
                )
                return result
            chrom_header_found = True
            continue

        # ── Skip if no header yet ──
        if not chrom_header_found:
            continue

        # ── Data lines ──
        if not line.strip():
            continue

        columns = line.split("\t")
        if len(columns) < 8:
            continue  # malformed row, skip

        chrom = columns[0]
        pos = columns[1]
        rsid = columns[2]
        ref = columns[3]
        alt = columns[4]
        info_raw = columns[7]

        # Genotype (column 9, optional)
        genotype = None
        if len(columns) >= 10:
            gt_field = columns[9].split(":")[0]
            if gt_field in VALID_GENOTYPES:
                genotype = gt_field

        # Only include variants with ALT (skip ref-only)
        if alt in (".", "") and genotype in ("0/0", "0|0", None):
            continue

        # ── Parse INFO ──
        info_dict = {}
        for item in info_raw.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                info_dict[k.strip()] = v.strip()
            else:
                info_dict[item.strip()] = True

        # ── Gene resolution ──
        gene = info_dict.get("GENE") or info_dict.get("gene")

        if not gene:
            geneinfo = info_dict.get("GENEINFO") or info_dict.get("ANN", "")
            if geneinfo and ":" in str(geneinfo):
                gene = str(geneinfo).split(":")[0]

        if not gene and rsid and rsid != ".":
            gene = RSID_TO_GENE.get(rsid.lower()) or RSID_TO_GENE.get(rsid)

        # Map common aliases or neighbors
        if gene and gene.upper() == "EXOC6":
            gene = "CYP2C19"

        if not gene:
            continue  # cannot identify gene, skip

        # Filter to supported PGx genes only
        gene = gene.upper().strip()
        if gene not in SUPPORTED_GENES:
            continue

        # ── Star allele from INFO ──
        star = info_dict.get("STAR") or info_dict.get("star") or "."

        # ── RS ID normalization ──
        # Prefer RS ID from INFO if available (standard format), else use column 3
        if "RS" in info_dict:
            rsid = f"rs{info_dict['RS']}"
        elif rsid == "." and "RS" in info_dict:
            rsid = f"rs{info_dict['RS']}"

        variant = {
            "gene": gene,
            "rsid": rsid,
            "chrom": chrom,
            "position": pos,
            "ref": ref,
            "alt": alt,
            "genotype": genotype or ".",
            "star": star,
        }
        result["variants"].append(variant)
        logger.debug("Variant detected: %s", variant)

    if not chrom_header_found and version_found:
        result["vcf_parsing_success"] = False
        result["error"] = "VCF file has no data lines or missing #CHROM header."
        return result

    if not version_found:
        result["vcf_parsing_success"] = False
        result["error"] = "VCF file does not contain a valid ##fileformat line."
        return result

    logger.info(
        "VCF parsed: %d pharmacogenomic variants found", len(result["variants"])
    )
    return result


def parse_vcf_bytes(raw_bytes: bytes) -> dict:
    """Parse VCF from bytes (e.g., FastAPI UploadFile content)."""
    try:
        text = raw_bytes.decode("utf-8", errors="replace")
        lines = text.splitlines()
        return _parse_lines(lines)
    except Exception as exc:
        logger.exception("VCF byte parsing error")
        return {"variants": [], "vcf_parsing_success": False, "error": str(exc)}


def parse_vcf(file_path: str) -> dict:
    """Parse VCF from a file path (used by CLI / legacy code)."""
    if not os.path.exists(file_path):
        return {
            "variants": [],
            "vcf_parsing_success": False,
            "error": f"File not found: {file_path}",
        }
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            return _parse_lines(fh)
    except Exception as exc:
        logger.exception("VCF file parsing error")
        return {"variants": [], "vcf_parsing_success": False, "error": str(exc)}
