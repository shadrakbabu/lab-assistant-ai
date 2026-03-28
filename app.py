import streamlit as st
import os
from pathlib import Path
from app.pdf_processor import PDFProcessor

# Page configuration
st.set_page_config(
    page_title="Lab Manual AI Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "processor" not in st.session_state:
    st.session_state.processor = PDFProcessor()
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

# Custom CSS
st.markdown("""
    <style>
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='header'><h1>🧪 Lab Manual AI Assistant</h1><p>Upload your lab manual PDF and get instant help with experiments, procedures, and theory</p></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(" API Key", type="password", key="api_key_input")
    llm_model = st.selectbox("LLM Model", ["gpt-3.5-turbo", "gpt-4", "gemini-pro"])
    st.markdown("---")
    st.info("✨ Features:\n- ✅ PDF text extraction\n- 🔄 Experiment extraction\n- 📋 Step-by-step procedures\n- 📚 Theory explanations\n- 🛠️ Equipment detection\n- ⚠️ Safety precautions")

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📁 Upload Lab Manual")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF lab manual to analyze"
    )

    if uploaded_file is not None:
        # Save uploaded file
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        file_path = data_dir / uploaded_file.name

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Process PDF
        with st.spinner("📄 Processing PDF..."):
            processor = st.session_state.processor
            extracted_data = processor.process_pdf(
                str(file_path), clean=True, chunk=True
            )

            if extracted_data["success"]:
                st.session_state.extracted_data = extracted_data
                st.success(f"✅ File processed: {uploaded_file.name}")
                st.info(f"📊 Pages: {extracted_data['num_pages']} | Chunks: {extracted_data['num_chunks']}")
            else:
                st.error(f"❌ Error: {extracted_data['error']}")

with col2:
    st.subheader("💡 How to Use")
    st.markdown("""
    1. **Upload PDF**: Choose your lab manual PDF
    2. **View Content**: Extracted text appears below
    3. **Ask Questions**:
       - "Explain experiment 1"
       - "Give me the procedure"
       - "Explain the theory simply"
       - "List the equipment needed"
       - "Show safety precautions"
    4. **Get Answers**: AI-powered responses

    ### Current Features
    - ✅ PDF text extraction
    - ✅ Text cleaning & normalization
    - ✅ Content chunking for processing
    - ✅ Statistics & metadata
    """)

# Main interaction area
if st.session_state.extracted_data is not None:
    data = st.session_state.extracted_data
    st.divider()
    st.subheader("📖 Extracted Content")

    tabs = st.tabs(["📄 Raw Text", "🧹 Cleaned Text", "📊 Statistics", "💬 Query"])

    with tabs[0]:
        st.markdown("**Raw extracted text from PDF:**")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_area(
                "Raw Text:",
                value=data["raw_text"][:2000] + "..." if len(data["raw_text"]) > 2000 else data["raw_text"],
                height=300,
                disabled=True,
            )
        with col2:
            st.metric("Total Characters", len(data["raw_text"]))
            st.metric("Total Pages", data["num_pages"])
            if st.button("📥 Download Raw Text", key="raw"):
                st.text(data["raw_text"])

    with tabs[1]:
        st.markdown("**Cleaned and normalized text:**")
        st.text_area(
            "Cleaned Text:",
            value=data["cleaned_text"][:2000] + "..." if len(data["cleaned_text"]) > 2000 else data["cleaned_text"],
            height=300,
            disabled=True,
        )

    with tabs[2]:
        st.markdown("**Text Statistics & Metadata:**")
        stats = st.session_state.processor.get_text_stats(data["cleaned_text"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Character Count", f"{stats['character_count']:,}")
            st.metric("📚 Word Count", f"{stats['word_count']:,}")
            st.metric("🔤 Avg Word Length", f"{stats['avg_word_length']:.2f}")

        with col2:
            st.metric("🔢 Sentence Count", f"{stats['sentence_count']:,}")
            st.metric("📖 Chunk Count", data["num_chunks"])
            st.metric("📏 Avg Sentence Length", f"{stats['avg_sentence_length']:.2f}")

        with st.expander("View Text Chunks"):
            for i, chunk in enumerate(data["chunks"][:10]):  # Show first 10 chunks
                st.write(f"**Chunk {i + 1}:**")
                st.text(chunk[:300] + "..." if len(chunk) > 300 else chunk)

    with tabs[3]:
        st.markdown("**Ask Questions About Your Lab Manual:**")
        user_query = st.text_area(
            "Your Question:",
            placeholder="e.g., What is experiment 1 about? Explain the theory...",
            height=100,
        )

        if st.button("🔍 Search & Analyze", use_container_width=True):
            st.info("🔄 Processing... (Advanced features coming in next phase)")

elif uploaded_file is not None and st.session_state.extracted_data is None:
    st.warning("⚠️ Please upload a PDF file to see content")
else:
    st.markdown("<div class='info-box'><h3>👈 Get Started</h3><p>Upload a PDF lab manual to begin. The assistant will extract and process the content for you.</p></div>", unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    <p><small>Lab Manual AI Assistant | Powered by Streamlit, PyPDF2 & LangChain</small></p>
</div>
""", unsafe_allow_html=True)
