
import streamlit as st
import os
import re
from pathlib import Path
from app.pdf_processor import PDFProcessor
from app.experiment_parser import ExperimentParser


st.set_page_config(
    page_title="Lab Manual AI Assistant",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "processor" not in st.session_state:
    st.session_state.processor = PDFProcessor()

if "parser" not in st.session_state:
    st.session_state.parser = ExperimentParser()

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None

if "experiments" not in st.session_state:
    st.session_state.experiments = {}

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

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='header'>
    <h1>🧪 Lab Manual AI Assistant</h1>
    <p>
        Upload your lab manual PDF and instantly extract experiments,
        procedures, equipment, theory, and safety precautions.
    </p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:

    st.markdown("## 📘 About")

    st.markdown("""
<div class='feature-box'>

<div class='feature-title'>
✨ Features
</div>

✅ PDF text extraction  
✅ Experiment detection  
✅ Step-by-step procedures  
✅ Equipment identification  
✅ Safety precautions  
✅ Smart text cleaning  
✅ Statistics & metadata  

</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    st.success("✅ Student Mode Enabled")


col1, col2 = st.columns([1, 2])


with col1:

    st.subheader("📁 Upload Lab Manual")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload your lab manual PDF"
    )

    if uploaded_file is not None:

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        file_path = data_dir / uploaded_file.name

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("🔍 Extracting experiments and analyzing PDF..."):

            processor = st.session_state.processor

            extracted_data = processor.process_pdf(
                str(file_path),
                clean=True,
                chunk=True
            )

            if extracted_data["success"]:

                st.session_state.extracted_data = extracted_data

                parser = st.session_state.parser

                cleaned_text = extracted_data["cleaned_text"]

                # =========================
                # BETTER EXPERIMENT DETECTION
                # =========================
                experiment_patterns = [
                    r'EXPERIMENT\s*[-:]?\s*\d+',
                    r'Experiment\s*No\.?\s*\d+',
                    r'Exercise\s*\d+',
                    r'Practical\s*\d+',
                    r'Aim\s*:'
                ]

                detected = False

                for pattern in experiment_patterns:
                    if re.search(pattern, cleaned_text, re.IGNORECASE):
                        detected = True
                        break

                if detected:
                    experiments = parser.parse_experiments(cleaned_text)
                    st.session_state.experiments = experiments
                else:
                    st.session_state.experiments = {}

                st.markdown(f"""
                <div class='success-box'>
                ✅ File processed successfully<br><br>
                📄 <b>{uploaded_file.name}</b><br>
                📚 Pages: {extracted_data['num_pages']}<br>
                📦 Chunks: {extracted_data['num_chunks']}
                </div>
         """, unsafe_allow_html=True)

            else:
                st.error(f"❌ Error: {extracted_data['error']}")


with col2:

    st.subheader("💡 How to Use")

    st.markdown("""
<div class='info-box'>

### Steps

1. Upload your lab manual PDF  
2. Wait for extraction & analysis  
3. Open the experiment tab  
4. Ask questions about experiments  

### Example Questions
- Aim of experiment 1 
- Theory of experiment 2 
- Procedure of experiment 3 
- Apparatus required for experiment 4 
- Result of experiment 5 
- Viva questions of experiment 6

</div>
""", unsafe_allow_html=True)

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
    # RAW TEXT TAB
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

    # =========================
    # CLEANED TEXT TAB
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

    
    with tabs[2]:

        st.markdown("## 🧪 Detected Experiments")

        experiments = st.session_state.get("experiments", {})

        if experiments:

            parser = st.session_state.parser

            summaries = parser.get_summary(experiments)

            st.success(f"✅ {len(summaries)} experiments detected")

            for summary in summaries:

                exp = experiments[summary["number"]]

                with st.expander(
                    f"🧪 Experiment {exp.number}: {exp.title}"
                ):

                    st.write("## 📘 Title")
                    st.write(exp.title)

                    st.write("## 🛠 Equipment")

                    if exp.equipment:
                        for item in exp.equipment:
                            st.write(f"- {item}")
                    else:
                        st.write("No equipment detected")

                    st.write("## 📋 Procedure")

                    if exp.procedure:
                        for i, step in enumerate(exp.procedure, 1):
                            st.write(f"{i}. {step}")
                    else:
                        st.write("No procedure detected")

                    st.write("## ⚠️ Safety Precautions")

                    if exp.safety:
                        for item in exp.safety:
                            st.write(f"- {item}")
                    else:
                        st.write("No safety precautions detected")

        else:

            st.markdown("""
<div class='warning-box'>

⚠️ No structured experiment headings detected.

Possible reasons:
- The PDF is scanned
- Non-standard experiment headings
- OCR may be required
- Poor PDF formatting

</div>
""", unsafe_allow_html=True)

    with tabs[3]:

        st.markdown("## 📊 Text Statistics")

        stats = st.session_state.processor.get_text_stats(
            data["cleaned_text"]
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric("📝 Character Count", f"{stats['character_count']:,}")
            st.metric("📚 Word Count", f"{stats['word_count']:,}")
            st.metric("🔤 Avg Word Length", f"{stats['avg_word_length']:.2f}")

        with c2:
            st.metric("🔢 Sentence Count", f"{stats['sentence_count']:,}")
            st.metric("📦 Chunk Count", data["num_chunks"])
            st.metric("📏 Avg Sentence Length", f"{stats['avg_sentence_length']:.2f}")

        with st.expander("📚 View Text Chunks"):

            for i, chunk in enumerate(data["chunks"][:10]):

                st.write(f"### Chunk {i + 1}")

                st.text(
                    chunk[:400] + "..."
                    if len(chunk) > 400
                    else chunk
                )

    
    

    with tabs[4]:

        st.markdown("## 💬 Ask Questions About Your Lab Manual")

        user_query = st.text_area(
        "Your Question",
        placeholder=""" Ask your questions in here
""",
        height=120
    )

    if st.button(
        "🔍 Search & Analyze",
        use_container_width=True
    ):

        if user_query.strip() == "":

            st.warning(
                "⚠️ Please enter a question"
            )

        else:

            # =========================
            # NORMALIZE QUERY
            # =========================
            query = user_query.lower().strip()

            found_answer = False

            # =========================
            # DETECT EXPERIMENT NUMBER
            # =========================
            exp_match = re.search(
                r"experiment\s*(?:no\.?|number)?\s*[-:\.]?\s*(\d+)",
                query,
                re.IGNORECASE
            )

            if exp_match:

                exp_number = exp_match.group(1)

                # =========================
                # GET CLEANED TEXT
                # =========================
                cleaned_text = st.session_state.extracted_data[
                    "cleaned_text"
                ]

                # =========================
                # FIND EXPERIMENT BLOCK
                # =========================
                experiment_pattern = (
                    rf"(EXPERIMENT\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*{exp_number}"
                    rf".*?)(?=EXPERIMENT\s*(?:NO\.?|NUMBER)?\s*[-:\.]?\s*\d+|$)"
                )

                experiment_match = re.search(
                    experiment_pattern,
                    cleaned_text,
                    re.IGNORECASE | re.DOTALL
                )

                if experiment_match:

                    experiment_text = experiment_match.group(1)

                    # =========================
                    # GENERIC SECTION EXTRACTOR
                    # =========================
                    def extract_section(
                        keywords,
                        stop_words
                    ):

                        pattern = (
                            rf"({'|'.join(keywords)})\s*[:\-]?\s*"
                            rf"(.*?)"
                            rf"(?={'|'.join(stop_words)}|$)"
                        )

                        match = re.search(
                            pattern,
                            experiment_text,
                            re.IGNORECASE | re.DOTALL
                        )

                        if match:

                            return match.group(2).strip()

                        return None

                    # =========================
                    # COMMON STOP WORDS
                    # =========================
                    stop_words = [
                        "AIM",
                        "OBJECTIVE",
                        "THEORY",
                        "APPARATUS",
                        "EQUIPMENT",
                        "MATERIALS REQUIRED",
                        "PROCEDURE",
                        "RESULT",
                        "OBSERVATION",
                        "CONCLUSION",
                        "PRECAUTIONS",
                        "SAFETY",
                        "VIVA",
                        "QUESTIONS"
                    ]

                    # =========================
                    # AIM
                    # =========================
                    if (
                        "aim" in query
                        or "objective" in query
                    ):

                        st.success(
                            f"🎯 Aim of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["AIM", "OBJECTIVE"],
                            stop_words
                        )

                        if result:
                            st.write(result)
                        else:
                            st.warning("Aim not found")

                        found_answer = True

                    # =========================
                    # THEORY
                    # =========================
                    elif "theory" in query:

                        st.success(
                            f"📘 Theory of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["THEORY"],
                            stop_words
                        )

                        if result:
                            st.write(result)
                        else:
                            st.warning("Theory not found")

                        found_answer = True

                    # =========================
                    # PROCEDURE
                    # =========================
                    elif (
                        "procedure" in query
                        or "steps" in query
                    ):

                        st.success(
                            f"🧪 Procedure of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["PROCEDURE"],
                            stop_words
                        )

                        if result:

                            steps = [
                                step.strip()
                                for step in re.split(
                                    r"\n|\d+\.",
                                    result
                                )
                                if len(step.strip()) > 5
                            ]

                            for i, step in enumerate(
                                steps,
                                1
                            ):

                                st.write(
                                    f"{i}. {step}"
                                )

                        else:
                            st.warning(
                                "Procedure not found"
                            )

                        found_answer = True

                    # =========================
                    # APPARATUS / EQUIPMENT
                    # =========================
                    elif (
                        "apparatus" in query
                        or "equipment" in query
                        or "materials" in query
                    ):

                        st.success(
                            f"🔧 Apparatus for Experiment {exp_number}"
                        )

                        result = extract_section(
                            [
                                "APPARATUS",
                                "EQUIPMENT",
                                "MATERIALS REQUIRED"
                            ],
                            stop_words
                        )

                        if result:

                            items = [
                                item.strip()
                                for item in re.split(
                                    r",|\n|•|-",
                                    result
                                )
                                if len(item.strip()) > 2
                            ]

                            for item in items:

                                st.write(
                                    f"- {item}"
                                )

                        else:
                            st.warning(
                                "Apparatus not found"
                            )

                        found_answer = True

                    # =========================
                    # RESULT
                    # =========================
                    elif "result" in query:

                        st.success(
                            f"📊 Result of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["RESULT"],
                            stop_words
                        )

                        if result:
                            st.write(result)
                        else:
                            st.warning("Result not found")

                        found_answer = True

                    # =========================
                    # OBSERVATION
                    # =========================
                    elif "observation" in query:

                        st.success(
                            f"👀 Observation of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["OBSERVATION"],
                            stop_words
                        )

                        if result:
                            st.write(result)
                        else:
                            st.warning(
                                "Observation not found"
                            )

                        found_answer = True

                    # =========================
                    # CONCLUSION
                    # =========================
                    elif "conclusion" in query:

                        st.success(
                            f"✅ Conclusion of Experiment {exp_number}"
                        )

                        result = extract_section(
                            ["CONCLUSION"],
                            stop_words
                        )

                        if result:
                            st.write(result)
                        else:
                            st.warning(
                                "Conclusion not found"
                            )

                        found_answer = True

                    # =========================
                    # PRECAUTIONS / SAFETY
                    # =========================
                    elif (
                        "precaution" in query
                        or "safety" in query
                    ):

                        st.success(
                            f"⚠️ Precautions for Experiment {exp_number}"
                        )

                        result = extract_section(
                            [
                                "PRECAUTIONS",
                                "SAFETY"
                            ],
                            stop_words
                        )

                        if result:

                            items = [
                                item.strip()
                                for item in re.split(
                                    r"\n|•|-",
                                    result
                                )
                                if len(item.strip()) > 3
                            ]

                            for item in items:

                                st.write(
                                    f"- {item}"
                                )

                        else:
                            st.warning(
                                "Precautions not found"
                            )

                        found_answer = True

                    # =========================
                    # VIVA QUESTIONS
                    # =========================
                    elif (
                        "viva" in query
                        or "questions" in query
                    ):

                        st.success(
                            f"❓ Viva Questions of Experiment {exp_number}"
                        )

                        result = extract_section(
                            [
                                "VIVA",
                                "VIVA QUESTIONS",
                                "QUESTIONS"
                            ],
                            stop_words
                        )

                        if result:

                            questions = [
                                q.strip()
                                for q in re.split(
                                    r"\n|\d+\.",
                                    result
                                )
                                if len(q.strip()) > 5
                            ]

                            for i, q in enumerate(
                                questions,
                                1
                            ):

                                st.write(
                                    f"{i}. {q}"
                                )

                        else:
                            st.warning(
                                "Viva questions not found"
                            )

                        found_answer = True

                    # =========================
                    # FULL DETAILS
                    # =========================
                    else:

                        st.success(
                            f"📘 Full Details of Experiment {exp_number}"
                        )

                        st.text_area(
                            "Experiment Content",
                            value=experiment_text[:5000],
                            height=500
                        )

                        found_answer = True

            # =========================
            # NO RESULT
            # =========================
            if not found_answer:

                st.warning("""
Could not find matching experiment information.

Try:
- Aim of experiment 1
- Theory of experiment 2
- Procedure of experiment 3
- Apparatus required for experiment 4
- Result of experiment 5
- Viva questions of experiment 6
""")


else:

    st.markdown("""
<div class='info-box'>
<h3>👋 Welcome</h3>

Upload a lab manual PDF to begin analysis.

The system will automatically:
- Extract text
- Detect experiments
- Parse procedures
- Identify equipment
- Detect safety instructions

</div>
""", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.divider()

st.markdown("""
<div style='text-align:center; color:gray; padding:20px;'>

Lab Manual AI Assistant  
Powered by Streamlit, PDF Processing & AI

</div>
""", unsafe_allow_html=True)
