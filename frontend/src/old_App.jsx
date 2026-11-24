import React, { useState } from 'react';
import SearchBar from './components/SearchBar';
import RecommendationList from './components/RecommendationList';
import './App.css';

const MOCK_PRODUCTS = [
  {
    id: 1,
    title: "ASUS ROG Strix G16 (2023) Gaming Laptop, 16” 16:10 FHD 165Hz, GeForce RTX 4060",
    image: "https://m.media-amazon.com/images/I/711q9BvD42L._AC_SX679_.jpg",
    price: 1249.99,
    originalRating: 4.6,
    aiSentimentScore: 4.8,
    features: [
      { name: "165Hz Display", sentiment: 1 },
      { name: "RTX 4060", sentiment: 1 },
      { name: "Loud Fans", sentiment: -1 },
      { name: "Heavy", sentiment: 0 }
    ]
  },
  {
    id: 2,
    title: "Acer Nitro 5 AN515-58-525P Gaming Laptop | Intel Core i5-12500H | NVIDIA GeForce RTX 3050",
    image: "https://m.media-amazon.com/images/I/718t1gEq4hL._AC_SX679_.jpg",
    price: 799.99,
    originalRating: 4.4,
    aiSentimentScore: 3.9,
    features: [
      { name: "Value for Money", sentiment: 1 },
      { name: "Battery Life", sentiment: -1 },
      { name: "144Hz Screen", sentiment: 1 }
    ]
  },
  {
    id: 3,
    title: "Lenovo Legion Pro 5i 16\" LCD Gaming Laptop WQXGA 165Hz Intel Core i7-13700HX 16GB RAM 1TB SSD",
    image: "https://m.media-amazon.com/images/I/71qJIt6p1OL._AC_SX679_.jpg",
    price: 1479.00,
    originalRating: 4.7,
    aiSentimentScore: 4.9,
    features: [
      { name: "Build Quality", sentiment: 1 },
      { name: "Cooling System", sentiment: 1 },
      { name: "Keyboard", sentiment: 1 }
    ]
  }
];

function App() {
  const [products, setProducts] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");
  const [sortMethod, setSortMethod] = useState("rank_desc");

  const handleSearch = async (query, sort = sortMethod) => {
    setIsLoading(true);
    setProducts(null);
    setCurrentQuery(query);
    setSortMethod(sort);

    try {
      // Pass both query and sort method to FastAPI
      const url = `http://localhost:8000/api/recommendations?q=${encodeURIComponent(query)}&sort=${sort}`;
      const response = await fetch(url);
      const result = await response.json();

      if (result.status === "success") {
        setProducts(result.data);
      } else if (Array.isArray(result)) {
        setProducts(result);
      } else if (result.error) {
        console.error("Backend returned an error:", result.error);
        setProducts([]);
      } else {
        // Fallback for unexpected format
        setProducts([]);
      }
    } catch (error) {
      console.error("Failed to connect to backend API. Make sure FastAPI is running on port 8000.", error);
    } finally {
      setIsLoading(false);
    }
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
          <p className="hero-subtitle">We read thousands of Amazon reviews using advanced AI to find the real sentiment behind the ratings.</p>

          <div className="search-wrapper">
            <SearchBar
              onSearch={handleSearch}
              currentSort={sortMethod}
              onSortChange={(newSort) => handleSearch(currentQuery, newSort)}
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
        <p>Product Recommendation System - Powered by NLP & Hugging Face</p>
      </footer>
    </div>
  );
}

export default App;
