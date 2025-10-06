"""
Text normalization service for recommendations.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Union

class NormalizeService:
    """Service for normalizing text data and liquor products."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text by removing extra whitespace, special characters, etc.
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)

        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')

        return text

    @staticmethod
    def clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize metadata fields.
        """
        if not metadata:
            return {}

        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, str):
                cleaned[key] = NormalizeService.normalize_text(value)
            elif isinstance(value, (int, float, bool)):
                cleaned[key] = value
            elif isinstance(value, list):
                cleaned[key] = [NormalizeService.normalize_text(str(item)) if isinstance(item, str) else item for item in value]
            else:
                cleaned[key] = str(value)

        return cleaned

    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text for indexing.
        """
        if not text:
            return []

        # Normalize text
        text = NormalizeService.normalize_text(text.lower())

        # Remove common stop words (basic list)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }

        # Extract words
        words = re.findall(r'\b\w+\b', text)

        # Filter by length and stop words
        keywords = [word for word in words if len(word) >= min_length and word not in stop_words]

        return list(set(keywords))  # Remove duplicates

    # Liquor product normalization helpers

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        """Convert value to float, return None if invalid."""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove common non-numeric characters
                cleaned = re.sub(r'[^\d.-]', '', value.strip())
                return float(cleaned) if cleaned else None
            return None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        """Convert value to int, return None if invalid."""
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                # Remove common non-numeric characters
                cleaned = re.sub(r'[^\d]', '', value.strip())
                return int(cleaned) if cleaned else None
            return None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_size_ml(value: Any) -> Optional[int]:
        """Parse size in milliliters from various formats."""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            # Assume it's already in ml if it's a reasonable number
            if 0 < value < 10000:  # Reasonable range for ml
                return int(value)
            return None

        if isinstance(value, str):
            value = value.lower().strip()

            # Handle common patterns
            # "750ml", "750 ml", "750mL"
            ml_match = re.search(r'(\d+(?:\.\d+)?)\s*ml', value)
            if ml_match:
                return int(float(ml_match.group(1)))

            # "1L", "1.5L", "1 L"
            l_match = re.search(r'(\d+(?:\.\d+)?)\s*l', value)
            if l_match:
                return int(float(l_match.group(1)) * 1000)

            # Just numbers - assume ml if reasonable
            num_match = re.search(r'(\d+(?:\.\d+)?)', value)
            if num_match:
                size = float(num_match.group(1))
                if 0 < size < 10000:
                    return int(size)

        return None

    @staticmethod
    def _infer_format(value: Any) -> str:
        """Infer container format from size and other attributes."""
        if not value:
            return "bottle"

        if isinstance(value, str):
            value = value.lower()

            # Check for explicit format indicators
            if any(word in value for word in ['can', 'tin']):
                return "can"
            if any(word in value for word in ['bottle', 'btl']):
                return "bottle"
            if any(word in value for word in ['keg', 'barrel']):
                return "keg"
            if any(word in value for word in ['box', 'cask']):
                return "box"
            if any(word in value for word in ['sachet', 'pouch']):
                return "sachet"

        # Default to bottle
        return "bottle"

    @staticmethod
    def _pack_count(value: Any) -> int:
        """Extract pack count from value."""
        if value is None:
            return 1

        if isinstance(value, (int, float)):
            return max(1, int(value))

        if isinstance(value, str):
            # Look for pack indicators
            pack_match = re.search(r'(\d+)\s*(?:pack|pk|pcs|pieces?)', value.lower())
            if pack_match:
                return int(pack_match.group(1))

            # Just numbers
            num_match = re.search(r'(\d+)', value)
            if num_match:
                count = int(num_match.group(1))
                return max(1, count)

        return 1

    @staticmethod
    def _collect_region_codes(raw: Dict[str, Any]) -> List[str]:
        """Map sold_at_* fields to region codes."""
        region_mapping = {
            'sold_at_adelaide': 'AU-SA',
            'sold_at_brisbane': 'AU-QLD',
            'sold_at_melbourne': 'AU-VIC',
            'sold_at_sydney': 'AU-NSW',
            'sold_at_perth': 'AU-WA',
            'sold_at_darwin': 'AU-NT',
            'sold_at_hobart': 'AU-TAS',
            'sold_at_canberra': 'AU-ACT'
        }

        region_codes = []
        for field, region_code in region_mapping.items():
            if field in raw:
                value = raw[field]
                # Check if the field indicates availability (1, '1', 'true', 'yes', etc.)
                if str(value).lower() in ['1', 'true', 'yes', 'y', 'available']:
                    region_codes.append(region_code)

        return region_codes

    @staticmethod
    def _infer_category(raw: Dict[str, Any]) -> Dict[str, str]:
        """Infer hierarchical product category structure."""
        # Initialize category structure
        category = {
            'level_1': '',
            'level_2': '',
            'level_3': '',
            'level_4': ''
        }

        # Check for explicit hierarchical category fields first
        for level in range(1, 5):
            field_name = f'category_level_{level}'
            if field_name in raw and raw[field_name]:
                category[f'level_{level}'] = str(raw[field_name]).strip()

        # If we have hierarchical categories, return them
        if any(category.values()):
            return category

        # Fallback: Check single category field
        if 'category' in raw and raw['category']:
            category_str = str(raw['category']).lower()
            if 'beer' in category_str:
                category['level_1'] = 'Beer'
            elif 'wine' in category_str:
                category['level_1'] = 'Wine'
            elif 'spirit' in category_str:
                category['level_1'] = 'Spirits'
            elif 'rtd' in category_str or 'ready' in category_str:
                category['level_1'] = 'RTD'
            elif 'mixer' in category_str:
                category['level_1'] = 'Mixers'
            else:
                category['level_1'] = str(raw['category']).strip()

        # If still no category, infer from product name/description
        if not category['level_1']:
            text_fields = ['name', 'title', 'description', 'product_name']
            text_content = ' '.join([
                str(raw.get(field, '')) for field in text_fields
                if raw.get(field)
            ]).lower()

        # RTD keywords (check first to catch "vodka cruiser" before "vodka")
        rtd_keywords = ['rtd', 'ready to drink', 'premix', 'cocktail', 'sour', 'cruiser', 'vodka cruiser']
        if any(keyword in text_content for keyword in rtd_keywords):
            category['level_1'] = 'RTD'
        # Wine keywords
        elif any(keyword in text_content for keyword in ['wine', 'chardonnay', 'shiraz', 'cabernet', 'pinot', 'merlot', 'sauvignon', 'riesling', 'champagne', 'sparkling']):
            category['level_1'] = 'Wine'
        # Spirits keywords
        elif any(keyword in text_content for keyword in ['whisky', 'whiskey', 'vodka', 'gin', 'rum', 'tequila', 'brandy', 'cognac', 'bourbon', 'scotch', 'liqueur']):
            category['level_1'] = 'Spirits'
        # Mixer keywords
        elif any(keyword in text_content for keyword in ['mixer', 'tonic', 'soda', 'juice', 'syrup', 'bitter']):
            category['level_1'] = 'Mixers'
        # Beer keywords
        elif any(keyword in text_content for keyword in ['beer', 'ale', 'lager', 'stout', 'porter', 'ipa', 'pilsner', 'draught']):
            category['level_1'] = 'Beer'
        else:
            category['level_1'] = 'Beer'  # Default

        return category

    @staticmethod
    def _infer_style(raw: Dict[str, Any]) -> str:
        """Infer product style from name and description."""
        text_fields = ['name', 'title', 'description', 'product_name', 'style']
        text_content = ' '.join([
            str(raw.get(field, '')) for field in text_fields
            if raw.get(field)
        ]).lower()

        # Common style patterns
        styles = {
            'IPA': ['ipa', 'india pale ale'],
            'Lager': ['lager', 'pilsner', 'pils'],
            'Stout': ['stout', 'porter'],
            'Ale': ['ale', 'pale ale', 'brown ale'],
            'Chardonnay': ['chardonnay', 'chard'],
            'Shiraz': ['shiraz', 'syrah'],
            'Cabernet': ['cabernet', 'cab sav'],
            'Pinot Noir': ['pinot noir', 'pinot'],
            'Merlot': ['merlot'],
            'Sauvignon Blanc': ['sauvignon blanc', 'sauv blanc'],
            'Riesling': ['riesling'],
            'Sparkling': ['sparkling', 'champagne', 'prosecco'],
            'Vodka': ['vodka'],
            'Whisky': ['whisky', 'whiskey', 'scotch', 'bourbon'],
            'Gin': ['gin'],
            'Rum': ['rum'],
            'Tequila': ['tequila'],
            'Brandy': ['brandy', 'cognac'],
            'Liqueur': ['liqueur', 'baileys', 'kahlua'],
            'RTD': ['rtd', 'ready to drink', 'premix'],
            'Tonic': ['tonic'],
            'Soda': ['soda', 'soft drink']
        }

        for style, keywords in styles.items():
            if any(keyword in text_content for keyword in keywords):
                return style

        return 'Standard'

    @staticmethod
    def _infer_brand(raw: Dict[str, Any]) -> str:
        """Infer brand from product name."""
        if 'brand' in raw and raw['brand']:
            return str(raw['brand']).strip()

        # Try to extract brand from name/title
        name_fields = ['name', 'title', 'product_name']
        for field in name_fields:
            if field in raw and raw[field]:
                name = str(raw[field]).strip()
                # Common pattern: "Brand Name Product"
                # Take first word or two as brand
                words = name.split()
                if len(words) >= 2:
                    # Check if first two words look like a brand
                    potential_brand = ' '.join(words[:2])
                    if len(potential_brand) <= 20:  # Reasonable brand name length
                        return potential_brand
                elif len(words) == 1:
                    return words[0]

        return 'Unknown'

    @staticmethod
    def normalize_product(raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw product data to standardized format.

        Args:
            raw: Raw product data dictionary

        Returns:
            Normalized product dictionary with standardized structure
        """
        # Generate ID from SKU or name
        product_id = raw.get('id') or raw.get('sku') or raw.get('name', '')
        if not product_id:
            # Generate from available fields
            name = raw.get('name') or raw.get('title') or 'unknown'
            product_id = f"prod_{hash(name) % 1000000}"

        # Collect region codes for inventory
        region_codes = NormalizeService._collect_region_codes(raw)

        # Determine inventory status
        inventory_status = 'in_stock' if region_codes else 'out_of_stock'

        # Get hierarchical category structure
        category_structure = NormalizeService._infer_category(raw)

        # Build normalized product
        normalized = {
            'id': str(product_id),
            'sku': str(raw.get('sku', '')),
            'title': str(raw.get('name') or raw.get('title') or raw.get('product_name', '')),
            'image': str(raw.get('image') or raw.get('image_url') or ''),
            'brand': NormalizeService._infer_brand(raw),
            'category': category_structure,
            'style': NormalizeService._infer_style(raw),
            'abv': NormalizeService._to_float(raw.get('abv') or raw.get('alcohol_content')),
            'country': str(raw.get('country') or 'Australia'),
            'region': str(raw.get('region') or ''),
            'container': {
                'size_ml': NormalizeService._parse_size_ml(raw.get('size') or raw.get('volume')),
                'pack_count': NormalizeService._pack_count(raw.get('pack_count') or raw.get('pack_size')),
                'format': NormalizeService._infer_format(raw.get('format') or raw.get('container_type') or raw.get('size'))
            },
            'price': None,  # Will be set by pricing service
            'inventory': {
                'status': inventory_status,
                'region_codes': region_codes
            },
            'compliance': {
                'min_age': 18,
                'shipping_restrictions': []
            },
            'tags': [],
            'promo_ids': []
        }

        # Add tags from various fields
        tags = []
        tag_fields = ['tags', 'keywords', 'type', 'subcategory']
        for field in tag_fields:
            if field in raw and raw[field]:
                if isinstance(raw[field], list):
                    tags.extend([str(tag).strip() for tag in raw[field] if tag])
                else:
                    tags.append(str(raw[field]).strip())

        # Add category levels and style as tags
        for level in ['level_1', 'level_2', 'level_3', 'level_4']:
            if normalized['category'][level]:
                tags.append(normalized['category'][level])
        if normalized['style'] and normalized['style'] != 'Standard':
            tags.append(normalized['style'])

        # Clean and deduplicate tags
        normalized['tags'] = list(set([tag for tag in tags if tag and len(tag) > 1]))

        return normalized
