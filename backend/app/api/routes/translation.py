"""
AI Translation Benchmark - Translation Routes

Author: Zoltan Tamas Toth
Date: 2025-12-25

Main translation and evaluation endpoints.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config_manager
from app.core.constants import MSG_RUN_NOT_FOUND, ROUTE_RUN, ROUTE_RUN_BY_ID
from app.core.logging import get_logger
from app.db.database import get_db_session
from app.db.repository import Repository
from app.evaluation.evaluator import Evaluator
from app.providers.factory import ProviderFactory
from app.schemas.api import (
    RunSummary,
    TranslationRequest,
    TranslationResponse,
    TranslationWithEvaluation,
)
from app.schemas.provider import TranslationResult

logger = get_logger(__name__)

router = APIRouter()

# Global evaluator instance
evaluator = Evaluator()


@router.post(ROUTE_RUN, response_model=TranslationResponse)
async def run_translation(
    request: TranslationRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TranslationResponse:
    """
    Execute translation and evaluation.

    Args:
        request: Translation request
        session: Database session

    Returns:
        TranslationResponse with results and evaluations
    """
    logger.info(
        f"Translation request received: target_lang={request.target_lang}, "
        f"providers={len(request.providers)}, text_length={len(request.text)}"
    )
    logger.debug(f"Request details: {request.model_dump()}")

    repo = Repository(session)

    logger.info("Creating run record...")
    # Create run record
    config_snapshot = {
        "providers": [p.model_dump() for p in request.providers],
        "metrics": config_manager.get("metrics", {}),
    }

    run = await repo.create_run(
        source_text=request.text,
        target_lang=request.target_lang,
        source_lang=request.source_lang,
        config_snapshot=config_snapshot,
    )
    logger.info(f"Run record created with ID: {run.id}")

    logger.info(f"Creating {len(request.providers)} provider instances...")
    # Create provider instances
    providers = []
    for idx, provider_req in enumerate(request.providers, 1):
        try:
            logger.info(f"Creating provider {idx}/{len(request.providers)}: {provider_req.type} - {provider_req.model}")
            provider = ProviderFactory.create_from_request(provider_req.model_dump())
            providers.append(provider)
            logger.info(f"Provider {idx} created successfully")
        except Exception as e:
            logger.error(f"Failed to create provider {idx}: {str(e)}")
            logger.exception("Provider creation error:")
            # Continue with other providers

    if not providers:
        logger.error("No valid providers configured")
        raise HTTPException(status_code=400, detail="No valid providers configured")
    logger.info(f"Successfully created {len(providers)} providers")

    # Execute translations in parallel
    logger.info(f"Starting parallel translations with {len(providers)} providers")

    translation_tasks = [
        provider.translate_with_timing(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            timeout=request.timeout,
        )
        for provider in providers
    ]

    translation_results: list[TranslationResult] = await asyncio.gather(
        *translation_tasks, return_exceptions=False
    )

    # Store translations and run evaluations
    results_with_eval = []

    for translation_result in translation_results:
        # Store translation in database
        translation = await repo.create_translation(
            run_id=run.id,
            provider=translation_result.provider_name,
            model=translation_result.model_id,
            output_text=translation_result.output_text,
            latency_ms=translation_result.latency_ms,
            usage_tokens=translation_result.usage_tokens,
            raw_response=translation_result.raw_response,
            error=translation_result.error,
        )

        # Run evaluation
        if not translation_result.error:
            evaluation_result = await evaluator.evaluate_translation(
                translation_id=translation.id,
                provider_name=translation_result.provider_name,
                model_id=translation_result.model_id,
                source_text=request.text,
                target_text=translation_result.output_text,
                target_lang=request.target_lang,
                source_lang=request.source_lang,
                reference_translation=request.reference_translation,
            )

            # Store evaluation metrics
            for metric in evaluation_result.score_breakdown.metrics:
                await repo.create_evaluation(
                    translation_id=translation.id,
                    metric_name=metric.name,
                    metric_value=metric.value,
                    details=metric.details,
                )

            # Store overall score
            await repo.create_evaluation(
                translation_id=translation.id,
                metric_name="overall_score",
                metric_value=evaluation_result.score_breakdown.overall_score,
                details={
                    "explanation": evaluation_result.score_breakdown.explanation,
                    "warnings": evaluation_result.score_breakdown.warnings,
                },
            )

            results_with_eval.append(
                TranslationWithEvaluation(
                    translation=translation_result,
                    evaluation=evaluation_result,
                )
            )
        else:
            # Create dummy evaluation for failed translations
            from app.schemas.evaluation import EvaluationResult, ScoreBreakdown

            dummy_eval = EvaluationResult(
                translation_id=translation.id,
                provider_name=translation_result.provider_name,
                model_id=translation_result.model_id,
                score_breakdown=ScoreBreakdown(
                    overall_score=0.0,
                    metrics=[],
                    warnings=[translation_result.error or "Translation failed"],
                    explanation="Translation failed",
                ),
            )

            results_with_eval.append(
                TranslationWithEvaluation(
                    translation=translation_result,
                    evaluation=dummy_eval,
                )
            )

    # Commit all changes
    await repo.commit()

    # Generate summary
    summary = _generate_summary(results_with_eval)

    logger.info(f"Translation run {run.id} completed successfully")

    return TranslationResponse(
        run_id=run.id,
        source_text=request.text,
        target_lang=request.target_lang,
        source_lang=request.source_lang,
        results=results_with_eval,
        summary=summary,
        created_at=run.created_at.isoformat() if run.created_at else "",
    )


@router.get("/runs")
async def list_runs(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """Get list of translation runs."""
    from app.schemas.api import RunListItem

    repo = Repository(session)
    runs_data = await repo.get_runs_list(limit=limit, offset=offset)

    items = []
    for run, provider_count, avg_score in runs_data:
        preview = run.source_text[:100] + "..." if len(run.source_text) > 100 else run.source_text
        items.append(
            RunListItem(
                id=run.id,
                created_at=run.created_at.isoformat(),
                source_lang=run.source_lang,
                target_lang=run.target_lang,
                source_text_preview=preview,
                provider_count=provider_count,
                avg_score=avg_score,
            )
        )

    return items


@router.get(ROUTE_RUN_BY_ID, response_model=TranslationResponse)
async def get_run(
    run_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> TranslationResponse:
    """
    Get saved translation run by ID.

    Args:
        run_id: Run ID
        session: Database session

    Returns:
        TranslationResponse with saved results

    Raises:
        HTTPException: If run not found
    """
    repo = Repository(session)
    run = await repo.get_run(run_id)

    if not run:
        raise HTTPException(status_code=404, detail=MSG_RUN_NOT_FOUND)

    # Reconstruct response from database
    results_with_eval = []

    for translation in run.translations:
        # Reconstruct translation result
        translation_result = TranslationResult(
            provider_name=translation.provider,
            model_id=translation.model,
            output_text=translation.output_text,
            latency_ms=translation.latency_ms,
            usage_tokens=translation.usage_tokens,
            raw_response=translation.raw_response,
            error=translation.error,
        )

        # Reconstruct evaluation result
        from app.schemas.evaluation import EvaluationResult, MetricResult, ScoreBreakdown

        metrics = []
        overall_score = 0.0
        explanation = None
        warnings = []

        for evaluation in translation.evaluations:
            if evaluation.metric_name == "overall_score":
                overall_score = evaluation.metric_value
                if evaluation.details:
                    explanation = evaluation.details.get("explanation")
                    warnings = evaluation.details.get("warnings", [])
            else:
                metrics.append(
                    MetricResult(
                        name=evaluation.metric_name,
                        value=evaluation.metric_value,
                        weight=0.0,  # Weight not stored
                        details=evaluation.details,
                    )
                )

        score_breakdown = ScoreBreakdown(
            overall_score=overall_score,
            metrics=metrics,
            warnings=warnings,
            explanation=explanation,
        )

        evaluation_result = EvaluationResult(
            translation_id=translation.id,
            provider_name=translation.provider,
            model_id=translation.model,
            score_breakdown=score_breakdown,
        )

        results_with_eval.append(
            TranslationWithEvaluation(
                translation=translation_result,
                evaluation=evaluation_result,
            )
        )

    summary = _generate_summary(results_with_eval)

    return TranslationResponse(
        run_id=run.id,
        source_text=run.source_text,
        target_lang=run.target_lang,
        source_lang=run.source_lang,
        results=results_with_eval,
        summary=summary,
        created_at=run.created_at.isoformat() if run.created_at else "",
    )


def _generate_summary(results: list[TranslationWithEvaluation]) -> RunSummary:
    """
    Generate summary with rankings.

    Args:
        results: List of translation results with evaluations

    Returns:
        RunSummary with rankings
    """
    # Sort by overall score
    sorted_results = sorted(
        results,
        key=lambda r: r.evaluation.score_breakdown.overall_score,
        reverse=True,
    )

    rankings = []
    for idx, result in enumerate(sorted_results, 1):
        rankings.append(
            {
                "rank": idx,
                "provider": result.translation.provider_name,
                "model": result.translation.model_id,
                "score": result.evaluation.score_breakdown.overall_score,
                "latency_ms": result.translation.latency_ms,
            }
        )

    best_provider = None
    best_score = None

    if rankings:
        best_provider = rankings[0]["provider"]
        best_score = rankings[0]["score"]

    return RunSummary(
        total_providers=len(results),
        rankings=rankings,
        best_provider=best_provider,
        best_score=best_score,
    )
