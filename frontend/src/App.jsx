import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import RecommendationList from './components/RecommendationList';
import './App.css';

function App() {
  const [products, setProducts] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");
  const [sortMethod, setSortMethod] = useState("relevance");
  const [category, setCategory] = useState("");
  const [categoriesList, setCategoriesList] = useState([]);

  // Fetch available categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/categories");
        const data = await response.json();
        if (data && data.categories) {
          setCategoriesList(data.categories);
        }
      } catch (err) {
        console.error("Failed to fetch categories", err);
      }
    };
    fetchCategories();
    // Default load some products
    fetchProducts("", "relevance", "");
  }, []);

  // Sort products locally
  const sortProducts = (prodList, method) => {
    if (!prodList) return prodList;
    const sorted = [...prodList];
    if (method === "price_low") {
      sorted.sort((a, b) => (a.price || 0) - (b.price || 0));
    } else if (method === "price_high") {
      sorted.sort((a, b) => (b.price || 0) - (a.price || 0));
    } else {
      // 'relevance' - assume already sorted by backend final_score
      // We don't re-sort unless they had changed it and changed it back, 
      // but since we keep the original list from backend, we can just rely on final_score if present
      sorted.sort((a, b) => (b.final_score || b.initial_rank || 0) - (a.final_score || a.initial_rank || 0));
    }
    return sorted;
  };

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

  const handleCategoryChange = (newCategory) => {
    setCategory(newCategory);
    // Automatically browse if category changed and query is empty
    if (!currentQuery.trim()) {
      fetchProducts("", sortMethod, newCategory);
    }
  };

  const handleSortChange = (newSort) => {
    setSortMethod(newSort);
    if (products) {
      setProducts(sortProducts(products, newSort));
    }
  };

  const handleSearch = (query) => {
    fetchProducts(query, sortMethod, category);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <span className="logo-icon">🤖</span>
          <h1 className="logo-text">AI<span>Recommend</span></h1>
        </div>
      </header>

      <main className="main-content">
        <section className="hero-section">
          <h2 className="hero-title">Discover Products with <span>True Intelligence</span></h2>
          <p className="hero-subtitle">Smart search understanding Brands, Categories, and natural language.</p>

          <div className="search-wrapper">
            <SearchBar
              onSearch={handleSearch}
              currentSort={sortMethod}
              onSortChange={handleSortChange}
              currentCategory={category}
              onCategoryChange={handleCategoryChange}
              categoriesList={categoriesList}
            />
          </div>
        </section>

        <section className="results-section">
          {products !== null || isLoading ? (
            <RecommendationList products={products} isLoading={isLoading} />
          ) : null}
        </section>
      </main>

      <footer className="app-footer">
        <p>Product Recommendation System - Powered by NLP & Entity Tagging</p>
      </footer>
    </div>
  );
}

export default App;
