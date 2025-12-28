from openai import OpenAI
from typing import List, Dict, Any
from app.core.config import get_settings
import os

settings = get_settings()

class RAGGenerator:
    """Generate answers using OpenRouter (OpenAI-compatible)"""
    
    SYSTEM_PROMPT = """You are a helpful AI assistant. Answer questions 
    based ONLY on the provided context. If the context doesn't contain 
    the answer, say "I don't have enough information to answer that."
    
    Always cite your sources by referencing [Doc X] where X is the 
    document number."""
    
    def __init__(self):
        # Initialize OpenAI client with OpenRouter base URL
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = settings.MODEL_NAME
    
    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]],
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        # Format context
        context = self._format_context(context_docs)
        
        # Build prompt
        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""
        
        try:
            # Generate
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=500,
                extra_headers={
                    "HTTP-Referer": "https://github.com/your-repo", # Recommended by OpenRouter
                    "X-Title": "RAG System"
                }
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": context_docs,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            print(f"Generation failed: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "tokens_used": 0
            }
    
    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        formatted = []
        for i, doc in enumerate(docs, 1):
            content = doc.get('content', '')
            formatted.append(f"[Doc {i}]\n{content}\n")
        return "\n".join(formatted)
