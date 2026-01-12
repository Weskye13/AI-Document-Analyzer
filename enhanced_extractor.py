"""
AI Document Analyzer - Enhanced Document Extractor
===================================================

Multi-pass extraction system inspired by Ralph Brainstormer's
"Debate & Consensus" pattern for higher accuracy extraction.

IMPROVEMENTS OVER BASE EXTRACTOR:
1. Self-Critique Pass - AI reviews its own extraction for errors
2. Confidence-Based Re-Extraction - Low-confidence fields get retried
3. Cross-Validation Extraction - Multiple prompt styles find consensus
4. Validation Layer - Logical consistency checks before comparison
5. Iterative Improvement Loop - Refine until quality threshold met
6. Family Member Verification - Two-pass extraction for family data

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
from dataclasses import dataclass, field
from enum import Enum

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
from extraction_validator import ExtractionValidator, ValidationResult


class ExtractionStrategy(Enum):
    """Extraction prompt strategies for cross-validation."""
    STRUCTURED = 'structured'      # Direct JSON schema approach
    NARRATIVE = 'narrative'        # Describe then extract
    FIELD_BY_FIELD = 'field_by_field'  # Section-by-section


@dataclass
class ExtractionMetrics:
    """Tracks extraction quality metrics."""
    iterations: int = 0
    total_api_calls: int = 0
    strategies_used: List[str] = field(default_factory=list)
    validation_errors_initial: int = 0
    validation_errors_final: int = 0
    low_confidence_fields_initial: int = 0
    low_confidence_fields_final: int = 0
    family_members_verified: int = 0
    critique_corrections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'iterations': self.iterations,
            'total_api_calls': self.total_api_calls,
            'strategies_used': self.strategies_used,
            'validation_errors_initial': self.validation_errors_initial,
            'validation_errors_final': self.validation_errors_final,
            'low_confidence_fields_initial': self.low_confidence_fields_initial,
            'low_confidence_fields_final': self.low_confidence_fields_final,
            'family_members_verified': self.family_members_verified,
            'critique_corrections': self.critique_corrections,
        }


class EnhancedDocumentExtractor:
    """
    Multi-pass AI document extractor with self-improvement capabilities.
    
    Uses Ralph Brainstormer-inspired patterns:
    - Multiple extraction strategies (like multiple AI agents)
    - Self-critique phase (like boardroom critique)
    - Consensus finding (merge best results)
    - Iterative refinement (loop until quality)
    """
    
    # Quality thresholds
    CONFIDENCE_THRESHOLD = 0.7
    MIN_OVERALL_CONFIDENCE = 0.8
    MAX_ITERATIONS = 3
    MAX_RETRY_FIELDS = 5
    
    def __init__(self, verbose: bool = True, use_enhanced: bool = True):
        """
        Initialize enhanced extractor.
        
        Args:
            verbose: Print progress messages
            use_enhanced: Enable all enhanced features (set False for basic extraction)
        """
        self.verbose = verbose
        self.use_enhanced = use_enhanced
        self.client = None
        self.validator = ExtractionValidator(verbose=verbose)
        self.metrics = ExtractionMetrics()
        
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
    # MAIN EXTRACTION ENTRY POINTS
    # ========================================================================
    
    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main entry point - extract with all enhancements.
        
        If use_enhanced=False, falls back to basic single-pass extraction.
        """
        if self.use_enhanced:
            return self.extract_enhanced(file_path)
        else:
            return self.extract_basic(file_path)
    
    def extract_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic single-pass extraction (original behavior)."""
        self.log(f"\n{'='*60}")
        self.log(f"📊 BASIC EXTRACTION: {Path(file_path).name}")
        self.log(f"{'='*60}")
        
        images, media_type = self._load_document(file_path)
        doc_type, q_type = self._detect_document_type(images, media_type)
        
        result = self._extract_single_pass(images, media_type, doc_type)
        result['document_type'] = doc_type
        result['questionnaire_type'] = q_type
        result['extraction_mode'] = 'basic'
        
        return result
    
    def extract_enhanced(self, file_path: str) -> Dict[str, Any]:
        """
        Enhanced multi-pass extraction with all improvements.
        
        Pipeline:
        1. Initial extraction with multiple strategies
        2. Find consensus across strategies
        3. Self-critique pass
        4. Validation check
        5. Re-extract low-confidence fields
        6. Verify family members
        7. Final validation
        8. Iterate if needed
        """
        self.log(f"\n{'='*60}")
        self.log(f"🚀 ENHANCED EXTRACTION: {Path(file_path).name}")
        self.log(f"{'='*60}")
        
        self.metrics = ExtractionMetrics()
        
        # Load document
        images, media_type = self._load_document(file_path)
        doc_type, q_type = self._detect_document_type(images, media_type)
        
        all_types = get_all_document_types()
        config = all_types.get(doc_type, {})
        
        # ====================================================================
        # IMPROVEMENT 3: Cross-Validation Extraction
        # ====================================================================
        self.log(f"\n📋 Phase 1: Multi-Strategy Extraction")
        
        strategy_results = {}
        for strategy in [ExtractionStrategy.STRUCTURED, ExtractionStrategy.NARRATIVE]:
            self.log(f"   Running {strategy.value} strategy...")
            result = self._extract_with_strategy(images, media_type, config, strategy)
            strategy_results[strategy.value] = result
            self.metrics.strategies_used.append(strategy.value)
        
        # Find consensus
        consensus = self._find_consensus(strategy_results)
        self.log(f"   Consensus: {len(consensus.get('fields', {}))} fields")
        
        # ====================================================================
        # IMPROVEMENT 1: Self-Critique Pass
        # ====================================================================
        self.log(f"\n🔍 Phase 2: Self-Critique")
        
        critiqued = self._self_critique(images, media_type, consensus, config)
        self.log(f"   Corrections made: {self.metrics.critique_corrections}")
        
        # ====================================================================
        # IMPROVEMENT 4: Validation Layer
        # ====================================================================
        self.log(f"\n✓ Phase 3: Validation")
        
        validation = self.validator.validate(critiqued)
        self.metrics.validation_errors_initial = validation.error_count
        self.metrics.low_confidence_fields_initial = len([
            f for f in critiqued.get('fields', {}).values()
            if isinstance(f, dict) and f.get('confidence', 1) < self.CONFIDENCE_THRESHOLD
        ])
        
        if validation.error_count > 0:
            self.log(f"   ⚠ {validation.error_count} validation errors found")
        
        # ====================================================================
        # IMPROVEMENT 2: Confidence-Based Re-Extraction
        # ====================================================================
        low_conf_fields = self._get_low_confidence_fields(critiqued)
        
        if low_conf_fields:
            self.log(f"\n🔄 Phase 4: Re-Extract Low Confidence Fields")
            self.log(f"   Fields to retry: {[f['key'] for f in low_conf_fields[:self.MAX_RETRY_FIELDS]]}")
            
            critiqued = self._reextract_low_confidence(
                images, media_type, critiqued, low_conf_fields[:self.MAX_RETRY_FIELDS]
            )
        
        # ====================================================================
        # IMPROVEMENT 6: Family Member Verification
        # ====================================================================
        family_members = critiqued.get('family_members', [])
        
        if family_members:
            self.log(f"\n👨‍👩‍👧 Phase 5: Family Member Verification")
            self.log(f"   Verifying {len(family_members)} family members...")
            
            verified_family = self._verify_family_members(
                images, media_type, family_members, config
            )
            critiqued['family_members'] = verified_family
            self.metrics.family_members_verified = len(verified_family)
        
        # ====================================================================
        # IMPROVEMENT 5: Iterative Improvement Loop
        # ====================================================================
        self.metrics.iterations = 1
        
        # Check if we need more iterations
        validation = self.validator.validate(critiqued)
        overall_confidence = critiqued.get('confidence', 0)
        
        while (self.metrics.iterations < self.MAX_ITERATIONS and 
               (validation.error_count > 0 or overall_confidence < self.MIN_OVERALL_CONFIDENCE)):
            
            self.log(f"\n🔁 Iteration {self.metrics.iterations + 1}: Refinement Loop")
            
            # Feed errors back for refinement
            critiqued = self._refine_with_feedback(
                images, media_type, critiqued, validation, config
            )
            
            self.metrics.iterations += 1
            validation = self.validator.validate(critiqued)
            overall_confidence = critiqued.get('confidence', 0)
            
            self.log(f"   Errors remaining: {validation.error_count}")
            self.log(f"   Confidence: {overall_confidence:.0%}")
        
        # Final validation metrics
        self.metrics.validation_errors_final = validation.error_count
        self.metrics.low_confidence_fields_final = len(self._get_low_confidence_fields(critiqued))
        
        # Add metadata
        critiqued['document_type'] = doc_type
        critiqued['questionnaire_type'] = q_type
        critiqued['extraction_mode'] = 'enhanced'
        critiqued['extraction_metrics'] = self.metrics.to_dict()
        critiqued['validation_result'] = validation.to_dict()
        
        self._log_extraction_summary(critiqued)
        
        return critiqued
    
    # ========================================================================
    # DOCUMENT LOADING
    # ========================================================================
    
    def _load_document(self, file_path: str) -> Tuple[List[str], str]:
        """Load document and convert to base64 images."""
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
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
            b64 = base64.standard_b64encode(png_bytes).decode('utf-8')
            images.append(b64)
        
        doc.close()
        self.log(f"   Loaded {len(images)} pages")
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
    
    def _detect_document_type(self, images: List[str], media_type: str) -> Tuple[str, Optional[str]]:
        """Detect document type and questionnaire subtype."""
        self.log("🔍 Detecting document type...")
        
        all_types = get_all_document_types()
        type_list = [f"- {k}: {v['display_name']}" for k, v in all_types.items()]
        
        prompt = f"""Analyze this document and identify its type.

