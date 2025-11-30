"""
Data Models for Financial News Intelligence System
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class EntityType(str, Enum):
    """Types of entities that can be extracted"""
    COMPANY = "company"
    SECTOR = "sector"
    REGULATOR = "regulator"
    PERSON = "person"
    EVENT = "event"


class ImpactType(str, Enum):
    """Types of stock impact"""
    DIRECT = "direct"  # 100% confidence - direct mention
    SECTOR_WIDE = "sector_wide"  # 60-80% - sector news
    REGULATORY = "regulatory"  # Variable - regulatory impact
    SUPPLY_CHAIN = "supply_chain"  # Variable - supply chain impact


class Entity(BaseModel):
    """Extracted entity from news article"""
    name: str
    entity_type: EntityType
    mentions: int = 1
    context: Optional[str] = None


class StockImpact(BaseModel):
    """Stock impact mapping with confidence score"""
    symbol: str
    company_name: str
    confidence: float = Field(ge=0.0, le=1.0, description="0-1 confidence score")
    impact_type: ImpactType
    reasoning: Optional[str] = None


class NewsArticle(BaseModel):
    """Financial news article model"""
    id: Optional[str] = None
    title: str
    content: str
    source: str
    url: Optional[str] = None
    published_date: datetime
    author: Optional[str] = None

    # Processed fields (filled by agents)
    entities: List[Entity] = []
    stock_impacts: List[StockImpact] = []
    embedding: Optional[List[float]] = None
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "HDFC Bank announces 15% dividend",
                "content": "HDFC Bank board approves...",
                "source": "MoneyControl",
                "published_date": "2024-11-28T10:00:00"
            }
        }


class UniqueStory(BaseModel):
    """Consolidated unique news story (after deduplication)"""
    id: str
    primary_article: NewsArticle
    duplicate_articles: List[NewsArticle] = []
    all_entities: List[Entity] = []
    all_stock_impacts: List[StockImpact] = []
    confidence_score: float = 1.0


class QueryRequest(BaseModel):
    """Request model for queries"""
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    include_sector_news: bool = True
    min_relevance_score: float = 0.5


class QueryResult(BaseModel):
    """Response model for queries"""
    query: str
    results: List[UniqueStory]
    total_results: int
    processing_time: float
    explanation: Optional[str] = None