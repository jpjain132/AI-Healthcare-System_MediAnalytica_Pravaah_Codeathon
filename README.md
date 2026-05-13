# MediAnalytica — an AI-ML healthcare website

Our team built MediAnalytica — an AI-ML healthcare website that analyzes medical documents, processes prescriptions, and detects rare diseases using LLM integration (DeepSeek API) 🧠⚕️

💡 Features we built:
- 📄 Medical Document Analyzer — Extracts key information from lab reports, patient histories, and clinical notes, identifies patterns, and detects abnormal values.
- 💊 Prescription Safety Analyzer — AI-powered safety analysis, drug-interaction checks, and clinical validation from prescription images.
- 🧬 Rare Disease Detection — Intelligent medical report analysis to identify rare disease patterns.

⚙️ Tech stack: HTML, CSS, TypeScript, JSON, Python, AI/ML, and LLM integration.
🚀 Deployed live on Netlify

🌐 View our work demo: https://medical-app-api.netlify.app/

You can explore as a guest or login here: https://medical-app-api.netlify.app/login



# 📌 Project Overview

Smart Health Assistant is a full-stack AI-powered healthcare intelligence platform designed to automate:

- Medical document analysis
- Disease prediction assistance
- Clinical anomaly detection
- Prescription safety analysis
- Rare disease support
- Patient case comparison
- AI treatment planning
- Clinical trial matching
- Medical community recommendation

The platform combines:

- Large Language Models (LLMs)
- OCR pipelines
- Semantic embeddings
- NLP clinical extraction
- FastAPI microservices
- Flask frontend integration
- Gemini AI reasoning
- Authentication systems
- Responsive healthcare dashboards

---

# 🧠 Core Technologies Used

| Technology | Purpose |
|---|---|
| FastAPI | AI backend microservices |
| Flask | Frontend request gateway |
| Gemini 2.5 Flash | Medical reasoning + generation |
| Sentence Transformers | Semantic similarity |
| MiniLM-L6-v2 | Lightweight embedding model |
| PyTorch | Embedding inference backend |
| Tesseract OCR | Text extraction from reports |
| PIL / Pillow | Image preprocessing |
| Supabase | Authentication system |
| JavaScript | Frontend interactivity |
| HTML/CSS | UI dashboard |
| Regex | Clinical entity extraction |
| JSON | Structured AI response format |

---

# 🏗️ Complete Architecture

```text
Frontend (HTML/CSS/JS)
        │
        ▼
Flask Application Layer
        │
        ▼
FastAPI AI Services
        │
        ├── OCR Pipeline
        ├── PDF Processing
        ├── NLP Entity Extraction
        ├── Semantic Similarity Engine
        ├── Gemini LLM Reasoning
        ├── Prescription Analyzer
        ├── Anomaly Detection
        └── Evaluation Pipeline
        │
        ▼
JSON Medical Intelligence Response
        │
        ▼
Interactive Medical Dashboard
```

---

# 📂 COMPLETE PROJECT STRUCTURE EXPLANATION

---

# 1️⃣ FEATURES.py

## 📌 Purpose

Main AI microservice backend for:

- Patient similarity search
- Medical community recommendation
- Treatment plan generation
- Clinical trial matching

---

# ✅ Technologies Used

```python
FastAPI
SentenceTransformers
PyTorch
Gemini API
scikit-learn
Cosine Similarity
```

---

# ✅ Important Code Terms Used

| Term | Meaning |
|---|---|
| FastAPI | High-performance Python API framework |
| HTTPException | Raises structured API errors |
| BaseModel | Pydantic schema validator |
| SentenceTransformer | Converts text into semantic embeddings |
| Embeddings | Numerical vector representation of text |
| cosine_similarity | Measures semantic similarity between vectors |
| torch.cuda.is_available() | Detects GPU availability |
| requests.post() | Sends API requests |
| dotenv | Loads environment variables |
| Gemini API | LLM reasoning engine |

---

# ✅ Key Functionalities

---

## 🔹 Medical Community Recommendation

### Purpose
Recommends support communities based on patient symptoms.

### Workflow

