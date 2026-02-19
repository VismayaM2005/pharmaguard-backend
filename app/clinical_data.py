# clinical_data.py
# EXACT CPIC DATA – extracted only from user-provided guideline tables
# No assumptions. No modifications.


# -----------------------------------------------------------
# 1️⃣ CODEINE – CYP2D6
# Source: Table 2 Codeine therapy recommendations
# -----------------------------------------------------------

CODEINE_CYP2D6 = {
    "gene": "CYP2D6",
    "drug": "CODEINE",
    "phenotypes": {
        "Ultrarapid Metabolizer": {
            "activity_score": "> 2.25",
            "recommendation": "Avoid codeine use because of potential for serious toxicity. If opioid use is warranted, consider a non-tramadol opioid.",
            "strength": "Strong"
        },
        "Normal Metabolizer": {
            "activity_score": "1.25 ≤ AS ≤ 2.25",
            "recommendation": "Use codeine label recommended age-specific or weight-specific dosing.",
            "strength": "Strong"
        },
        "Intermediate Metabolizer": {
            "activity_score": "0 < AS < 1.25",
            "recommendation": "Use codeine label recommended age-specific or weight-specific dosing. If no response and opioid use is warranted, consider a non-tramadol opioid.",
            "strength": "Moderate"
        },
        "Poor Metabolizer": {
            "activity_score": "0",
            "recommendation": "Avoid codeine use because of possibility of diminished analgesia. If opioid use is warranted, consider a non-tramadol opioid.",
            "strength": "Strong"
        }
    }
}


# -----------------------------------------------------------
# 2️⃣ CLOPIDOGREL – CYP2C19 (ACS/PCI column only)
# Source: Table 2 Antiplatelet therapy recommendations
# -----------------------------------------------------------

CLOPIDOGREL_CYP2C19 = {
    "gene": "CYP2C19",
    "drug": "CLOPIDOGREL",
    "context": "ACS and/or PCI",
    "phenotypes": {
        "Ultrarapid Metabolizer": {
            "recommendation": "If considering clopidogrel, use at standard dose (75 mg/day).",
            "strength": "Strong"
        },
        "Rapid Metabolizer": {
            "recommendation": "If considering clopidogrel, use at standard dose (75 mg/day).",
            "strength": "Strong"
        },
        "Normal Metabolizer": {
            "recommendation": "If considering clopidogrel, use at standard dose (75 mg/day).",
            "strength": "Strong"
        },
        "Intermediate Metabolizer": {
            "recommendation": "Avoid standard dose (75 mg) clopidogrel if possible. Use prasugrel or ticagrelor at standard dose if no contraindication.",
            "strength": "Strong"
        },
        "Poor Metabolizer": {
            "recommendation": "Avoid clopidogrel if possible. Use prasugrel or ticagrelor at standard dose if no contraindication.",
            "strength": "Strong"
        }
    }
}


# -----------------------------------------------------------
# 3️⃣ SIMVASTATIN – SLCO1B1
# Source: Table 2 Dosing recommendations for statins
# -----------------------------------------------------------

SIMVASTATIN_SLCO1B1 = {
    "gene": "SLCO1B1",
    "drug": "SIMVASTATIN",
    "phenotypes": {
        "Increased Function": {
            "recommendation": "Prescribe desired starting dose and adjust doses based on disease-specific guidelines.",
            "strength": "Strong"
        },
        "Normal Function": {
            "recommendation": "Prescribe desired starting dose and adjust doses based on disease-specific guidelines.",
            "strength": "Strong"
        },
        "Decreased Function": {
            "recommendation": "Prescribe an alternative statin depending on the desired potency. If simvastatin therapy is warranted, limit dose to <20 mg/day.",
            "strength": "Strong"
        },
        "Poor Function": {
            "recommendation": "Prescribe an alternative statin depending on the desired potency.",
            "strength": "Strong"
        }
    }
}


# -----------------------------------------------------------
# 4️⃣ AZATHIOPRINE – TPMT
# Source: Table 2 Recommended dosing of thiopurines by TPMT phenotype
# -----------------------------------------------------------

AZATHIOPRINE_TPMT = {
    "gene": "TPMT",
    "drug": "AZATHIOPRINE",
    "phenotypes": {
        "Normal Metabolizer": {
            "recommendation": "Start with normal starting dose (2–3 mg/kg/day) and adjust doses of azathioprine based on disease-specific guidelines. Allow 2 weeks to reach steady-state after each dose adjustment.",
            "strength": "Strong"
        },
        "Intermediate Metabolizer": {
            "recommendation": "Start with reduced starting doses (30–80% of normal dose) and adjust doses of azathioprine based on degree of myelosuppression and disease-specific guidelines. Allow 2–4 weeks to reach steady-state after each dose adjustment.",
            "strength": "Strong"
        },
        "Poor Metabolizer": {
            "recommendation": "For nonmalignant conditions, consider alternative nonthiopurine immunosuppressant therapy. For malignancy, start with drastically reduced doses (reduce daily dose by 10-fold and dose thrice weekly instead of daily) and adjust doses based on degree of myelosuppression and disease-specific guidelines. Allow 4–6 weeks to reach steady-state after each dose adjustment.",
            "strength": "Strong"
        }
    }
}


# -----------------------------------------------------------
# 5️⃣ FLUOROURACIL – DPYD
# Source: Table 2 Recommended dosing of fluoropyrimidines
# -----------------------------------------------------------

FLUOROURACIL_DPYD = {
    "gene": "DPYD",
    "drug": "FLUOROURACIL",
    "phenotypes": {
        "Normal Metabolizer": {
            "recommendation": "Use label-recommended dosage and administration.",
            "strength": "Strong"
        },
        "Intermediate Metabolizer": {
            "recommendation": "Reduce starting dose based on activity score followed by titration of dose based on toxicity or therapeutic drug monitoring. Activity score 1: Reduce dose by 50%. Activity score 1.5: Reduce dose by 25% to 50%.",
            "strength": "Activity score 1: Strong; Activity score 1.5: Moderate"
        },
        "Poor Metabolizer": {
            "recommendation": "Avoid use of 5-fluorouracil or 5-fluorouracil prodrug-based regimens.",
            "strength": "Strong"
        }
    }
}
# -----------------------------------------------------------
# 6️⃣ WARFARIN – CYP2C9 (Genotype-based guidance)
# Source: Figure 2 CPIC Pharmacogenetics-Guided Warfarin Dosing
# -----------------------------------------------------------

WARFARIN_CYP2C9 = {
    "gene": "CYP2C9",
    "drug": "WARFARIN",
    "note": "Warfarin dosing recommendations are genotype-based, not phenotype-based.",
    "genotype_guidance": {
        "*1/*1": {
            "recommendation": "Use standard warfarin dosing algorithm.",
            "strength": "CPIC algorithm-based"
        },
        "*1/*2": {
            "recommendation": "Consider reduced dose; increased bleeding risk due to decreased metabolism.",
            "strength": "CPIC algorithm-based"
        },
        "*1/*3": {
            "recommendation": "Consider reduced dose; increased bleeding risk due to decreased metabolism.",
            "strength": "CPIC algorithm-based"
        },
        "*2/*2": {
            "recommendation": "Reduced dose recommended; increased bleeding risk.",
            "strength": "CPIC algorithm-based"
        },
        "*2/*3": {
            "recommendation": "Significantly reduced dose recommended; increased bleeding risk.",
            "strength": "CPIC algorithm-based"
        },
        "*3/*3": {
            "recommendation": "Significantly reduced dose recommended; high bleeding risk.",
            "strength": "CPIC algorithm-based"
        }
    }
}