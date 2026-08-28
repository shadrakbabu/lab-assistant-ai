import streamlit as st
import tempfile
from dotenv import load_dotenv

from utils.pdf_loader import load_pdf
from utils.vector_store import create_vector_store
from utils.qa_chain import build_qa_chain
from utils.prompts import SYSTEM_PROMPT

load_dotenv()

st.set_page_config(
    page_title="AI Lab Assistant",
    layout="wide"
)

st.title("🧪 AI-Powered Lab Manual Assistant")
st.subheader("Upload • Understand • Ask • Learn")

# Sidebar
st.sidebar.title("📚 Features")
st.sidebar.write("✔ Theory Explanation")
st.sidebar.write("✔ Step-by-Step Procedure")
st.sidebar.write("✔ Safety Precautions")
st.sidebar.write("✔ Experiment Q&A")

uploaded_file = st.file_uploader(
    "Upload Lab Manual PDF",
    type=["pdf"]
)

if uploaded_file:

    with st.spinner("Processing Lab Manual..."):
        temp_pdf = tempfile.NamedTemporaryFile(delete=False)
        temp_pdf.write(uploaded_file.read())

        docs = load_pdf(temp_pdf.name)

        vectorstore = create_vector_store(docs)

        qa_chain = build_qa_chain(
            vectorstore,
            SYSTEM_PROMPT
        )

    st.success("Lab Manual Processed Successfully ✅")

    question = st.text_input(
        "Ask a question about the experiment"
    )

    sample_questions = [
        "Explain the theory of Experiment 3",
        "What are the precautions?",
        "Give the procedure step by step",
        "Explain this experiment in simple terms"
    ]

    st.write("### Example Questions")
    for q in sample_questions:
        st.write(f"• {q}")

    if question:
        with st.spinner("Generating Answer..."):
            response = qa_chain.run(question)

        st.write("## 📖 Answer")
        st.write(response)