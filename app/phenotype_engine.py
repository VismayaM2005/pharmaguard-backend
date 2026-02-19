"""
phenotype_engine.py – Upgraded
Returns CPIC recommendations and maps phenotype to short codes.
"""

import logging
from clinical_data import (
    CODEINE_CYP2D6,
    CLOPIDOGREL_CYP2C19,
    SIMVASTATIN_SLCO1B1,
    AZATHIOPRINE_TPMT,
    FLUOROURACIL_DPYD,
    WARFARIN_CYP2C9,
)

logger = logging.getLogger("pharmaguard.phenotype")

# CPIC standard short codes
PHENOTYPE_SHORT_CODES = {
    "Poor Metabolizer":          "PM",
    "Intermediate Metabolizer":  "IM",
    "Normal Metabolizer":        "NM",
    "Rapid Metabolizer":         "RM",
    "Ultrarapid Metabolizer":    "URM",
    "Poor Function":             "PM",
    "Decreased Function":        "IM",
    "Normal Function":           "NM",
    "Increased Function":        "RM",
    "Indeterminate":             "Unknown",
}


def phenotype_short_code(phenotype: str) -> str:
    return PHENOTYPE_SHORT_CODES.get(phenotype, "Unknown")


def get_drug_recommendation(gene: str, drug: str, phenotype: str):
    """
    Return CPIC recommendation dict for given gene / drug / phenotype.
    """
    drug = drug.upper()

    if drug == "CODEINE" and gene == "CYP2D6":
        return CODEINE_CYP2D6["phenotypes"].get(phenotype)

    if drug == "CLOPIDOGREL" and gene == "CYP2C19":
        return CLOPIDOGREL_CYP2C19["phenotypes"].get(phenotype)

    if drug == "SIMVASTATIN" and gene == "SLCO1B1":
        return SIMVASTATIN_SLCO1B1["phenotypes"].get(phenotype)

    if drug == "AZATHIOPRINE" and gene == "TPMT":
        return AZATHIOPRINE_TPMT["phenotypes"].get(phenotype)

    if drug == "FLUOROURACIL" and gene == "DPYD":
        return FLUOROURACIL_DPYD["phenotypes"].get(phenotype)

    if drug == "WARFARIN" and gene == "CYP2C9":
        # Warfarin: phenotype-level approximation
        warf_map = {
            "Poor Metabolizer":         "*2/*2",
            "Intermediate Metabolizer": "*1/*2",
            "Normal Metabolizer":       "*1/*1",
        }
        diplotype_key = warf_map.get(phenotype, "*1/*1")
        return WARFARIN_CYP2C9["genotype_guidance"].get(diplotype_key)

    return None