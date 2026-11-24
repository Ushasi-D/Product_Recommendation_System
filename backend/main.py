from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import pandas as pd
from typing import Optional

from query_processor import preprocess_query, detect_entities, score_and_rank_products

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)

# Global variables
df = pd.DataFrame()
brands_set = set()
categories_set = set()

@app.on_event("startup")
async def load_data():
    global df, brands_set, categories_set

    filepath = os.path.join(BASE_DIR, "final_master_dataset.jsonl")
    
    if os.path.exists(filepath):
        try:
            print(f"Loading master dataset from {filepath}...")
            # Load the JSONL into a Pandas DataFrame
            df = pd.read_json(filepath, lines=True)
            
            # Basic cleanup / fill missing values to prevent Nan errors
            for col in ['brand', 'category', 'title']:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str)
            if 'initial_rank' not in df.columns:
                df['initial_rank'] = 0
            if 'price' not in df.columns:
                df['price'] = 0.0
                
            # Extract unique Brands and Categories
            brands_set = set(df[df['brand'] != '']['brand'].unique())
            categories_set = set(df[df['category'] != '']['category'].unique())
            
            # Remove "Unknown" if it somehow got in
            brands_set.discard('Unknown')
            categories_set.discard('Unknown')

            print(f"Server ready! Loaded {len(df)} products.")
            print(f"Extracted {len(brands_set)} brands and {len(categories_set)} categories.")
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            df = pd.DataFrame()
    else:
        print(f"Error: {filepath} not found!")


@app.get("/api/search")
async def search_products(q: str = Query(..., description="Search query")):
    if df.empty:
        return {"status": "error", "message": "Dataset not loaded", "count": 0, "data": []}
        
    if not q or not q.strip():
        # If empty query, just return top general products
        top_items = df.sort_values(by='initial_rank', ascending=False).head(20)
        # Convert NaN to None for JSON serialization
        results = top_items.where(pd.notnull(top_items), None).to_dict(orient="records")
        return {"status": "success", "count": len(results), "data": results, "query_understanding": "Empty Query"}

    # 1. Preprocess
    tokens = preprocess_query(q)
    
    # 2. Extract Entities
    entities = detect_entities(tokens, brands_set, categories_set)
    
    # 3. Score and Rank
    ranked_df = score_and_rank_products(df, entities)
    
    # 4. Take top 20
    top_items = ranked_df.head(20).copy()
    
    # Clean up output
    results = top_items.where(pd.notnull(top_items), None).to_dict(orient="records")
    
    query_interpretation = {
        "identified_brands": list(entities["brands"]),
        "identified_categories": list(entities["categories"]),
        "unmatched_keywords": list(entities["keywords"])
    }
    
    return {
        "status": "success", 
        "count": len(results), 
        "data": results,
        "query_understanding": query_interpretation
    }


@app.get("/api/browse")
async def browse_category(category: str = Query(..., description="Category name to browse")):
    if df.empty:
        return {"status": "error", "message": "Dataset not loaded", "count": 0, "data": []}
        
    if not category or not category.strip():
        return {"status": "error", "message": "Category parameter is required", "count": 0, "data": []}

    cat_lower = category.lower().strip()
    
    # Filter by exact category (case-insensitive)
    cat_mask = df['category'].str.lower() == cat_lower
    category_df = df[cat_mask]
    
    # Sort by initial_rank
    top_items = category_df.sort_values(by='initial_rank', ascending=False).head(20)
    
    results = top_items.where(pd.notnull(top_items), None).to_dict(orient="records")
    
    return {
        "status": "success", 
        "count": len(results), 
        "data": results,
        "category_browsed": category
    }


@app.get("/api/categories")
async def get_categories():
    """Returns exactly the available categories dynamically pulled from the dataset"""
    return {"categories": sorted(list(categories_set))}


@app.get("/api/brands")
async def get_brands():
    """Returns exactly the available brands dynamically pulled from the dataset"""
    return {"brands": sorted(list(brands_set))}


@app.get("/")
async def root():
    return {
        "message": "Product Recommendation System - Smart Engine Active", 
        "total_products": len(df),
        "total_categories": len(categories_set),
        "total_brands": len(brands_set)
    }

# Backward compatibility for the old endpoint while frontend is transitioning
@app.get("/api/recommendations")
async def fallback_recommendations(
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query("rank_desc"),
    category: Optional[str] = Query(None)
):
    if q and q.strip():
        return await search_products(q=q)
    elif category and category.lower() != "all":
        return await browse_category(category=category)
    else:
        # Just return top 20 overall if no search and category is 'all' or empty
        if df.empty:
            return {"status": "error", "count": 0, "data": []}
        top_items = df.sort_values(by='initial_rank', ascending=False).head(20)
        results = top_items.where(pd.notnull(top_items), None).to_dict(orient="records")
        return {"status": "success", "count": len(results), "data": results}
