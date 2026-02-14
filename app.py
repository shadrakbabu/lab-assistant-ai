import streamlit as st
from src.pdf_processor import extract_text_from_pdf
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

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

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
    
    # Extract experiments
    experiments = extractor.extract_experiments(text)
    
    with col2:
        st.header("📚 Extracted Experiments")
        
        if experiments:
            # Create experiment labels for selectbox
            exp_titles = [f"Exp {e['number']}: {e['title']}" for e in experiments]
            selected_idx = st.selectbox("Select an experiment:", range(len(exp_titles)), 
                                       format_func=lambda x: exp_titles[x])
            
            # Get selected experiment
            selected_exp = experiments[selected_idx]
            
            # Extract section for this specific experiment
            exp_section = extractor.extract_experiment_section(text, selected_exp['number'])
            
            # Extract procedures only from this experiment's section
            procedures = parser.extract_procedures(exp_section) if exp_section else []
            
            st.header("📝 Procedure Steps")
            
            if procedures:
                for proc in procedures:
                    st.write(f"**Step {proc['step_number']}:** {proc['description']}")
            else:
                st.info("No specific steps found. Showing experiment title...")
                st.write(f"**Experiment {selected_exp['number']}:** {selected_exp['title']}")
                st.info("This experiment may not have step-by-step procedures in the document.")
        else:
            st.warning("❌ No experiments found. Try another PDF.")

st.divider()
st.write("✅ **Week 1-2 Milestone:** Basic lab manual processing working!")
