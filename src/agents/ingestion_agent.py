"""
News Ingestion Agent
First agent in the pipeline - processes raw news and generates embeddings
"""
from typing import Dict, Any
from src.models.schemas import NewsArticle
from src.utils.embeddings import get_embedding_generator


class NewsIngestionAgent:
    """
    Agent 1: News Ingestion

    Responsibilities:
    - Validate incoming news article
    - Generate embeddings for semantic search
    - Prepare article for deduplication
    """

    def __init__(self):
        self.embedding_gen = get_embedding_generator()

    def process(self, article: NewsArticle) -> NewsArticle:
        """
        Process a news article

        Args:
            article: NewsArticle to process

        Returns:
            Article with embedding generated
        """
        print(f"\n📥 INGESTION AGENT: Processing article")
        print(f"   Title: {article.title[:60]}...")

        # Generate embedding if not already present
        if article.embedding is None:
            print(f"   🔢 Generating embedding...")
            article.embedding = self.embedding_gen.generate_article_embedding(
                article.title,
                article.content
            )
            print(f"   ✅ Embedding generated (dim: {len(article.embedding)})")
        else:
            print(f"   ⏭️  Embedding already exists")

        return article


# Test the agent
if __name__ == "__main__":
    from datetime import datetime

    print("=" * 60)
    print("Testing News Ingestion Agent")
    print("=" * 60)

    # Create test article
    test_article = NewsArticle(
        id="test_001",
        title="HDFC Bank announces 15% dividend",
        content="HDFC Bank announced a 15% dividend to shareholders. The board also approved a stock buyback program.",
        source="MoneyControl",
        published_date=datetime.now()
    )

    # Process with agent
    agent = NewsIngestionAgent()
    processed = agent.process(test_article)

    print(f"\n✅ Test completed!")
    print(f"   Article has embedding: {processed.embedding is not None}")
    print(f"   Embedding dimensions: {len(processed.embedding) if processed.embedding else 0}")