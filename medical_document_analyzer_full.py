# ================== LOAD ENV ==================
from dotenv import load_dotenv
load_dotenv()

# ================== IMPORTS ==================
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
from PyPDF2 import PdfReader
from PIL import Image, ImageOps
import pytesseract
import google.generativeai as genai
import os
import json
import re
import io

# ================== GEMINI CLIENT ==================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables!")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)

# ================== FASTAPI APP ==================
app = FastAPI(
    title="Medical Document Analyzer API",
    description="Analyze medical documents + symptoms, suggest diseases and doctors",
    version="1.0"
)

# ================== HELPER FUNCTIONS ==================
async def extract_text_from_pdf(file: UploadFile) -> str:
    content = await file.read()
    reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()

async def extract_text_from_image(file: UploadFile) -> str:
    content = await file.read()
    img = Image.open(io.BytesIO(content)).convert("RGB")
    # Convert to grayscale to improve OCR accuracy
    img = ImageOps.grayscale(img)
    return pytesseract.image_to_string(img).strip()

def prepare_gemini_prompt(
    document_text: str,
    main_symptoms: List[str],
    additional_symptoms: List[str],
    allergies: List[str]
) -> str:
    return f"""
You are a careful medical assistant AI.
⚠️ You are NOT providing a medical diagnosis.

Medical document content:
{document_text}

User symptoms:
- Main: {', '.join(main_symptoms)}
- Additional: {', '.join(additional_symptoms)}
- Allergies: {', '.join(allergies)}

TASK:
1. Suggest up to 10 possible diseases with likelihood (Low/Medium/High).
2. For each disease include:
   - Name
   - Brief symptoms
   - Detailed explanation
   - Additional symptoms
3. Identify top common symptoms.
4. Recommend doctor specialties.

RETURN STRICT JSON ONLY:
{{
  "disease_analysis": [
    {{
      "name": "",
      "possibility": "",
      "brief_symptoms": [],
      "details": "",
      "additional_symptoms": []
    }}
  ],
  "top_symptoms": [],
  "recommended_doctors": []
}}
"""

def call_gemini(prompt: str) -> dict:
    try:
        response = model.generate_content(prompt)
        content = response.text

        # Remove code block markdowns if present
        cleaned = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()

        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"error": "Gemini returned invalid JSON", "raw_output": content}
    except Exception as e:
        return {"error": "Gemini processing failed", "details": str(e)}

# ================== API ENDPOINT ==================
@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    main_symptoms: str = Form(...),
    additional_symptoms: str = Form(""),
    allergies: str = Form("")
):
    try:
        if file.filename.lower().endswith(".pdf"):
            document_text = await extract_text_from_pdf(file)
        elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            document_text = await extract_text_from_image(file)
        elif file.filename.lower().endswith(".txt"):
            document_text = (await file.read()).decode()
        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file type"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"File processing failed: {str(e)}"})

    prompt = prepare_gemini_prompt(
        document_text,
        [s.strip() for s in main_symptoms.split(",") if s.strip()],
        [s.strip() for s in additional_symptoms.split(",") if s.strip()],
        [s.strip() for s in allergies.split(",") if s.strip()]
    )

    result = call_gemini(prompt)
    return result

# ================== RUN ==================
# uvicorn medical_document_analyzer_gemini:app --reload
