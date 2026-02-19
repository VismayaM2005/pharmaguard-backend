def infer_dpyd_phenotype(rsid, genotype):
    """
    CPIC-aligned DPYD phenotype inference.
    """

    if rsid == "rs1801160":
        if genotype in ["1/1", "1|1"]:
            return "Poor Metabolizer"
        if genotype in ["0/1", "0|1"]:
            return "Intermediate Metabolizer"

    return "Normal Metabolizer"