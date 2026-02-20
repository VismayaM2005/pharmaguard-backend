"""
llm_engine.py
Generates clinical explanations using Google Gemini API.
Strict prompt to avoid hallucination – only uses structured data passed in.
Falls back to template-based explanation if API unavailable.
"""

import logging
import os

logger = logging.getLogger("pharmaguard.llm")

# Metabolism pathway descriptions per gene
GENE_MECHANISM = {
    "CYP2D6": (
        "CYP2D6 is a cytochrome P450 enzyme responsible for the hepatic oxidative metabolism "
        "of codeine to its active analgesic form, morphine. Variants in CYP2D6 alter enzyme "
        "activity and directly determine morphine exposure."
    ),
    "CYP2C19": (
        "CYP2C19 catalyses the bioactivation of clopidogrel (a pro-drug) into its active "
        "thiol metabolite via two oxidative steps. Reduced CYP2C19 activity results in "
        "lower active metabolite levels and diminished platelet inhibition."
    ),
    "CYP2C9": (
        "CYP2C9 is the primary enzyme responsible for the S-warfarin hydroxylation pathway. "
        "Decreased CYP2C9 activity causes reduced warfarin clearance, leading to elevated "
        "plasma concentrations and increased bleeding risk."
    ),
    "SLCO1B1": (
        "SLCO1B1 encodes OATP1B1, a hepatic uptake transporter that internalises statins "
        "from portal blood into hepatocytes for metabolism. Reduced OATP1B1 function leads "
        "to increased systemic statin exposure and elevated myopathy risk."
    ),
    "TPMT": (
        "TPMT (thiopurine S-methyltransferase) inactivates thiopurines including azathioprine "
        "by methylation. Reduced TPMT activity diverts thiopurine metabolism toward "
        "6-thioguanine nucleotides (6-TGN), causing myelosuppression at standard doses."
    ),
    "DPYD": (
        "DPYD (dihydropyrimidine dehydrogenase) is the rate-limiting enzyme in fluoropyrimidine "
        "catabolism, responsible for > 80 % of 5-fluorouracil degradation. DPYD variants "
        "reduce enzyme activity, causing life-threatening fluorouracil accumulation."
    ),
}


def _template_explanation(
    drug, gene, diplotype, phenotype, risk_label, variants, recommendation
):
    """
    Generate a structured clinical explanation without LLM (fallback).
    """
    rsids = [v["rsid"] for v in variants if v.get("rsid") and v["rsid"] != "."]
    stars = list(
        {v["star"] for v in variants if v.get("star") and v["star"] not in (".", "")}
    )

    rsid_text = ", ".join(rsids) if rsids else "no specific rsID detected in this VCF"
    star_text = " / ".join(stars) if stars else "not determined from VCF"
    mechanism = GENE_MECHANISM.get(
        gene, f"{gene} enzyme activity influences drug metabolism."
    )

    rec_text = ""
    if isinstance(recommendation, dict):
        rec_text = recommendation.get("recommendation", "")
    elif isinstance(recommendation, str):
        rec_text = recommendation

    summary = (
        f"Pharmacogenomic analysis of {drug} ({gene}): "
        f"The patient carries the diplotype {diplotype} ({phenotype}), "
        f"identified via variant(s) {rsid_text}"
        f"{(' (star allele(s): ' + star_text + ')') if star_text != 'not determined from VCF' else ''}. "
        f"{mechanism} "
        f"Based on CPIC guidelines, this pharmacogenomic profile is classified as {risk_label}. "
        f"Clinical recommendation: {rec_text}"
    )
    return summary.strip()


async def generate_explanation(
    drug, gene, diplotype, phenotype, risk_label, variants, recommendation
):
    """
    Attempt Gemini API call; fall back to template on any failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        logger.info("GEMINI_API_KEY not set – using template explanation")
        return _template_explanation(
            drug, gene, diplotype, phenotype, risk_label, variants, recommendation
        )

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        rsids = [v["rsid"] for v in variants if v.get("rsid") and v["rsid"] != "."]
        stars = list(
            {
                v["star"]
                for v in variants
                if v.get("star") and v["star"] not in (".", "")
            }
        )
        mechanism = GENE_MECHANISM.get(gene, "")

        rec_text = ""
        if isinstance(recommendation, dict):
            rec_text = recommendation.get("recommendation", "")
        elif isinstance(recommendation, str):
            rec_text = recommendation

        prompt = f"""You are a clinical pharmacogenomics expert generating structured explanations for clinicians.

STRICT RULES:
1. Only use the data provided below. Do NOT invent or hallucinate any information.
2. Explicitly cite rsIDs and star alleles provided.
3. Explain the enzyme activity mechanism using the provided mechanism text.
4. Cite the CPIC recommendation exactly as given.
5. Write in clear, professional clinical language. 2–4 sentences maximum.

DATA:
- Drug: {drug}
- Gene: {gene}
- Diplotype: {diplotype}
- Phenotype: {phenotype}
- Risk Label: {risk_label}
- Detected rsIDs: {', '.join(rsids) if rsids else 'none'}
- Star Alleles: {', '.join(stars) if stars else 'not determined'}
- Enzyme Mechanism: {mechanism}
- CPIC Recommendation: {rec_text}

Generate a concise clinical explanation (2–4 sentences) that:
1. Names the detected variant(s)/rsID(s) and star allele(s)
2. Explains how they affect {gene} enzyme activity
3. Explains the pharmacokinetic consequence for {drug}
4. States the CPIC-aligned clinical recommendation

Output ONLY the explanation text. No headers, no bullet points."""

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        logger.info("LLM explanation generated (len=%d chars)", len(text))
        return text

    except Exception as exc:
        logger.warning("LLM call failed (%s) – using template fallback", exc)
        return _template_explanation(
            drug, gene, diplotype, phenotype, risk_label, variants, recommendation
        )
