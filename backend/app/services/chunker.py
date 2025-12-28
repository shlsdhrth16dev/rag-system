from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
from typing import List, Dict, Any
from langchain_core.documents import Document

class SmartChunker:
    """Intelligent document chunking with token awareness"""
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._token_length,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunked_docs = []
        for doc in documents:
            splits = splitter.split_text(doc.page_content)
            for i, chunk_content in enumerate(splits):
                new_metadata = doc.metadata.copy()
                new_metadata.update({
                    "chunk_id": i,
                    "total_chunks": len(splits)
                })
                chunked_docs.append(Document(
                    page_content=chunk_content,
                    metadata=new_metadata
                ))
        return chunked_docs
    
    def _token_length(self, text: str) -> int:
        return len(self.encoding.encode(text))
