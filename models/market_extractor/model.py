"""
Market Data Extractor Model
Extracts and normalizes market data from various sources
"""

import json
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3
from datetime import datetime


class MarketDataExtractor:
    def __init__(self, db_path: str = "market_data.db"):
        """Initialize the market data extractor"""
        self.db_path = db_path
        self.schema_path = Path(__file__).parent.parent.parent / "schemas" / "canonical_schema.json"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for market data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create market data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                property_type TEXT NOT NULL,
                property_class TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT NOT NULL,
                data_source TEXT NOT NULL,
                collection_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_schema(self) -> Dict[str, Any]:
        """Load the canonical schema"""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def fetch_zillow_data(self, location: str, property_type: str) -> Dict[str, Any]:
        """Fetch data from Zillow API (placeholder - requires API key)"""
        # This is a placeholder implementation
        # In practice, you'd use the Zillow API or web scraping
        return {
            "market_rent_per_sqft": 25.50,
            "market_cap_rate": 5.2,
            "market_vacancy_rate": 8.5,
            "data_source": "zillow",
            "location": location,
            "property_type": property_type
        }
    
    def fetch_fred_data(self, series_id: str) -> Dict[str, Any]:
        """Fetch economic data from FRED API (free)"""
        try:
            # FRED API endpoint (free, no key required for basic data)
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": "demo",  # Use demo key for testing
                "file_type": "json",
                "limit": 1,
                "sort_order": "desc"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("observations"):
                    return {
                        "value": float(data["observations"][0]["value"]),
                        "date": data["observations"][0]["date"],
                        "series_id": series_id
                    }
        except Exception as e:
            print(f"Error fetching FRED data: {e}")
        
        return {}
    
    def fetch_census_data(self, location: str) -> Dict[str, Any]:
        """Fetch demographic and economic data from Census API (free)"""
        # Placeholder for Census API integration
        return {
            "population": 500000,
            "median_income": 75000,
            "unemployment_rate": 4.2,
            "data_source": "census",
            "location": location
        }
    
    def normalize_market_data(self, raw_data: Dict[str, Any], location: str, property_type: str) -> Dict[str, Any]:
        """Normalize market data to canonical schema format"""
        schema = self.load_schema()
        
        normalized_data = {
            "property_info": {
                "city": location.split(",")[0].strip() if "," in location else location,
                "state": location.split(",")[1].strip() if "," in location else "",
                "property_type": property_type.lower()
            },
            "market_data": {},
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "extraction_method": "market_data",
                "confidence_score": 0.8  # Default confidence for market data
            }
        }
        
        # Map raw data to schema fields
        if "market_rent_per_sqft" in raw_data:
            normalized_data["market_data"]["market_rent_per_sqft"] = {
                "value": raw_data["market_rent_per_sqft"],
                "unit": "usd_per_sqft_per_year"
            }
        
        if "market_cap_rate" in raw_data:
            normalized_data["market_data"]["market_cap_rate"] = {
                "value": raw_data["market_cap_rate"],
                "unit": "percentage"
            }
        
        if "market_vacancy_rate" in raw_data:
            normalized_data["market_data"]["market_vacancy_rate"] = {
                "value": raw_data["market_vacancy_rate"],
                "unit": "percentage"
            }
        
        return normalized_data
    
    def store_market_data(self, data: Dict[str, Any]):
        """Store market data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        location = f"{data['property_info']['city']}, {data['property_info']['state']}"
        property_type = data['property_info']['property_type']
        
        for metric_name, metric_data in data['market_data'].items():
            cursor.execute('''
                INSERT INTO market_data 
                (location, property_type, property_class, metric_name, metric_value, metric_unit, data_source, collection_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location,
                property_type,
                "unknown",  # Property class not available from market data
                metric_name,
                metric_data['value'],
                metric_data['unit'],
                data['metadata']['extraction_method'],
                data['metadata']['extraction_date']
            ))
        
        conn.commit()
        conn.close()
    
    def get_market_data(self, location: str, property_type: str) -> Dict[str, Any]:
        """Get market data for a specific location and property type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric_name, metric_value, metric_unit, data_source, collection_date
            FROM market_data
            WHERE location = ? AND property_type = ?
            ORDER BY collection_date DESC
        ''', (location, property_type))
        
        results = cursor.fetchall()
        conn.close()
        
        market_data = {}
        for row in results:
            metric_name, value, unit, source, date = row
            market_data[metric_name] = {
                "value": value,
                "unit": unit,
                "source": source,
                "date": date
            }
        
        return market_data
    
    def extract_market_data(self, location: str, property_type: str) -> Dict[str, Any]:
        """Extract market data from various sources"""
        try:
            # Fetch data from multiple sources
            zillow_data = self.fetch_zillow_data(location, property_type)
            fred_data = self.fetch_fred_data("FEDFUNDS")  # Federal funds rate
            census_data = self.fetch_census_data(location)
            
            # Combine data
            combined_data = {**zillow_data, **census_data}
            
            # Normalize to schema
            normalized_data = self.normalize_market_data(combined_data, location, property_type)
            
            # Store in database
            self.store_market_data(normalized_data)
            
            return normalized_data
            
        except Exception as e:
            print(f"Error extracting market data: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = MarketDataExtractor()
    
    # Extract market data for a location
    result = extractor.extract_market_data("Austin, TX", "multifamily")
    print(json.dumps(result, indent=2))
