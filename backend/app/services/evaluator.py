from typing import List, Dict, Any, Union
import numpy as np
from openai import OpenAI
from app.core.config import get_settings

class RAGEvaluator:
    """Evaluate RAG system performance using OpenRouter (LLM-as-a-Judge)"""
    
    def __init__(self):
        self.settings = get_settings()
        
        api_key = self.settings.OPENROUTER_API_KEY
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = self.settings.MODEL_NAME

    def evaluate_retrieval(
        self,
        queries: List[str],
        retrieved_docs: List[List[Dict[str, Any]]],
        relevant_docs: List[List[Union[int, str]]]
    ) -> Dict[str, float]:
        """
        Calculate retrieval metrics (Precision, Recall, F1)
        """
        
        precisions = []
        recalls = []
        
        for retrieved, relevant in zip(retrieved_docs, relevant_docs):
            # Extract IDs robustly
            retrieved_ids = set()
            for doc in retrieved:
                doc_id = doc.get('chunk_id') or doc.get('id')
                if doc_id is not None:
                    retrieved_ids.add(str(doc_id))
            
            relevant_set = {str(d) for d in relevant}
            
            intersection = retrieved_ids & relevant_set
            
            precision = len(intersection) / len(retrieved_ids) if retrieved_ids else 0.0
            recall = len(intersection) / len(relevant_set) if relevant_set else 0.0
            
            precisions.append(precision)
            recalls.append(recall)
        
        mean_precision = float(np.mean(precisions)) if precisions else 0.0
        mean_recall = float(np.mean(recalls)) if recalls else 0.0
        
        if (mean_precision + mean_recall) > 0:
            mean_f1 = 2 * mean_precision * mean_recall / (mean_precision + mean_recall)
        else:
            mean_f1 = 0.0

        return {
            "mean_precision": mean_precision,
            "mean_recall": mean_recall,
            "mean_f1": mean_f1
        }
    
    async def evaluate_generation(
        self,
        generated_answers: List[str],
        reference_answers: List[str],
        queries: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate answer quality using LLM-as-judge
        """
        
        scores = []
        
        for gen, ref, query in zip(generated_answers, reference_answers, queries):
            prompt = f"""
            You are an expert judge evaluating the quality of a RAG system's answer.
            
            Query: {query}
            
            Reference Answer (Ground Truth):
            {ref}
            
            Generated Answer:
            {gen}
            
            Rate the quality of the Generated Answer compared to the Reference Answer on a scale of 1 to 5.
            1 = Completely wrong or irrelevant
            3 = Partially correct but missing key identifying details
            5 = Perfect match or better quality than reference
            
            Return ONLY the integer score (e.g. 5). Do not output any text.
            Score:
            """
            
            try:
                # Use OpenRouter client
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=5,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/your-repo",
                        "X-Title": "RAG Evaluator"
                    }
                )
                
                content = response.choices[0].message.content.strip()
                score = int(''.join(filter(str.isdigit, content)))
                score = max(1, min(5, score))
                scores.append(score)
            except Exception as e:
                print(f"Error evaluating answer: {e}")
                scores.append(0)
        
        return {
            "mean_score": float(np.mean(scores)) if scores else 0.0,
            "scores": scores
        }
