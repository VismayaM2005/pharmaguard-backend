"""
schemas.py – Upgraded
Builds exact hackathon JSON schema output.
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger("pharmaguard.schemas")


def build_response(
    patient_id: str,
    drug: str,
    gene: str,
    diplotype: str,
    phenotype: str,        # CPIC short code: PM/IM/NM/RM/URM/Unknown
    phenotype_full: str,   # Full label: "Poor Metabolizer"
    risk_label: str,
    recommendation,
    detected_variants: list,
    vcf_parsing_success: bool,
) -> dict:
    """
    Build exact hackathon-required JSON output.
    """
    severity_map = {
        "Safe":          "none",
        "Adjust Dosage": "moderate",
        "Ineffective":   "high",
        "Toxic":         "critical",
        "Unknown":       "moderate",
    }

    confidence_map = {
        "Safe":          0.95,
        "Adjust Dosage": 0.88,
        "Ineffective":   0.90,
        "Toxic":         0.93,
        "Unknown":       0.50,
    }

    # Normalise recommendation
    if isinstance(recommendation, dict):
        clinical_rec = recommendation
    elif isinstance(recommendation, str):
        clinical_rec = {"recommendation": recommendation, "strength": "N/A"}
    else:
        clinical_rec = {
            "recommendation": "No CPIC guideline available for this combination.",
            "strength": "N/A",
        }

    # Detected variants: strip internal fields, keep rsid
    variant_entries = [{"rsid": v.get("rsid", ".")} for v in detected_variants]

    return {
        "patient_id":  patient_id,
        "drug":        drug,
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "risk_assessment": {
            "risk_label":       risk_label,
            "confidence_score": confidence_map.get(risk_label, 0.80),
            "severity":         severity_map.get(risk_label, "moderate"),
        },
        "pharmacogenomic_profile": {
            "primary_gene":      gene,
            "diplotype":         diplotype,
            "phenotype":         phenotype,
            "detected_variants": variant_entries,
        },
        "clinical_recommendation": clinical_rec,
        "llm_generated_explanation": {
            "summary": "",   # filled by main.py after LLM call
        },
        "quality_metrics": {
            "vcf_parsing_success": vcf_parsing_success,
        },
    }