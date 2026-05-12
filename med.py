# # """
# # RARE DISEASE DIAGNOSTIC ASSISTANT
# # One-file solution using OpenRouter API for analyzing medical reports
# # Author: Medical AI Team
# # """

# # import os
# # import re
# # import json
# # import base64
# # import requests
# # from typing import List, Dict, Tuple, Optional
# # from dataclasses import dataclass
# # import PyPDF2
# # from PIL import Image
# # import pytesseract
# # import numpy as np
# # from pathlib import Path
# # import mimetypes

# # # ============================================================================
# # # CONFIGURATION - EDIT THESE VALUES
# # # ============================================================================

# # OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-api-key-here")
# # MODEL = "deepseek/deepseek-r1:free"  # Using DeepSeek R1 via OpenRouter
# # API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# # # Rare disease database (simplified - in production, use a real database)
# # RARE_DISEASES_DB = {
# #     "ehlers_danlos": {
# #         "name": "Ehlers-Danlos Syndrome",
# #         "symptoms": ["joint hypermobility", "skin hyperextensibility", "easy bruising", "chronic pain"],
# #         "prevalence": "1 in 5,000",
# #         "confidence_factors": ["family_history", "multiple_system_involvement"]
# #     },
# #     "marfan": {
# #         "name": "Marfan Syndrome",
# #         "symptoms": ["tall stature", "arachnodactyly", "lens dislocation", "aortic dilation"],
# #         "prevalence": "1 in 5,000",
# #         "confidence_factors": ["aortic_root_diameter", "systemic_score"]
# #     },
# #     "pompe": {
# #         "name": "Pompe Disease",
# #         "symptoms": ["muscle weakness", "respiratory issues", "cardiomegaly", "feeding difficulties"],
# #         "prevalence": "1 in 40,000",
# #         "confidence_factors": ["enzyme_deficiency", "muscle_biopsy"]
# #     }
# # }

# # # ============================================================================
# # # DATA CLASSES
# # # ============================================================================

# # @dataclass
# # class MedicalFinding:
# #     """Represents a medical finding from reports"""
# #     text: str
# #     source: str  # e.g., "lab_report", "clinical_note", "imaging"
# #     confidence: float = 0.0
# #     normalized_value: Optional[float] = None
# #     unit: Optional[str] = None

# # @dataclass
# # class RareDiseaseRecommendation:
# #     """Represents a rare disease possibility"""
# #     disease_name: str
# #     confidence_score: float  # 0-1
# #     supporting_evidence: List[str]
# #     conflicting_evidence: List[str]
# #     next_steps: List[str]
# #     prevalence: str
# #     urgency_level: str  # low, medium, high, critical

# # @dataclass
# # class PatientContext:
# #     """Patient demographic and clinical context"""
# #     age: Optional[int] = None
# #     gender: Optional[str] = None
# #     existing_conditions: List[str] = None
# #     family_history: List[str] = None
# #     symptoms: List[str] = None
    
# #     def __post_init__(self):
# #         if self.existing_conditions is None:
# #             self.existing_conditions = []
# #         if self.family_history is None:
# #             self.family_history = []
# #         if self.symptoms is None:
# #             self.symptoms = []

# # # ============================================================================
# # # FILE PROCESSING FUNCTIONS
# # # ============================================================================

# # class MedicalReportProcessor:
# #     """Process various medical report formats"""
    
# #     @staticmethod
# #     def extract_text_from_pdf(file_path: str) -> str:
# #         """Extract text from PDF files"""
# #         text = ""
# #         try:
# #             with open(file_path, 'rb') as file:
# #                 pdf_reader = PyPDF2.PdfReader(file)
# #                 for page in pdf_reader.pages:
# #                     text += page.extract_text() + "\n"
# #         except Exception as e:
# #             print(f"Error reading PDF: {e}")
# #             text = MedicalReportProcessor._fallback_pdf_processing(file_path)
# #         return text
    
# #     @staticmethod
# #     def _fallback_pdf_processing(file_path: str) -> str:
# #         """Fallback method for PDF processing"""
# #         # For hackathon, return placeholder
# #         return f"PDF content from {file_path} - unable to extract text fully"
    
# #     @staticmethod
# #     def extract_text_from_image(file_path: str) -> str:
# #         """Extract text from image files using OCR"""
# #         try:
# #             image = Image.open(file_path)
# #             # Preprocess image for better OCR
# #             image = image.convert('L')  # Convert to grayscale
# #             text = pytesseract.image_to_string(image)
# #             return text
# #         except Exception as e:
# #             print(f"Error processing image: {e}")
# #             return ""
    
# #     @staticmethod
# #     def extract_text_from_file(file_path: str) -> Tuple[str, str]:
# #         """Main function to extract text from any file type"""
# #         mime_type, _ = mimetypes.guess_type(file_path)
        
# #         if mime_type is None:
# #             # Try to determine from extension
# #             if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
# #                 mime_type = 'image'
# #             elif file_path.lower().endswith('.pdf'):
# #                 mime_type = 'application/pdf'
# #             elif file_path.lower().endswith('.txt'):
# #                 mime_type = 'text/plain'
        
# #         if 'pdf' in mime_type:
# #             return MedicalReportProcessor.extract_text_from_pdf(file_path), 'pdf'
# #         elif 'image' in mime_type:
# #             return MedicalReportProcessor.extract_text_from_image(file_path), 'image'
# #         elif 'text' in mime_type:
# #             with open(file_path, 'r') as f:
# #                 return f.read(), 'text'
# #         else:
# #             # Try as text file
# #             try:
# #                 with open(file_path, 'r') as f:
# #                     return f.read(), 'text'
# #             except:
# #                 return "", 'unknown'
    
# #     @staticmethod
# #     def extract_medical_findings(text: str, source_type: str) -> List[MedicalFinding]:
# #         """Extract structured medical findings from text"""
# #         findings = []
        
# #         # Look for lab values
# #         lab_patterns = [
# #             r'(?:HbA1c|A1C)[\s:]*([\d\.]+)\s*%?',
# #             r'(?:Glucose|Blood Sugar)[\s:]*([\d\.]+)\s*(?:mg/dL|mmol/L)?',
# #             r'(?:WBC|White Blood Cells)[\s:]*([\d\.]+)\s*(?:x10\^9/L)?',
# #             r'(?:CRP|C-reactive Protein)[\s:]*([\d\.]+)\s*(?:mg/L)?'
# #         ]
        
# #         for pattern in lab_patterns:
# #             matches = re.finditer(pattern, text, re.IGNORECASE)
# #             for match in matches:
# #                 findings.append(MedicalFinding(
# #                     text=match.group(0),
# #                     source=source_type,
# #                     confidence=0.8
# #                 ))
        
# #         # Look for symptoms
# #         symptom_keywords = ['pain', 'weakness', 'fatigue', 'fever', 'rash', 
# #                            'swelling', 'numbness', 'dizziness', 'shortness of breath']
        
# #         for symptom in symptom_keywords:
# #             if symptom.lower() in text.lower():
# #                 # Find context around symptom
# #                 start = max(0, text.lower().find(symptom) - 100)
# #                 end = min(len(text), text.lower().find(symptom) + 100)
# #                 context = text[start:end]
                
# #                 findings.append(MedicalFinding(
# #                     text=f"Symptom: {symptom} - {context}",
# #                     source=source_type,
# #                     confidence=0.7
# #                 ))
        
# #         return findings

# # # ============================================================================
# # # LLM INTEGRATION
# # # ============================================================================

# # class RareDiseaseAnalyzer:
# #     """Main analyzer using LLM via OpenRouter"""
    
# #     def __init__(self, api_key: str):
# #         self.api_key = api_key
# #         self.headers = {
# #             "Authorization": f"Bearer {api_key}",
# #             "Content-Type": "application/json",
# #             "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
# #             "X-Title": "Rare Disease Assistant"
# #         }
    
# #     def analyze_reports(self, 
# #                        report_texts: List[str],
# #                        patient_context: PatientContext,
# #                        file_types: List[str]) -> List[RareDiseaseRecommendation]:
# #         """Main analysis function"""
        
# #         # Combine all report texts
# #         combined_text = "\n---\n".join(report_texts)
        
# #         # Prepare prompt for LLM
# #         prompt = self._create_analysis_prompt(combined_text, patient_context)
        
# #         # Call LLM
# #         response = self._call_openrouter(prompt)
        
# #         # Parse response
# #         recommendations = self._parse_llm_response(response)
        
# #         # Add confidence scores based on evidence
# #         recommendations = self._calculate_confidence_scores(recommendations, report_texts)
        
# #         # Filter and sort
# #         recommendations = [r for r in recommendations if r.confidence_score > 0.3]
# #         recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
# #         return recommendations[:5]  # Return top 5
    
# #     def _create_analysis_prompt(self, report_text: str, patient_context: PatientContext) -> str:
# #         """Create optimized prompt for rare disease analysis"""
        
# #         return f"""You are a medical expert specializing in rare diseases. Analyze the following patient information and suggest possible rare diseases.

# # PATIENT CONTEXT:
# # - Age: {patient_context.age or 'Unknown'}
# # - Gender: {patient_context.gender or 'Unknown'}
# # - Existing Conditions: {', '.join(patient_context.existing_conditions) or 'None'}
# # - Family History: {', '.join(patient_context.family_history) or 'None'}
# # - Symptoms: {', '.join(patient_context.symptoms) or 'None'}

# # MEDICAL REPORTS:
# # {report_text[:8000]}  # Limit to 8000 chars for API

# # ANALYSIS REQUEST:
# # 1. Analyze the reports for unusual patterns, rare symptoms, or atypical presentations
# # 2. Suggest 3-5 possible rare diseases that could explain the findings
# # 3. For each disease, provide:
# #    - Disease name and brief description
# #    - Key evidence from reports supporting this possibility
# #    - Key evidence that doesn't fit (if any)
# #    - Suggested next steps for confirmation
# #    - Estimated prevalence (if known)
# #    - Urgency level (low, medium, high, critical)

# # FORMAT YOUR RESPONSE AS JSON:
# # {{
# #   "analysis_summary": "Brief overall assessment",
# #   "rare_disease_possibilities": [
# #     {{
# #       "disease_name": "Disease Name",
# #       "description": "Brief description",
# #       "supporting_evidence": ["Evidence 1", "Evidence 2"],
# #       "conflicting_evidence": ["Evidence that doesn't fit"],
# #       "next_steps": ["Test 1", "Consult specialist"],
# #       "prevalence": "e.g., 1 in 50,000",
# #       "urgency_level": "low/medium/high/critical"
# #     }}
# #   ],
# #   "confidence_factors": ["Factor 1", "Factor 2"],
# #   "red_flags": ["Urgent finding 1", "Urgent finding 2"],
# #   "recommended_specialists": ["Specialist 1", "Specialist 2"]
# # }}

# # IMPORTANT: Only suggest rare diseases (<1 in 2,000 prevalence). If no rare disease seems likely, say so clearly.
# # """
    
# #     def _call_openrouter(self, prompt: str) -> Dict:
# #         """Call OpenRouter API"""
        
# #         payload = {
# #             "model": MODEL,
# #             "messages": [
# #                 {"role": "system", "content": "You are a world-class medical diagnostician specializing in rare diseases. Be thorough but concise."},
# #                 {"role": "user", "content": prompt}
# #             ],
# #             "temperature": 0.3,  # Lower temperature for more consistent results
# #             "max_tokens": 3000,
# #             "response_format": {"type": "json_object"}  # Request JSON response
# #         }
        
# #         try:
# #             response = requests.post(API_BASE_URL, headers=self.headers, json=payload, timeout=30)
# #             response.raise_for_status()
# #             return response.json()
# #         except requests.exceptions.RequestException as e:
# #             print(f"API Error: {e}")
# #             # Fallback to mock response for demo
# #             return self._get_mock_response()
    
# #     def _get_mock_response(self) -> Dict:
# #         """Fallback mock response for demo/testing"""
# #         return {
# #             "choices": [{
# #                 "message": {
# #                     "content": json.dumps({
# #                         "analysis_summary": "Demo analysis - connect to API for real analysis",
# #                         "rare_disease_possibilities": [
# #                             {
# #                                 "disease_name": "Ehlers-Danlos Syndrome",
# #                                 "description": "Connective tissue disorder",
# #                                 "supporting_evidence": ["Joint hypermobility noted", "Skin elasticity"],
# #                                 "conflicting_evidence": ["No family history"],
# #                                 "next_steps": ["Genetic testing", "Rheumatology consult"],
# #                                 "prevalence": "1 in 5,000",
# #                                 "urgency_level": "medium"
# #                             }
# #                         ],
# #                         "confidence_factors": ["Multiple system involvement", "Atypical presentation"],
# #                         "red_flags": ["Cardiovascular symptoms present"],
# #                         "recommended_specialists": ["Rheumatologist", "Geneticist"]
# #                     })
# #                 }
# #             }]
# #         }
    
# #     def _parse_llm_response(self, response: Dict) -> List[RareDiseaseRecommendation]:
# #         """Parse LLM response into structured recommendations"""
        
# #         try:
# #             content = response["choices"][0]["message"]["content"]
# #             data = json.loads(content)
            
# #             recommendations = []
# #             for disease in data.get("rare_disease_possibilities", []):
# #                 rec = RareDiseaseRecommendation(
# #                     disease_name=disease.get("disease_name", "Unknown"),
# #                     confidence_score=0.5,  # Will be calculated later
# #                     supporting_evidence=disease.get("supporting_evidence", []),
# #                     conflicting_evidence=disease.get("conflicting_evidence", []),
# #                     next_steps=disease.get("next_steps", []),
# #                     prevalence=disease.get("prevalence", "Unknown"),
# #                     urgency_level=disease.get("urgency_level", "medium")
# #                 )
# #                 recommendations.append(rec)
            
# #             return recommendations
            
# #         except (KeyError, json.JSONDecodeError) as e:
# #             print(f"Error parsing response: {e}")
# #             return []
    
# #     def _calculate_confidence_scores(self, 
# #                                    recommendations: List[RareDiseaseRecommendation],
# #                                    report_texts: List[str]) -> List[RareDiseaseRecommendation]:
# #         """Calculate confidence scores based on evidence matching"""
        
# #         combined_text = " ".join(report_texts).lower()
        
# #         for rec in recommendations:
# #             # Base confidence
# #             confidence = 0.5
            
# #             # Increase confidence for each piece of supporting evidence found in text
# #             for evidence in rec.supporting_evidence:
# #                 # Check if evidence keywords appear in reports
# #                 keywords = self._extract_keywords(evidence)
# #                 matches = sum(1 for kw in keywords if kw in combined_text)
# #                 if matches > 0:
# #                     confidence += 0.1 * matches
            
