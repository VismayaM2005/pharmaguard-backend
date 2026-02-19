"""
risk_engine.py – Full 6-drug risk classification
"""


def classify_risk(drug: str, phenotype: str) -> str:
    """
    Map phenotype to risk label per CPIC-aligned clinical intent.
    Returns: Safe | Adjust Dosage | Toxic | Ineffective | Unknown
    """
    drug = drug.upper()

    # CODEINE (CYP2D6)
    if drug == "CODEINE":
        if phenotype == "Ultrarapid Metabolizer":   return "Toxic"
        if phenotype == "Poor Metabolizer":          return "Ineffective"
        if phenotype in ("Normal Metabolizer", "Intermediate Metabolizer", "Rapid Metabolizer"):
            return "Safe"

    # CLOPIDOGREL (CYP2C19)
    elif drug == "CLOPIDOGREL":
        if phenotype in ("Intermediate Metabolizer", "Poor Metabolizer"):
            return "Ineffective"
        if phenotype in ("Normal Metabolizer", "Rapid Metabolizer", "Ultrarapid Metabolizer"):
            return "Safe"

    # SIMVASTATIN (SLCO1B1)
    elif drug == "SIMVASTATIN":
        if phenotype == "Poor Function":             return "Toxic"
        if phenotype == "Decreased Function":        return "Adjust Dosage"
        if phenotype in ("Normal Function", "Increased Function"):
            return "Safe"

    # AZATHIOPRINE (TPMT)
    elif drug == "AZATHIOPRINE":
        if phenotype == "Poor Metabolizer":          return "Toxic"
        if phenotype == "Intermediate Metabolizer":  return "Adjust Dosage"
        if phenotype == "Normal Metabolizer":        return "Safe"

    # FLUOROURACIL (DPYD)
    elif drug == "FLUOROURACIL":
        if phenotype == "Poor Metabolizer":          return "Toxic"
        if phenotype == "Intermediate Metabolizer":  return "Adjust Dosage"
        if phenotype == "Normal Metabolizer":        return "Safe"

    # WARFARIN (CYP2C9)
    elif drug == "WARFARIN":
        if phenotype == "Poor Metabolizer":          return "Toxic"
        if phenotype == "Intermediate Metabolizer":  return "Adjust Dosage"
        if phenotype == "Normal Metabolizer":        return "Safe"

    return "Unknown"