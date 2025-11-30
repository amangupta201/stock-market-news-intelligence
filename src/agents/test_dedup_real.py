"""
Test Deduplication Agent with REAL scraped news
Run from project root: python test_dedup_real.py
"""
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.ingestion_agent import NewsIngestionAgent
from src.agents.deduplication_agent import DeduplicationAgent
from src.models.schemas import NewsArticle


def load_real_news():
    """Load real news from data/real_news.json"""
    print("📂 Loading real news from data/real_news.json...")

    # Try different paths
    possible_paths = [
        'data/real_news.json',  # If running from project root
        '../data/real_news.json',  # If running from src folder
        '../../data/real_news.json',  # If running from src/agents
        '../../../data/real_news.json',  # If running from deeper
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

    # Convert to NewsArticle objects
    articles = []
    for data in articles_data:
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

    print(f"✅ Loaded {len(articles)} real articles")
    return articles


def test_deduplication_real():
    print("=" * 60)
    print("🧪 TESTING DEDUPLICATION WITH REAL NEWS")
    print("=" * 60)

    # Load real news
    articles = load_real_news()

    # Known duplicate in real data: Articles 2 and 3 (Bajaj Finance - same ID)
    print("\n📋 Known Duplicate in Real Data:")
    print(f"  Article 2: {articles[2].title}")
    print(f"  Article 3: {articles[3].title}")
    print(f"  Same ID: {articles[2].id == articles[3].id}")

    # Step 1: Ingestion (generate embeddings)
    print("\n" + "=" * 60)
    print("📥 STEP 1: INGESTION")
    print("=" * 60)

    ingestion = NewsIngestionAgent()
    for article in articles:
        ingestion.process(article)

    print(f"\n✅ Generated embeddings for {len(articles)} articles")

    # Step 2: Deduplication
    print("\n" + "=" * 60)
    print("🔍 STEP 2: DEDUPLICATION")
    print("=" * 60)

    dedup = DeduplicationAgent(similarity_threshold=0.85)

    for article in articles:
        dedup.process(article)

    # Step 3: Results
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)

    stats = dedup.get_stats()
    print(f"\nStatistics:")
    print(f"  Total articles: {stats['total_processed']}")
    print(f"  Unique articles: {stats['unique_articles']}")
    print(f"  Duplicate articles: {stats['duplicate_articles']}")
    print(f"  Duplicate rate: {stats['duplicate_rate'] * 100:.1f}%")
    print(f"  Duplicate groups: {stats['duplicate_groups']}")

    # Show which articles were marked as duplicates
    print("\n🔍 Duplicate Detection Details:")
    duplicates_found = [a for a in articles if a.is_duplicate]

    if duplicates_found:
        print(f"\nFound {len(duplicates_found)} duplicate(s):")
        for dup in duplicates_found:
            print(f"\n  {dup.id}: {dup.title[:60]}...")
            print(f"    Duplicate of: {dup.duplicate_of}")
    else:
        print("\n  No duplicates detected")

    # Show duplicate groups
    groups = dedup.get_duplicate_groups()
    if groups:
        print("\n📋 Duplicate Groups:")
        for primary_id, dup_ids in groups.items():
            primary = next(a for a in articles if a.id == primary_id)
            print(f"\n  Primary ({primary_id}):")
            print(f"    {primary.title[:70]}...")
            print(f"  Duplicates ({len(dup_ids)}):")
            for dup_id in dup_ids:
                dup = next(a for a in articles if a.id == dup_id)
                print(f"    - {dup.title[:60]}...")

    # Check specific known duplicate (Bajaj Finance articles 2 and 3)
    print("\n" + "=" * 60)
    print("✅ KNOWN DUPLICATE CHECK")
    print("=" * 60)

    print("\nArticles 2 and 3 (Bajaj Finance - identical):")
    print(f"  Article 2 is duplicate: {articles[2].is_duplicate}")
    print(f"  Article 3 is duplicate: {articles[3].is_duplicate}")

    if articles[2].is_duplicate or articles[3].is_duplicate:
        print(f"  ✅ SUCCESS: Detected the known duplicate!")
    else:
        print(f"  ❌ MISSED: Did not detect the known duplicate")
        print(f"  Threshold might be too high. Current: {dedup.threshold}")

    return stats


if __name__ == "__main__":
    stats = test_deduplication_real()