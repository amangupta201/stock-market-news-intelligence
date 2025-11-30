"""
Storage & Indexing Agent
Stores processed articles in database and vector store
"""
import os
import sys
import json
from typing import List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.schemas import NewsArticle, UniqueStory


class StorageIndexingAgent:
    """
    Agent 5: Storage & Indexing

    Responsibilities:
    - Store articles in vector database (ChromaDB)
    - Store metadata in simple JSON files
    - Create unique story clusters
    - Enable fast retrieval for queries
    """

    def __init__(self, storage_dir: str = "data/processed"):
        """
        Initialize storage agent

        Args:
            storage_dir: Directory to store processed data
        """
        self.storage_dir = storage_dir
        self.articles_file = os.path.join(storage_dir, "articles.json")
        self.stories_file = os.path.join(storage_dir, "unique_stories.json")

        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

        # In-memory storage (for now)
        self.articles = []
        self.unique_stories = []

        # Load existing data if available
        self._load_existing_data()

        print("💾 Storage & Indexing Agent initialized")
        print(f"   Storage directory: {storage_dir}")
        print(f"   Existing articles: {len(self.articles)}")
        print(f"   Existing stories: {len(self.unique_stories)}")

    def _load_existing_data(self):
        """Load existing data from storage"""
        try:
            if os.path.exists(self.articles_file):
                with open(self.articles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert to NewsArticle objects (simplified - just count)
                    self.articles = data
                    print(f"   Loaded {len(self.articles)} existing articles")
        except Exception as e:
            print(f"   Warning: Could not load existing data: {e}")

    def _save_to_json(self, data: List[dict], filepath: str):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"   Error saving to {filepath}: {e}")

    def create_unique_story(self, primary_article: NewsArticle, duplicates: List[NewsArticle] = None) -> UniqueStory:
        """
        Create a unique story from primary article and duplicates

        Args:
            primary_article: Main article for this story
            duplicates: List of duplicate articles (if any)

        Returns:
            UniqueStory object
        """
        if duplicates is None:
            duplicates = []

        # Merge entities from all articles
        all_entities = list(primary_article.entities)
        for dup in duplicates:
            all_entities.extend(dup.entities)

        # Remove duplicate entities (by name and type)
        seen = set()
        unique_entities = []
        for entity in all_entities:
            key = (entity.name.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        # Merge stock impacts (keep highest confidence for each symbol)
        all_impacts = list(primary_article.stock_impacts)
        for dup in duplicates:
            all_impacts.extend(dup.stock_impacts)

        # Keep highest confidence for each stock
        unique_impacts = {}
        for impact in all_impacts:
            if impact.symbol not in unique_impacts:
                unique_impacts[impact.symbol] = impact
            else:
                if impact.confidence > unique_impacts[impact.symbol].confidence:
                    unique_impacts[impact.symbol] = impact

        story = UniqueStory(
            id=primary_article.id,
            primary_article=primary_article,
            duplicate_articles=duplicates,
            all_entities=unique_entities,
            all_stock_impacts=list(unique_impacts.values()),
            confidence_score=1.0
        )

        return story

    def process(self, articles: List[NewsArticle]) -> List[UniqueStory]:
        """
        Process and store a batch of articles

        Args:
            articles: List of processed NewsArticles

        Returns:
            List of UniqueStory objects
        """
        print(f"\n💾 STORAGE & INDEXING AGENT: Processing {len(articles)} articles")

        # Group duplicates
        unique_stories = []
        processed_ids = set()

        for article in articles:
            if article.id in processed_ids:
                continue

            if article.is_duplicate:
                # Skip duplicates - they're handled with their primary
                processed_ids.add(article.id)
                continue

            # Find all duplicates of this article
            duplicates = []
            for other in articles:
                if other.is_duplicate and other.duplicate_of == article.id:
                    duplicates.append(other)
                    processed_ids.add(other.id)

            # Create unique story
            story = self.create_unique_story(article, duplicates)
            unique_stories.append(story)
            processed_ids.add(article.id)

        print(f"   ✅ Created {len(unique_stories)} unique stories")
        print(f"   📊 Grouped {len(articles) - len(unique_stories)} duplicates")

        # Store in memory
        self.unique_stories.extend(unique_stories)

        # Save to JSON
        self._save_stories(unique_stories)

        return unique_stories

    def _save_stories(self, stories: List[UniqueStory]):
        """Save unique stories to JSON"""
        stories_data = []

        for story in stories:
            story_dict = {
                "id": story.id,
                "title": story.primary_article.title,
                "content": story.primary_article.content,
                "source": story.primary_article.source,
                "published_date": str(story.primary_article.published_date),
                "entities": [
                    {
                        "name": e.name,
                        "type": e.entity_type.value
                    }
                    for e in story.all_entities
                ],
                "stock_impacts": [
                    {
                        "symbol": imp.symbol,
                        "company": imp.company_name,
                        "confidence": imp.confidence,
                        "type": imp.impact_type.value
                    }
                    for imp in story.all_stock_impacts
                ],
                "num_duplicates": len(story.duplicate_articles)
            }
            stories_data.append(story_dict)

        self._save_to_json(stories_data, self.stories_file)
        print(f"   💾 Saved {len(stories)} stories to {self.stories_file}")

    def get_all_stories(self) -> List[UniqueStory]:
        """Get all stored unique stories"""
        return self.unique_stories

    def get_story_by_id(self, story_id: str) -> UniqueStory:
        """Get a specific story by ID"""
        for story in self.unique_stories:
            if story.id == story_id:
                return story
        return None

    def search_by_symbol(self, symbol: str) -> List[UniqueStory]:
        """
        Search stories by stock symbol

        Args:
            symbol: Stock symbol (e.g., "HDFCBANK")

        Returns:
            List of stories mentioning this stock
        """
        results = []
        for story in self.unique_stories:
            for impact in story.all_stock_impacts:
                if impact.symbol.upper() == symbol.upper():
                    results.append(story)
                    break
        return results

    def search_by_company(self, company_name: str) -> List[UniqueStory]:
        """
        Search stories by company name

        Args:
            company_name: Company name (partial match)

        Returns:
            List of stories mentioning this company
        """
        results = []
        company_lower = company_name.lower()

        for story in self.unique_stories:
            # Check entities
            for entity in story.all_entities:
                if company_lower in entity.name.lower():
                    results.append(story)
                    break

        return results

    def get_stats(self) -> dict:
        """Get storage statistics"""
        total_impacts = sum(len(story.all_stock_impacts) for story in self.unique_stories)
        total_entities = sum(len(story.all_entities) for story in self.unique_stories)

        return {
            "total_stories": len(self.unique_stories),
            "total_impacts": total_impacts,
            "total_entities": total_entities,
            "storage_dir": self.storage_dir
        }