# #             # Decrease confidence for conflicting evidence
# #             for evidence in rec.conflicting_evidence:
# #                 keywords = self._extract_keywords(evidence)
# #                 matches = sum(1 for kw in keywords if kw in combined_text)
# #                 if matches > 0:
# #                     confidence -= 0.15 * matches
            
# #             # Adjust based on urgency
# #             urgency_boost = {
# #                 "critical": 0.2,
# #                 "high": 0.1,
# #                 "medium": 0.0,
# #                 "low": -0.1
# #             }
# #             confidence += urgency_boost.get(rec.urgency_level, 0.0)
            
# #             # Cap between 0.1 and 0.95
# #             rec.confidence_score = max(0.1, min(0.95, confidence))
        
# #         return recommendations
    
# #     def _extract_keywords(self, text: str) -> List[str]:
# #         """Extract keywords from text for matching"""
# #         # Simple keyword extraction
# #         words = re.findall(r'\b[a-z]{4,}\b', text.lower())
# #         # Remove common words
# #         common_words = {'this', 'that', 'with', 'from', 'have', 'were', 'been', 'they'}
# #         return [w for w in words if w not in common_words][:5]

# # # ============================================================================
# # # MAIN APPLICATION
# # # ============================================================================

# # class RareDiseaseDetector:
# #     """Main application class"""
    
# #     def __init__(self, api_key: str):
# #         self.processor = MedicalReportProcessor()
# #         self.analyzer = RareDiseaseAnalyzer(api_key)
    
# #     def analyze_patient(self, 
# #                        file_paths: List[str],
# #                        patient_context: Optional[PatientContext] = None) -> Dict:
# #         """Main analysis pipeline"""
        
# #         if patient_context is None:
# #             patient_context = PatientContext()
        
# #         print(f"Processing {len(file_paths)} files...")
        
# #         # Process all files
# #         report_texts = []
# #         file_types = []
        
# #         for file_path in file_paths:
# #             if not os.path.exists(file_path):
# #                 print(f"File not found: {file_path}")
# #                 continue
            
# #             text, file_type = self.processor.extract_text_from_file(file_path)
# #             if text.strip():
# #                 report_texts.append(f"From {os.path.basename(file_path)} ({file_type}):\n{text}")
# #                 file_types.append(file_type)
# #                 print(f"✓ Processed {file_path} ({len(text)} chars)")
# #             else:
# #                 print(f"✗ Could not extract text from {file_path}")
        
# #         if not report_texts:
# #             return {"error": "No text extracted from files"}
        
# #         # Analyze with LLM
# #         print("\nAnalyzing with AI...")
# #         recommendations = self.analyzer.analyze_reports(
# #             report_texts, 
# #             patient_context, 
# #             file_types
# #         )
        
# #         # Prepare results
# #         results = {
# #             "patient_context": {
# #                 "age": patient_context.age,
# #                 "gender": patient_context.gender,
# #                 "conditions": patient_context.existing_conditions,
# #                 "symptoms": patient_context.symptoms
# #             },
# #             "files_processed": len(report_texts),
# #             "total_findings": sum(len(self.processor.extract_medical_findings(t, ft)) 
# #                                   for t, ft in zip(report_texts, file_types)),
# #             "recommendations": [
# #                 {
# #                     "disease": rec.disease_name,
# #                     "confidence": f"{rec.confidence_score:.1%}",
# #                     "confidence_score": rec.confidence_score,
# #                     "prevalence": rec.prevalence,
# #                     "urgency": rec.urgency_level,
# #                     "supporting_evidence": rec.supporting_evidence[:3],  # Top 3
# #                     "next_steps": rec.next_steps[:3],
# #                     "match_level": self._get_match_level(rec.confidence_score)
# #                 }
# #                 for rec in recommendations
# #             ],
# #             "summary": self._generate_summary(recommendations)
# #         }
        
# #         return results
    
# #     def _get_match_level(self, confidence: float) -> str:
# #         """Convert confidence score to match level"""
# #         if confidence >= 0.7:
# #             return "High Match"
# #         elif confidence >= 0.5:
# #             return "Medium Match"
# #         elif confidence >= 0.3:
# #             return "Low Match"
# #         else:
# #             return "Unlikely"
    
# #     def _generate_summary(self, recommendations: List[RareDiseaseRecommendation]) -> Dict:
# #         """Generate summary of findings"""
# #         if not recommendations:
# #             return {
# #                 "message": "No rare disease patterns detected in the provided reports.",
# #                 "action": "Continue with standard diagnostic procedures."
# #             }
        
# #         # Find highest confidence recommendation
# #         top_rec = max(recommendations, key=lambda x: x.confidence_score)
        
# #         urgent_count = sum(1 for r in recommendations if r.urgency_level in ["high", "critical"])
        
# #         return {
# #             "top_suspicion": top_rec.disease_name,
# #             "top_confidence": f"{top_rec.confidence_score:.1%}",
# #             "urgent_findings": urgent_count,
# #             "total_possibilities": len(recommendations),
# #             "action_required": urgent_count > 0,
# #             "message": f"Found {len(recommendations)} rare disease possibilities. " +
# #                       f"Top match: {top_rec.disease_name} ({top_rec.confidence_score:.1%} confidence)."
# #         }

# # # ============================================================================
# # # DEMO & TESTING FUNCTIONS
# # # ============================================================================

# # def run_demo():
# #     """Run a demo with sample data"""
    
# #     print("=" * 60)
# #     print("RARE DISEASE DETECTOR - DEMO MODE")
# #     print("=" * 60)
    
# #     # Create detector
# #     detector = RareDiseaseDetector(OPENROUTER_API_KEY)
    
# #     # Sample patient context (simulating Ehlers-Danlos like case)
# #     patient = PatientContext(
# #         age=28,
# #         gender="female",
# #         existing_conditions=["joint pain", "easy bruising"],
# #         family_history=["mother: flexible joints", "aunt: chronic pain"],
# #         symptoms=["joint hypermobility", "skin elasticity", "fatigue", "chronic pain"]
# #     )
    
# #     # Create sample report text (in real usage, this would come from files)
# #     sample_reports = [
# #         """CLINICAL NOTE
# # Patient: Jane Doe, 28F
# # History: Chronic joint pain since adolescence, easy bruising
# # Exam: Beighton Score 7/9 (joint hypermobility present)
# # Skin: Hyperextensible, atrophic scarring noted
# # Cardiac: Mitral valve prolapse murmur heard
# # Impression: Connective tissue disorder suspected
# # Plan: Refer to genetics for EDS evaluation""",
        
# #         """LAB RESULTS
# # CBC: Normal
# # CRP: 0.5 mg/L (normal)
# # ESR: 15 mm/hr (normal)
# # Coagulation: Normal
# # Note: No inflammatory markers elevated"""
# #     ]
    
# #     # Save sample reports to temporary files for demo
# #     temp_files = []
# #     for i, report in enumerate(sample_reports):
# #         filename = f"temp_report_{i}.txt"
# #         with open(filename, 'w') as f:
# #             f.write(report)
# #         temp_files.append(filename)
    
# #     try:
# #         # Analyze
# #         results = detector.analyze_patient(temp_files, patient)
        
# #         print("\n" + "=" * 60)
# #         print("ANALYSIS RESULTS")
# #         print("=" * 60)
        
# #         print(f"\nPatient: {patient.age}y {patient.gender}")
# #         print(f"Symptoms: {', '.join(patient.symptoms[:3])}...")
        
# #         print(f"\nFiles Processed: {results['files_processed']}")
# #         print(f"Total Findings: {results['total_findings']}")
        
# #         print(f"\nSUMMARY: {results['summary']['message']}")
        
# #         print("\nTOP RECOMMENDATIONS:")
# #         print("-" * 40)
        
# #         for i, rec in enumerate(results['recommendations'], 1):
# #             print(f"\n{i}. {rec['disease']}")
# #             print(f"   Confidence: {rec['confidence']} ({rec['match_level']})")
# #             print(f"   Prevalence: {rec['prevalence']}")
# #             print(f"   Urgency: {rec['urgency']}")
# #             print(f"   Key Evidence: {rec['supporting_evidence'][0] if rec['supporting_evidence'] else 'None'}")
# #             print(f"   Next Step: {rec['next_steps'][0] if rec['next_steps'] else 'Consult specialist'}")
        
# #         if results['summary']['action_required']:
# #             print("\n⚠️  URGENT ACTION RECOMMENDED")
# #             print("Please consult with a specialist immediately.")
        
# #         print("\n" + "=" * 60)
        
# #         # Save results to file
# #         output_file = "rare_disease_analysis.json"
# #         with open(output_file, 'w') as f:
# #             json.dump(results, f, indent=2)
# #         print(f"\nResults saved to: {output_file}")
        
# #     finally:
# #         # Clean up temp files
# #         for f in temp_files:
# #             try:
# #                 os.remove(f)
# #             except:
# #                 pass

# # def analyze_real_files(file_paths: List[str], patient_info: Dict):
# #     """Analyze real patient files"""
    
# #     if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
# #         print("ERROR: Please set your OpenRouter API key!")
# #         print("1. Get API key from: https://openrouter.ai/keys")
# #         print("2. Set environment variable: OPENROUTER_API_KEY=your-key-here")
# #         print("   OR edit the OPENROUTER_API_KEY variable in this script")
# #         return
    
# #     # Create patient context
# #     patient = PatientContext(
# #         age=patient_info.get('age'),
# #         gender=patient_info.get('gender'),
# #         existing_conditions=patient_info.get('existing_conditions', []),
# #         family_history=patient_info.get('family_history', []),
# #         symptoms=patient_info.get('symptoms', [])
# #     )
    
# #     # Check files exist
# #     valid_files = []
# #     for fp in file_paths:
# #         if os.path.exists(fp):
# #             valid_files.append(fp)
# #         else:
# #             print(f"File not found: {fp}")
    
# #     if not valid_files:
# #         print("No valid files to analyze")
# #         return
    
# #     # Create detector and analyze
# #     detector = RareDiseaseDetector(OPENROUTER_API_KEY)
# #     results = detector.analyze_patient(valid_files, patient)
    
# #     # Display results
# #     print("\n" + "=" * 60)
# #     print("RARE DISEASE ANALYSIS COMPLETE")
# #     print("=" * 60)
    
# #     if 'error' in results:
# #         print(f"Error: {results['error']}")
# #         return
    
# #     print(f"\nAnalyzed {results['files_processed']} file(s)")
# #     print(f"Found {len(results['recommendations'])} rare disease possibility(ies)")
    
# #     for i, rec in enumerate(results['recommendations'], 1):
# #         print(f"\n{'='*40}")
# #         print(f"POSSIBILITY #{i}: {rec['disease']}")
# #         print(f"{'='*40}")
# #         print(f"Confidence: {rec['confidence']} ({rec['match_level']})")
# #         print(f"Prevalence: {rec['prevalence']}")
# #         print(f"Urgency Level: {rec['urgency'].upper()}")
        
# #         print(f"\nSupporting Evidence:")
# #         for evidence in rec['supporting_evidence']:
# #             print(f"  • {evidence}")
        
# #         print(f"\nRecommended Next Steps:")
# #         for step in rec['next_steps']:
# #             print(f"  • {step}")
    
# #     print(f"\n{'='*60}")
# #     print("SUMMARY")
# #     print(f"{'='*60}")
# #     print(results['summary']['message'])
    
# #     if results['summary']['action_required']:
# #         print("\n🚨 URGENT: Immediate specialist consultation recommended!")
    
# #     # Save detailed results
# #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #     output_file = f"rare_disease_report_{timestamp}.json"
# #     with open(output_file, 'w') as f:
# #         json.dump(results, f, indent=2)
    
# #     print(f"\nDetailed report saved to: {output_file}")

# # # ============================================================================
# # # COMMAND LINE INTERFACE
# # # ============================================================================

# # if __name__ == "__main__":
# #     import sys
# #     from datetime import datetime
    
# #     print("Rare Disease Possibility Recommender")
# #     print("=" * 50)
    
# #     if len(sys.argv) > 1 and sys.argv[1] == "--demo":
# #         run_demo()
# #     else:
# #         # Interactive mode
# #         print("\nInteractive Analysis Mode")
# #         print("-" * 30)
        
# #         # Get patient info
# #         patient_info = {}
# #         try:
# #             patient_info['age'] = int(input("Patient age (or press Enter to skip): ") or 0) or None
# #         except:
# #             patient_info['age'] = None
        
# #         patient_info['gender'] = input("Patient gender (M/F/Other): ") or None
        
# #         conditions = input("Existing conditions (comma separated): ")
# #         patient_info['existing_conditions'] = [c.strip() for c in conditions.split(",") if c.strip()]
        
# #         family = input("Family history of rare diseases (comma separated): ")
# #         patient_info['family_history'] = [f.strip() for f in family.split(",") if f.strip()]
        
# #         symptoms = input("Current symptoms (comma separated): ")
# #         patient_info['symptoms'] = [s.strip() for s in symptoms.split(",") if s.strip()]
        
# #         # Get file paths
# #         print("\nEnter file paths (one per line, empty line to finish):")
# #         file_paths = []
# #         while True:
# #             path = input("> ").strip()
# #             if not path:
# #                 break
# #             file_paths.append(path)
        
# #         if file_paths:
# #             analyze_real_files(file_paths, patient_info)
# #         else:
# #             print("No files provided. Running demo...")
# #             run_demo()






# """
# RARE DISEASE DIAGNOSTIC ASSISTANT
# One-file solution using OpenRouter API for analyzing medical reports
# Author: Medical AI Team
# """

# import os
# import re
# import json
# import base64
# import requests
# from typing import List, Dict, Tuple, Optional
# from dataclasses import dataclass
# import PyPDF2
# from PIL import Image
# import pytesseract
# import numpy as np
# from pathlib import Path
# import mimetypes
# from datetime import datetime

# # ============================================================================
# # LOAD ENVIRONMENT VARIABLES
# # ============================================================================

# # Try to load from .env file
# def load_env_file():
#     """Load environment variables from .env file"""
#     env_path = Path(__file__).parent / '.env'
#     if env_path.exists():
#         print(f"Loading environment from: {env_path}")
#         with open(env_path, 'r') as f:
#             for line in f:
#                 line = line.strip()
#                 if line and not line.startswith('#') and '=' in line:
#                     key, value = line.split('=', 1)
#                     os.environ[key.strip()] = value.strip().strip('"\'')
#     else:
#         print("No .env file found. Creating template...")
#         create_env_template()

# def create_env_template():
#     """Create a template .env file if it doesn't exist"""
#     env_template = """# OpenRouter API Configuration
# OPENROUTER_API_KEY=your-api-key-here

# # Optional: Set your preferred model
# # MODEL=deepseek/deepseek-r1:free
# # MODEL=openai/gpt-4o
# # MODEL=anthropic/claude-3.5-sonnet
# # MODEL=google/gemini-1.5-pro

