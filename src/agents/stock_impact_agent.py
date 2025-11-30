"""
Stock Impact Analysis Agent
Maps extracted entities to impacted stocks with confidence scores
"""
import os
import sys
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.schemas import NewsArticle, Entity, StockImpact, EntityType, ImpactType


class StockImpactAnalysisAgent:
    """
    Agent 4: Stock Impact Analysis

    Responsibilities:
    - Map companies to stock symbols (NSE/BSE)
    - Assign confidence scores based on impact type
    - Handle sector-wide impacts
    - Map regulatory news to affected sectors

    Confidence Levels:
    - Direct mention: 100% (company explicitly mentioned)
    - Sector-wide: 60-80% (sector news affects all companies)
    - Regulatory: 50-70% (regulatory changes affect sector)
    - Supply chain: 40-60% (indirect impact)
    """

    def __init__(self):
        """Initialize stock impact agent with company-to-symbol mapping"""

        # Company name to NSE symbol mapping
        self.company_to_symbol = {
            # Banking
            "hdfc bank": ("HDFCBANK", "HDFC Bank Ltd"),
            "hdfc": ("HDFCBANK", "HDFC Bank Ltd"),
            "icici bank": ("ICICIBANK", "ICICI Bank Ltd"),
            "icici": ("ICICIBANK", "ICICI Bank Ltd"),
            "sbi": ("SBIN", "State Bank of India"),
            "state bank": ("SBIN", "State Bank of India"),
            "axis bank": ("AXISBANK", "Axis Bank Ltd"),
            "kotak mahindra": ("KOTAKBANK", "Kotak Mahindra Bank"),
            "kotak": ("KOTAKBANK", "Kotak Mahindra Bank"),

            # IT
            "tcs": ("TCS", "Tata Consultancy Services"),
            "tata consultancy": ("TCS", "Tata Consultancy Services"),
            "infosys": ("INFY", "Infosys Ltd"),
            "wipro": ("WIPRO", "Wipro Ltd"),
            "tech mahindra": ("TECHM", "Tech Mahindra Ltd"),
            "hcl": ("HCLTECH", "HCL Technologies"),
            "hcl technologies": ("HCLTECH", "HCL Technologies"),

            # Auto
            "maruti": ("MARUTI", "Maruti Suzuki India"),
            "maruti suzuki": ("MARUTI", "Maruti Suzuki India"),
            "tata motors": ("TATAMOTORS", "Tata Motors Ltd"),
            "mahindra": ("M&M", "Mahindra & Mahindra"),
            "bajaj auto": ("BAJAJ-AUTO", "Bajaj Auto Ltd"),

            # Finance/NBFC
            "bajaj finance": ("BAJFINANCE", "Bajaj Finance Ltd"),
            "hdfc life": ("HDFCLIFE", "HDFC Life Insurance"),

            # Telecom
            "reliance": ("RELIANCE", "Reliance Industries"),
            "bharti airtel": ("BHARTIARTL", "Bharti Airtel"),
            "airtel": ("BHARTIARTL", "Bharti Airtel"),

            # Others
            "itc": ("ITC", "ITC Ltd"),
            "hul": ("HINDUNILVR", "Hindustan Unilever"),
            "nestle": ("NESTLEIND", "Nestle India"),
            "britannia": ("BRITANNIA", "Britannia Industries"),
            "indigo": ("INDIGO", "InterGlobe Aviation"),
            "persistent systems": ("PERSISTENT", "Persistent Systems"),
            "tejas networks": ("TEJASNET", "Tejas Networks"),
            "patel engineering": ("PATELENG", "Patel Engineering"),
        }

        # Sector to stocks mapping (for sector-wide impact)
        self.sector_to_stocks = {
            "banking": [
                ("HDFCBANK", "HDFC Bank", 0.75),
                ("ICICIBANK", "ICICI Bank", 0.75),
                ("SBIN", "State Bank of India", 0.75),
                ("AXISBANK", "Axis Bank", 0.70),
                ("KOTAKBANK", "Kotak Mahindra Bank", 0.70),
            ],
            "financial services": [
                ("HDFCBANK", "HDFC Bank", 0.70),
                ("BAJFINANCE", "Bajaj Finance", 0.75),
                ("HDFCLIFE", "HDFC Life", 0.70),
            ],
            "it": [
                ("TCS", "Tata Consultancy Services", 0.75),
                ("INFY", "Infosys", 0.75),
                ("WIPRO", "Wipro", 0.70),
                ("TECHM", "Tech Mahindra", 0.70),
                ("HCLTECH", "HCL Technologies", 0.70),
            ],
            "information technology": [
                ("TCS", "Tata Consultancy Services", 0.75),
                ("INFY", "Infosys", 0.75),
                ("WIPRO", "Wipro", 0.70),
            ],
            "it services": [
                ("TCS", "Tata Consultancy Services", 0.75),
                ("INFY", "Infosys", 0.75),
                ("WIPRO", "Wipro", 0.70),
            ],
            "automobile": [
                ("MARUTI", "Maruti Suzuki", 0.75),
                ("TATAMOTORS", "Tata Motors", 0.75),
                ("M&M", "Mahindra & Mahindra", 0.70),
            ],
            "auto": [
                ("MARUTI", "Maruti Suzuki", 0.75),
                ("TATAMOTORS", "Tata Motors", 0.75),
            ],
            "nbfc": [
                ("BAJFINANCE", "Bajaj Finance", 0.80),
            ],
            "insurance": [
                ("HDFCLIFE", "HDFC Life", 0.75),
            ],
            "telecom": [
                ("RELIANCE", "Reliance Industries", 0.70),
                ("BHARTIARTL", "Bharti Airtel", 0.75),
            ],
            "fmcg": [
                ("ITC", "ITC", 0.70),
                ("HINDUNILVR", "Hindustan Unilever", 0.70),
                ("BRITANNIA", "Britannia Industries", 0.65),
            ],
        }

        print("📈 Stock Impact Analysis Agent initialized")
        print(f"   Company mappings: {len(self.company_to_symbol)}")
        print(f"   Sector mappings: {len(self.sector_to_stocks)}")

    def map_company_to_stock(self, company_name: str) -> StockImpact:
        """
        Map a company entity to stock symbol with 100% confidence

        Args:
            company_name: Name of the company

        Returns:
            StockImpact with direct mention (100% confidence)
        """
        company_lower = company_name.lower()

        # Try exact match first
        if company_lower in self.company_to_symbol:
            symbol, full_name = self.company_to_symbol[company_lower]
            return StockImpact(
                symbol=symbol,
                company_name=full_name,
                confidence=1.0,
                impact_type=ImpactType.DIRECT,
                reasoning=f"Direct mention of {company_name} in article"
            )

        # Try partial match
        for key, (symbol, full_name) in self.company_to_symbol.items():
            if key in company_lower or company_lower in key:
                return StockImpact(
                    symbol=symbol,
                    company_name=full_name,
                    confidence=0.95,
                    impact_type=ImpactType.DIRECT,
                    reasoning=f"Partial match for {company_name}"
                )

        # No match found - return with unknown symbol
        return StockImpact(
            symbol="UNKNOWN",
            company_name=company_name,
            confidence=0.50,
            impact_type=ImpactType.DIRECT,
            reasoning=f"Company {company_name} not in mapping database"
        )

    def map_sector_to_stocks(self, sector_name: str) -> List[StockImpact]:
        """
        Map a sector to affected stocks with 60-80% confidence

        Args:
            sector_name: Name of the sector

        Returns:
            List of StockImpacts for sector-wide impact
        """
        sector_lower = sector_name.lower()

        if sector_lower in self.sector_to_stocks:
            impacts = []
            for symbol, company_name, confidence in self.sector_to_stocks[sector_lower]:
                impacts.append(StockImpact(
                    symbol=symbol,
                    company_name=company_name,
                    confidence=confidence,
                    impact_type=ImpactType.SECTOR_WIDE,
                    reasoning=f"Sector-wide {sector_name} news"
                ))
            return impacts

        return []

    def map_regulator_to_stocks(self, regulator_name: str) -> List[StockImpact]:
        """
        Map regulatory news to affected sectors/stocks

        Args:
            regulator_name: Name of the regulator

        Returns:
            List of StockImpacts for regulatory impact
        """
        regulator_lower = regulator_name.lower()
        impacts = []

        # RBI impacts banking sector
        if any(x in regulator_lower for x in ["rbi", "reserve bank"]):
            if "banking" in self.sector_to_stocks:
                for symbol, company_name, base_conf in self.sector_to_stocks["banking"]:
                    impacts.append(StockImpact(
                        symbol=symbol,
                        company_name=company_name,
                        confidence=base_conf * 0.85,  # Slightly lower for regulatory
                        impact_type=ImpactType.REGULATORY,
                        reasoning=f"RBI regulatory news affects banking sector"
                    ))

        # SEBI impacts all listed companies (but mainly financial services)
        elif "sebi" in regulator_lower:
            if "financial services" in self.sector_to_stocks:
                for symbol, company_name, base_conf in self.sector_to_stocks["financial services"]:
                    impacts.append(StockImpact(
                        symbol=symbol,
                        company_name=company_name,
                        confidence=base_conf * 0.75,
                        impact_type=ImpactType.REGULATORY,
                        reasoning=f"SEBI regulatory news"
                    ))

        # IRDAI impacts insurance sector
        elif "irdai" in regulator_lower or "insurance regulatory" in regulator_lower:
            if "insurance" in self.sector_to_stocks:
                for symbol, company_name, base_conf in self.sector_to_stocks["insurance"]:
                    impacts.append(StockImpact(
                        symbol=symbol,
                        company_name=company_name,
                        confidence=base_conf * 0.80,
                        impact_type=ImpactType.REGULATORY,
                        reasoning=f"IRDAI regulatory news affects insurance sector"
                    ))

        return impacts

    def process(self, article: NewsArticle) -> NewsArticle:
        """
        Process an article for stock impact analysis

        Args:
            article: NewsArticle with entities already extracted

        Returns:
            Article with stock_impacts populated
        """
        print(f"\n📈 STOCK IMPACT AGENT: Analyzing article")
        print(f"   Title: {article.title[:60]}...")

        if not article.entities:
            print(f"   ⚠️  No entities found, skipping stock mapping")
            return article

        stock_impacts = []

        # Process each entity
        for entity in article.entities:

            if entity.entity_type == EntityType.COMPANY:
                # Direct company mention - 100% confidence
                impact = self.map_company_to_stock(entity.name)
                stock_impacts.append(impact)

            elif entity.entity_type == EntityType.SECTOR:
                # Sector-wide impact - 60-80% confidence
                sector_impacts = self.map_sector_to_stocks(entity.name)
                stock_impacts.extend(sector_impacts)

            elif entity.entity_type == EntityType.REGULATOR:
                # Regulatory impact - 50-70% confidence
                reg_impacts = self.map_regulator_to_stocks(entity.name)
                stock_impacts.extend(reg_impacts)

        # Remove duplicates (keep highest confidence)
        unique_impacts = {}
        for impact in stock_impacts:
            if impact.symbol not in unique_impacts:
                unique_impacts[impact.symbol] = impact
            else:
                # Keep the one with higher confidence
                if impact.confidence > unique_impacts[impact.symbol].confidence:
                    unique_impacts[impact.symbol] = impact

        article.stock_impacts = list(unique_impacts.values())

        print(f"   ✅ Mapped to {len(article.stock_impacts)} stock(s)")

        # Show breakdown by impact type
        impact_counts = {}
        for impact in article.stock_impacts:
            impact_type = impact.impact_type.value
            impact_counts[impact_type] = impact_counts.get(impact_type, 0) + 1

        for impact_type, count in impact_counts.items():
            print(f"      - {impact_type}: {count}")

        return article