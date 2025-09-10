import os
import json
import fitz
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedder once
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    chunks = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("blocks")  # keep paragraph-level blocks
        for block_id, block in enumerate(text):
            block_text = block[4].strip()
            if block_text:
                chunks.append({
                    "policy": os.path.basename(pdf_path),
                    "page": page_num,
                    "chunk_id": block_id,
                    "text": block_text,
                    "embedding": embedder.encode(block_text).tolist()
                })
    return chunks


def build_and_save_index(policy_folder="public_policies", output_file="policy_index.json"):
    """Walk through policy_folder, process PDFs, and save JSON index"""
    index = []

    for root, _, files in os.walk(policy_folder):
        for filename in files:
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"Processing {pdf_path} ...")
                try:
                    chunks = extract_text_from_pdf(pdf_path)
                    index.extend(chunks)
                except Exception as e:
                    print(f"Skipping {pdf_path}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(index)} chunks into {output_file}")


if __name__ == "__main__":
    build_and_save_index()
