import re
import streamlit as st
from src.pdf_processor import extract_text_from_pdf
from src.experiment_extractor import ExperimentExtractor
from src.procedure_parser import ProcedureParser
import os

st.set_page_config(page_title="Lab Manual Assistant", layout="wide")

st.title(" Lab Manual Conversational Assistant")
st.subheader("Upload your lab manual and extract procedures")

# Sidebar
with st.sidebar:
    st.header("Instructions")
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
            # Create experiment labels for selectbox (shortened)
            def short_title(e):
                t = e.get('title','').strip()
                t = t if len(t) <= 120 else t[:117] + '...'
                return f"Exp {e['number']}: {t}"

            exp_titles = [short_title(e) for e in experiments]
            selected_idx = st.selectbox("Select an experiment:", range(len(exp_titles)), 
                                       format_func=lambda x: exp_titles[x])
            
            # Get selected experiment
            selected_exp = experiments[selected_idx]
            
            # Extract section for this specific experiment (prefer title-based anchoring)
            exp_section = extractor.extract_experiment_section(
                text, selected_exp['number'], selected_exp.get('title')
            )

            # Extract experiment section from entire text
            exp_section = extractor.extract_experiment_section(
                text, selected_exp['number'], selected_exp.get('title')
            )

            if not exp_section:
                exp_section = text

            procedures = parser.extract_procedures(exp_section)
            precautions = parser.extract_precautions(exp_section)

            st.header("Procedure Steps")
            if procedures:
                for proc in procedures:
                    st.markdown(f"**Step {proc['step_number']}:**")
                    st.markdown(proc['description'])
                    st.markdown("---")
            else:
                st.warning("No step-by-step procedures detected in this experiment section.")

            if precautions:
                st.header("Precautions")
                st.markdown(precautions)

        else:
            st.warning("No experiments found. Try another PDF.")

st.divider()
