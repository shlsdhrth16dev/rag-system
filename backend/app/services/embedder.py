import google.generativeai as genai
from typing import List, Dict
from app.core.config import get_settings

settings = get_settings()

class EmbeddingService:
    """Generate embeddings using Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in configuration")
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = settings.EMBEDDING_MODEL
        self.cache: Dict[str, List[float]] = {}
    
    def embed_texts(self, texts: List[str], batch_size: int = 20) -> List[List[float]]: # Batch size limited for Gemini
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # Check cache
            uncached = [t for t in batch if t not in self.cache]
            
            if uncached:
                try:
                    # Gemini embedding call
                    # Task types: 'retrieval_document' (for corpus), 'retrieval_query' (for queries)
                    # We default to 'retrieval_document' for bulk storage
                    result = genai.embed_content(
                        model=self.model,
                        content=uncached,
                        task_type="retrieval_document",
                        title="RAG Document" # Required for retrieval_document
                    )
                    
                    # Result is dict with 'embedding' key which is a list (if single) or list of lists
                    # embed_content returns dict: {'embedding': [values]} for single
                    # or list of values for multiple? API behavior varies by version
                    # Checking docs: embed_content helper returns dict with 'embedding'. 
                    # For list input, it's 'embedding': [ [v1], [v2] ]
                    
                    batch_vectors = result['embedding']
                    
                    for j, vec in enumerate(batch_vectors):
                        self.cache[uncached[j]] = vec
                        
                except Exception as e:
                    print(f"Embedding failed: {e}")
                    # Fallback or retry? Raising for now to be safe
                    raise e
            
            # Get from cache
            batch_embeddings = [self.cache[t] for t in batch]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        if query in self.cache:
            return self.cache[query]
        
        result = genai.embed_content(
            model=self.model,
            content=query,
            task_type="retrieval_query"
        )
        
        embedding = result['embedding']
        self.cache[query] = embedding
        return embedding
