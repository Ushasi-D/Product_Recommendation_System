import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ onSearch, currentSort, onSortChange }) => {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query);
        }
    };

    return (
        <div className="search-controls-wrapper">
            <form className="search-bar-container" onSubmit={handleSubmit}>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search for products (e.g., 'samsung')"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />

                <select
                    className="sort-dropdown"
                    value={currentSort}
                    onChange={(e) => onSortChange(e.target.value)}
                    title="Sort Results"
                >
                    <option value="rank_desc">Highly Recommended</option>
                    <option value="rank_asc">Lowest Recommended</option>
                    <option value="price_low">Price: Low to High</option>
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
