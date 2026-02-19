"""
diplotype_engine.py – Upgraded
Loads CPIC CSV tables at startup and resolves star-allele diplotypes.
"""

import os
import logging

logger = logging.getLogger("pharmaguard.diplotype")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

DIPLOTYPE_TABLES: dict = {}


def load_all_tables():
    """Load all CSV diplotype tables from data/ directory into memory."""
    global DIPLOTYPE_TABLES
    if not os.path.isdir(DATA_PATH):
        logger.warning("Data path not found: %s", DATA_PATH)
        return

    try:
        import pandas as pd
    except ImportError:
        logger.warning("pandas not installed – diplotype CSV lookup disabled")
        return

    for fname in os.listdir(DATA_PATH):
        if not fname.endswith(".csv"):
            continue
        gene = fname.split("_")[0].upper()
        fpath = os.path.join(DATA_PATH, fname)
        try:
            df = pd.read_csv(fpath, low_memory=False)
            df.columns = df.columns.str.strip()
            DIPLOTYPE_TABLES[gene] = df
            logger.info("Loaded diplotype table: %s (%d rows)", gene, len(df))
        except Exception as exc:
            logger.warning("Failed to load %s: %s", fname, exc)

    logger.info("Diplotype tables ready: %s", list(DIPLOTYPE_TABLES.keys()))


def resolve_diplotype(gene: str, variants: list) -> str:
    """
    Build a human-readable diplotype string from detected variants.
    Uses STAR allele from INFO field if present, otherwise rsID-based.
    Format: *1/*4A or rs1801265/rs3918290 etc.
    """
    if not variants:
        return "*1/*1"  # Default wild-type

    stars = []
    rsids = []

    for v in variants:
        star = v.get("star", ".")
        rsid = v.get("rsid", ".")
        gt   = v.get("genotype", "0/1")

        if star and star not in (".", ""):
            stars.append(star)
        elif rsid and rsid != ".":
            rsids.append(rsid)

    if stars:
        if len(stars) == 1:
            # Heterozygous: *1/*X
            return f"*1/{stars[0]}"
        return f"{stars[0]}/{stars[1]}"

    if rsids:
        return f"*1(ref)/{rsids[0]}"

    return "*1/*1"