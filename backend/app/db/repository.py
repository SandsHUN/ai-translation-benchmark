"""
AI Translation Benchmark - Data Repository

Author: Zoltan Tamas Toth

Data access layer for CRUD operations on database models.
"""

import hashlib
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.models import Evaluation, Run, Translation

logger = get_logger(__name__)


class Repository:
    """Data access layer for database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    @staticmethod
    def _hash_text(text: str) -> str:
        """
        Generate hash for text content.

        Args:
            text: Text to hash

        Returns:
            SHA-256 hash hex string
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def create_run(
        self,
        source_text: str,
        target_lang: str,
        source_lang: str | None = None,
        config_snapshot: dict[str, Any] | None = None,
    ) -> Run:
        """
        Create a new translation run.

        Args:
            source_text: Source text to translate
            target_lang: Target language code
            source_lang: Source language code (optional)
            config_snapshot: Configuration snapshot for reproducibility

        Returns:
            Created Run instance
        """
        text_hash = self._hash_text(source_text)

        run = Run(
            source_text=source_text,
            target_lang=target_lang,
            source_lang=source_lang,
            text_hash=text_hash,
            config_snapshot=config_snapshot,
        )

        self.session.add(run)
        await self.session.flush()
        logger.info(f"Created run {run.id} for target language '{target_lang}'")

        return run

    async def create_translation(
        self,
        run_id: int,
        provider: str,
        model: str,
        output_text: str,
        latency_ms: float,
        usage_tokens: int | None = None,
        raw_response: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Translation:
        """
        Create a translation result.

        Args:
            run_id: Associated run ID
            provider: Provider name
            model: Model name
            output_text: Translated text
            latency_ms: Translation latency in milliseconds
            usage_tokens: Token usage (if available)
            raw_response: Raw API response
            error: Error message (if failed)

        Returns:
            Created Translation instance
        """
        translation = Translation(
            run_id=run_id,
            provider=provider,
            model=model,
            output_text=output_text,
            latency_ms=latency_ms,
            usage_tokens=usage_tokens,
            raw_response=raw_response,
            error=error,
        )

        self.session.add(translation)
        await self.session.flush()
        logger.info(f"Created translation {translation.id} from provider '{provider}'")

        return translation

    async def create_evaluation(
        self,
        translation_id: int,
        metric_name: str,
        metric_value: float,
        details: dict[str, Any] | None = None,
    ) -> Evaluation:
        """
        Create an evaluation metric result.

        Args:
            translation_id: Associated translation ID
            metric_name: Name of the metric
            metric_value: Metric score value
            details: Additional metric details

        Returns:
            Created Evaluation instance
        """
        evaluation = Evaluation(
            translation_id=translation_id,
            metric_name=metric_name,
            metric_value=metric_value,
            details=details,
        )

        self.session.add(evaluation)
        await self.session.flush()
        logger.debug(f"Created evaluation for translation {translation_id}: {metric_name}")

        return evaluation

    async def get_run(self, run_id: int) -> Run | None:
        """
        Get run by ID with all related data.

        Args:
            run_id: Run ID

        Returns:
            Run instance or None if not found
        """
        stmt = (
            select(Run)
            .where(Run.id == run_id)
            .options(
                selectinload(Run.translations).selectinload(Translation.evaluations)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_runs(self, limit: int = 10) -> list[Run]:
        """
        Get recent translation runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of Run instances
        """
        stmt = (
            select(Run)
            .order_by(Run.created_at.desc())
            .limit(limit)
            .options(
                selectinload(Run.translations).selectinload(Translation.evaluations)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_translation(self, translation_id: int) -> Translation | None:
        """
        Get translation by ID with evaluations.

        Args:
            translation_id: Translation ID

        Returns:
            Translation instance or None if not found
        """
        stmt = (
            select(Translation)
            .where(Translation.id == translation_id)
            .options(selectinload(Translation.evaluations))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_runs_list(
        self, limit: int = 50, offset: int = 0
    ) -> list[tuple[Run, int, float | None]]:
        """Get list of runs with aggregated stats."""
        from sqlalchemy import func

        stmt = (
            select(
                Run,
                func.count(Translation.id).label("provider_count"),
                func.avg(Evaluation.metric_value).label("avg_score"),
            )
            .outerjoin(Translation, Run.id == Translation.run_id)
            .outerjoin(Evaluation, Translation.id == Evaluation.translation_id)
            .group_by(Run.id)
            .order_by(Run.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def commit(self) -> None:
        """Commit current transaction."""
        await self.session.commit()
        logger.debug("Transaction committed")

    async def rollback(self) -> None:
        """Rollback current transaction."""
        await self.session.rollback()
        logger.warning("Transaction rolled back")
