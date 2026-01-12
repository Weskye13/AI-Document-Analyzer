"""
AI Document Analyzer - Document Extractor
==========================================

Uses Claude AI to extract structured data from documents.
Supports OCR for images and text extraction from PDFs.

Author: Law Office of Joshua E. Bardavid
Version: 1.0.0
Date: January 2026
"""

import base64
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import DOCUMENT_TYPES, AI_CONFIG, ANTHROPIC_API_KEY


class DocumentExtractor:
    """
    AI-powered document data extractor using Claude Vision.
    
    Supports:
    - PDF documents (converted to images)
    - Image files (PNG, JPG, etc.)
    - Scanned documents
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the document extractor.
        
        Args:
            verbose: Print status messages
        """
        self.verbose = verbose
        self.client = None
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def log(self, message: str):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(f"  {message}")
    
    # ========================================================================
    # FILE PROCESSING
    # ========================================================================
    
    def load_document(self, file_path: str) -> Tuple[List[str], str]:
        """
        Load a document and convert to base64 images.
        
        Args:
            file_path: Path to document (PDF or image)
            
        Returns:
            Tuple of (list of base64 images, media type)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return self._load_pdf(path)
        elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            return self._load_image(path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def _load_pdf(self, path: Path) -> Tuple[List[str], str]:
        """Load PDF and convert pages to images."""
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
        
        self.log(f"📄 Loading PDF: {path.name}")
        
        images = []
        doc = fitz.open(path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render at 2x resolution for better OCR
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PNG bytes
            png_bytes = pix.tobytes("png")
            b64 = base64.standard_b64encode(png_bytes).decode('utf-8')
            images.append(b64)
            
            self.log(f"   Page {page_num + 1}/{len(doc)} converted")
        
        doc.close()
        return images, "image/png"
    
    def _load_image(self, path: Path) -> Tuple[List[str], str]:
        """Load single image file."""
        self.log(f"🖼️ Loading image: {path.name}")
        
        suffix = path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        
        media_type = media_type_map.get(suffix, 'image/png')
        
        with open(path, 'rb') as f:
            b64 = base64.standard_b64encode(f.read()).decode('utf-8')
        
        return [b64], media_type
    
    # ========================================================================
    # DOCUMENT TYPE DETECTION
    # ========================================================================
    
    def detect_document_type(self, images: List[str], media_type: str) -> str:
        """
        Use AI to detect the type of document.
        
        Args:
            images: List of base64 encoded images
            media_type: MIME type of images
            
        Returns:
            Document type key from DOCUMENT_TYPES
        """
        self.log("🔍 Detecting document type...")
        
        # Build document type descriptions
        type_descriptions = []
        for key, config in DOCUMENT_TYPES.items():
            type_descriptions.append(f"- {key}: {config['display_name']} - {config['description']}")
        
        prompt = f"""Analyze this document and determine its type.

Available document types:
{chr(10).join(type_descriptions)}

