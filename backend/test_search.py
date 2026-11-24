from fastapi.testclient import TestClient
import json
import asyncio
from main import app, load_data

queries = [
    "Samsung",
    "Smartphone",
    "Samsung Smartphone",
    "Samsung s24 case",
    "laptop under 500",
    "some_cell_phone_case_Samsung_s24"
]

def run_tests():
    # Force load data
    asyncio.run(load_data())
    
    client = TestClient(app)

    print("Fetching Categories...")
    r = client.get("/api/categories")
    print("Categories:", r.json().get('categories', [])[:5], "...")

    print("\n================================")
    print("Testing Search Edge Cases")
    print("================================\n")
    
    for q in queries:
        print(f"\n--- Query: '{q}' ---")
        try:
            r = client.get("/api/search", params={"q": q})
            data = r.json()
            if 'query_understanding' in data:
                print("Understanding:", json.dumps(data['query_understanding']))
                
            items = data.get('data', [])
            print(f"Returned {len(items)} items. Top 3:")
            for item in items[:3]:
                score = item.get('final_score')
                brand = item.get('brand', 'N/A')
                cat = item.get('category', 'N/A')
                title = item.get('title', 'N/A')[:60]
                print(f" - [{score}] {brand} | {cat} | {title}")
        except Exception as e:
            print("Error testing query:", e)

if __name__ == "__main__":
    run_tests()
