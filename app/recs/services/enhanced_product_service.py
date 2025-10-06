"""
Enhanced product service that integrates with ProductService for rich product data.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class EnhancedProductService:
    """Service for enriching recommendation data with ProductService insights."""

    def __init__(self, db_session=None):
        self.db_session = db_session

    def enrich_recommendation_items(self,
                                  faiss_hits: List[Dict[str, Any]],
                                  include_pricing: bool = True,
                                  include_trends: bool = True) -> List[Dict[str, Any]]:
        """
        Enrich FAISS hits with additional product data from ProductService.

        Args:
            faiss_hits: List of items from FAISS search
            include_pricing: Whether to include pricing information
            include_trends: Whether to include trend analysis

        Returns:
            List of enriched recommendation items
        """
        enriched_items = []

        for hit in faiss_hits:
            try:
                enriched_item = self._enrich_single_item(hit, include_pricing, include_trends)
                enriched_items.append(enriched_item)
            except Exception as e:
                logger.warning(f"Failed to enrich item {hit.get('id', 'unknown')}: {e}")
                # Return original item if enrichment fails
                enriched_items.append(hit)

        return enriched_items

    def _enrich_single_item(self,
                           item: Dict[str, Any],
                           include_pricing: bool = True,
                           include_trends: bool = True) -> Dict[str, Any]:
        """Enrich a single recommendation item with additional data."""

        # Start with the original item
        enriched = item.copy()

        # Add enhanced product data if available
        metadata = item.get('metadata', {})

        # Enhanced product attributes
        enriched.update({
            'size': metadata.get('size'),
            'origin': metadata.get('origin'),
            'country': metadata.get('country'),
            'container': metadata.get('container'),
            'varietal': metadata.get('varietal'),
        })

        # Pricing information
        if include_pricing:
            pricing_data = self._get_pricing_data(item)
            enriched.update(pricing_data)

        # Trend analysis
        if include_trends:
            trend_data = self._get_trend_data(item)
            enriched.update(trend_data)

        # Availability information
        inventory = metadata.get('inventory', {})
        enriched.update({
            'in_stock': inventory.get('status') == 'in_stock',
            'region_codes': inventory.get('region_codes', [])
        })

        return enriched

    def _get_pricing_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pricing information from item data."""
        pricing_data = {
            'wholesale_price': None,
            'retail_price': None,
            'discount_percentage': None
        }

        # Try to extract pricing from various sources
        metadata = item.get('metadata', {})

        # Check for wholesale prices in paramount_wholesale_prices
        wholesale_prices = metadata.get('paramount_wholesale_prices', {})
        if isinstance(wholesale_prices, dict):
            # Try to get unit or case wholesale price
            pricing_data['wholesale_price'] = (
                wholesale_prices.get('unit') or
                wholesale_prices.get('case') or
                wholesale_prices.get('unit_price_before_discount_ex_gst') or
                wholesale_prices.get('case_price_before_discount_ex_gst')
            )

        # Check for retail prices
        retail_prices = metadata.get('paramount_prices', {})
        if isinstance(retail_prices, dict):
            pricing_data['retail_price'] = (
                retail_prices.get('unit') or
                retail_prices.get('case') or
                retail_prices.get('price')
            )

        # Calculate discount percentage if both wholesale and retail prices exist
        if pricing_data['wholesale_price'] and pricing_data['retail_price']:
            try:
                wholesale = float(pricing_data['wholesale_price'])
                retail = float(pricing_data['retail_price'])
                if retail > 0:
                    discount = ((retail - wholesale) / retail) * 100
                    pricing_data['discount_percentage'] = round(discount, 2)
            except (ValueError, TypeError):
                pass

        return pricing_data

    def _get_trend_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract trend and volatility information from item data."""
        trend_data = {
            'price_volatility': None,
            'trend_direction': 'stable',
            'is_trending': False
        }

        # For now, we'll use mock trend data
        # In a real implementation, this would query the ProductService
        # for historical price data and calculate actual trends

        # Mock trend analysis based on product characteristics
        metadata = item.get('metadata', {})
        category = metadata.get('category', {}).get('level_1', '').lower()
        brand = metadata.get('brand', '').lower()

        # Simple heuristic for trending products
        trending_brands = ['weihenstephaner', 'guinness', 'corona', 'heineken']
        trending_categories = ['beer', 'wine']

        if any(trending_brand in brand for trending_brand in trending_brands):
            trend_data['is_trending'] = True
            trend_data['trend_direction'] = 'increasing'
            trend_data['price_volatility'] = 15.5  # Mock volatility score

        elif category in trending_categories:
            trend_data['is_trending'] = True
            trend_data['trend_direction'] = 'stable'
            trend_data['price_volatility'] = 8.2  # Mock volatility score

        return trend_data

    def get_price_volatility_insights(self, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get price volatility insights for multiple products.

        Args:
            product_ids: List of product IDs to analyze

        Returns:
            Dictionary mapping product_id to volatility insights
        """
        insights = {}

        for product_id in product_ids:
            # Mock volatility analysis
            # In real implementation, this would use ProductService.get_price_volatility_index_with_filters
            insights[product_id] = {
                'volatility_score': 12.5,  # Mock score
                'trend_direction': 'stable',
                'price_stability': 'high',
                'recommendation': 'stable_price'
            }

        return insights

    def get_discount_insights(self, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get discount insights for multiple products.

        Args:
            product_ids: List of product IDs to analyze

        Returns:
            Dictionary mapping product_id to discount insights
        """
        insights = {}

        for product_id in product_ids:
            # Mock discount analysis
            # In real implementation, this would use ProductService.get_discount_index_with_filters
            insights[product_id] = {
                'discount_frequency': 25.0,  # Mock percentage
                'average_discount': 15.0,    # Mock percentage
                'best_discount_period': 'weekend',
                'recommendation': 'wait_for_discount'
            }

        return insights

    def filter_by_price_range(self,
                            items: List[Dict[str, Any]],
                            min_price: Optional[float] = None,
                            max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Filter items by price range.

        Args:
            items: List of items to filter
            min_price: Minimum price threshold
            max_price: Maximum price threshold

        Returns:
            Filtered list of items
        """
        if min_price is None and max_price is None:
            return items

        filtered_items = []

        for item in items:
            # Get price from various sources
            price = (
                item.get('price') or
                item.get('retail_price') or
                item.get('wholesale_price')
            )

            if price is None:
                # Include items without price if no price filter is applied
                if min_price is None:
                    filtered_items.append(item)
                continue

            try:
                price_float = float(price)

                # Apply price filters
                if min_price is not None and price_float < min_price:
                    continue
                if max_price is not None and price_float > max_price:
                    continue

                filtered_items.append(item)

            except (ValueError, TypeError):
                # Include items with invalid prices if no price filter is applied
                if min_price is None:
                    filtered_items.append(item)
                continue

        return filtered_items

    def sort_by_value_score(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort items by value score (quality/price ratio).

        Args:
            items: List of items to sort

        Returns:
            Sorted list of items by value score
        """
        def calculate_value_score(item):
            try:
                # Get price and quality indicators
                price = (
                    item.get('price') or
                    item.get('retail_price') or
                    item.get('wholesale_price')
                )

                if price is None or price <= 0:
                    return 0.0

                # Quality indicators
                quality_score = 0.0

                # Brand reputation (mock scoring)
                brand = item.get('brand', '').lower()
                premium_brands = ['weihenstephaner', 'guinness', 'corona', 'heineken', 'stella artois']
                if any(premium_brand in brand for premium_brand in premium_brands):
                    quality_score += 20

                # Category quality
                category = item.get('category', '').lower()
                if 'premium' in category or 'craft' in category:
                    quality_score += 15

                # ABV quality (higher ABV often indicates premium)
                abv = item.get('abv', 0)
                if abv and abv > 5.0:
                    quality_score += 10

                # Discount bonus
                discount = item.get('discount_percentage', 0)
                if discount and discount > 10:
                    quality_score += float(discount)

                # Calculate value score (quality per dollar)
                value_score = quality_score / float(price)
                return value_score

            except (ValueError, TypeError, ZeroDivisionError):
                return 0.0

        # Sort by value score (descending)
        return sorted(items, key=calculate_value_score, reverse=True)

    def get_recommendation_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate insights about the recommendation set.

        Args:
            items: List of recommended items

        Returns:
            Dictionary with recommendation insights
        """
        if not items:
            return {
                'total_items': 0,
                'price_range': {'min': 0, 'max': 0, 'avg': 0},
                'categories': {},
                'trending_items': 0,
                'discounted_items': 0,
                'value_recommendations': []
            }

        # Calculate price statistics
        prices = []
        for item in items:
            price = item.get('price') or item.get('retail_price') or item.get('wholesale_price')
            if price is not None:
                try:
                    prices.append(float(price))
                except (ValueError, TypeError):
                    pass

        price_stats = {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'avg': statistics.mean(prices) if prices else 0
        }

        # Count categories
        categories = {}
        for item in items:
            category = item.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1

        # Count trending and discounted items
        trending_count = sum(1 for item in items if item.get('is_trending', False))
        discounted_count = sum(1 for item in items if item.get('discount_percentage') and item.get('discount_percentage', 0) > 0)

        # Get top value recommendations
        value_items = self.sort_by_value_score(items)[:3]
        value_recommendations = [
            {
                'sku': item.get('sku', ''),
                'title': item.get('title', ''),
                'value_score': item.get('value_score', 0)
            }
            for item in value_items
        ]

        return {
            'total_items': len(items),
            'price_range': price_stats,
            'categories': categories,
            'trending_items': trending_count,
            'discounted_items': discounted_count,
            'value_recommendations': value_recommendations
        }