```text
Patient Symptoms
      ↓
Embedding Generation
      ↓
Cosine Similarity
      ↓
Best Matching Community
      ↓
Gemini AI Explanation
```

### AI Approach Used

```text
Semantic Similarity Search
```

### Model Used

```text
all-MiniLM-L6-v2
```

---

## 🔹 Patient Case Comparison

### Purpose
Compares patient symptoms with previous patient cases.

### AI Technique Used

```text
Embedding-Based Retrieval
```

### Workflow

```text
Input Symptoms
      ↓
Embedding Vector
      ↓
Similarity Matching
      ↓
Rank Similar Cases
```

---

## 🔹 Treatment Plan Generator

### Purpose
Generates AI-based personalized treatment guidance.

### Gemini Prompt Engineering Used

- Structured prompting
- Context injection
- Constraint-based generation
- Medical disclaimer enforcement

---

## 🔹 Clinical Trial Matching

### Purpose
Matches patients with relevant clinical trials.

### AI Approach

```text
LLM-Based Reasoning + Medical Context Matching
```

---

# 2️⃣ medical_document_analyzer_full_with_evaluation.py

## 📌 Purpose

Main medical AI analysis engine.

This file performs:

- OCR extraction
- PDF processing
- Medical NLP
- Disease analysis
- Doctor recommendation
- Anomaly detection
- Evaluation metrics generation

---

# ✅ Supported File Types

```text
PDF
PNG
JPG
JPEG
TXT
```

---

# 🧠 COMPLETE AI PIPELINE

```text
Medical Report Upload
        │
        ▼
OCR / PDF Extraction
        │
        ▼
Clinical Entity Extraction
        │
        ▼
Medical Anomaly Detection
        │
        ▼
Gemini AI Analysis
        │
        ▼
Structured JSON Medical Report
```

---

# ✅ Important Code Terms Used

| Term | Meaning |
|---|---|
| UploadFile | FastAPI file upload handler |
| PdfReader | Extracts text from PDFs |
| pytesseract | OCR engine |
| ImageOps.grayscale | Converts image to grayscale |
| regex / re | Pattern matching engine |
| JSONResponse | Structured API response |
| f1_score | Classification evaluation metric |
| GenerativeModel | Gemini model interface |
| generate_content() | Sends prompt to Gemini |
| json.loads() | Converts JSON string into Python object |

---

# 🔬 OCR Pipeline

## PDF Extraction

### Library Used

```python
PyPDF2
```

### Purpose

Extracts machine-readable text from PDFs.

---

## Image OCR

### Libraries Used

```python
pytesseract
Pillow (PIL)
```

### Image Preprocessing Used

```python
ImageOps.grayscale(img)
```

### Why?

To improve:

- OCR readability
- Text extraction quality
- Noise reduction
- Lab report interpretation

---

# 🧬 Clinical Entity Extraction

## Purpose

Extracts medical entities from reports.

---

# ✅ Extracted Entities

- Diseases
- Medications
- Lab values
- Abnormal findings

---

# ✅ Disease Patterns Used

```python
diabetes
hypertension
kidney disease
heart failure
anemia
sepsis
pneumonia
```

---

# ✅ Medication Patterns Used

```python
aspirin
metformin
insulin
amiodarone
lisinopril
furosemide
```

---

# 🚨 Medical Anomaly Detection

## Purpose

Detects critical medical abnormalities.

---

# ✅ Conditions Detected

- Severe Hyperglycemia
- Sepsis
- Respiratory Failure
- Cardiac Arrest
- High Creatinine

---

# ✅ AI Technique Used

```text
Rule-Based Detection + Medical Threshold Logic
```

---

# 🤖 Gemini Prompt Engineering

## Purpose

Structured AI reasoning.

---

# ✅ Prompting Techniques Used

| Technique | Purpose |
|---|---|
| Structured prompting | Enforce predictable outputs |
| JSON constrained generation | Valid API responses |
| Context injection | Better reasoning |
| Safety disclaimer prompting | Avoid direct diagnosis |
| Hallucination reduction | Improve reliability |

---

# 📊 Evaluation Metrics

---

# ✅ F1 Score

Approximate value:

