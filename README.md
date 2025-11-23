# Project Prahlada - Social Media Analytics Dashboard

A comprehensive analytics platform for monitoring and analyzing social media trends, specifically tailored for Chhattisgarh region. The system features a robust Cognitive Reasoning Engine for automated data correction and a premium glassmorphic UI.

## 🚀 Features

*   **Cognitive Reasoning Engine:** Automated parsing and correction of tweet data using local LLMs (Phi-3.5, Gemma-2).
*   **Geospatial Analytics:** Interactive Mapbox integration for visualizing tweet locations.
*   **Hierarchy Mindmap:** D3.js-based visualization of administrative hierarchies (District -> Block -> Village).
*   **Glassmorphic UI:** Modern, responsive interface with advanced animations.
*   **Role-Based Access:** Secure admin dashboard with JWT authentication.

## 🛠️ Tech Stack

*   **Frontend:** React, TypeScript, Vite, Tailwind CSS, Framer Motion
*   **Backend:** FastAPI, Python, SQLite/PostgreSQL
*   **AI/ML:** Ollama (Phi-3.5, Gemma-2), LangChain
*   **Visualization:** Mapbox GL, D3.js, Recharts

## 🏃‍♂️ Running Locally

1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd Project-Prahlada
    ```

2.  **Backend Setup:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn backend.main:app --reload
    ```

3.  **Frontend Setup:**
    ```bash
    npm install
    npm run dev
    ```

4.  **Cognitive Engine:**
    Ensure Ollama is running with `phi3.5` and `gemma2:2b` models pulled.

## 🧪 Testing

*   **E2E Tests:** `python tests/e2e/test_cognitive_flow.py`
*   **Scenario Tests:** `python tests/e2e/test_scenarios.py`
*   **Frontend Tests:** `npm test`

## 🔒 Security

*   JWT Authentication for API endpoints.
*   Secure environment variable management.
*   Input sanitization and validation.

## 📄 License

Proprietary - Project Prahlada Team