Known document types:
{chr(10).join(type_list)}

Respond in JSON: {{"document_type": "type_key", "questionnaire_name": "name if visible"}}
"""
        
        response = self._call_claude(images[:1], media_type, prompt, max_tokens=200)
        self.metrics.total_api_calls += 1
        
        try:
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                doc_type = result.get('document_type', 'unknown')
                q_name = result.get('questionnaire_name')
                q_type = detect_questionnaire_type(q_name) if q_name else None
                
                self.log(f"   Detected: {doc_type}" + (f" ({q_type})" if q_type else ""))
                return doc_type, q_type
        except:
            pass
        
        return 'unknown', None
    
    # ========================================================================
    # EXTRACTION STRATEGIES (Improvement 3)
    # ========================================================================
    
    def _extract_with_strategy(
        self, 
        images: List[str], 
        media_type: str, 
        config: Dict,
        strategy: ExtractionStrategy
    ) -> Dict[str, Any]:
        """Extract using a specific prompt strategy."""
        
        if strategy == ExtractionStrategy.STRUCTURED:
            prompt = self._build_structured_prompt(config)
        elif strategy == ExtractionStrategy.NARRATIVE:
            prompt = self._build_narrative_prompt(config)
        else:
            prompt = self._build_field_by_field_prompt(config)
        
        response = self._call_claude(images, media_type, prompt)
        self.metrics.total_api_calls += 1
        
        return self._parse_extraction_response(response)
    
    def _build_structured_prompt(self, config: Dict) -> str:
        """Direct JSON schema extraction prompt."""
        return self._build_base_extraction_prompt(config, """
