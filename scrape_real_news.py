"""
Real Financial News Scraper
Scrapes live news from RSS feeds mentioned in the problem statement
"""
import feedparser
import requests
from datetime import datetime
from typing import List
import hashlib
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.schemas import NewsArticle


class RealNewsScraper:
    """Scrapes real financial news from RSS feeds"""

    RSS_FEEDS = {
        "MoneyControl": "https://www.moneycontrol.com/rss/latestnews.xml",
        "Economic Times": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
        "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
        "LiveMint": "https://www.livemint.com/rss/homepage",
        "Financial Express": "https://www.financialexpress.com/feed/",
        "NSE India": "https://www.nseindia.com/rss/news.xml",
        "RBI": "https://www.rbi.org.in/Scripts/RSS/RbiPressReleasesRSS.xml"
    }

    def __init__(self):
        self.articles = []

    def generate_article_id(self, title: str, source: str) -> str:
        """Generate unique ID for article"""
        unique_string = f"{title}_{source}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def parse_rss_feed(self, feed_url: str, source_name: str) -> List[NewsArticle]:
        """Parse a single RSS feed"""
        articles = []

        try:
            print(f"📡 Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"⚠️  Warning: Feed might have issues: {feed_url}")

            for entry in feed.entries[:10]:  # Get top 10 from each source
                try:
                    # Extract published date
                    published_date = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6])

                    # Extract content
                    content = ""
                    if hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    elif hasattr(entry, 'content'):
                        content = entry.content[0].value if entry.content else ""

                    # Clean HTML tags from content
                    import re
                    content = re.sub('<[^<]+?>', '', content)
                    content = content.strip()

                    # Skip if no content
                    if not content or len(content) < 50:
                        content = entry.title  # Use title as content if nothing else

                    # Create article
                    article = NewsArticle(
                        id=self.generate_article_id(entry.title, source_name),
                        title=entry.title,
                        content=content,
                        source=source_name,
                        url=entry.link if hasattr(entry, 'link') else None,
                        published_date=published_date,
                        author=entry.author if hasattr(entry, 'author') else None
                    )

                    articles.append(article)

                except Exception as e:
                    print(f"  ⚠️  Error parsing entry: {str(e)}")
                    continue

            print(f"  ✅ Got {len(articles)} articles from {source_name}")

        except Exception as e:
            print(f"  ❌ Error fetching {source_name}: {str(e)}")

        return articles

    def scrape_all_feeds(self, max_per_source: int = 10) -> List[NewsArticle]:
        """Scrape all RSS feeds"""
        print("\n" + "=" * 60)
        print("🚀 Starting Real News Scraper")
        print("=" * 60 + "\n")

        all_articles = []

        for source_name, feed_url in self.RSS_FEEDS.items():
            articles = self.parse_rss_feed(feed_url, source_name)
            all_articles.extend(articles)

        print("\n" + "=" * 60)
        print(f"✅ Total articles scraped: {len(all_articles)}")
        print("=" * 60 + "\n")

        self.articles = all_articles
        return all_articles

    def get_articles_by_keyword(self, keyword: str) -> List[NewsArticle]:
        """Filter articles by keyword"""
        keyword_lower = keyword.lower()
        return [
            article for article in self.articles
            if keyword_lower in article.title.lower() or keyword_lower in article.content.lower()
        ]

    def save_to_json(self, filename: str = "data/real_news.json"):
        """Save scraped articles to JSON file"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = [article.model_dump(mode='json') for article in self.articles]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"💾 Saved {len(self.articles)} articles to {filename}")


def main():
    """Test the scraper"""
    scraper = RealNewsScraper()

    # Scrape all feeds
    articles = scraper.scrape_all_feeds()

    # Show samples
    print("\n📰 Sample Articles:")
    print("-" * 60)
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Published: {article.published_date}")
        print(f"   URL: {article.url}")
        print(f"   Content preview: {article.content[:150]}...")

    # Save to file
    scraper.save_to_json("data/real_news.json")

    print("\n" + "=" * 60)
    print(f"✅ SUCCESS! Scraped {len(articles)} real articles")
    print("=" * 60)

    return articles


if __name__ == "__main__":
    articles = main()