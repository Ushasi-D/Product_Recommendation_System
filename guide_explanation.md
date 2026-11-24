# Project Explanation: Amazon Product Recommendation System

## Overview (The "Elevator Pitch")
This project is a smart shopping assistant. Unlike standard websites that just look at star ratings (which can be fake or misleading), our system reads the actual reviews using Artificial Intelligence. It understands *context*—so if someone says "Great... it broke in a day", our AI knows that's actually negative, even if the user gave it 5 stars.

## How It Works (The 4 Main Parts)

### 1. The User View (Front-End)
*   **What it is:** The website the user sees.
*   **What it does:** It looks like a normal slick shopping site. The user types "Gaming Laptop" into the search box.
*   **The Difference:** It feels fast and modern (built with React.js), designed to look professional.

### 2. The Controller (Back-End System)
*   **What it is:** The traffic cop of the system.
*   **What it does:** When the user searches, this system takes the request and coordinates everything. It collects potential products and asks the "Brain" (AI) to rank them.
*   **The Logic:** It calculates a **"Hybrid Score"**:
    *   30% of the score comes from the Star Rating.
    *   70% of the score comes from our AI's opinion of the reviews.
    *   *Why?* Because text reviews tell the real truth more than stars do.

### 3. The Intelligence / "The Brain" (AI Layer)
*   **What it is:** The core innovation. It uses a model called **RoBERTa** (a smarter version of BERT).
*   **What it does:** It doesn't just look for "good" or "bad" words. It reads whole sentences to understand emotion.
*   **Example:**
    *   *Old Way:* sees the word "Great" -> thinks it's Positive.
    *   *Our Way:* reads "Great, it broke" -> understands Sarcasm -> marks it Negative.
*   It also automatically pulls out specs like "16GB RAM" from the titles so users can filter easily.

### 4. The Data (Storage)
*   **What it is:** A massive collection of Amazon Reviews (from 2023).
*   **What it does:** To keep things fast and relevant, we filter out anything older than 2022. We stream this data so the system doesn't crash trying to load millions of reviews at once.

---
## Summary for the Guide
"Sir/Ma'am, we are building a recommendation engine that fixes the problem of misleading star ratings. We use a Transformer-based AI to 'read' the reviews like a human would, catching sarcasm and nuance, and then we combine that with the star rating to give the user a truly honest product recommendation."