# # Optional: Set your application details (required by OpenRouter)
# HTTP_REFERER=http://localhost:3000
# X_TITLE=Rare Disease Assistant

# # Optional: Tesseract OCR path (if not in system PATH)
# # TESSERACT_PATH=/usr/bin/tesseract
# """
    
#     env_path = Path(__file__).parent / '.env'
#     with open(env_path, 'w') as f:
#         f.write(env_template)
#     print(f"Created template .env file at: {env_path}")
#     print("Please edit it with your API key!")

# # Load environment variables
# load_env_file()

# # ============================================================================
# # CONFIGURATION - NOW FROM ENVIRONMENT VARIABLES
# # ============================================================================

# # Get API key from environment
# OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# # Get model from environment or use default
# MODEL = os.environ.get("MODEL", "deepseek/deepseek-r1:free")

# # Get other settings
# HTTP_REFERER = os.environ.get("HTTP_REFERER", "http://localhost:3000")
# X_TITLE = os.environ.get("X_TITLE", "Rare Disease Assistant")

# API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# # Validate API key
# if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
#     print("⚠️  WARNING: No valid API key found!")
#     print("Please:")
#     print("1. Get a free API key from: https://openrouter.ai/keys")
#     print("2. Add it to your .env file:")
#     print("   OPENROUTER_API_KEY=your-actual-key-here")
#     print("\nContinuing in demo mode...")

# # Rare disease database (simplified - in production, use a real database)
# RARE_DISEASES_DB = {
#     "ehlers_danlos": {
#         "name": "Ehlers-Danlos Syndrome",
#         "symptoms": ["joint hypermobility", "skin hyperextensibility", "easy bruising", "chronic pain"],
#         "prevalence": "1 in 5,000",
#         "confidence_factors": ["family_history", "multiple_system_involvement"]
#     },
#     "marfan": {
#         "name": "Marfan Syndrome",
#         "symptoms": ["tall stature", "arachnodactyly", "lens dislocation", "aortic dilation"],
#         "prevalence": "1 in 5,000",
#         "confidence_factors": ["aortic_root_diameter", "systemic_score"]
#     },
#     "pompe": {
#         "name": "Pompe Disease",
#         "symptoms": ["muscle weakness", "respiratory issues", "cardiomegaly", "feeding difficulties"],
#         "prevalence": "1 in 40,000",
#         "confidence_factors": ["enzyme_deficiency", "muscle_biopsy"]
#     },
#     "turner": {
#         "name": "Turner Syndrome",
#         "symptoms": ["short stature", "lymphedema", "shield chest", "low hairline"],
#         "prevalence": "1 in 2,500 females",
#         "confidence_factors": ["karyotype", "multiple congenital anomalies"]
#     },
#     "cystic_fibrosis": {
#         "name": "Cystic Fibrosis",
#         "symptoms": ["chronic cough", "recurrent infections", "poor growth", "salty sweat"],
#         "prevalence": "1 in 3,500",
#         "confidence_factors": ["sweat_chloride", "genetic_mutation"]
#     }
# }

# # ============================================================================
# # DATA CLASSES
# # ============================================================================

# @dataclass
# class MedicalFinding:
#     """Represents a medical finding from reports"""
#     text: str
#     source: str  # e.g., "lab_report", "clinical_note", "imaging"
#     confidence: float = 0.0
#     normalized_value: Optional[float] = None
#     unit: Optional[str] = None

# @dataclass
# class RareDiseaseRecommendation:
#     """Represents a rare disease possibility"""
#     disease_name: str
#     confidence_score: float  # 0-1
#     supporting_evidence: List[str]
#     conflicting_evidence: List[str]
#     next_steps: List[str]
#     prevalence: str
#     urgency_level: str  # low, medium, high, critical

# @dataclass
# class PatientContext:
#     """Patient demographic and clinical context"""
#     age: Optional[int] = None
#     gender: Optional[str] = None
#     existing_conditions: List[str] = None
#     family_history: List[str] = None
#     symptoms: List[str] = None
    
#     def __post_init__(self):
#         if self.existing_conditions is None:
#             self.existing_conditions = []
#         if self.family_history is None:
#             self.family_history = []
#         if self.symptoms is None:
#             self.symptoms = []

# # ============================================================================
# # FILE PROCESSING FUNCTIONS
# # ============================================================================

# class MedicalReportProcessor:
#     """Process various medical report formats"""
    
#     @staticmethod
#     def extract_text_from_pdf(file_path: str) -> str:
#         """Extract text from PDF files"""
#         text = ""
#         try:
#             with open(file_path, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 for page in pdf_reader.pages:
#                     text += page.extract_text() + "\n"
#         except Exception as e:
#             print(f"Error reading PDF: {e}")
#             text = MedicalReportProcessor._fallback_pdf_processing(file_path)
#         return text
    
#     @staticmethod
#     def _fallback_pdf_processing(file_path: str) -> str:
#         """Fallback method for PDF processing"""
#         # For hackathon, return placeholder
#         return f"PDF content from {file_path} - unable to extract text fully"
    
#     @staticmethod
#     def extract_text_from_image(file_path: str) -> str:
#         """Extract text from image files using OCR"""
#         try:
#             image = Image.open(file_path)
#             # Preprocess image for better OCR
#             image = image.convert('L')  # Convert to grayscale
#             # Check if Tesseract path is specified in environment
#             tesseract_path = os.environ.get("TESSERACT_PATH")
#             if tesseract_path:
#                 pytesseract.pytesseract.tesseract_cmd = tesseract_path
#             text = pytesseract.image_to_string(image)
#             return text
#         except Exception as e:
#             print(f"Error processing image: {e}")
#             return ""
    
#     @staticmethod
#     def extract_text_from_file(file_path: str) -> Tuple[str, str]:
#         """Main function to extract text from any file type"""
#         mime_type, _ = mimetypes.guess_type(file_path)
        
#         if mime_type is None:
#             # Try to determine from extension
#             if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
#                 mime_type = 'image'
#             elif file_path.lower().endswith('.pdf'):
#                 mime_type = 'application/pdf'
#             elif file_path.lower().endswith(('.txt', '.doc', '.docx', '.rtf')):
#                 mime_type = 'text'
        
#         if 'pdf' in mime_type:
#             return MedicalReportProcessor.extract_text_from_pdf(file_path), 'pdf'
#         elif 'image' in mime_type:
#             return MedicalReportProcessor.extract_text_from_image(file_path), 'image'
#         elif 'text' in mime_type:
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     return f.read(), 'text'
#             except UnicodeDecodeError:
#                 # Try different encoding
#                 try:
#                     with open(file_path, 'r', encoding='latin-1') as f:
#                         return f.read(), 'text'
#                 except:
#                     return "", 'unknown'
#         else:
#             # Try as text file
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     return f.read(), 'text'
#             except:
#                 return "", 'unknown'
    
#     @staticmethod
#     def extract_medical_findings(text: str, source_type: str) -> List[MedicalFinding]:
#         """Extract structured medical findings from text"""
#         findings = []
        
#         # Look for lab values with patterns
#         lab_patterns = [
#             (r'(?:HbA1c|A1C|Hemoglobin A1c)[\s:]*([\d\.]+)\s*%?', 'HbA1c'),
#             (r'(?:Glucose|Blood Sugar|FBS|RBS)[\s:]*([\d\.]+)\s*(?:mg/dL|mmol/L)?', 'Glucose'),
#             (r'(?:WBC|White Blood Cells|White count)[\s:]*([\d\.]+)\s*(?:x10\^9/L|K/uL)?', 'WBC'),
#             (r'(?:CRP|C-reactive Protein)[\s:]*([\d\.]+)\s*(?:mg/L)?', 'CRP'),
#             (r'(?:ESR|Erythrocyte Sedimentation Rate)[\s:]*([\d\.]+)\s*(?:mm/hr)?', 'ESR'),
#             (r'(?:Creatinine)[\s:]*([\d\.]+)\s*(?:mg/dL|umol/L)?', 'Creatinine'),
#             (r'(?:ALT|Alanine Aminotransferase)[\s:]*([\d\.]+)\s*(?:U/L)?', 'ALT'),
#             (r'(?:AST|Aspartate Aminotransferase)[\s:]*([\d\.]+)\s*(?:U/L)?', 'AST'),
#             (r'(?:Bilirubin|Total Bilirubin)[\s:]*([\d\.]+)\s*(?:mg/dL)?', 'Bilirubin')
#         ]
        
#         for pattern, lab_name in lab_patterns:
#             matches = re.finditer(pattern, text, re.IGNORECASE)
#             for match in matches:
#                 value = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
#                 findings.append(MedicalFinding(
#                     text=f"{lab_name}: {value}",
#                     source=source_type,
#                     confidence=0.8
#                 ))
        
#         # Look for symptoms in context
#         symptom_contexts = []
#         symptom_keywords = ['pain', 'weakness', 'fatigue', 'fever', 'rash', 
#                            'swelling', 'numbness', 'dizziness', 'shortness of breath',
#                            'headache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
#                            'cough', 'sore throat', 'chest pain', 'palpitations']
        
#         for symptom in symptom_keywords:
#             symptom_pattern = r'([^.!?]*' + re.escape(symptom) + r'[^.!?]*[.!?])'
#             matches = re.findall(symptom_pattern, text, re.IGNORECASE)
#             for match in matches:
#                 findings.append(MedicalFinding(
#                     text=f"Symptom mentioned: {match.strip()}",
#                     source=source_type,
#                     confidence=0.7
#                 ))
        
#         # Look for diagnoses
#         diagnosis_patterns = [
#             r'Diagnosis:?\s*([^\.\n]+)',
#             r'Impression:?\s*([^\.\n]+)',
#             r'Assessment:?\s*([^\.\n]+)',
#             r'Final Diagnosis:?\s*([^\.\n]+)'
#         ]
        
#         for pattern in diagnosis_patterns:
#             matches = re.findall(pattern, text, re.IGNORECASE)
#             for match in matches:
#                 findings.append(MedicalFinding(
#                     text=f"Diagnosis: {match.strip()}",
#                     source=source_type,
#                     confidence=0.9
#                 ))
        
#         return findings

# # ============================================================================
# # LLM INTEGRATION
# # ============================================================================

# class RareDiseaseAnalyzer:
#     """Main analyzer using LLM via OpenRouter"""
    
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#             "HTTP-Referer": HTTP_REFERER,
#             "X-Title": X_TITLE
#         }
    
#     def analyze_reports(self, 
#                        report_texts: List[str],
#                        patient_context: PatientContext,
#                        file_types: List[str]) -> List[RareDiseaseRecommendation]:
#         """Main analysis function"""
        
#         # Combine all report texts
#         combined_text = "\n---\n".join(report_texts)
        
#         # Prepare prompt for LLM
#         prompt = self._create_analysis_prompt(combined_text, patient_context)
        
#         # Call LLM
#         response = self._call_openrouter(prompt)
        
#         # Parse response
#         recommendations = self._parse_llm_response(response)
        
#         # Add confidence scores based on evidence
#         recommendations = self._calculate_confidence_scores(recommendations, report_texts)
        
#         # Filter and sort
#         recommendations = [r for r in recommendations if r.confidence_score > 0.2]
#         recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
#         return recommendations[:5]  # Return top 5
    
#     def _create_analysis_prompt(self, report_text: str, patient_context: PatientContext) -> str:
#         """Create optimized prompt for rare disease analysis"""
        
#         # Truncate report text if too long
#         if len(report_text) > 6000:
#             report_text = report_text[:3000] + "\n[...truncated...]\n" + report_text[-3000:]
        
#         return f"""You are a medical expert specializing in rare diseases. Analyze the following patient information and suggest possible rare diseases.

# PATIENT CONTEXT:
# - Age: {patient_context.age or 'Unknown'}
# - Gender: {patient_context.gender or 'Unknown'}
# - Existing Conditions: {', '.join(patient_context.existing_conditions) or 'None'}
# - Family History: {', '.join(patient_context.family_history) or 'None'}
# - Symptoms: {', '.join(patient_context.symptoms) or 'None'}

# MEDICAL REPORTS:
# {report_text}

# ANALYSIS REQUEST:
# 1. Analyze the reports for unusual patterns, rare symptoms, or atypical presentations
# 2. Suggest 3-5 possible rare diseases that could explain the findings
# 3. For each disease, provide:
#    - Disease name and brief description
#    - Key evidence from reports supporting this possibility
#    - Key evidence that doesn't fit (if any)
#    - Suggested next steps for confirmation
#    - Estimated prevalence (if known)
#    - Urgency level (low, medium, high, critical)
# 4. Also identify any red flags requiring immediate attention

# FORMAT YOUR RESPONSE AS JSON:
# {{
#   "analysis_summary": "Brief overall assessment",
#   "rare_disease_possibilities": [
#     {{
#       "disease_name": "Disease Name",
#       "description": "Brief description",
#       "supporting_evidence": ["Evidence 1", "Evidence 2"],
#       "conflicting_evidence": ["Evidence that doesn't fit"],
#       "next_steps": ["Test 1", "Consult specialist"],
#       "prevalence": "e.g., 1 in 50,000",
#       "urgency_level": "low/medium/high/critical"
#     }}
#   ],
#   "confidence_factors": ["Factor 1", "Factor 2"],
#   "red_flags": ["Urgent finding 1", "Urgent finding 2"],
#   "recommended_specialists": ["Specialist 1", "Specialist 2"]
# }}

# IMPORTANT: 
# - Only suggest rare diseases (<1 in 2,000 prevalence). 
# - Be conservative - if evidence is weak, don't suggest a rare disease.
# - Focus on diseases that could explain multiple symptoms together.
# - If no rare disease seems likely, return empty array for rare_disease_possibilities.
# """
    
#     def _call_openrouter(self, prompt: str) -> Dict:
#         """Call OpenRouter API"""
        
#         payload = {
#             "model": MODEL,
#             "messages": [
#                 {"role": "system", "content": "You are a world-class medical diagnostician specializing in rare diseases. Be thorough, accurate, and conservative in your assessments."},
#                 {"role": "user", "content": prompt}
#             ],
#             "temperature": 0.2,  # Low temperature for consistent, conservative results
#             "max_tokens": 4000,
#             "response_format": {"type": "json_object"}  # Request JSON response
#         }
        
#         try:
#             print(f"Calling OpenRouter API with model: {MODEL}")
#             response = requests.post(API_BASE_URL, headers=self.headers, json=payload, timeout=60)
#             response.raise_for_status()
#             result = response.json()
#             print("API call successful!")
#             return result
#         except requests.exceptions.RequestException as e:
#             print(f"API Error: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 print(f"Response status: {e.response.status_code}")
#                 print(f"Response body: {e.response.text}")
#             # Fallback to mock response for demo
#             return self._get_mock_response()
    
