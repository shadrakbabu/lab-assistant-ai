# Installation Fix - FAISS Version Compatibility

## Problem
```
ERROR: Could not find a version that satisfies the requirement faiss-cpu==1.7.4
```

## Solution
Updated `requirements.txt` with compatible versions:

### What Changed
- ❌ `faiss-cpu==1.7.4` → ✅ `faiss-cpu==1.13.2` (latest stable)
- ✅ Added `sentence-transformers==2.2.2` (for embeddings)
- ✅ Added `numpy<1.24` (compatibility constraint)

## Updated Requirements

```txt
streamlit==1.28.1
langchain==0.1.7
langchain-community==0.0.10
langchain-openai==0.0.5
PyPDF2==3.0.1
faiss-cpu==1.13.2          # UPDATED: Latest stable version
spacy==3.7.2
python-dotenv==1.0.0
pydantic==2.5.0
sentence-transformers==2.2.2  # NEW: For embeddings
numpy<1.24                    # NEW: Compatibility constraint
```

## Installation Steps

### 1. Clean Previous Installation (if needed)
```bash
# Deactivate venv if it exists
deactivate 2>/dev/null || true

# Remove old venv (optional)
rm -rf venv
```

### 2. Create Fresh Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip
```bash
pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 6. Verify Installation
```bash
python -c "import faiss; import streamlit; import langchain; print('✅ All imports successful')"
```

## If Installation Still Fails

### For FAISS Issues:
```bash
# Try installing FAISS separately
pip install faiss-cpu==1.13.2 --no-cache-dir

# If that fails, try the latest:
pip install faiss-cpu --upgrade
```

### For Numpy Issues:
```bash
# Install compatible numpy
pip install numpy==1.23.5
```

### For Other Issues:
```bash
# Clear pip cache and reinstall
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

## Alternative: Use GPU Version (if NVIDIA GPU available)

Replace `faiss-cpu` with `faiss-gpu`:

```bash
# Uninstall CPU version
pip uninstall faiss-cpu -y

# Install GPU version
pip install faiss-gpu==1.13.2
```

## Verify Installation Works

After installation, test with:

```bash
python -c "
import faiss
import streamlit
import langchain
import PyPDF2
import spacy
import sentence_transformers
print('✅ All packages installed successfully!')
"
```

## Run the Application

```bash
streamlit run app.py
```

The app will be available at: **http://localhost:8501**

---

## Version Details

| Package | Version | Reason |
|---------|---------|--------|
| streamlit | 1.28.1 | Latest stable |
| langchain | 0.1.7 | Compatible with components |
| PyPDF2 | 3.0.1 | Latest stable |
| faiss-cpu | 1.13.2 | Latest (1.7.4 deprecated) |
| spacy | 3.7.2 | Latest stable |
| sentence-transformers | 2.2.2 | For embeddings |
| numpy | <1.24 | Compatibility |

---

## Troubleshooting

### Error: "No module named 'faiss'"
```bash
# Reinstall FAISS
pip install --force-reinstall faiss-cpu==1.13.2
```

### Error: "numpy version conflict"
```bash
# Install compatible numpy
pip install numpy==1.23.5
```

### Error: "Python < 3.8 not supported"
```bash
# Check Python version
python3 --version

# Must be Python 3.8 or higher
# If needed, install Python 3.9 or 3.10
```

### ImportError after installation
```bash
# Deactivate and reactivate venv
deactivate
source venv/bin/activate

# Try import again
python -c "import faiss"
```

---

## Success Indicator

After successful installation, you should see:
```
✅ All packages installed successfully!
```

And running Streamlit should show:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

