"""
Run this script in Google Colab to process the Kaggle Amazon Cell Phones Reviews dataset.
Make sure to select Runtime -> Change runtime type -> Hardware accelerator -> T4 GPU.

Required installations:
!pip install transformers torch pandas scikit-learn tqdm
"""

import pandas as pd
import numpy as np
import torch
from transformers import pipeline
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
ITEMS_CSV_PATH = "20191226-items.csv" 
REVIEWS_CSV_PATH = "20191226-reviews.csv"
OUTPUT_JSON_PATH = "processed_products.json"

device = 0 if torch.cuda.is_available() else -1
print(f"Using device: {'GPU' if device == 0 else 'CPU'}")

# Use a RoBERTa model specifically fine-tuned on Amazon Reviews for 1-5 star prediction.
# RoBERTa offers superior context understanding and sarcasm detection compared to base BERT models.
print("Loading Hugging Face Sentiment Model (RoBERTa for Amazon Reviews)...")
sentiment_analyzer = pipeline(
    "sentiment-analysis", 
    model="LiYuan/amazon-review-sentiment-analysis", 
    device=device,
    truncation=True,
    max_length=512
)

# ==========================================
# 2. DATA LOADING & CLEANING
# ==========================================
print("Loading datasets...")
try:
    items_df = pd.read_csv(ITEMS_CSV_PATH)
    reviews_df = pd.read_csv(REVIEWS_CSV_PATH)
except FileNotFoundError:
    print("ERROR: Dataset files not found. Upload '20191226-items.csv' and '20191226-reviews.csv'.")
    exit()

# Crucial Fix: Strip whitespace from ASIN to ensure perfect merging later
items_df['asin'] = items_df['asin'].astype(str).str.strip()
reviews_df['asin'] = reviews_df['asin'].astype(str).str.strip()

# Drop rows with totally missing text
reviews_df = reviews_df.dropna(subset=['body'])

# Rename the rating column from items.csv so it's clear
items_df = items_df.rename(columns={'rating': 'product_star_rating'})

# ==========================================
# 3. SENTIMENT ANALYSIS VERIFICATION
# ==========================================
print("\n--- Verifying NLP Model Accuracy ---")
test_sample = reviews_df.dropna(subset=['rating']).sample(200, random_state=42).copy()

print(f"Running sentiment analysis on {len(test_sample)} labeled test reviews...")
test_texts = test_sample['body'].astype(str).tolist()
predictions = sentiment_analyzer(test_texts)

# The model outputs labels like '1 star', '2 stars', etc. Extract the integer.
test_sample['predicted_stars'] = [int(p['label'].split()[0]) for p in predictions]

# Since predicting exact stars (e.g. 3 vs 4) is hard, we classify accuracy by positive/negative polarity.
def to_polarity(rating):
    if rating >= 4: return 1     # Positive
    elif rating <= 2: return -1  # Negative
    else: return 0               # Neutral

test_sample['true_polarity'] = test_sample['rating'].apply(to_polarity)
test_sample['pred_polarity'] = test_sample['predicted_stars'].apply(to_polarity)

# Calculate Accuracy based on matching polarity
filtered_for_acc = test_sample[test_sample['true_polarity'] != 0]
accuracy = accuracy_score(filtered_for_acc['true_polarity'], filtered_for_acc['pred_polarity'])
print(f"Model Polarity Accuracy (Pos vs Neg): {accuracy * 100:.2f}%\n")

print("Sample Predictions (Note how it handles nuance/sarcasm):")
for _, row in test_sample.head(5).iterrows():
    text = str(row['body'])[:100] + "..." if len(str(row['body'])) > 100 else str(row['body'])
    print(f"Actual User Rating: {row['rating']} | AI Predicted: {row['predicted_stars']}")
    print(f"Text: {text}\n")


# ==========================================
# 4. RUNNING NLP ON ALL DATA
# ==========================================
print("\n--- Processing Entire Dataset ---")
# To avoid Colab crashing, sample up to 30 reviews per product to get a solid average
sampled_reviews = reviews_df.groupby('asin').apply(lambda x: x.sample(min(len(x), 30))).reset_index(drop=True)

