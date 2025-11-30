"""
Deduplication Agent
Identifies duplicate news articles using semantic similarity
Target: ≥95% accuracy on duplicate detection
"""
from typing import List, Tuple
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.schemas import NewsArticle
from src.utils.embeddings import get_embedding_generator


class DeduplicationAgent:
    """
    Agent 2: Deduplication

    Responsibilities:
    - Compare new article with existing articles
    - Detect semantic similarity (not just exact matches)
    - Mark duplicates with confidence scores
    - Maintain unique story clusters

    Target: ≥95% duplicate detection accuracy
    """

    def __init__(self, similarity_threshold: float = None):
        """
        Initialize deduplication agent

        Args:
            similarity_threshold: Threshold for marking duplicates (0-1)
                                 Default: 0.85 from .env or hardcoded
        """
        if similarity_threshold is None:
            # Try to get from environment, default to 0.85
            similarity_threshold = float(os.getenv('DUPLICATE_THRESHOLD', '0.85'))

        self.threshold = similarity_threshold
        self.embedding_gen = get_embedding_generator()
        self.processed_articles = []  # Keep track of processed articles

        print(f"🔍 Deduplication Agent initialized (threshold: {self.threshold})")

    def calculate_similarity(self, article1: NewsArticle, article2: NewsArticle) -> float:
        """
        Calculate semantic similarity between two articles

        Args:
            article1: First article (must have embedding)
            article2: Second article (must have embedding)

        Returns:
            Similarity score between 0 and 1
        """
        if article1.embedding is None or article2.embedding is None:
            raise ValueError("Both articles must have embeddings")

        return self.embedding_gen.get_similarity(article1.embedding, article2.embedding)

    def find_duplicates(self, new_article: NewsArticle) -> Tuple[bool, str, float, List[str]]:
        """
        Check if new article is a duplicate of any existing article

        Args:
            new_article: Article to check (must have embedding)

        Returns:
            Tuple of (is_duplicate, duplicate_of_id, max_similarity, all_similar_ids)
        """
        if not self.processed_articles:
            return False, None, 0.0, []

        max_similarity = 0.0
        duplicate_of = None
        similar_articles = []

        # Compare with all processed articles
        for existing in self.processed_articles:
            similarity = self.calculate_similarity(new_article, existing)

            if similarity > max_similarity:
                max_similarity = similarity
                duplicate_of = existing.id

            # Track all articles above threshold
            if similarity >= self.threshold:
                similar_articles.append(existing.id)

        is_duplicate = max_similarity >= self.threshold

        return is_duplicate, duplicate_of, max_similarity, similar_articles

    def process(self, article: NewsArticle) -> NewsArticle:
        """
        Process an article for deduplication

        Args:
            article: NewsArticle with embedding already generated

        Returns:
            Article with duplicate fields updated
        """
        print(f"\n🔍 DEDUPLICATION AGENT: Checking article")
        print(f"   Title: {article.title[:60]}...")

        if article.embedding is None:
            raise ValueError("Article must have embedding before deduplication")

        # Find duplicates
        is_dup, dup_of, similarity, all_similar = self.find_duplicates(article)

        if is_dup:
            article.is_duplicate = True
            article.duplicate_of = dup_of
            print(f"   🔴 DUPLICATE FOUND!")
            print(f"      Duplicate of: {dup_of}")
            print(f"      Similarity: {similarity:.4f} (threshold: {self.threshold})")
            if len(all_similar) > 1:
                print(f"      Total similar articles: {len(all_similar)}")
        else:
            article.is_duplicate = False
            article.duplicate_of = None
            print(f"   ✅ UNIQUE article")
            if self.processed_articles:
                print(f"      Max similarity: {similarity:.4f} (threshold: {self.threshold})")

        # Add to processed list
        self.processed_articles.append(article)

        return article

    def get_unique_articles(self) -> List[NewsArticle]:
        """Get all unique (non-duplicate) articles"""
        return [a for a in self.processed_articles if not a.is_duplicate]

    def get_duplicate_groups(self) -> dict:
        """
        Group duplicates together

        Returns:
            Dict mapping primary article ID to list of duplicate IDs
        """
        groups = {}

        for article in self.processed_articles:
            if article.is_duplicate and article.duplicate_of:
                if article.duplicate_of not in groups:
                    groups[article.duplicate_of] = []
                groups[article.duplicate_of].append(article.id)

        return groups

    def get_stats(self) -> dict:
        """Get deduplication statistics"""
        total = len(self.processed_articles)
        unique = len(self.get_unique_articles())
        duplicates = total - unique

        return {
            "total_processed": total,
            "unique_articles": unique,
            "duplicate_articles": duplicates,
            "duplicate_rate": duplicates / total if total > 0 else 0,
            "duplicate_groups": len(self.get_duplicate_groups())
        }