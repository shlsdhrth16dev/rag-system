from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    optimize_query: bool = True

class SourceDocument(BaseModel):
    source: str
    content: str
    score: Optional[float] = None
    chunk_id: Optional[int] = None
    
    # Allow extra fields in metadata
    model_config = {"extra": "ignore"} 

class QueryResponse(BaseModel):
    query: str
    optimized_query: Optional[str] = None
    answer: str
    sources: List[SourceDocument]
    tokens_used: int

class StatsResponse(BaseModel):
    total_documents: int
    embedding_model: str
    llm_model: str
