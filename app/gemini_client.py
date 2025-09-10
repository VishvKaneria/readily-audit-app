import os
import json
import requests
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("VERTEX_API_KEY")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"


def analyze_question_with_gemini(question: str, chunks: list) -> dict:
    # Build context including metadata
    context = "\n\n".join(
        f"Policy: {c['policy']} | Page: {c['page']}\nText: {c['text']}"
        for c in chunks
    )

    prompt = f"""
    You are an audit compliance assistant.

    Requirement: {question}

    Context from policies:
    {context}

    Task:
    - Check if the requirement is satisfied in ANY of the above chunks.
    - If yes, return:
        - requirement_met = true
        - evidence = the full **paragraph(s)** from the matching chunk (direct quote, no paraphrasing)
        - policy = the policy filename
        - page = the page number
    - Pay special attention to timing words (e.g., "24 hours", "next business day") and enrollment/eligibility phrases (e.g., "remain enrolled", "while receiving hospice", "Fraud, Waste, Abuse") if they appear in the requirement.
    - If multiple matches exist, return the most relevant single paragraph.
    - If not found, return requirement_met = false, policy = null, page = null, evidence = "".

    Respond ONLY in valid JSON:
    {{
        "requirement_met": true/false,
        "evidence": "...",
        "policy": "...",
        "page": number
    }}
    """

    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(API_URL, headers=headers, params=params, json=body)
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Try parsing JSON safely
        try:
            return json.loads(text)
        except Exception:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            return {
                "requirement_met": False,
                "evidence": "",
                "policy": None,
                "page": None
            }
    except Exception as e:
        return {
            "requirement_met": False,
            "evidence": f"Error: {str(e)}",
            "policy": None,
            "page": None
        }
