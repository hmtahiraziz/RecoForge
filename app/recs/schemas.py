"""
Pydantic schemas for recommendations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime

# User preference schemas

class Answers(BaseModel):
    """User questionnaire answers and preferences."""
    categories: Optional[List[str]] = None
    style: Optional[str] = None
    abv_band: Optional[Literal["low", "mid", "high"]] = None
    pack_size: Optional[int] = None
    brand_pref: Optional[List[str]] = None
    dietary: Optional[List[str]] = None
    nice_to_have: Optional[List[str]] = None
    ship_region: Optional[str] = None
    user_age: Optional[int] = Field(default=21, ge=0, le=120)

# Request/Response schemas

class RecReq(BaseModel):
    """Recommendation request."""
    query: str = Field(..., description="User's search query")
    answers: Answers = Field(..., description="User preferences and questionnaire answers")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of recommendations")

class RecommendationItem(BaseModel):
    """Individual recommendation item with enhanced product data."""
    sku: str = Field(..., description="Product SKU")
    title: str = Field(..., description="Product title")
    brand: str = Field(..., description="Product brand")
    category: str = Field(..., description="Product category")
    style: str = Field(..., description="Product style")
    abv: Optional[float] = Field(None, description="Alcohol by volume percentage")
    price: Optional[float] = Field(None, description="Product price")
    score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")
    reasons: List[str] = Field(..., description="Explanation reasons for recommendation")
    qty: int = Field(..., ge=1, description="Recommended quantity")

    # Enhanced product data from ProductService
    size: Optional[str] = Field(None, description="Product size")
    origin: Optional[str] = Field(None, description="Product origin")
    country: Optional[str] = Field(None, description="Product country")
    container: Optional[str] = Field(None, description="Container type")
    varietal: Optional[str] = Field(None, description="Wine varietal")

    # Pricing information
    wholesale_price: Optional[float] = Field(None, description="Wholesale price")
    retail_price: Optional[float] = Field(None, description="Retail price")
    discount_percentage: Optional[float] = Field(None, description="Current discount percentage")

    # Availability and inventory
    in_stock: bool = Field(True, description="Product availability")
    region_codes: List[str] = Field(default_factory=list, description="Available regions")

    # Trend and volatility data
    price_volatility: Optional[float] = Field(None, description="Price volatility score")
    trend_direction: Optional[str] = Field(None, description="Price trend (increasing/decreasing/stable)")
    is_trending: bool = Field(False, description="Whether product is trending")

class RecResponse(BaseModel):
    """Recommendation response."""
    query: str = Field(..., description="Original user query")
    items: List[RecommendationItem] = Field(..., description="Recommended items")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    subtotal: float = Field(..., ge=0.0, description="Total price of recommendations")
    total_items: int = Field(..., ge=0, description="Total number of items returned")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")

class SaveTemplate(BaseModel):
    """Template for saving user preferences."""
    name: str = Field(..., description="Template name")
    answers: Answers = Field(..., description="Saved user preferences")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Admin schemas

class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool = Field(..., description="Service health status")

class CatalogStats(BaseModel):
    """Catalog statistics response."""
    catalog_items: int = Field(..., description="Number of items in catalog")
    embeddings_count: int = Field(..., description="Number of embeddings")
    faiss_vectors: int = Field(..., description="Number of vectors in FAISS index")
    faiss_dimension: int = Field(..., description="Embedding dimension")
    index_type: str = Field(..., description="FAISS index type")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")

class RebuildIndexResponse(BaseModel):
    """Rebuild index response."""
    count: int = Field(..., description="Number of items processed")
    dim: int = Field(..., description="Embedding dimension")
    index_type: str = Field(..., description="FAISS index type")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")

class ReloadResponse(BaseModel):
    """Reload response."""
    success: bool = Field(..., description="Reload success status")
    message: str = Field(..., description="Reload status message")

# Legacy schemas (for backward compatibility)

class ProductContainer(BaseModel):
    size_ml: Optional[int] = None
    pack_count: int = 1
    format: str = "bottle"

class ProductInventory(BaseModel):
    status: str = "out_of_stock"
    region_codes: List[str] = []

class ProductCompliance(BaseModel):
    min_age: int = 18
    shipping_restrictions: List[str] = []

class CategoryHierarchy(BaseModel):
    level_1: str = ""
    level_2: str = ""
    level_3: str = ""
    level_4: str = ""

class NormalizedProduct(BaseModel):
    id: str
    sku: str
    title: str
    image: str
    brand: str
    category: CategoryHierarchy
    style: str
    abv: Optional[float] = None
    country: str
    region: str
    container: ProductContainer
    price: Optional[float] = None
    inventory: ProductInventory
    compliance: ProductCompliance
    tags: List[str] = []
    promo_ids: List[str] = []
