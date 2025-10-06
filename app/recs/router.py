"""
FastAPI router for recommendations with secure admin endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import List, Dict, Any, Optional
import logging
import time
import jwt
from datetime import datetime
from pathlib import Path
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    RecReq, RecResponse, RecommendationItem, HealthResponse,
    CatalogStats, RebuildIndexResponse, ReloadResponse, SaveTemplate
)
from .services.embed_openai import EmbedOpenAIService
from .services.filters import FilterService
from .services.rank_gpt import RankGPTService
from .services.ingest import IngestService
from .services.template_service import TemplateService
from .services.enhanced_product_service import EnhancedProductService
from .services.config import config
from .models import ActionType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recs", tags=["recommendations"])

# Initialize services
embed_service = EmbedOpenAIService()
filter_service = FilterService()
rank_service = RankGPTService()
ingest_service = IngestService()
enhanced_product_service = EnhancedProductService()

# Database session dependency (simplified for demo)
async def get_db_session() -> AsyncSession:
    """Get database session (simplified for demo)."""
    # In real implementation, this would get the actual database session
    # For now, we'll return None and handle it in the service
    return None

# JWT dependency for admin routes
async def verify_admin_token(authorization: str = Header(None)):
    """Verify admin token for protected routes."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1]

        # Verify JWT token using JWT secret key
        import os
        jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])

        # Check if user has SUPERADMIN role
        if payload.get("role") != "SUPERADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="SUPERADMIN role required"
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

# Health endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(ok=True)

# Catalog stats endpoint
@router.get("/catalog/stats", response_model=CatalogStats)
async def get_catalog_stats():
    """Get catalog and index statistics."""
    try:
        # Get manifest stats
        manifest = ingest_service.get_manifest()
        catalog_items = manifest.get('count', 0) if manifest else 0
        last_updated = manifest.get('fetched_at') if manifest else None

        # Get index stats
        index_stats = embed_service.get_index_stats()
        embeddings_count = index_stats.get('embeddings_shape', [0, 0])[0] if index_stats.get('embeddings_shape') else 0
        faiss_vectors = index_stats.get('faiss_vectors', 0)
        faiss_dimension = index_stats.get('faiss_dimension', 0)

        # Determine index type
        index_type = "Unknown"
        if faiss_vectors > 300000:
            index_type = "IndexIVFFlat"
        elif faiss_vectors > 0:
            index_type = "IndexHNSWFlat"

        return CatalogStats(
            catalog_items=catalog_items,
            embeddings_count=embeddings_count,
            faiss_vectors=faiss_vectors,
            faiss_dimension=faiss_dimension,
            index_type=index_type,
            last_updated=last_updated
        )

    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting catalog stats: {str(e)}"
        )

# Admin endpoints (require SUPERADMIN role)

@router.post("/admin/rebuild-index", response_model=RebuildIndexResponse)
async def rebuild_index(admin_user: dict = Depends(verify_admin_token)):
    """Rebuild the entire index (ingest + embeddings)."""
    try:
        start_time = time.time()

        logger.info("Starting index rebuild...")

        # Step 1: Run ingestion (Part 3)
        logger.info("Running ingestion...")
        ingest_result = ingest_service.normalize_and_write()

        if ingest_result['count'] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No items were ingested"
            )

        # Step 2: Run embeddings (Part 4)
        logger.info("Running embeddings...")
        embed_result = embed_service.process_embeddings()

        if embed_result['processed'] == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No embeddings were created"
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Determine index type
        index_type = "IndexIVFFlat" if embed_result['processed'] > 300000 else "IndexHNSWFlat"

        logger.info(f"Index rebuild completed in {processing_time_ms}ms")

        return RebuildIndexResponse(
            count=embed_result['processed'],
            dim=embed_service.dimension,
            index_type=index_type,
            processing_time_ms=processing_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rebuilding index: {str(e)}"
        )

@router.post("/admin/reload", response_model=ReloadResponse)
async def reload_index(admin_user: dict = Depends(verify_admin_token)):
    """Reload FAISS index in memory."""
    try:
        logger.info("Reloading FAISS index...")

        # Try to load the index
        index = embed_service.load_faiss_index()

        if index is None:
            return ReloadResponse(
                success=False,
                message="No FAISS index found to reload"
            )

        # Verify index is loaded
        if index.ntotal > 0:
            return ReloadResponse(
                success=True,
                message=f"Successfully reloaded index with {index.ntotal} vectors"
            )
        else:
            return ReloadResponse(
                success=False,
                message="Index loaded but contains no vectors"
            )

    except Exception as e:
        logger.error(f"Error reloading index: {e}")
        return ReloadResponse(
            success=False,
            message=f"Error reloading index: {str(e)}"
        )

