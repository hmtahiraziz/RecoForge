"""
Filtering service for recommendations.
"""

from typing import List, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class FilterService:
    """Service for filtering recommendation results with hard guardrails."""

    def __init__(self):
        self.filters = {}
        self._register_default_filters()

    def _register_default_filters(self):
        """Register default filter functions."""
        self.filters.update({
            'min_score': self._filter_by_min_score,
            'max_score': self._filter_by_max_score,
            'category': self._filter_by_category,
            'tags': self._filter_by_tags,
            'date_range': self._filter_by_date_range,
            'text_contains': self._filter_by_text_contains,
            'exclude_ids': self._filter_exclude_ids,
            'include_ids': self._filter_include_ids,
            # Hard guardrail filters
            'in_stock': self._filter_in_stock,
            'region_ok': self._filter_region_ok,
            'legal_ok': self._filter_legal_ok,
            'abv_band_ok': self._filter_abv_band_ok
        })

    def _filter_by_min_score(self, items: List[Dict[str, Any]], value: float) -> List[Dict[str, Any]]:
        """Filter items by minimum score."""
        return [item for item in items if item.get('score', 0) >= value]

    def _filter_by_max_score(self, items: List[Dict[str, Any]], value: float) -> List[Dict[str, Any]]:
        """Filter items by maximum score."""
        return [item for item in items if item.get('score', 0) <= value]

    def _filter_by_category(self, items: List[Dict[str, Any]], value: str) -> List[Dict[str, Any]]:
        """Filter items by category."""
        return [item for item in items
                if item.get('metadata', {}).get('category', '').lower() == value.lower()]

    def _filter_by_tags(self, items: List[Dict[str, Any]], value: List[str]) -> List[Dict[str, Any]]:
        """Filter items that have any of the specified tags."""
        if not value:
            return items

        value_lower = [tag.lower() for tag in value]
        return [item for item in items
                if any(tag.lower() in value_lower
                      for tag in item.get('metadata', {}).get('tags', []))]

    def _filter_by_date_range(self, items: List[Dict[str, Any]], value: Dict[str, str]) -> List[Dict[str, Any]]:
        """Filter items by date range."""
        from datetime import datetime

        start_date = value.get('start')
        end_date = value.get('end')

        if not start_date and not end_date:
            return items

        filtered_items = []
        for item in items:
            item_date = item.get('metadata', {}).get('date')
            if not item_date:
                continue

            try:
                item_dt = datetime.fromisoformat(item_date.replace('Z', '+00:00'))

                if start_date:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    if item_dt < start_dt:
                        continue

                if end_date:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if item_dt > end_dt:
                        continue

                filtered_items.append(item)

            except ValueError:
                logger.warning(f"Invalid date format: {item_date}")
                continue

        return filtered_items

    def _filter_by_text_contains(self, items: List[Dict[str, Any]], value: str) -> List[Dict[str, Any]]:
        """Filter items that contain the specified text."""
        if not value:
            return items

        value_lower = value.lower()
        return [item for item in items
                if value_lower in item.get('title', '').lower() or
                   value_lower in item.get('description', '').lower() or
                   value_lower in item.get('content', '').lower()]

    def _filter_exclude_ids(self, items: List[Dict[str, Any]], value: List[str]) -> List[Dict[str, Any]]:
        """Exclude items with specified IDs."""
        if not value:
            return items

        return [item for item in items if str(item.get('id', '')) not in value]

    def _filter_include_ids(self, items: List[Dict[str, Any]], value: List[str]) -> List[Dict[str, Any]]:
        """Include only items with specified IDs."""
        if not value:
            return items

        return [item for item in items if str(item.get('id', '')) in value]

    def apply_filters(self, items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply multiple filters to items."""
        if not filters:
            return items

        filtered_items = items

        for filter_name, filter_value in filters.items():
            if filter_name in self.filters:
                try:
                    filtered_items = self.filters[filter_name](filtered_items, filter_value)
                    logger.debug(f"Applied filter '{filter_name}': {len(filtered_items)} items remaining")
                except Exception as e:
                    logger.error(f"Error applying filter '{filter_name}': {e}")
                    continue
            else:
                logger.warning(f"Unknown filter: {filter_name}")

        return filtered_items

    def register_filter(self, name: str, filter_func: Callable):
        """Register a custom filter function."""
        self.filters[name] = filter_func
        logger.info(f"Registered custom filter: {name}")

    def get_available_filters(self) -> List[str]:
        """Get list of available filter names."""
        return list(self.filters.keys())

    # Hard guardrail filters

    def _filter_in_stock(self, items: List[Dict[str, Any]], value: bool = True) -> List[Dict[str, Any]]:
        """Filter items by stock availability."""
        if not value:
            return items

        return [item for item in items
                if item.get('metadata', {}).get('inventory', {}).get('status') == 'in_stock']

    def _filter_region_ok(self, items: List[Dict[str, Any]], ship_region: str) -> List[Dict[str, Any]]:
        """Filter items available in the shipping region."""
        if not ship_region:
            return items

        return [item for item in items
                if ship_region in item.get('metadata', {}).get('inventory', {}).get('region_codes', [])]

    def _filter_legal_ok(self, items: List[Dict[str, Any]], user_age: int) -> List[Dict[str, Any]]:
        """Filter items based on legal age requirements."""
        if not user_age or user_age < 0:
            return items

        min_age = 18  # Default minimum age for alcohol
        if user_age < min_age:
            # If user is underage, filter out all alcohol products
            return [item for item in items
                    if item.get('metadata', {}).get('compliance', {}).get('min_age', min_age) <= user_age]

        return items

    def _filter_abv_band_ok(self, items: List[Dict[str, Any]], abv_band: str) -> List[Dict[str, Any]]:
        """Filter items by ABV band preference."""
        if not abv_band:
            return items

        abv_bands = {
            'low': (0, 5),      # 0-5% ABV
            'medium': (5, 15),  # 5-15% ABV
            'high': (15, 25),   # 15-25% ABV
            'very_high': (25, 100)  # 25%+ ABV
        }

        if abv_band not in abv_bands:
            return items

        min_abv, max_abv = abv_bands[abv_band]

        return [item for item in items
                if (item_abv := item.get('metadata', {}).get('abv')) is not None and min_abv <= item_abv < max_abv]

    def apply_hard_filters(self, items: List[Dict[str, Any]],
                          ship_region: Optional[str] = None,
                          user_age: Optional[int] = None,
                          abv_band: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Apply hard guardrail filters to items.

        Args:
            items: List of candidate items
            ship_region: Shipping region code (e.g., 'AU-NSW')
            user_age: User's age for legal compliance
            abv_band: Preferred ABV band ('low', 'medium', 'high', 'very_high')

        Returns:
            Filtered list of items that pass all hard filters
        """
        filtered_items = items

        # Apply stock filter
        filtered_items = self._filter_in_stock(filtered_items, True)

        # Apply region filter
        if ship_region:
            filtered_items = self._filter_region_ok(filtered_items, ship_region)

        # Apply legal age filter
        if user_age is not None:
            filtered_items = self._filter_legal_ok(filtered_items, user_age)

        # Apply ABV band filter
        if abv_band:
            filtered_items = self._filter_abv_band_ok(filtered_items, abv_band)

        logger.info(f"Hard filters applied: {len(items)} -> {len(filtered_items)} items")

        return filtered_items
