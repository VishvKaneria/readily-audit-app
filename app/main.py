import os
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pdf_parser import extract_questions
from policy_retriever import load_policy_index, find_relevant_chunks
from gemini_client import analyze_question_with_gemini

app = FastAPI()
policy_index = None

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_policy_index():
    """
    Download policy_index.json from OneDrive (link stored in env var)
    and cache it in memory for fast lookups.
    """
    global policy_index
    policy_url = os.getenv("POLICY_JSON_URL")

    if not policy_url:
        raise RuntimeError("POLICY_JSON_URL is not set in environment variables")

    print("Downloading policy_index.json from OneDrive...")
    resp = requests.get(policy_url)
    resp.raise_for_status()
    policy_index = resp.json()
    print(f"Loaded {len(policy_index)} records from policy index")

@app.get("/")
def root():
    return {"msg": "Audit API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    
    global policy_index
    if not policy_index:
        return JSONResponse(
            status_code=500,
            content={"error": "Policy index not loaded"},
        )
    
    print("file uploaded")
    pdf_bytes = await file.read()
    questions = extract_questions(pdf_bytes)

    results = []
    for q in questions:
        relevant_chunks = find_relevant_chunks(q["question"], policy_index, top_k=15)
        analysis = analyze_question_with_gemini(q["question"], relevant_chunks)

        results.append({
            "id": q["id"],
            "question": q["question"],
            "requirement_met": analysis.get("requirement_met", False),
            "policy": analysis.get("policy", None),
            "page": analysis.get("page", None),
            "evidence": analysis.get("evidence", "")
        })

    return {"questions": results}