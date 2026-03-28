"""
Vector Store Module

Implements semantic search using FAISS and sentence-transformers.
Integrates with LangChain for document retrieval and Q&A.
"""

import os
import pickle
import logging
from typing import List, Dict, Tuple
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic search."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        store_path: Path = None
    ):
        """
        Initialize vector store.

        Args:
            model_name: Sentence transformer model name
            store_path: Path to store FAISS index and metadata
        """
        self.model_name = model_name
        self.store_path = Path(store_path) if store_path else Path("vectorstore")
        self.store_path.mkdir(exist_ok=True)

        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index = None
        self.documents = []  # Store original texts
        self.metadata = []   # Store metadata (source, chunk_id, etc.)

        # Load existing index if available
        self._load_index()

    def _load_index(self) -> bool:
        """Load FAISS index from disk if it exists."""
        index_path = self.store_path / "faiss_index.bin"
        docs_path = self.store_path / "documents.pkl"
        meta_path = self.store_path / "metadata.pkl"

        if index_path.exists() and docs_path.exists():
            try:
                self.index = faiss.read_index(str(index_path))
                with open(docs_path, "rb") as f:
                    self.documents = pickle.load(f)
                with open(meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded {len(self.documents)} documents from disk")
                return True
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")
                return False

        return False

    def _save_index(self) -> None:
        """Save FAISS index to disk."""
        try:
            index_path = self.store_path / "faiss_index.bin"
            docs_path = self.store_path / "documents.pkl"
            meta_path = self.store_path / "metadata.pkl"

            faiss.write_index(self.index, str(index_path))
            with open(docs_path, "wb") as f:
                pickle.dump(self.documents, f)
            with open(meta_path, "wb") as f:
                pickle.dump(self.metadata, f)

            logger.info(f"Saved {len(self.documents)} documents to disk")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def add_documents(
        self,
        texts: List[str],
        metadata: List[Dict] = None
    ) -> None:
        """
        Add documents to vector store.

        Args:
            texts: List of text chunks
            metadata: List of metadata dicts (source, chunk_id, etc.)
        """
        if not texts:
            logger.warning("No texts provided")
            return

        logger.info(f"Adding {len(texts)} documents to vector store")

        # Generate embeddings
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Initialize or update FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Add embeddings to index
        self.index.add(embeddings.astype(np.float32))

        # Store documents and metadata
        self.documents.extend(texts)

        if metadata is None:
            metadata = [{"source": "unknown", "chunk_id": i} for i in range(len(texts))]

        self.metadata.extend(metadata)

        # Save to disk
        self._save_index()

        logger.info(f"Vector store now contains {len(self.documents)} documents")

    def search(
        self,
        query: str,
        k: int = 5,
        similarity_threshold: float = 0.0
    ) -> Tuple[List[str], List[float], List[Dict]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            similarity_threshold: Minimum similarity score

        Returns:
            Tuple of (documents, scores, metadata)
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("Vector store is empty")
            return [], [], []

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)

        # Convert distances to similarity scores (L2 distance)
        # Lower distance = higher similarity
        scores = 1 / (1 + distances[0])  # Convert to similarity

        # Filter by threshold
        results = []
        result_scores = []
        result_metadata = []

        for idx, score in zip(indices[0], scores):
            if score >= similarity_threshold and idx < len(self.documents):
                results.append(self.documents[idx])
                result_scores.append(float(score))
                result_metadata.append(self.metadata[idx])

        logger.info(f"Search returned {len(results)} results for query: {query}")
        return results, result_scores, result_metadata

    def search_by_experiment(
        self,
        experiment_number: int,
        k: int = 5
    ) -> Tuple[List[str], List[float], List[Dict]]:
        """
        Search for documents related to an experiment.

        Args:
            experiment_number: Experiment number
            k: Number of results to return

        Returns:
            Tuple of (documents, scores, metadata)
        """
        query = f"Experiment {experiment_number}"
        return self.search(query, k)

    def clear(self) -> None:
        """Clear all data from vector store."""
        self.index = None
        self.documents = []
        self.metadata = []
        logger.info("Vector store cleared")

    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        return {
            "model": self.model_name,
            "embedding_dim": self.embedding_dim,
            "document_count": len(self.documents),
            "index_size": len(self.documents),
            "store_path": str(self.store_path)
        }


class LANGChainIntegration:
    """Integration with LangChain for Q&A and retrieval."""

    def __init__(self, vector_store: VectorStore):
        """
        Initialize LangChain integration.

        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store
        logger.info("LangChain integration initialized")

    def retrieve_context(
        self,
        query: str,
        k: int = 5
    ) -> str:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query
            k: Number of documents to retrieve

        Returns:
            Concatenated context string
        """
        documents, scores, metadata = self.vector_store.search(query, k)

        if not documents:
            return "No relevant documents found."

        # Build context
        context = "Retrieved Context:\n\n"
        for i, (doc, score, meta) in enumerate(zip(documents, scores, metadata), 1):
            context += f"[{i}] (Score: {score:.2f})\n"
            context += f"Source: {meta.get('source', 'Unknown')}\n"
            context += f"Content: {doc[:300]}...\n\n"

        return context

    def answer_query(
        self,
        query: str,
        k: int = 5,
        use_llm: bool = False
    ) -> Dict:
        """
        Answer a query using retrieved context.

        Args:
            query: User query
            k: Number of documents to retrieve
            use_llm: Whether to use LLM for answer generation (requires API key)

        Returns:
            Dict with query, context, and answer
        """
        documents, scores, metadata = self.vector_store.search(query, k)

        result = {
            "query": query,
            "retrieved_docs": len(documents),
            "documents": documents,
            "scores": scores,
            "metadata": metadata
        }

        if not documents:
            result["answer"] = "No relevant documents found in the knowledge base."
            return result

        # Build context from retrieved documents
        context_parts = []
        for doc, meta in zip(documents, metadata):
            source = meta.get("source", "Unknown")
            context_parts.append(f"From {source}: {doc}")

        result["context"] = "\n\n".join(context_parts)

        # Generate simple answer from context
        result["answer"] = f"Based on {len(documents)} relevant document(s): {documents[0][:200]}..."

        # TODO: Integrate with LLM (OpenAI/Gemini) for better answers
        if use_llm:
            result["answer"] = "[LLM integration coming soon]"

        return result

    def get_experiment_insights(
        self,
        experiment_number: int,
        k: int = 5
    ) -> Dict:
        """
        Get insights about a specific experiment.

        Args:
            experiment_number: Experiment number
            k: Number of results to return

        Returns:
            Dict with experiment insights
        """
        documents, scores, metadata = self.vector_store.search_by_experiment(
            experiment_number, k
        )

        return {
            "experiment": experiment_number,
            "documents_found": len(documents),
            "documents": documents,
            "scores": scores,
            "metadata": metadata
        }
