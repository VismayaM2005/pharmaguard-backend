"""
PharmaGuard – FastAPI Backend
RIFT 2026 Hackathon | Pharmacogenomics / Explainable AI Track
"""

import logging
import os
import io
import sys
from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add app directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from vcf_parser import parse_vcf_bytes
from diplotype_engine import load_all_tables, resolve_diplotype
from phenotype_engine import get_drug_recommendation, phenotype_short_code
from risk_engine import classify_risk
from schemas import build_response
from llm_engine import generate_explanation

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger("pharmaguard")

# ─── Constants ───────────────────────────────────────────────────────────────
SUPPORTED_DRUGS = {
    "CODEINE", "WARFARIN", "CLOPIDOGREL",
    "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL",
}

DRUG_GENE_MAP = {
    "CODEINE":       "CYP2D6",
    "WARFARIN":      "CYP2C9",
    "CLOPIDOGREL":   "CYP2C19",
    "SIMVASTATIN":   "SLCO1B1",
    "AZATHIOPRINE":  "TPMT",
    "FLUOROURACIL":  "DPYD",
}

MAX_VCF_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PharmaGuard API",
    description="Pharmacogenomic Risk Prediction System – RIFT 2026",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Startup ──────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("Loading diplotype tables …")
    load_all_tables()
    logger.info("PharmaGuard API ready ✓")


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "service": "PharmaGuard API"}


# ─── Analyze ──────────────────────────────────────────────────────────────────
@app.post("/analyze")
async def analyze(
    vcf_file: UploadFile = File(...),
    drugs: str = Form(...),
    patient_id: str = Form("PATIENT_001"),
):
    logger.info("Received analysis request – patient=%s drugs=%s file=%s", patient_id, drugs, vcf_file.filename)

    # ── 1. Read & size-check VCF ─────────────────────────────────────────────
    raw_bytes = await vcf_file.read()
    if len(raw_bytes) > MAX_VCF_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="VCF file exceeds 5 MB limit.")

    # ── 2. Parse VCF ─────────────────────────────────────────────────────────
    parse_result = parse_vcf_bytes(raw_bytes)

    if not parse_result["vcf_parsing_success"]:
        raise HTTPException(
            status_code=400,
            detail=f"VCF parsing failed: {parse_result.get('error', 'Unknown error')}",
        )

    variants = parse_result["variants"]
    logger.info("Parsed %d pharmacogenomic variants", len(variants))

    # ── 3. Validate drugs ────────────────────────────────────────────────────
    raw_drugs = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    invalid_drugs = [d for d in raw_drugs if d not in SUPPORTED_DRUGS]
    if invalid_drugs:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported drug(s): {', '.join(invalid_drugs)}. Supported: {', '.join(sorted(SUPPORTED_DRUGS))}",
        )
    if not raw_drugs:
        raise HTTPException(status_code=422, detail="No drugs specified.")

    # ── 4. Process each drug ─────────────────────────────────────────────────
    results = []

    for drug in raw_drugs:
        gene = DRUG_GENE_MAP[drug]
        gene_variants = [v for v in variants if v["gene"] == gene]

        # Resolve diplotype
        diplotype = resolve_diplotype(gene, gene_variants)

        # Infer phenotype (full label)
        from phenotype_infer import infer_phenotype
        phenotype_full = infer_phenotype(gene, gene_variants, diplotype)

        # CPIC short code
        phenotype_code = phenotype_short_code(phenotype_full)

        # Risk label
        risk_label = classify_risk(drug, phenotype_full)

        # Clinical recommendation
        recommendation = get_drug_recommendation(gene, drug, phenotype_full)
        if recommendation is None:
            recommendation = {
                "recommendation": "No specific CPIC guideline available for this phenotype.",
                "strength": "N/A",
            }

        # Build base JSON
        output = build_response(
            patient_id=patient_id,
            drug=drug,
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype_code,
            phenotype_full=phenotype_full,
            risk_label=risk_label,
            recommendation=recommendation,
            detected_variants=gene_variants,
            vcf_parsing_success=parse_result["vcf_parsing_success"],
        )

        # LLM explanation
        explanation = generate_explanation(
            drug=drug,
            gene=gene,
            diplotype=diplotype,
            phenotype=phenotype_full,
            risk_label=risk_label,
            variants=gene_variants,
            recommendation=recommendation,
        )
        output["llm_generated_explanation"]["summary"] = explanation

        logger.info("Drug=%s Gene=%s Phenotype=%s Risk=%s", drug, gene, phenotype_full, risk_label)
        results.append(output)

    return JSONResponse(content=results)


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
