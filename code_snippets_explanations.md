# Code Snippets and Explanations for Thesis

This document contains important code snippets from the Frontend, Backend, and Data Processing pipelines of the Product Recommendation System, along with detailed explanations suitable for a thesis.

---

## 1. Frontend Important Sections

### 1.1 Managing State and Fetching Products (App.jsx)

This snippet demonstrates how the React frontend manages the application state and connects with the backend REST API to fetch product recommendations based on search queries, categories, and sorting preferences.

```javascript
  // Fetch products from backend
  const fetchProducts = async (query = "", sort = sortMethod, cat = category) => {
    setIsLoading(true);
    setProducts(null);
    setCurrentQuery(query);
    if (sort) setSortMethod(sort);
    if (cat !== undefined) setCategory(cat);

    try {
      let url = "";
      // If there's a search query, use the smart search endpoint
      if (query.trim()) {
        const params = new URLSearchParams({ q: query });
        url = `http://localhost:8000/api/search?${params.toString()}`;
      } 
      // If no query but there is a category, use browse endpoint
      else if (cat && cat !== "all") {
        const params = new URLSearchParams({ category: cat });
        url = `http://localhost:8000/api/browse?${params.toString()}`;
      } 
      // Fallback 
      else {
        url = `http://localhost:8000/api/search?q=`; 
      }

      const response = await fetch(url);
      const result = await response.json();

      let fetchedProducts = [];
      if (result.status === "success") {
        fetchedProducts = result.data;
      } else if (Array.isArray(result)) {
        fetchedProducts = result;
      }

      // Sort locally
      setProducts(sortProducts(fetchedProducts, sort));

    } catch (error) {
      console.error("Failed to connect to backend API.", error);
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  };
```

**Explanation:**
This asynchronous function, `fetchProducts`, is the core data-fetching mechanism in the frontend application. It constructs dynamic API URLs using the built-in `URLSearchParams` based on user inputs (search queries or category selections). 
- If a user enters a search string, it directs the request to the `/api/search` endpoint. 
- If a user navigates via a category dropdown, it directs the request to the `/api/browse` endpoint. 
The function makes an HTTP GET request using the `fetch` API, awaits the JSON response, handles potential errors or failed connections gracefully by setting an empty array, and finally passes the retrieved product data to a local `sortProducts` method to handle client-side sorting before updating the React component state via `setProducts`. The `setIsLoading` state ensures users see a loading indicator during network delays, enhancing the user experience.

### 1.2 User Input Handling (SearchBar.jsx)

This snippet shows how the Search component captures user inputs and triggers the search process.

```javascript
    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    return (
        <form className="search-bar-container" onSubmit={handleSubmit}>
            <select
                className="category-dropdown"
                value={currentCategory}
                onChange={(e) => onCategoryChange(e.target.value)}
                title="Browse by Category"
            >
                <option value="">📂 All Categories</option>
                {categoriesList.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                ))}
            </select>

            <input
                type="text"
                className="search-input"
                placeholder="Describe what you need — e.g. 'wireless earbuds under ₹2000'"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            />
            {/* ... sort dropdown and submit button omitted for brevity ... */}
        </form>
    );
```

**Explanation:**
The `SearchBar` component is a controlled React component that captures natural language search queries and category selections. The `handleSubmit` function intercepts the default HTML form submission behavior (`e.preventDefault()`), preventing a full page reload, and instead delegates the `query` value to the `onSearch` callback function defined in the parent `App` component. The category `<select>` dropdown dynamically loops through `categoriesList` ensuring the UI matches the datasets available from the backend. 

---

## 2. Backend Important Sections

### 2.1 The Smart Search Endpoint (main.py)

This represents the primary API route where the client interactions meet the intelligent system logic securely within FastAPI.

```python
@app.get("/api/search")
async def search_products(q: str = Query(..., description="Search query")):
    if df.empty:
        return {"status": "error", "message": "Dataset not loaded", "count": 0, "data": []}
        
    if not q or not q.strip():
        # If empty query, just return top general products
        top_items = df.sort_values(by='initial_rank', ascending=False).head(20)
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
```

**Explanation:**
This FastAPI endpoint securely exposes the product matching engine to the web. It is mapped to the `/api/search` URL via the `@app.get` decorator. When an HTTP requirement matches this route with a query string `q`, the backend executes four key operations: preprocessing the string into standardized NLP tokens, detecting core Named Entities (like brands and categories), and finally scoring/ranking the Pandas DataFrame based on those entities. It restricts the massive dataset down to a slice of the top 20 relevant items using `.head(20)` to ensure fast payload delivery, replaces `NaN` components with native Python `None` values to avoid strict JSON syntax errors, and builds a comprehensive dictionary response inclusive of how the system "understood" the query.

### 2.2 Intelligent Entity Detection (query_processor.py)

This is the Natural Language string parsing engine responsible for token entity recognition.

```python
def detect_entities(tokens: list, brands_set: set, categories_set: set) -> dict:
    """Detects brand, category, and keywords from tokens. Supports bigrams/unigrams."""
    entities = {
        "brands": set(),
        "categories": set(),
        "keywords": set()
    }
    
    brands_lower = {str(b).lower(): b for b in brands_set if b}
    categories_lower = {str(c).lower(): c for c in categories_set if c}
    
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
            entities["keywords"].add(token)
            
    return entities
