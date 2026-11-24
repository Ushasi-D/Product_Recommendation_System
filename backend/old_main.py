from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "processed_products.json")
# Fallback to mock data if processed not available
if not os.path.exists(DATA_FILE):
    DATA_FILE = os.path.join(os.path.dirname(__file__), "mock_data.json")

# ==========================================
# IN-MEMORY CACHE & SEARCH INDEX
# ==========================================
products_db = []
tfidf_vectorizer = None
tfidf_matrix = None

@app.on_event("startup")
async def load_data():
    global products_db, tfidf_vectorizer, tfidf_matrix
    print(f"Loading database from {DATA_FILE}...")
    
    try:
        with open(DATA_FILE, "r") as f:
            products_db = json.load(f)
            
        print(f"Successfully loaded {len(products_db)} products.")
        
        text_corpus = []
        for p in products_db:
            title = p.get("title", "")
            brand = p.get("brand", "")
            # If your items.csv had categories, we could append it here!
            text_corpus.append(f"{brand} {title}".lower())
        
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(text_corpus)
        print("Search Index built successfully!")
        
    except FileNotFoundError:
        print(f"ERROR: {DATA_FILE} not found!")

@app.get("/api/recommendations")
async def get_recommendations(
    q: str = Query(None, description="Search query"),
    sort: str = Query("rank_desc", description="Sorting method: rank_desc, rank_asc, price_low, price_high")
):
    global products_db, tfidf_vectorizer, tfidf_matrix
    results = []
    
    if q and q.strip():
        q_lower = q.lower()
        query_vector = tfidf_vectorizer.transform([q_lower])
        similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        for idx in similarity_scores.argsort()[::-1]:
            # TF-IDF threshold check.
            if similarity_scores[idx] > 0.01:
                 product = products_db[idx].copy()
                 product['search_relevance'] = similarity_scores[idx]
                 results.append(product)
            # Fallback for exact word matches if TF-IDF similarity is very low but word is in text
            elif q_lower in str(products_db[idx].get("title", "")).lower() or q_lower in str(products_db[idx].get("brand", "")).lower():
                 product = products_db[idx].copy()
                 product['search_relevance'] = 0.01
                 results.append(product)
    else:
        results = products_db.copy()

    # 2. SORTING LOGIC
    if sort == "price_low":
        results = sorted(results, key=lambda x: x.get('price', 0))
    elif sort == "price_high":
        results = sorted(results, key=lambda x: x.get('price', 0), reverse=True)
    elif sort == "rank_asc":
        # Lowly recommended to Highly recommended
        results = sorted(results, key=lambda x: x.get('initial_rank', 0))
    else:
        # Default: rank_desc (Highly recommended to Lowly recommended)
        # Note: If there was a search query, it's currently sorted by relevance. 
        # If we want the BEST products among the SEARCH RESULTS, we sort by initial_rank here.
        results = sorted(results, key=lambda x: x.get('initial_rank', 0), reverse=True)
        
    return {"status": "success", "count": len(results), "data": results}

@app.get("/")
async def root():
    return {"message": "Welcome to the Intelligent Recommendation System API"}
