# JusticeAI: Autonomous Judicial Reasoning Engine

JusticeAI is an enterprise-grade, agentic AI platform designed to analyze criminal sentencing for consistency, legal compliance, and bias. Unlike standard LLM wrappers, JusticeAI utilizes programmatic deterministic engines, live web scraping for legal statutes, and a rigid, multi-layered reasoning pipeline to eliminate AI hallucinations.

## 🚀 Core Features

### 1. The Reasoning Pipeline
Rather than relying on static training data, JusticeAI operates via an autonomous orchestrator:
- **DataPreFetcher:** Automatically scrapes DuckDuckGo for official statutes, sentencing commission reports, international precedent, behavioral psychology journals, and criminology bias studies based on the case facts.
- **PromptBuilder:** Injects the live, pre-fetched data directly into modular, layered markdown prompts, forcing the AI to ground its answers in real-world citations.
- **OutputValidator:** Strictly parses the AI's output, ensuring it adheres to a robust JSON schema.

### 2. Deterministic Calculation Engines
LLMs are notoriously bad at math and self-evaluation. JusticeAI offloads these tasks to Python modules:
- **SentencingCalculator:** Automatically computes the cumulative minimum, maximum, and typical concurrent/consecutive ranges for multi-count convictions based on jurisdiction-specific laws.
- **ConfidenceCalculator:** Algorithmically scores the AI's analysis out of 100 based on the presence and quality of its citations (e.g., deducting points if no official statute is cited or if fewer than 5 global jurisdictions are compared).

### 3. Layered Analysis
The AI evaluates every case across 5 strict dimensions:
1. **Legal Compliance:** Does the sentence fall within statutory bounds?
2. **Sentencing Consistency:** How does it compare to regional averages?
3. **Factor Analysis & Bias:** Are there documented racial or socioeconomic disparities at play?
4. **Cross-Jurisdictional Precedent:** How would this case be handled in the UK, Canada, Australia, Germany, or Sweden?
5. **Human Context:** What does behavioral psychology indicate about the defendant's specific profile (age, mental health)?

## 💻 Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic (SQLite)
- **AI/LLM:** Groq (Llama 3.3 70B Versatile)
- **Data Sourcing:** DuckDuckGo Search API
- **Frontend:** React, TypeScript, Vite, Recharts, TailwindCSS

## 🛠️ Setup & Installation

### Backend
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `.\venv\Scripts\Activate.ps1`
   - Unix: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `alembic upgrade head`
6. Create a `.env` file and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_key_here
   ```
7. Start the server: `uvicorn main:app --reload`

### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

## 📊 Testing
JusticeAI includes a robust suite of unit and integration tests.
```bash
# Run the test suite from the root directory
pytest
```

## ⚖️ License
Proprietary. All rights reserved.
