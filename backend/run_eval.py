import asyncio
import os
import sys

# Add app to path
sys.path.append(os.getcwd())

from app.services.evaluator import RAGEvaluator

async def main():
    print("Initializing Evaluator...")
    evaluator = RAGEvaluator()

    # --- 1. Define Synthetic Test Data ---
    print("\n--- 1. Evaluating Retrieval (Mock Data) ---")
    
    queries = [
        "What is the capital of France?",
        "How does RAG work?"
    ]
    
    # retrieved_docs: list of lists of dicts
    # Scenario: Query 1 retrieves correct doc (id: 101). Query 2 retrieves irrelevant data.
    retrieved_docs = [
        [{"id": 101, "content": "Paris is the capital of France."}], 
        [{"id": 205, "content": "Bananas are yellow."}] 
    ]
    
    # relevant_docs: list of lists of correct IDs
    relevant_docs = [
        [101],    # Query 1 expects doc 101
        [300]     # Query 2 expects doc 300 (which we missed)
    ]
    
    retrieval_metrics = evaluator.evaluate_retrieval(queries, retrieved_docs, relevant_docs)
    print(f"Retrieval Metrics: {retrieval_metrics}")
    
    # --- 2. Evaluating Generation (LLM-as-a-Judge) ---
    print("\n--- 2. Evaluating Generation (LLM Judge) ---")
    
    generated_answers = [
        "The capital of France is Paris.",
        "RAG involves retrieving documents and generating answers."
    ]
    
    reference_answers = [
        "Paris is the capital city of France.",
        "Retrieval-Augmented Generation (RAG) combines an information retrieval component with a text generator model."
    ]
    
    gen_metrics = await evaluator.evaluate_generation(generated_answers, reference_answers, queries)
    print(f"Generation Metrics: {gen_metrics}")

if __name__ == "__main__":
    asyncio.run(main())
