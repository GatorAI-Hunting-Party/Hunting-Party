"""
Outlier Detection Model
Compares GP data against market data to identify anomalies and inconsistencies
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import sqlite3


class OutlierDetector:
    def __init__(self, db_path: str = "hunting_party.db"):
        """Initialize the outlier detector"""
        self.db_path = db_path
        self.schema_path = Path(__file__).parent.parent.parent / "schemas" / "canonical_schema.json"
        self.validation_rules_path = Path(__file__).parent.parent.parent / "schemas" / "validation_rules.json"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
    
    def load_schema(self) -> Dict[str, Any]:
        """Load the canonical schema"""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules"""
        with open(self.validation_rules_path, 'r') as f:
            return json.load(f)
    
    def validate_financial_consistency(self, gp_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check financial consistency within GP data"""
        validation_rules = self.load_validation_rules()
        flags = []
        
        try:
            # Check NOI calculation
            revenue = gp_data.get("financial_metrics", {}).get("t12_revenue", 0)
            expenses = gp_data.get("financial_metrics", {}).get("t12_expenses", 0)
            noi = gp_data.get("financial_metrics", {}).get("t12_noi", 0)
            
            if revenue and expenses and noi:
                calculated_noi = revenue - expenses
                variance = abs(calculated_noi - noi) / noi if noi != 0 else 0
                
                if variance > validation_rules["validation_rules"]["financial_consistency"]["noi_calculation"]["tolerance"]:
                    flags.append({
                        "type": "financial_consistency",
                        "metric": "t12_noi",
                        "gp_value": noi,
                        "expected_value": calculated_noi,
                        "variance": variance,
                        "severity": "high",
                        "reason": f"NOI calculation inconsistent. Expected {calculated_noi}, got {noi}"
                    })
            
            # Check DSCR calculation
            loan_amount = gp_data.get("debt_info", {}).get("loan_amount", 0)
            interest_rate = gp_data.get("debt_info", {}).get("interest_rate", 0)
            dscr = gp_data.get("debt_info", {}).get("dscr", 0)
            
            if loan_amount and interest_rate and dscr and noi:
                annual_debt_service = loan_amount * (interest_rate / 100)
                calculated_dscr = noi / annual_debt_service if annual_debt_service != 0 else 0
                variance = abs(calculated_dscr - dscr) / dscr if dscr != 0 else 0
                
                if variance > validation_rules["validation_rules"]["financial_consistency"]["dscr_calculation"]["tolerance"]:
                    flags.append({
                        "type": "financial_consistency",
                        "metric": "dscr",
                        "gp_value": dscr,
                        "expected_value": calculated_dscr,
                        "variance": variance,
                        "severity": "high",
                        "reason": f"DSCR calculation inconsistent. Expected {calculated_dscr:.2f}, got {dscr:.2f}"
                    })
            
            # Check LTV calculation
            purchase_price = gp_data.get("financial_metrics", {}).get("purchase_price", 0)
            ltv = gp_data.get("debt_info", {}).get("ltv_ratio", 0)
            
            if purchase_price and loan_amount and ltv:
                calculated_ltv = (loan_amount / purchase_price) * 100
                variance = abs(calculated_ltv - ltv) / ltv if ltv != 0 else 0
                
                if variance > validation_rules["validation_rules"]["financial_consistency"]["ltv_consistency"]["tolerance"]:
                    flags.append({
                        "type": "financial_consistency",
                        "metric": "ltv_ratio",
                        "gp_value": ltv,
                        "expected_value": calculated_ltv,
                        "variance": variance,
                        "severity": "medium",
                        "reason": f"LTV calculation inconsistent. Expected {calculated_ltv:.1f}%, got {ltv:.1f}%"
                    })
        
        except Exception as e:
            print(f"Error in financial consistency check: {e}")
        
        return flags
    
    def validate_value_ranges(self, gp_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if values are within reasonable ranges"""
        validation_rules = self.load_validation_rules()
        flags = []
        
        value_ranges = validation_rules["validation_rules"]["value_ranges"]
        
        # Check occupancy
        occupancy = gp_data.get("financial_metrics", {}).get("current_occupancy")
        if occupancy is not None:
            min_val = value_ranges["occupancy"]["min"]
            max_val = value_ranges["occupancy"]["max"]
            if occupancy < min_val or occupancy > max_val:
                flags.append({
                    "type": "value_range",
                    "metric": "current_occupancy",
                    "gp_value": occupancy,
                    "expected_range": f"{min_val}-{max_val}%",
                    "severity": "high",
                    "reason": f"Occupancy rate {occupancy}% is outside normal range"
                })
        
        # Check DSCR
        dscr = gp_data.get("debt_info", {}).get("dscr")
        if dscr is not None:
            min_val = value_ranges["dscr"]["min"]
            max_val = value_ranges["dscr"]["max"]
            if dscr < min_val or dscr > max_val:
                flags.append({
                    "type": "value_range",
                    "metric": "dscr",
                    "gp_value": dscr,
                    "expected_range": f"{min_val}-{max_val}",
                    "severity": "high",
                    "reason": f"DSCR {dscr} is outside normal range"
                })
        
        # Check cap rate
        cap_rate = gp_data.get("investment_metrics", {}).get("entry_cap_rate")
        if cap_rate is not None:
            min_val = value_ranges["cap_rate"]["min"]
            max_val = value_ranges["cap_rate"]["max"]
            if cap_rate < min_val or cap_rate > max_val:
                flags.append({
                    "type": "value_range",
                    "metric": "entry_cap_rate",
                    "gp_value": cap_rate,
                    "expected_range": f"{min_val}-{max_val}%",
                    "severity": "medium",
                    "reason": f"Cap rate {cap_rate}% is outside normal range"
                })
        
        return flags
    
    def compare_with_market_data(self, gp_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare GP data with market data"""
        validation_rules = self.load_validation_rules()
        flags = []
        
        market_comparison = validation_rules["validation_rules"]["market_comparison"]
        
        # Compare rent per sqft
        gp_rent = gp_data.get("financial_metrics", {}).get("rent_per_sqft")
        market_rent = market_data.get("market_data", {}).get("market_rent_per_sqft", {}).get("value")
        
        if gp_rent and market_rent:
            variance = abs(gp_rent - market_rent) / market_rent
            threshold = market_comparison["rent_variance"]["threshold"]
            
            if variance > threshold:
                flags.append({
                    "type": "market_comparison",
                    "metric": "rent_per_sqft",
                    "gp_value": gp_rent,
                    "market_value": market_rent,
                    "variance": variance,
                    "severity": "medium",
                    "reason": f"GP rent ${gp_rent}/sqft differs from market ${market_rent}/sqft by {variance:.1%}"
                })
        
        # Compare cap rates
        gp_cap_rate = gp_data.get("investment_metrics", {}).get("entry_cap_rate")
        market_cap_rate = market_data.get("market_data", {}).get("market_cap_rate", {}).get("value")
        
        if gp_cap_rate and market_cap_rate:
            variance = abs(gp_cap_rate - market_cap_rate) / market_cap_rate
            threshold = market_comparison["cap_rate_variance"]["threshold"]
            
            if variance > threshold:
                flags.append({
                    "type": "market_comparison",
                    "metric": "entry_cap_rate",
                    "gp_value": gp_cap_rate,
                    "market_value": market_cap_rate,
                    "variance": variance,
                    "severity": "high",
                    "reason": f"GP cap rate {gp_cap_rate}% differs from market {market_cap_rate}% by {variance:.1%}"
                })
        
        return flags
    
    def detect_statistical_outliers(self, gp_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use statistical methods to detect outliers"""
        flags = []
        
        if len(historical_data) < 10:  # Need sufficient data for statistical analysis
            return flags
        
        try:
            # Extract relevant metrics for outlier detection
            metrics = ["entry_cap_rate", "target_irr", "ltv_ratio", "dscr"]
            
            for metric in metrics:
                values = []
                for deal in historical_data:
                    if metric == "entry_cap_rate":
                        val = deal.get("investment_metrics", {}).get("entry_cap_rate")
                    elif metric == "target_irr":
                        val = deal.get("investment_metrics", {}).get("target_irr")
                    elif metric == "ltv_ratio":
                        val = deal.get("debt_info", {}).get("ltv_ratio")
                    elif metric == "dscr":
                        val = deal.get("debt_info", {}).get("dscr")
                    
                    if val is not None:
                        values.append(val)
                
                if len(values) >= 10:
                    # Use Isolation Forest for outlier detection
                    X = np.array(values).reshape(-1, 1)
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    outlier_labels = iso_forest.fit_predict(X)
                    
                    # Check if current GP value is an outlier
                    gp_value = None
                    if metric == "entry_cap_rate":
                        gp_value = gp_data.get("investment_metrics", {}).get("entry_cap_rate")
                    elif metric == "target_irr":
                        gp_value = gp_data.get("investment_metrics", {}).get("target_irr")
                    elif metric == "ltv_ratio":
                        gp_value = gp_data.get("debt_info", {}).get("ltv_ratio")
                    elif metric == "dscr":
                        gp_value = gp_data.get("debt_info", {}).get("dscr")
                    
                    if gp_value is not None:
                        gp_prediction = iso_forest.predict([[gp_value]])
                        if gp_prediction[0] == -1:  # Outlier
                            flags.append({
                                "type": "statistical_outlier",
                                "metric": metric,
                                "gp_value": gp_value,
                                "severity": "medium",
                                "reason": f"{metric} value {gp_value} is a statistical outlier compared to historical deals"
                            })
        
        except Exception as e:
            print(f"Error in statistical outlier detection: {e}")
        
        return flags
    
    def store_analysis_results(self, deal_id: str, flags: List[Dict[str, Any]]):
        """Store analysis results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for flag in flags:
            cursor.execute('''
                INSERT INTO analysis_results 
                (deal_id, analysis_type, metric_name, gp_value, market_value, variance, outlier_score, flag_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deal_id,
                flag["type"],
                flag["metric"],
                flag.get("gp_value"),
                flag.get("market_value"),
                flag.get("variance"),
                flag.get("outlier_score", 0.5),
                flag["reason"]
            ))
        
        conn.commit()
        conn.close()
    
    def analyze_deal(self, gp_data: Dict[str, Any], market_data: Dict[str, Any], deal_id: str = None) -> Dict[str, Any]:
        """Comprehensive analysis of a deal"""
        if deal_id is None:
            deal_id = gp_data.get("metadata", {}).get("source_document", "unknown")
        
        all_flags = []
        
        # Run all analysis types
        all_flags.extend(self.validate_financial_consistency(gp_data))
        all_flags.extend(self.validate_value_ranges(gp_data))
        all_flags.extend(self.compare_with_market_data(gp_data, market_data))
        
        # Statistical outlier detection (requires historical data)
        # all_flags.extend(self.detect_statistical_outliers(gp_data, historical_data))
        
        # Calculate overall risk score
        risk_score = self.calculate_risk_score(all_flags)
        
        # Store results
        self.store_analysis_results(deal_id, all_flags)
        
        return {
            "deal_id": deal_id,
            "analysis_date": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
            "risk_score": risk_score,
            "flags": all_flags,
            "summary": self.generate_summary(all_flags)
        }
    
    def calculate_risk_score(self, flags: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score based on flags"""
        if not flags:
            return 0.0
        
        severity_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
        total_weight = 0
        weighted_score = 0
        
        for flag in flags:
            severity = flag.get("severity", "medium")
            weight = severity_weights.get(severity, 0.6)
            weighted_score += weight
            total_weight += 1
        
        return min(weighted_score / total_weight, 1.0) if total_weight > 0 else 0.0
    
    def generate_summary(self, flags: List[Dict[str, Any]]) -> str:
        """Generate human-readable summary of analysis"""
        if not flags:
            return "No issues detected. Deal appears to be within normal parameters."
        
        high_flags = [f for f in flags if f.get("severity") == "high"]
        medium_flags = [f for f in flags if f.get("severity") == "medium"]
        
        summary = f"Analysis found {len(flags)} potential issues: "
        
        if high_flags:
            summary += f"{len(high_flags)} high-severity issues requiring immediate attention. "
        
        if medium_flags:
            summary += f"{len(medium_flags)} medium-severity issues to review. "
        
        summary += "Please review flagged metrics and verify assumptions."
        
        return summary


# Example usage
if __name__ == "__main__":
    # Initialize detector
    detector = OutlierDetector()
    
    # Sample GP data
    gp_data = {
        "financial_metrics": {
            "t12_revenue": 1000000,
            "t12_expenses": 400000,
            "t12_noi": 600000,
            "rent_per_sqft": 30.0
        },
        "debt_info": {
            "loan_amount": 4000000,
            "ltv_ratio": 80.0,
            "interest_rate": 5.0,
            "dscr": 1.2
        },
        "investment_metrics": {
            "entry_cap_rate": 6.0,
            "target_irr": 15.0
        }
    }
    
    # Sample market data
    market_data = {
        "market_data": {
            "market_rent_per_sqft": {"value": 25.0},
            "market_cap_rate": {"value": 5.5}
        }
    }
    
    # Analyze deal
    result = detector.analyze_deal(gp_data, market_data, "sample_deal")
    print(json.dumps(result, indent=2))
