"""
Test the Ingestion Agent with real scraped data
"""
import json
from src.agents.ingestion_agent import NewsIngestionAgent
from src.models.schemas import NewsArticle
from datetime import datetime


def test_ingestion_agent():
    print("=" * 60)
    print("Testing Ingestion Agent with Real Data")
    print("=" * 60)

    # Load real scraped news - try multiple paths
    print("\n📂 Loading scraped news data...")
    import os

    # Try different paths
    possible_paths = [
        'data/real_news.json',  # If running from project root
        '../data/real_news.json',  # If running from src folder
        '../../data/real_news.json',  # If running from src/agents
    ]

    articles_data = None
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   Found data at: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            break

    if articles_data is None:
        raise FileNotFoundError("Could not find data/real_news.json in any expected location")

    print(f"✅ Loaded {len(articles_data)} articles")

    # Convert to NewsArticle objects (take first 3 for testing)
    articles = []
    for data in articles_data[:3]:
        # Convert published_date string to datetime
        pub_date = datetime.fromisoformat(data['published_date'].replace('Z', '+00:00'))

        article = NewsArticle(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            source=data['source'],
            url=data['url'],
            published_date=pub_date,
            author=data.get('author')
        )
        articles.append(article)

    # Initialize agent
    print("\n🤖 Initializing Ingestion Agent...")
    agent = NewsIngestionAgent()

    # Process each article
    print(f"\n📊 Processing {len(articles)} articles...")
    print("-" * 60)

    processed_articles = []
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}/{len(articles)}:")
        processed = agent.process(article)
        processed_articles.append(processed)

    # Verify results
    print("\n" + "=" * 60)
    print("✅ INGESTION TEST COMPLETE")
    print("=" * 60)

    print(f"\nResults:")
    print(f"  - Total articles processed: {len(processed_articles)}")
    print(f"  - All have embeddings: {all(a.embedding is not None for a in processed_articles)}")
    print(f"  - Embedding dimensions: {len(processed_articles[0].embedding)}")

    # Test similarity between first two articles
    if len(processed_articles) >= 2:
        from src.utils.embeddings import get_embedding_generator
        emb_gen = get_embedding_generator()

        similarity = emb_gen.get_similarity(
            processed_articles[0].embedding,
            processed_articles[1].embedding
        )

        print(f"\n📊 Similarity Test:")
        print(f"  Article 1: {processed_articles[0].title[:50]}...")
        print(f"  Article 2: {processed_articles[1].title[:50]}...")
        print(f"  Similarity Score: {similarity:.4f}")

    return processed_articles


if __name__ == "__main__":
    processed = test_ingestion_agent()