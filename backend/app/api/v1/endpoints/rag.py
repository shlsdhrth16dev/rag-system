from fastapi import APIRouter, UploadFile, HTTPException, Depends, File
from typing import List
from sqlalchemy.orm import Session
import json
import tempfile
import os
import shutil

from app.core.database import get_db, Document
from app.core.config import get_settings
from app.services.document_loader import DocumentLoader
from app.services.chunker import SmartChunker
from app.services.embedder import EmbeddingService
from app.services.retriever import HybridRetriever
from app.services.generator import RAGGenerator
from app.services.query_optimizer import QueryOptimizer
from app.models.rag import QueryRequest, QueryResponse, StatsResponse
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

@router.post("/upload", status_code=201)
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process documents"""
    loader = DocumentLoader()
    chunker = SmartChunker()
    embedder = EmbeddingService()
    
    documents_processed = 0
    total_chunks = 0
    
    try:
        all_chunks = []
        source_files = []
        
        for file in files:
            # Create a secure temp file
            # delete=False because Windows can't open open files by name
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                temp_path = tmp.name
            
            try:
                # Load based on extension
                if file.filename.lower().endswith('.pdf'):
                    docs = loader.load_pdf(temp_path)
                elif file.filename.lower().endswith('.txt'):
                    docs = loader.load_text(temp_path)
                else:
                    # Skip unsupported but don't crash whole batch? 
                    # For now raise to be explicit
                    raise HTTPException(400, f"Unsupported file type: {file.filename}")
                
                # Chunk
                chunks = chunker.chunk_documents(docs)
                all_chunks.extend(chunks)
                source_files.append(file.filename)
                documents_processed += 1
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        if not all_chunks:
            return {"status": "success", "message": "No content processed"}

        # Generate embeddings (batching handled in service)
        texts = [c.page_content for c in all_chunks]
        embeddings = embedder.embed_texts(texts)
        
        # Store in DB
        new_docs = []
        for i, chunk in enumerate(all_chunks):
            # Source should be in metadata from loader, but fallback to filename if needed
            # Our loader puts source in metadata
            source = chunk.metadata.get('source', 'unknown')
             # If source is the temp path, we might want to fix it to the original filename?
             # For now, let's just ensure we track it.
             
            doc = Document(
                content=chunk.page_content,
                embedding=embeddings[i],
                doc_metadata=json.dumps(chunk.metadata),
                source=source
            )
            db.add(doc)
            new_docs.append(doc)
        
        db.commit()
        total_chunks = len(new_docs)
        
        return {
            "status": "success",
            "documents_processed": documents_processed,
            "chunks_created": total_chunks,
            "files": source_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Processing failed: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Query the RAG system"""
    start_time = time.time()
    
    if not request.query.strip():
        logger.warning("Empty query received")
        raise HTTPException(400, "Query cannot be empty")
        
    logger.info("Query received", extra={"query": request.query, "optimize": request.optimize_query})

        
    try:
        embedder = EmbeddingService()
        retriever = HybridRetriever(db, embedder)
        generator = RAGGenerator()
        optimizer = QueryOptimizer()
        
        final_query = request.query
        optimized_query_str = None
        
        if request.optimize_query:
            final_query = optimizer.optimize(request.query)
            if final_query != request.query:
                optimized_query_str = final_query
        
        # Retrieve relevant docs
        docs = retriever.retrieve(final_query, top_k=request.top_k)
        
        # Generate answer
        result = generator.generate_answer(request.query, docs)
        
        # Map sources to response model
        sources = []
        for doc in result.get("sources", []):
            # Parse metadata if string
            meta = doc.get('metadata', {})
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except:
                    pass
                    
            sources.append({
                "source": doc.get('source') or meta.get('source', 'unknown'),
                "content": doc.get('content', '')[:200] + "...", # Snippet
                "score": doc.get('score'),
                "chunk_id": meta.get('chunk_id')
            })


        
        latency = (time.time() - start_time) * 1000
        logger.info("Query processed", extra={
            "query": request.query,
            "optimized_query": optimized_query_str,
            "tokens_used": result.get("tokens_used", 0),
            "doc_count": len(docs),
            "latency_ms": round(latency, 2)
        })
        
        return {
            "query": request.query,
            "optimized_query": optimized_query_str,
            "answer": result["answer"],
            "sources": sources,
            "tokens_used": result.get("tokens_used", 0)
        }
        
    except Exception as e:
        logger.error("Query failed", extra={"error": str(e), "query": request.query}, exc_info=True)
        raise HTTPException(500, str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    doc_count = db.query(Document).count()
    
    return {
        "total_documents": doc_count,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.MODEL_NAME
    }
