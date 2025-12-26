"""
AI Translation Benchmark - Semantic Similarity Metric

Author: Zoltan Tamas Toth

Cross-lingual semantic similarity using multilingual embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.constants import EMBEDDING_MODEL_MULTILINGUAL
from app.core.logging import get_logger

logger = get_logger(__name__)


class SemanticSimilarityMetric:
    """Semantic similarity metric using multilingual embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_MULTILINGUAL):
        """
        Initialize semantic similarity metric.

        Args:
            model_name: Sentence transformer model name
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        return self._model

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def evaluate(self, source_text: str, target_text: str) -> dict:
        """
        Evaluate semantic similarity between source and target.

        Args:
            source_text: Source text
            target_text: Translated text

        Returns:
            Dictionary with similarity score and details
        """
        if not source_text or not target_text:
            return {
                "score": 0.0,
                "similarity": 0.0,
                "warning": "Empty text",
            }

        try:
            # Generate embeddings
            logger.debug("Generating embeddings for semantic similarity")
            embeddings = self.model.encode([source_text, target_text])

            source_embedding = embeddings[0]
            target_embedding = embeddings[1]

            # Calculate cosine similarity
            similarity = self._cosine_similarity(source_embedding, target_embedding)

            # Convert to 0-100 scale
            # Cosine similarity ranges from -1 to 1, but for translations
            # we expect positive similarity, so we map [0, 1] to [0, 100]
            score = max(0.0, similarity) * 100.0

            logger.debug(f"Semantic similarity: {similarity:.4f}, score: {score:.2f}")

            return {
                "score": score,
                "similarity": similarity,
                "model": self.model_name,
                "warning": None,
            }

        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return {
                "score": 0.0,
                "similarity": 0.0,
                "warning": f"Similarity calculation error: {str(e)}",
            }
