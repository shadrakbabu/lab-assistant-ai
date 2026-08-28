import os
import pickle
import logging
import re
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from backend.app.config import settings

logger = logging.getLogger(__name__)

# Check SentenceTransformer availability
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.info("sentence_transformers not installed. Using TF-IDF vector search fallback.")

# Check FAISS availability
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class LightweightTFIDFVectorizer:
    """Zero-dependency TF-IDF text encoder for fast vector retrieval fallback."""

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def fit_transform(self, docs: List[str]) -> np.ndarray:
        word_counts = []
        doc_freq = {}
        all_words = set()

        for doc in docs:
            words = re.findall(r'\w+', doc.lower())
            counts = {}
            for w in words:
                if len(w) > 2:
                    counts[w] = counts.get(w, 0) + 1
                    all_words.add(w)
            word_counts.append(counts)
            for w in set(counts.keys()):
                doc_freq[w] = doc_freq.get(w, 0) + 1

        self.vocab = {word: i for i, word in enumerate(sorted(all_words))}
        num_docs = len(docs)
        self.idf = {word: math.log((num_docs + 1) / (df + 1)) + 1.0 for word, df in doc_freq.items()}

        vectors = np.zeros((num_docs, len(self.vocab)), dtype=np.float32)
        for d_idx, counts in enumerate(word_counts):
            for word, count in counts.items():
                if word in self.vocab:
                    v_idx = self.vocab[word]
                    vectors[d_idx, v_idx] = count * self.idf[word]

        # L2 normalize
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms

    def transform(self, docs: List[str]) -> np.ndarray:
        num_docs = len(docs)
        vectors = np.zeros((num_docs, len(self.vocab)), dtype=np.float32)
        if not self.vocab:
            return vectors

        for d_idx, doc in enumerate(docs):
            words = re.findall(r'\w+', doc.lower())
            counts = {}
            for w in words:
                if w in self.vocab:
                    counts[w] = counts.get(w, 0) + 1
            for word, count in counts.items():
                v_idx = self.vocab[word]
                vectors[d_idx, v_idx] = count * self.idf.get(word, 1.0)

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


class FAISSVectorStore:
    """Vector store supporting SentenceTransformers/FAISS and Lightweight TF-IDF fallback."""

    def __init__(self, model_name: str = None, store_dir: Path = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.store_dir = Path(store_dir or settings.VECTORSTORE_DIR)
        self.store_dir.mkdir(exist_ok=True, parents=True)
        self.encoder = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading SentenceTransformer model: {self.model_name}")
                self.encoder = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {e}")

    def build_and_save_index(self, manual_id: str, chunks: List[Dict[str, Any]]) -> bool:
        if not chunks:
            logger.warning(f"No chunks provided for manual {manual_id}")
            return False

        texts = [chunk["text"] for chunk in chunks]
        meta_path = self.store_dir / f"{manual_id}_meta.pkl"
        embeddings_path = self.store_dir / f"{manual_id}_emb.npy"
        tfidf_path = self.store_dir / f"{manual_id}_tfidf.pkl"

        try:
            if self.encoder:
                embeddings = self.encoder.encode(texts, convert_to_numpy=True).astype(np.float32)
                np.save(str(embeddings_path), embeddings)

                if FAISS_AVAILABLE:
                    index = faiss.IndexFlatL2(embeddings.shape[1])
                    index.add(embeddings)
                    faiss.write_index(index, str(self.store_dir / f"{manual_id}_index.bin"))
            else:
                tfidf = LightweightTFIDFVectorizer()
                embeddings = tfidf.fit_transform(texts)
                np.save(str(embeddings_path), embeddings)
                with open(tfidf_path, "wb") as f:
                    pickle.dump(tfidf, f)

            with open(meta_path, "wb") as f:
                pickle.dump(chunks, f)

            logger.info(f"Successfully saved vector index for {manual_id} ({len(chunks)} chunks)")
            return True
        except Exception as e:
            logger.error(f"Failed to save vector index for {manual_id}: {e}")
            return False

    def search(
        self,
        manual_id: str,
        query: str,
        top_k: int = 5,
        experiment_number: int = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        meta_path = self.store_dir / f"{manual_id}_meta.pkl"
        embeddings_path = self.store_dir / f"{manual_id}_emb.npy"

        if not meta_path.exists() or not embeddings_path.exists():
            logger.warning(f"No vector index found for manual_id {manual_id}")
            return []

        try:
            with open(meta_path, "rb") as f:
                chunks: List[Dict[str, Any]] = pickle.load(f)

            embeddings = np.load(str(embeddings_path))

            if self.encoder:
                query_vector = self.encoder.encode([query], convert_to_numpy=True).astype(np.float32)
                norm_q = query_vector / (np.linalg.norm(query_vector, axis=1, keepdims=True) + 1e-9)
                norm_emb = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9)
                sims = np.dot(norm_emb, norm_q.T).flatten()
            else:
                tfidf_path = self.store_dir / f"{manual_id}_tfidf.pkl"
                if tfidf_path.exists():
                    with open(tfidf_path, "rb") as f:
                        tfidf: LightweightTFIDFVectorizer = pickle.load(f)
                    query_vector = tfidf.transform([query])
                    sims = np.dot(embeddings, query_vector.T).flatten()
                else:
                    sims = np.zeros(len(chunks))

            raw_indices = np.argsort(sims)[::-1][:top_k * 3]
            raw_scores = [float(sims[idx]) for idx in raw_indices]

            results = []
            for idx, score in zip(raw_indices, raw_scores):
                if idx < len(chunks):
                    chunk = chunks[idx]
                    if experiment_number is not None and chunk.get("experiment_number") != experiment_number:
                        continue

                    results.append((chunk, score))
                    if len(results) >= top_k:
                        break

            return results

        except Exception as e:
            logger.error(f"Error searching vector store for {manual_id}: {e}")
            return []


# Global singleton instance
vector_store = FAISSVectorStore()
