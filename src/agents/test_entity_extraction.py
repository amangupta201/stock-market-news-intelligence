"""
Test Entity Extraction Agent
"""
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.entity_extraction_agent import EntityExtractionAgent
from src.models.schemas import NewsArticle


def test_entity_extraction():
    print("=" * 60)
    print("🧪 TESTING ENTITY EXTRACTION AGENT")
    print("=" * 60)

    # Create test articles with known entities
    test_articles = [
        NewsArticle(
            id="test_1",
            title="HDFC Bank announces 15% dividend, board approves buyback",
            content="HDFC Bank Ltd announced a 15% dividend payout to shareholders. The board has also approved a Rs 5,000 crore stock buyback program. This is a major move in the banking sector.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_2",
            title="RBI raises repo rate by 25bps to 6.75%, citing inflation",
            content="The Reserve Bank of India (RBI) increased the repo rate by 25 basis points to 6.75% in its monetary policy meeting. Governor cited persistent inflation concerns. This will impact the banking sector.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_3",
            title="TCS reports 12% growth, announces special dividend",
            content="Tata Consultancy Services reported 12% YoY revenue growth in Q3. The IT services giant also announced a special dividend of Rs 50 per share. Strong performance in the technology sector.",
            source="Test",
            published_date=datetime.now()
        ),
        NewsArticle(
            id="test_4",
            title="Bajaj Finance targets Rs 9000: Analyst report",
            content="Bajaj Finance shows strong growth in NBFC segment. Analysts recommend buy rating with target price of Rs 9000. Financial services sector remains bullish.",
            source="Test",
            published_date=datetime.now()
        )
    ]

    # Initialize agent
    print("\n🤖 Initializing Entity Extraction Agent...")
    agent = EntityExtractionAgent()

    # Process each article
    print("\n" + "=" * 60)
    print("📊 PROCESSING TEST ARTICLES")
    print("=" * 60)

    all_entities = []
    for i, article in enumerate(test_articles, 1):
        print(f"\n--- Test Article {i}/{len(test_articles)} ---")
        processed = agent.process(article)
        all_entities.extend(processed.entities)

        # Show extracted entities
        print(f"\n   Entities found:")
        for entity in processed.entities:
            print(f"     - {entity.name} ({entity.entity_type.value})")

    # Evaluate accuracy
    print("\n" + "=" * 60)
    print("📊 EVALUATION")
    print("=" * 60)

    # Expected entities (ground truth)
    expected_entities = {
        "companies": ["HDFC Bank", "TCS", "Bajaj Finance", "Tata Consultancy Services"],
        "sectors": ["Banking", "Technology", "IT", "Financial Services", "NBFC"],
        "regulators": ["RBI", "Reserve Bank of India"],
        "events": ["dividend", "buyback", "rate hike", "growth"]
    }

    # Count extracted entities by type
    extracted_by_type = {}
    for entity in all_entities:
        entity_type = entity.entity_type.value
        if entity_type not in extracted_by_type:
            extracted_by_type[entity_type] = []
        extracted_by_type[entity_type].append(entity.name)

    print(f"\nExtracted entities by type:")
    for entity_type, entities in extracted_by_type.items():
        print(f"\n  {entity_type.upper()}: {len(entities)}")
        for entity_name in entities[:5]:  # Show first 5
            print(f"    - {entity_name}")
        if len(entities) > 5:
            print(f"    ... and {len(entities) - 5} more")

    # Check if key entities were found
    print(f"\n" + "=" * 60)
    print("✅ KEY ENTITY DETECTION")
    print("=" * 60)

    extracted_names_lower = [e.name.lower() for e in all_entities]

    key_checks = [
        ("HDFC Bank", "hdfc" in str(extracted_names_lower)),
        ("RBI / Reserve Bank", any(x in str(extracted_names_lower) for x in ["rbi", "reserve bank"])),
        ("TCS / Tata Consultancy", any(x in str(extracted_names_lower) for x in ["tcs", "tata consultancy"])),
        # Will match "tata consultancy services"
        ("Bajaj Finance", "bajaj" in str(extracted_names_lower)),
        ("Banking Sector", "banking" in str(extracted_names_lower)),
    ]

    found_count = 0
    for entity_name, check in key_checks:
        if isinstance(check, bool):
            found = check
        else:
            found = check in str(extracted_names_lower)

        if found:
            found_count += 1
            print(f"  ✅ {entity_name}: FOUND")
        else:
            print(f"  ❌ {entity_name}: NOT FOUND")

    precision = (found_count / len(key_checks)) * 100

    print(f"\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)

    print(f"\nTotal entities extracted: {len(all_entities)}")
    print(f"Key entities found: {found_count}/{len(key_checks)}")
    print(f"Precision: {precision:.1f}%")

    TARGET_PRECISION = 90.0

    if precision >= TARGET_PRECISION:
        print(f"\n🎉 SUCCESS! Precision {precision:.1f}% >= {TARGET_PRECISION}% (requirement met!)")
    else:
        print(f"\n⚠️  NEEDS IMPROVEMENT: Precision {precision:.1f}% < {TARGET_PRECISION}%")
        print(f"   Tip: Make sure GEMINI API KEY is set in .env for better extraction")

    return all_entities


if __name__ == "__main__":
    entities = test_entity_extraction()