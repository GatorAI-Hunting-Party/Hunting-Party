"""
GP Document Extractor Model
Extracts structured real estate data from GP investment materials
Uses local processing (no external APIs required)
"""

import json
from typing import Dict, Any, List
from pathlib import Path
from .local_extractor import LocalGPDocumentExtractor


class GPDocumentExtractor:
    def __init__(self, api_key: str = None):
        """Initialize the GP document extractor"""
        # Use local extractor (no API key required)
        self.local_extractor = LocalGPDocumentExtractor()
        self.schema_path = Path(__file__).parent.parent.parent / "schemas" / "canonical_schema.json"
        
    def load_schema(self) -> Dict[str, Any]:
        """Load the canonical schema"""
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_text_from_excel(self, file_path: str) -> str:
        """Extract text from Excel file"""
        workbook = openpyxl.load_workbook(file_path)
        text = ""
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            text += f"Sheet: {sheet_name}\n"
            for row in sheet.iter_rows(values_only=True):
                text += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
        return text
    
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
    
    def create_extraction_prompt(self, text: str, schema: Dict[str, Any]) -> str:
        """Create the extraction prompt for the LLM"""
        return f"""
You are a real estate investment analyst extracting structured data from GP investment materials.

Extract the following information from the provided text and return it as valid JSON matching this schema:

{schema}

IMPORTANT RULES:
1. Return ONLY valid JSON, no additional text
2. Use "null" for missing values, not empty strings
3. Include confidence scores (0-1) for each extracted field
4. Specify units for all numeric values
5. If a value is not found, use null
6. Be conservative - don't guess or estimate

Text to analyze:
{text}

Return the extracted data as JSON:
"""
    
    def extract_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from a GP document"""
        # Use local extractor (no external APIs)
        return self.local_extractor.extract_data(file_path)
    
    def batch_extract(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Extract data from multiple files"""
        results = []
        for file_path in file_paths:
            result = self.extract_data(file_path)
            results.append(result)
        return results


# Example usage
if __name__ == "__main__":
    # Initialize extractor (no API key required)
    extractor = GPDocumentExtractor()
    
    # Extract from a single file
    result = extractor.extract_data("sample_gp_document.pdf")
    print(json.dumps(result, indent=2))
