"""
Test Stock Impact Analysis Agent
"""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.entity_extraction_agent import EntityExtractionAgent
from src.agents.stock_impact_agent import StockImpactAnalysisAgent
from src.models.schemas import NewsArticle


def test_stock_impact():
    print("=" * 60)
    print("🧪 TESTING STOCK IMPACT ANALYSIS AGENT")
    print("=" * 60)

    # Create test articles
    test_articles = [
        NewsArticle(
            id="test_1",
            title="HDFC Bank announces 15% dividend",
            content="HDFC Bank announced a 15% dividend payout to shareholders. This is positive news for the banking sector.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_2",
            title="RBI raises repo rate by 25bps",
            content="The Reserve Bank of India raised the repo rate by 25 basis points. This will impact the entire banking sector.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_3",
            title="TCS reports strong Q3 growth",
            content="Tata Consultancy Services reported strong growth in IT services segment. Technology sector outlook remains positive.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_4",
            title="Bajaj Finance posts record profits",
            content="Bajaj Finance, a leading NBFC, posted record quarterly profits. Financial services sector shows strength.",
            source="Test",
            published_date=datetime.now()
        )
    ]

    # Initialize agents
    print("\n🤖 Initializing agents...")
    entity_agent = EntityExtractionAgent()
    stock_agent = StockImpactAnalysisAgent()

    # Process articles
    print("\n" + "=" * 60)
    print("📊 PROCESSING TEST ARTICLES")
    print("=" * 60)

    all_impacts = []

    for i, article in enumerate(test_articles, 1):
        print(f"\n--- Test Article {i}/{len(test_articles)} ---")
        print(f"Title: {article.title}")

        # Step 1: Extract entities
        article = entity_agent.process(article)

        # Step 2: Map to stocks
        article = stock_agent.process(article)

        all_impacts.extend(article.stock_impacts)

        # Show results
        print(f"\n   Stock Impacts ({len(article.stock_impacts)}):")
        for impact in article.stock_impacts:
            print(f"     - {impact.symbol} ({impact.company_name})")
            print(f"       Confidence: {impact.confidence * 100:.1f}% | Type: {impact.impact_type.value}")

    # Evaluate results
    print("\n" + "=" * 60)
    print("📊 EVALUATION")
    print("=" * 60)

    # Expected mappings
    expected_mappings = {
        "test_1": {  # HDFC Bank dividend
            "direct": ["HDFCBANK"],
            "sector": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"]
        },
        "test_2": {  # RBI rate hike
            "regulatory": ["HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"]
        },
        "test_3": {  # TCS growth
            "direct": ["TCS"],
            "sector": ["TCS", "INFY", "WIPRO"]
        },
        "test_4": {  # Bajaj Finance
            "direct": ["BAJFINANCE"],
            "sector": ["BAJFINANCE"]
        }
    }

    # Check mappings
    print("\n✅ KEY MAPPINGS CHECK:")
    print("-" * 60)

    correct_mappings = 0
    total_checks = 0

    for article in test_articles:
        print(f"\n{article.id}: {article.title[:40]}...")

        if article.id in expected_mappings:
            expected = expected_mappings[article.id]
            actual_symbols = [imp.symbol for imp in article.stock_impacts]

            # Check direct mentions
            if "direct" in expected:
                for symbol in expected["direct"]:
                    total_checks += 1
                    direct_impacts = [imp for imp in article.stock_impacts
                                      if imp.symbol == symbol and imp.impact_type.value == "direct"]
                    if direct_impacts:
                        correct_mappings += 1
                        print(f"  ✅ {symbol}: Found (direct, {direct_impacts[0].confidence * 100:.0f}%)")
                    else:
                        print(f"  ❌ {symbol}: Not found as direct mention")

            # Check sector impacts
            if "sector" in expected:
                sector_found = any(imp.impact_type.value == "sector_wide" for imp in article.stock_impacts)
                total_checks += 1
                if sector_found:
                    correct_mappings += 1
                    sector_symbols = [imp.symbol for imp in article.stock_impacts
                                      if imp.impact_type.value == "sector_wide"]
                    print(f"  ✅ Sector impacts: {len(sector_symbols)} stocks")
                else:
                    print(f"  ❌ Sector impacts: Not found")

    # Calculate accuracy
    accuracy = (correct_mappings / total_checks * 100) if total_checks > 0 else 0

    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)

    print(f"\nTotal stock impacts: {len(all_impacts)}")
    print(f"Unique stocks affected: {len(set(imp.symbol for imp in all_impacts))}")

    # Impact type breakdown
    impact_types = {}
    for impact in all_impacts:
        impact_type = impact.impact_type.value
        impact_types[impact_type] = impact_types.get(impact_type, 0) + 1

    print(f"\nImpact type breakdown:")
    for impact_type, count in impact_types.items():
        print(f"  - {impact_type}: {count}")

    print(f"\nMapping Accuracy:")
    print(f"  Correct mappings: {correct_mappings}/{total_checks}")
    print(f"  Accuracy: {accuracy:.1f}%")

    # Check confidence levels
    direct_impacts = [imp for imp in all_impacts if imp.impact_type.value == "direct"]
    sector_impacts = [imp for imp in all_impacts if imp.impact_type.value == "sector_wide"]
    regulatory_impacts = [imp for imp in all_impacts if imp.impact_type.value == "regulatory"]

    print(f"\nConfidence levels:")
    if direct_impacts:
        avg_direct = sum(imp.confidence for imp in direct_impacts) / len(direct_impacts)
        print(f"  Direct mentions: {avg_direct * 100:.1f}% avg (target: 100%)")
    if sector_impacts:
        avg_sector = sum(imp.confidence for imp in sector_impacts) / len(sector_impacts)
        print(f"  Sector-wide: {avg_sector * 100:.1f}% avg (target: 60-80%)")
    if regulatory_impacts:
        avg_reg = sum(imp.confidence for imp in regulatory_impacts) / len(regulatory_impacts)
        print(f"  Regulatory: {avg_reg * 100:.1f}% avg (target: 50-70%)")

    TARGET_ACCURACY = 80.0

    if accuracy >= TARGET_ACCURACY:
        print(f"\n🎉 SUCCESS! Accuracy {accuracy:.1f}% >= {TARGET_ACCURACY}%")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT: Accuracy {accuracy:.1f}% < {TARGET_ACCURACY}%")

    return all_impacts


if __name__ == "__main__":
    impacts = test_stock_impact()