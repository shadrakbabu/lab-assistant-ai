import os
import re
import uuid
from pathlib import Path
import streamlit as st

# Import production-ready backend modules
from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.models.manual import LabManualDB, ExperimentDB
from backend.app.parsers.pdf_extractor import PDFExtractor
from backend.app.parsers.experiment_parser import ExperimentParser
from backend.app.parsers.subject_classifier import SubjectClassifier
from backend.app.rag.text_splitter import TextSplitter
from backend.app.rag.vector_store import vector_store
from backend.app.rag.qa_engine import qa_engine

# Initialize database tables
init_db()

# Initialize Streamlit Page Config (Exact original settings)
st.set_page_config(
    page_title="Lab Manual AI Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session States
if "processor" not in st.session_state:
    st.session_state.processor = PDFExtractor(max_file_size_mb=settings.MAX_FILE_SIZE_MB)

if "parser" not in st.session_state:
    st.session_state.parser = ExperimentParser()

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

if "experiments" not in st.session_state:
    st.session_state.experiments = {}

if "active_manual_id" not in st.session_state:
    st.session_state.active_manual_id = None

# Custom CSS (Exact original styles)
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

.header {
    text-align: center;
    padding: 25px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}

.feature-box {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #374151;
    margin-top: 20px;
}

.feature-title {
    color: #60a5fa;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    border-radius: 10px;
    height: 45px;
    font-size: 16px;
    font-weight: bold;
}

.stButton > button:hover {
    opacity: 0.9;
}

.info-box {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 10px;
    border-left: 5px solid #3b82f6;
    margin-top: 10px;
}

.success-box {
    background-color: #052e16;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #22c55e;
}

.warning-box {
    background-color: #3f2f0b;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #facc15;
}

.citation-box {
    background-color: #0f172a;
    padding: 12px;
    border-radius: 8px;
    border-left: 4px solid #60a5fa;
    margin-top: 8px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# Exact Header UI
st.markdown("""
<div class='header'>
    <h1>🧪 Lab Manual AI Assistant</h1>
    <p>
        Upload your lab manual PDF and instantly extract experiments,
        procedures, equipment, theory, and safety precautions.
    </p>
</div>
""", unsafe_allow_html=True)

# Exact Sidebar UI
with st.sidebar:
    st.markdown("## 📘 About")
    st.markdown("""
<div class='feature-box'>
<div class='feature-title'>
✨ Features
</div>
✅ PDF text extraction  
✅ Experiment detection  
✅ Step-by-Step procedures  
✅ Equipment identification  
✅ Safety precautions  
✅ Grounded RAG Chat  
✅ Statistics & metadata  
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.success("✅ Student Mode Enabled")

    if st.session_state.extracted_data:
        st.markdown("---")
        st.markdown(f"**Subject**: `{st.session_state.extracted_data.get('subject', 'General Science')}`")
        st.markdown(f"**Manual ID**: `{st.session_state.active_manual_id}`")

# 2-Column Top Section
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📁 Upload Lab Manual")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload your lab manual PDF"
    )

    if uploaded_file is not None:
        data_dir = settings.DATA_DIR
        data_dir.mkdir(exist_ok=True, parents=True)

        manual_id = f"man_{uuid.uuid4().hex[:10]}"
        file_path = data_dir / f"{manual_id}_{uploaded_file.name}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("🔍 Extracting experiments, classifying subject, and indexing vector store..."):
            extractor = st.session_state.processor
            extracted_res = extractor.extract_pdf_data(str(file_path))

            if extracted_res["success"]:
                full_text = extracted_res["extracted_text"]
                num_pages = extracted_res["num_pages"]
                file_size_kb = extracted_res["file_size_kb"]

                # Subject classification & Experiment parsing
                subject = SubjectClassifier.classify(full_text)
                parser = st.session_state.parser
                parsed_exps = parser.parse_experiments(full_text)

                # Store in SQLite database
                db = SessionLocal()
                manual_db = LabManualDB(
                    id=manual_id,
                    filename=uploaded_file.name,
                    file_path=str(file_path),
                    file_size_kb=file_size_kb,
                    page_count=num_pages,
                    subject=subject,
                    extracted_text=full_text,
                    num_experiments=len(parsed_exps)
                )
                db.add(manual_db)

                exp_dict = {}
                for exp_data in parsed_exps:
                    exp_num = exp_data["experiment_number"]
                    exp_id = f"{manual_id}_exp_{exp_num}"
                    exp_db = ExperimentDB(
                        id=exp_id,
                        manual_id=manual_id,
                        experiment_number=exp_num,
                        title=exp_data["title"],
                        aim=exp_data["aim"],
                        theory=exp_data["theory"],
                        equipment=exp_data["equipment"],
                        procedure=exp_data["procedure"],
                        observations=exp_data["observations"],
                        result=exp_data["result"],
                        safety=exp_data["safety"],
                        troubleshooting=exp_data["troubleshooting"],
                        subject=subject,
                        raw_content=exp_data["raw_content"]
                    )
                    db.add(exp_db)
                    exp_dict[exp_num] = {
                        "experiment_number": exp_num,
                        "title": exp_data["title"],
                        "aim": exp_data["aim"],
                        "theory": exp_data["theory"],
                        "equipment": exp_data["equipment"],
                        "procedure": exp_data["procedure"],
                        "observations": exp_data["observations"],
                        "result": exp_data["result"],
                        "safety": exp_data["safety"],
                        "troubleshooting": exp_data["troubleshooting"],
                        "subject": subject,
                        "raw_content": exp_data["raw_content"]
                    }

                db.commit()
                db.close()

                # Build & Save FAISS Index
                splitter = TextSplitter(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
                chunks = splitter.split_experiments(manual_id, parsed_exps)
                vector_store.build_and_save_index(manual_id, chunks)

                # Update session state
                st.session_state.active_manual_id = manual_id
                st.session_state.extracted_data = {
                    "raw_text": full_text,
                    "cleaned_text": full_text,
                    "num_pages": num_pages,
                    "num_chunks": len(chunks),
                    "chunks": [c["text"] for c in chunks],
                    "subject": subject,
                    "parsed_experiments": parsed_exps
                }
                st.session_state.experiments = exp_dict

                st.markdown(f"""
                <div class='success-box'>
                ✅ File processed successfully<br><br>
                📄 <b>{uploaded_file.name}</b><br>
                🏷️ Subject: <b>{subject}</b><br>
                📚 Pages: {num_pages}<br>
                📦 Chunks: {len(chunks)}<br>
                🧪 Experiments: {len(parsed_exps)}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ Error: {extracted_res.get('error')}")

with col2:
    st.subheader("💡 How to Use")
    st.markdown("""
<div class='info-box'>

### Steps

1. Upload your lab manual PDF  
2. Wait for extraction & RAG indexing  
3. Open the experiment tab to review structured details  
4. Ask questions about experiments in the Query tab  

### Example Questions
- Aim of experiment 1 
- Theory of experiment 2 
- Procedure of experiment 3 
- Apparatus required for experiment 4 
- Result of experiment 5 
- Safety precautions for experiment 6

</div>
""", unsafe_allow_html=True)

# 5-Tab Extracted Content View (Exact UI layout preserved)
if st.session_state.extracted_data is not None:
    data = st.session_state.extracted_data
    st.divider()
    st.subheader("📖 Extracted Content")

    tabs = st.tabs([
        "📄 Raw Text",
        "🧹 Cleaned Text",
        "🧪 Experiments",
        "📊 Statistics",
        "💬 Query"
    ])

    # =========================
    # TAB 1: RAW TEXT
    # =========================
    with tabs[0]:
        st.markdown("### 📄 Raw Extracted Text")
        st.text_area(
            "Raw Text",
            value=(
                data["raw_text"][:3000] + "..."
                if len(data["raw_text"]) > 3000
                else data["raw_text"]
            ),
            height=350,
            disabled=True
        )
        st.download_button(
            label="📥 Download Full Raw Text",
            data=data["raw_text"],
            file_name=f"lab_manual_raw_{st.session_state.active_manual_id}.txt",
            mime="text/plain"
        )

    # =========================
    # TAB 2: CLEANED TEXT
    # =========================
    with tabs[1]:
        st.markdown("### 🧹 Cleaned & Normalized Text")
        st.text_area(
            "Cleaned Text",
            value=(
                data["cleaned_text"][:3000] + "..."
                if len(data["cleaned_text"]) > 3000
                else data["cleaned_text"]
            ),
            height=350,
            disabled=True
        )

    # =========================
    # TAB 3: EXPERIMENTS
    # =========================
    with tabs[2]:
        st.markdown("## 🧪 Detected Experiments")
        experiments = st.session_state.get("experiments", {})

        if experiments:
            st.success(f"✅ {len(experiments)} experiment(s) detected — Subject: {data.get('subject', 'General Science')}")
            for exp_num in sorted(experiments.keys()):
                exp = experiments[exp_num]
                title = getattr(exp, "title", None) or exp.get("title", f"Experiment {exp_num}")
                aim = getattr(exp, "aim", None) or exp.get("aim", "")
                theory = getattr(exp, "theory", None) or exp.get("theory", "")
                equipment = getattr(exp, "equipment", None) or exp.get("equipment", [])
                procedure = getattr(exp, "procedure", None) or exp.get("procedure", [])
                safety = getattr(exp, "safety", None) or exp.get("safety", [])
                trouble = getattr(exp, "troubleshooting", None) or exp.get("troubleshooting", "")

                with st.expander(f"🧪 Experiment {exp_num}: {title}"):
                    st.write("### 🎯 Aim")
                    st.write(aim or f"Conduct Experiment {exp_num}")

                    st.write("### 📘 Theory")
                    st.write(theory or "Theory section available in manual content.")

                    st.write("### 🛠 Equipment / Apparatus")
                    if equipment:
                        for item in equipment:
                            st.write(f"- {item}")
                    else:
                        st.write("No explicit equipment listed.")

                    st.write("### 📋 Step-by-Step Procedure")
                    if procedure:
                        for i, step in enumerate(procedure, 1):
                            st.write(f"{i}. {step}")
                    else:
                        st.write("No step-by-step procedure extracted.")

                    st.write("### ⚠️ Safety Precautions")
                    if safety:
                        for item in safety:
                            st.write(f"- {item}")
                    else:
                        st.write("Standard safety precautions apply.")

                    if trouble:
                        st.write("### 🔧 Troubleshooting Notes")
                        st.write(trouble)
        else:
            st.markdown("""
<div class='warning-box'>
⚠️ No structured experiment headings detected.
Possible reasons:
- The PDF is scanned
- Non-standard experiment headings
- OCR may be required
</div>
""", unsafe_allow_html=True)

    # =========================
    # TAB 4: STATISTICS
    # =========================
    with tabs[3]:
        st.markdown("## 📊 Text Statistics")
        text_val = data["cleaned_text"]
        words = text_val.split()
        sentences = [s for s in re.split(r"[.!?]+", text_val) if s.strip()]

        c1, c2 = st.columns(2)
        with c1:
            st.metric("📝 Character Count", f"{len(text_val):,}")
            st.metric("📚 Word Count", f"{len(words):,}")
            st.metric("🔤 Avg Word Length", f"{len(text_val) / len(words) if words else 0:.2f}")

        with c2:
            st.metric("🔢 Sentence Count", f"{len(sentences):,}")
            st.metric("📦 Chunk Count", data["num_chunks"])
            st.metric("📏 Avg Sentence Length", f"{len(words) / len(sentences) if sentences else 0:.2f}")

        with st.expander("📚 View Text Chunks"):
            for i, chunk in enumerate(data["chunks"][:10]):
                st.write(f"### Chunk {i + 1}")
                st.text(chunk[:400] + "..." if len(chunk) > 400 else chunk)

    # =========================
    # TAB 5: QUERY (GROUNDED RAG CHAT)
    # =========================
    with tabs[4]:
        st.markdown("## 💬 Ask Questions About Your Lab Manual")
        user_query = st.text_area(
            "Your Question",
            placeholder="Ask questions about procedures, theory, apparatus, safety, or troubleshooting...",
            height=120
        )

        if st.button("🔍 Search & Analyze", use_container_width=True):
            if not user_query.strip():
                st.warning("⚠️ Please enter a question")
            else:
                with st.spinner("Searching manual context & generating grounded answer..."):
                    # Check for experiment number in query
                    exp_match = re.search(r"exp[a-z]*\s*(?:no\.?|number)?\s*[-:\.]?\s*(\d+)", user_query, re.IGNORECASE)
                    exp_num = int(exp_match.group(1)) if exp_match else None
                    exp_id = f"{st.session_state.active_manual_id}_exp_{exp_num}" if exp_num else None

                    exp_ctx = None
                    if exp_num and exp_num in st.session_state.experiments:
                        e = st.session_state.experiments[exp_num]
                        exp_ctx = {
                            "experiment_number": exp_num,
                            "title": getattr(e, "title", "") or e.get("title", ""),
                            "aim": getattr(e, "aim", "") or e.get("aim", ""),
                            "theory": getattr(e, "theory", "") or e.get("theory", ""),
                            "equipment": getattr(e, "equipment", []) or e.get("equipment", []),
                            "procedure": getattr(e, "procedure", []) or e.get("procedure", []),
                            "safety": getattr(e, "safety", []) or e.get("safety", []),
                            "troubleshooting": getattr(e, "troubleshooting", "") or e.get("troubleshooting", "")
                        }

                    # Execute Grounded RAG Chat Lookup
                    response = qa_engine.answer_question(
                        manual_id=st.session_state.active_manual_id,
                        query=user_query,
                        experiment_id=exp_id,
                        exp_number=exp_num,
                        mode="standard",
                        exp_context=exp_ctx
                    )

                    st.markdown("### 📖 Answer")
                    st.markdown(response.answer)

                    # Collapsible Grounded Source Citations
                    if response.citations:
                        with st.expander(f"📚 Grounded Source Citations ({len(response.citations)} manual excerpts)"):
                            for cite in response.citations:
                                st.markdown(f"""
                                <div class='citation-box'>
                                <b>Section:</b> {cite.section_name} ({cite.experiment_title or 'Manual'})<br>
                                <b>Similarity Score:</b> {cite.score * 100:.1f}%<br>
                                <i>"{cite.excerpt}"</i>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("ℹ️ No specific manual excerpts found for this query.")

else:
    st.markdown("""
<div class='info-box'>
<h3>👋 Welcome</h3>

Upload a lab manual PDF to begin analysis.

The system will automatically:
- Extract text
- Classify subject
- Detect experiments & structure procedures
- Identify equipment & safety precautions
- Build vector store index for Grounded RAG Q&A

</div>
""", unsafe_allow_html=True)

# Footer (Exact original)
st.divider()
st.markdown("""
<div style='text-align:center; color:gray; padding:20px;'>

Lab Manual AI Assistant  
Powered by Streamlit, PDF Processing & Grounded RAG AI

</div>
""", unsafe_allow_html=True)
