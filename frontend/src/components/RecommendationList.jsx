import React from 'react';
import ProductCard from './ProductCard';
import './RecommendationList.css';

const RecommendationList = ({ products, isLoading }) => {
    if (isLoading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p className="loading-text">AI is reading thousands of reviews...</p>
            </div>
        );
    }

    if (!products || products.length === 0) {
        return (
            <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <h3 className="empty-title">Ready to find the perfect product?</h3>
                <p className="empty-desc">Enter a search term above and our AI will analyze reviews to find the best options for you.</p>
            </div>
        );
    }

    return (
        <div className="recommendations-container">
            <div className="recommendations-header">
                <h2 className="recommendations-title">Top Recommendations</h2>
                <p className="recommendations-subtitle">Ranked by our Hybrid AI Sentiment Engine</p>
            </div>

            <div className="recommendations-grid">
                {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                ))}
            </div>
        </div>
    );
};

export default RecommendationList;
