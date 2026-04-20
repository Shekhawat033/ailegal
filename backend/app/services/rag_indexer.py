import logging
from pathlib import Path

import chromadb
from chromadb.config import Settings

log = logging.getLogger(__name__)

# Initialize an in-memory Chroma client
_chroma_client = chromadb.Client(Settings(is_persistent=False))
_collection = None

def get_rag_collection():
    global _collection
    if _collection is not None:
        return _collection
        
    log.info("Initializing RAG vector store...")
    _collection = _chroma_client.get_or_create_collection(name="indian_law")
    
    # Load knowledge base
    kb_path = Path(__file__).resolve().parents[2] / "data" / "knowledge_base.txt"
    if kb_path.exists():
        text = kb_path.read_text(encoding="utf-8")
        # Simple chunking by paragraphs or double newlines
        chunks = [c.strip() for c in text.split("\n\n") if c.strip() and not c.strip().startswith("#")]
        
        if chunks:
            # We use the chunks as both the document content and the ID
            _collection.add(
                documents=chunks,
                ids=[f"chunk_{i}" for i in range(len(chunks))],
            )
            log.info(f"Indexed {len(chunks)} legal chunks into RAG store.")
    else:
        log.warning(f"Knowledge base file not found at {kb_path}")
        
    return _collection


def search_legal_context(query: str, n_results: int = 3) -> str:
    collection = get_rag_collection()
    if collection.count() == 0:
        return "No relevant legal context available in the database."
        
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )
    
    docs = results.get("documents", [[]])[0]
    if not docs:
        return "No relevant legal context found."
        
    # Join the retrieved snippets into a single string
    context = "\n---\n".join(docs)
    return context
