import os
from .diplotype_engine import load_all_tables
from .phenotype_engine import get_drug_recommendation
from .risk_engine import classify_risk
from .schemas import build_response
from .vcf_parser import parse_vcf
from .dpyd_engine import infer_dpyd_phenotype


# Drug → Gene mapping
DRUG_GENE_MAP = {
    "FLUOROURACIL": "DPYD",
    "CODEINE": "CYP2D6",
    "CLOPIDOGREL": "CYP2C19",
    "SIMVASTATIN": "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "WARFARIN": "CYP2C9"
}


def infer_phenotype(gene, variant):
    rsid = variant["rsid"]
    genotype = variant["genotype"]

    if gene == "DPYD":
        return infer_dpyd_phenotype(rsid, genotype)

    # For now fallback
    return "Normal Metabolizer"


if __name__ == "__main__":

    load_all_tables()

    patient_id = "PATIENT_001"

    # 🔥 MULTI-DRUG INPUT
    drug_input = "FLUOROURACIL, CODEINE"
    drugs = [d.strip().upper() for d in drug_input.split(",")]

    vcf_file = "patient_dpyd_test.vcf"

    print("VCF file exists:", os.path.exists(vcf_file))

    parse_result = parse_vcf(vcf_file)

    if not parse_result["vcf_parsing_success"]:
        print("VCF Parsing Error:", parse_result["error"])
        exit()

    variants = parse_result["variants"]

    if not variants:
        print("No pharmacogenomic variants detected.")
        exit()

    final_outputs = []

    for drug in drugs:

        gene = DRUG_GENE_MAP.get(drug)

        if not gene:
            continue

        # Find matching variant for this gene
        gene_variants = [v for v in variants if v["gene"] == gene]

        if gene_variants:
            variant = gene_variants[0]
            phenotype = infer_phenotype(gene, variant)
            diplotype = f"{variant['rsid']}-{variant['genotype']}"
        else:
            phenotype = "Normal Metabolizer"
            diplotype = "No variant detected"

        recommendation = get_drug_recommendation(gene, drug, phenotype)
        risk_label = classify_risk(drug, phenotype)

        final_json = build_response(
            patient_id=patient_id,
            drug=drug,
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype,
            risk_label=risk_label,
            recommendation=recommendation
        )

        final_json["pharmacogenomic_profile"]["detected_variants"] = gene_variants
        final_outputs.append(final_json)

    print("\nFINAL OUTPUTS:\n")

    for output in final_outputs:
        print(output)
