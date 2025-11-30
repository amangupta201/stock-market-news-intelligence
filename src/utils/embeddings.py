"""
Utilities for generating embeddings
"""
from sentence_transformers import SentenceTransformer
from typing import List
import os


class EmbeddingGenerator:
    """Generate embeddings for news articles"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model

        Args:
            model_name: HuggingFace model name for embeddings
        """
        print(f"📦 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Embedding model loaded")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_article_embedding(self, title: str, content: str) -> List[float]:
        """
        Generate embedding for a news article
        Combines title and content with proper weighting

        Args:
            title: Article title
            content: Article content

        Returns:
            Embedding vector
        """
        # Combine title (more weight) and content
        combined_text = f"{title} {title} {content[:500]}"
        return self.generate_embedding(combined_text)

    def get_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        import numpy as np

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        return float(similarity)


# Global instance (singleton pattern)
_embedding_generator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the global embedding generator"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator