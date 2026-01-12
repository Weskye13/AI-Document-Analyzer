"""
AI Document Analyzer - Document Extractor
==========================================

Uses Claude AI to extract structured data from documents.
Handles questionnaires with family members and history sections.

Author: Law Office of Joshua E. Bardavid
Version: 2.0.0
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

from config import (
    DOCUMENT_TYPES, QUESTIONNAIRE_TYPES, AI_CONFIG, ANTHROPIC_API_KEY,
    FAMILY_RELATIONSHIPS, HISTORY_TYPES, get_all_document_types, detect_questionnaire_type
)


class DocumentExtractor:
    """
    AI-powered document data extractor using Claude Vision.
    
    Extracts:
    - Primary contact fields
    - Family member information
    - Address, employment, education history
    - Other questionnaire-specific data
    """
    
    def __init__(self, verbose: bool = True):
        """Initialize the document extractor."""
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
        """Load a document and convert to base64 images."""
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
            mat = fitz.Matrix(2, 2)  # 2x resolution
            pix = page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
            b64 = base64.standard_b64encode(png_bytes).decode('utf-8')
            images.append(b64)
            self.log(f"   Page {page_num + 1}/{len(doc)} converted")
        
        doc.close()
        return images, "image/png"
    
    def _load_image(self, path: Path) -> Tuple[List[str], str]:
        """Load single image file."""
        self.log(f"🖼️ Loading image: {path.name}")
        
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        
        media_type = media_type_map.get(path.suffix.lower(), 'image/png')
        
        with open(path, 'rb') as f:
            b64 = base64.standard_b64encode(f.read()).decode('utf-8')
        
        return [b64], media_type
    
    # ========================================================================
    # DOCUMENT TYPE DETECTION
    # ========================================================================
    
    def detect_document_type(self, images: List[str], media_type: str) -> Tuple[str, Optional[str]]:
        """
        Detect document type and questionnaire subtype.
        
        Returns:
            Tuple of (document_type, questionnaire_type or None)
        """
        self.log("🔍 Detecting document type...")
        
        # Build type descriptions
        all_types = get_all_document_types()
        type_list = []
        for key, config in all_types.items():
            type_list.append(f"- {key}: {config['display_name']}")
        
        prompt = f"""Analyze this document and identify its type.

Known document types:
{chr(10).join(type_list)}

Respond in JSON format:
{{"document_type": "type_key", "questionnaire_name": "specific questionnaire name if visible"}}

If unknown, use: {{"document_type": "unknown", "questionnaire_name": null}}
"""
        
        content = [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": images[0]}},
            {"type": "text", "text": prompt}
        ]
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=200,
            temperature=0,
            messages=[{"role": "user", "content": content}]
        )
        
        result_text = response.content[0].text.strip()
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', result_text)
            if json_match:
                result = json.loads(json_match.group())
                doc_type = result.get('document_type', 'unknown')
                q_name = result.get('questionnaire_name')
                
                # Try to match questionnaire type from name
                q_type = None
                if q_name:
                    q_type = detect_questionnaire_type(q_name)
                
                self.log(f"   Detected: {doc_type}" + (f" ({q_type})" if q_type else ""))
                return doc_type, q_type
        except:
            pass
        
        # Fallback: check if text matches any type
        for key in all_types:
            if key in result_text.lower():
                self.log(f"   Detected: {key}")
                return key, None
        
        self.log("   ⚠ Could not detect document type")
        return 'unknown', None
    
    # ========================================================================
    # MAIN EXTRACTION
    # ========================================================================
    
    def extract_data(self, file_path: str, document_type: str = None) -> Dict[str, Any]:
        """
        Extract all data from document.
        
        Returns dict with:
        - document_type: str
        - questionnaire_type: str or None
        - confidence: float
        - fields: Dict of primary fields
        - family_members: List of family member dicts
        - history: Dict of history records by type
        - other: Dict of other extracted info
        """
        self.log(f"\n{'='*60}")
        self.log(f"📊 EXTRACTING DATA FROM: {Path(file_path).name}")
        self.log(f"{'='*60}")
        
        # Load document
        images, media_type = self.load_document(file_path)
        
        # Detect type if not specified
        q_type = None
        if not document_type:
            document_type, q_type = self.detect_document_type(images, media_type)
        
        # Get configuration
        all_types = get_all_document_types()
        if document_type not in all_types:
            self.log(f"   ⚠ Unknown document type: {document_type}")
            return {
                'document_type': document_type,
                'questionnaire_type': q_type,
                'confidence': 0.0,
                'fields': {},
                'family_members': [],
                'history': {},
                'other': {},
                'error': f"Unknown document type: {document_type}"
            }
        
        config = all_types[document_type]
        is_questionnaire = document_type in QUESTIONNAIRE_TYPES
        
        # Build extraction prompt
        prompt = self._build_extraction_prompt(config, is_questionnaire)
        
        # Send to AI with all pages
        self.log(f"🤖 Sending {len(images)} page(s) to AI...")
        
        content = []
        for i, img in enumerate(images):
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": img}
            })
        content.append({"type": "text", "text": prompt})
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=AI_CONFIG['max_tokens'],
            temperature=AI_CONFIG['temperature'],
            messages=[{"role": "user", "content": content}]
        )
        
        result_text = response.content[0].text.strip()
        
        # Parse response
        extracted = self._parse_extraction_response(result_text, config, is_questionnaire)
        extracted['document_type'] = document_type
        extracted['questionnaire_type'] = q_type
        
        self._log_extraction_summary(extracted)
        
        return extracted
    
    def _build_extraction_prompt(self, config: Dict, is_questionnaire: bool) -> str:
        """Build the extraction prompt based on document config."""
        
        # Get field definitions
        if is_questionnaire:
            field_defs = config.get('fields', {})
            primary_fields = field_defs.get('primary', [])
            family_defs = field_defs.get('family_members', [])
            history_defs = field_defs.get('history', {})
            other_defs = field_defs.get('other', [])
        else:
            primary_fields = config.get('fields', [])
            family_defs = []
            history_defs = {}
            other_defs = []
        
        # Build field list for primary
        primary_list = []
        for f in primary_fields:
            primary_list.append(f"- {f['key']}: {f['label']}")
        
        # Build family member section
        family_section = ""
        if family_defs:
            family_parts = []
            for fm_def in family_defs:
                rel = fm_def['relationship']
                fields = fm_def.get('fields', [])
                family_parts.append(f"  - {rel}: Extract {', '.join(fields[:5])}...")
            family_section = f"""
