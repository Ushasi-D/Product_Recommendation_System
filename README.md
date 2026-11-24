# AI-Powered Product Recommendation System

## 1. Short Description
The **AI-Powered Product Recommendation System** is an intelligent e-commerce search engine that ranks products based on verified user sentiment and product specification richness. It ingests large-scale Amazon datasets (McAuley Lab) using deep learning (RoBERTa Sentiment Analysis) combined with TF-IDF Vectorization. The result is a robust "hybrid rank" that pushes the best-reviewed, most relevant products to the top. This intelligence is served via a lightning-fast Python API and consumed by a modern, interactive React web application.

## 2. Used Tech Stack
- **Frontend**: React.js, Vite, Vanilla CSS
- **Backend API**: FastAPI, Python, Pandas, Uvicorn
- **Data Engineering & AI Pipeline**: Google Colab, Hugging Face `transformers` (RoBERTa model by LiYuan), Scikit-learn (TF-IDF Vectorization)
- **Dataset**: Amazon 2023 Reviews Dataset (JSONL & Parquet)

## 3. How to Run

### Clone the Repository
Start by opening a terminal and navigating to the project folder.

### Run the Backend (FastAPI server)
1. Open a new terminal instance and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Activate your Virtual Environment (optional but recommended):
   ```bash
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
3. Install the backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: ensure you have `fastapi`, `uvicorn`, and `pandas` installed at minimum).*
4. Start the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend API will start running perfectly at `http://localhost:8000`.

### Run the Frontend (React site)
1. Open a **second** terminal instance and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the frontend dependencies via npm:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open the Local URL provided in your terminal (usually `http://localhost:5173/`) in your browser to interact with the Product Recommendation System!
