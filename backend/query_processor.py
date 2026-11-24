import string
import pandas as pd

STOPWORDS = {"a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
             "when", "where", "how", "why", "who", "which", "this", "that", "these",
             "those", "then", "just", "so", "than", "such", "both", "through",
             "about", "for", "is", "of", "to", "in", "it", "with", "on", "by", "at", "under"}

CATEGORY_ALIASES = {
    "smartphone": "Cell Phones",
    "smartphones": "Cell Phones",
    "mobile": "Cell Phones",
    "phone": "Cell Phones",
    "tv": "Electronics",
    "television": "Electronics",
    "laptop": "Computers&Accessories",
    "pc": "Computers&Accessories",
    "computer": "Computers&Accessories",
    "case": "Cell Phones", # Will boost Cell Phones items; could be combined with keyword match
    "cover": "Cell Phones"
}

def preprocess_query(query: str) -> list:
    """Converts to lowercase, removes punctuation, splits, removes stopwords."""
    if not query:
        return []
    
    # Lowercase
    query = str(query).lower()
    # Remove punctuation
    query = query.translate(str.maketrans('_-', '  ', string.punctuation.replace('_', '').replace('-', '')))
    
    # Tokenize
    tokens = query.split()
    # Remove stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

def detect_entities(tokens: list, brands_set: set, categories_set: set) -> dict:
    """Detects brand, category, and keywords from tokens. Supports bigrams/unigrams."""
    entities = {
        "brands": set(),
        "categories": set(),
        "keywords": set()
    }
    
    brands_lower = {str(b).lower(): b for b in brands_set if b}
    categories_lower = {str(c).lower(): c for c in categories_set if c}
    
    # Support basic bigrams for aliases like "phone case" -> "accessories" 
    # However since we removed "phone case" from aliases to keep it simple, we just process tokens.
    
    for token in tokens:
        if token in brands_lower:
            entities["brands"].add(brands_lower[token])
        elif token in categories_lower:
            entities["categories"].add(categories_lower[token])
        elif token in CATEGORY_ALIASES:
            mapped_cat = CATEGORY_ALIASES[token]
            if mapped_cat.lower() in categories_lower:
                entities["categories"].add(categories_lower[mapped_cat.lower()])
            else:
                entities["categories"].add(mapped_cat)
        else:
            # Check price constraint roughly
            if token.isdigit():
                # We could add price logic here, but for now treat as keyword 
                # e.g., "15000" in "under 15000"
                entities["keywords"].add(token)
            else:
                entities["keywords"].add(token)
            
    return entities

def score_and_rank_products(df: pd.DataFrame, entities: dict) -> pd.DataFrame:
    """Calculates final score and returns sorted dataframe."""
    if df.empty:
        return df

    relevance_scores = pd.Series(0, index=df.index, dtype=float)
    
    brands = entities.get("brands", set())
    categories = entities.get("categories", set())
    keywords = entities.get("keywords", set())

    # Brand match -> +100
    if brands:
        brands_lower = {b.lower() for b in brands}
        brand_mask = df['brand'].astype(str).str.lower().isin(brands_lower)
        relevance_scores[brand_mask] += 100
        
    # Category match -> +80
    if categories:
        categories_lower = {c.lower() for c in categories}
        cat_mask = df['category'].astype(str).str.lower().isin(categories_lower)
        relevance_scores[cat_mask] += 80

    # Keyword matches
    for kw in keywords:
        # Title keyword match -> +40
        title_mask = df['title'].astype(str).str.lower().str.contains(kw, na=False, regex=False)
        relevance_scores[title_mask] += 40

    df_scored = df.copy()
    df_scored['relevance_score'] = relevance_scores
    
    # Filter if user provided any search terms
    if brands or categories or keywords:
        df_scored = df_scored[df_scored['relevance_score'] > 0]

    # Combine with rank
    df_scored['final_score'] = df_scored['relevance_score'] + df_scored['initial_rank'].fillna(0)
    
    # Sort
    df_sorted = df_scored.sort_values(by=['final_score', 'rating', 'review_count'], ascending=[False, False, False])
    
    return df_sorted
