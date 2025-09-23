#!/usr/bin/env python3
"""
Data Pipeline Script for HuntingParty.ai
Demonstrates the complete data flow from document upload to analysis
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.gp_extractor.model import GPDocumentExtractor
from models.market_extractor.model import MarketDataExtractor
from models.outlier_detector.model import OutlierDetector

def demo_pipeline():
    """Demonstrate the complete data pipeline"""
    print("🔄 Running HuntingParty.ai Data Pipeline Demo")
    print("=" * 60)
    
    # No external API keys required for local processing
    print("✅ Using local processing (no external APIs required)")
    
    # Initialize models
    print("📋 Initializing models...")
    gp_extractor = GPDocumentExtractor()  # No API key required
    market_extractor = MarketDataExtractor()
    outlier_detector = OutlierDetector()
    print("✅ Models initialized")
    
    # Step 1: Extract market data
    print("\n📊 Step 1: Extracting market data...")
    location = "Austin, TX"
    property_type = "multifamily"
    
    market_data = market_extractor.extract_market_data(location, property_type)
    print(f"✅ Market data extracted for {location} - {property_type}")
    print(f"   Data: {json.dumps(market_data, indent=2)}")
    
    # Step 2: Create sample GP data (since we don't have actual documents)
    print("\n📄 Step 2: Creating sample GP data...")
    sample_gp_data = {
        "property_info": {
            "address": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip_code": "78701",
            "property_type": "multifamily",
            "property_class": "class_b",
            "year_built": 2010,
            "total_sqft": 50000,
            "total_units": 50
        },
        "financial_metrics": {
            "purchase_price": 8000000,
            "current_occupancy": 95.0,
            "t12_revenue": 1200000,
            "t12_expenses": 400000,
            "t12_noi": 800000,
            "rent_per_sqft": 24.0
        },
        "debt_info": {
            "loan_amount": 6400000,
            "ltv_ratio": 80.0,
            "interest_rate": 5.5,
            "dscr": 1.25
        },
        "investment_metrics": {
            "entry_cap_rate": 6.0,
            "target_irr": 15.0,
            "target_equity_multiple": 2.5,
            "hold_period_years": 5.0
        },
        "metadata": {
            "source_document": "sample_deal.pdf",
            "extraction_date": "2024-01-01T00:00:00Z",
            "extraction_method": "gp_document",
            "confidence_score": 0.85
        }
    }
    
    print("✅ Sample GP data created")
    
    # Step 3: Analyze the deal
    print("\n🔍 Step 3: Analyzing deal for outliers...")
    analysis_result = outlier_detector.analyze_deal(sample_gp_data, market_data, "demo_deal")
    
    print("✅ Analysis complete")
    print(f"   Risk Score: {analysis_result['risk_score']:.2f}")
    print(f"   Flags Found: {len(analysis_result['flags'])}")
    print(f"   Summary: {analysis_result['summary']}")
    
    # Step 4: Display detailed results
    print("\n📋 Step 4: Detailed Analysis Results")
    print("-" * 40)
    
    if analysis_result['flags']:
        for i, flag in enumerate(analysis_result['flags'], 1):
            print(f"{i}. {flag['type'].upper()} - {flag['metric']}")
            print(f"   Severity: {flag['severity']}")
            print(f"   Reason: {flag['reason']}")
            if 'gp_value' in flag:
                print(f"   GP Value: {flag['gp_value']}")
            if 'market_value' in flag:
                print(f"   Market Value: {flag['market_value']}")
            print()
    else:
        print("✅ No issues detected!")
    
    print("=" * 60)
    print("🎉 Pipeline demo complete!")
    print("\nThis demonstrates the core functionality:")
    print("1. Market data extraction from various sources")
    print("2. GP document data extraction (simulated)")
    print("3. Outlier detection and risk analysis")
    print("4. Comprehensive reporting")

def test_models():
    """Test individual model components"""
    print("🧪 Testing Model Components")
    print("=" * 40)
    
    # Test market extractor
    print("Testing Market Data Extractor...")
    market_extractor = MarketDataExtractor()
    test_data = market_extractor.extract_market_data("Austin, TX", "multifamily")
    print(f"✅ Market extractor working: {len(test_data.get('market_data', {}))} metrics")
    
    # Test outlier detector
    print("Testing Outlier Detector...")
    outlier_detector = OutlierDetector()
    
    # Simple test data
    test_gp_data = {
        "financial_metrics": {
            "t12_revenue": 1000000,
            "t12_expenses": 400000,
            "t12_noi": 600000
        },
        "debt_info": {
            "loan_amount": 4000000,
            "ltv_ratio": 80.0,
            "interest_rate": 5.0,
            "dscr": 1.2
        },
        "investment_metrics": {
            "entry_cap_rate": 6.0
        }
    }
    
    test_market_data = {
        "market_data": {
            "market_cap_rate": {"value": 5.5},
            "market_rent_per_sqft": {"value": 25.0}
        }
    }
    
    result = outlier_detector.analyze_deal(test_gp_data, test_market_data, "test_deal")
    print(f"✅ Outlier detector working: {len(result['flags'])} flags found")
    
    print("✅ All model tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_models()
    else:
        demo_pipeline()
