"""
Simple Deals Handler
Database-agnostic operations for core metrics
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List, Optional

Base = declarative_base()

class Deal(Base):
    """Simple Deal model"""
    __tablename__ = 'deals'
    
    id = Column(Integer, primary_key=True)
    asset_name = Column(String(255), nullable=False)
    full_address = Column(Text, nullable=False)
    total_units = Column(Integer)
    net_rentable_area_sqft = Column(Integer)
    current_occupancy_percent = Column(DECIMAL(5, 2))
    source_document = Column(String(255))
    created_at = Column(TIMESTAMP)

class SimpleDealsHandler:
    """Simple handler for deals operations"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """Create tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Tables created")
    
    def insert_deal(self, deal_data: Dict[str, Any]) -> int:
        """Insert a deal"""
        session = self.Session()
        try:
            deal = Deal(**deal_data)
            session.add(deal)
            session.commit()
            return deal.id
        finally:
            session.close()
    
    def get_all_deals(self) -> List[Dict[str, Any]]:
        """Get all deals"""
        session = self.Session()
        try:
            deals = session.query(Deal).all()
            return [
                {
                    'id': d.id,
                    'asset_name': d.asset_name,
                    'full_address': d.full_address,
                    'total_units': d.total_units,
                    'net_rentable_area_sqft': d.net_rentable_area_sqft,
                    'current_occupancy_percent': float(d.current_occupancy_percent) if d.current_occupancy_percent else None,
                    'source_document': d.source_document,
                    'created_at': d.created_at
                }
                for d in deals
            ]
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    # Example database URLs for different databases
    # SQLite: "sqlite:///hunting_party.db"
    # PostgreSQL: "postgresql://user:pass@localhost:5432/hunting_party"
    # MySQL: "mysql://user:pass@localhost:3306/hunting_party"
    
    DATABASE_URL = "sqlite:///hunting_party.db"  # Default to SQLite for simplicity
    handler = SimpleDealsHandler(DATABASE_URL)
    handler.create_tables()
    
    # Insert sample deal
    sample_deal = {
        'asset_name': 'Test Property',
        'full_address': '123 Test St, Test City, TX 12345',
        'total_units': 100,
        'net_rentable_area_sqft': 50000,
        'current_occupancy_percent': 95.5,
        'source_document': 'test_om.pdf'
    }
    
    deal_id = handler.insert_deal(sample_deal)
    print(f"Inserted deal with ID: {deal_id}")
    
    # Get all deals
    deals = handler.get_all_deals()
    print(f"Total deals: {len(deals)}")
