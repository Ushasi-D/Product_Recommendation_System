import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, currentSort, onSortChange, currentCategory, onCategoryChange, categoriesList = [] }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    return (
        <div className="search-controls-wrapper">
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

                <select
                    className="sort-dropdown"
                    value={currentSort}
                    onChange={(e) => onSortChange(e.target.value)}
                    title="Sort Results"
                >
                    <option value="" disabled>📊 Sort By</option>
                    <option value="relevance">⭐ Best Match (Relevance)</option>
                    <option value="price_low">💰 Price: Low to High</option>
                    <option value="price_high">Price: High to Low</option>
                </select>

                <button type="submit" className="search-button">
                    Search
                </button>
            </form>
        </div>
    );
};

export default SearchBar;
