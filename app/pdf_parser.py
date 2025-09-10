import fitz
import re

def extract_questions(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    blocks = []
    for page in doc:
        for block in page.get_text("blocks"):
            blocks.append(block[4])  # block[4] contains the text

    # Merge all blocks into one string
    full_text = " ".join(blocks)
    full_text = " ".join(full_text.split())  # collapse newlines and spaces

    # Capture audit-style questions ending in ?
    matches = re.findall(r"(Does the P&P[^?]+\?)", full_text)

    questions = []
    for match in matches:
        q = match.strip()
        questions.append(q)

    # Deduplicate
    unique_questions = list(dict.fromkeys(questions))

    return [{"id": i+1, "question": q} for i, q in enumerate(unique_questions)]