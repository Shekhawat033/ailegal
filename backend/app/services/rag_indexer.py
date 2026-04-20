import logging
import math
from pathlib import Path

from app.services.gemini_client import get_embedding

log = logging.getLogger(__name__)

# In-memory store: list of dicts {"text": str, "embedding": list[float]}
_collection = None

def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)

async def _build_index():
    global _collection
    _collection = []
    
    kb_path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.txt"
    if not kb_path.exists():
        log.warning(f"Knowledge base file not found at {kb_path}")
        return
        
    text = kb_path.read_text(encoding="utf-8")
    chunks = [c.strip() for c in text.split("\n\n") if c.strip() and not c.strip().startswith("#")]
    
    log.info(f"Indexing {len(chunks)} legal chunks into RAG store...")
    
    for chunk in chunks:
        try:
            emb = await get_embedding(chunk)
            _collection.append({"text": chunk, "embedding": emb})
        except Exception as e:
            log.warning(f"Failed to embed chunk: {e}")
            
    log.info("RAG index built successfully.")

async def search_legal_context(query: str, n_results: int = 3) -> str:
    global _collection
    if _collection is None:
        await _build_index()
        
    if not _collection:
        return "No relevant legal context available in the database."
        
    try:
        query_emb = await get_embedding(query)
    except Exception as e:
        log.warning(f"Failed to embed query: {e}")
        return "No relevant legal context found."
        
    # Calculate similarities
    scored_chunks = []
    for item in _collection:
        score = _cosine_similarity(query_emb, item["embedding"])
        scored_chunks.append((score, item["text"]))
        
    # Sort descending by score
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Get top N
    top_docs = [doc for score, doc in scored_chunks[:n_results]]
    
    if not top_docs:
        return "No relevant legal context found."
        
    return "\n---\n".join(top_docs)
