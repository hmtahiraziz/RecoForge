"""
FAISS index service for recommendations.
"""

import numpy as np
import faiss
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from .config import config

logger = logging.getLogger(__name__)

class IndexService:
    """Service for managing FAISS index for recommendations."""

    def __init__(self):
        self.index_path = Path(config.index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.index = None
        self.metadata = []
        self.dimension = config.embedding_dimension

        self._load_index()

    def _load_index(self):
        """Load existing index or create new one."""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.pkl"

        if index_file.exists() and metadata_file.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))

                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)

                logger.info(f"Loaded index with {self.index.ntotal} vectors")

            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        # Use IndexFlatIP for cosine similarity (after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        logger.info("Created new FAISS index")

    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings for cosine similarity."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return embeddings / norms

    def add_embeddings(self, items: List[Dict[str, Any]]):
        """Add embeddings to the index."""
        if not items:
            return

        embeddings = []
        metadata_batch = []

        for item in items:
            if 'embedding' in item:
                embeddings.append(item['embedding'])

                # Store metadata
                metadata = {
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'content': item.get('content', ''),
                    'metadata': item.get('metadata', {}),
                    'embedding_text': item.get('embedding_text', '')
                }
                metadata_batch.append(metadata)

        if not embeddings:
            logger.warning("No embeddings found in items")
            return

        # Convert to numpy array and normalize
        embeddings_array = np.array(embeddings, dtype=np.float32)
        normalized_embeddings = self._normalize_embeddings(embeddings_array)

        # Add to index
        self.index.add(normalized_embeddings)
        self.metadata.extend(metadata_batch)

        logger.info(f"Added {len(embeddings)} embeddings to index")

    def search(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar items."""
        if self.index is None or self.index.ntotal == 0:
            return []

        # Normalize query embedding
        query_array = np.array([query_embedding], dtype=np.float32)
        normalized_query = self._normalize_embeddings(query_array)

        # Search
        scores, indices = self.index.search(normalized_query, min(limit, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(score)
                results.append(result)

        return results

    def search_by_text(self, query_text: str, limit: int = 10, embed_service=None) -> List[Dict[str, Any]]:
        """Search using text query (requires embedding service)."""
        if embed_service is None:
            logger.error("Embedding service required for text search")
            return []

        try:
            # Create embedding for query
            query_embedding = embed_service.create_embedding(query_text)
            return self.search(query_embedding, limit)
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []

    def save_index(self):
        """Save index and metadata to disk."""
        try:
            index_file = self.index_path / "index.faiss"
            metadata_file = self.index_path / "metadata.pkl"

            # Save FAISS index
            faiss.write_index(self.index, str(index_file))

            # Save metadata
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)

            logger.info(f"Saved index with {self.index.ntotal} vectors")

        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None,
            'metadata_count': len(self.metadata)
        }

    def rebuild_index(self, items: List[Dict[str, Any]]):
        """Rebuild the entire index from scratch."""
        logger.info("Rebuilding index...")

        # Create new index
        self._create_new_index()

        # Add all items
        self.add_embeddings(items)

        # Save
        self.save_index()

        logger.info(f"Rebuilt index with {len(items)} items")

    def clear_index(self):
        """Clear the index."""
        self._create_new_index()
        self.save_index()
        logger.info("Cleared index")
