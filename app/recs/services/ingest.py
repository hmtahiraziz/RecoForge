"""
Data ingestion service for recommendations.
"""

import json
import ijson
import orjson
from typing import List, Dict, Any, Iterator, Optional
from pathlib import Path
import logging
from datetime import datetime
import os
from .config import config
from .normalize import NormalizeService

logger = logging.getLogger(__name__)

class IngestService:
    """Service for ingesting data from various sources."""

    def __init__(self):
        self.normalizer = NormalizeService()
        self.output_dir = Path("/app/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.catalog_path = self.output_dir / "catalog.jsonl"
        self.manifest_path = self.output_dir / "manifest.json"

    def detect_file_format(self, file_path: Path) -> str:
        """
        Detect file format and determine parsing strategy.
        """
        suffix = file_path.suffix.lower()

        if suffix in ['.jsonl', '.ndjson']:
            return 'jsonl'
        elif suffix == '.json':
            # Check if it's a large file that needs streaming
            try:
                file_size = file_path.stat().st_size
                if file_size > 100 * 1024 * 1024:  # 100MB threshold
                    return 'large_json'
                else:
                    return 'json'
            except OSError:
                return 'json'
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def load_jsonl(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Load data from JSONL/NDJSON file line by line.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        yield data
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
        except FileNotFoundError:
            logger.error(f"Source file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSONL file {file_path}: {e}")
            raise

    def load_json(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Load data from small JSON file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                yield data

        except FileNotFoundError:
            logger.error(f"Source file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            raise

    def load_large_json(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """
        Load large JSON file using streaming parser (ijson).
        """
        try:
            with open(file_path, 'rb') as file:
                # Parse as array of objects
                parser = ijson.items(file, 'item')
                for item in parser:
                    yield item

        except FileNotFoundError:
            logger.error(f"Source file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading large JSON file {file_path}: {e}")
            raise

    def get_source_data(self, source_path: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """
        Get data from configured source with format detection.
        """
        if source_path is None:
            source_path = config.rec_source_json

        source_file = Path(source_path)

        if not source_file.exists():
            logger.warning(f"Source file does not exist: {source_file}")
            return iter([])

        file_format = self.detect_file_format(source_file)
        logger.info(f"Detected file format: {file_format} for {source_file}")

        if file_format == 'jsonl':
            return self.load_jsonl(str(source_file))
        elif file_format == 'json':
            return self.load_json(str(source_file))
        elif file_format == 'large_json':
            return self.load_large_json(str(source_file))
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def validate_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate that an item has required fields.
        """
        # Check for at least one identifier field
        identifier_fields = ['id', 'sku', 'name', 'title', 'product_name']
        return any(field in item and item[field] for field in identifier_fields)

    def normalize_and_write(self, source_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Stream source data, normalize each item, and write to catalog.jsonl.
        """
        logger.info("Starting ingestion process...")

        # Initialize counters
        total_processed = 0
        total_written = 0
        errors = []

        # Get source data iterator
        source_data = self.get_source_data(source_path)

        # Open output file for writing
        with open(self.catalog_path, 'wb') as output_file:
            for raw_item in source_data:
                total_processed += 1

                try:
                    # Validate item
                    if not self.validate_item(raw_item):
                        logger.warning(f"Skipping invalid item at position {total_processed}")
                        continue

                    # Normalize the item
                    normalized_item = self.normalizer.normalize_product(raw_item)

                    # Write as compact JSON line using orjson
                    json_line = orjson.dumps(normalized_item)
                    output_file.write(json_line + b'\n')

                    total_written += 1

                    # Log progress every 1000 items
                    if total_written % 1000 == 0:
                        logger.info(f"Processed {total_written} items...")

                except Exception as e:
                    error_msg = f"Error processing item at position {total_processed}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

        # Generate manifest
        manifest = {
            'fetched_at': datetime.utcnow().isoformat(),
            'count': total_written,
            'total_processed': total_processed,
            'errors': len(errors),
            'source_file': str(source_path or config.rec_source_json),
            'output_file': str(self.catalog_path)
        }

        # Write manifest
        with open(self.manifest_path, 'wb') as manifest_file:
            manifest_file.write(orjson.dumps(manifest))

        logger.info(f"Ingestion completed: {total_written} items written to {self.catalog_path}")
        logger.info(f"Manifest written to {self.manifest_path}")

        if errors:
            logger.warning(f"Encountered {len(errors)} errors during processing")

        return manifest

    def get_manifest(self) -> Optional[Dict[str, Any]]:
        """
        Read and return the current manifest.
        """
        if not self.manifest_path.exists():
            return None

        try:
            with open(self.manifest_path, 'rb') as f:
                return orjson.loads(f.read())
        except Exception as e:
            logger.error(f"Error reading manifest: {e}")
            return None

    def get_catalog_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the catalog file.
        """
        if not self.catalog_path.exists():
            return {'exists': False}

        try:
            file_size = self.catalog_path.stat().st_size
            line_count = 0

            with open(self.catalog_path, 'rb') as f:
                for _ in f:
                    line_count += 1

            return {
                'exists': True,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'line_count': line_count
            }
        except Exception as e:
            logger.error(f"Error getting catalog stats: {e}")
            return {'exists': False, 'error': str(e)}