# Main recommendations endpoint
@router.post("/recommendations", response_model=RecResponse)
async def get_recommendations(request: RecReq):
    """
    Get personalized recommendations using the full pipeline.
    """
    try:
        start_time = time.time()

        logger.info(f"Getting recommendations for query: {request.query}")
        logger.info(f"Answers: {request.answers}")

        # Build query text from answers
        query_parts = []

        if request.answers.categories:
            query_parts.extend(request.answers.categories)

        if request.answers.style:
            query_parts.append(f"style {request.answers.style}")

        if request.answers.brand_pref:
            query_parts.extend([f"brands {brand}" for brand in request.answers.brand_pref])

        if request.answers.pack_size:
            query_parts.append(f"pack {request.answers.pack_size}")

        if request.answers.ship_region:
            query_parts.append(f"region {request.answers.ship_region}")

        if request.answers.abv_band:
            query_parts.append(f"abv {request.answers.abv_band}")

        if request.answers.nice_to_have:
            query_parts.extend([f"tags {tag}" for tag in request.answers.nice_to_have])

        # Combine with original query
        full_query = f"{request.query}; {'; '.join(query_parts)}"

        # Step 1: Create embedding for query
        query_text = embed_service.prepare_text_for_embedding({'title': full_query})
        logger.info(f"Query text for embedding: {query_text}")
        query_embedding = embed_service.create_embeddings_batch([query_text])[0]
        logger.info(f"Query embedding created, dimension: {len(query_embedding)}")

        # Step 2: FAISS search (topK=600)
        faiss_hits = embed_service.search_similar(query_embedding, k=600)
        logger.info(f"FAISS search returned {len(faiss_hits)} hits")

        if not faiss_hits:
            return RecResponse(
                query=request.query,
                items=[],
                confidence=0.0,
                subtotal=0.0,
                total_items=0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 3: Apply hard filters
        filtered_items = filter_service.apply_hard_filters(
            faiss_hits,
            ship_region=request.answers.ship_region,
            user_age=request.answers.user_age,
            abv_band=request.answers.abv_band
        )
        logger.info(f"Hard filters returned {len(filtered_items)} items")

        if not filtered_items:
            return RecResponse(
                query=request.query,
                items=[],
                confidence=0.0,
                subtotal=0.0,
                total_items=0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 4: Enhance items with additional product data
        logger.info(f"Enhancing {len(filtered_items)} items with additional product data")
        enhanced_items = enhanced_product_service.enrich_recommendation_items(
            filtered_items,
            include_pricing=True,
            include_trends=True
        )
        logger.info(f"Enhanced {len(enhanced_items)} items")

        # Step 5: GPT re-ranking
        answers_dict = request.answers.model_dump()
        logger.info(f"Calling GPT ranking with {len(enhanced_items)} candidates")
        ranking_result = await rank_service.rerank_with_function_calling(
            query=request.query,
            candidates=enhanced_items,
            answers=answers_dict,
            limit=request.limit
        )
        logger.info(f"GPT ranking returned {len(ranking_result.get('items', []))} items")

        # Step 6: Convert to response format with enhanced data
        recommendation_items = []
        for item in ranking_result['items']:
            # Find enhanced item data
            enhanced_item = next(
                (hit for hit in enhanced_items if hit.get('sku') == item['sku']),
                None
            )

            if enhanced_item:
                metadata = enhanced_item.get('metadata', {})
                category = metadata.get('category', {})
                category_str = category.get('level_1', '') if isinstance(category, dict) else str(category)

                recommendation_item = RecommendationItem(
                    sku=item['sku'],
                    title=enhanced_item.get('title', ''),
                    brand=metadata.get('brand', ''),
                    category=category_str,
                    style=metadata.get('style', ''),
                    abv=metadata.get('abv'),
                    price=enhanced_item.get('retail_price') or enhanced_item.get('wholesale_price') or item.get('price'),
                    score=item['score'],
                    reasons=item['reasons'],
                    qty=item['qty'],

                    # Enhanced product data
                    size=enhanced_item.get('size'),
                    origin=enhanced_item.get('origin'),
                    country=enhanced_item.get('country'),
                    container=enhanced_item.get('container'),
                    varietal=enhanced_item.get('varietal'),

                    # Pricing information
                    wholesale_price=enhanced_item.get('wholesale_price'),
                    retail_price=enhanced_item.get('retail_price'),
                    discount_percentage=enhanced_item.get('discount_percentage'),

                    # Availability
                    in_stock=enhanced_item.get('in_stock', True),
                    region_codes=enhanced_item.get('region_codes', []),

                    # Trend data
                    price_volatility=enhanced_item.get('price_volatility'),
                    trend_direction=enhanced_item.get('trend_direction'),
                    is_trending=enhanced_item.get('is_trending', False)
                )
                recommendation_items.append(recommendation_item)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Log "shown" events (Part 9)
        logger.info(f"Shown {len(recommendation_items)} recommendations for query: {request.query}")

        return RecResponse(
            query=request.query,
            items=recommendation_items,
            confidence=ranking_result['confidence'],
            subtotal=ranking_result['subtotal'],
            total_items=len(recommendation_items),
            processing_time_ms=processing_time_ms
        )

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )

# Template endpoints (require authentication)

@router.post("/templates")
async def save_template(
    template_data: SaveTemplate,
    authorization: str = Header(None),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Save a recommendation template.
    """
    try:
        # Verify user authentication (simplified for demo)
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required"
            )

        # Extract user_id from token (simplified)
        user_id = "user123"  # In real implementation, extract from JWT

        # Initialize template service
        template_service = TemplateService(db_session)

        # Save template
        template_id = await template_service.save_template(user_id, template_data)

        return {
            "id": str(template_id),
            "message": "Template saved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving template: {str(e)}"
        )

@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    authorization: str = Header(None),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Get a recommendation template by ID.
    """
    try:
        # Verify user authentication
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required"
            )

        # Extract user_id from token (simplified)
        user_id = "user123"  # In real implementation, extract from JWT

        # Initialize template service
        template_service = TemplateService(db_session)

        # Get template
        template = await template_service.get_template(UUID(template_id), user_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        return {
            "id": str(template.id),
            "template_name": template.template_name,
            "items": template.items,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template ID format"
        )
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting template: {str(e)}"
        )

@router.post("/events")
async def log_event(
    sku: str,
    action: str,
    meta: Optional[Dict[str, Any]] = None,
    template_id: Optional[str] = None,
    authorization: str = Header(None),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Log a recommendation event.
    """
    try:
        # Verify user authentication
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required"
            )

        # Extract user_id from token (simplified)
        user_id = "user123"  # In real implementation, extract from JWT

        # Validate action
        try:
            action_enum = ActionType(action.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action. Must be one of: {[a.value for a in ActionType]}"
            )

        # Initialize template service
        template_service = TemplateService(db_session)

        # Log event
        event_id = await template_service.log_event(
            user_id=user_id,
            sku=sku,
            action=action_enum,
            meta=meta,
            template_id=UUID(template_id) if template_id else None
        )

        return {
            "id": str(event_id),
            "message": f"Event logged successfully"
        }

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template ID format"
        )
    except Exception as e:
        logger.error(f"Error logging event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging event: {str(e)}"
        )

@router.post("/recommendations/enhanced", response_model=RecResponse)
async def get_enhanced_recommendations(
    request: RecReq,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    include_trending: bool = True,
    sort_by_value: bool = False
):
    """
    Get enhanced recommendations with advanced filtering and sorting options.
    """
    try:
        start_time = time.time()

        logger.info(f"Getting enhanced recommendations for query: {request.query}")

        # Build query text from answers
        query_parts = []

        if request.answers.categories:
            query_parts.extend(request.answers.categories)

        if request.answers.style:
            query_parts.append(f"style {request.answers.style}")

        if request.answers.brand_pref:
            query_parts.extend([f"brands {brand}" for brand in request.answers.brand_pref])

        if request.answers.pack_size:
            query_parts.append(f"pack {request.answers.pack_size}")

        if request.answers.ship_region:
            query_parts.append(f"region {request.answers.ship_region}")

        if request.answers.abv_band:
            query_parts.append(f"abv {request.answers.abv_band}")

        if request.answers.nice_to_have:
            query_parts.extend([f"tags {tag}" for tag in request.answers.nice_to_have])

        # Combine with original query
        full_query = f"{request.query}; {'; '.join(query_parts)}"

        # Step 1: Create embedding for query
        query_text = embed_service.prepare_text_for_embedding({'title': full_query})
        query_embedding = embed_service.create_embeddings_batch([query_text])[0]

        # Step 2: FAISS search (topK=600)
        faiss_hits = embed_service.search_similar(query_embedding, k=600)
        logger.info(f"FAISS search returned {len(faiss_hits)} hits")

        if not faiss_hits:
            return RecResponse(
                query=request.query,
                items=[],
                confidence=0.0,
                subtotal=0.0,
                total_items=0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 3: Apply hard filters
        filtered_items = filter_service.apply_hard_filters(
            faiss_hits,
            ship_region=request.answers.ship_region,
            user_age=request.answers.user_age,
            abv_band=request.answers.abv_band
        )
        logger.info(f"Hard filters returned {len(filtered_items)} items")

        if not filtered_items:
            return RecResponse(
                query=request.query,
                items=[],
                confidence=0.0,
                subtotal=0.0,
                total_items=0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Step 4: Enhance items with additional product data
        enhanced_items = enhanced_product_service.enrich_recommendation_items(
            filtered_items,
            include_pricing=True,
            include_trends=True
        )
        logger.info(f"Enhanced {len(enhanced_items)} items")

        # Step 5: Apply price filtering if specified
        if min_price is not None or max_price is not None:
            enhanced_items = enhanced_product_service.filter_by_price_range(
                enhanced_items, min_price, max_price
            )
            logger.info(f"Price filtering returned {len(enhanced_items)} items")

        # Step 6: Filter for trending items if requested
        if include_trending:
            trending_items = [item for item in enhanced_items if item.get('is_trending', False)]
            if trending_items:
                # Add trending items to the top of the list
                enhanced_items = trending_items + [item for item in enhanced_items if not item.get('is_trending', False)]
                logger.info(f"Prioritized {len(trending_items)} trending items")

        # Step 7: Sort by value if requested
        if sort_by_value:
            enhanced_items = enhanced_product_service.sort_by_value_score(enhanced_items)
            logger.info("Sorted items by value score")

        # Step 8: GPT re-ranking
        answers_dict = request.answers.model_dump()
        ranking_result = await rank_service.rerank_with_function_calling(
            query=request.query,
            candidates=enhanced_items,
            answers=answers_dict,
            limit=request.limit
        )
        logger.info(f"GPT ranking returned {len(ranking_result.get('items', []))} items")

        # Step 9: Convert to response format with enhanced data
        recommendation_items = []
        for item in ranking_result['items']:
            enhanced_item = next(
                (hit for hit in enhanced_items if hit.get('sku') == item['sku']),
                None
            )

            if enhanced_item:
                metadata = enhanced_item.get('metadata', {})
                category = metadata.get('category', {})
                category_str = category.get('level_1', '') if isinstance(category, dict) else str(category)

                recommendation_item = RecommendationItem(
                    sku=item['sku'],
                    title=enhanced_item.get('title', ''),
                    brand=metadata.get('brand', ''),
                    category=category_str,
                    style=metadata.get('style', ''),
                    abv=metadata.get('abv'),
                    price=enhanced_item.get('retail_price') or enhanced_item.get('wholesale_price') or item.get('price'),
                    score=item['score'],
                    reasons=item['reasons'],
                    qty=item['qty'],

                    # Enhanced product data
                    size=enhanced_item.get('size'),
                    origin=enhanced_item.get('origin'),
                    country=enhanced_item.get('country'),
                    container=enhanced_item.get('container'),
                    varietal=enhanced_item.get('varietal'),

                    # Pricing information
                    wholesale_price=enhanced_item.get('wholesale_price'),
                    retail_price=enhanced_item.get('retail_price'),
                    discount_percentage=enhanced_item.get('discount_percentage'),

                    # Availability
                    in_stock=enhanced_item.get('in_stock', True),
                    region_codes=enhanced_item.get('region_codes', []),

                    # Trend data
                    price_volatility=enhanced_item.get('price_volatility'),
                    trend_direction=enhanced_item.get('trend_direction'),
                    is_trending=enhanced_item.get('is_trending', False)
                )
                recommendation_items.append(recommendation_item)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Calculate subtotal
        subtotal = sum(item.price * item.qty for item in recommendation_items if item.price)

        # Calculate confidence
        confidence = ranking_result.get('confidence', 0.0)

        return RecResponse(
            query=request.query,
            items=recommendation_items,
            confidence=confidence,
            subtotal=subtotal,
            total_items=len(recommendation_items),
            processing_time_ms=processing_time_ms
        )

    except Exception as e:
        logger.error(f"Error getting enhanced recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting enhanced recommendations: {str(e)}"
        )

@router.get("/insights/{query}")
async def get_recommendation_insights(query: str, limit: int = 20):
    """
    Get insights about recommendations for a query without returning the actual recommendations.
    """
    try:
        # Get FAISS hits
        query_text = embed_service.prepare_text_for_embedding({'title': query})
        query_embedding = embed_service.create_embeddings_batch([query_text])[0]
        faiss_hits = embed_service.search_similar(query_embedding, k=limit)

        if not faiss_hits:
            return {
                "query": query,
                "insights": {
                    "total_candidates": 0,
                    "message": "No products found for this query"
                }
            }

        # Enhance items
        enhanced_items = enhanced_product_service.enrich_recommendation_items(
            faiss_hits,
            include_pricing=True,
            include_trends=True
        )

        # Get insights
        insights = enhanced_product_service.get_recommendation_insights(enhanced_items)

        return {
            "query": query,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error getting recommendation insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendation insights: {str(e)}"
        )