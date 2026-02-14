import streamlit as st
from src.pdf_processor import extract_text_from_pdf, extract_pages
from src.experiment_extractor import ExperimentExtractor
from src.procedure_parser import ProcedureParser
import os

st.set_page_config(page_title="Lab Manual Assistant", layout="wide")

st.title("🧪 Lab Manual Conversational Assistant")
st.subheader("Upload your lab manual and extract procedures")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.write("1. Upload a lab manual PDF")
    st.write("2. Select an experiment")
    st.write("3. View procedures and theory")

# Main area
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Upload Manual")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file:
    # Save uploaded file
    with open(f"uploads/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    pdf_path = f"uploads/{uploaded_file.name}"
    
    # Extract content
    text = extract_text_from_pdf(pdf_path)
    extractor = ExperimentExtractor()
    parser = ProcedureParser()
    
    experiments = extractor.extract_experiments(text)
    
    with col2:
        st.header("📚 Extracted Experiments")
        
        if experiments:
            exp_titles = [f"Exp {e['number']}: {e['title']}" for e in experiments]
            selected = st.selectbox("Select an experiment:", exp_titles)
            
            st.header("📝 Procedure Steps")
            procedures = parser.extract_procedures(text)
            
            for proc in procedures:
                st.write(f"**Step {proc['step_number']}:** {proc['description']}")
        else:
            st.warning("No experiments found. Try another PDF.")

st.divider()
st.write("✅ **Week 1-2 Milestone:** Basic lab manual processing working!")