Extract ALL information into this exact JSON structure.
Be precise - extract exactly what is written.""")
    
    def _build_narrative_prompt(self, config: Dict) -> str:
        """Narrative description then extraction prompt."""
        return f"""First, describe what you see in this document in 2-3 sentences.
Then, extract all information into JSON format.

{self._build_base_extraction_prompt(config, """
After describing the document, extract all fields.
Look carefully at each section before extracting.""")}
"""
    
    def _build_field_by_field_prompt(self, config: Dict) -> str:
        """Section-by-section extraction prompt."""
        return self._build_base_extraction_prompt(config, """
Go through the document section by section:
1. First, find the personal information section
2. Then, find any family member information
3. Then, find any address/employment/education history
4. Finally, note any other important information

Extract each section carefully before moving to the next.""")
    
    def _build_base_extraction_prompt(self, config: Dict, instructions: str) -> str:
        """Build base extraction prompt with field definitions."""
        display_name = config.get('display_name', 'Document')
        
        # Get field definitions
        field_defs = config.get('fields', {})
        if isinstance(field_defs, dict):
            primary_fields = field_defs.get('primary', [])
        else:
            primary_fields = field_defs
        
        primary_list = [f"- {f['key']}: {f['label']}" for f in primary_fields] if primary_fields else []
        
        return f"""Extract all information from this {display_name}.
{instructions}

