import React, { useState } from 'react';
import Badge from './Badge';
import ProductModal from './ProductModal';
import './ProductCard.css';

const ProductCard = ({ product }) => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Safely map the new NLP JSON keys with fallbacks
    const title = product.title || "Unknown Product";
    const image = product.image || "https://placehold.co/600x400/eeeeee/333333.png?text=No+Image";
    const price = product.price || 0;

    // Map processed JSON fields to the original logic
    const originalRating = product.rating || 0;
    const aiSentimentScore = product.calculated_sentiment_score || 0;
    const finalHybridScore = product.initial_rank || 0;

    // Safety check for reviews
    const hasReviews = product.review_count > 0;

    // Features array might not be implemented yet in phase 2, so default to empty
    const features = product.features || [];

    return (
        <div className="product-card">
            <div className="product-image-container">
                <img
                    src={image}
                    alt={title}
                    className="product-image"
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = "https://placehold.co/600x400/eeeeee/333333.png?text=Image+Not+Found";
                    }}
                />
                {!hasReviews ? (
                    <div className="hybrid-badge" style={{ background: 'rgba(100, 116, 139, 0.9)' }}>
                        NEW - Specs Only
                    </div>
                ) : (
                    <div className="hybrid-badge">
                        ⭐ {Number(finalHybridScore).toFixed(1)} AI Rank
                    </div>
                )}
            </div>

            <div className="product-content">
                <h3 className="product-title" title={title}>{title.length > 60 ? title.substring(0, 60) + '...' : title}</h3>
                <p className="product-price">
                    {Number(price) === 0 ? "Price Not Found" : `₹${Number(price).toLocaleString('en-IN')}`}
                </p>

                <div className="metrics-container">
                    <div className="metric">
                        <span className="metric-label">Amazon Rating</span>
                        <div className="metric-value">
                            <span className="stars">{'★'.repeat(Math.round(originalRating)) + '☆'.repeat(5 - Math.round(originalRating))}</span>
                            <span className="rating-number">{Number(originalRating).toFixed(1)}</span>
                        </div>
                    </div>

                    <div className="metric ai-metric">
                        <span className="metric-label">AI Sentiment</span>
                        <div className="metric-value">
                            {!hasReviews ? (
                                <span className="rating-number" style={{ fontSize: '0.9rem', color: '#64748b' }}>No text reviews</span>
                            ) : (
                                <>
                                    <div className="progress-bar">
                                        <div
                                            className="progress-fill"
                                            style={{ width: `${(aiSentimentScore / 5) * 100}%`, backgroundColor: aiSentimentScore > 4 ? '#10b981' : aiSentimentScore > 3 ? '#fbbf24' : '#ef4444' }}
                                        ></div>
                                    </div>
                                    <span className="rating-number">{Number(aiSentimentScore).toFixed(1)}/5</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                {features.length > 0 && (
                    <div className="features-container">
                        <h4 className="features-title">Extracted Features</h4>
                        <div className="badges-wrapper">
                            {features.map((feature, idx) => (
                                <Badge key={idx} variant={feature.sentiment > 0 ? 'positive' : feature.sentiment < 0 ? 'negative' : 'neutral'}>
                                    {feature.name}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}

                <button className="view-details-btn" onClick={() => setIsModalOpen(true)}>
                    View Details
                </button>
            </div>

            {isModalOpen && (
                <ProductModal product={product} onClose={() => setIsModalOpen(false)} />
            )}
        </div>
    );
};

export default ProductCard;
