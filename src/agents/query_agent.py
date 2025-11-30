"""
Query Processing Agent
Handles natural language queries and retrieves relevant news
"""
import os
import sys
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.schemas import UniqueStory, QueryResult
from src.agents.storage_agent import StorageIndexingAgent
from src.utils.embeddings import get_embedding_generator


class QueryProcessingAgent:
    """
    Agent 6: Query Processing

    Responsibilities:
    - Parse natural language queries
    - Detect entities in queries (companies, sectors)
    - Retrieve relevant news with context expansion
    - Rank results by relevance

    Query patterns:
    - "HDFC Bank news" → Direct + sector news
    - "Banking sector update" → All banking stocks
    - "RBI policy changes" → Regulator-specific
    - "Interest rate impact" → Semantic search
    """

    def __init__(self, storage_agent: StorageIndexingAgent):
        """
        Initialize query agent

        Args:
            storage_agent: Storage agent to query from
        """
        self.storage = storage_agent
        self.embedding_gen = get_embedding_generator()

        # Company/symbol keywords for query parsing
        self.company_keywords = {
            "hdfc": "HDFCBANK",
            "hdfc bank": "HDFCBANK",
            "icici": "ICICIBANK",
            "icici bank": "ICICIBANK",
            "sbi": "SBIN",
            "tcs": "TCS",
            "infosys": "INFY",
            "wipro": "WIPRO",
            "bajaj finance": "BAJFINANCE",
            "bajaj": "BAJFINANCE",
            "reliance": "RELIANCE",
        }

        self.sector_keywords = {
            "banking": "banking",
            "bank": "banking",
            "it": "information technology",
            "tech": "technology",
            "auto": "automobile",
            "finance": "financial services",
            "nbfc": "nbfc",
        }

        print("🔍 Query Processing Agent initialized")
        print(f"   Available stories: {len(self.storage.get_all_stories())}")

    def parse_query(self, query: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Parse query to extract companies, sectors, and keywords

        Args:
            query: Natural language query

        Returns:
            Tuple of (company_symbols, sectors, keywords)
        """
        query_lower = query.lower()

        companies = []
        sectors = []
        keywords = []

        # Extract companies
        for keyword, symbol in self.company_keywords.items():
            if keyword in query_lower:
                companies.append(symbol)

        # Extract sectors
        for keyword, sector in self.sector_keywords.items():
            if keyword in query_lower:
                sectors.append(sector)

        # Extract other keywords (news, update, policy, etc.)
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 3 and word not in ["news", "update", "latest", "recent"]:
                keywords.append(word)

        return companies, sectors, keywords

    def search_by_query(
            self,
            query: str,
            limit: int = 10,
            include_sector_news: bool = True,
            min_relevance_score: float = 0.5
    ) -> List[Tuple[UniqueStory, float]]:
        """
        Search stories by natural language query

        Args:
            query: Natural language query
            limit: Maximum number of results
            include_sector_news: Include sector-wide news
            min_relevance_score: Minimum relevance threshold

        Returns:
            List of (story, relevance_score) tuples
        """
        companies, sectors, keywords = self.parse_query(query)

        all_stories = self.storage.get_all_stories()
        results = []

        for story in all_stories:
            relevance = 0.0
            reasons = []

            # Direct company match - highest relevance
            for company in companies:
                for impact in story.all_stock_impacts:
                    if impact.symbol == company:
                        relevance += 1.0 * impact.confidence
                        reasons.append(f"Direct mention: {company}")
                        break

            # Sector match - medium relevance
            if include_sector_news:
                for sector in sectors:
                    for entity in story.all_entities:
                        if sector in entity.name.lower():
                            relevance += 0.7
                            reasons.append(f"Sector match: {sector}")
                            break

            # Keyword match in title/content - lower relevance
            title_lower = story.primary_article.title.lower()
            content_lower = story.primary_article.content.lower()

            for keyword in keywords:
                if keyword in title_lower:
                    relevance += 0.5
                    reasons.append(f"Keyword in title: {keyword}")
                elif keyword in content_lower:
                    relevance += 0.3
                    reasons.append(f"Keyword in content: {keyword}")

            # Add to results if relevant
            if relevance >= min_relevance_score:
                results.append((story, relevance))

        # Sort by relevance (highest first)
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def process(
            self,
            query: str,
            limit: int = 10,
            include_sector_news: bool = True,
            min_relevance_score: float = 0.5
    ) -> QueryResult:
        """
        Process a query and return results

        Args:
            query: Natural language query
            limit: Maximum results
            include_sector_news: Include sector-wide news
            min_relevance_score: Minimum relevance threshold

        Returns:
            QueryResult object
        """
        print(f"\n🔍 QUERY PROCESSING AGENT: Processing query")
        print(f"   Query: '{query}'")

        import time
        start_time = time.time()

        # Parse query
        companies, sectors, keywords = self.parse_query(query)

        print(f"   Detected companies: {companies if companies else 'None'}")
        print(f"   Detected sectors: {sectors if sectors else 'None'}")
        print(f"   Keywords: {keywords[:3] if keywords else 'None'}")

        # Search
        results = self.search_by_query(
            query,
            limit=limit,
            include_sector_news=include_sector_news,
            min_relevance_score=min_relevance_score
        )

        processing_time = time.time() - start_time

        print(f"   ✅ Found {len(results)} relevant stories")
        print(f"   ⏱️  Processing time: {processing_time * 1000:.1f}ms")

        # Create QueryResult
        query_result = QueryResult(
            query=query,
            results=[story for story, score in results],
            total_results=len(results),
            processing_time=processing_time,
            expansion_applied=include_sector_news and len(sectors) > 0
        )

        return query_result