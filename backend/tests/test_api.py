import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.database import init_db, SessionLocal
from backend.app.models.manual import LabManualDB, ExperimentDB
from backend.app.parsers.pdf_extractor import PDFExtractor
from backend.app.parsers.experiment_parser import ExperimentParser
from backend.app.parsers.subject_classifier import SubjectClassifier
from backend.app.rag.text_splitter import TextSplitter
from backend.app.rag.vector_store import vector_store
from backend.app.rag.qa_engine import qa_engine


def test_full_pipeline():
    print("=== Initializing test database ===")
    init_db()

    pdf_path = root_dir / "data" / "LAB MANUAL PDF FOR TESTING.pdf"
    if not pdf_path.exists():
        pdf_path = root_dir / "data" / "Final_BET_manual.pdf"

    print(f"Testing with PDF file: {pdf_path.name}")
    extractor = PDFExtractor()
    extracted_data = extractor.extract_pdf_data(str(pdf_path))

    assert extracted_data["success"], f"Extraction failed: {extracted_data.get('error')}"
    print(f"Extracted {extracted_data['num_pages']} pages successfully.")

    subject = SubjectClassifier.classify(extracted_data["extracted_text"])
    print(f"Classified Subject: {subject}")

    parser = ExperimentParser()
    experiments = parser.parse_experiments(extracted_data["extracted_text"])
    print(f"Detected {len(experiments)} experiment(s).")

    for exp in experiments:
        print(f"   - Exp {exp['experiment_number']}: {exp['title']} ({len(exp['procedure'])} steps, {len(exp['equipment'])} equipment, {len(exp['safety'])} safety rules)")

    # Test database persistence
    db = SessionLocal()
    manual_id = "test_manual_001"
    
    # Clean up both tables explicitly before insert
    db.query(ExperimentDB).filter(ExperimentDB.manual_id == manual_id).delete()
    db.query(LabManualDB).filter(LabManualDB.id == manual_id).delete()
    db.commit()

    manual_db = LabManualDB(
        id=manual_id,
        filename=pdf_path.name,
        file_path=str(pdf_path),
        file_size_kb=extracted_data["file_size_kb"],
        page_count=extracted_data["num_pages"],
        subject=subject,
        extracted_text=extracted_data["extracted_text"],
        num_experiments=len(experiments)
    )
    db.add(manual_db)

    for exp_data in experiments:
        exp_db = ExperimentDB(
            id=f"{manual_id}_exp_{exp_data['experiment_number']}",
            manual_id=manual_id,
            experiment_number=exp_data["experiment_number"],
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

    db.commit()
    print("Successfully saved manual & experiments to SQLite database.")

    # Test FAISS Vector Store Indexing
    splitter = TextSplitter()
    chunks = splitter.split_experiments(manual_id, experiments)
    success = vector_store.build_and_save_index(manual_id, chunks)
    assert success, "FAISS vector store indexing failed."
    print(f"Vector store index built and saved ({len(chunks)} text chunks).")

    # Test Grounded Q&A Chat Engine with Exp 11
    queries = [
        "What is the procedure?",
        "What equipment is required?",
        "What precautions should I take?"
    ]

    first_exp_num = experiments[0]["experiment_number"] if experiments else 11
    exp_id = f"{manual_id}_exp_{first_exp_num}"
    first_exp = experiments[0] if experiments else None

    for q in queries:
        response = qa_engine.answer_question(
            manual_id=manual_id,
            query=q,
            experiment_id=exp_id,
            exp_number=first_exp_num,
            mode="standard",
            exp_context=first_exp
        )
        print(f"\nQuery: {q}")
        print(f"Answer: {response.answer[:150]}...")
        print(f"Citations: {len(response.citations)} source excerpt(s) retrieved.")
        assert len(response.citations) > 0, "Expected at least 1 citation excerpt for detected experiment."

    db.close()
    print("\nALL BACKEND PIPELINE TESTS PASSED CLEANLY WITH CITATIONS!")


if __name__ == "__main__":
    test_full_pipeline()
