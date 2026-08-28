from typing import List, Dict, Any


class TextSplitter:
    """Splits lab manual text into overlapping chunks with metadata attributes."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_experiments(
        self,
        manual_id: str,
        experiments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        chunks = []
        global_chunk_id = 0

        for exp in experiments:
            exp_num = exp["experiment_number"]
            title = exp["title"]
            raw_text = exp.get("raw_content", "")

            if not raw_text:
                continue

            # Split raw text into chunks
            start = 0
            while start < len(raw_text):
                end = start + self.chunk_size
                chunk_text = raw_text[start:end].strip()

                if len(chunk_text) > 30:
                    chunks.append({
                        "chunk_id": f"{manual_id}_exp{exp_num}_c{global_chunk_id}",
                        "manual_id": manual_id,
                        "experiment_number": exp_num,
                        "experiment_title": title,
                        "text": chunk_text
                    })
                    global_chunk_id += 1

                start = end - self.chunk_overlap

        return chunks
