"""
Supabase Deals Handler
Handles operations for the core metrics schema with Supabase
"""

import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import json

class SupabaseDealsHandler:
    """Handler for deals operations with Supabase"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize Supabase client"""
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and Key are required")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
    def insert_deal(self, deal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new deal"""
        try:
            result = self.supabase.table("deals").insert(deal_data).execute()
            if result.data:
                print(f"✅ Deal inserted with ID: {result.data[0]['id']}")
                return result.data[0]
            else:
                raise Exception("No data returned from insert")
        except Exception as e:
            print(f"❌ Error inserting deal: {e}")
            raise
    
    def get_all_deals(self) -> List[Dict[str, Any]]:
        """Get all deals"""
        try:
            result = self.supabase.table("deals").select("*").order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting deals: {e}")
            return []
    
    def get_deal(self, deal_id: int) -> Optional[Dict[str, Any]]:
        """Get a deal by ID"""
        try:
            result = self.supabase.table("deals").select("*").eq("id", deal_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Error getting deal {deal_id}: {e}")
            return None
    
    def update_deal(self, deal_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a deal"""
        try:
            result = self.supabase.table("deals").update(update_data).eq("id", deal_id).execute()
            if result.data:
                print(f"✅ Deal {deal_id} updated successfully")
                return result.data[0]
            return None
        except Exception as e:
            print(f"❌ Error updating deal {deal_id}: {e}")
            return None
    
    def delete_deal(self, deal_id: int) -> bool:
        """Delete a deal"""
        try:
            result = self.supabase.table("deals").delete().eq("id", deal_id).execute()
            print(f"✅ Deal {deal_id} deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting deal {deal_id}: {e}")
            return False
    
    def search_deals_by_name(self, asset_name: str) -> List[Dict[str, Any]]:
        """Search deals by asset name"""
        try:
            result = self.supabase.table("deals").select("*").ilike("asset_name", f"%{asset_name}%").execute()
            return result.data
        except Exception as e:
            print(f"❌ Error searching deals: {e}")
            return []
    
    def get_deals_by_occupancy_range(self, min_occupancy: float, max_occupancy: float) -> List[Dict[str, Any]]:
        """Get deals within occupancy range"""
        try:
            result = self.supabase.table("deals").select("*").gte("current_occupancy_percent", min_occupancy).lte("current_occupancy_percent", max_occupancy).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error getting deals by occupancy: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about deals"""
        try:
            deals = self.get_all_deals()
            
            total_deals = len(deals)
            occupancy_values = [d['current_occupancy_percent'] for d in deals if d['current_occupancy_percent'] is not None]
            avg_occupancy = sum(occupancy_values) / len(occupancy_values) if occupancy_values else 0
            
            total_units = sum(d['total_units'] for d in deals if d['total_units'] is not None)
            total_area = sum(d['net_rentable_area_sqft'] for d in deals if d['net_rentable_area_sqft'] is not None)
            
            return {
                'total_deals': total_deals,
                'average_occupancy': round(avg_occupancy, 2),
                'total_units': total_units,
                'total_area_sqft': total_area,
                'average_area_per_deal': round(total_area / total_deals, 2) if total_deals > 0 else 0
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    # Initialize handler with environment variables
    # Set these in your .env file:
    # SUPABASE_URL=your_supabase_project_url
    # SUPABASE_ANON_KEY=your_supabase_anon_key
    
    try:
        handler = SupabaseDealsHandler()
        
        # Insert sample deal
        sample_deal = {
            'asset_name': 'Test Property',
            'full_address': '123 Test St, Test City, TX 12345',
            'total_units': 100,
            'net_rentable_area_sqft': 50000,
            'current_occupancy_percent': 95.5,
            'source_document': 'test_om.pdf'
        }
        
        # Insert deal
        deal = handler.insert_deal(sample_deal)
        print(f"Inserted deal: {deal['asset_name']}")
        
        # Get all deals
        deals = handler.get_all_deals()
        print(f"Total deals: {len(deals)}")
        
        # Get statistics
        stats = handler.get_statistics()
        print(f"Statistics: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
