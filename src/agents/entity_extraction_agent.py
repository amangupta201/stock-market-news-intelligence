"""
Entity Extraction Agent
Extracts structured entities from financial news articles
Target: ≥90% entity extraction precision
"""
import os
import sys
from typing import List, Dict
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.schemas import NewsArticle, Entity, EntityType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EntityExtractionAgent:
    """
    Agent 3: Entity Extraction

    Responsibilities:
    - Extract companies, sectors, regulators, people, events
    - Use LLM for intelligent extraction
    - Handle variations (HDFC Bank = HDFC Bank Ltd = HDFC)

    Target: ≥90% precision on entity extraction
    """

    def __init__(self):
        """Initialize entity extraction agent"""

        # Known entities database for matching
        self.known_companies = {
            "hdfc bank", "icici bank", "sbi", "axis bank", "kotak mahindra bank",
            "tcs", "infosys", "wipro", "tech mahindra", "hcl technologies",
            "reliance", "reliance industries", "reliance jio",
            "bajaj finance", "bajaj auto",
            "maruti suzuki", "tata motors", "mahindra",
            "sun pharma", "dr reddy", "cipla",
            "itc", "hul", "britannia", "nestle india",
            "tejas networks", "persistent systems",
            "aditya birla", "patel engineering",
            "hdfc life", "hdfc life insurance",
            "indigo", "air india"
        }

        self.known_sectors = {
            "banking", "financial services", "insurance", "nbfc",
            "information technology", "it services", "software",
            "automobile", "auto", "ev", "electric vehicle",
            "pharmaceuticals", "pharma", "healthcare",
            "fmcg", "consumer goods",
            "telecommunications", "telecom",
            "aviation", "airlines",
            "real estate", "infrastructure"
        }

        self.known_regulators = {
            "rbi", "reserve bank of india", "reserve bank",
            "sebi", "securities and exchange board",
            "irdai", "insurance regulatory",
            "government", "ministry"
        }

        print("🏢 Entity Extraction Agent initialized")
        print(f"   Known companies: {len(self.known_companies)}")
        print(f"   Known sectors: {len(self.known_sectors)}")
        print(f"   Known regulators: {len(self.known_regulators)}")

    def extract_entities_simple(self, article: NewsArticle) -> List[Entity]:
        """
        Simple rule-based entity extraction
        (Fallback when LLM is not available)

        Args:
            article: NewsArticle to extract entities from

        Returns:
            List of extracted entities
        """
        entities = []
        text_lower = f"{article.title} {article.content}".lower()

        # Extract companies
        for company in self.known_companies:
            if company in text_lower:
                # Count mentions
                mentions = text_lower.count(company)
                entities.append(Entity(
                    name=company.title(),
                    entity_type=EntityType.COMPANY,
                    mentions=mentions,
                    context=f"Mentioned {mentions} time(s) in article"
                ))

        # Extract sectors
        for sector in self.known_sectors:
            if sector in text_lower:
                entities.append(Entity(
                    name=sector.title(),
                    entity_type=EntityType.SECTOR,
                    mentions=1,
                    context="Industry/sector mention"
                ))

        # Extract regulators
        for regulator in self.known_regulators:
            if regulator in text_lower:
                entities.append(Entity(
                    name=regulator.upper() if len(regulator) <= 5 else regulator.title(),
                    entity_type=EntityType.REGULATOR,
                    mentions=1,
                    context="Regulatory body"
                ))

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.name.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def extract_entities_llm(self, article: NewsArticle) -> List[Entity]:
        """
        LLM-based entity extraction (more accurate)
        Uses Google Gemini API

        Args:
            article: NewsArticle to extract entities from

        Returns:
            List of extracted entities
        """
        try:
            import google.generativeai as genai

            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key or api_key == 'your_gemini_api_key_here':
                print("   ⚠️  No API key found, using simple extraction")
                return self.extract_entities_simple(article)

            # Configure Gemini
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash - fast and efficient for entity extraction
            model = genai.GenerativeModel('models/gemini-pro-latest')

            # Create prompt for entity extraction
            prompt = f"""Extract financial entities from this news article. Return ONLY a JSON object, no other text.

Article Title: {article.title}
Article Content: {article.content[:500]}

Extract these entity types:
1. COMPANY - Company names (HDFC Bank, Infosys, etc.)
2. SECTOR - Industry sectors (Banking, IT, Auto, etc.)
3. REGULATOR - Regulatory bodies (RBI, SEBI, etc.)
4. PERSON - People mentioned (CEOs, officials, etc.)
5. EVENT - Significant events (dividend, merger, rate hike, etc.)

Return JSON in this exact format:
{{
  "companies": ["Company Name 1", "Company Name 2"],
  "sectors": ["Sector 1", "Sector 2"],
  "regulators": ["Regulator 1"],
  "people": ["Person Name"],
  "events": ["Event 1", "Event 2"]
}}

IMPORTANT: Return ONLY the JSON object, nothing else."""

            response = model.generate_content(prompt)

            # Parse response
            response_text = response.text.strip()

            # Clean response (remove markdown code blocks if present)
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            data = json.loads(response_text)

            # Convert to Entity objects
            entities = []

            for company in data.get("companies", []):
                entities.append(Entity(
                    name=company,
                    entity_type=EntityType.COMPANY,
                    mentions=1,
                    context="Company mention"
                ))

            for sector in data.get("sectors", []):
                entities.append(Entity(
                    name=sector,
                    entity_type=EntityType.SECTOR,
                    mentions=1,
                    context="Sector/Industry"
                ))

            for regulator in data.get("regulators", []):
                entities.append(Entity(
                    name=regulator,
                    entity_type=EntityType.REGULATOR,
                    mentions=1,
                    context="Regulatory body"
                ))

            for person in data.get("people", []):
                entities.append(Entity(
                    name=person,
                    entity_type=EntityType.PERSON,
                    mentions=1,
                    context="Person mentioned"
                ))

            for event in data.get("events", []):
                entities.append(Entity(
                    name=event,
                    entity_type=EntityType.EVENT,
                    mentions=1,
                    context="Significant event"
                ))

            return entities

        except Exception as e:
            print(f"   ⚠️  LLM extraction failed: {str(e)}")
            print(f"   Falling back to simple extraction")
            return self.extract_entities_simple(article)

    def process(self, article: NewsArticle) -> NewsArticle:
        """
        Process an article for entity extraction

        Args:
            article: NewsArticle to process

        Returns:
            Article with entities populated
        """
        print(f"\n🏢 ENTITY EXTRACTION AGENT: Processing article")
        print(f"   Title: {article.title[:60]}...")

        # Try LLM-based extraction first, fall back to simple
        entities = self.extract_entities_llm(article)

        # Update article
        article.entities = entities

        print(f"   ✅ Extracted {len(entities)} entities")

        # Show entity breakdown
        entity_counts = {}
        for entity in entities:
            entity_type = entity.entity_type.value
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        for entity_type, count in entity_counts.items():
            print(f"      - {entity_type}: {count}")

        return article