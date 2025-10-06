"""
Template service for managing recommendation templates and events.
"""

from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from uuid import UUID

from ..models import RecommendationTemplate, RecommendationEvent, ActionType
from ..schemas import SaveTemplate

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for managing recommendation templates and events."""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save_template(self, user_id: str, template_data: SaveTemplate) -> UUID:
        """
        Save a recommendation template.

        Args:
            user_id: User ID
            template_data: Template data including name and items

        Returns:
            Template ID
        """
        try:
            template = RecommendationTemplate(
                user_id=user_id,
                template_name=template_data.name,
                items=template_data.answers.dict()
            )

            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)

            logger.info(f"Saved template {template.id} for user {user_id}")
            return template.id

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error saving template: {e}")
            raise

    async def get_template(self, template_id: UUID, user_id: str) -> Optional[RecommendationTemplate]:
        """
        Get a recommendation template by ID.

        Args:
            template_id: Template ID
            user_id: User ID (for authorization)

        Returns:
            Template if found and accessible, None otherwise
        """
        try:
            result = await self.db.execute(
                select(RecommendationTemplate)
                .where(RecommendationTemplate.id == template_id)
                .where(RecommendationTemplate.user_id == user_id)
            )

            template = result.scalar_one_or_none()

            if template:
                logger.info(f"Retrieved template {template_id} for user {user_id}")
            else:
                logger.warning(f"Template {template_id} not found or not accessible by user {user_id}")

            return template

        except Exception as e:
            logger.error(f"Error getting template: {e}")
            raise

    async def list_templates(self, user_id: str) -> List[RecommendationTemplate]:
        """
        List all templates for a user.

        Args:
            user_id: User ID

        Returns:
            List of templates
        """
        try:
            result = await self.db.execute(
                select(RecommendationTemplate)
                .where(RecommendationTemplate.user_id == user_id)
                .order_by(RecommendationTemplate.updated_at.desc())
            )

            templates = result.scalars().all()
            logger.info(f"Retrieved {len(templates)} templates for user {user_id}")

            return templates

        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            raise

    async def update_template(self, template_id: UUID, user_id: str, template_data: SaveTemplate) -> bool:
        """
        Update a recommendation template.

        Args:
            template_id: Template ID
            user_id: User ID (for authorization)
            template_data: Updated template data

        Returns:
            True if updated, False if not found
        """
        try:
            result = await self.db.execute(
                update(RecommendationTemplate)
                .where(RecommendationTemplate.id == template_id)
                .where(RecommendationTemplate.user_id == user_id)
                .values(
                    template_name=template_data.name,
                    items=template_data.answers.dict()
                )
            )

            if result.rowcount > 0:
                await self.db.commit()
                logger.info(f"Updated template {template_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Template {template_id} not found or not accessible by user {user_id}")
                return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating template: {e}")
            raise

    async def delete_template(self, template_id: UUID, user_id: str) -> bool:
        """
        Delete a recommendation template.

        Args:
            template_id: Template ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.db.execute(
                delete(RecommendationTemplate)
                .where(RecommendationTemplate.id == template_id)
                .where(RecommendationTemplate.user_id == user_id)
            )

            if result.rowcount > 0:
                await self.db.commit()
                logger.info(f"Deleted template {template_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Template {template_id} not found or not accessible by user {user_id}")
                return False

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting template: {e}")
            raise

    async def log_event(self, user_id: str, sku: str, action: ActionType,
                       meta: Optional[Dict[str, Any]] = None,
                       template_id: Optional[UUID] = None) -> UUID:
        """
        Log a recommendation event.

        Args:
            user_id: User ID
            sku: Product SKU
            action: Event action
            meta: Optional metadata
            template_id: Optional template ID

        Returns:
            Event ID
        """
        try:
            event = RecommendationEvent(
                user_id=user_id,
                sku=sku,
                action=action,
                meta=meta,
                template_id=template_id
            )

            self.db.add(event)
            await self.db.commit()
            await self.db.refresh(event)

            logger.info(f"Logged {action.value} event for SKU {sku} by user {user_id}")
            return event.id

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error logging event: {e}")
            raise

    async def get_user_events(self, user_id: str, limit: int = 100) -> List[RecommendationEvent]:
        """
        Get events for a user.

        Args:
            user_id: User ID
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        try:
            result = await self.db.execute(
                select(RecommendationEvent)
                .where(RecommendationEvent.user_id == user_id)
                .order_by(RecommendationEvent.created_at.desc())
                .limit(limit)
            )

            events = result.scalars().all()
            logger.info(f"Retrieved {len(events)} events for user {user_id}")

            return events

        except Exception as e:
            logger.error(f"Error getting user events: {e}")
            raise

    async def get_sku_events(self, sku: str, limit: int = 100) -> List[RecommendationEvent]:
        """
        Get events for a specific SKU.

        Args:
            sku: Product SKU
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        try:
            result = await self.db.execute(
                select(RecommendationEvent)
                .where(RecommendationEvent.sku == sku)
                .order_by(RecommendationEvent.created_at.desc())
                .limit(limit)
            )

            events = result.scalars().all()
            logger.info(f"Retrieved {len(events)} events for SKU {sku}")

            return events

        except Exception as e:
            logger.error(f"Error getting SKU events: {e}")
            raise
