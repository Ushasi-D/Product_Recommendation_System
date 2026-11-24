import React from 'react';
import { createPortal } from 'react-dom';
import './ProductModal.css';
import Badge from './Badge';

const ProductModal = ({ product, onClose }) => {
    if (!product) return null;

    const title = product.title || "Unknown Product";
    const image = product.image || "https://placehold.co/600x400/eeeeee/333333.png?text=No+Image";
    const price = product.price || 0;
    const originalRating = product.rating || 0;
    const aiSentimentScore = product.calculated_sentiment_score || 0;
    const finalHybridScore = product.initial_rank || 0;
    const reviewCount = product.review_count || 0;
    
    const brand = product.brand || "N/A";
    const category = product.category || "N/A";
    const features = product.features || [];

    // Stop propagation so clicking inside the modal doesn't close it
    const handleModalClick = (e) => {
        e.stopPropagation();
    };

    return createPortal(
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={handleModalClick}>
                <button className="modal-close-btn" onClick={onClose}>&times;</button>
                
                <div className="modal-body">
                    <div className="modal-image-col">
                        <img
                            src={image}
                            alt={title}
                            className="modal-image"
                            onError={(e) => {
                                e.target.onerror = null;
                                e.target.src = "https://placehold.co/600x400/eeeeee/333333.png?text=Image+Not+Found";
                            }}
                        />
                        <div className="modal-price">
                            {Number(price) === 0 ? "Price Not Found" : `₹${Number(price).toLocaleString('en-IN')}`}
                        </div>
                    </div>
                    
                    <div className="modal-info-col">
                        <h2 className="modal-title">{title}</h2>
                        
                        <div className="modal-tags">
                            <span className="modal-tag"><strong>Brand:</strong> {brand}</span>
                            <span className="modal-tag"><strong>Category:</strong> {category}</span>
                        </div>

                        <div className="modal-metrics">
                            <div className="modal-metric-box">
                                <div className="modal-metric-title">AI Rank</div>
                                <div className="modal-metric-value hybrid">⭐ {Number(finalHybridScore).toFixed(1)}</div>
                            </div>
                            <div className="modal-metric-box">
                                <div className="modal-metric-title">Amazon Rating</div>
                                <div className="modal-metric-value">★ {Number(originalRating).toFixed(1)} <span className="reviews-count">({reviewCount} reviews)</span></div>
                            </div>
                            <div className="modal-metric-box">
                                <div className="modal-metric-title">AI Sentiment</div>
                                <div className="modal-metric-value sentiment">{Number(aiSentimentScore).toFixed(1)}/5</div>
                            </div>
                        </div>

                        {features.length > 0 && (
                            <div className="modal-features">
                                <h3 className="modal-features-title">Detailed Feature Sentiment</h3>
                                <div className="modal-badges-wrapper">
                                    {features.map((feature, idx) => (
                                        <Badge key={idx} variant={feature.sentiment > 0 ? 'positive' : feature.sentiment < 0 ? 'negative' : 'neutral'}>
                                            {feature.name}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        <div className="modal-raw-data">
                            <h3 className="modal-features-title">Raw Data (JSON)</h3>
                            <pre className="json-display">
                                {JSON.stringify(product, null, 2)}
                            </pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
};

export default ProductModal;
