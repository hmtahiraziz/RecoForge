"""
OpenAI embedding service for recommendations.
"""

import numpy as np
import faiss
import orjson
from typing import List, Dict, Any, Optional, Iterator
import openai
import logging
import time
import math
from pathlib import Path
from .config import config

logger = logging.getLogger(__name__)

class EmbedOpenAIService:
    """Service for creating embeddings using OpenAI API and building FAISS indices."""

    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

        # Initialize OpenAI client - only pass organization if it's set
        client_kwargs = {"api_key": config.openai_api_key}
        if config.openai_org_id and config.openai_org_id.strip():
            client_kwargs["organization"] = config.openai_org_id

        self.client = openai.OpenAI(**client_kwargs)
        self.model = config.embedding_model
        self.batch_size = config.rec_embed_batch

        # Set embedding dimension based on model
        if 'text-embedding-3-large' in self.model:
            self.dimension = 3072
        elif 'text-embedding-3-small' in self.model:
            self.dimension = 1536
        else:
            self.dimension = 1536  # Default for older models

        # Setup paths
        self.index_dir = Path("/app/index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_path = self.index_dir / "embeddings.npy"
        self.faiss_index_path = self.index_dir / "faiss.index"
        self.id_map_path = self.index_dir / "id_map.jsonl"
        self.meta_path = self.index_dir / "meta.jsonl"

    def prepare_text_for_embedding(self, item: Dict[str, Any]) -> str:
        """
        Prepare text from item for embedding using the specified format.
        Format: "{category}; {style}; brand {brand}; title {title}; {country or ''} {region or ''}; {pack_count}x{size_ml}ml; abv {abv}%; tags {','.join(tags)}"
        """
        # Extract category information
        category = item.get('category', {})
        if isinstance(category, dict):
            category_str = category.get('level_1', '')
        else:
            category_str = str(category) if category else ''

        # Extract other fields
        style = item.get('style', '')
        brand = item.get('brand', '')
        title = item.get('title', '')
        country = item.get('country', '')
        region = item.get('region', '')

        # Extract container information
        container = item.get('container', {})
        pack_count = container.get('pack_count', 1)
        size_ml = container.get('size_ml', '')

        # Extract ABV
        abv = item.get('abv', '')

        # Extract tags
        tags = item.get('tags', [])
        tags_str = ','.join(tags) if tags else ''

        # Build the formatted text
        parts = []

        if category_str:
            parts.append(category_str)

        if style:
            parts.append(style)

        if brand:
            parts.append(f"brand {brand}")

        if title:
            parts.append(f"title {title}")

        location_parts = []
        if country:
            location_parts.append(country)
        if region:
            location_parts.append(region)
        if location_parts:
            parts.append(' '.join(location_parts))

        if pack_count and size_ml:
            parts.append(f"{pack_count}x{size_ml}ml")

        if abv:
            parts.append(f"abv {abv}%")

        if tags_str:
            parts.append(f"tags {tags_str}")

        return "; ".join(parts)

    def create_embeddings_batch(self, texts: List[str], max_retries: int = 3) -> List[List[float]]:
        """
        Create embeddings for a batch of texts with rate limiting and backoff.
        """
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    encoding_format="float"
                )

                return [item.embedding for item in response.data]

            except openai.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error creating batch embeddings: {e}")
                raise

    def load_catalog_data(self, catalog_path: str = "/app/data/catalog.jsonl") -> Iterator[Dict[str, Any]]:
        """
        Load normalized product data from catalog.jsonl.
        """
        catalog_file = Path(catalog_path)
        if not catalog_file.exists():
            logger.error(f"Catalog file not found: {catalog_path}")
            return iter([])

        with open(catalog_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    item = orjson.loads(line)
                    yield item
                except Exception as e:
                    logger.warning(f"Error parsing line {line_num}: {e}")
                    continue

    def process_embeddings(self, catalog_path: str = "/app/data/catalog.jsonl") -> Dict[str, Any]:
        """
        Process all products to create embeddings and build FAISS index.
        """
        logger.info("Starting embeddings processing...")

        # Load catalog data
        catalog_data = list(self.load_catalog_data(catalog_path))
        total_items = len(catalog_data)

        if total_items == 0:
            logger.warning("No items found in catalog")
            return {'total_items': 0, 'processed': 0, 'errors': 0}

        logger.info(f"Processing {total_items} items for embeddings")

        # Initialize arrays for storage
        embeddings_list = []
        id_map = []
        meta_list = []

        processed = 0
        errors = 0

        # Process in batches
        for i in range(0, total_items, self.batch_size):
            batch = catalog_data[i:i + self.batch_size]
            batch_texts = []
            batch_items = []

            # Prepare texts for this batch
            for item in batch:
                try:
                    text = self.prepare_text_for_embedding(item)
                    batch_texts.append(text)
                    batch_items.append(item)
                except Exception as e:
                    logger.warning(f"Error preparing text for item {item.get('id', 'unknown')}: {e}")
                    errors += 1
                    continue

            if not batch_texts:
                continue

            try:
                # Create embeddings for this batch
                logger.info(f"Processing batch {i//self.batch_size + 1}/{(total_items + self.batch_size - 1)//self.batch_size}")
                batch_embeddings = self.create_embeddings_batch(batch_texts)

                # Store results
                for item, embedding in zip(batch_items, batch_embeddings):
                    embeddings_list.append(embedding)
                    id_map.append({
                        'id': item.get('id', ''),
                        'sku': item.get('sku', ''),
                        'title': item.get('title', '')
                    })
                    meta_list.append({
                        'id': item.get('id', ''),
                        'title': item.get('title', ''),
                        'brand': item.get('brand', ''),
                        'category': item.get('category', {}),
                        'style': item.get('style', ''),
                        'abv': item.get('abv'),
                        'inventory': item.get('inventory', {})
                    })
                    processed += 1

                # Small delay to be respectful to API
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error processing batch {i//self.batch_size + 1}: {e}")
                errors += len(batch_texts)
                continue

        if not embeddings_list:
            logger.error("No embeddings were created")
            return {'total_items': total_items, 'processed': 0, 'errors': errors}

        # Convert to numpy array and save
        embeddings_array = np.array(embeddings_list, dtype=np.float32)

        # Save embeddings using memmap
        logger.info(f"Saving {len(embeddings_array)} embeddings to {self.embeddings_path}")
        np.save(self.embeddings_path, embeddings_array)

        # Build FAISS index
        logger.info("Building FAISS index...")
        self.build_faiss_index(embeddings_array)

        # Save metadata files
        self.save_metadata_files(id_map, meta_list)

        logger.info(f"Embeddings processing completed: {processed} items processed, {errors} errors")

        return {
            'total_items': total_items,
            'processed': processed,
            'errors': errors,
            'embeddings_file': str(self.embeddings_path),
            'faiss_index': str(self.faiss_index_path),
            'id_map': str(self.id_map_path),
            'meta': str(self.meta_path)
        }

    def build_faiss_index(self, embeddings: np.ndarray):
        """
        Build FAISS index based on the number of vectors.
        """
        n_vectors = len(embeddings)
        dimension = embeddings.shape[1]

        logger.info(f"Building FAISS index for {n_vectors} vectors of dimension {dimension}")

        if n_vectors > 300000:
            # Use IndexIVFFlat for large datasets
            nlist = min(16384, max(1024, int(math.sqrt(n_vectors)) * 4))
            logger.info(f"Using IndexIVFFlat with nlist={nlist}")

            # Create quantizer
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

            # Train the index
            logger.info("Training IndexIVFFlat...")
            index.train(embeddings)

        else:
            # Use IndexHNSWFlat for smaller datasets
            logger.info("Using IndexHNSWFlat with M=32, efConstruction=200")
            index = faiss.IndexHNSWFlat(dimension, 32)
            index.hnsw.efConstruction = 200

        # Add vectors to index
        logger.info("Adding vectors to index...")
        index.add(embeddings)

        # Save index
        faiss.write_index(index, str(self.faiss_index_path))
        logger.info(f"FAISS index saved to {self.faiss_index_path}")

    def save_metadata_files(self, id_map: List[Dict[str, Any]], meta_list: List[Dict[str, Any]]):
        """
        Save ID map and metadata files.
        """
        # Save ID map
        logger.info(f"Saving ID map to {self.id_map_path}")
        with open(self.id_map_path, 'wb') as f:
            for item in id_map:
                f.write(orjson.dumps(item) + b'\n')

        # Save metadata
        logger.info(f"Saving metadata to {self.meta_path}")
        with open(self.meta_path, 'wb') as f:
            for item in meta_list:
                f.write(orjson.dumps(item) + b'\n')

    def load_faiss_index(self) -> Optional[faiss.Index]:
        """
        Load the FAISS index from disk.
        """
        if not self.faiss_index_path.exists():
            logger.warning(f"FAISS index not found: {self.faiss_index_path}")
            return None

        try:
            index = faiss.read_index(str(self.faiss_index_path))
            logger.info(f"Loaded FAISS index with {index.ntotal} vectors")
            return index
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            return None

    def search_similar(self, query_embedding: List[float], k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar items using the FAISS index.
        """
        index = self.load_faiss_index()
        if index is None:
            return []

        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)

        # Search
        scores, indices = index.search(query_array, min(k, index.ntotal))

        # Load results
        results = []
        id_map = self.load_id_map()
        meta_list = self.load_metadata()

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            if idx < len(id_map) and idx < len(meta_list):
                result = {
                    'id': id_map[idx].get('id'),
                    'sku': id_map[idx].get('sku'),
                    'title': id_map[idx].get('title'),
                    'score': float(score),
                    'metadata': meta_list[idx]
                }
                results.append(result)

        return results

    def load_id_map(self) -> List[Dict[str, Any]]:
        """
        Load the ID map from disk.
        """
        if not self.id_map_path.exists():
            return []

        id_map = []
        with open(self.id_map_path, 'rb') as f:
            for line in f:
                try:
                    item = orjson.loads(line)
                    id_map.append(item)
                except Exception as e:
                    logger.warning(f"Error parsing ID map line: {e}")
                    continue

        return id_map

    def load_metadata(self) -> List[Dict[str, Any]]:
        """
        Load metadata from disk.
        """
        if not self.meta_path.exists():
            return []

        meta_list = []
        with open(self.meta_path, 'rb') as f:
            for line in f:
                try:
                    item = orjson.loads(line)
                    meta_list.append(item)
                except Exception as e:
                    logger.warning(f"Error parsing metadata line: {e}")
                    continue

        return meta_list

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current index.
        """
        stats = {
            'embeddings_exists': self.embeddings_path.exists(),
            'faiss_index_exists': self.faiss_index_path.exists(),
            'id_map_exists': self.id_map_path.exists(),
            'meta_exists': self.meta_path.exists()
        }

        if self.embeddings_path.exists():
            embeddings = np.load(self.embeddings_path)
            stats['embeddings_shape'] = embeddings.shape
            stats['embeddings_size_mb'] = round(embeddings.nbytes / (1024 * 1024), 2)

        if self.faiss_index_path.exists():
            try:
                index = faiss.read_index(str(self.faiss_index_path))
                stats['faiss_vectors'] = index.ntotal
                stats['faiss_dimension'] = index.d
            except Exception as e:
                stats['faiss_error'] = str(e)

        if self.id_map_path.exists():
            id_map = self.load_id_map()
            stats['id_map_count'] = len(id_map)

        if self.meta_path.exists():
            meta_list = self.load_metadata()
            stats['meta_count'] = len(meta_list)

        return stats
