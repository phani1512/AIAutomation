"""
Intelligent Prompt Matcher - Multi-Strategy Matching System

Cascading matching strategies for test builder prompts:
1. EXACT MATCH - Direct dataset lookup (fastest, most accurate)
2. TEMPLATE MATCH - Parameter extraction from templates (e.g., "click {text} button")
3. FUZZY MATCH - Similarity scoring against dataset entries
4. ML INFERENCE - NLP-based inference (fallback for novel prompts)

Each strategy returns a confidence score, and the best match is used.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from pathlib import Path

logger = logging.getLogger(__name__)


class IntelligentPromptMatcher:
    """
    Multi-strategy prompt matching engine that cascades through different
    matching techniques to find the best code generation approach.
    """
    
    def __init__(self, dataset_path: str = None):
        """Initialize matcher with dataset."""
        if dataset_path is None:
            # Default to combined dataset - go up 5 levels from semantic_analysis/ to project root
            base_dir = Path(__file__).parent.parent.parent.parent.parent
            dataset_path = base_dir / "resources" / "ml_data" / "datasets" / "combined-training-dataset-final.json"
        
        self.dataset_path = dataset_path
        self.dataset = []
        self.templates = []
        self.exact_lookup = {}
        
        self._load_dataset()
        # Logging is done in _load_dataset()
    
    def _load_dataset(self):
        """Load and index dataset for fast lookups."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.dataset = json.load(f)
            
            # Build indexes for fast lookup
            variations_loaded = 0  # Initialize counter
            for entry in self.dataset:
                prompt = entry.get('prompt', '').strip().lower()
                
                # Index exact matches
                if prompt and '{' not in prompt:  # Not a template
                    self.exact_lookup[prompt] = entry
                    
                    # **FIX: Also index all prompt variations!**
                    variations = entry.get('metadata', {}).get('prompt_variations', [])
                    for variation in variations:
                        variation_clean = variation.strip().lower()
                        if variation_clean and variation_clean != prompt:  # Avoid duplicates
                            self.exact_lookup[variation_clean] = entry
                            variations_loaded += 1
                
                # Index templates
                if '{' in prompt and entry.get('metadata', {}).get('entry_type') == 'template':
                    self.templates.append(entry)
            
            logger.info(f"[MATCHER] Indexed {len(self.exact_lookup)} exact entries ({variations_loaded} variations), {len(self.templates)} templates")
        
        except Exception as e:
            logger.error(f"[MATCHER] Error loading dataset: {e}")
            self.dataset = []
    
    def match(self, user_prompt: str) -> Dict:
        """
        Match user prompt using cascading strategies.
        
        Returns:
            {
                'strategy': 'exact|template|fuzzy|ml',
                'confidence': 0.0-1.0,
                'matched_entry': {...},
                'parameters': {...},  # For template matches
                'code': 'generated code',
                'xpath': 'locator',
                'explanation': 'why this match was chosen'
            }
        """
        user_prompt_clean = user_prompt.strip().lower()
        
        # Strategy 1: EXACT MATCH
        exact_result = self._exact_match(user_prompt_clean)
        if exact_result:
            logger.info(f"[MATCHER] ✓ EXACT MATCH: {user_prompt}")
            return exact_result
        
        # Strategy 2: TEMPLATE MATCH
        template_result = self._template_match(user_prompt_clean)
        if template_result and template_result['confidence'] >= 0.85:
            logger.info(f"[MATCHER] ✓ TEMPLATE MATCH: {user_prompt} → {template_result['matched_template']}")
            return template_result
        
        # Strategy 3: FUZZY MATCH
        fuzzy_result = self._fuzzy_match(user_prompt_clean)
        if fuzzy_result and fuzzy_result['confidence'] >= 0.80:
            logger.info(f"[MATCHER] ✓ FUZZY MATCH: {user_prompt} → {fuzzy_result['matched_prompt']}")
            return fuzzy_result
        
        # Strategy 4: ML FALLBACK
        logger.info(f"[MATCHER] → ML INFERENCE (no high-confidence match): {user_prompt}")
        return {
            'strategy': 'ml',
            'confidence': 0.5,  # Unknown confidence for ML
            'matched_entry': None,
            'parameters': {},
            'code': None,  # ML inference will generate
            'xpath': None,
            'explanation': 'No exact/template/fuzzy match found, using ML inference'
        }
    
    def _exact_match(self, prompt: str) -> Optional[Dict]:
        """Strategy 1: Direct dataset lookup."""
        entry = self.exact_lookup.get(prompt)
        if entry:
            return {
                'strategy': 'exact',
                'confidence': 1.0,
                'matched_entry': entry,
                'matched_prompt': entry['prompt'],
                'parameters': {},
                'code': entry.get('code', ''),
                'xpath': entry.get('xpath', ''),
                'explanation': f'Exact match for "{entry["prompt"]}"'
            }
        return None
    
    def _template_match(self, prompt: str) -> Optional[Dict]:
        """Strategy 2: Template pattern matching with parameter extraction."""
        best_match = None
        best_score = 0.0
        
        for template_entry in self.templates:
            template = template_entry['prompt'].lower()
            
            # Convert template to regex pattern
            # e.g., "click {text} button" → "click (.+?) button"
            pattern = re.escape(template)
            pattern = pattern.replace(r'\{text\}', r'(?P<text>.+?)')
            pattern = pattern.replace(r'\{field_name\}', r'(?P<field_name>.+?)')
            pattern = pattern.replace(r'\{element\}', r'(?P<element>.+?)')
            pattern = pattern.replace(r'\{value\}', r'(?P<value>.+?)')
            pattern = pattern.replace(r'\{menu_text\}', r'(?P<menu_text>.+?)')
            pattern = pattern.replace(r'\{tab_name\}', r'(?P<tab_name>.+?)')
            pattern = f'^{pattern}$'
            
            try:
                match = re.match(pattern, prompt, re.IGNORECASE)
                if match:
                    # Extract parameters
                    params = match.groupdict()
                    
                    # Calculate confidence based on template specificity
                    # More specific templates (more static text) = higher confidence
                    static_chars = len(template) - sum(len(p) for p in re.findall(r'\{[^}]+\}', template))
                    total_chars = len(template)
                    specificity = static_chars / total_chars if total_chars > 0 else 0
                    confidence = 0.85 + (specificity * 0.14)  # Range: 0.85-0.99
                    
                    if confidence > best_score:
                        best_score = confidence
                        best_match = {
                            'strategy': 'template',
                            'confidence': confidence,
                            'matched_entry': template_entry,
                            'matched_template': template_entry['prompt'],
                            'parameters': params,
                            'code': self._substitute_parameters(template_entry.get('code', ''), params),
                            'xpath': self._substitute_parameters(template_entry.get('xpath', ''), params),
                            'explanation': f'Matched template "{template_entry["prompt"]}" with parameters: {params}'
                        }
            except Exception as e:
                logger.debug(f"[MATCHER] Template regex error: {e}")
                continue
        
        return best_match
    
    def _fuzzy_match(self, prompt: str) -> Optional[Dict]:
        """Strategy 3: Fuzzy matching with similarity scoring."""
        best_match = None
        best_score = 0.0
        
        # Try fuzzy matching against all non-template entries
        for entry_prompt, entry in self.exact_lookup.items():
            similarity = SequenceMatcher(None, prompt, entry_prompt).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = {
                    'strategy': 'fuzzy',
                    'confidence': similarity,
                    'matched_entry': entry,
                    'matched_prompt': entry['prompt'],
                    'parameters': {},
                    'code': entry.get('code', ''),
                    'xpath': entry.get('xpath', ''),
                    'explanation': f'Fuzzy match ({similarity:.2%} similar) to "{entry["prompt"]}"'
                }
        
        # Also check prompt variations
        for entry in self.dataset:
            variations = entry.get('metadata', {}).get('prompt_variations', [])
            for variation in variations:
                variation_clean = variation.lower().strip()
                similarity = SequenceMatcher(None, prompt, variation_clean).ratio()
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = {
                        'strategy': 'fuzzy',
                        'confidence': similarity,
                        'matched_entry': entry,
                        'matched_prompt': variation,
                        'parameters': {},
                        'code': entry.get('code', ''),
                        'xpath': entry.get('xpath', ''),
                        'explanation': f'Fuzzy match ({similarity:.2%} similar) to variation "{variation}"'
                    }
        
        return best_match if best_score >= 0.70 else None
    
    def _substitute_parameters(self, text: str, params: Dict) -> str:
        """Replace template placeholders with actual parameter values."""
        if not text or not params:
            return text
        
        result = text
        for key, value in params.items():
            # Handle different placeholder formats
            placeholders = [
                f'{{{key}}}',                    # {text}
                f'{{{key.upper()}}}',            # {TEXT}
                f'{{" + {key.upper()} + "}}',    # Java string concat
            ]
            
            for placeholder in placeholders:
                result = result.replace(placeholder, value)
        
        return result
    
    def get_match_suggestions(self, user_prompt: str, limit: int = 5) -> List[Dict]:
        """
        Get multiple match suggestions for user to choose from.
        Useful for showing "Did you mean?" options.
        """
        suggestions = []
        prompt_clean = user_prompt.strip().lower()
        
        # Get exact match
        exact = self._exact_match(prompt_clean)
        if exact:
            suggestions.append(exact)
        
        # Get template matches
        template = self._template_match(prompt_clean)
        if template:
            suggestions.append(template)
        
        # Get top fuzzy matches
        fuzzy_matches = []
        for entry_prompt, entry in self.exact_lookup.items():
            similarity = SequenceMatcher(None, prompt_clean, entry_prompt).ratio()
            if similarity >= 0.60:
                fuzzy_matches.append((similarity, entry))
        
        fuzzy_matches.sort(key=lambda x: x[0], reverse=True)
        for similarity, entry in fuzzy_matches[:limit - len(suggestions)]:
            suggestions.append({
                'strategy': 'fuzzy',
                'confidence': similarity,
                'matched_entry': entry,
                'matched_prompt': entry['prompt'],
                'parameters': {},
                'code': entry.get('code', ''),
                'xpath': entry.get('xpath', ''),
                'explanation': f'Similar ({similarity:.2%}) to "{entry["prompt"]}"'
            })
        
        return suggestions[:limit]
    
    def explain_match(self, match_result: Dict) -> str:
        """Generate human-readable explanation of the match."""
        strategy = match_result['strategy']
        confidence = match_result['confidence']
        
        if strategy == 'exact':
            return f"✓ Exact match found in dataset (100% confidence)"
        elif strategy == 'template':
            params = match_result.get('parameters', {})
            param_str = ', '.join(f"{k}='{v}'" for k, v in params.items())
            return f"✓ Template match: {match_result['matched_template']} ({param_str}) - {confidence:.1%} confidence"
        elif strategy == 'fuzzy':
            return f"≈ Similar to: {match_result['matched_prompt']} - {confidence:.1%} confidence"
        elif strategy == 'ml':
            return f"→ Using ML inference (no dataset match found)"
        else:
            return f"? Unknown strategy: {strategy}"
    
    def match_with_fallbacks(self, user_prompt: str, max_fallbacks: int = 3) -> Dict:
        """
        Match user prompt and return primary match + fallback alternatives.
        
        This enables self-healing tests that try alternative locators if the
        primary one fails during execution.
        
        Args:
            user_prompt: User's test instruction
            max_fallbacks: Maximum number of fallback alternatives to return
            
        Returns:
            {
                'primary': {...},  # Best match (same as match() return value)
                'fallbacks': [     # List of alternative matches
                    {...},
                    {...}
                ],
                'has_fallbacks': bool  # True if fallbacks are available
            }
        """
        user_prompt_clean = user_prompt.strip().lower()
        
        # Get primary match using existing match() method
        primary = self.match(user_prompt)
        
        # Collect fallback alternatives
        fallbacks = []
        seen_xpaths = {primary.get('xpath', '')}
        
        # Strategy 1: Get other exact matches (different code/xpath for same intent)
        for entry_prompt, entry in self.exact_lookup.items():
            if len(fallbacks) >= max_fallbacks:
                break
            
            xpath = entry.get('xpath', '')
            if xpath and xpath not in seen_xpaths:
                # Check if it's semantically similar to user prompt
                similarity = SequenceMatcher(None, user_prompt_clean, entry_prompt).ratio()
                if similarity >= 0.70:
                    fallbacks.append({
                        'strategy': 'exact_alternative',
                        'confidence': similarity,
                        'matched_entry': entry,
                        'matched_prompt': entry['prompt'],
                        'code': entry.get('code', ''),
                        'xpath': xpath,
                        'explanation': f'Alternative approach: "{entry["prompt"]}"'
                    })
                    seen_xpaths.add(xpath)
        
        # Strategy 2: Get fuzzy matches with different locators
        fuzzy_candidates = []
        for entry_prompt, entry in self.exact_lookup.items():
            if entry.get('xpath', '') not in seen_xpaths:
                similarity = SequenceMatcher(None, user_prompt_clean, entry_prompt).ratio()
                if 0.60 <= similarity < 0.70:  # Lower threshold for fallbacks
                    fuzzy_candidates.append((similarity, entry))
        
        fuzzy_candidates.sort(key=lambda x: x[0], reverse=True)
        for similarity, entry in fuzzy_candidates[:max_fallbacks - len(fallbacks)]:
            xpath = entry.get('xpath', '')
            if xpath:
                fallbacks.append({
                    'strategy': 'fuzzy_fallback',
                    'confidence': similarity,
                    'matched_entry': entry,
                    'matched_prompt': entry['prompt'],
                    'code': entry.get('code', ''),
                    'xpath': xpath,
                    'explanation': f'Fallback option ({similarity:.1%} similar): "{entry["prompt"]}"'
                })
                seen_xpaths.add(xpath)
        
        return {
            'primary': primary,
            'fallbacks': fallbacks,
            'has_fallbacks': len(fallbacks) > 0
        }


# Singleton instance
_matcher_instance = None

def get_matcher() -> IntelligentPromptMatcher:
    """Get or create singleton matcher instance."""
    global _matcher_instance
    if _matcher_instance is None:
        _matcher_instance = IntelligentPromptMatcher()
    return _matcher_instance
