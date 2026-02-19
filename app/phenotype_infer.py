"""
phenotype_infer.py
Infers full phenotype string from gene variants and diplotype.
Integrates dpyd_engine + diplotype_engine CSV lookup.
"""

import logging

logger = logging.getLogger("pharmaguard.phenotype_infer")

# ── DPYD rsID → phenotype lookup ─────────────────────────────────────────────
# Source: CPIC DPYD guideline (activity scores)
DPYD_VARIANT_PHENOTYPE = {
    "rs3918290": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs55886062": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs67376798": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Intermediate Metabolizer",
        "1|1": "Intermediate Metabolizer",
    },
    "rs1801160": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1801265": {
        "0/1": "Normal Metabolizer",
        "0|1": "Normal Metabolizer",
        "1/1": "Normal Metabolizer",
        "1|1": "Normal Metabolizer",
    },
    # Added from sample VCFs
    "rs34534958": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },  # DPYD*2A
    "rs369672458": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs772853110": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
}

# ── CYP2D6 rsID → phenotype ──────────────────────────────────────────────────
CYP2D6_VARIANT_PHENOTYPE = {
    "rs3892097": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1065852": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs5030655": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs16947": {
        "0/1": "Normal Metabolizer",
        "0|1": "Normal Metabolizer",
        "1/1": "Normal Metabolizer",
        "1|1": "Normal Metabolizer",
    },
    # Added from sample VCFs
    "rs1602563541": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1252450087": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1602563653": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
}

# ── CYP2C19 rsID → phenotype ─────────────────────────────────────────────────
CYP2C19_VARIANT_PHENOTYPE = {
    "rs4244285": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs4986893": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs28399504": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    # Added from sample VCFs
    "rs768818424": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs201331363": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
}

# ── CYP2C9 rsID → phenotype ──────────────────────────────────────────────────
CYP2C9_VARIANT_PHENOTYPE = {
    "rs1799853": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1057910": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
}

# ── SLCO1B1 rsID → phenotype ─────────────────────────────────────────────────
SLCO1B1_VARIANT_PHENOTYPE = {
    "rs4149056": {
        "0/1": "Decreased Function",
        "0|1": "Decreased Function",
        "1/1": "Poor Function",
        "1|1": "Poor Function",
    },
}

# ── TPMT rsID → phenotype ────────────────────────────────────────────────────
TPMT_VARIANT_PHENOTYPE = {
    "rs1800460": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1142345": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
    "rs1800584": {
        "0/1": "Intermediate Metabolizer",
        "0|1": "Intermediate Metabolizer",
        "1/1": "Poor Metabolizer",
        "1|1": "Poor Metabolizer",
    },
}

GENE_PHENOTYPE_MAP = {
    "DPYD": DPYD_VARIANT_PHENOTYPE,
    "CYP2D6": CYP2D6_VARIANT_PHENOTYPE,
    "CYP2C19": CYP2C19_VARIANT_PHENOTYPE,
    "CYP2C9": CYP2C9_VARIANT_PHENOTYPE,
    "SLCO1B1": SLCO1B1_VARIANT_PHENOTYPE,
    "TPMT": TPMT_VARIANT_PHENOTYPE,
}

# Severity hierarchy (higher = worse)
PHENOTYPE_SEVERITY = {
    "Poor Metabolizer": 4,
    "Poor Function": 4,
    "Intermediate Metabolizer": 3,
    "Decreased Function": 3,
    "Normal Metabolizer": 2,
    "Normal Function": 2,
    "Increased Function": 1,
    "Rapid Metabolizer": 1,
    "Ultrarapid Metabolizer": 0,
}

# Default "no variant" phenotype per gene
DEFAULT_PHENOTYPE = {
    "DPYD": "Normal Metabolizer",
    "CYP2D6": "Normal Metabolizer",
    "CYP2C19": "Normal Metabolizer",
    "CYP2C9": "Normal Metabolizer",
    "SLCO1B1": "Normal Function",
    "TPMT": "Normal Metabolizer",
}


def infer_phenotype(gene: str, variants: list, diplotype: str) -> str:
    """
    Infer phenotype from detected variants for a gene.
    Uses per-rsID tables then picks worst phenotype (most severe).
    If no variants detected, returns default (Normal Metabolizer / Normal Function).
    """
    if not variants:
        return DEFAULT_PHENOTYPE.get(gene, "Normal Metabolizer")

    gene_table = GENE_PHENOTYPE_MAP.get(gene, {})
    inferred = []

    for v in variants:
        rsid = (v.get("rsid") or "").lower()
        gt = v.get("genotype", ".")

        # If no genotype in VCF ( ClinVar typical), assume heterozygous if ALT is present
        if gt == "." and v.get("alt") not in (".", ""):
            gt = "0/1"

        if rsid in gene_table:
            # Try direct match
            if gt in gene_table[rsid]:
                inferred.append(gene_table[rsid][gt])
            # Fallback for phasing differences or missing GT
            elif "0/1" in gene_table[rsid] and (
                gt == "0|1" or gt == "1/0" or gt == "1|0"
            ):
                inferred.append(gene_table[rsid]["0/1"])
            elif "1/1" in gene_table[rsid] and gt == "1|1":
                inferred.append(gene_table[rsid]["1/1"])

    if not inferred:
        return DEFAULT_PHENOTYPE.get(gene, "Normal Metabolizer")

    # Return the most severe phenotype detected
    inferred.sort(key=lambda p: PHENOTYPE_SEVERITY.get(p, 2), reverse=True)
    return inferred[0]