```

**Explanation:**
The `detect_entities` function behaves as a lightweight Named Entity Recognition (NER) system tailored specifically for ecommerce catalogs. Rather than employing massive neural networks at runtime, which would increase system latency, this uses memory-optimized sets with time complexities of O(1) for lookups. It iterates across processed user tokens, cleanly classifying them into semantic buckets: `brands`, `categories`, or unmatched generic `keywords`. Crucially, it manages synonyms utilizing a `CATEGORY_ALIASES` mapping—so a user typing "smartphone" seamlessly maps internally to the technical dataset string "Cell Phones".

---

## 3. Data Processing and Intelligence (Colab Notebooks)

The following snippets are extracted from `colab_jsonl_category.ipynb` representing the system's intelligence generation phase.

### 3.1 Sentiment Analysis using RoBERTa

```python
# ==========================================
# 4. SENTIMENT ANALYSIS
# ==========================================
print("\n--- Running RoBERTa Sentiment Analysis ---")

# Keep max 30 reviews per product to optimize computation time
sampled_reviews = reviews_df.groupby('asin').apply(
    lambda x: x.sample(min(len(x), 30))
).reset_index(drop=True)

all_texts = sampled_reviews['body'].astype(str).tolist()

results = []
batch_size = 128
for i in tqdm(range(0, len(all_texts), batch_size)):
    batch = all_texts[i:i+batch_size]
    # sentiment_analyzer is a HuggingFace pipeline powered by the LiYuan/amazon-review-sentiment-analysis model
    preds = sentiment_analyzer(batch)
    results.extend(preds)

# Extract predicted numerical labels based on model classification text mapping 
sampled_reviews['sentiment'] = [int(r['label'].split()[0]) for r in results]

# Aggregate sentiment predictions mathematically back to the root product ASIN
review_agg = sampled_reviews.groupby('asin').agg({
    'sentiment': 'mean',
    'body': 'count'
}).rename(columns={'sentiment': 'calculated_sentiment_score', 'body': 'review_count'}).reset_index()
```

**Explanation:**
This cell performs the large-scale Natural Language Processing (NLP) crucial to the project. Instead of simply trusting raw Amazon ratings which can occasionally be skewed by bot manipulation or spam, the system ingests the raw user review strings. It leverages a state-of-the-art RoBERTa deep learning model configured through the Hugging Face `pipeline` architecture (mapped directly to a T4 GPU locally). To optimize graphical memory allocations and compute speed, reviews are passed through the neural network in batched arrays of 128 indices. The model evaluates the underlying semantics and outputs a deterministic integer star prediction per review. These outputs are mathematically averaged using Pandas `groupby` aggregations yielding a newly authenticated `calculated_sentiment_score` for each product ID.

### 3.2 Feature Scoring & Hybrid Ranking Vectorization

```python
# ==========================================
# 5. FEATURE SCORE & HYBRID RANK
# ==========================================
# ... [Dataframe Merging code omitted for brevity] ...

final_df['feature_text'] = final_df['brand'] + ' ' + CATEGORY_NAME + ' ' + final_df['title']

# TF-IDF feature score computation
tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_matrix = tfidf.fit_transform(final_df['feature_text'])
doc_lengths = tfidf_matrix.sum(axis=1)
min_len, max_len = doc_lengths.min(), doc_lengths.max()

# Normalize lengths to a 1-5 scalar point system
if max_len > min_len:
    final_df['feature_score'] = 1 + 4 * ((doc_lengths - min_len) / (max_len - min_len))
else:
    final_df['feature_score'] = 3.0
final_df['feature_score'] = np.asarray(final_df['feature_score']).flatten()

def calculate_rank(row):
    feat = row['feature_score']
    sent = row.get('calculated_sentiment_score', 0)
    stars = row.get('product_star_rating', 0)
    
    has_sent = pd.notna(sent) and sent > 0
    has_stars = pd.notna(stars) and stars > 0
    
    # Priority Hybrid Formulation
    if has_sent and has_stars:
        return (0.6 * sent) + (0.2 * stars) + (0.2 * feat)
    elif has_sent:
        return (0.7 * sent) + (0.3 * feat)
    elif has_stars:
        return (0.7 * stars) + (0.3 * feat)
    else:
        return feat
        
final_df['initial_rank'] = final_df.apply(calculate_rank, axis=1)
```

**Explanation:**
This cell performs the final transformation phases before dataset export. First, it extracts a quantitative `feature_score` by concatenating strings defining the product (brand, category, and title) and assessing their distinctiveness utilizing a Term Frequency-Inverse Document Frequency (TF-IDF) Machine Learning vectorizer. This generates a dense mathematical matrix that effectively grades the "richness" or detail orientation of a product listing. 

Secondly, the algorithm yields the definitive `initial_rank` composite score. This is computed through a nested conditional architecture defining a custom `calculate_rank` weighted hybrid equation algorithm. When completely mapped data spans are available, it intrinsically trusts the NLP sentiment generation above all else (60% weight), combining it equitably with raw platform reputation stars (20% weight), and algorithmic specification depth (20% weight) guaranteeing that generic listings or poorly modeled reviews do not catastrophically ruin organic product order matrices.
