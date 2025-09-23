"""
FastAPI Backend for HuntingParty.ai
Simple API for document processing and analysis
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from pathlib import Path
import sqlite3
from typing import List, Dict, Any
import uvicorn

# Import our models
import sys
sys.path.append(str(Path(__file__).parent.parent))
from models.gp_extractor.model import GPDocumentExtractor
from models.market_extractor.model import MarketDataExtractor
from models.outlier_detector.model import OutlierDetector

app = FastAPI(
    title="HuntingParty.ai API",
    description="AI-powered real estate deal analysis platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
gp_extractor = None
market_extractor = None
outlier_detector = None

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global gp_extractor, market_extractor, outlier_detector
    
    # Initialize GP extractor (no API key required)
    gp_extractor = GPDocumentExtractor()
    market_extractor = MarketDataExtractor()
    outlier_detector = OutlierDetector()
    
    print("✅ All models initialized successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "HuntingParty.ai API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models": {
            "gp_extractor": gp_extractor is not None,
            "market_extractor": market_extractor is not None,
            "outlier_detector": outlier_detector is not None
        }
    }

@app.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a GP document"""
    try:
        # Validate file type
        allowed_types = [".pdf", ".docx", ".xlsx", ".xls"]
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed types: {allowed_types}"
            )
        
        # Save file temporarily
        upload_dir = Path("data/raw/gp_documents")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract data using GP extractor
        if gp_extractor is None:
            raise HTTPException(
                status_code=500,
                detail="GP extractor not initialized."
            )
        
        extracted_data = gp_extractor.extract_data(str(file_path))
        
        # Store in database
        deal_id = store_deal_data(extracted_data, file.filename)
        
        return {
            "message": "Document processed successfully",
            "deal_id": deal_id,
            "extracted_data": extracted_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/{location}/{property_type}")
async def get_market_data(location: str, property_type: str):
    """Get market data for a specific location and property type"""
    try:
        if market_extractor is None:
            raise HTTPException(status_code=500, detail="Market extractor not initialized")
        
        market_data = market_extractor.extract_market_data(location, property_type)
        return market_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{deal_id}")
async def analyze_deal(deal_id: str):
    """Analyze a deal for outliers and inconsistencies"""
    try:
        if outlier_detector is None:
            raise HTTPException(status_code=500, detail="Outlier detector not initialized")
        
        # Get GP data
        gp_data = get_deal_data(deal_id)
        if not gp_data:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        # Get market data
        location = f"{gp_data['property_info']['city']}, {gp_data['property_info']['state']}"
        property_type = gp_data['property_info']['property_type']
        market_data = market_extractor.extract_market_data(location, property_type)
        
        # Analyze deal
        analysis_result = outlier_detector.analyze_deal(gp_data, market_data, deal_id)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deals")
async def list_deals():
    """List all processed deals"""
    try:
        conn = sqlite3.connect("hunting_party.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT deal_id, source_document, extraction_date, confidence_score
            FROM deals
            ORDER BY extraction_date DESC
        ''')
        
        deals = []
        for row in cursor.fetchall():
            deals.append({
                "deal_id": row[0],
                "source_document": row[1],
                "extraction_date": row[2],
                "confidence_score": row[3]
            })
        
        conn.close()
        return {"deals": deals}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deals/{deal_id}")
async def get_deal(deal_id: str):
    """Get specific deal data"""
    try:
        deal_data = get_deal_data(deal_id)
        if not deal_data:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        return deal_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def store_deal_data(data: Dict[str, Any], filename: str) -> str:
    """Store deal data in database"""
    conn = sqlite3.connect("hunting_party.db")
    cursor = conn.cursor()
    
    # Create deals table if it doesn't exist
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
    
    # Generate deal ID
    deal_id = f"deal_{len(cursor.execute('SELECT * FROM deals').fetchall()) + 1}"
    
    # Store data
    cursor.execute('''
        INSERT INTO deals (deal_id, source_document, extraction_date, confidence_score, data_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        deal_id,
        filename,
        data.get("metadata", {}).get("extraction_date", "2024-01-01T00:00:00Z"),
        data.get("metadata", {}).get("confidence_score", 0.5),
        json.dumps(data)
    ))
    
    conn.commit()
    conn.close()
    
    return deal_id

def get_deal_data(deal_id: str) -> Dict[str, Any]:
    """Get deal data from database"""
    conn = sqlite3.connect("hunting_party.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT data_json FROM deals WHERE deal_id = ?', (deal_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
