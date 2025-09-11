import numpy as np
from sentence_transformers import SentenceTransformer

# Lazy load embedder
_embedder = None
def get_embedder():
    global _embedder
    if _embedder is None:
        model_path = os.path.join(os.path.dirname(__file__), "all-MiniLM-L6-v2")
        _embedder = SentenceTransformer(model_path)
    return _embedder

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors"""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_relevant_chunks(query_text, policy_index, top_k=15, min_score=0.3):
    """
    Given a query string, embed it and find top_k relevant chunks.
    """
    query_embedding = get_embedder().encode(query_text)

    scored = []
    for entry in policy_index:
        if "embedding" not in entry:
            continue
        emb_score = cosine_similarity(query_embedding, entry["embedding"])
        if emb_score >= min_score:
            scored.append((emb_score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:top_k]]