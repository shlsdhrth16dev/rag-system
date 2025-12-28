from sqlalchemy import func, text
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.services.embedder import EmbeddingService
from app.core.database import Document

class HybridRetriever:
    """Combine semantic and keyword search"""
    
    def __init__(self, db_session: Session, embedder: EmbeddingService):
        self.db = db_session
        self.embedder = embedder
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        semantic_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        try:
            # Get query embedding
            query_emb = self.embedder.embed_query(query)
            
            # Semantic search using cosine similarity
            semantic_results = self._semantic_search(query_emb, top_k * 2)
            
            # Keyword search using PostgreSQL FTS
            keyword_results = self._keyword_search(query, top_k * 2)
        except Exception as e:
            print(f"Retriever Error: {e}")
            raise e
        
        # Combine and rerank
        combined = self._hybrid_rerank(
            semantic_results, 
            keyword_results,
            semantic_weight
        )
        
        return combined[:top_k]
    
    def _semantic_search(self, query_emb: List[float], k: int) -> List[Dict[str, Any]]:
        # Using pgvector cosine distance operator
        results = self.db.query(
            Document.id,
            Document.content,
            Document.doc_metadata,
            Document.embedding.cosine_distance(query_emb).label('distance')
        ).order_by(
            Document.embedding.cosine_distance(query_emb)
        ).limit(k).all()
        
        return [
            {
                "id": r.id,
                "content": r.content,
                "metadata": r.doc_metadata,
                "score": 1 - r.distance  # Convert distance to similarity
            }
            for r in results
        ]
    
    def _keyword_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        # PostgreSQL full-text search
        # english config is standard
        ts_query = func.plainto_tsquery('english', query)
        
        results = self.db.query(
            Document.id,
            Document.content,
            Document.doc_metadata,
            func.ts_rank(
                func.to_tsvector('english', Document.content),
                ts_query
            ).label('rank')
        ).filter(
            func.to_tsvector('english', Document.content).op('@@')(ts_query)
        ).order_by(text('rank DESC')).limit(k).all()
        
        return [
            {
                "id": r.id,
                "content": r.content,
                "metadata": r.doc_metadata,
                # Normalize raw rank loosely to 0-1 range for combination 
                # (simple implementation, real world might need better normalization)
                "score": 0.5 + (r.rank / 2) if r.rank < 1 else 1.0 
            }
            for r in results
        ]
    
    def _hybrid_rerank(self, semantic, keyword, weight):
        # Combine scores with weighted average
        combined = {}
        
        for result in semantic:
            combined[result['id']] = {
                **result,
                'final_score': result['score'] * weight
            }
        
        for result in keyword:
            if result['id'] in combined:
                combined[result['id']]['final_score'] += \
                    result['score'] * (1 - weight)
            else:
                combined[result['id']] = {
                    **result,
                    'final_score': result['score'] * (1 - weight)
                }
        
        return sorted(
            combined.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )
