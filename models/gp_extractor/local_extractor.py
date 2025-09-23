"""
Local GP Document Extractor (No AI APIs Required)
Uses rule-based extraction, OCR, and pattern matching
"""

import json
import re
import pytesseract
from PIL import Image
from typing import Dict, Any, List, Optional
from pathlib import Path
import PyPDF2
import pdfplumber
from docx import Document
import openpyxl
import pandas as pd


class LocalGPDocumentExtractor:
    def __init__(self):
        """Initialize the local GP document extractor"""
        self.schema_path = Path(__file__).parent.parent.parent / "schemas" / "canonical_schema.json"
        
        # Define extraction patterns
        self.patterns = {
            'purchase_price': [
                r'purchase\s+price[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'acquisition\s+price[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'total\s+investment[:\s]*\$?([0-9,]+(?:\.\d{2})?)'
            ],
            'occupancy': [
                r'occupancy[:\s]*([0-9]+\.?[0-9]*)\s*%',
                r'current\s+occupancy[:\s]*([0-9]+\.?[0-9]*)\s*%'
            ],
            'cap_rate': [
                r'cap\s+rate[:\s]*([0-9]+\.?[0-9]*)\s*%',
                r'capitalization\s+rate[:\s]*([0-9]+\.?[0-9]*)\s*%'
            ],
            'irr': [
                r'irr[:\s]*([0-9]+\.?[0-9]*)\s*%',
                r'internal\s+rate\s+of\s+return[:\s]*([0-9]+\.?[0-9]*)\s*%'
            ],
            'ltv': [
                r'ltv[:\s]*([0-9]+\.?[0-9]*)\s*%',
                r'loan\s+to\s+value[:\s]*([0-9]+\.?[0-9]*)\s*%'
            ],
            'dscr': [
                r'dscr[:\s]*([0-9]+\.?[0-9]*)',
                r'debt\s+service\s+coverage\s+ratio[:\s]*([0-9]+\.?[0-9]*)'
            ],
            'revenue': [
                r't12\s+revenue[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'trailing\s+twelve\s+month\s+revenue[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'annual\s+revenue[:\s]*\$?([0-9,]+(?:\.\d{2})?)'
            ],
            'expenses': [
                r't12\s+expenses[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'trailing\s+twelve\s+month\s+expenses[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'annual\s+expenses[:\s]*\$?([0-9,]+(?:\.\d{2})?)'
            ],
            'noi': [
                r't12\s+noi[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'net\s+operating\s+income[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                r'noi[:\s]*\$?([0-9,]+(?:\.\d{2})?)'
            ]
        }
        
    def load_schema(self) -> Dict[str, Any]:
        """Load the canonical schema"""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            # Try pdfplumber first (better for tables)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                text += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
        
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # Extract tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
        
        return text
    
    def extract_text_from_excel(self, file_path: str) -> str:
        """Extract text from Excel file"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text = ""
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                text += f"Sheet: {sheet_name}\n"
                text += df.to_string() + "\n\n"
            
            return text
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(str(file_path))
        elif extension == '.docx':
            return self.extract_text_from_docx(str(file_path))
        elif extension in ['.xlsx', '.xls']:
            return self.extract_text_from_excel(str(file_path))
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def clean_number(self, text: str) -> Optional[float]:
        """Clean and convert number text to float"""
        if not text:
            return None
        
        # Remove commas and convert to float
        cleaned = re.sub(r'[,$]', '', text.strip())
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def extract_value_by_pattern(self, text: str, patterns: List[str]) -> Optional[float]:
        """Extract a value using regex patterns"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match
                value = self.clean_number(matches[0])
                if value is not None:
                    return value
        return None
    
    def extract_property_info(self, text: str) -> Dict[str, Any]:
        """Extract property information using patterns"""
        property_info = {}
        
        # Extract address (look for common address patterns)
        address_patterns = [
            r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir|Court|Ct))',
            r'address[:\s]*([^\n]+)',
            r'property\s+address[:\s]*([^\n]+)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                property_info['address'] = match.group(1).strip()
                break
        
        # Extract city and state
        city_state_pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})'
        match = re.search(city_state_pattern, text)
        if match:
            property_info['city'] = match.group(1).strip()
            property_info['state'] = match.group(2).strip()
        
        # Extract property type
        property_type_patterns = [
            r'multifamily|apartment|residential',
            r'office|commercial',
            r'retail|shopping',
            r'industrial|warehouse',
            r'hotel|hospitality',
            r'mixed\s+use'
        ]
        
        for pattern in property_type_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                property_info['property_type'] = pattern.replace('|', '_').replace(' ', '_')
                break
        
        # Extract square footage
        sqft_patterns = [
            r'(\d+(?:,\d{3})*)\s*(?:sq\s*ft|square\s*feet|sf)',
            r'total\s*(?:sq\s*ft|square\s*feet|sf)[:\s]*(\d+(?:,\d{3})*)'
        ]
        
        for pattern in sqft_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                property_info['total_sqft'] = self.clean_number(match.group(1))
                break
        
        # Extract year built
        year_pattern = r'(?:built|constructed|year)[:\s]*(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            property_info['year_built'] = int(match.group(1))
        
        return property_info
    
    def extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics using patterns"""
        metrics = {}
        
        # Extract purchase price
        purchase_price = self.extract_value_by_pattern(text, self.patterns['purchase_price'])
        if purchase_price:
            metrics['purchase_price'] = purchase_price
        
        # Extract occupancy
        occupancy = self.extract_value_by_pattern(text, self.patterns['occupancy'])
        if occupancy:
            metrics['current_occupancy'] = occupancy
        
        # Extract revenue
        revenue = self.extract_value_by_pattern(text, self.patterns['revenue'])
        if revenue:
            metrics['t12_revenue'] = revenue
        
        # Extract expenses
        expenses = self.extract_value_by_pattern(text, self.patterns['expenses'])
        if expenses:
            metrics['t12_expenses'] = expenses
        
        # Extract NOI
        noi = self.extract_value_by_pattern(text, self.patterns['noi'])
        if noi:
            metrics['t12_noi'] = noi
        
        # Calculate NOI if not found but revenue and expenses are available
        if 't12_noi' not in metrics and 't12_revenue' in metrics and 't12_expenses' in metrics:
            metrics['t12_noi'] = metrics['t12_revenue'] - metrics['t12_expenses']
        
        return metrics
    
    def extract_debt_info(self, text: str) -> Dict[str, Any]:
        """Extract debt information using patterns"""
        debt_info = {}
        
        # Extract loan amount
        loan_patterns = [
            r'loan\s+amount[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
            r'mortgage\s+amount[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
            r'debt\s+amount[:\s]*\$?([0-9,]+(?:\.\d{2})?)'
        ]
        
        loan_amount = self.extract_value_by_pattern(text, loan_patterns)
        if loan_amount:
            debt_info['loan_amount'] = loan_amount
        
        # Extract LTV
        ltv = self.extract_value_by_pattern(text, self.patterns['ltv'])
        if ltv:
            debt_info['ltv_ratio'] = ltv
        
        # Extract interest rate
        interest_patterns = [
            r'interest\s+rate[:\s]*([0-9]+\.?[0-9]*)\s*%',
            r'mortgage\s+rate[:\s]*([0-9]+\.?[0-9]*)\s*%',
            r'loan\s+rate[:\s]*([0-9]+\.?[0-9]*)\s*%'
        ]
        
        interest_rate = self.extract_value_by_pattern(text, interest_patterns)
        if interest_rate:
            debt_info['interest_rate'] = interest_rate
        
        # Extract DSCR
        dscr = self.extract_value_by_pattern(text, self.patterns['dscr'])
        if dscr:
            debt_info['dscr'] = dscr
        
        return debt_info
    
    def extract_investment_metrics(self, text: str) -> Dict[str, Any]:
        """Extract investment metrics using patterns"""
        metrics = {}
        
        # Extract cap rate
        cap_rate = self.extract_value_by_pattern(text, self.patterns['cap_rate'])
        if cap_rate:
            metrics['entry_cap_rate'] = cap_rate
        
        # Extract IRR
        irr = self.extract_value_by_pattern(text, self.patterns['irr'])
        if irr:
            metrics['target_irr'] = irr
        
        # Extract equity multiple
        multiple_patterns = [
            r'equity\s+multiple[:\s]*([0-9]+\.?[0-9]*)',
            r'total\s+return[:\s]*([0-9]+\.?[0-9]*)x',
            r'multiple[:\s]*([0-9]+\.?[0-9]*)x'
        ]
        
        multiple = self.extract_value_by_pattern(text, multiple_patterns)
        if multiple:
            metrics['target_equity_multiple'] = multiple
        
        return metrics
    
    def calculate_confidence_score(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted fields"""
        total_fields = 0
        extracted_fields = 0
        
        # Count total possible fields
        schema = self.load_schema()
        for section in schema.values():
            if isinstance(section, dict):
                for field in section.values():
                    if isinstance(field, dict) and field.get('required'):
                        total_fields += 1
        
        # Count extracted fields
        for section_name, section_data in extracted_data.items():
            if isinstance(section_data, dict):
                for field_name, field_value in section_data.items():
                    if field_value is not None and field_value != "":
                        extracted_fields += 1
        
        return extracted_fields / max(total_fields, 1)
    
    def extract_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from a GP document"""
        try:
            # Extract text from file
            text = self.extract_text_from_file(file_path)
            
            if not text.strip():
                raise ValueError("No text extracted from file")
            
            # Extract data using patterns
            extracted_data = {
                "property_info": self.extract_property_info(text),
                "financial_metrics": self.extract_financial_metrics(text),
                "debt_info": self.extract_debt_info(text),
                "investment_metrics": self.extract_investment_metrics(text),
                "metadata": {
                    "source_document": Path(file_path).name,
                    "extraction_date": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
                    "extraction_method": "gp_document_local",
                    "confidence_score": 0.0  # Will be calculated below
                }
            }
            
            # Calculate confidence score
            confidence = self.calculate_confidence_score(extracted_data)
            extracted_data["metadata"]["confidence_score"] = confidence
            
            return extracted_data
            
        except Exception as e:
            print(f"Error extracting data from {file_path}: {e}")
            return {"error": str(e)}
    
    def batch_extract(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Extract data from multiple files"""
        results = []
        for file_path in file_paths:
            result = self.extract_data(file_path)
            results.append(result)
        return results


# Example usage
if __name__ == "__main__":
    # Initialize extractor
    extractor = LocalGPDocumentExtractor()
    
    # Extract from a single file
    result = extractor.extract_data("sample_gp_document.pdf")
    print(json.dumps(result, indent=2))
