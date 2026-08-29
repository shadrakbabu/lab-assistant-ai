# 🧪 Lab Manual Conversational AI Assistant

A production-ready, full-stack AI web application where students and researchers can upload laboratory manual PDFs, automatically detect experiments, explore step-by-step procedures, understand scientific theory, inspect equipment/safety instructions, and engage in grounded RAG-powered conversation without hallucinations.

---
Website (Project) Link : https://lab-assistant-ai.streamlit.app/
## ✨ Features

1. **PDF Lab Manual Extraction**: Upload laboratory manuals (up to 50MB) and extract text, page maps, and text statistics using `pypdf`. Handles scanned documents gracefully.
2. **Automated Experiment Parsing**: Detects experiment boundaries (`EXPERIMENT 1`, `EXP. 2`) and structures sections: Aim, Theory, Equipment/Apparatus, Procedure, Observations, Result, Precautions/Safety, and Troubleshooting.
3. **Automated Subject Classification**: Categorizes manuals into **Physics**, **Chemistry**, **Biology**, **Computer Science**, or **General Science**.
4. **Interactive Procedure Checklist**: Step-by-step numbered procedures with completion checkboxes, step progress bar, and safety warnings.
5. **Theory & Simple Explanation Mode**: Full academic theory viewer + a student-friendly "Simple Explanation" mode toggle.
6. **Equipment & Safety Assistant**: Itemized apparatus cards with purpose guidance and prominent hazard alerts.
7. **Grounded RAG Conversational AI**: LangChain & FAISS RAG chat interface. Answers are strictly grounded in uploaded manual content with collapsible source citations. Explicitly states when information is not in the manual.
8. **Modern Educational UI**: Responsive React + Vite + Tailwind CSS dashboard.

---

## 🏗️ Repository Architecture

```
lab-assistant-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI Entry Point & CORS setup
│   │   ├── config.py                # App configuration & settings manager
│   │   ├── database.py              # SQLite connection & ORM Session Local
│   │   ├── models/
│   │   │   ├── manual.py            # Manual & Experiment database models
│   │   │   └── chat.py              # Chat Request & Response schemas
│   │   ├── parsers/
│   │   │   ├── pdf_extractor.py     # PDF text extraction & quality validator
│   │   │   ├── experiment_parser.py # Regex section boundary detector
│   │   │   └── subject_classifier.py# Automated subject classifier
│   │   ├── rag/
│   │   │   ├── text_splitter.py     # Overlapping text chunker with metadata mapping
│   │   │   ├── vector_store.py      # FAISS Index + SentenceTransformer embeddings
│   │   │   └── qa_engine.py         # Grounded RAG Chat Engine (No hallucinations)
│   │   └── routes/
│   │       ├── manuals.py           # Upload PDF, list manuals, and manual details
│   │       ├── experiments.py       # List & fetch experiment details
│   │       └── chat.py              # Grounded Q&A Chat endpoint
│   └── tests/
│       └── test_api.py              # Automated backend pipeline test script
├── frontend/                        # React + Vite + Tailwind CSS Frontend
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.jsx                  # Main Dashboard Workspace
│   │   ├── components/              # React UI Components
│   │   └── services/
│   │       └── api.js               # Axios API client for FastAPI backend
├── requirements.txt                 # Backend Python Dependencies
├── .env.example                     # Environment Configuration Template
├── docker-compose.yml               # Multi-container Docker configuration
└── README.md                        # Project Documentation
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.9+
- Node.js 18+ & npm

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Run FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger API Docs: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
- Web Application: `http://localhost:3000`

---

## 🧪 Running Automated Tests

Run the full end-to-end backend pipeline test (PDF extraction, section parsing, SQLite DB storage, FAISS vector indexing, and Grounded Q&A citations):

```bash
python backend/tests/test_api.py
```

Test production frontend build:
```bash
cd frontend
npm run build
```

---

## 🐳 Docker Deployment

To run both backend and frontend using Docker Compose:

```bash
docker-compose up --build
```

---

## 📡 API Endpoints Summary

- `POST /api/manuals/upload`: Upload PDF manual, parse experiments, store in SQLite, index in FAISS vector store.
- `GET /api/manuals`: List all processed manuals.
- `GET /api/manuals/{manual_id}`: Get manual metadata & detected experiments.
- `GET /api/experiments/manual/{manual_id}`: List experiments for a manual.
- `GET /api/experiments/{experiment_id}`: Get experiment breakdown (Procedure, Theory, Equipment, Safety, Troubleshooting).
- `POST /api/chat`: Send grounded Q&A chat prompt. Returns answer + source citation excerpts.
- `GET /health`: System health & vector store status.