PRIMARY FIELDS TO EXTRACT:
{chr(10).join(primary_list) if primary_list else '- Extract all visible personal information'}

IMPORTANT RULES:
- Extract exactly what is written, do not infer
- For handwritten text, indicate confidence (0.0-1.0)
- Dates: use YYYY-MM-DD format
- A-Numbers: include all 9 digits
- If a field is empty/not visible, omit it

Respond in JSON:
{{
    "confidence": 0.0-1.0,
    "fields": {{
        "field_key": {{"value": "...", "confidence": 0.0-1.0}},
        ...
    }},
    "family_members": [
        {{"relationship": "spouse|child|parent", "data": {{...}}, "confidence": 0.9}},
        ...
    ],
    "history": {{
        "address": [{{"data": {{...}}, "is_current": true, "confidence": 0.9}}],
        "employment": [...],
        "education": [...]
    }},
    "other": {{}}
}}
"""
    
    def _find_consensus(self, strategy_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Find consensus across multiple extraction strategies."""
        
        if len(strategy_results) == 1:
            return list(strategy_results.values())[0]
        
        # Start with first result as base
        results_list = list(strategy_results.values())
        consensus = {
            'confidence': 0,
            'fields': {},
            'family_members': [],
            'history': {},
            'other': {}
        }
        
        # Merge fields - prefer higher confidence
        all_field_keys = set()
        for result in results_list:
            all_field_keys.update(result.get('fields', {}).keys())
        
        for key in all_field_keys:
            best_value = None
            best_confidence = 0
            
            for result in results_list:
                field_data = result.get('fields', {}).get(key)
                if field_data:
                    conf = field_data.get('confidence', 0.5) if isinstance(field_data, dict) else 0.5
                    if conf > best_confidence:
                        best_confidence = conf
                        best_value = field_data
            
            if best_value:
                consensus['fields'][key] = best_value
        
        # Merge family members - combine unique ones
        seen_family = set()
        for result in results_list:
            for fm in result.get('family_members', []):
                key = (
                    fm.get('relationship', ''),
                    fm.get('data', {}).get('first_name', ''),
                    fm.get('data', {}).get('last_name', '')
                )
                if key not in seen_family:
                    consensus['family_members'].append(fm)
                    seen_family.add(key)
        
        # Merge history - combine all
        for result in results_list:
            for history_type, records in result.get('history', {}).items():
                if history_type not in consensus['history']:
                    consensus['history'][history_type] = []
                consensus['history'][history_type].extend(records)
        
        # Average confidence
        confidences = [r.get('confidence', 0.5) for r in results_list]
        consensus['confidence'] = sum(confidences) / len(confidences)
        
        return consensus

    
    # ========================================================================
    # SELF-CRITIQUE (Improvement 1)
    # ========================================================================
    
    def _self_critique(
        self, 
        images: List[str], 
        media_type: str, 
        extraction: Dict[str, Any],
        config: Dict
    ) -> Dict[str, Any]:
        """
        Have AI critique its own extraction and fix errors.
        
        This is like the "Boardroom Critique" phase in Ralph Brainstormer.
        """
        
        # Build critique prompt
        fields_json = json.dumps(extraction.get('fields', {}), indent=2, default=str)
        family_json = json.dumps(extraction.get('family_members', []), indent=2, default=str)
        
        critique_prompt = f"""I extracted this data from the document. Please review it for errors.

EXTRACTED FIELDS:
{fields_json}

EXTRACTED FAMILY MEMBERS:
{family_json}

CHECK FOR THESE COMMON ERRORS:
1. SWAPPED VALUES: First/last name swapped, dates in wrong fields
2. FORMAT ERRORS: Dates not in YYYY-MM-DD, A-numbers missing digits
3. OCR ERRORS: Numbers misread (0 vs O, 1 vs I, 8 vs B)
4. MISSING DATA: Fields visible in document but not extracted
5. CONFIDENCE TOO HIGH: Handwritten/unclear text marked as high confidence
6. LOGICAL ERRORS: DOB after entry date, impossible dates

Look at the ORIGINAL DOCUMENT again and compare with my extraction.

Respond with CORRECTED JSON (same format). Include a "corrections" array listing what you fixed:
{{
    "confidence": 0.0-1.0,
    "fields": {{...}},
    "family_members": [...],
    "history": {{...}},
    "corrections": [
        {{"field": "field_name", "old": "old_value", "new": "new_value", "reason": "why"}}
    ]
}}

If no corrections needed, return the same data with empty corrections array.
"""
        
        response = self._call_claude(images, media_type, critique_prompt)
        self.metrics.total_api_calls += 1
        
        critiqued = self._parse_extraction_response(response)
        
        # Count corrections
        corrections = critiqued.get('corrections', [])
        self.metrics.critique_corrections = len(corrections)
        
        if corrections:
            self.log(f"   Corrections found:")
            for c in corrections[:5]:  # Show first 5
                self.log(f"      - {c.get('field', '?')}: {c.get('reason', 'fixed')}")
        
        # Merge critiqued data back
        if critiqued.get('fields'):
            extraction['fields'] = critiqued['fields']
        if critiqued.get('family_members'):
            extraction['family_members'] = critiqued['family_members']
        if critiqued.get('history'):
            extraction['history'] = critiqued['history']
        if critiqued.get('confidence'):
            extraction['confidence'] = critiqued['confidence']
        
        return extraction
    
    # ========================================================================
    # CONFIDENCE-BASED RE-EXTRACTION (Improvement 2)
    # ========================================================================
    
    def _get_low_confidence_fields(self, extraction: Dict[str, Any]) -> List[Dict]:
        """Get list of fields with confidence below threshold."""
        low_conf = []
        
        for key, field_data in extraction.get('fields', {}).items():
            if isinstance(field_data, dict):
                confidence = field_data.get('confidence', 1.0)
                if confidence < self.CONFIDENCE_THRESHOLD:
                    low_conf.append({
                        'key': key,
                        'value': field_data.get('value'),
                        'confidence': confidence
                    })
        
        # Sort by confidence (lowest first)
        low_conf.sort(key=lambda x: x['confidence'])
        return low_conf
    
    def _reextract_low_confidence(
        self,
        images: List[str],
        media_type: str,
        extraction: Dict[str, Any],
        low_conf_fields: List[Dict]
    ) -> Dict[str, Any]:
        """Re-extract specific low-confidence fields with focused prompt."""
        
        field_list = [f['key'] for f in low_conf_fields]
        
        retry_prompt = f"""I need you to look MORE CAREFULLY at these specific fields that were unclear:

FIELDS TO RE-EXAMINE:
{chr(10).join(f'- {f["key"]}: currently "{f.get("value", "unknown")}" (confidence: {f.get("confidence", 0):.0%})' for f in low_conf_fields)}

Look at the document again. These fields exist but were hard to read.
Try different interpretations. Consider:
- Could characters be misread? (0/O, 1/I, 8/B, 5/S)
- Is there faded or handwritten text?
- Could the value be in a different location?

Return ONLY the re-examined fields in JSON:
{{
    "fields": {{
        "field_key": {{"value": "corrected_value", "confidence": 0.0-1.0}},
        ...
    }}
}}
"""
        
        response = self._call_claude(images, media_type, retry_prompt)
        self.metrics.total_api_calls += 1
        
        retried = self._parse_extraction_response(response)
        
        # Merge improved fields back
        improved_count = 0
        for key, new_data in retried.get('fields', {}).items():
            if isinstance(new_data, dict):
                new_conf = new_data.get('confidence', 0)
                old_data = extraction['fields'].get(key, {})
                old_conf = old_data.get('confidence', 0) if isinstance(old_data, dict) else 0
                
                # Only update if confidence improved
                if new_conf > old_conf:
                    extraction['fields'][key] = new_data
                    improved_count += 1
        
        self.log(f"   Improved {improved_count}/{len(low_conf_fields)} fields")
        
        return extraction
    
    # ========================================================================
    # FAMILY MEMBER VERIFICATION (Improvement 6)
    # ========================================================================
    
    def _verify_family_members(
        self,
        images: List[str],
        media_type: str,
        family_members: List[Dict],
        config: Dict
    ) -> List[Dict]:
        """
        Two-pass verification for family members.
        
        Pass 1: Already done (initial extraction)
        Pass 2: Verify each family member exists and has required fields
        """
        
        if not family_members:
            return []
        
        # Build verification prompt
        fm_summary = []
        for i, fm in enumerate(family_members):
            rel = fm.get('relationship', 'unknown')
            data = fm.get('data', {})
            name = f"{data.get('first_name', '?')} {data.get('last_name', '?')}"
            fm_summary.append(f"{i+1}. {rel}: {name}")
        
        verify_prompt = f"""I found these family members in the document:

{chr(10).join(fm_summary)}

Please VERIFY each one by re-reading the family member sections.

For each family member:
1. Confirm they actually exist in the document (not a misread)
2. Extract any MISSING fields: date_of_birth, country_of_birth, a_number, citizenship
3. If a person doesn't actually exist, mark them as "NOT_FOUND"

Return verified family members in JSON:
{{
    "family_members": [
        {{
            "relationship": "spouse|child|parent",
            "verified": true,
            "data": {{
                "first_name": "...",
                "last_name": "...",
                "date_of_birth": "YYYY-MM-DD",
                "country_of_birth": "...",
                "citizenship": "...",
                "a_number": "...",
                ...
            }},
            "confidence": 0.0-1.0
        }},
        ...
    ]
}}

Mark "verified": false and include reason if person NOT_FOUND.
"""
        
        response = self._call_claude(images, media_type, verify_prompt)
        self.metrics.total_api_calls += 1
        
        verified = self._parse_extraction_response(response)
        verified_members = verified.get('family_members', [])
        
        # Filter out not found
        final_members = []
        for fm in verified_members:
            if fm.get('verified', True) and fm.get('data'):
                final_members.append(fm)
            else:
                reason = fm.get('reason', 'not verified')
                self.log(f"   ⚠ Removed: {fm.get('relationship', '?')} - {reason}")
        
        return final_members
    
    # ========================================================================
    # ITERATIVE REFINEMENT (Improvement 5)
    # ========================================================================
    
    def _refine_with_feedback(
        self,
        images: List[str],
        media_type: str,
        extraction: Dict[str, Any],
        validation: ValidationResult,
        config: Dict
    ) -> Dict[str, Any]:
        """
        Refine extraction based on validation errors.
        
        This is the "Final Polish" phase - address specific critiques.
        """
        
        # Build error summary
        error_msgs = []
        for e in validation.errors[:5]:
            error_msgs.append(f"- {e.field_key}: {e.message}")
        for w in validation.warnings[:5]:
            error_msgs.append(f"- {w.field_key}: {w.message}")
        
        if not error_msgs:
            return extraction
        
        refine_prompt = f"""My extraction has these validation errors:

{chr(10).join(error_msgs)}

Look at the document again and fix these specific issues.
Return the CORRECTED data in the same JSON format.

Only return the fields that need correction:
{{
    "fields": {{
        "field_key": {{"value": "corrected", "confidence": 0.0-1.0}},
        ...
    }}
}}
"""
        
        response = self._call_claude(images, media_type, refine_prompt)
        self.metrics.total_api_calls += 1
        
        refined = self._parse_extraction_response(response)
        
        # Merge corrections
        for key, new_data in refined.get('fields', {}).items():
            if new_data:
                extraction['fields'][key] = new_data
        
        # Recalculate overall confidence
        confidences = []
        for field_data in extraction.get('fields', {}).values():
            if isinstance(field_data, dict):
                confidences.append(field_data.get('confidence', 0.5))
        
        if confidences:
            extraction['confidence'] = sum(confidences) / len(confidences)
        
        return extraction
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _call_claude(
        self,
        images: List[str],
        media_type: str,
        prompt: str,
        max_tokens: int = None
    ) -> str:
        """Make API call to Claude with images."""
        
        content = []
        for img in images:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": img}
            })
        content.append({"type": "text", "text": prompt})
        
        response = self.client.messages.create(
            model=AI_CONFIG['model'],
            max_tokens=max_tokens or AI_CONFIG['max_tokens'],
            temperature=AI_CONFIG['temperature'],
            messages=[{"role": "user", "content": content}]
        )
        
        return response.content[0].text.strip()
    
    def _extract_single_pass(
        self,
        images: List[str],
        media_type: str,
        doc_type: str
    ) -> Dict[str, Any]:
        """Basic single-pass extraction."""
        
        all_types = get_all_document_types()
        config = all_types.get(doc_type, {})
        
        prompt = self._build_structured_prompt(config)
        response = self._call_claude(images, media_type, prompt)
        self.metrics.total_api_calls += 1
        
        return self._parse_extraction_response(response)
    
    def _parse_extraction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        
        result = {
            'confidence': 0.0,
            'fields': {},
            'family_members': [],
            'history': {},
            'other': {}
        }
        
        try:
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
                result['corrections'] = parsed.get('corrections', [])
        
        except json.JSONDecodeError as e:
            self.log(f"   ⚠ JSON parse error: {e}")
            result['other']['raw_response'] = response_text
        
        return result
    
    def _log_extraction_summary(self, extracted: Dict):
        """Log summary of extraction."""
        self.log(f"\n{'='*60}")
        self.log(f"📋 EXTRACTION SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"   Mode: {extracted.get('extraction_mode', 'unknown')}")
        self.log(f"   Confidence: {extracted.get('confidence', 0):.0%}")
        self.log(f"   Fields: {len(extracted.get('fields', {}))}")
        self.log(f"   Family members: {len(extracted.get('family_members', []))}")
        
        history = extracted.get('history', {})
        for h_type, records in history.items():
            if records:
                self.log(f"   {h_type}: {len(records)} records")
        
        metrics = extracted.get('extraction_metrics', {})
        if metrics:
            self.log(f"\n   📊 Metrics:")
            self.log(f"      Iterations: {metrics.get('iterations', 1)}")
            self.log(f"      API calls: {metrics.get('total_api_calls', 1)}")
            self.log(f"      Strategies: {', '.join(metrics.get('strategies_used', []))}")
            self.log(f"      Critique corrections: {metrics.get('critique_corrections', 0)}")
            self.log(f"      Validation errors: {metrics.get('validation_errors_initial', 0)} → {metrics.get('validation_errors_final', 0)}")


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ENHANCED DOCUMENT EXTRACTOR - TEST MODE")
    print("="*60)
    
    import sys
    
    try:
        extractor = EnhancedDocumentExtractor(verbose=True, use_enhanced=True)
        
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            
            # Test basic mode
            print("\n--- BASIC MODE ---")
            extractor.use_enhanced = False
            basic_result = extractor.extract_from_file(file_path)
            
            # Test enhanced mode
            print("\n--- ENHANCED MODE ---")
            extractor.use_enhanced = True
            enhanced_result = extractor.extract_from_file(file_path)
            
            # Compare
            print("\n" + "="*60)
            print("COMPARISON:")
            print("="*60)
            print(f"Basic confidence: {basic_result.get('confidence', 0):.0%}")
            print(f"Enhanced confidence: {enhanced_result.get('confidence', 0):.0%}")
            print(f"Basic fields: {len(basic_result.get('fields', {}))}")
            print(f"Enhanced fields: {len(enhanced_result.get('fields', {}))}")
            
        else:
            print("\nUsage: python enhanced_extractor.py <file_path>")
            print("\nSupported formats: PDF, PNG, JPG, JPEG, GIF, WEBP")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