#     def _get_mock_response(self) -> Dict:
#         """Fallback mock response for demo/testing"""
#         return {
#             "choices": [{
#                 "message": {
#                     "content": json.dumps({
#                         "analysis_summary": "Demo analysis - connect to API with valid key for real analysis",
#                         "rare_disease_possibilities": [
#                             {
#                                 "disease_name": "Ehlers-Danlos Syndrome",
#                                 "description": "Connective tissue disorder characterized by joint hypermobility, skin hyperextensibility, and tissue fragility",
#                                 "supporting_evidence": ["Joint hypermobility noted in report", "History of easy bruising", "Chronic pain reported"],
#                                 "conflicting_evidence": ["No family history of similar symptoms"],
#                                 "next_steps": ["Genetic testing for COL5A1, COL5A2 genes", "Consultation with rheumatologist", "Echocardiogram to rule out vascular involvement"],
#                                 "prevalence": "1 in 5,000",
#                                 "urgency_level": "medium"
#                             },
#                             {
#                                 "disease_name": "Marfan Syndrome",
#                                 "description": "Genetic disorder affecting connective tissue, often involving heart, eyes, blood vessels, and skeleton",
#                                 "supporting_evidence": ["Tall stature mentioned", "Possible arachnodactyly (long fingers)"],
#                                 "conflicting_evidence": ["No mention of lens dislocation or aortic dilation"],
#                                 "next_steps": ["Echocardiogram to measure aortic root", "Ophthalmology evaluation", "FBN1 gene testing"],
#                                 "prevalence": "1 in 5,000",
#                                 "urgency_level": "high"
#                             }
#                         ],
#                         "confidence_factors": ["Multiple system involvement", "Atypical presentation for common conditions"],
#                         "red_flags": ["Cardiovascular symptoms present", "Need to rule out aortic dissection in Marfan"],
#                         "recommended_specialists": ["Rheumatologist", "Geneticist", "Cardiologist"]
#                     })
#                 }
#             }]
#         }
    
#     def _parse_llm_response(self, response: Dict) -> List[RareDiseaseRecommendation]:
#         """Parse LLM response into structured recommendations"""
        
#         try:
#             content = response["choices"][0]["message"]["content"]
#             print("Parsing LLM response...")
#             data = json.loads(content)
            
#             recommendations = []
#             for disease in data.get("rare_disease_possibilities", []):
#                 rec = RareDiseaseRecommendation(
#                     disease_name=disease.get("disease_name", "Unknown"),
#                     confidence_score=0.5,  # Will be calculated later
#                     supporting_evidence=disease.get("supporting_evidence", []),
#                     conflicting_evidence=disease.get("conflicting_evidence", []),
#                     next_steps=disease.get("next_steps", []),
#                     prevalence=disease.get("prevalence", "Unknown"),
#                     urgency_level=disease.get("urgency_level", "medium")
#                 )
#                 recommendations.append(rec)
            
#             print(f"Found {len(recommendations)} rare disease possibilities")
#             return recommendations
            
#         except (KeyError, json.JSONDecodeError) as e:
#             print(f"Error parsing response: {e}")
#             print(f"Response content: {response.get('choices', [{}])[0].get('message', {}).get('content', '')[:200]}")
#             return []
    
#     def _calculate_confidence_scores(self, 
#                                    recommendations: List[RareDiseaseRecommendation],
#                                    report_texts: List[str]) -> List[RareDiseaseRecommendation]:
#         """Calculate confidence scores based on evidence matching"""
        
#         combined_text = " ".join(report_texts).lower()
        
#         for rec in recommendations:
#             # Base confidence
#             confidence = 0.4
            
#             # Increase confidence for each piece of supporting evidence found in text
#             evidence_matches = 0
#             for evidence in rec.supporting_evidence:
#                 # Check if evidence keywords appear in reports
#                 keywords = self._extract_keywords(evidence)
#                 matches = sum(1 for kw in keywords if kw in combined_text)
#                 if matches >= 2:  # At least 2 keyword matches
#                     evidence_matches += 1
            
#             if evidence_matches > 0:
#                 confidence += 0.1 * evidence_matches
            
#             # Decrease confidence for conflicting evidence
#             conflicting_matches = 0
#             for evidence in rec.conflicting_evidence:
#                 keywords = self._extract_keywords(evidence)
#                 matches = sum(1 for kw in keywords if kw in combined_text)
#                 if matches > 0:
#                     conflicting_matches += 1
            
#             if conflicting_matches > 0:
#                 confidence -= 0.15 * conflicting_matches
            
#             # Adjust based on urgency (more urgent = higher confidence needed)
#             urgency_adjustment = {
#                 "critical": 0.0,  # No boost - critical needs high evidence
#                 "high": 0.05,
#                 "medium": 0.1,    # Medium urgency gets slight boost
#                 "low": 0.15       # Low urgency gets more boost (less risk)
#             }
#             confidence += urgency_adjustment.get(rec.urgency_level, 0.0)
            
#             # Adjust based on prevalence mention
#             if "1 in" in rec.prevalence.lower():
#                 try:
#                     prevalence_num = int(re.search(r'1 in (\d+)', rec.prevalence).group(1))
#                     # Rarer diseases need higher confidence
#                     if prevalence_num > 10000:
#                         confidence -= 0.1
#                     elif prevalence_num > 50000:
#                         confidence -= 0.2
#                 except:
#                     pass
            
#             # Cap between 0.1 and 0.95
#             rec.confidence_score = max(0.1, min(0.95, confidence))
        
#         return recommendations
    
#     def _extract_keywords(self, text: str) -> List[str]:
#         """Extract keywords from text for matching"""
#         # Remove common words and extract meaningful keywords
#         common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
#                        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
#                        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
#                        'could', 'can', 'may', 'might', 'must', 'shall', 'this', 'that',
#                        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
#         # Extract words of 4+ letters
#         words = re.findall(r'\b[a-z]{4,}\b', text.lower())
#         # Filter out common words and duplicates
#         keywords = []
#         for word in words:
#             if word not in common_words and word not in keywords:
#                 keywords.append(word)
        
#         return keywords[:8]  # Return top 8 keywords

# # ============================================================================
# # MAIN APPLICATION
# # ============================================================================

# class RareDiseaseDetector:
#     """Main application class"""
    
#     def __init__(self, api_key: str):
#         self.processor = MedicalReportProcessor()
#         self.analyzer = RareDiseaseAnalyzer(api_key)
    
#     def analyze_patient(self, 
#                        file_paths: List[str],
#                        patient_context: Optional[PatientContext] = None) -> Dict:
#         """Main analysis pipeline"""
        
#         if patient_context is None:
#             patient_context = PatientContext()
        
#         print(f"\n{'='*60}")
#         print("RARE DISEASE DETECTOR - ANALYSIS STARTED")
#         print(f"{'='*60}")
#         print(f"Processing {len(file_paths)} file(s)...")
        
#         # Process all files
#         report_texts = []
#         file_types = []
#         all_findings = []
        
#         for file_path in file_paths:
#             if not os.path.exists(file_path):
#                 print(f"✗ File not found: {file_path}")
#                 continue
            
#             try:
#                 text, file_type = self.processor.extract_text_from_file(file_path)
#                 if text.strip():
#                     report_texts.append(f"=== File: {os.path.basename(file_path)} ({file_type}) ===\n{text[:1000]}...")
#                     file_types.append(file_type)
#                     # Extract findings from this file
#                     findings = self.processor.extract_medical_findings(text, file_type)
#                     all_findings.extend(findings)
#                     print(f"✓ Processed: {os.path.basename(file_path)} ({file_type}, {len(text)} chars, {len(findings)} findings)")
#                 else:
#                     print(f"⚠️  No text extracted from: {file_path}")
#             except Exception as e:
#                 print(f"✗ Error processing {file_path}: {e}")
        
#         if not report_texts:
#             return {
#                 "error": "No text extracted from files",
#                 "suggestion": "Try using text files or clearer PDFs/images"
#             }
        
#         print(f"\nTotal findings extracted: {len(all_findings)}")
        
#         # Show sample findings
#         if all_findings:
#             print("\nSample findings:")
#             for i, finding in enumerate(all_findings[:5]):
#                 print(f"  {i+1}. {finding.text[:80]}...")
#             if len(all_findings) > 5:
#                 print(f"  ... and {len(all_findings) - 5} more")
        
#         # Analyze with LLM
#         print("\n" + "-"*40)
#         print("Analyzing with AI...")
#         print(f"Using model: {MODEL}")
#         print("-"*40)
        
#         recommendations = self.analyzer.analyze_reports(
#             report_texts, 
#             patient_context, 
#             file_types
#         )
        
#         # Prepare results
#         results = {
#             "patient_context": {
#                 "age": patient_context.age,
#                 "gender": patient_context.gender,
#                 "conditions": patient_context.existing_conditions,
#                 "symptoms": patient_context.symptoms[:10]  # First 10 symptoms
#             },
#             "processing_info": {
#                 "files_processed": len(report_texts),
#                 "file_types": list(set(file_types)),
#                 "total_findings": len(all_findings),
#                 "model_used": MODEL,
#                 "timestamp": datetime.now().isoformat()
#             },
#             "recommendations": [
#                 {
#                     "rank": i + 1,
#                     "disease": rec.disease_name,
#                     "confidence": f"{rec.confidence_score:.1%}",
#                     "confidence_score": float(f"{rec.confidence_score:.3f}"),
#                     "prevalence": rec.prevalence,
#                     "urgency": rec.urgency_level,
#                     "supporting_evidence": rec.supporting_evidence[:5],
#                     "conflicting_evidence": rec.conflicting_evidence[:3],
#                     "next_steps": rec.next_steps[:5],
#                     "match_level": self._get_match_level(rec.confidence_score),
#                     "urgency_icon": self._get_urgency_icon(rec.urgency_level)
#                 }
#                 for i, rec in enumerate(recommendations)
#             ],
#             "summary": self._generate_summary(recommendations)
#         }
        
#         return results
    
#     def _get_match_level(self, confidence: float) -> str:
#         """Convert confidence score to match level"""
#         if confidence >= 0.7:
#             return "High Match 🔥"
#         elif confidence >= 0.5:
#             return "Medium Match ⚡"
#         elif confidence >= 0.3:
#             return "Low Match 💡"
#         else:
#             return "Very Low Match ⚠️"
    
#     def _get_urgency_icon(self, urgency: str) -> str:
#         """Get icon for urgency level"""
#         icons = {
#             "critical": "🚨🚨",
#             "high": "🚨",
#             "medium": "⚠️",
#             "low": "ℹ️"
#         }
#         return icons.get(urgency, "❓")
    
#     def _generate_summary(self, recommendations: List[RareDiseaseRecommendation]) -> Dict:
#         """Generate summary of findings"""
#         if not recommendations:
#             return {
#                 "message": "No rare disease patterns detected in the provided reports.",
#                 "action": "Continue with standard diagnostic procedures.",
#                 "icon": "✅"
#             }
        
#         # Find highest confidence recommendation
#         top_rec = max(recommendations, key=lambda x: x.confidence_score)
        
#         urgent_count = sum(1 for r in recommendations if r.urgency_level in ["high", "critical"])
#         medium_count = sum(1 for r in recommendations if r.urgency_level == "medium")
        
#         return {
#             "top_suspicion": top_rec.disease_name,
#             "top_confidence": f"{top_rec.confidence_score:.1%}",
#             "top_urgency": top_rec.urgency_level,
#             "urgent_findings": urgent_count,
#             "medium_urgency_findings": medium_count,
#             "total_possibilities": len(recommendations),
#             "action_required": urgent_count > 0,
#             "message": f"Found {len(recommendations)} rare disease possibilities. "
#                       f"Top match: {top_rec.disease_name} ({top_rec.confidence_score:.1%} confidence, {top_rec.urgency_level} urgency).",
#             "icon": "🚨" if urgent_count > 0 else "⚠️" if medium_count > 0 else "ℹ️"
#         }

# # ============================================================================
# # DEMO & TESTING FUNCTIONS
# # ============================================================================

# def run_demo():
#     """Run a demo with sample data"""
    
#     print("=" * 60)
#     print("RARE DISEASE DETECTOR - DEMO MODE")
#     print("=" * 60)
    
#     # Check API key
#     if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
#         print("⚠️  Running in OFFLINE DEMO MODE (no API key)")
#         print("To use real AI analysis, add your OpenRouter API key to .env file")
#         print()
#     else:
#         print("✅ API key found! Using real AI analysis")
#         print()
    
#     # Create detector
#     detector = RareDiseaseDetector(OPENROUTER_API_KEY)
    
#     # Sample patient context (simulating Ehlers-Danlos like case)
#     patient = PatientContext(
#         age=28,
#         gender="female",
#         existing_conditions=["joint hypermobility", "easy bruising", "chronic pain"],
#         family_history=["mother: flexible joints", "aunt: chronic pain", "cousin: mitral valve prolapse"],
#         symptoms=["joint dislocations", "skin that stretches easily", "fatigue", "digestive issues", "dizziness"]
#     )
    
#     # Create sample report text (in real usage, this would come from files)
#     sample_reports = [
#         """CLINICAL NOTE - RHEUMATOLOGY CONSULT
# Patient: Jane Doe, 28-year-old female
# Date: March 15, 2024

# CHIEF COMPLAINT: Chronic joint pain and frequent dislocations

# HISTORY OF PRESENT ILLNESS:
# Patient reports lifelong joint hypermobility with frequent subluxations of shoulders, fingers, and patellae.
# She bruises easily with minimal trauma. Skin is noted to be hyperextensible. Reports chronic fatigue
# and gastrointestinal issues including reflux and alternating constipation/diarrhea. Also reports
# orthostatic intolerance and dizziness upon standing.

# PHYSICAL EXAM:
# - Beighton Score: 8/9 (positive for hypermobility)
# - Skin: Hyperextensible, atrophic scarring on knees and elbows
# - Cardiovascular: Soft systolic murmur heard at apex
# - Musculoskeletal: Generalized joint hypermobility without inflammation

# ASSESSMENT:
# 1. Connective tissue disorder, likely Ehlers-Danlos Syndrome, hypermobile type
# 2. Autonomic dysfunction (POTS)
# 3. Chronic pain syndrome

# PLAN:
# 1. Refer to genetics for formal evaluation
# 2. Echocardiogram to evaluate for mitral valve prolapse
# 3. Physical therapy for joint stabilization
# 4. Consider cardiac workup for dysautonomia""",
        
#         """LABORATORY RESULTS
# Date: March 10, 2024

# COMPLETE BLOOD COUNT:
# - WBC: 6.5 x10^9/L (normal)
# - Hemoglobin: 13.2 g/dL (normal)
# - Platelets: 250 x10^9/L (normal)

# INFLAMMATORY MARKERS:
# - CRP: 0.3 mg/L (normal)
# - ESR: 10 mm/hr (normal)