FAMILY MEMBERS:
Extract information for each family member found:
{chr(10).join(family_parts)}
"""
        
        # Build history section
        history_section = ""
        if history_defs:
            history_parts = []
            for h_type, h_config in history_defs.items():
                label = h_config.get('section_label', h_type) if isinstance(h_config, dict) else h_type
                history_parts.append(f"  - {h_type}: {label}")
            history_section = f"""
HISTORY RECORDS:
Extract all historical records:
{chr(10).join(history_parts)}
"""
        
        prompt = f"""Extract all information from this {config['display_name']}.

PRIMARY CONTACT FIELDS:
{chr(10).join(primary_list)}
{family_section}
{history_section}

IMPORTANT:
- Extract exactly what is written, do not infer or assume
- For handwritten text, indicate confidence (high/medium/low)
- Dates should be in YYYY-MM-DD format when possible
- A-Numbers should include all digits (9 digits)
- If a field is empty or not visible, omit it

Respond in JSON format:
{{
    "confidence": 0.0-1.0,
    "fields": {{
        "field_key": {{"value": "extracted value", "confidence": 0.0-1.0}},
        ...
    }},
    "family_members": [
        {{
            "relationship": "spouse|child|father|mother|sibling",
            "data": {{"first_name": "...", "last_name": "...", ...}},
            "confidence": 0.0-1.0
        }},
        ...
    ],
    "history": {{
        "address": [
            {{"data": {{"address_line1": "...", "city": "...", ...}}, "is_current": true, "confidence": 0.9}},
            ...
        ],
        "employment": [...],
        "education": [...]
    }},
    "other": {{
        "any_other_relevant_info": "..."
    }}
}}

Extract ALL visible information, even if some sections are empty.
"""
        return prompt
    
    def _parse_extraction_response(self, response_text: str, config: Dict, is_questionnaire: bool) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        
        result = {
            'confidence': 0.0,
            'fields': {},
            'family_members': [],
            'history': {},
            'other': {}
        }
        
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed = json.loads(json_text)
                
                result['confidence'] = parsed.get('confidence', 0.8)
                result['fields'] = parsed.get('fields', {})
                result['family_members'] = parsed.get('family_members', [])
                result['history'] = parsed.get('history', {})
                result['other'] = parsed.get('other', {})
        
        except json.JSONDecodeError as e:
            self.log(f"   ⚠ JSON parse error: {e}")
            # Try to extract key-value pairs manually
            result['other']['raw_response'] = response_text
        
        return result
    
    def _log_extraction_summary(self, extracted: Dict):
        """Log summary of extracted data."""
        self.log(f"\n   📋 EXTRACTION SUMMARY:")
        self.log(f"      Confidence: {extracted.get('confidence', 0):.0%}")
        self.log(f"      Fields: {len(extracted.get('fields', {}))}")
        self.log(f"      Family members: {len(extracted.get('family_members', []))}")
        
        history = extracted.get('history', {})
        for h_type, records in history.items():
            if records:
                self.log(f"      {h_type}: {len(records)} records")
    
    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================
    
    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Convenience method - auto-detect type and extract."""
        return self.extract_data(file_path)
    
    def extract_questionnaire(self, file_path: str, questionnaire_type: str) -> Dict[str, Any]:
        """Extract from a known questionnaire type."""
        if questionnaire_type not in QUESTIONNAIRE_TYPES:
            raise ValueError(f"Unknown questionnaire type: {questionnaire_type}")
        return self.extract_data(file_path, document_type=questionnaire_type)


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DOCUMENT EXTRACTOR - TEST MODE")
    print("="*60)
    
    try:
        extractor = DocumentExtractor(verbose=True)
        
        # Test with a sample file if provided
        import sys
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            result = extractor.extract_from_file(file_path)
            print("\n" + "="*60)
            print("EXTRACTION RESULT:")
            print("="*60)
            print(json.dumps(result, indent=2, default=str))
        else:
            print("\nUsage: python document_extractor.py <file_path>")
            print("\nSupported formats: PDF, PNG, JPG, JPEG, GIF, WEBP")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
