from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()

class QueryOptimizer:
    """Optimize queries for better retrieval using OpenRouter"""
    
    SYSTEM_PROMPT = """You are a helpful assistant that improves search queries. 
    Take the user's input/question and rephrase it to be a better semantic search query.
    Remove filler words, fix typos, and focus on keywords.
    Output ONLY the optimized query. Do not explain."""
    
    def __init__(self):
        # Switch to OpenRouter
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = settings.MODEL_NAME
    
    def optimize(self, query: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Query optimization failed: {e}")
            return query # Fallback as-is
