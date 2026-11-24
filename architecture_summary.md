# Amazon Product Recommendation System - Architecture Overview

## A. Data Layer (Amazon Only)
- **Dataset**: `McAuley-Lab/Amazon-Reviews-2023` (Hugging Face).
- **Strategy**: 
  - Stream data to handle large volume efficiently.
  - Filter for reviews from **2022 onwards**.
  - **Feature Extraction**: Extract specifications (e.g., RAM, 5G) directly from Product Titles.

## B. NLP Engine (The Core Novelty)
- **Model**: Utilizes pre-trained Transformer models (BERT or RoBERTa) instead of simple lexical models (like VADER).
- **False Positive Detection**: 
  - Uses attention mechanisms to analyze sentence context.
  - Capable of detecting sarcasm (e.g., "Great, it broke in a day" -> Negative) which simple models often miss.

## C. Ranking Logic
- **Hybrid Score Formula**: 
  $$ \text{Hybrid Score} = (0.7 \times \text{AI\_Sentiment\_Score}) + (0.3 \times \text{Star\_Rating}) $$
- **Philosophy**: Prioritizes the AI-driven sentiment analysis of the text reviews over the simple star rating.

## D. User Interface
- **Frontend**: **React.js** for a modern, responsive search experience.
- **Backend**: **Flask API** to serve recommendations and handle communication with the NLP engine.