Respond with ONLY the document type key (e.g., "passport", "questionnaire", "ead_card").
If the document doesn't match any type, respond with "unknown".
"""
        
        # Build message with first page image
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": images[0]
                }
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=100,
            temperature=0,
            messages=[{"role": "user", "content": content}]
        )
        
        doc_type = response.content[0].text.strip().lower()
        
        # Validate response
        if doc_type in DOCUMENT_TYPES:
            self.log(f"   ✓ Detected: {DOCUMENT_TYPES[doc_type]['display_name']}")
            return doc_type
        else:
            self.log(f"   ⚠ Unknown document type: {doc_type}")
            return "unknown"
    
    # ========================================================================
    # DATA EXTRACTION
    # ========================================================================
    
    def extract_data(self, file_path: str, document_type: str = None) -> Dict[str, Any]:
        """
        Extract structured data from a document.
        
        Args:
            file_path: Path to document
            document_type: Optional type override (auto-detects if not provided)
            
        Returns:
            Dict with extracted data including:
            - document_type: Detected or specified type
            - confidence: Overall extraction confidence (0-1)
            - fields: Dict of field_key -> {value, confidence, source_text}
            - raw_text: Full OCR text
            - errors: List of any extraction errors
        """
        self.log(f"\n{'='*60}")
        self.log(f"📋 EXTRACTING DATA FROM: {Path(file_path).name}")
        self.log(f"{'='*60}")
        
        # Load document
        images, media_type = self.load_document(file_path)
        
        # Detect or validate document type
        if document_type is None:
            document_type = self.detect_document_type(images, media_type)
        
        if document_type == "unknown" or document_type not in DOCUMENT_TYPES:
            return {
                'document_type': 'unknown',
                'confidence': 0,
                'fields': {},
                'raw_text': '',
                'errors': ['Could not determine document type']
            }
        
        doc_config = DOCUMENT_TYPES[document_type]
        
        # Extract data for this document type
        extracted = self._extract_fields(images, media_type, document_type, doc_config)
        
        return extracted
    
    def _extract_fields(self, images: List[str], media_type: str, 
                        document_type: str, doc_config: Dict) -> Dict[str, Any]:
        """
        Extract specific fields from document using AI.
        
        Args:
            images: List of base64 images
            media_type: Image MIME type
            document_type: Document type key
            doc_config: Document type configuration
            
        Returns:
            Extraction results dictionary
        """
        self.log(f"\n📝 Extracting {doc_config['display_name']} fields...")
        
        # Build field extraction prompt
        field_list = []
        for field in doc_config['fields']:
            field_list.append(f"- {field['key']}: {field['label']}")
        
        prompt = f"""You are an expert document analyzer. Extract the following information from this {doc_config['display_name']}.

FIELDS TO EXTRACT:
{chr(10).join(field_list)}

INSTRUCTIONS:
1. Carefully examine the document image(s)
2. Extract each field value exactly as shown in the document
3. For dates, use YYYY-MM-DD format
4. For phone numbers, include country code if visible
5. For A-numbers, include the "A" prefix (e.g., A123456789)
6. If a field is not visible or unclear, use null
7. Include a confidence score (0.0-1.0) for each field

RESPOND WITH VALID JSON ONLY in this exact format:
{{
    "fields": {{
        "field_key": {{
            "value": "extracted value or null",
            "confidence": 0.95,
            "source_text": "exact text from document"
        }}
    }},
    "raw_text": "full OCR text from document",
    "overall_confidence": 0.9,
    "notes": "any relevant observations"
}}

Be precise and accurate. Immigration documents require exact information."""

        # Build message with all images
        content = []
        for i, img in enumerate(images):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": img
                }
            })
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        try:
            response = self.client.messages.create(
                model=AI_CONFIG['model'],
                max_tokens=AI_CONFIG['max_tokens'],
                temperature=AI_CONFIG['temperature'],
                messages=[{"role": "user", "content": content}]
            )
            
            response_text = response.content[0].text
            
            # Parse JSON response
            # Try to find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
            
            # Build result structure
            extracted = {
                'document_type': document_type,
                'confidence': result.get('overall_confidence', 0.8),
                'fields': result.get('fields', {}),
                'raw_text': result.get('raw_text', ''),
                'notes': result.get('notes', ''),
                'errors': []
            }
            
            # Log extracted fields
            self.log(f"\n   Extracted {len(extracted['fields'])} fields:")
            for key, data in extracted['fields'].items():
                value = data.get('value', 'N/A')
                conf = data.get('confidence', 0)
                if value:
                    self.log(f"   ✓ {key}: {value} (conf: {conf:.0%})")
            
            return extracted
            
        except json.JSONDecodeError as e:
            self.log(f"   ⚠ JSON parse error: {e}")
            return {
                'document_type': document_type,
                'confidence': 0,
                'fields': {},
                'raw_text': '',
                'errors': [f"Failed to parse AI response: {e}"]
            }
        except Exception as e:
            self.log(f"   ⚠ Extraction error: {e}")
            return {
                'document_type': document_type,
                'confidence': 0,
                'fields': {},
                'raw_text': '',
                'errors': [str(e)]
            }
    
    # ========================================================================
    # SPECIALIZED EXTRACTORS
    # ========================================================================
    
    def extract_a_number(self, file_path: str) -> Optional[str]:
        """
        Quick extraction of just A-number from any document.
        
        Args:
            file_path: Path to document
            
        Returns:
            A-number string or None
        """
        self.log(f"🔍 Quick A-number extraction: {Path(file_path).name}")
        
        images, media_type = self.load_document(file_path)
        
        prompt = """Look for an Alien Registration Number (A-Number) in this document.
A-Numbers are typically formatted as "A" followed by 9 digits (e.g., A123456789).

If you find an A-Number, respond with ONLY the A-Number.
If no A-Number is found, respond with "NOT_FOUND".
"""
        
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": images[0]
                }
            },
            {"type": "text", "text": prompt}
        ]
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=50,
            temperature=0,
            messages=[{"role": "user", "content": content}]
        )
        
        result = response.content[0].text.strip()
        
        if result == "NOT_FOUND":
            self.log("   ⚠ No A-Number found")
            return None
        
        # Clean and validate A-number
        a_num = re.sub(r'[^A0-9]', '', result.upper())
        if re.match(r'^A?\d{9}$', a_num):
            if not a_num.startswith('A'):
                a_num = 'A' + a_num
            self.log(f"   ✓ Found: {a_num}")
            return a_num
        
        self.log(f"   ⚠ Invalid A-Number format: {result}")
        return None
    
    def identify_client(self, file_path: str) -> Dict[str, Optional[str]]:
        """
        Quick identification of client from any document.
        
        Args:
            file_path: Path to document
            
        Returns:
            Dict with 'name' and 'a_number' keys
        """
        self.log(f"🔍 Identifying client: {Path(file_path).name}")
        
        images, media_type = self.load_document(file_path)
        
        prompt = """Identify the primary person in this document.

Extract:
1. Full name (LAST NAME, First Name Middle Name format)
2. A-Number if visible (A + 9 digits)

Respond with JSON ONLY:
{"name": "LAST, First Middle", "a_number": "A123456789 or null"}"""
        
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": images[0]
                }
            },
            {"type": "text", "text": prompt}
        ]
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=200,
            temperature=0,
            messages=[{"role": "user", "content": content}]
        )
        
        try:
            result = json.loads(response.content[0].text)
            self.log(f"   ✓ Name: {result.get('name', 'Unknown')}")
            self.log(f"   ✓ A-Number: {result.get('a_number', 'Not found')}")
            return result
        except:
            return {'name': None, 'a_number': None}


# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_extractor.py <document_path>")
        print("\nSupported formats: PDF, PNG, JPG, GIF, WEBP")
        sys.exit(1)
    
    doc_path = sys.argv[1]
    
    try:
        extractor = DocumentExtractor(verbose=True)
        
        print("\n" + "="*60)
        print("AI DOCUMENT EXTRACTOR - TEST MODE")
        print("="*60)
        
        # First, identify the client
        print("\n--- CLIENT IDENTIFICATION ---")
        client_info = extractor.identify_client(doc_path)
        
        # Then extract full data
        print("\n--- FULL EXTRACTION ---")
        result = extractor.extract_data(doc_path)
        
        print("\n" + "="*60)
        print("EXTRACTION RESULTS")
        print("="*60)
        print(f"Document Type: {result['document_type']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Errors: {result['errors']}")
        print("\nExtracted Fields:")
        for key, data in result['fields'].items():
            print(f"  {key}: {data.get('value')} (conf: {data.get('confidence', 0):.0%})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