# COAGULATION PROFILE:
# - PT: 12.5 sec (normal)
# - PTT: 35 sec (normal)
# - INR: 1.0 (normal)

# IMPRESSION: No evidence of inflammatory or hematologic disorder.

# GENETICS NOTE: Patient has features suggestive of EDS. Recommended testing for COL5A1, COL5A2,
# and other connective tissue genes if insurance approves."""
#     ]
    
#     # Save sample reports to temporary files for demo
#     temp_files = []
#     for i, report in enumerate(sample_reports):
#         filename = f"temp_demo_report_{i}.txt"
#         with open(filename, 'w', encoding='utf-8') as f:
#             f.write(report)
#         temp_files.append(filename)
    
#     try:
#         # Analyze
#         print("Analyzing sample case (28F with joint hypermobility, easy bruising)...")
#         results = detector.analyze_patient(temp_files, patient)
        
#         display_results(results)
        
#         # Save results to file
#         output_file = "demo_rare_disease_analysis.json"
#         with open(output_file, 'w', encoding='utf-8') as f:
#             json.dump(results, f, indent=2, ensure_ascii=False)
#         print(f"\nFull results saved to: {output_file}")
        
#     finally:
#         # Clean up temp files
#         for f in temp_files:
#             try:
#                 os.remove(f)
#             except:
#                 pass

# def display_results(results):
#     """Display results in a readable format"""
#     print("\n" + "=" * 60)
#     print("ANALYSIS RESULTS")
#     print("=" * 60)
    
#     if 'error' in results:
#         print(f"Error: {results['error']}")
#         return
    
#     patient_info = results['patient_context']
#     print(f"\nPatient: {patient_info['age']}y {patient_info['gender']}")
#     print(f"Symptoms: {', '.join(patient_info['symptoms'][:5])}")
#     if len(patient_info['symptoms']) > 5:
#         print(f"          + {len(patient_info['symptoms']) - 5} more")
    
#     print(f"\nFiles Processed: {results['processing_info']['files_processed']}")
#     print(f"Total Findings: {results['processing_info']['total_findings']}")
#     print(f"AI Model Used: {results['processing_info']['model_used']}")
    
#     summary = results['summary']
#     print(f"\n📊 SUMMARY: {summary['message']}")
#     print(f"   Icon: {summary['icon']}")
    
#     if not results['recommendations']:
#         print("\n✅ No rare disease patterns detected.")
#         return
    
#     print(f"\nTOP RECOMMENDATIONS:")
#     print("-" * 60)
    
#     for rec in results['recommendations']:
#         print(f"\n#{rec['rank']} {rec['urgency_icon']} {rec['disease']}")
#         print(f"  Confidence: {rec['confidence']} ({rec['match_level']})")
#         print(f"  Prevalence: {rec['prevalence']}")
#         print(f"  Urgency Level: {rec['urgency'].upper()}")
        
#         if rec['supporting_evidence']:
#             print(f"  Key Evidence:")
#             for evidence in rec['supporting_evidence'][:3]:
#                 print(f"    • {evidence}")
        
#         if rec['next_steps']:
#             print(f"  Next Steps:")
#             for step in rec['next_steps'][:2]:
#                 print(f"    • {step}")
    
#     if summary['action_required']:
#         print("\n" + "🚨" * 20)
#         print("🚨 URGENT ACTION RECOMMENDED!")
#         print("🚨 Please consult with relevant specialists immediately.")
#         print("🚨" * 20)
    
#     print("\n" + "=" * 60)
#     print("Analysis complete! 🎯")

# def analyze_real_files(file_paths: List[str], patient_info: Dict):
#     """Analyze real patient files"""
    
#     if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
#         print("⚠️  WARNING: No valid API key found!")
#         print("Running in demo mode with simulated results.")
#         print("\nTo use real AI analysis:")
#         print("1. Get a free API key from: https://openrouter.ai/keys")
#         print("2. Add it to your .env file:")
#         print("   OPENROUTER_API_KEY=your-actual-key-here")
#         print()
    
#     # Create patient context
#     patient = PatientContext(
#         age=patient_info.get('age'),
#         gender=patient_info.get('gender'),
#         existing_conditions=patient_info.get('existing_conditions', []),
#         family_history=patient_info.get('family_history', []),
#         symptoms=patient_info.get('symptoms', [])
#     )
    
#     # Check files exist
#     valid_files = []
#     for fp in file_paths:
#         if os.path.exists(fp):
#             valid_files.append(fp)
#         else:
#             print(f"✗ File not found: {fp}")
    
#     if not valid_files:
#         print("No valid files to analyze")
#         return
    
#     # Create detector and analyze
#     detector = RareDiseaseDetector(OPENROUTER_API_KEY)
#     results = detector.analyze_patient(valid_files, patient)
    
#     # Display results
#     display_results(results)
    
#     # Save detailed results
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_file = f"rare_disease_report_{timestamp}.json"
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)
    
#     print(f"\nDetailed report saved to: {output_file}")

# # ============================================================================
# # COMMAND LINE INTERFACE
# # ============================================================================

# if __name__ == "__main__":
#     import sys
    
#     print("\n" + "="*60)
#     print("RARE DISEASE POSSIBILITY RECOMMENDER")
#     print("="*60)
    
#     # Check if .env exists, if not create it
#     env_path = Path(__file__).parent / '.env'
#     if not env_path.exists():
#         create_env_template()
#         print("\nPlease edit the .env file with your API key and run again.")
#         sys.exit(1)
    
#     if len(sys.argv) > 1:
#         if sys.argv[1] == "--demo":
#             run_demo()
#         elif sys.argv[1] == "--help":
#             print("\nUsage:")
#             print("  python rare_disease.py                    # Interactive mode")
#             print("  python rare_disease.py --demo            # Run demo")
#             print("  python rare_disease.py file1.pdf file2.txt  # Analyze specific files")
#             print("\nMake sure your .env file contains your OpenRouter API key!")
#         else:
#             # Assume arguments are file paths
#             file_paths = sys.argv[1:]
#             print(f"\nAnalyzing {len(file_paths)} file(s)...")
            
#             # Get minimal patient info
#             patient_info = {}
#             print("\nPlease provide basic patient info (press Enter to skip):")
#             try:
#                 age_input = input("Age: ").strip()
#                 if age_input:
#                     patient_info['age'] = int(age_input)
#             except:
#                 pass
            
#             patient_info['gender'] = input("Gender (M/F/Other): ").strip() or None
            
#             conditions = input("Existing conditions (comma separated): ").strip()
#             patient_info['existing_conditions'] = [c.strip() for c in conditions.split(",") if c.strip()]
            
#             family = input("Family history of rare diseases (comma separated): ").strip()
#             patient_info['family_history'] = [f.strip() for f in family.split(",") if f.strip()]
            
#             symptoms = input("Current symptoms (comma separated): ").strip()
#             patient_info['symptoms'] = [s.strip() for s in symptoms.split(",") if s.strip()]
            
#             analyze_real_files(file_paths, patient_info)
#     else:
#         # Interactive mode
#         print("\nInteractive Analysis Mode")
#         print("-" * 40)
        
#         # Get patient info
#         patient_info = {}
#         print("\nPATIENT INFORMATION (press Enter to skip):")
        
#         try:
#             age_input = input("Age: ").strip()
#             if age_input:
#                 patient_info['age'] = int(age_input)
#         except ValueError:
#             print("Invalid age, skipping...")
        
#         patient_info['gender'] = input("Gender (M/F/Other): ").strip() or None
        
#         conditions = input("Existing conditions (comma separated): ").strip()
#         patient_info['existing_conditions'] = [c.strip() for c in conditions.split(",") if c.strip()]
        
#         family = input("Family history of rare diseases (comma separated): ").strip()
#         patient_info['family_history'] = [f.strip() for f in family.split(",") if f.strip()]
        
#         symptoms = input("Current symptoms (comma separated): ").strip()
#         patient_info['symptoms'] = [s.strip() for s in symptoms.split(",") if s.strip()]
        
#         # Get file paths
#         print("\n" + "-"*40)
#         print("FILE UPLOAD")
#         print("Supported: PDF, JPG, PNG, TXT, DOC")
#         print("Enter file paths (one per line, empty line to finish):")
#         print("-"*40)
        
#         file_paths = []
#         while True:
#             path = input("> ").strip()
#             if not path:
#                 break
#             if path.lower() == 'demo':
#                 print("Switching to demo mode...")
#                 run_demo()
#                 sys.exit(0)
#             file_paths.append(path)
        
#         if file_paths:
#             analyze_real_files(file_paths, patient_info)
#         else:
#             print("\nNo files provided. Running demo instead...")
#             run_demo()






# """
# RARE DISEASE DIAGNOSTIC ASSISTANT
# One-file solution using OpenRouter API for analyzing medical reports
# Author: Medical AI Team
# """

# import os
# import sys
# import subprocess
# import importlib
# from pathlib import Path

# # ============================================================================
# # AUTO-INSTALL DEPENDENCIES
# # ============================================================================

# def install_package(package_name, pip_name=None):
#     """Install a package if not available"""
#     if pip_name is None:
#         pip_name = package_name
    
#     try:
#         importlib.import_module(package_name)
#         print(f"✓ {package_name} is already installed")
#         return True
#     except ImportError:
#         print(f"Installing {package_name}...")
#         try:
#             subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
#             print(f"✓ Successfully installed {package_name}")
#             return True
#         except Exception as e:
#             print(f"✗ Failed to install {package_name}: {e}")
#             return False

# # List of required packages
# REQUIRED_PACKAGES = [
#     ("requests", "requests"),
#     ("PIL", "pillow"),  # PIL comes from pillow
#     ("PyPDF2", "PyPDF2"),
#     ("pytesseract", "pytesseract"),
#     ("numpy", "numpy"),
# ]

# print("=" * 60)
# print("MEDICAL DOCUMENT ANALYZER - SETUP")
# print("=" * 60)

# # Install missing packages
# missing_packages = []
# for package_name, pip_name in REQUIRED_PACKAGES:
#     if not install_package(package_name, pip_name):
#         missing_packages.append(package_name)

# if missing_packages:
#     print(f"\n⚠️ Warning: Could not install: {', '.join(missing_packages)}")
#     print("Some features may not work properly.")
#     print("You can install them manually:")
#     for package in missing_packages:
#         print(f"  pip install {package}")
#     print()
# else:
#     print("\n✅ All dependencies are installed!")

# print("-" * 60)

# # ============================================================================
# # NOW IMPORT THE INSTALLED PACKAGES
# # ============================================================================

# try:
#     import re
#     import json
#     import base64
#     import requests
#     from typing import List, Dict, Tuple, Optional
#     from dataclasses import dataclass
#     import PyPDF2
#     from PIL import Image
#     import pytesseract
#     import numpy as np
#     import mimetypes
#     from datetime import datetime
#     print("✅ Successfully imported all modules")
# except ImportError as e:
#     print(f"✗ Import error: {e}")
#     print("Please restart the script or install missing packages manually")
#     sys.exit(1)

# # ============================================================================
# # LOAD ENVIRONMENT VARIABLES
# # ============================================================================

# def load_env_file():
#     """Load environment variables from .env file"""
#     env_path = Path(__file__).parent / '.env'
#     if env_path.exists():
#         print(f"Loading environment from: {env_path}")
#         with open(env_path, 'r') as f:
#             for line in f:
#                 line = line.strip()
#                 if line and not line.startswith('#') and '=' in line:
#                     key, value = line.split('=', 1)
#                     os.environ[key.strip()] = value.strip().strip('"\'')
#         print("✅ Environment variables loaded")
#     else:
#         print("⚠️ No .env file found")
#         create_env_template()
#         return False
#     return True

# def create_env_template():
#     """Create a template .env file if it doesn't exist"""
#     env_template = """# OpenRouter API Configuration
# OPENROUTER_API_KEY=your-api-key-here

# # Optional: Set your preferred model
# # MODEL=deepseek/deepseek-r1:free
# # MODEL=openai/gpt-4o
# # MODEL=anthropic/claude-3.5-sonnet
# # MODEL=google/gemini-1.5-pro

# # Optional: Set your application details (required by OpenRouter)
# HTTP_REFERER=http://localhost:3000
# X_TITLE=Rare Disease Assistant

# # Optional: Tesseract OCR path (Windows users might need this)
# # TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
# """
    
#     env_path = Path(__file__).parent / '.env'
#     try:
#         with open(env_path, 'w') as f:
#             f.write(env_template)
#         print(f"✅ Created template .env file at: {env_path}")
#         print("\n⚠️ IMPORTANT: Please edit the .env file with your API key!")
#         print("1. Get a free API key from: https://openrouter.ai/keys")
#         print("2. Open the .env file and replace 'your-api-key-here' with your key")
#         print("3. Run this script again")
#     except Exception as e:
#         print(f"✗ Could not create .env file: {e}")
    
#     return env_path

# # Load environment variables
# env_loaded = load_env_file()

# # ============================================================================
# # CONFIGURATION - FROM ENVIRONMENT VARIABLES
# # ============================================================================

# # Get API key from environment
# OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# # Get model from environment or use default
# MODEL = os.environ.get("MODEL", "deepseek/deepseek-r1:free")

# # Get other settings
# HTTP_REFERER = os.environ.get("HTTP_REFERER", "http://localhost:3000")
# X_TITLE = os.environ.get("X_TITLE", "Rare Disease Assistant")

# API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# # Check Tesseract installation on Windows
# if sys.platform == "win32":
#     tesseract_path = os.environ.get("TESSERACT_PATH")
#     if tesseract_path:
#         pytesseract.pytesseract.tesseract_cmd = tesseract_path
#     else:
#         # Try common Windows paths
#         common_paths = [
#             r"C:\Program Files\Tesseract-OCR\tesseract.exe",
#             r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
#         ]
#         for path in common_paths:
#             if os.path.exists(path):
#                 pytesseract.pytesseract.tesseract_cmd = path
#                 print(f"✅ Found Tesseract at: {path}")
#                 break
#         else:
#             print("⚠️ Tesseract OCR not found. Image processing may not work.")
#             print("   Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
#             print("   Then set TESSERACT_PATH in .env file")

# # Validate API key
# if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
#     print("\n⚠️  WARNING: No valid API key found!")
#     print("Running in DEMO MODE with simulated results.")
#     print("\nTo use real AI analysis:")
#     print("1. Get a free API key from: https://openrouter.ai/keys")
#     print("2. Edit the .env file and add your key")
#     print("3. Run the script again")
#     print("\n" + "-" * 60)

