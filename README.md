# PharmaGuard 
### Pharmacogenomic Risk Prediction System
**RIFT 2026 Hackathon — Pharmacogenomics / Explainable AI Track**

> AI-powered pharmacogenomic risk assessment aligned with CPIC clinical guidelines. Upload a patient VCF file, select drugs, and receive structured risk predictions with Explainable AI summaries.

---

## Live Demo
- **Frontend**: *(Deploy to Vercel — see below)*
- **Backend**: *(Deploy to Render — see below)*

---

## Architecture

```
pharmaguard-backend/
├── app/
│   ├── main.py              ← FastAPI server (endpoints, orchestration)
│   ├── vcf_parser.py        ← VCF v4.2 strict parser
│   ├── phenotype_infer.py   ← rsID → phenotype inference
│   ├── diplotype_engine.py  ← Star allele diplotype resolver
│   ├── phenotype_engine.py  ← CPIC recommendation lookup
│   ├── risk_engine.py       ← Risk label classifier
│   ├── llm_engine.py        ← Gemini LLM explanation generator
│   ├── schemas.py           ← JSON schema builder
│   ├── clinical_data.py     ← CPIC guideline data (6 drugs)
│   └── dpyd_engine.py       ← DPYD-specific phenotype logic
├── data/                    ← CPIC CSV diplotype tables (6 genes)
├── samples/                 ← Sample VCF files (6 genes)
├── frontend/
│   └── index.html           ← Clinical AI dashboard (pure HTML/JS)
├── requirements.txt
├── .env.example
└── README.md
```

### Data Flow
```
VCF Upload → VCF Parser → Gene Filter → Diplotype Resolver
    → Phenotype Engine → Risk Engine → LLM Explanation
    → JSON Schema Validator → Response
```

---

## Supported Genes & Drugs

| Drug | Gene | Risk Classes |
|------|------|-------------|
| Codeine | CYP2D6 | Safe / Ineffective / Toxic |
| Warfarin | CYP2C9 | Safe / Adjust Dosage / Toxic |
| Clopidogrel | CYP2C19 | Safe / Ineffective |
| Simvastatin | SLCO1B1 | Safe / Adjust Dosage / Toxic |
| Azathioprine | TPMT | Safe / Adjust Dosage / Toxic |
| Fluorouracil | DPYD | Safe / Adjust Dosage / Toxic |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 · FastAPI · Uvicorn |
| AI/LLM | Google Gemini 1.5 Flash |
| Data | Pandas · CPIC CSV tables |
| Frontend | HTML5 · Vanilla CSS · JavaScript |
| Fonts | Inter · JetBrains Mono |
| Deployment | Vercel (frontend) · Render (backend) |

---

## Local Setup

### 1. Clone & Install
```bash
git clone <your-repo-url>
cd pharmaguard-backend
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Start Backend
```bash
cd app
uvicorn main:app --reload --port 8000
```

### 4. Open Frontend
Open `frontend/index.html` in your browser.
Set Backend URL to `http://localhost:8000` and click **Ping** to verify.

---

## API Documentation

### `GET /health`
Returns service health status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-02-20T00:00:00+00:00",
  "service": "PharmaGuard API"
}
```

---

### `POST /analyze`
Analyze pharmacogenomic variants from a VCF file for specified drugs.

**Request (multipart/form-data):**
| Field | Type | Description |
|-------|------|-------------|
| `vcf_file` | File | VCF v4.x file (max 5 MB) |
| `drugs` | string | Comma-separated drug names |
| `patient_id` | string | Patient identifier (optional, default: PATIENT_001) |

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "vcf_file=@samples/sample_DPYD_poor.vcf" \
  -F "drugs=FLUOROURACIL,CODEINE" \
  -F "patient_id=PATIENT_001"
```

**Response Schema:**
```json
[
  {
    "patient_id": "PATIENT_001",
    "drug": "FLUOROURACIL",
    "timestamp": "2026-02-20T00:00:00+00:00",
    "risk_assessment": {
      "risk_label": "Toxic",
      "confidence_score": 0.93,
      "severity": "critical"
    },
    "pharmacogenomic_profile": {
      "primary_gene": "DPYD",
      "diplotype": "*1/*2A",
      "phenotype": "PM",
      "detected_variants": [{ "rsid": "rs3918290" }]
    },
    "clinical_recommendation": {
      "recommendation": "Avoid use of 5-fluorouracil...",
      "strength": "Strong"
    },
    "llm_generated_explanation": {
      "summary": "The patient carries the DPYD *2A variant (rs3918290)..."
    },
    "quality_metrics": {
      "vcf_parsing_success": true
    }
  }
]
```

**Error Responses:**
| Code | Reason |
|------|--------|
| 400 | Invalid VCF file or format |
| 422 | Unsupported drug name |
| 500 | Internal server error |

---

## Sample VCF Files

Located in `samples/`:

| File | Gene | Expected Risk (Drug) |
|------|------|---------------------|
| `sample_CYP2D6_poor.vcf` | CYP2D6 | Ineffective (Codeine) |
| `sample_CYP2C19_poor.vcf` | CYP2C19 | Ineffective (Clopidogrel) |
| `sample_CYP2C9_intermediate.vcf` | CYP2C9 | Adjust Dosage (Warfarin) |
| `sample_SLCO1B1_poor.vcf` | SLCO1B1 | Toxic (Simvastatin) |
| `sample_TPMT_poor.vcf` | TPMT | Toxic (Azathioprine) |
| `sample_DPYD_poor.vcf` | DPYD | Toxic (Fluorouracil) |

---

## Deployment

### Frontend → Vercel
```bash
npm install -g vercel
vercel frontend/
```

### Backend → Render
1. Push to GitHub
2. New Web Service on Render → Connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GEMINI_API_KEY`

---

## CPIC Alignment

All recommendations are sourced directly from CPIC (Clinical Pharmacogenomics Implementation Consortium) guidelines:
- [CPIC Codeine / CYP2D6](https://cpicpgx.org/guidelines/guideline-for-codeine-and-cyp2d6/)
- [CPIC Clopidogrel / CYP2C19](https://cpicpgx.org/guidelines/guideline-for-clopidogrel-and-cyp2c19/)
- [CPIC Warfarin / CYP2C9](https://cpicpgx.org/guidelines/guideline-for-warfarin-and-cyp2c9-vkorc1/)
- [CPIC Simvastatin / SLCO1B1](https://cpicpgx.org/guidelines/cpic-guideline-for-statins/)
- [CPIC Azathioprine / TPMT](https://cpicpgx.org/guidelines/guideline-for-thiopurines-and-tpmt/)
- [CPIC Fluorouracil / DPYD](https://cpicpgx.org/guidelines/guideline-for-fluoropyrimidines-and-dpyd/)

---

## Team
**PharmaGuard Team — RIFT 2026 Hackathon**
Harsha Bharadwaj 
Guru Raj Patil 
Thrisha R
Vismaya M
---
