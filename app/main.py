from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pdf_parser import extract_questions
from policy_retriever import load_policy_index, find_relevant_chunks
from gemini_client import analyze_question_with_gemini
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
policy_index = load_policy_index("policy_index.json")

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "Audit API is running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
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