```text
82.37%
```

### Meaning

Measures balance between:

- Precision
- Recall

Formula:

:contentReference[oaicite:0]{index=0}

---

# ✅ Additional Metrics

| Metric | Purpose |
|---|---|
| Processing Time | Speed analysis |
| OCR Accuracy | Extraction quality |
| Analysis Time Reduction | Performance optimization |
| Decision Accuracy | AI response quality |

---

# 🛠️ Debugging & Optimization Approaches

---

# ✅ JSON Recovery

```python
try:
    json.loads(cleaned)
except JSONDecodeError:
```

### Purpose

Prevents crashes caused by malformed Gemini output.

---

# ✅ OCR Optimization

Techniques used:

- grayscale conversion
- preprocessing
- normalization

Purpose:

- improve extraction accuracy

---

# ✅ API Failure Handling

Implemented:

```python
timeout handling
HTTP exception handling
structured API errors
```

---

# ✅ Prompt Cleaning

Removed:

```
```json
```

from Gemini responses before parsing.

---

# ✅ Embedding Optimization

Used:

- MiniLM lightweight embeddings
- cosine similarity ranking

Purpose:

- lower latency
- faster inference

---

# 3️⃣ app.py

## 📌 Purpose

Acts as Flask frontend gateway.

---

# ✅ Responsibilities

- Accept file uploads
- Send requests to FastAPI backend
- Render AI responses

---

# ✅ Flow

```text
Frontend Form
      ↓
Flask Backend
      ↓
FastAPI AI Service
      ↓
Gemini AI Processing
      ↓