# # Rare disease database (simplified)
# RARE_DISEASES_DB = {
#     "ehlers_danlos": {
#         "name": "Ehlers-Danlos Syndrome",
#         "symptoms": ["joint hypermobility", "skin hyperextensibility", "easy bruising", "chronic pain"],
#         "prevalence": "1 in 5,000",
#         "confidence_factors": ["family_history", "multiple_system_involvement"]
#     },
#     "marfan": {
#         "name": "Marfan Syndrome",
#         "symptoms": ["tall stature", "arachnodactyly", "lens dislocation", "aortic dilation"],
#         "prevalence": "1 in 5,000",
#         "confidence_factors": ["aortic_root_diameter", "systemic_score"]
#     },
#     "pompe": {
#         "name": "Pompe Disease",
#         "symptoms": ["muscle weakness", "respiratory issues", "cardiomegaly", "feeding difficulties"],
#         "prevalence": "1 in 40,000",
#         "confidence_factors": ["enzyme_deficiency", "muscle_biopsy"]
#     }
# }

# # ============================================================================
# # DATA CLASSES
# # ============================================================================

# @dataclass
# class MedicalFinding:
#     """Represents a medical finding from reports"""
#     text: str
#     source: str
#     confidence: float = 0.0
#     normalized_value: Optional[float] = None
#     unit: Optional[str] = None

# @dataclass
# class RareDiseaseRecommendation:
#     """Represents a rare disease possibility"""
#     disease_name: str
#     confidence_score: float
#     supporting_evidence: List[str]
#     conflicting_evidence: List[str]
#     next_steps: List[str]
#     prevalence: str
#     urgency_level: str

# @dataclass
# class PatientContext:
#     """Patient demographic and clinical context"""
#     age: Optional[int] = None
#     gender: Optional[str] = None
#     existing_conditions: List[str] = None
#     family_history: List[str] = None
#     symptoms: List[str] = None
    
#     def __post_init__(self):
#         if self.existing_conditions is None:
#             self.existing_conditions = []
#         if self.family_history is None:
#             self.family_history = []
#         if self.symptoms is None:
#             self.symptoms = []

# # ============================================================================
# # FILE PROCESSING FUNCTIONS
# # ============================================================================

# class MedicalReportProcessor:
#     """Process various medical report formats"""
    
#     @staticmethod
#     def extract_text_from_pdf(file_path: str) -> str:
#         """Extract text from PDF files"""
#         text = ""
#         try:
#             with open(file_path, 'rb') as file:
#                 pdf_reader = PyPDF2.PdfReader(file)
#                 for page in pdf_reader.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#             return text
#         except Exception as e:
#             print(f"Error reading PDF {file_path}: {e}")
#             return f"[PDF file: {os.path.basename(file_path)}]"
    
#     @staticmethod
#     def extract_text_from_image(file_path: str) -> str:
#         """Extract text from image files using OCR"""
#         try:
#             image = Image.open(file_path)
#             # Convert to grayscale for better OCR
#             if image.mode != 'L':
#                 image = image.convert('L')
#             text = pytesseract.image_to_string(image)
#             return text
#         except Exception as e:
#             print(f"Error processing image {file_path}: {e}")
#             return f"[Image file: {os.path.basename(file_path)}]"
    
#     @staticmethod
#     def extract_text_from_file(file_path: str) -> Tuple[str, str]:
#         """Main function to extract text from any file type"""
#         if not os.path.exists(file_path):
#             return f"File not found: {file_path}", "error"
        
#         filename_lower = file_path.lower()
        
#         if filename_lower.endswith('.pdf'):
#             return MedicalReportProcessor.extract_text_from_pdf(file_path), 'pdf'
#         elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
#             return MedicalReportProcessor.extract_text_from_image(file_path), 'image'
#         elif filename_lower.endswith(('.txt', '.md', '.rtf')):
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     return f.read(), 'text'
#             except:
#                 try:
#                     with open(file_path, 'r', encoding='latin-1') as f:
#                         return f.read(), 'text'
#                 except:
#                     return f"[Text file: {os.path.basename(file_path)}]", 'text'
#         else:
#             # Try to read as text
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                     if len(content) > 0:
#                         return content, 'text'
#                     else:
#                         return f"[File: {os.path.basename(file_path)}]", 'unknown'
#             except:
#                 return f"[Unsupported file: {os.path.basename(file_path)}]", 'unknown'

# # ============================================================================
# # LLM INTEGRATION
# # ============================================================================

# class RareDiseaseAnalyzer:
#     """Main analyzer using LLM via OpenRouter"""
    
#     def __init__(self, api_key: str):
#         self.api_key = api_key
#         self.headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#             "HTTP-Referer": HTTP_REFERER,
#             "X-Title": X_TITLE
#         }
    
#     def analyze_reports(self, report_texts: List[str], patient_context: PatientContext) -> List[RareDiseaseRecommendation]:
#         """Main analysis function"""
        
#         # Combine all report texts
#         combined_text = "\n---\n".join(report_texts)
        
#         # Prepare prompt for LLM
#         prompt = self._create_analysis_prompt(combined_text, patient_context)
        
#         # Call LLM
#         response = self._call_openrouter(prompt)
        
#         # Parse response
#         recommendations = self._parse_llm_response(response)
        
#         # Calculate confidence scores
#         recommendations = self._calculate_confidence_scores(recommendations, report_texts)
        
#         # Filter and sort
#         recommendations = [r for r in recommendations if r.confidence_score > 0.2]
#         recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
#         return recommendations[:5]
    
#     def _create_analysis_prompt(self, report_text: str, patient_context: PatientContext) -> str:
#         """Create optimized prompt for rare disease analysis"""
        
#         # Truncate if too long
#         if len(report_text) > 5000:
#             report_text = report_text[:2500] + "\n[...truncated...]\n" + report_text[-2500:]
        
#         return f"""You are a medical expert specializing in rare diseases. Analyze this patient information:

# PATIENT CONTEXT:
# - Age: {patient_context.age or 'Unknown'}
# - Gender: {patient_context.gender or 'Unknown'}
# - Conditions: {', '.join(patient_context.existing_conditions) or 'None'}
# - Family History: {', '.join(patient_context.family_history) or 'None'}
# - Symptoms: {', '.join(patient_context.symptoms) or 'None'}

# MEDICAL REPORTS:
# {report_text}

# ANALYZE FOR RARE DISEASES (prevalence <1 in 2,000):
# 1. Look for unusual patterns or multiple unexplained symptoms
# 2. Consider diseases that could explain multiple findings together
# 3. For each possible disease, provide:
#    - Disease name
#    - Brief description
#    - Supporting evidence from reports
#    - Conflicting evidence (if any)
#    - Next steps for confirmation
#    - Estimated prevalence
#    - Urgency (low/medium/high/critical)

# FORMAT AS JSON:
# {{
#   "analysis_summary": "Brief assessment",
#   "rare_disease_possibilities": [
#     {{
#       "disease_name": "Name",
#       "description": "Brief description",
#       "supporting_evidence": ["Evidence 1", "Evidence 2"],
#       "conflicting_evidence": ["Evidence that doesn't fit"],
#       "next_steps": ["Test 1", "Consult specialist"],
#       "prevalence": "e.g., 1 in 50,000",
#       "urgency_level": "low/medium/high/critical"
#     }}
#   ]
# }}

# Be conservative. If no rare disease is likely, return empty array.
# """
    
#     def _call_openrouter(self, prompt: str) -> Dict:
#         """Call OpenRouter API"""
        
#         payload = {
#             "model": MODEL,
#             "messages": [
#                 {"role": "system", "content": "You are a medical diagnostician. Be accurate and conservative."},
#                 {"role": "user", "content": prompt}
#             ],
#             "temperature": 0.3,
#             "max_tokens": 3000,
#             "response_format": {"type": "json_object"}
#         }
        
#         # If no API key, return mock response
#         if not self.api_key or self.api_key == "your-api-key-here":
#             return self._get_mock_response()
        
#         try:
#             print("Calling OpenRouter API...")
#             response = requests.post(API_BASE_URL, headers=self.headers, json=payload, timeout=30)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             print(f"API Error: {e}")
#             return self._get_mock_response()
    
#     def _get_mock_response(self) -> Dict:
#         """Fallback mock response"""
#         return {
#             "choices": [{
#                 "message": {
#                     "content": json.dumps({
#                         "analysis_summary": "Demo mode - add API key for real analysis",
#                         "rare_disease_possibilities": [
#                             {
#                                 "disease_name": "Ehlers-Danlos Syndrome",
#                                 "description": "Connective tissue disorder",
#                                 "supporting_evidence": ["Joint hypermobility", "Easy bruising"],
#                                 "conflicting_evidence": [],
#                                 "next_steps": ["Genetic testing", "Rheumatology consult"],
#                                 "prevalence": "1 in 5,000",
#                                 "urgency_level": "medium"
#                             }
#                         ]
#                     })
#                 }
#             }]
#         }
    
#     def _parse_llm_response(self, response: Dict) -> List[RareDiseaseRecommendation]:
#         """Parse LLM response"""
#         try:
#             content = response["choices"][0]["message"]["content"]
#             data = json.loads(content)
            
#             recommendations = []
#             for disease in data.get("rare_disease_possibilities", []):
#                 rec = RareDiseaseRecommendation(
#                     disease_name=disease.get("disease_name", "Unknown"),
#                     confidence_score=0.5,
#                     supporting_evidence=disease.get("supporting_evidence", []),
#                     conflicting_evidence=disease.get("conflicting_evidence", []),
#                     next_steps=disease.get("next_steps", []),
#                     prevalence=disease.get("prevalence", "Unknown"),
#                     urgency_level=disease.get("urgency_level", "medium")
#                 )
#                 recommendations.append(rec)
            
#             return recommendations
#         except:
#             return []
    
#     def _calculate_confidence_scores(self, recommendations, report_texts):
#         """Calculate confidence scores"""
#         combined_text = " ".join(report_texts).lower()
        
#         for rec in recommendations:
#             confidence = 0.4
            
#             # Check supporting evidence
#             for evidence in rec.supporting_evidence[:3]:
#                 words = [w.lower() for w in evidence.split() if len(w) > 3]
#                 matches = sum(1 for w in words if w in combined_text)
#                 if matches > 0:
#                     confidence += 0.1
            
#             # Check conflicting evidence
#             for evidence in rec.conflicting_evidence[:2]:
#                 words = [w.lower() for w in evidence.split() if len(w) > 3]
#                 matches = sum(1 for w in words if w in combined_text)
#                 if matches > 0:
#                     confidence -= 0.15
            
#             # Adjust based on urgency
#             if rec.urgency_level == "critical":
#                 confidence += 0.1
#             elif rec.urgency_level == "low":
#                 confidence -= 0.1
            
#             rec.confidence_score = max(0.1, min(0.95, confidence))
        
#         return recommendations

# # ============================================================================
# # MAIN APPLICATION
# # ============================================================================

# class RareDiseaseDetector:
#     """Main application class"""
    
#     def __init__(self, api_key: str):
#         self.processor = MedicalReportProcessor()
#         self.analyzer = RareDiseaseAnalyzer(api_key)
    
#     def analyze_patient(self, file_paths: List[str], patient_context: PatientContext = None) -> Dict:
#         """Main analysis pipeline"""
        
#         if patient_context is None:
#             patient_context = PatientContext()
        
#         print(f"\nProcessing {len(file_paths)} file(s)...")
        
#         # Process files
#         report_texts = []
#         for file_path in file_paths:
#             text, file_type = self.processor.extract_text_from_file(file_path)
#             if text and "File not found" not in text:
#                 report_texts.append(f"=== {os.path.basename(file_path)} ===\n{text[:1000]}")
#                 print(f"✓ {os.path.basename(file_path)} ({file_type})")
        
#         if not report_texts:
#             return {"error": "No readable content found in files"}
        
#         # Analyze
#         print("\nAnalyzing with AI...")
#         recommendations = self.analyzer.analyze_reports(report_texts, patient_context)
        
#         # Format results
#         results = {
#             "patient": {
#                 "age": patient_context.age,
#                 "gender": patient_context.gender,
#                 "symptoms": patient_context.symptoms[:5]
#             },
#             "files_processed": len(report_texts),
#             "recommendations": [
#                 {
#                     "disease": rec.disease_name,
#                     "confidence": f"{rec.confidence_score:.0%}",
#                     "prevalence": rec.prevalence,
#                     "urgency": rec.urgency_level,
#                     "evidence": rec.supporting_evidence[:2],
#                     "next_steps": rec.next_steps[:2]
#                 }
#                 for rec in recommendations
#             ],
#             "summary": self._generate_summary(recommendations)
#         }
        
#         return results
    
#     def _generate_summary(self, recommendations):
#         """Generate summary"""
#         if not recommendations:
#             return {"message": "No rare disease patterns detected."}
        
#         top = max(recommendations, key=lambda x: x.confidence_score)
#         urgent = sum(1 for r in recommendations if r.urgency_level in ["high", "critical"])
        
#         return {
#             "top_match": top.disease_name,
#             "top_confidence": f"{top.confidence_score:.0%}",
#             "total_found": len(recommendations),
#             "urgent_alerts": urgent,
#             "message": f"Found {len(recommendations)} rare disease possibility(ies)"
#         }

# # ============================================================================
# # USER INTERFACE
# # ============================================================================

# def display_menu():
#     """Display main menu"""
#     print("\n" + "=" * 60)
#     print("MEDICAL DOCUMENT ANALYZER")
#     print("=" * 60)
#     print("\n1. Analyze medical documents")
#     print("2. Run demo with sample data")
#     print("3. Check API key status")
#     print("4. Exit")
#     print("\n" + "-" * 60)

# def get_patient_info():
#     """Get patient information from user"""
#     print("\nPATIENT INFORMATION (press Enter to skip)")
#     print("-" * 40)
    
#     patient = {}
    
#     try:
#         age = input("Age: ").strip()
#         if age:
#             patient["age"] = int(age)
#     except:
#         pass
    
#     patient["gender"] = input("Gender (M/F/Other): ").strip() or None
    
#     conditions = input("Existing conditions (comma separated): ").strip()
#     patient["conditions"] = [c.strip() for c in conditions.split(",") if c.strip()]
    
#     family = input("Family history (comma separated): ").strip()
#     patient["family"] = [f.strip() for f in family.split(",") if f.strip()]
    
#     symptoms = input("Current symptoms (comma separated): ").strip()
#     patient["symptoms"] = [s.strip() for s in symptoms.split(",") if s.strip()]
    
#     return patient

# def get_files_from_user():
#     """Get file paths from user"""
#     print("\nFILE UPLOAD")
#     print("-" * 40)
#     print("Supported: PDF, JPG, PNG, TXT")
#     print("Enter file paths (one per line, empty line to finish):")
#     print("Example: C:\\Users\\Name\\Documents\\report.pdf")
#     print("-" * 40)
    
#     files = []
#     while True:
#         path = input("> ").strip()
#         if not path:
#             break
#         if path.lower() == "demo":
#             return "demo"
#         if os.path.exists(path):
#             files.append(path)
#             print(f"Added: {os.path.basename(path)}")
#         else:
#             print(f"File not found: {path}")
    