print(f"Running sentiment analysis on {len(sampled_reviews)} reviews... This will take a few minutes.")
all_texts = sampled_reviews['body'].astype(str).tolist()

results = []
batch_size = 128
for i in tqdm(range(0, len(all_texts), batch_size)):
    batch = all_texts[i:i+batch_size]
    preds = sentiment_analyzer(batch)
    results.extend(preds)

# The sentiment score is directly the 1-5 predicted stars
sampled_reviews['calculated_sentiment_score'] = [int(r['label'].split()[0]) for r in results]

# Aggregate sentiment scores back to the item level
review_aggregates = sampled_reviews.groupby('asin').agg({
    'calculated_sentiment_score': 'mean',
    'body': 'count'
}).rename(columns={'body': 'review_count'}).reset_index()


# ==========================================
# 5. MERGING & FEATURE SCORE CALCULATION
# ==========================================
print("\n--- Merging Data & Calculating Feature Scores ---")
# Merge text review insights onto the items catalog
final_df = pd.merge(items_df, review_aggregates, on='asin', how='left')

# Calculate Feature Score using TF-IDF similarity on Title + Brand
final_df['title'] = final_df['title'].fillna('')
final_df['brand'] = final_df['brand'].fillna('')
final_df['feature_text'] = final_df['brand'] + " " + final_df['title']

tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
tfidf_matrix = tfidf.fit_transform(final_df['feature_text'])

doc_lengths = tfidf_matrix.sum(axis=1)
min_len, max_len = doc_lengths.min(), doc_lengths.max()
if max_len > min_len:
    final_df['feature_score'] = 1 + 4 * ((doc_lengths - min_len) / (max_len - min_len))
else:
    final_df['feature_score'] = 3.0

final_df['feature_score'] = np.asarray(final_df['feature_score']).flatten()


# ==========================================
# 6. HYBRID SCORE CALCULATION
# ==========================================
print("Calculating Hybrid Scores based on your custom ranking formula...")

def calculate_initial_rank(row):
    feat_score = row['feature_score']
    
    # Text NLP sentiment score average
    sentiment = row['calculated_sentiment_score'] 
    
    # Official catalog star rating from items.csv
    static_stars = row['product_star_rating'] 
    
    has_sentiment = pd.notna(sentiment)
    has_static_stars = pd.notna(static_stars)
    
    if has_sentiment and has_static_stars:
        # Full formula
        return (0.6 * sentiment) + (0.2 * static_stars) + (0.2 * feat_score)
    elif has_sentiment and not has_static_stars:
        # Missing catalog stars, but has texts
        return (0.7 * sentiment) + (0.3 * feat_score)
    elif not has_sentiment and has_static_stars:
        # Missing texts, but has catalog stars
        return (0.7 * static_stars) + (0.3 * feat_score)
    else:
        # Missing both, purely text richness / features
        return feat_score

final_df['initial_rank'] = final_df.apply(calculate_initial_rank, axis=1)

# Clean up final output fields and round to two decimals
final_df['calculated_sentiment_score'] = final_df['calculated_sentiment_score'].fillna(0.0).round(2)
final_df['product_star_rating'] = final_df['product_star_rating'].fillna(0.0).round(2)
final_df['review_count'] = final_df['review_count'].fillna(0).astype(int)
final_df['feature_score'] = final_df['feature_score'].round(2)
final_df['initial_rank'] = final_df['initial_rank'].round(2)

export_df = final_df[['asin', 'title', 'brand', 'image', 'price', 
                      'product_star_rating', 'review_count', 'calculated_sentiment_score', 
                      'feature_score', 'initial_rank']]

export_df = export_df.rename(columns={'asin': 'id', 'product_star_rating': 'rating'})
export_df = export_df.sort_values(by='initial_rank', ascending=False)

# ==========================================
# 7. EXPORT DATA
# ==========================================
print(f"Exporting exactly {len(export_df)} items to JSON...")
export_df.to_json(OUTPUT_JSON_PATH, orient='records', indent=4)
print("Pipeline Complete! Download `processed_products.json`.")