Frontend Dashboard
```

---

# ✅ Important Terms Used

| Term | Meaning |
|---|---|
| render_template | Renders HTML page |
| request.files | Access uploaded file |
| flash() | Temporary UI message |
| redirect() | Redirect webpage |
| requests.post() | API communication |
| response.json() | Parse JSON response |

---

# 4️⃣ Authentication System

Files:

```text
login.html
register.html
otp.html
session.js
client.js
```

---

# 🔐 Authentication Features

---

## ✅ Supabase Authentication

Implemented:

- Signup
- Login
- OTP verification
- Session persistence

---

## ✅ Session Management

Implemented using:

```javascript
localStorage
```

---

# ✅ Features

- Auto-login redirect
- Session expiration
- Logout handling
- Persistent authentication

---

# 5️⃣ client.js

## 📌 Purpose

Initializes Supabase client.

---

# ✅ Important Terms

| Term | Meaning |
|---|---|
| createClient() | Creates Supabase instance |
| supabaseUrl | Database endpoint |
| supabaseKey | API access key |

---

# 6️⃣ session.js

## 📌 Purpose

Handles authentication sessions.

---

# ✅ Features

- Save sessions
- Retrieve sessions
- Auto-redirect logged users
- Logout management

---

# ✅ Important Terms

| Term | Meaning |
|---|---|
| localStorage | Browser storage |
| JSON.parse() | Converts string to object |
| JSON.stringify() | Converts object to string |
| expiresAt | Session expiration timestamp |

---

# 7️⃣ login.html

## 📌 Purpose

User login interface.

---

# ✅ Features

- Email/password login
- Responsive authentication UI
- Supabase login integration

---

# 8️⃣ register.html

## 📌 Purpose

User registration interface.

---

# ✅ Features

- User signup
- Email verification
- Redirect to OTP page

---

# 9️⃣ otp.html

## 📌 Purpose

OTP verification page.

---

# ✅ Features

- Email OTP verification
- Session initialization
- Auto-login after verification

---

# 🔟 index.html

## 📌 Purpose

Main healthcare dashboard UI.

---

# ✅ Features

- Upload medical reports
- AI response rendering
- Responsive medical dashboard

---

# 1️⃣1️⃣ Medical.html

## 📌 Purpose

Advanced medical document analyzer dashboard.

Features include:

- drag-drop upload
- disease cards
- anomaly visualization
- recommendation sections
- result panels

:contentReference[oaicite:1]{index=1}

---

# 1️⃣2️⃣ med_html_css.html

## 📌 Purpose

Rare disease identification interface.

Features:

- multi-tab dashboard
- offline mode
- urgency scoring
- confidence visualization
- console output simulation

:contentReference[oaicite:2]{index=2}

---

# 1️⃣3️⃣ test.html

## 📌 Purpose

Prescription Safety Analyzer UI.

---

# ✅ Features

- medicine extraction
- interaction analysis
- contraindication analysis
- generic medicine conversion
- clinical validation suggestions

:contentReference[oaicite:3]{index=3}

---

# 💊 Prescription Safety Analyzer

## AI Features

- Detect medicines
- Convert brand names to generic names
- Remove duplicates
- Analyze interactions
- Suggest tests
- Detect contraindications

---

# ✅ AI Technique Used

```text
Vision + Prompt Engineering + LLM Analysis
```

---

# 🧪 DATASETS USED

---

# 1️⃣ Medical Report Dataset: https://www.kaggle.com/datasets/dikshaasinghhh/bajaj

## Size

```text
819.2 MB
```

---

## Total Files

```text
426 files
```

---

# ✅ Dataset Includes

- Blood reports
- Liver function reports
- Peripheral smear reports
- Pathology scans
- Prescription images
- OCR-compatible documents
- Lab result reports

---

# ✅ Sample Images Provided

You shared:

- Liver Function Test report
- Peripheral smear / hematology report

These belong to the OCR medical analysis dataset.

---

# 2️⃣ Patient Symptom Dataset

Embedded directly inside code.

```python
PATIENT_CASES = [
    {"id": 1, "symptoms": "fever cough"},
    {"id": 2, "symptoms": "chest pain breathless"}
]
```

---

# Purpose

- semantic similarity
- patient retrieval
- symptom comparison

---

# 3️⃣ Medical Community Dataset

Embedded in:

```python
FEATURES.py
```

Example:

```python
COMMUNITIES = [
    {"name": "Respiratory Support Group"},
    {"name": "Diabetes Community"}
]
```

---

# Purpose

- patient clustering
- community recommendation
- support group assignment

---

# ⚙️ APIs & Services Used

---

# ✅ Gemini API

Purpose:

- reasoning
- medical summarization
- anomaly explanation
- treatment planning

---

# ✅ Supabase

Purpose:

- authentication
- OTP verification
- session persistence

---

# 📈 Key Achievements

✅ AI-powered medical report understanding

✅ OCR-based healthcare document analysis

✅ Semantic patient similarity engine

✅ Rare disease support system

✅ Prescription safety analysis

✅ Interactive medical dashboards

✅ JSON-based AI APIs

✅ FastAPI healthcare microservices

✅ Session-based authentication system

✅ Rule-based anomaly detection

---

# 🛡️ AI Safety Measures

The system avoids:

- direct diagnosis
- replacing doctors
- unsafe treatment instructions

Every AI output contains disclaimers such as:

```text
Not a substitute for professional medical advice
```

---

# 🚀 Future Improvements

Planned upgrades:

- RAG pipelines
- Vector databases
- Medical knowledge graphs
- Fine-tuned medical LLMs
- Multimodal medical AI
- Cloud deployment
- Docker orchestration
- Kubernetes deployment
- Real-time doctor APIs
- Speech-to-medical-text systems

---

# 📂 Missing / Recommended Files

---

# ✅ Backend

```text
requirements.txt
.env
config.py
utils.py
```

---

# ✅ Deployment

```text
Dockerfile
docker-compose.yml
Procfile
nginx.conf
```

---

# ✅ Frontend

```text
styles.css
main.js
```

---

# ✅ AI / ML

```text
evaluation_report.ipynb
training_logs/
datasets/
```

---

# ✅ Documentation

```text
README screenshots
API documentation
architecture diagrams
workflow diagrams
```

---

# 🧠 AI Concepts Demonstrated

- OCR
- NLP
- Semantic Search
- Embeddings
- Prompt Engineering
- Medical AI
- JSON-Constrained Generation
- Hybrid AI Systems
- Authentication Systems
- Evaluation Metrics
- AI Safety
- Rare Disease Detection
- Rule-Based AI
- Information Extraction

---


---