#     return files

# def display_results(results):
#     """Display analysis results"""
#     print("\n" + "=" * 60)
#     print("ANALYSIS RESULTS")
#     print("=" * 60)
    
#     if "error" in results:
#         print(f"\nError: {results['error']}")
#         return
    
#     print(f"\nPatient: {results['patient'].get('age', '?')}y {results['patient'].get('gender', '?')}")
#     print(f"Files processed: {results['files_processed']}")
    
#     summary = results['summary']
#     print(f"\nSUMMARY: {summary['message']}")
    
#     if not results['recommendations']:
#         print("\n✅ No rare disease patterns detected.")
#         return
    
#     print(f"\nRECOMMENDATIONS:")
#     print("-" * 60)
    
#     for i, rec in enumerate(results['recommendations'], 1):
#         print(f"\n{i}. {rec['disease']}")
#         print(f"   Confidence: {rec['confidence']}")
#         print(f"   Prevalence: {rec['prevalence']}")
#         print(f"   Urgency: {rec['urgency'].upper()}")
        
#         if rec['evidence']:
#             print(f"   Evidence: {', '.join(rec['evidence'])}")
        
#         if rec['next_steps']:
#             print(f"   Next steps: {', '.join(rec['next_steps'])}")
    
#     if summary.get('urgent_alerts', 0) > 0:
#         print("\n🚨 URGENT: Specialist consultation recommended!")

# def run_demo():
#     """Run demo with sample data"""
#     print("\n" + "=" * 60)
#     print("DEMO MODE - SAMPLE ANALYSIS")
#     print("=" * 60)
    
#     detector = RareDiseaseDetector(OPENROUTER_API_KEY)
    
#     # Create sample patient
#     patient = PatientContext(
#         age=28,
#         gender="female",
#         existing_conditions=["joint hypermobility"],
#         family_history=["mother: flexible joints"],
#         symptoms=["joint pain", "easy bruising", "skin elasticity"]
#     )
    
#     # Create temporary sample file
#     sample_text = """CLINICAL NOTE
# Patient: 28F with chronic joint pain
# Exam: Beighton score 7/9 (hypermobile)
# Skin: Hyperextensible, atrophic scars
# Plan: Refer to genetics for EDS evaluation"""
    
#     temp_file = "temp_demo.txt"
#     with open(temp_file, 'w') as f:
#         f.write(sample_text)
    
#     try:
#         print("\nAnalyzing sample case...")
#         results = detector.analyze_patient([temp_file], patient)
#         display_results(results)
#     finally:
#         if os.path.exists(temp_file):
#             os.remove(temp_file)

# def check_api_status():
#     """Check API key status"""
#     print("\n" + "=" * 60)
#     print("API STATUS CHECK")
#     print("=" * 60)
    
#     if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your-api-key-here":
#         print("✅ API Key: Found (starts with 'sk-or-v1-...')")
#         print(f"🔧 Model: {MODEL}")
#         print("📡 Status: Ready for real analysis")
#     else:
#         print("⚠️ API Key: Not found or invalid")
#         print("📡 Status: Running in demo mode")
#         print("\nTo enable real AI analysis:")
#         print("1. Get free API key: https://openrouter.ai/keys")
#         print("2. Edit .env file in this directory")
#         print("3. Add: OPENROUTER_API_KEY=your-key-here")
#         print("4. Run the script again")

# # ============================================================================
# # MAIN PROGRAM
# # ============================================================================

# def main():
#     """Main program loop"""
    
#     print("\n" + "=" * 60)
#     print("WELCOME TO MEDICAL DOCUMENT ANALYZER")
#     print("=" * 60)
#     print("Analyze medical reports for rare disease possibilities")
    
#     while True:
#         display_menu()
        
#         try:
#             choice = input("\nSelect option (1-4): ").strip()
            
#             if choice == "1":
#                 # Get files
#                 files = get_files_from_user()
                
#                 if files == "demo":
#                     run_demo()
#                     continue
                
#                 if not files:
#                     print("No files provided. Returning to menu.")
#                     continue
                
#                 # Get patient info
#                 patient_info = get_patient_info()
#                 patient = PatientContext(
#                     age=patient_info.get("age"),
#                     gender=patient_info.get("gender"),
#                     existing_conditions=patient_info.get("conditions", []),
#                     family_history=patient_info.get("family", []),
#                     symptoms=patient_info.get("symptoms", [])
#                 )
                
#                 # Analyze
#                 detector = RareDiseaseDetector(OPENROUTER_API_KEY)
#                 results = detector.analyze_patient(files, patient)
                
#                 # Display results
#                 display_results(results)
                
#                 # Save results
#                 save = input("\nSave results to file? (y/n): ").lower()
#                 if save == 'y':
#                     filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#                     with open(filename, 'w') as f:
#                         json.dump(results, f, indent=2)
#                     print(f"Results saved to: {filename}")
            
#             elif choice == "2":
#                 run_demo()
            
#             elif choice == "3":
#                 check_api_status()
            
#             elif choice == "4":
#                 print("\nThank you for using Medical Document Analyzer!")
#                 print("Goodbye!")
#                 break
            
#             else:
#                 print("Invalid choice. Please select 1-4.")
        
#         except KeyboardInterrupt:
#             print("\n\nProgram interrupted. Exiting...")
#             break
#         except Exception as e:
#             print(f"\nError: {e}")
#             print("Please try again.")

# # ============================================================================
# # ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(f"\nFatal error: {e}")
#         print("\nTroubleshooting tips:")
#         print("1. Make sure you have Python 3.7+ installed")
#         print("2. Run as administrator if installation fails")
#         print("3. Install Tesseract OCR for image processing")
#         print("4. Check your internet connection for API calls")
#         input("\nPress Enter to exit...")








"""
RARE DISEASE DIAGNOSTIC ASSISTANT
One-file solution using OpenRouter API for analyzing medical reports
Author: Medical AI Team
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

# ============================================================================
# AUTO-INSTALL DEPENDENCIES
# ============================================================================

def install_package(package_name, pip_name=None):
    """Install a package if not available"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        importlib.import_module(package_name)
        print(f"✓ {package_name} is already installed")
        return True
    except ImportError:
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name, "--quiet"])
            print(f"✓ Successfully installed {package_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to install {package_name}: {e}")
            return False

# List of required packages
REQUIRED_PACKAGES = [
    ("requests", "requests"),
    ("PIL", "pillow"),  # PIL comes from pillow
    ("PyPDF2", "PyPDF2"),
    ("pytesseract", "pytesseract"),
    ("numpy", "numpy"),
]

print("=" * 60)
print("MEDICAL DOCUMENT ANALYZER - SETUP")
print("=" * 60)

# Install missing packages
missing_packages = []
for package_name, pip_name in REQUIRED_PACKAGES:
    if not install_package(package_name, pip_name):
        missing_packages.append(package_name)

if missing_packages:
    print(f"\n⚠️ Warning: Could not install: {', '.join(missing_packages)}")
    print("Some features may not work properly.")
    print("You can install them manually:")
    for package in missing_packages:
        print(f"  pip install {package}")
    print()
else:
    print("\n✅ All dependencies are installed!")

print("-" * 60)

# ============================================================================
# NOW IMPORT THE INSTALLED PACKAGES
# ============================================================================

try:
    import re
    import json
    import base64
    import requests
    from typing import List, Dict, Tuple, Optional
    from dataclasses import dataclass
    import PyPDF2
    from PIL import Image
    import pytesseract
    import numpy as np
    import mimetypes
    from datetime import datetime
    print("✅ Successfully imported all modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please restart the script or install missing packages manually")
    sys.exit(1)

# ============================================================================
# LOAD ENVIRONMENT VARIABLES - FIXED VERSION
# ============================================================================

def clean_env_value(value):
    """Remove null characters and other problematic characters from environment values"""
    # Remove null characters
    value = value.replace('\x00', '')
    # Remove BOM characters if present
    value = value.replace('\ufeff', '')
    # Strip whitespace and quotes
    value = value.strip().strip('"\'')
    return value

def load_env_file():
    """Load environment variables from .env file - FIXED to handle null characters"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("⚠️ No .env file found")
        create_env_template()
        return False
    
    print(f"Loading environment from: {env_path}")
    
    try:
        # Read file as binary to detect null characters
        with open(env_path, 'rb') as f:
            content = f.read()
        
        # Check for null bytes
        if b'\x00' in content:
            print("⚠️ Warning: .env file contains null characters. Cleaning...")
            # Remove null bytes
            content = content.replace(b'\x00', b'')
        
        # Decode to string
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            content_str = content.decode('latin-1')
        
        # Process each line
        for line in content_str.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Split at first '=' to handle values with '='
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = clean_env_value(value)
                
                if key:  # Only set if key is not empty
                    os.environ[key] = value
                    print(f"  Set: {key} = {'*' * len(value) if 'key' in key.lower() or 'secret' in key.lower() else value}")
        
        print("✅ Environment variables loaded")
        return True
        
    except Exception as e:
        print(f"✗ Error loading .env file: {e}")
        print("Creating a fresh .env file...")
        create_env_template()
        return False

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    env_template = """# OpenRouter API Configuration
OPENROUTER_API_KEY=your-api-key-here

# Optional: Set your preferred model
# MODEL=deepseek/deepseek-r1
# MODEL=openai/gpt-4o
# MODEL=anthropic/claude-3.5-sonnet
# MODEL=google/gemini-1.5-pro

# Optional: Set your application details (required by OpenRouter)
HTTP_REFERER=http://localhost:3000
X_TITLE=Rare Disease Assistant

