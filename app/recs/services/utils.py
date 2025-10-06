"""
Utility functions for recommendations.
"""

import hashlib
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UtilsService:
    """Utility service for recommendations."""

    @staticmethod
    def generate_id(item: Dict[str, Any]) -> str:
        """Generate a unique ID for an item."""
        # Use title and content to generate a hash
        content = f"{item.get('title', '')}{item.get('content', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """Calculate simple text similarity using Jaccard similarity."""
        if not text1 or not text2:
            return 0.0

        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def format_timestamp(timestamp: Optional[datetime] = None) -> str:
        """Format timestamp for logging."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        return timestamp.isoformat()

    @staticmethod
    def safe_json_dumps(data: Any) -> str:
        """Safely serialize data to JSON."""
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error serializing to JSON: {e}")
            return "{}"

    @staticmethod
    def safe_json_loads(json_str: str) -> Any:
        """Safely deserialize JSON string."""
        try:
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error deserializing JSON: {e}")
            return {}

    @staticmethod
    def truncate_text(text: str, max_length: int = 200) -> str:
        """Truncate text to specified length."""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    @staticmethod
    def extract_metadata_keys(items: List[Dict[str, Any]]) -> List[str]:
        """Extract all unique metadata keys from items."""
        keys = set()
        for item in items:
            metadata = item.get('metadata', {})
            if isinstance(metadata, dict):
                keys.update(metadata.keys())
        return sorted(list(keys))

    @staticmethod
    def validate_item_structure(item: Dict[str, Any]) -> bool:
        """Validate that item has required structure."""
        required_fields = ['title']

        for field in required_fields:
            if field not in item or not item[field]:
                return False

        return True
