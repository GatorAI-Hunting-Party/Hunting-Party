"""
Utility functions for the API
"""

import json
import sqlite3
from typing import Dict, Any, List
from pathlib import Path


def init_database():
    """Initialize the main database"""
    conn = sqlite3.connect("hunting_party.db")
    cursor = conn.cursor()
    
    # Create deals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            source_document TEXT NOT NULL,
            extraction_date TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            data_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            gp_value REAL,
            market_value REAL,
            variance REAL,
            outlier_score REAL,
            flag_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def validate_schema(data: Dict[str, Any], schema_path: str) -> List[str]:
    """Validate data against canonical schema"""
    errors = []
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Basic validation - check required fields
        required_fields = [
            "property_info.address",
            "property_info.city", 
            "property_info.state",
            "property_info.property_type",
            "financial_metrics.purchase_price",
            "financial_metrics.current_occupancy"
        ]
        
        for field_path in required_fields:
            keys = field_path.split('.')
            current = data
            for key in keys:
                if key not in current:
                    errors.append(f"Missing required field: {field_path}")
                    break
                current = current[key]
    
    except Exception as e:
        errors.append(f"Schema validation error: {str(e)}")
    
    return errors


def format_analysis_summary(analysis_result: Dict[str, Any]) -> str:
    """Format analysis result into human-readable summary"""
    risk_score = analysis_result.get("risk_score", 0)
    flags = analysis_result.get("flags", [])
    
    summary = f"Risk Score: {risk_score:.2f}/1.0\n\n"
    
    if not flags:
        summary += "✅ No issues detected. Deal appears to be within normal parameters."
        return summary
    
    # Group flags by severity
    high_flags = [f for f in flags if f.get("severity") == "high"]
    medium_flags = [f for f in flags if f.get("severity") == "medium"]
    low_flags = [f for f in flags if f.get("severity") == "low"]
    
    if high_flags:
        summary += "🚨 HIGH SEVERITY ISSUES:\n"
        for flag in high_flags:
            summary += f"  • {flag['reason']}\n"
        summary += "\n"
    
    if medium_flags:
        summary += "⚠️  MEDIUM SEVERITY ISSUES:\n"
        for flag in medium_flags:
            summary += f"  • {flag['reason']}\n"
        summary += "\n"
    
    if low_flags:
        summary += "ℹ️  LOW SEVERITY ISSUES:\n"
        for flag in low_flags:
            summary += f"  • {flag['reason']}\n"
    
    return summary


def export_deal_data(deal_id: str, format: str = "json") -> str:
    """Export deal data in specified format"""
    conn = sqlite3.connect("hunting_party.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT data_json FROM deals WHERE deal_id = ?', (deal_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if not row:
        return None
    
    data = json.loads(row[0])
    
    if format == "json":
        return json.dumps(data, indent=2)
    elif format == "csv":
        # Convert to CSV format (simplified)
        csv_data = []
        csv_data.append("Field,Value,Unit")
        
        # Flatten the nested structure
        for section, values in data.items():
            if isinstance(values, dict):
                for field, value in values.items():
                    if isinstance(value, dict) and "value" in value:
                        csv_data.append(f"{section}.{field},{value['value']},{value.get('unit', '')}")
                    else:
                        csv_data.append(f"{section}.{field},{value},")
        
        return "\n".join(csv_data)
    
    return None