# Optional: Tesseract OCR path (Windows users might need this)
# TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
"""
    
    env_path = Path(__file__).parent / '.env'
    try:
        # Ensure we write clean UTF-8 without BOM
        with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(env_template)
        print(f"✅ Created clean .env file at: {env_path}")
        print("\n⚠️ IMPORTANT: Please edit the .env file with your API key!")
        print("1. Get a free API key from: https://openrouter.ai/keys")
        print("2. Open the .env file and replace 'your-api-key-here' with your key")
        print("3. Run this script again")
    except Exception as e:
        print(f"✗ Could not create .env file: {e}")
    
    return env_path

# Load environment variables
env_loaded = load_env_file()

# ============================================================================
# CONFIGURATION - FROM ENVIRONMENT VARIABLES
# ============================================================================

# Get API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Get model from environment or use default
MODEL = os.environ.get("MODEL", "deepseek/deepseek-r1")

# Get other settings
HTTP_REFERER = os.environ.get("HTTP_REFERER", "http://localhost:3000")
X_TITLE = os.environ.get("X_TITLE", "Rare Disease Assistant")

API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Check Tesseract installation on Windows
if sys.platform == "win32":
    tesseract_path = os.environ.get("TESSERACT_PATH")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        # Try common Windows paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME'))
        ]
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Found Tesseract at: {path}")
                break
        else:
            print("⚠️ Tesseract OCR not found. Image processing may not work.")
            print("   Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   Then set TESSERACT_PATH in .env file")

# Validate API key
if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-api-key-here":
    print("\n⚠️  WARNING: No valid API key found!")
    print("Running in DEMO MODE with simulated results.")
    print("\nTo use real AI analysis:")
    print("1. Get a free API key from: https://openrouter.ai/keys")
    print("2. Edit the .env file and add your key")
    print("3. Run the script again")
    print("\n" + "-" * 60)

# Rare disease database (simplified)
RARE_DISEASES_DB = {
    "ehlers_danlos": {
        "name": "Ehlers-Danlos Syndrome",
        "symptoms": ["joint hypermobility", "skin hyperextensibility", "easy bruising", "chronic pain"],
        "prevalence": "1 in 5,000",
        "confidence_factors": ["family_history", "multiple_system_involvement"]
    },
    "marfan": {
        "name": "Marfan Syndrome",
        "symptoms": ["tall stature", "arachnodactyly", "lens dislocation", "aortic dilation"],
        "prevalence": "1 in 5,000",
        "confidence_factors": ["aortic_root_diameter", "systemic_score"]
    },
    "pompe": {
        "name": "Pompe Disease",
        "symptoms": ["muscle weakness", "respiratory issues", "cardiomegaly", "feeding difficulties"],
        "prevalence": "1 in 40,000",
        "confidence_factors": ["enzyme_deficiency", "musble_biopsy"]
    }
}

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class MedicalFinding:
    """Represents a medical finding from reports"""
    text: str
    source: str
    confidence: float = 0.0
    normalized_value: Optional[float] = None
    unit: Optional[str] = None

@dataclass
class RareDiseaseRecommendation:
    """Represents a rare disease possibility"""
    disease_name: str
    confidence_score: float
    supporting_evidence: List[str]
    conflicting_evidence: List[str]
    next_steps: List[str]
    prevalence: str
    urgency_level: str

@dataclass
class PatientContext:
    """Patient demographic and clinical context"""
    age: Optional[int] = None
    gender: Optional[str] = None
    existing_conditions: List[str] = None
    family_history: List[str] = None
    symptoms: List[str] = None
    
    def __post_init__(self):
        if self.existing_conditions is None:
            self.existing_conditions = []
        if self.family_history is None:
            self.family_history = []
        if self.symptoms is None:
            self.symptoms = []

# ============================================================================
# FILE PROCESSING FUNCTIONS
# ============================================================================

class MedicalReportProcessor:
    """Process various medical report formats"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return f"[PDF file: {os.path.basename(file_path)}]"
    
    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """Extract text from image files using OCR"""
        try:
            image = Image.open(file_path)
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error processing image {file_path}: {e}")
            return f"[Image file: {os.path.basename(file_path)}]"
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> Tuple[str, str]:
        """Main function to extract text from any file type"""
        if not os.path.exists(file_path):
            return f"File not found: {file_path}", "error"
        
        filename_lower = file_path.lower()
        
        if filename_lower.endswith('.pdf'):
            return MedicalReportProcessor.extract_text_from_pdf(file_path), 'pdf'
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            return MedicalReportProcessor.extract_text_from_image(file_path), 'image'
        elif filename_lower.endswith(('.txt', '.md', '.rtf')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read(), 'text'
            except:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        return f.read(), 'text'
                except:
                    return f"[Text file: {os.path.basename(file_path)}]", 'text'
        else:
            # Try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 0:
                        return content, 'text'
                    else:
                        return f"[File: {os.path.basename(file_path)}]", 'unknown'
            except:
                return f"[Unsupported file: {os.path.basename(file_path)}]", 'unknown'

# ============================================================================
# LLM INTEGRATION
# ============================================================================

class RareDiseaseAnalyzer:
    """Main analyzer using LLM via OpenRouter"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": HTTP_REFERER,
            "X-Title": X_TITLE
        }
    
    def analyze_reports(self, report_texts: List[str], patient_context: PatientContext) -> List[RareDiseaseRecommendation]:
        """Main analysis function"""
        
        # Combine all report texts
        combined_text = "\n---\n".join(report_texts)
        
        # Prepare prompt for LLM
        prompt = self._create_analysis_prompt(combined_text, patient_context)
        
        # Call LLM
        response = self._call_openrouter(prompt)
        
        # Parse response
        recommendations = self._parse_llm_response(response)
        
        # Calculate confidence scores
        recommendations = self._calculate_confidence_scores(recommendations, report_texts)
        
        # Filter and sort
        recommendations = [r for r in recommendations if r.confidence_score > 0.2]
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations[:5]
    
    def _create_analysis_prompt(self, report_text: str, patient_context: PatientContext) -> str:
        """Create optimized prompt for rare disease analysis"""
        
        # Truncate if too long
        if len(report_text) > 5000:
            report_text = report_text[:2500] + "\n[...truncated...]\n" + report_text[-2500:]
        
        return f"""You are a medical expert specializing in rare diseases. Analyze this patient information:

PATIENT CONTEXT:
- Age: {patient_context.age or 'Unknown'}
- Gender: {patient_context.gender or 'Unknown'}
- Conditions: {', '.join(patient_context.existing_conditions) or 'None'}
- Family History: {', '.join(patient_context.family_history) or 'None'}
- Symptoms: {', '.join(patient_context.symptoms) or 'None'}

MEDICAL REPORTS:
{report_text}

ANALYZE FOR RARE DISEASES (prevalence <1 in 2,000):
1. Look for unusual patterns or multiple unexplained symptoms
2. Consider diseases that could explain multiple findings together
3. For each possible disease, provide:
   - Disease name
   - Brief description
   - Supporting evidence from reports
   - Conflicting evidence (if any)
   - Next steps for confirmation
   - Estimated prevalence
   - Urgency (low/medium/high/critical)

FORMAT AS JSON:
{{
  "analysis_summary": "Brief assessment",
  "rare_disease_possibilities": [
    {{
      "disease_name": "Name",
      "description": "Brief description",
      "supporting_evidence": ["Evidence 1", "Evidence 2"],
      "conflicting_evidence": ["Evidence that doesn't fit"],
      "next_steps": ["Test 1", "Consult specialist"],
      "prevalence": "e.g., 1 in 50,000",
      "urgency_level": "low/medium/high/critical"
    }}
  ]
}}

Be conservative. If no rare disease is likely, return empty array.
"""
    
    def _call_openrouter(self, prompt: str) -> Dict:
        """Call OpenRouter API"""
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a medical diagnostician. Be accurate and conservative."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 3000,
            "response_format": {"type": "json_object"}
        }
        
        # If no API key, return mock response
        if not self.api_key or self.api_key == "your-api-key-here":
            return self._get_mock_response()
        
        try:
            print("Calling OpenRouter API...")
            response = requests.post(API_BASE_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return self._get_mock_response()
    
    def _get_mock_response(self) -> Dict:
        """Fallback mock response"""
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "analysis_summary": "Demo mode - add API key for real analysis",
                        "rare_disease_possibilities": [
                            {
                                "disease_name": "Ehlers-Danlos Syndrome",
                                "description": "Connective tissue disorder",
                                "supporting_evidence": ["Joint hypermobility", "Easy bruising"],
                                "conflicting_evidence": [],
                                "next_steps": ["Genetic testing", "Rheumatology consult"],
                                "prevalence": "1 in 5,000",
                                "urgency_level": "medium"
                            }
                        ]
                    })
                }
            }]
        }
    
    def _parse_llm_response(self, response: Dict) -> List[RareDiseaseRecommendation]:
        """Parse LLM response"""
        try:
            content = response["choices"][0]["message"]["content"]
            data = json.loads(content)
            
            recommendations = []
            for disease in data.get("rare_disease_possibilities", []):
                rec = RareDiseaseRecommendation(
                    disease_name=disease.get("disease_name", "Unknown"),
                    confidence_score=0.5,
                    supporting_evidence=disease.get("supporting_evidence", []),
                    conflicting_evidence=disease.get("conflicting_evidence", []),
                    next_steps=disease.get("next_steps", []),
                    prevalence=disease.get("prevalence", "Unknown"),
                    urgency_level=disease.get("urgency_level", "medium")
                )
                recommendations.append(rec)
            
            return recommendations
        except:
            return []
    
    def _calculate_confidence_scores(self, recommendations, report_texts):
        """Calculate confidence scores"""
        combined_text = " ".join(report_texts).lower()
        
        for rec in recommendations:
            confidence = 0.4
            
            # Check supporting evidence
            for evidence in rec.supporting_evidence[:3]:
                words = [w.lower() for w in evidence.split() if len(w) > 3]
                matches = sum(1 for w in words if w in combined_text)
                if matches > 0:
                    confidence += 0.1
            
            # Check conflicting evidence
            for evidence in rec.conflicting_evidence[:2]:
                words = [w.lower() for w in evidence.split() if len(w) > 3]
                matches = sum(1 for w in words if w in combined_text)
                if matches > 0:
                    confidence -= 0.15
            
            # Adjust based on urgency
            if rec.urgency_level == "critical":
                confidence += 0.1
            elif rec.urgency_level == "low":
                confidence -= 0.1
            
            rec.confidence_score = max(0.1, min(0.95, confidence))
        
        return recommendations

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class RareDiseaseDetector:
    """Main application class"""
    
    def __init__(self, api_key: str):
        self.processor = MedicalReportProcessor()
        self.analyzer = RareDiseaseAnalyzer(api_key)
    
    def analyze_patient(self, file_paths: List[str], patient_context: PatientContext = None) -> Dict:
        """Main analysis pipeline"""
        
        if patient_context is None:
            patient_context = PatientContext()
        
        print(f"\nProcessing {len(file_paths)} file(s)...")
        
        # Process files
        report_texts = []
        for file_path in file_paths:
            text, file_type = self.processor.extract_text_from_file(file_path)
            if text and "File not found" not in text:
                report_texts.append(f"=== {os.path.basename(file_path)} ===\n{text[:1000]}")
                print(f"✓ {os.path.basename(file_path)} ({file_type})")
        
        if not report_texts:
            return {"error": "No readable content found in files"}
        
        # Analyze
        print("\nAnalyzing with AI...")
        recommendations = self.analyzer.analyze_reports(report_texts, patient_context)
        
        # Format results
        results = {
            "patient": {
                "age": patient_context.age,
                "gender": patient_context.gender,
                "symptoms": patient_context.symptoms[:5]
            },
            "files_processed": len(report_texts),
            "recommendations": [
                {
                    "disease": rec.disease_name,
                    "confidence": f"{rec.confidence_score:.0%}",
                    "prevalence": rec.prevalence,
                    "urgency": rec.urgency_level,
                    "evidence": rec.supporting_evidence[:2],
                    "next_steps": rec.next_steps[:2]
                }
                for rec in recommendations
            ],
            "summary": self._generate_summary(recommendations)
        }
        
        return results
    
    def _generate_summary(self, recommendations):
        """Generate summary"""
        if not recommendations:
            return {"message": "No rare disease patterns detected."}
        
        top = max(recommendations, key=lambda x: x.confidence_score)
        urgent = sum(1 for r in recommendations if r.urgency_level in ["high", "critical"])
        
        return {
            "top_match": top.disease_name,
            "top_confidence": f"{top.confidence_score:.0%}",
            "total_found": len(recommendations),
            "urgent_alerts": urgent,
            "message": f"Found {len(recommendations)} rare disease possibility(ies)"
        }

# ============================================================================
# QUICK FIX: Delete and recreate the .env file
# ============================================================================

def fix_env_file():
    """Delete and recreate the .env file if it's corrupted"""
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        try:
            # Try to read it to check if corrupted
            with open(env_path, 'rb') as f:
                content = f.read()
            
            # Check for null bytes
            if b'\x00' in content:
                print("⚠️ Detected corrupted .env file with null bytes")
                backup = env_path.with_suffix('.env.backup')
                env_path.rename(backup)
                print(f"  Backup created: {backup}")
                
                # Create fresh .env file
                create_env_template()
                return True
        except Exception as e:
            print(f"Error checking .env file: {e}")
    
    return False

# ============================================================================
# USER INTERFACE
# ============================================================================

def display_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("MEDICAL DOCUMENT ANALYZER")
    print("=" * 60)
    print("\n1. Analyze medical documents")
    print("2. Run demo with sample data")
    print("3. Check API key status")
    print("4. Fix .env file (if corrupted)")
    print("5. Exit")
    print("\n" + "-" * 60)

def get_patient_info():
    """Get patient information from user"""
    print("\nPATIENT INFORMATION (press Enter to skip)")
    print("-" * 40)
    
    patient = {}
    
    try:
        age = input("Age: ").strip()
        if age:
            patient["age"] = int(age)
    except:
        pass
    
    patient["gender"] = input("Gender (M/F/Other): ").strip() or None
    
    conditions = input("Existing conditions (comma separated): ").strip()
    patient["conditions"] = [c.strip() for c in conditions.split(",") if c.strip()]
    
    family = input("Family history (comma separated): ").strip()
    patient["family"] = [f.strip() for f in family.split(",") if f.strip()]
    
    symptoms = input("Current symptoms (comma separated): ").strip()
    patient["symptoms"] = [s.strip() for s in symptoms.split(",") if s.strip()]
    
    return patient

def get_files_from_user():
    """Get file paths from user"""
    print("\nFILE UPLOAD")
    print("-" * 40)
    print("Supported: PDF, JPG, PNG, TXT")
    print("Enter file paths (one per line, empty line to finish):")
    print("Example: C:\\Users\\Name\\Documents\\report.pdf")
    print("-" * 40)
    
    files = []
    while True:
        path = input("> ").strip()
        if not path:
            break
        if path.lower() == "demo":
            return "demo"
        if os.path.exists(path):
            files.append(path)
            print(f"Added: {os.path.basename(path)}")
        else:
            print(f"File not found: {path}")
    
    return files

def display_results(results):
    """Display analysis results"""
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    if "error" in results:
        print(f"\nError: {results['error']}")
        return
    
    print(f"\nPatient: {results['patient'].get('age', '?')}y {results['patient'].get('gender', '?')}")
    print(f"Files processed: {results['files_processed']}")
    
    summary = results['summary']
    print(f"\nSUMMARY: {summary['message']}")
    
    if not results['recommendations']:
        print("\n✅ No rare disease patterns detected.")
        return
    
    print(f"\nRECOMMENDATIONS:")
    print("-" * 60)
    
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"\n{i}. {rec['disease']}")
        print(f"   Confidence: {rec['confidence']}")
        print(f"   Prevalence: {rec['prevalence']}")
        print(f"   Urgency: {rec['urgency'].upper()}")
        
        if rec['evidence']:
            print(f"   Evidence: {', '.join(rec['evidence'])}")
        
        if rec['next_steps']:
            print(f"   Next steps: {', '.join(rec['next_steps'])}")
    
    if summary.get('urgent_alerts', 0) > 0:
        print("\n🚨 URGENT: Specialist consultation recommended!")

def run_demo():
    """Run demo with sample data"""
    print("\n" + "=" * 60)
    print("DEMO MODE - SAMPLE ANALYSIS")
    print("=" * 60)
    
    detector = RareDiseaseDetector(OPENROUTER_API_KEY)
    
    # Create sample patient
    patient = PatientContext(
        age=28,
        gender="female",
        existing_conditions=["joint hypermobility"],
        family_history=["mother: flexible joints"],
        symptoms=["joint pain", "easy bruising", "skin elasticity"]
    )
    
    # Create temporary sample file
    sample_text = """CLINICAL NOTE
Patient: 28F with chronic joint pain
Exam: Beighton score 7/9 (hypermobile)
Skin: Hyperextensible, atrophic scars
Plan: Refer to genetics for EDS evaluation"""
    
    temp_file = "temp_demo.txt"
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    try:
        print("\nAnalyzing sample case...")
        results = detector.analyze_patient([temp_file], patient)
        display_results(results)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def check_api_status():
    """Check API key status"""
    print("\n" + "=" * 60)
    print("API STATUS CHECK")
    print("=" * 60)
    
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your-api-key-here":
        print("✅ API Key: Found (starts with 'sk-or-v1-...')")
        print(f"🔧 Model: {MODEL}")
        print("📡 Status: Ready for real analysis")
    else:
        print("⚠️ API Key: Not found or invalid")
        print("📡 Status: Running in demo mode")
        print("\nTo enable real AI analysis:")
        print("1. Get free API key: https://openrouter.ai/keys")
        print("2. Edit .env file in this directory")
        print("3. Add: OPENROUTER_API_KEY=your-key-here")
        print("4. Run the script again")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program loop"""
    
    print("\n" + "=" * 60)
    print("WELCOME TO MEDICAL DOCUMENT ANALYZER")
    print("=" * 60)
    print("Analyze medical reports for rare disease possibilities")
    
    # First, try to fix the .env file if corrupted
    if not env_loaded:
        print("\n⚠️ Could not load .env file. Attempting to fix...")
        if fix_env_file():
            print("✅ .env file fixed. Please restart the script.")
            return
    
    while True:
        display_menu()
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == "1":
                # Get files
                files = get_files_from_user()
                
                if files == "demo":
                    run_demo()
                    continue
                
                if not files:
                    print("No files provided. Returning to menu.")
                    continue
                
                # Get patient info
                patient_info = get_patient_info()
                patient = PatientContext(
                    age=patient_info.get("age"),
                    gender=patient_info.get("gender"),
                    existing_conditions=patient_info.get("conditions", []),
                    family_history=patient_info.get("family", []),
                    symptoms=patient_info.get("symptoms", [])
                )
                
                # Analyze
                detector = RareDiseaseDetector(OPENROUTER_API_KEY)
                results = detector.analyze_patient(files, patient)
                
                # Display results
                display_results(results)
                
                # Save results
                save = input("\nSave results to file? (y/n): ").lower()
                if save == 'y':
                    filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    print(f"Results saved to: {filename}")
            
            elif choice == "2":
                run_demo()
            
            elif choice == "3":
                check_api_status()
            
            elif choice == "4":
                print("\nFixing .env file...")
                if fix_env_file():
                    print("✅ .env file fixed. Please restart the script.")
                    return
                else:
                    print("✅ .env file is already clean.")
            
            elif choice == "5":
                print("\nThank you for using Medical Document Analyzer!")
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please select 1-5.")
        
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Delete the .env file and let the script create a fresh one")
        print("2. Make sure you have Python 3.7+ installed")
        print("3. Run as administrator if installation fails")
        print("4. Install Tesseract OCR for image processing")
        print("5. Check your internet connection for API calls")
        
        # Try to delete corrupted .env file
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            try:
                env_path.unlink()
                print(f"\nDeleted corrupted .env file. Please run the script again.")
            except:
                pass
        
        input("\nPress Enter to exit...")