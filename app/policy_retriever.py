import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Lazy load embedder
_embedder = None
def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors"""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_policy_index(index_file: str = "policy_index.json"):
    if not os.path.exists(index_file):
        print(f"Index file not found: {index_file}")
        return []
        
    with open(index_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for entry in data:
        entry["embedding"] = np.array(entry["embedding"], dtype=float)

    return data

def find_relevant_chunks(query_text, policy_index, top_k=15, min_score=0.3):
    """
    Given a query string, embed it and find top_k relevant chunks.
    """
    query_embedding = get_embedder().encode(query_text)

    scored = []
    for entry in policy_index:
        emb_score = cosine_similarity(query_embedding, entry["embedding"])
        if emb_score >= min_score:
            scored.append((emb_score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]