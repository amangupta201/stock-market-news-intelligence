"""
Financial News Intelligence System - Main API
FastAPI application for the multi-agent news processing system
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.ingestion_agent import NewsIngestionAgent
from src.agents.deduplication_agent import DeduplicationAgent
from src.agents.entity_extraction_agent import EntityExtractionAgent
from src.agents.stock_impact_agent import StockImpactAnalysisAgent
from src.agents.storage_agent import StorageIndexingAgent
from src.agents.query_agent import QueryProcessingAgent
from src.models.schemas import NewsArticle, Entity, StockImpact

# Initialize FastAPI app
app = FastAPI(
    title="Financial News Intelligence API",
    description="AI-Powered multi-agent system for financial news processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (singleton pattern)
print("🚀 Initializing agents...")
ingestion_agent = NewsIngestionAgent()
dedup_agent = DeduplicationAgent(similarity_threshold=0.85)
entity_agent = EntityExtractionAgent()
stock_agent = StockImpactAnalysisAgent()
storage_agent = StorageIndexingAgent(storage_dir="data/processed")
query_agent = QueryProcessingAgent(storage_agent)
print("✅ All agents initialized!")


# Request/Response Models
class NewsSubmission(BaseModel):
    """Request model for submitting news"""
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content")
    source: str = Field(..., description="News source")
    url: Optional[str] = Field(None, description="Article URL")
    published_date: Optional[datetime] = Field(None, description="Publication date")


class ProcessedArticleResponse(BaseModel):
    """Response model for processed article"""
    id: str
    title: str
    source: str
    is_duplicate: bool
    duplicate_of: Optional[str]
    entities: List[dict]
    stock_impacts: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123",
                "title": "HDFC Bank announces dividend",
                "source": "MoneyControl",
                "is_duplicate": False,
                "duplicate_of": None,
                "entities": [
                    {"name": "HDFC Bank", "type": "company"}
                ],
                "stock_impacts": [
                    {"symbol": "HDFCBANK", "confidence": 1.0, "type": "direct"}
                ]
            }
        }


class QueryRequest(BaseModel):
    """Request model for querying news"""
    query: str = Field(..., description="Natural language query")
    limit: int = Field(10, ge=1, le=50, description="Maximum results")
    include_sector_news: bool = Field(True, description="Include sector-wide news")


class QueryResponse(BaseModel):
    """Response model for query results"""
    query: str
    results: List[dict]
    total_results: int
    processing_time: float


class SystemStats(BaseModel):
    """System statistics"""
    total_stories: int
    total_entities: int
    total_stock_impacts: int
    dedup_stats: dict
    storage_info: dict


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Financial News Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "POST /process": "Process a single news article",
            "POST /process/batch": "Process multiple articles",
            "POST /query": "Query news articles",
            "GET /stats": "Get system statistics",
            "GET /stories": "Get all unique stories",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "ingestion": "operational",
            "deduplication": "operational",
            "entity_extraction": "operational",
            "stock_impact": "operational",
            "storage": "operational",
            "query": "operational"
        }
    }


@app.post("/process", response_model=ProcessedArticleResponse)
async def process_article(news: NewsSubmission):
    """
    Process a single news article through the complete pipeline

    Steps:
    1. Ingestion (generate embeddings)
    2. Deduplication (check for duplicates)
    3. Entity Extraction (extract companies, sectors, etc.)
    4. Stock Impact (map to stock symbols)
    5. Storage (save to database)
    """
    try:
        # Generate unique ID
        import hashlib
        article_id = hashlib.md5(f"{news.title}_{news.source}".encode()).hexdigest()[:12]

        # Create NewsArticle object
        article = NewsArticle(
            id=article_id,
            title=news.title,
            content=news.content,
            source=news.source,
            url=news.url,
            published_date=news.published_date or datetime.now()
        )

        # Process through pipeline
        article = ingestion_agent.process(article)
        article = dedup_agent.process(article)
        article = entity_agent.process(article)
        article = stock_agent.process(article)

        # Store (as single article batch)
        storage_agent.process([article])

        # Format response
        return ProcessedArticleResponse(
            id=article.id,
            title=article.title,
            source=article.source,
            is_duplicate=article.is_duplicate,
            duplicate_of=article.duplicate_of,
            entities=[
                {"name": e.name, "type": e.entity_type.value}
                for e in article.entities
            ],
            stock_impacts=[
                {
                    "symbol": imp.symbol,
                    "company": imp.company_name,
                    "confidence": round(imp.confidence, 3),
                    "type": imp.impact_type.value
                }
                for imp in article.stock_impacts
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/process/batch")
async def process_batch(articles: List[NewsSubmission]):
    """
    Process multiple news articles in batch

    More efficient than processing one by one
    """
    try:
        if len(articles) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 articles per batch")

        processed = []
        news_articles = []

        # Convert to NewsArticle objects
        import hashlib
        for news in articles:
            article_id = hashlib.md5(f"{news.title}_{news.source}".encode()).hexdigest()[:12]
            article = NewsArticle(
                id=article_id,
                title=news.title,
                content=news.content,
                source=news.source,
                url=news.url,
                published_date=news.published_date or datetime.now()
            )
            news_articles.append(article)

        # Process through pipeline
        for article in news_articles:
            article = ingestion_agent.process(article)
            article = dedup_agent.process(article)
            article = entity_agent.process(article)
            article = stock_agent.process(article)
            processed.append(article)

        # Store all at once
        storage_agent.process(processed)

        # Format response
        return {
            "processed": len(processed),
            "duplicates": sum(1 for a in processed if a.is_duplicate),
            "unique": sum(1 for a in processed if not a.is_duplicate),
            "articles": [
                {
                    "id": a.id,
                    "title": a.title,
                    "is_duplicate": a.is_duplicate,
                    "entities_count": len(a.entities),
                    "stocks_count": len(a.stock_impacts)
                }
                for a in processed
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_news(request: QueryRequest):
    """
    Query news articles using natural language

    Examples:
    - "HDFC Bank news"
    - "Banking sector update"
    - "RBI policy changes"
    - "TCS results"
    """
    try:
        result = query_agent.process(
            query=request.query,
            limit=request.limit,
            include_sector_news=request.include_sector_news
        )

        return QueryResponse(
            query=result.query,
            results=[
                {
                    "id": story.id,
                    "title": story.primary_article.title,
                    "content": story.primary_article.content[:200] + "...",
                    "source": story.primary_article.source,
                    "published_date": story.primary_article.published_date.isoformat(),
                    "entities": [
                        {"name": e.name, "type": e.entity_type.value}
                        for e in story.all_entities[:5]
                    ],
                    "stock_impacts": [
                        {
                            "symbol": imp.symbol,
                            "confidence": round(imp.confidence, 3)
                        }
                        for imp in story.all_stock_impacts[:5]
                    ],
                    "num_duplicates": len(story.duplicate_articles)
                }
                for story in result.results
            ],
            total_results=result.total_results,
            processing_time=result.processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/stats", response_model=SystemStats)
async def get_stats():
    """Get system statistics"""
    try:
        storage_stats = storage_agent.get_stats()
        dedup_stats = dedup_agent.get_stats()

        return SystemStats(
            total_stories=storage_stats['total_stories'],
            total_entities=storage_stats['total_entities'],
            total_stock_impacts=storage_stats['total_impacts'],
            dedup_stats=dedup_stats,
            storage_info={
                "directory": storage_stats['storage_dir'],
                "stories_file": storage_agent.stories_file
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


@app.get("/stories")
async def get_all_stories(limit: int = 50, offset: int = 0):
    """Get all unique stories with pagination"""
    try:
        all_stories = storage_agent.get_all_stories()

        # Paginate
        stories = all_stories[offset:offset + limit]

        return {
            "total": len(all_stories),
            "limit": limit,
            "offset": offset,
            "stories": [
                {
                    "id": story.id,
                    "title": story.primary_article.title,
                    "source": story.primary_article.source,
                    "published_date": story.primary_article.published_date.isoformat(),
                    "entities_count": len(story.all_entities),
                    "stocks_count": len(story.all_stock_impacts),
                    "duplicates_count": len(story.duplicate_articles)
                }
                for story in stories
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stories: {str(e)}")


@app.get("/stocks/{symbol}")
async def get_news_by_stock(symbol: str):
    """Get all news for a specific stock symbol"""
    try:
        stories = storage_agent.search_by_symbol(symbol)

        return {
            "symbol": symbol.upper(),
            "total_stories": len(stories),
            "stories": [
                {
                    "id": story.id,
                    "title": story.primary_article.title,
                    "published_date": story.primary_article.published_date.isoformat(),
                    "impact": next(
                        (imp.confidence for imp in story.all_stock_impacts if imp.symbol.upper() == symbol.upper()),
                        0.0
                    )
                }
                for story in stories[:10]  # Limit to 10
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("🚀 Starting Financial News Intelligence API")
    print("=" * 70)
    print("\nAPI will be available at: http://localhost:8000")
    print("API docs (Swagger): http://localhost:8000/docs")
    print("Alternative docs (ReDoc): http://localhost:8000/redoc")
    print("\n" + "=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8000)