# ================== LOAD ENV ==================
from dotenv import load_dotenv
load_dotenv()

# ================== IMPORTS ==================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import requests
import torch

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    raise ImportError(
        "❌ Install dependencies: pip install sentence-transformers scikit-learn torch"
    ) from e

# ================== CONFIG ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found. Add it to your .env file.")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

app = FastAPI(title="Medical LLM API – Gemini Powered", version="1.0")

# ================== EMBEDDING MODEL ==================
device = "cuda" if torch.cuda.is_available() else "cpu"

try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load embedding model: {e}")

def get_embedding(text: str):
    try:
        return embedding_model.encode(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {e}")

# ================== GEMINI HELPER ==================
def call_gemini(prompt: str) -> str:
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=500, detail="Unexpected Gemini API response format")

# ================== SCHEMAS ==================
class CommunityInput(BaseModel):
    age: int
    gender: str
    symptoms: List[str]

class CaseInput(BaseModel):
    symptoms: List[str]

class TreatmentInput(BaseModel):
    age: int
    symptoms: List[str]
    comorbidities: List[str]

class TrialInput(BaseModel):
    age: int
    diagnosis: str
    symptoms: List[str]

# ================== SECTION 1: MEDICAL COMMUNITIES ==================
COMMUNITIES = [
    {"name": "Respiratory Support Group", "keywords": "cough fever breathing"},
    {"name": "Diabetes Community", "keywords": "diabetes sugar insulin"},
    {"name": "Heart Care Group", "keywords": "chest pain heart blood pressure"},
]

@app.post("/medical-communities")
def medical_communities(data: CommunityInput):
    patient_emb = get_embedding(" ".join(data.symptoms))
    scores = []

    for c in COMMUNITIES:
        c_emb = get_embedding(c["keywords"])
        score = float(cosine_similarity([patient_emb], [c_emb])[0][0])  # cast to float
        scores.append((c["name"], score))

    best = max(scores, key=lambda x: x[1])

    reasoning = call_gemini(
        f"Explain why a patient with symptoms {data.symptoms} "
        f"should join the {best[0]} community."
    )

    return {
        "community": best[0],
        "confidence": round(best[1], 3),
        "reason": reasoning
    }

# ================== SECTION 2: PATIENT CASE COMPARISON ==================
PATIENT_CASES = [
    {"id": 1, "symptoms": "fever cough", "outcome": "Recovered"},
    {"id": 2, "symptoms": "chest pain breathless", "outcome": "Stable"},
    {"id": 3, "symptoms": "fatigue fever", "outcome": "Recovered"},
]

@app.post("/compare-patient-cases")
def compare_cases(data: CaseInput):
    input_emb = get_embedding(" ".join(data.symptoms))
    results = []

    for case in PATIENT_CASES:
        case_emb = get_embedding(case["symptoms"])
        sim = float(cosine_similarity([input_emb], [case_emb])[0][0])  # cast to float
        results.append({
            "case_id": case["id"],
            "similarity": round(sim, 3),
            "outcome": case["outcome"]
        })

    return sorted(results, key=lambda x: x["similarity"], reverse=True)

# ================== SECTION 3: TREATMENT PLAN ==================
@app.post("/treatment-plan")
def treatment_plan(data: TreatmentInput):
    prompt = f"""
    Patient Age: {data.age}
    Symptoms: {data.symptoms}
    Comorbidities: {data.comorbidities}

    Create a clear, step-by-step personalized treatment plan.
    Include precautions and lifestyle guidance.
    """
    plan = call_gemini(prompt)

    return {
        "treatment_plan": plan,
        "note": "AI-generated. Not a substitute for professional medical advice."
    }

# ================== SECTION 4: CLINICAL TRIAL MATCHING ==================
@app.post("/clinical-trials")
def clinical_trials(data: TrialInput):
    prompt = f"""
    Identify suitable clinical trials for:
    Age: {data.age}
    Diagnosis: {data.diagnosis}
    Symptoms: {data.symptoms}

    Provide trial type and eligibility notes.
    """
    trials = call_gemini(prompt)

    return {
        "matched_trials": trials,
        "source": "AI-assisted clinical trial matching"
    }

# ================== RUN ==================
# uvicorn FEATURES:app --reload
