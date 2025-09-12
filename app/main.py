import os
import json
import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from pdf_parser import extract_questions
from policy_retriever import find_relevant_chunks
from gemini_client import analyze_question_with_gemini

policy_index = []

@asynccontextmanager
async def lifespan(app: FastAPI):

    global policy_index
    merged = []

    # Resolve absolute path for policy_parts folder
    parts_dir = os.path.join(os.path.dirname(__file__), "policy_parts")

    for filename in sorted(os.listdir(parts_dir)):
        if filename.startswith("policy_index_part") and filename.endswith(".json"):
            file_path = os.path.join(parts_dir, filename)
            print(f"Loading {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                merged.extend(json.load(f))

    policy_index = merged
    print(f"Loaded {len(policy_index)} records from {len(os.listdir(parts_dir))} part files")
    yield
    print("Server shutting down...")


app = FastAPI(lifespan=lifespan)

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    pdf_bytes = await file.read()
    questions = extract_questions(pdf_bytes)

    # Build async tasks for all questions
    async def analyze(q):
        relevant_chunks = find_relevant_chunks(q["question"], policy_index, top_k=15)
        # Wrap the sync Gemini call into a thread (so asyncio can parallelize)
        analysis = await asyncio.to_thread(analyze_question_with_gemini, q["question"], relevant_chunks)
        return {
            "id": q["id"],
            "question": q["question"],
            "requirement_met": analysis.get("requirement_met", False),
            "policy": analysis.get("policy"),
            "page": analysis.get("page"),
            "evidence": analysis.get("evidence", "")
        }

    # Run all Gemini calls concurrently
    results = await asyncio.gather(*(analyze(q) for q in questions))

    return {"questions": results}