from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from .diplotype_engine import load_all_tables
from .phenotype_engine import get_drug_recommendation
from .risk_engine import classify_risk
from .schemas import build_response
from .vcf_parser import parse_vcf
from .dpyd_engine import infer_dpyd_phenotype

# ✅ CREATE FASTAPI APP
app = FastAPI()

# Load CPIC tables at startup
load_all_tables()

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

    return "Normal Metabolizer"


# 🔥 API ENDPOINT
@app.post("/analyze")
async def analyze(
    patient_id: str = Form(...),
    drug_input: str = Form(...),
    file: UploadFile = File(...)
):

    contents = await file.read()
    parse_result = parse_vcf(contents)

    if not parse_result["vcf_parsing_success"]:
        return {"error": parse_result["error"]}

    variants = parse_result["variants"]
    drugs = [d.strip().upper() for d in drug_input.split(",")]

    final_outputs = []

    for drug in drugs:

        gene = DRUG_GENE_MAP.get(drug)
        if not gene:
            continue

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

    return final_outputs


# Serve frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")
