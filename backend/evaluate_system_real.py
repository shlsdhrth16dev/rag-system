import asyncio
import os
import sys
import requests
import json
from typing import List, Dict

# Add app to path
sys.path.append(os.getcwd())

from app.services.evaluator import RAGEvaluator

API_URL = "http://localhost:8000/api/v1/rag"

# --- Test Data ---
TEST_CONTENT = """
The "Project Antigravity" is a secret initiative started in 2024 to develop anti-gravity propulsion using quantum field manipulation.
The core component is the "Zero-Point Drive", which was invented by Dr. Sarah Connor.
The project is headquartered in a submerged facility under the Atlantic Ocean.
"""

TEST_QA = [
    {
        "query": "Who invented the Zero-Point Drive?",
        "expected": "Dr. Sarah Connor invented the Zero-Point Drive."
    },
    {
        "query": "Where is Project Antigravity headquartered?",
        "expected": "It is headquartered in a submerged facility under the Atlantic Ocean."
    },
    {
        "query": "When did the project start?",
        "expected": "The project started in 2024."
    }
]

async def eval_system():
    print("=== Starting Full System Evaluation ===")
    
    # 1. Upload Test Data
    print("\n[1/4] Uploading Test Content...")
    # Create temp file
    filename = "antigravity_test.txt"
    with open(filename, "w") as f:
        f.write(TEST_CONTENT)
    
    try:
        with open(filename, "rb") as f:
            files = {'files': (filename, f, 'text/plain')}
            res = requests.post(f"{API_URL}/upload", files=files)
            if res.status_code != 201:
                print(f"❌ Upload failed: {res.text}")
                return
            print("✅ Upload Successful")
            print(f"   Response: {res.json()}")
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return
    finally:
        if os.path.exists(filename):
            os.remove(filename)
            
    # 2. Query System
    print("\n[2/4] Querying System...")
    generated_answers = []
    actual_queries = []
    
    for item in TEST_QA:
        query = item["query"]
        print(f"   Query: {query}")
        try:
            res = requests.post(f"{API_URL}/query", json={"query": query})
            if res.status_code == 200:
                ans = res.json()["answer"]
                print(f"   Answer: {ans}")
                generated_answers.append(ans)
                actual_queries.append(query)
            else:
                print(f"   ❌ Failed: {res.text}")
                generated_answers.append("Error")
                actual_queries.append(query)
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            generated_answers.append("Error")
            actual_queries.append(query)
            
    # 3. Evaluate Results (LLM Judge)
    print("\n[3/4] Running LLM Evaluation (Accuracy Check)...")
    evaluator = RAGEvaluator()
    reference_answers = [item["expected"] for item in TEST_QA]
    
    metrics = await evaluator.evaluate_generation(
        generated_answers, 
        reference_answers, 
        actual_queries
    )
    
    # 4. Final Report
    print("\n" + "="*40)
    print("       📊 SYSTEM ACCURACY REPORT       ")
    print("="*40)
    print(f"Mean Accuracy Score: {metrics['mean_score']} / 5.0")
    print("-" * 40)
    for i, score in enumerate(metrics['scores']):
        print(f"Q: {actual_queries[i]}")
        print(f"Expected: {reference_answers[i]}")
        print(f"Actual:   {generated_answers[i]}")
        print(f"Score:    {score}/5")
        print("-" * 40)
        
    if metrics['mean_score'] >= 4.0:
        print("\n✅ SYSTEM RESULT: PASS (Ready for Showcase)")
    else:
        print("\n⚠️ SYSTEM RESULT: NEEDS IMPROVEMENT")

if __name__ == "__main__":
    asyncio.run(eval_system())
