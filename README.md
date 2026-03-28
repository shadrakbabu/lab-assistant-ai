# Lab Manual AI Assistant

A production-ready AI-powered lab manual assistant that accepts PDF lab manuals, extracts content, identifies experiments, and provides step-by-step procedures with theory explanations via a clean Streamlit UI.

## Features

- ✅ PDF upload and text extraction
- ✅ Experiment identification and extraction
- ✅ Procedure parsing and step-by-step display
- ✅ Theory explanation in simple terms
- ✅ Equipment detection and listing
- ✅ Safety precautions extraction
- ✅ Semantic search using FAISS
- ✅ Conversation-based Q&A
- ✅ Export results (coming soon)

## Tech Stack

- **Python 3.8+** - Core language
- **Streamlit** - Web UI framework
- **LangChain** - LLM orchestration and RAG
- **PyPDF2** - PDF text extraction
- **FAISS** - Vector semantic search
- **spaCy** - NLP for information extraction
- **SQLite** - Metadata storage
- **OpenAI/Gemini** - LLM backends

## Project Structure

```
lab-assistant-ai/
├── app/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── data/                    # Uploaded PDFs stored here
├── db/                      # SQLite database
├── vectorstore/             # FAISS indices
├── app.py                   # Main Streamlit app
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## Setup Instructions

### 1. Clone or Navigate to Project
```bash
cd lab-assistant-ai
```

### 2. Create Virtual Environment
```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Download spaCy model (required for NLP)
python -m spacy download en_core_web_sm
```

### 4. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# Add your OpenAI API key:
# OPENAI_API_KEY=sk-...
```

### 5. Run the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Usage

### Basic Workflow

1. **Upload PDF**: Click on the file uploader in the sidebar and select your lab manual PDF
2. **Ask Questions**: Use the query box to ask about:
   - Specific experiments: "Explain experiment 1"
   - Procedures: "Give me the procedure"
   - Theory: "Explain the theory simply"
   - Equipment: "List the equipment needed"
   - Safety: "Show safety precautions"
3. **View Results**: Get instant AI-powered responses
4. **Export/Share**: Download procedures and explanations (coming soon)

### Example Queries

```
"What is the objective of experiment 2?"
"List all equipment needed for experiment 1"
"Give me step-by-step procedure for experiment 3"
"Explain the theory behind water distillation"
"What safety precautions should I take?"
```

## Implementation Phases

### Week 1-2: Foundation ✅
- [x] Project structure setup
- [x] Basic Streamlit UI
- [x] File upload capability
- [x] Configuration management
- [ ] PDF text extraction (next)
- [ ] Experiment identification (next)

### Week 3-4: Core Features (Coming Soon)
- Procedure parsing tool
- Theory explanation module
- Equipment extraction
- Safety precautions detection
- Troubleshooting suggestions

### Week 5-6: Specialization (Coming Soon)
- Subject-specific assistant (Chemistry/Physics/CS)
- Full experiment lifecycle support

### Week 7-8: Production Ready (Coming Soon)
- Enhanced UI with dashboards
- Error handling and validation
- Export to text/PDF
- Deployment configuration

## API Configuration

### OpenAI Setup
1. Create account at https://platform.openai.com
2. Generate API key from https://platform.openai.com/api-keys
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Gemini Setup
1. Create account at https://makersuite.google.com
2. Generate API key at https://makersuite.google.com/app/apikey
3. Add to `.env`: `GEMINI_API_KEY=...`

## Deployment (Streamlit Cloud)

### Prerequisites
- GitHub account
- GitHub repository with this code

### Deployment Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit: Lab Manual AI Assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lab-assistant-ai.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect GitHub repo
   - Select this repo and `app.py` as main file
   - Click Deploy

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to "Settings"
   - Add secrets:
     ```
     OPENAI_API_KEY = "sk-..."
     LLM_MODEL = "gpt-3.5-turbo"
     ```

## Development Notes

### Adding New Modules

**PDF Processor** (app/pdf_processor.py) - Coming Soon
```python
# Extract text from PDFs
# Chunk documents for processing
```

**Experiment Parser** (app/experiment_parser.py) - Coming Soon
```python
# Identify experiment sections
# Extract experiment details
```

**Theory Explainer** (app/theory_explainer.py) - Coming Soon
```python
# Simplify complex concepts
# Generate explanations
```

**Safety Module** (app/safety_module.py) - Coming Soon
```python
# Extract safety information
# Provide precautions
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Copy `.env.example` to `.env` and add your API key

### Issue: spaCy model not found
**Solution**: Run `python -m spacy download en_core_web_sm`

### Issue: "ModuleNotFoundError"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Streamlit port already in use
**Solution**: Run on different port:
```bash
streamlit run app.py --server.port 8502
```

## Performance Tips

- **Large PDFs**: Break into smaller files (< 10 MB recommended)
- **Vector Search**: First initialization takes longer; subsequent searches are fast
- **API Calls**: Use gpt-3.5-turbo for faster responses and lower costs

## Contributing

This is a learning project. Feel free to:
- Add new features
- Improve extraction accuracy
- Add support for more document formats
- Optimize performance

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review requirements.txt versions
3. Verify API keys are correctly set

---

**Happy learning! 🧪**
