"""
Test script to verify data models work correctly
Run this to check if schemas.py is working
"""
from datetime import datetime
from src.models.schemas import (
    NewsArticle,
    Entity,
    StockImpact,
    EntityType,
    ImpactType
)


def test_schemas():
    print("=" * 60)
    print("Testing Data Models (schemas.py)")
    print("=" * 60)

    # Test 1: Create a NewsArticle
    print("\n1. Creating NewsArticle...")
    article = NewsArticle(
        id="test_001",
        title="HDFC Bank announces 15% dividend",
        content="HDFC Bank announced a dividend of 15% to shareholders.",
        source="MoneyControl",
        published_date=datetime.now(),
        url="https://example.com/test"
    )
    print(f"   ✅ Created article: {article.title}")

    # Test 2: Create an Entity
    print("\n2. Creating Entity...")
    entity = Entity(
        name="HDFC Bank",
        entity_type=EntityType.COMPANY,
        mentions=1,
        context="Banking sector"
    )
    print(f"   ✅ Created entity: {entity.name} ({entity.entity_type})")

    # Test 3: Create StockImpact
    print("\n3. Creating StockImpact...")
    impact = StockImpact(
        symbol="HDFCBANK",
        company_name="HDFC Bank",
        confidence=1.0,
        impact_type=ImpactType.DIRECT,
        reasoning="Direct mention in article"
    )
    print(f"   ✅ Created stock impact: {impact.symbol} (confidence: {impact.confidence})")

    # Test 4: Add entities and impacts to article
    print("\n4. Adding entities and impacts to article...")
    article.entities = [entity]
    article.stock_impacts = [impact]
    print(f"   ✅ Article now has {len(article.entities)} entities")
    print(f"   ✅ Article now has {len(article.stock_impacts)} stock impacts")

    # Test 5: Convert to dict/JSON
    print("\n5. Testing JSON serialization...")
    article_dict = article.model_dump()
    print(f"   ✅ Converted to dict with {len(article_dict)} fields")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Schemas are working correctly.")
    print("=" * 60)


if __name__ == "__main__":
    test_schemas()