"""
Improved inference with better output formatting and cleaning.
VERSION: 3.0.0 - LOCAL AI ENGINE - True AI Understanding
"""

import pickle
import tiktoken
import re
import json
import os
from ml_training.train_simple import NGramLanguageModel
from .action_suggestion_engine import ActionSuggestionEngine
from generators.comprehensive_code_generator import ComprehensiveCodeGenerator
from nlp.template_engine import TemplateEngine
from nlp.template_parameter_extractor import TemplateParameterExtractor
from difflib import SequenceMatcher
from typing import List, Dict, Optional

# Refactored modules
from .fallback_strategy import FallbackStrategyGenerator
from .locator_utils import LocatorUtils
from nlp.language_converter import LanguageConverter
from .universal_patterns import UniversalPatternHandler
from .dataset_matcher import DatasetMatcher

# NEW: Local AI Engine for intelligent prompt understanding
from .local_ai_engine import LocalAIEngine

class ImprovedSeleniumGenerator:
    """Enhanced Selenium code generator with better output quality."""
    
    # Action verb synonyms for improved matching
    ACTION_SYNONYMS = {
        'click': ['click', 'press', 'tap', 'select', 'choose', 'hit'],
        'enter': ['enter', 'type', 'input', 'fill', 'write'],
        'open': ['open', 'activate', 'show', 'display'],
        'get': ['get', 'read', 'fetch', 'retrieve', 'extract'],
        'verify': ['verify', 'check', 'validate', 'confirm', 'assert'],
    }
    
    def __init__(self, model_path: str = 'resources/ml_data/models/selenium_ngram_model.pkl', silent: bool = False, enable_local_ai: bool = True):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.version = "3.0.0-LOCAL-AI"
        self.enable_local_ai = enable_local_ai
        
        # Build synonym mapping for quick lookup
        self.synonym_map = {}
        for canonical, synonyms in self.ACTION_SYNONYMS.items():
            for synonym in synonyms:
                self.synonym_map[synonym] = canonical
        
        if not silent:
            print(f"[INFERENCE] Version {self.version} - LOCAL AI ENGINE")
            if enable_local_ai:
                print(f"[INFERENCE] ✓ Local AI Intelligence ENABLED")
            else:
                print(f"[INFERENCE] ⚠ Using legacy rule-based matching")
            print(f"Loading model from {model_path}...")
        
        # Initialize Local AI Engine (NEW)
        if enable_local_ai:
            self.local_ai = LocalAIEngine()
            if not silent:
                print(f"[INFERENCE] ✓ Local AI Engine initialized")
        
        # Initialize N-Gram model (optional - for action name suggestions)
        self.model = NGramLanguageModel(n=4)
        try:
            self.model.load(model_path)
            if not silent:
                print(f"[INFERENCE] ✓ N-Gram model loaded successfully")
        except FileNotFoundError:
            if not silent:
                print(f"[INFERENCE] ⚠ N-Gram model not found at {model_path}")
                print(f"[INFERENCE] ⚠ Continuing without N-Gram model (core features still work)")
            self.model = None
        except Exception as e:
            if not silent:
                print(f"[INFERENCE] ⚠ Error loading N-Gram model: {e}")
                print(f"[INFERENCE] ⚠ Continuing without N-Gram model")
            self.model = None
        
        # Initialize enhanced action suggestion engine
        self.action_engine = ActionSuggestionEngine()
        
        # Initialize comprehensive code generator (dataset-driven)
        self.comprehensive_generator = ComprehensiveCodeGenerator()
        
        # Initialize template engine for code generation
        self.template_engine = TemplateEngine()
        
        # Initialize template parameter extractor for dynamic placeholder substitution
        self.param_extractor = TemplateParameterExtractor()
        
        # Store last found alternatives (for HYBRID mode)
        self._last_alternatives = []
        
        # Initialize refactored modules
        self.fallback_generator = FallbackStrategyGenerator()
        self.locator_utils = LocatorUtils()
        self.universal_handler = UniversalPatternHandler(self.locator_utils)
        self.language_converter = None  # Lazy initialization (needs method_mappings)
        
        # Load datasets for element extraction
        self._load_datasets()
        
        # Phase 5: Load PageHelper patterns dataset (63 methods)
        self.pagehelper_cache = {}
        self._load_pagehelper_patterns()
        
        # Load method name mappings from dataset
        self._load_method_mappings()
        
        # PHASE 3: Initialize unified parameter extractor (needs dataset_cache loaded first)
        self.param_extractor_unified = self.ParameterExtractor(
            dataset_cache=self.dataset_cache,
            find_dataset_match_func=self._find_dataset_match
        )
        
        # Initialize dataset matcher (needs datasets and caches loaded first)
        self.dataset_matcher = DatasetMatcher(
            synonym_map=self.synonym_map,
            dataset_cache=self.dataset_cache,
            pagehelper_cache=self.pagehelper_cache,
            param_extractor=self.param_extractor,
            language_converter=self.language_converter  # Will be initialized lazily
        )
        
        if not silent:
            print(f"[OK] Model loaded successfully!")
            if self.model:
                print(f"  Vocabulary size: {len(self.model.vocab)}")
                print(f"  Unique contexts: {len(self.model.ngrams)}")
            print(f"  Dataset entries: {len(self.dataset_cache)}")
            print(f"  Method mappings: {sum(len(v.get('method_mappings', [])) for v in self.method_mappings.values())} mappings loaded")
            print(f"  Action engine: {len(self.action_engine.action_catalog)} element types\n")
            print()
    
    def _load_datasets(self):
        """Load training dataset (prompt variations grouped by code).
        
        Uses: combined-training-dataset-final.json
        - 938 unique code patterns (expanded with advanced examples)
        - Each entry has multiple prompt variations (7+ avg variations per entry)
        - 5,826+ total prompts with variations
        - 100% pure Selenium WebDriver code
        - Covers: clicks, inputs, alerts, frames, JavaScript, mouse actions, keyboard, waits, etc.
        
        Format: JSON array with metadata.prompt_variations containing all alternative prompts
        """
        self.dataset_cache = {}
        
        # Determine the project root (go up 4 levels from core/inference_improved.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))  # core/
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))  # -> AIAutomation/
        dataset_dir = os.path.join(project_root, 'resources', 'ml_data', 'datasets')
        
        # Load the consolidated dataset (prompt variations grouped by code pattern)
        unified_dataset_path = os.path.join(dataset_dir, 'combined-training-dataset-final.json')
        
        try:
            with open(unified_dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # New format: direct array of entries (not wrapped in "prompts" key)
                prompts = data if isinstance(data, list) else data.get('prompts', [])
                
                # Build cache from prompts
                for item in prompts:
                    prompt = item.get('prompt', '').strip().lower()
                    if prompt:
                        cache_entry = {
                            'locator': item.get('xpath', ''),  # New format uses 'xpath' field
                            'code': item.get('code', ''),
                            'element_type': item.get('category', ''),  # category as element type
                            'action': item.get('category', ''),
                            'template_category': item.get('category', ''),
                            'category': item.get('category', ''),  # Add category field
                            'fallback_selectors': item.get('fallback_selectors', []),  # Add fallback selectors
                            'metadata': item.get('metadata', {})
                        }
                        
                        # Cache the main prompt
                        self.dataset_cache[prompt] = cache_entry
                        
                        # Also cache all prompt_variations (check both root level and metadata)
                        variations = item.get('prompt_variations', [])
                        if not variations and 'metadata' in item:
                            variations = item.get('metadata', {}).get('prompt_variations', [])
                        
                        for variation in variations:
                            variation_key = variation.strip().lower()
                            if variation_key and variation_key != prompt:  # Don't duplicate main prompt
                                self.dataset_cache[variation_key] = cache_entry
                        
                        # Debug specific prompts
                        if 'close' in prompt and 'dialog' in prompt:
                            print(f"[DATASET LOAD] Loaded 'close dialog' prompt: {prompt} -> code: {item.get('code', '')[:100]}...")
                
                print(f"[DATASET] Loaded {len(prompts)} unique code patterns from combined-training-dataset-final.json")
                print(f"[DATASET] Expanded to {len(self.dataset_cache)} unique prompts (with variations)")
        
        except Exception as e:
            print(f"[ERROR] Could not load dataset: {e}")
            print(f"[ERROR] Please ensure combined-training-dataset-final.json exists in resources/ml_data/datasets/")
            raise SystemExit(f"Critical: Dataset file not found. Cannot proceed without training data.")
    
    def _load_pagehelper_patterns(self):
        """Load PageHelper patterns dataset (Phase 5).
        
        This dataset contains 63 PageHelper methods with prompt variations
        for label-based interactions (input fields, dropdowns, checkboxes, etc.).
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        pagehelper_path = os.path.join(project_root, 'resources', 'ml_data', 'datasets', 'page-helper-patterns-dataset.json')
        
        try:
            with open(pagehelper_path, 'r', encoding='utf-8') as f:
                pagehelper_data = json.load(f)
                
                # Build cache from PageHelper patterns
                for item in pagehelper_data:
                    method_name = item.get('method_name', '')
                    code_template = item.get('code_template', '')
                    prompt_variations = item.get('prompt_variations', [])
                    category = item.get('category', '')
                    returns = item.get('returns', '')
                    
                    # Cache each prompt variation
                    for variation in prompt_variations:
                        prompt_key = variation.lower().strip()
                        self.pagehelper_cache[prompt_key] = {
                            'method_name': method_name,
                            'code_template': code_template,
                            'category': category,
                            'returns': returns,
                            'parameters': item.get('parameters', {}),
                            'example_usage': item.get('example_usage', '')
                        }
                
                print(f"[PAGEHELPER] Loaded {len(self.pagehelper_cache)} PageHelper prompt variations")
        except Exception as e:
            print(f"[WARNING] Could not load PageHelper patterns dataset: {e}")
    
    def _load_method_mappings(self):
        """Load method name mappings from dataset file."""
        self.method_mappings = {}
        
        # Determine the project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        mappings_path = os.path.join(project_root, 'resources', 'ml_data', 'datasets', 'method-name-mappings.json')
        
        try:
            if os.path.exists(mappings_path):
                with open(mappings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.method_mappings = data.get('mappings', {})
                    # Debug output removed in production
            else:
                print(f"[WARNING] Method mappings file not found: {mappings_path}")
                # Initialize with empty mappings
                self.method_mappings = {
                    'python': {'type_conversions': [], 'method_mappings': []},
                    'javascript': {'type_conversions': [], 'method_mappings': []},
                    'csharp': {'type_conversions': [], 'method_patterns': []}
                }
        except Exception as e:
            print(f"[ERROR] Failed to load method mappings: {e}")
            self.method_mappings = {
                'python': {'type_conversions': [], 'method_mappings': []},
                'javascript': {'type_conversions': [], 'method_mappings': []},
                'csharp': {'type_conversions': [], 'method_patterns': []}
            }
    
    def _normalize_with_synonyms(self, text: str) -> str:
        """REFACTORED: Now delegates to dataset_matcher module."""
        return self.dataset_matcher.normalize_with_synonyms(text)

    def _find_dataset_match(self, prompt: str, return_alternatives: bool = True):
        """REFACTORED: Now delegates to dataset_matcher module."""
        preserve_placeholder = getattr(self, '_preserve_data_placeholder', False)
        return self.dataset_matcher.find_dataset_match(prompt, return_alternatives, preserve_placeholder)

    def _is_template(self, entry: dict) -> bool:
        """REFACTORED: Now delegates to dataset_matcher module."""
        return self.dataset_matcher._is_template(entry)

    def get_last_alternatives(self) -> List[Dict]:
        """REFACTORED: Now delegates to dataset_matcher module."""
        return self.dataset_matcher.get_last_alternatives()

    def _find_pagehelper_match(self, prompt: str):
        """REFACTORED: Now delegates to dataset_matcher module."""
        return self.dataset_matcher.find_pagehelper_match(prompt)

    def _generate_from_pagehelper(self, prompt: str, pagehelper_match: dict, language: str, comprehensive_mode: bool) -> str:
        """REFACTORED: Now delegates to dataset_matcher module."""
        preserve_placeholder = getattr(self, '_preserve_data_placeholder', False)
        return self.dataset_matcher.generate_from_pagehelper(prompt, pagehelper_match, language, comprehensive_mode, preserve_placeholder)

    def _extract_pagehelper_params(self, prompt: str, pagehelper_match: dict) -> dict:
        """REFACTORED: Now delegates to dataset_matcher module."""
        return self.dataset_matcher.extract_pagehelper_params(prompt, pagehelper_match)

    def _handle_universal_input_pattern(self, prompt: str, language: str, comprehensive_mode: bool) -> str:
        """REFACTORED: Now delegates to universal_patterns module."""
        preserve_placeholder = getattr(self, '_preserve_data_placeholder', False)
        return self.universal_handler.handle_universal_input_pattern(
            prompt, language, comprehensive_mode, preserve_placeholder
        )

    def _generate_field_selectors(self, field_name: str) -> list:
        """Generate multiple CSS selector strategies for a field name.
        
        REFACTORED: Now delegates to locator_utils module.
        """
        return self.locator_utils.generate_field_selectors(field_name)
    
    def _sort_selectors_by_specificity(self, selectors: list) -> list:
        """Sort selectors by specificity - most specific first.
        
        Specificity scoring (higher = more specific):
        - ID selector: 1000 points (e.g., input[id='username'])
        - Name selector: 800 points (e.g., input[name='email'])
        - Data-test attributes: 900 points (e.g., [data-testid='email'])
        - Multiple attributes: 700 points (e.g., input[type='email'][name='email'])
        - Single type/class: 500 points (e.g., input[type='email'])
        - XPath with label context: 600 points
        - Generic XPath: 400 points
        
        Returns:
            Sorted list with most specific selectors first
        """
        import re
        
        def calculate_specificity(selector: str) -> int:
            score = 0
            
            # ID selectors - highest specificity
            if re.search(r"\[id=['\"]", selector) or re.search(r"#[\w-]+", selector):
                score += 1000
            
            # Data-test attributes - very specific
            if re.search(r"\[data-test", selector):
                score += 900
            
            # Name attributes - high specificity
            if re.search(r"\[name=['\"]", selector):
                score += 800
            
            # Multiple attributes - good specificity
            attribute_count = len(re.findall(r"\[[\w-]+[*^$|~]?=['\"]", selector))
            if attribute_count > 1:
                score += 700
            elif attribute_count == 1 and not any(x in selector for x in ['[id=', '[name=', '[data-test']):
                score += 500
            
            # XPath with label/text context - moderate specificity
            if selector.startswith('xpath://') and any(x in selector for x in ['label', 'text()', 'normalize-space']):
                score += 600
            elif selector.startswith('xpath://'):
                score += 400
            
            # Penalize overly generic selectors
            if selector in ['input', 'button', 'select', 'textarea', 'a']:
                score -= 500
            
            # Type-only selectors - lowest specificity (but still useful as fallback)
            if re.match(r"^(input|button|select|textarea|a)\[type=['\"][^'\"]+['\"]\]$", selector):
                score += 300
            
            return score
        
        # Sort by specificity (descending - highest first)
        sorted_selectors = sorted(selectors, key=calculate_specificity, reverse=True)
        
        return sorted_selectors
    
    def _generate_code_with_fallbacks(self, prompt: str, fallback_selectors: list, action_type: str, language: str, comprehensive_mode: bool, compact_mode: bool = False) -> str:
        """Generate code with OPTIMIZED fallback selector support - 10-20x faster!
        
        REFACTORED: Now delegates to fallback_strategy module.
        
        Performance optimizations:
        - Reduced timeout: 2s instead of 10s (5x faster)
        - Instant check first: Try visible elements immediately (no wait)
        - Limited selectors: Top 6 only (2-3x faster)
        - Hybrid strategy: Fast path + fallback path
        - NEW: Compact mode - 70% smaller code for DB/CI-CD
        """
        preserve_placeholder = getattr(self, '_preserve_data_placeholder', False)
        return self.fallback_generator.generate_code_with_fallbacks(
            prompt, 
            fallback_selectors, 
            action_type, 
            language, 
            comprehensive_mode,
            value_extractor_func=self._extract_input_value,
            preserve_placeholder=preserve_placeholder,
            compact_mode=compact_mode
        )

    def _enhance_dataset_code_comprehensive(self, java_code: str, action_type: str, prompt: str, language: str) -> str:
        """Enhance simple dataset code to comprehensive code with waits and strategies.
        
        NOW UNIVERSAL: Works for ALL code, not just custom helpers.
        Uses the ComprehensiveCodeGenerator module for clean separation of concerns.
        """
        print(f"[COMPREHENSIVE] Enhancing dataset code to comprehensive mode")
        print(f"[COMPREHENSIVE] Original code: {java_code}")
        print(f"[COMPREHENSIVE] Action type: {action_type}")
        
        # Use the universal comprehensive code generator
        # This works for ALL prompts, not just custom helpers
        comprehensive_code = self.comprehensive_generator.enhance_to_comprehensive(
            simple_code=java_code,
            prompt=prompt,
            language=language
        )
        
        print(f"[COMPREHENSIVE] ✅ Generated comprehensive code: {comprehensive_code[:200]}...")
        return comprehensive_code
    
    def _convert_code_to_language(self, code: str, language: str) -> str:
        """REFACTORED: Now delegates to language_converter module.
        
        Convert code to target language. Dataset now has Python code by default.
        """
        # Lazy initialization of language_converter
        if self.language_converter is None:
            self.language_converter = LanguageConverter(method_mappings=self.method_mappings)
        
        return self.language_converter.convert_code_to_language(code, language)
    
    def _java_to_python_by(self, java_by_method: str) -> str:
        """REFACTORED: Now delegates to language_converter module."""
        if self.language_converter is None:
            self.language_converter = LanguageConverter(method_mappings=self.method_mappings)
        return self.language_converter.java_to_python_by(java_by_method)
    
    def _convert_by_to_playwright(self, by_type: str, value: str) -> str:
        """REFACTORED: Now delegates to language_converter module."""
        if self.language_converter is None:
            self.language_converter = LanguageConverter(method_mappings=self.method_mappings)
        return self.language_converter.convert_by_to_playwright(by_type, value)
    
    def _convert_by_to_cypress(self, by_type: str, value: str) -> str:
        """REFACTORED: Now delegates to language_converter module."""
        if self.language_converter is None:
            self.language_converter = LanguageConverter(method_mappings=self.method_mappings)
        return self.language_converter.convert_by_to_cypress(by_type, value)
    
    def _simple_code_from_locator(self, locator: str, action_type: str, prompt: str) -> str:
        """Generate SIMPLE raw Selenium code from locator (no waits).
        
        This replaces 200+ lines of comprehensive logic in _generate_from_locator.
        Returns simple code that ComprehensiveCodeGenerator can enhance universally.
        
        Args:
            locator: Locator string (By.id("btn") or xpath)
            action_type: Action from dataset  
            prompt: User prompt for context
        
        Returns:
            Simple Selenium code (e.g., driver.findElement(By.id("btn")).click();)
        """
        # Parse locator: By.method("value") or raw xpath
        locator_match = re.match(r'By\.(\w+)\("([^"]+)"\)', locator)
        if locator_match:
            by_method = locator_match.group(1)
            locator_value = locator_match.group(2)
        elif locator.startswith('//'):
            by_method = 'xpath'
            locator_value = locator
        else:
            by_method = 'id'
            locator_value = 'elementId'
        
        # Determine action from prompt (simplified)
        prompt_lower = prompt.lower()
        
        if 'table' in prompt_lower and ('row' in prompt_lower or 'count' in prompt_lower):
            return f'List<WebElement> rows = driver.findElements(By.{by_method}("{locator_value}")); int count = rows.size();'
        
        elif 'get' in prompt_lower and ('message' in prompt_lower or 'text' in prompt_lower):
            return f'String text = driver.findElement(By.{by_method}("{locator_value}")).getText();'
        
        elif 'enabled' in prompt_lower or 'disabled' in prompt_lower:
            return f'boolean isEnabled = driver.findElement(By.{by_method}("{locator_value}")).isEnabled();'
        
        elif 'select' in prompt_lower or 'dropdown' in prompt_lower:
            value = self._extract_input_value(prompt) or 'Option'
            return f'Select dropdown = new Select(driver.findElement(By.{by_method}("{locator_value}"))); dropdown.selectByVisibleText("{value}");'
        
        elif 'enter' in prompt_lower or 'type' in prompt_lower or 'input' in prompt_lower:
            value = self._extract_input_value(prompt) or 'value'
            return f'driver.findElement(By.{by_method}("{locator_value}")).sendKeys("{value}");'
        
        elif 'checkbox' in prompt_lower:
            return f'WebElement checkbox = driver.findElement(By.{by_method}("{locator_value}")); if (!checkbox.isSelected()) {{ checkbox.click(); }}'
        
        else:
            # Default: click
            return f'driver.findElement(By.{by_method}("{locator_value}")).click();'
    
    def _generate_label_based_fallbacks(self, prompt: str) -> list:
        """Generate fallback locators based on label text extracted from prompt.
        
        DEPRECATED: Label-based fallbacks are now in the dataset.
        This method is kept for backward compatibility but returns empty list.
        All label-based XPath strategies have been moved to the dataset's 
        fallback_selectors for better centralization and performance.
        
        See combined-training-dataset-final.json for label-based strategies.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            Empty list (fallbacks now in dataset)
        """
        # Method body removed - all label fallbacks now in dataset
        return []
    
    def _generate_from_locator(self, prompt: str, locator: str, action_type: str, element_type: str, fallback_locators: list = None, language: str = 'java', comprehensive_mode: bool = False) -> str:
        """Generate Selenium code from locator (SIMPLIFIED - uses ComprehensiveCodeGenerator).
        
        This method is now minimal - it generates simple code then enhances if needed.
        Replaces 370 lines of hardcoded logic with clean dataset-driven approach.
        
        Args:
            prompt: Natural language prompt
            locator: Locator string (By.id("btn") or xpath)
            action_type: Action from dataset
            element_type: Element type from dataset
            language: Target language
            comprehensive_mode: If True, enhance with ComprehensiveCodeGenerator
        """
        # Generate simple code from locator
        simple_code = self._simple_code_from_locator(locator, action_type, prompt)
        
        # Comprehensive mode: Enhance with ComprehensiveCodeGenerator
        if comprehensive_mode:
            return self.comprehensive_generator.enhance_to_comprehensive(
                simple_code=simple_code,
                prompt=prompt,
                language=language
            )
        
        # Simple mode: Convert to target language
        return self._convert_code_to_language(simple_code, language) if language != 'java' else simple_code
    
    def clean_output(self, text: str) -> str:
        """Clean and format the generated output."""
        # Remove excessive special characters
        text = re.sub(r'[|:><]+\s*[|:><]+', ' ', text)
        
        # Remove standalone symbols
        text = re.sub(r'\s+[|:><]\s+', ' ', text)
        
        # Clean up entry patterns
        text = re.sub(r'entry[:|]\s*entry', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove trailing symbols
        text = re.sub(r'[|:><]+$', '', text)
        
        return text.strip()
    
    def extract_code_snippet(self, text: str) -> str:
        """Extract valid code patterns from generated text."""
        # Look for Java/Selenium patterns
        patterns = [
            r'driver\.\w+\([^)]*\)',
            r'By\.\w+\([^)]*\)',
            r'WebElement\s+\w+',
            r'findElement\([^)]*\)',
            r'sendKeys\([^)]*\)',
            r'click\(\)',
            r'@\w+',
        ]
        
        snippets = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            snippets.extend(matches)
        
        return ' '.join(snippets) if snippets else text
    
    def infer(self, prompt: str, return_alternatives: bool = False, language: str = 'java', comprehensive_mode: bool = False, preserve_data_placeholder: bool = False, compact_mode: bool = False, ignore_fallbacks: bool = False):
        """Inference method for Test Builder/Recorder - returns dict with code and xpath.
        
        This is the main entry point used by test_suite_runner.py and api_server_modular.py.
        
        Args:
            prompt: User's natural language prompt
            return_alternatives: If True, includes alternative matches in response
            language: Target language (default: 'java')
            comprehensive_mode: If True, generates comprehensive code
            preserve_data_placeholder: If True, keeps {VALUE} placeholder instead of extracting value from prompt (for Test Builder)
            compact_mode: If True, generates compact code without fallback_selectors (for Test Builder)
            ignore_fallbacks: If True, skips fallback_selectors even if present (generates simple code)
        
        Returns:
            dict with keys:
                - 'code': Generated code string
                - 'xpath': XPath/locator string
                - 'alternatives': List of alternative matches (if return_alternatives=True)
        """
        # Store preserve_data_placeholder for use in nested calls
        self._preserve_data_placeholder = preserve_data_placeholder
        
        # Try to find dataset match first to get XPath ​
        dataset_result = self._find_dataset_match(prompt, return_alternatives=return_alternatives)
        dataset_match = dataset_result.get('match') if isinstance(dataset_result, dict) else dataset_result
        alternatives = dataset_result.get('alternatives', []) if isinstance(dataset_result, dict) else []
        
        # Generate code using generate_clean (pass compact_mode AND ignore_fallbacks through)
        generated_code = self.generate_clean(prompt, max_tokens=50, temperature=0.3, language=language, comprehensive_mode=comprehensive_mode, compact_mode=compact_mode, ignore_fallbacks=ignore_fallbacks)
        
        # Get XPath from dataset match if available
        xpath = ''
        if dataset_match:
            xpath = dataset_match.get('xpath', dataset_match.get('locator', ''))
        
        # Build response
        result = {
            'code': generated_code,
            'xpath': xpath
        }
        
        if return_alternatives and alternatives:
            result['alternatives'] = alternatives
        
        return result
    
    def generate_clean(self, prompt: str, max_tokens: int = 30, temperature: float = 0.3, language: str = 'java', comprehensive_mode: bool = False, ignore_fallbacks: bool = False, compact_mode: bool = False):
        """Generate with cleaning and formatting using template-based approach.
        
        Args:
            prompt: The user's natural language prompt
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            language: Target programming language ('java', 'python', 'javascript', 'csharp')
            comprehensive_mode: If True, generates comprehensive code with multiple strategies (for Generate Code module)
                               If False, generates simpler code (for Test Recorder/Builder modules)
            ignore_fallbacks: If True, ignores fallback_selectors even if present in dataset (respects with_fallbacks: false from UI)
            compact_mode: If True, generates 70% smaller code perfect for DB storage and CI/CD
        """
        print(f"[CODE GEN] Generating {language} code for prompt: '{prompt}' (comprehensive={comprehensive_mode}, ignore_fallbacks={ignore_fallbacks}, compact={compact_mode})")
        
        # NEW: Use Local AI Engine for intelligent understanding (if enabled)
        ai_understanding = None
        if self.enable_local_ai:
            try:
                ai_understanding = self.local_ai.understand_prompt(prompt)
                print(f"[LOCAL-AI] Intent: {ai_understanding['intent']} (confidence: {ai_understanding['confidence']:.2f})")
                print(f"[LOCAL-AI] Entities: {ai_understanding['entities']}")
                
                # If AI has high confidence, use its execution plan
                if ai_understanding['confidence'] >= 0.85:
                    print(f"[LOCAL-AI] ✓ High confidence - using AI execution plan")
                    ai_code = self._generate_from_ai_plan(ai_understanding, language, comprehensive_mode, compact_mode)
                    if ai_code:
                        # Learn from this execution for future improvements
                        self.local_ai.learn_from_execution(prompt, ai_understanding, True)
                        return ai_code
                else:
                    print(f"[LOCAL-AI] ⚠ Low confidence - falling back to hybrid matching")
            except Exception as e:
                print(f"[LOCAL-AI] Error: {e}, falling back to hybrid matching")
        
        # Store flags in instance variables so nested calls can access them
        self._comprehensive_mode = comprehensive_mode
        self._compact_mode = compact_mode
        
        # Check if prompt contains multiple actions separated by "and"
        if ' and ' in prompt.lower():
            # Split the compound prompt into individual actions
            actions = self._split_compound_prompt(prompt)
            if len(actions) > 1:
                # Generate code for each action and combine
                combined_code = []
                for i, action in enumerate(actions, 1):
                    code = self.generate_clean(action.strip(), max_tokens, temperature, language, comprehensive_mode, ignore_fallbacks)
                    # Add step comment in appropriate style
                    comment_prefix = '//' if language in ['java', 'javascript', 'csharp'] else '#'
                    combined_code.append(f"{comment_prefix} Step {i}: {action.strip()}")
                    combined_code.append(code)
                    combined_code.append("")  # Empty line between steps
                return "\n".join(combined_code).strip()
        
        # Parse the prompt for common patterns
        prompt_lower = prompt.lower()
        
        # PRIORITY 1: Try dataset lookup FIRST (to use curated fallback_selectors)
        # HYBRID MODE: returns match + alternatives
        dataset_result = self._find_dataset_match(prompt, return_alternatives=True)
        dataset_match = dataset_result['match'] if isinstance(dataset_result, dict) else dataset_result
        alternatives = dataset_result.get('alternatives', []) if isinstance(dataset_result, dict) else []
        
        # Check if dataset match has fallback_selectors - if yes, prioritize it
        has_fallback_selectors = (dataset_match and 
                                 dataset_match.get('fallback_selectors') and 
                                 len(dataset_match.get('fallback_selectors', [])) > 1)
        
        # PRIORITY 2: Universal handler as fallback (if no dataset match with fallback_selectors)
        # This allows ANY field name to work, not just hardcoded dataset entries
        if not has_fallback_selectors and re.search(r'(?:enter|type|input|fill)\s+.+?\s+in\s+', prompt_lower):
            print(f"[UNIVERSAL] No dataset fallback_selectors found, trying universal handler")
            universal_code = self._handle_universal_input_pattern(prompt, language, comprehensive_mode)
            if universal_code:
                print(f"[UNIVERSAL] ✅ Successfully generated code using universal pattern")
                return universal_code
            else:
                print(f"[UNIVERSAL] Pattern match failed, continuing to dataset processing")
        
        print(f"[DATASET] Prompt: '{prompt}'")
        print(f"[DATASET] Match found: {dataset_match is not None}")
        if dataset_match:
            print(f"[DATASET] Locator: {dataset_match.get('locator')}")
            print(f"[DATASET] Code: {dataset_match.get('code')}")
            print(f"[DATASET] Action: {dataset_match.get('action')}")
        
        # Store alternatives in instance variable for later retrieval
        self._last_alternatives = alternatives
        
        # DEBUG: Log alternatives for tracing
        print(f"[ALTERNATIVES DEBUG] Stored {len(alternatives)} alternatives from dataset matcher:")
        for i, alt in enumerate(alternatives[:3], 1):
            print(f"  {i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')}")
        
        # TRACE: Check if DatasetMatcher has the correct alternatives
        matcher_alts = self.dataset_matcher.get_last_alternatives()
        print(f"[ALTERNATIVES TRACE] DatasetMatcher has {len(matcher_alts)} alternatives:")
        for i, alt in enumerate(matcher_alts[:3], 1):
            print(f"  {i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')}")
        
        # DEBUG: Write what we found
        with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Prompt: {prompt}\n")
            f.write(f"Language: {language}\n")
            f.write(f"Comprehensive mode: {comprehensive_mode}\n")
            f.write(f"Dataset match found: {dataset_match is not None}\n")
            if dataset_match:
                f.write(f"Has code: {dataset_match.get('code') is not None}\n")
                if dataset_match.get('code'):
                    f.write(f"Code (first 100): {dataset_match.get('code')[:100]}\n")
        
        # If dataset has direct code, use ComprehensiveCodeGenerator for enhancement
        if dataset_match and dataset_match.get('code'):
            # DEBUG: Entered this block
            with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
                f.write(f"ENTERED: dataset has code block\n")
            
            # IMPORTANT: Dataset code is stored in PYTHON format, not Java!
            python_code = dataset_match['code']
            fallback_selectors = dataset_match.get('fallback_selectors', [])
            
            print(f"[DATASET] Code (Python format): {python_code[:80]}...")
            print(f"[DATASET] Target language: {language}")
            if fallback_selectors:
                print(f"[DATASET] Found {len(fallback_selectors)} fallback selectors")
            
            # DEBUG: Check fallback_selectors path
            with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
                f.write(f"Fallback selectors count: {len(fallback_selectors)}\n")
                f.write(f"ignore_fallbacks: {ignore_fallbacks}\n")
            
            # Check if this is a custom helper method (abstracted, not raw Selenium)
            is_custom_helper = ('(' in python_code and ')' in python_code and 
                              'driver.find' not in python_code.lower() and
                              'driver.get' not in python_code.lower() and
                              'By.' not in python_code)
            
            if is_custom_helper and comprehensive_mode and dataset_match.get('locator'):
                # Custom helper + comprehensive mode: Generate raw Selenium from locator first
                print(f"[DATASET] Custom helper in comprehensive mode - generating explicit Selenium")
                locator = dataset_match['locator']
                action_type = dataset_match.get('action', '')
                
                # Generate simple Selenium code from locator
                simple_selenium = self._simple_code_from_locator(locator, action_type, prompt)
                
                # Now enhance with ComprehensiveCodeGenerator
                return self.comprehensive_generator.enhance_to_comprehensive(
                    simple_code=simple_selenium,
                    prompt=prompt,
                    language=language
                )
            
            # If fallback_selectors available AND ignore_fallbacks is False, regenerate code with fallback logic
            # compact_mode will generate 70% smaller code while still using fallback selectors for self-healing
            if fallback_selectors and len(fallback_selectors) > 1 and not ignore_fallbacks:
                # DEBUG
                with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
                    f.write(f"ENTERED: fallback_selectors path (will NOT convert to {language}!)\n")
                
                # CRITICAL FIX: Order selectors by SPECIFICITY (most specific first)
                # This ensures accurate targeting: ID > Name > Combined > Type-only
                primary_xpath = dataset_match.get('xpath', '')
                
                # Ensure primary xpath is in the list
                if primary_xpath and primary_xpath not in fallback_selectors:
                    fallback_selectors = [primary_xpath] + fallback_selectors
                
                # Sort by specificity (higher score = try first)
                fallback_selectors = self._sort_selectors_by_specificity(fallback_selectors)
                
                print(f"[DATASET] Ordered {len(fallback_selectors)} selectors by specificity (most specific first)")
                print(f"[DATASET] Top 3 selectors: {fallback_selectors[:3]}")
                
                mode_desc = "compact" if compact_mode else "standard"
                print(f"[DATASET] Generating {mode_desc} code with fallback strategy")
                action_type = dataset_match.get('category', 'click')
                return self._generate_code_with_fallbacks(
                    prompt, fallback_selectors, action_type, language, comprehensive_mode, compact_mode
                )
            
            # If ignore_fallbacks is True, skip fallback generation even if selectors exist
            if ignore_fallbacks and fallback_selectors:
                print(f"[DATASET] ignore_fallbacks=True, skipping {len(fallback_selectors)} fallback selectors - using primary code only")
                # DEBUG
                with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
                    f.write(f"ignore_fallbacks is TRUE, skipping fallback generation\n")
            
            # Comprehensive mode: Use ComprehensiveCodeGenerator (universal enhancement!)
            if comprehensive_mode:
                # DEBUG
                with open('debug_dataset_match.txt', 'a', encoding='utf-8') as f:
                    f.write(f"ENTERED: comprehensive_mode is TRUE\n")
                    f.write(f"Checking for WebDriverWait in code...\n")
                # **FIX: Check if code is already comprehensive!**
                # If it already has WebDriverWait, it's comprehensive Python code - convert to target language
                if 'WebDriverWait' in python_code or 'webdriverwait' in python_code.lower():
                    print(f"[DATASET] Code already comprehensive (Python), converting to {language}")
                    print(f"[DATASET] BEFORE CONVERSION (Python): {python_code[:150]}...")
                    
                    # DEBUG: Write to file to verify this code path is executing
                    with open('debug_conversion.txt', 'a', encoding='utf-8') as f:
                        f.write(f"\n{'='*80}\n")
                        f.write(f"[{language.upper()} CONVERSION STARTED]\n")
                        f.write(f"Prompt: {prompt}\n")
                        f.write(f"Python code (first 200 chars): {python_code[:200]}\n")
                    
                    # **CRITICAL FIX**: Dataset code is PYTHON, always convert to target language
                    converted_code = self._convert_code_to_language(python_code, language)
                    print(f"[DATASET] AFTER CONVERSION ({language}): {converted_code[:150]}...")
                    
                    # DEBUG: Write result
                    with open('debug_conversion.txt', 'a', encoding='utf-8') as f:
                        f.write(f"Converted code (first 200 chars): {converted_code[:200]}\n")
                        f.write(f"[CONVERSION COMPLETE]\n")
                    
                    return converted_code
                else:
                    print(f"[DATASET] Enhancing simple Python code with ComprehensiveCodeGenerator for {language}")
                    return self.comprehensive_generator.enhance_to_comprehensive(
                        simple_code=python_code,
                        prompt=prompt,
                        language=language
                    )
            
            # Simple mode: Use dataset code directly (Test Builder/Recorder)
            print(f"[DATASET] Using simple code for Test Builder/Recorder, converting to {language}")
            # **CRITICAL FIX**: Always convert from Python (dataset format) to target language
            return self._convert_code_to_language(python_code, language)
        
        # Otherwise use locator-based generation (no direct code in dataset)
        if dataset_match and dataset_match.get('locator'):
            locator = dataset_match['locator']
            action_type = dataset_match.get('action', 'click')
            element_type = dataset_match.get('element_type', 'element')
            fallback_locators = list(dataset_match.get('fallback_locators', []))  # Make a copy
            
            # Label-based fallbacks are now in the dataset's fallback_selectors
            # No need for dynamic generation - dataset contains comprehensive XPath strategies
            
            print(f"[DATASET LOCATOR] Found locator: {locator}")
            print(f"[DATASET LOCATOR] Action: {action_type}, Element: {element_type}")
            print(f"[DATASET LOCATOR] Comprehensive mode: {comprehensive_mode}")
            print(f"[DATASET LOCATOR] Total fallbacks from dataset: {len(fallback_locators)}")
            
            # Convert locator and generate code with fallback support for target language
            return self._generate_from_locator(prompt, locator, action_type, element_type, fallback_locators, language, comprehensive_mode)
        
        # Phase 5: Try PageHelper pattern matching
        # In comprehensive mode, skip PageHelper to generate explicit Selenium code
        if not comprehensive_mode:
            print(f"[PAGEHELPER] No dataset match, checking PageHelper patterns")
            pagehelper_match = self._find_pagehelper_match(prompt)
            if pagehelper_match:
                print(f"[PAGEHELPER] ✅ Found PageHelper method: {pagehelper_match['method_name']}")
                try:
                    code = self._generate_from_pagehelper(prompt, pagehelper_match, language, comprehensive_mode)
                    if code:
                        print(f"[PAGEHELPER] ✅ Generated code using PageHelper method")
                        return code
                except Exception as e:
                    print(f"[PAGEHELPER] ⚠️ PageHelper generation failed: {e}, continuing to pattern matching")
        else:
            print(f"[PAGEHELPER] Skipping PageHelper in comprehensive mode - will generate explicit Selenium code")
        
        # No dataset match - try pattern-based generation (Phase 2B refactoring)
        print(f"[PATTERN] No dataset/PageHelper match, attempting pattern-based generation")
        print(f"[PATTERN] Comprehensive mode: {comprehensive_mode}")
        
        # Try pattern matching first (Phase 2B)
        pattern_match = self.template_engine.match_action(prompt)
        if pattern_match and pattern_match['confidence'] >= 0.7:
            print(f"[PATTERN] Matched action: {pattern_match['action']} (confidence: {pattern_match['confidence']})")
            try:
                # Use pattern-based generation
                code = self._generate_from_pattern(prompt, pattern_match, language, comprehensive_mode)
                if code:
                    print(f"[PATTERN] ✅ Generated code using pattern matching")
                    return code
            except Exception as e:
                print(f"[PATTERN] ⚠️ Pattern generation failed: {e}, falling back to simple generation")
        
        # Final fallback: Generate code using template engine or comprehensive methods
        # All modern paths (dataset, PageHelper, patterns) have been tried
        print(f"[FALLBACK] No matching pattern found, generating {'comprehensive' if comprehensive_mode else 'simple'} code")
        comment_prefix = '//' if language in ['java', 'javascript', 'csharp'] else '#'
        
        # Determine most likely action from prompt
        prompt_lower = prompt.lower()
        
        if 'select' in prompt_lower and ('dropdown' in prompt_lower or 'from' in prompt_lower or 'option' in prompt_lower):
            # Dropdown selection
            element_id = self._extract_element_name(prompt)
            option = self._extract_input_value(prompt) or "Option"
            
            if comprehensive_mode:
                return self._generate_comprehensive_select(element_id, option, language)
            else:
                # Simple mode: Use compact Select code (1-2 lines max)
                return f"{comment_prefix} Select from dropdown\nnew Select(driver.findElement(By.id(\"{element_id}\"))).selectByVisibleText(\"{option}\");"
        
        elif 'click' in prompt_lower:
            element_id = self._extract_element_name(prompt)
            element_type = 'button' if 'button' in prompt_lower else 'link' if 'link' in prompt_lower else 'element'
            
            if comprehensive_mode:
                return self._generate_comprehensive_click(element_type, 'id', element_id, language)
            else:
                code_template = self.template_engine.generate_code(
                    action='click', mode='simple', language=language,
                    element_desc=element_type, locator=element_id, locator_method='id',
                    by_method='id', by_constant='ID'
                )
                return code_template if code_template else f"{comment_prefix} Click {element_type}\ndriver.findElement(By.id(\"{element_id}\")).click();"
        
        elif 'enter' in prompt_lower or 'type' in prompt_lower or 'input' in prompt_lower:
            element_id = self._extract_element_name(prompt)
            value = self._extract_input_value(prompt) or "text"
            field_name = 'email' if 'email' in prompt_lower else 'password' if 'password' in prompt_lower else 'field'
            
            if comprehensive_mode:
                return self._generate_comprehensive_input(field_name, element_id, value, None, None, language)
            else:
                code_template = self.template_engine.generate_code(
                    action='input', mode='simple', language=language,
                    field_name=field_name, locator=element_id, value=value, locator_method='id',
                    by_method='id', by_constant='ID'
                )
                return code_template if code_template else f"{comment_prefix} Enter text\ndriver.findElement(By.id(\"{element_id}\")).sendKeys(\"{value}\");"
        
        elif 'verify' in prompt_lower and 'title' in prompt_lower:
            # Title verification - use driver.getTitle()
            expected_title = self._extract_input_value(prompt) or "Expected Title"
            
            if comprehensive_mode:
                if language == 'java':
                    return f"""// Verify page title  with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.titleContains("{expected_title}"));
String actualTitle = driver.getTitle();
Assert.assertEquals("{expected_title}", actualTitle);"""
                elif language == 'python':
                    return f"""# Verify page title with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
wait.until(EC.title_contains("{expected_title}"))
actual_title = driver.title
assert actual_title == "{expected_title}"  """
            else:
                return f"{comment_prefix} Verify title\nString title = driver.getTitle();\nAssert.assertEquals(\"{expected_title}\", title);"
        
        else:
            # Generic fallback for any other action
            element_id = self._extract_element_name(prompt)
            
            if comprehensive_mode:
                # Use comprehensive click as generic fallback
                return self._generate_comprehensive_click('element', 'id', element_id, language)
            else:
                return f"{comment_prefix} {prompt}\ndriver.findElement(By.id(\"{element_id}\")).click();"
    
    def _generate_from_pattern(self, prompt: str, pattern_match: dict, language: str, comprehensive_mode: bool) -> str:
        """Generate code using pattern matching and template engine (Phase 2B).
        
        This replaces the massive if/elif chains with a clean pattern-based approach.
        
        Args:
            prompt: User's natural language prompt
            pattern_match: Result from template_engine.match_action()
            language: Target language
            comprehensive_mode: Simple or comprehensive code
        
        Returns:
            Generated code string or None if pattern can't be handled
        """
        action = pattern_match['action']
        print(f"[PATTERN GEN] Generating {action} code for: '{prompt}'")
        
        # Extract parameters inline (simplified)
        prompt_lower = prompt.lower()
        
        # Smart locator generation: Use type attribute for email/password fields
        if 'email' in prompt_lower and 'field' in prompt_lower:
            # For "email field", use CSS selector targeting type="email"
            element_id = '[type="email"]'
            locator_method = 'css_selector'
        elif 'password' in prompt_lower and 'field' in prompt_lower:
            # For "password field", use CSS selector targeting type="password"
            element_id = '[type="password"]'
            locator_method = 'css_selector'
        elif 'email' in prompt_lower:
            element_id = 'email'
            locator_method = 'id'
        elif 'password' in prompt_lower:
            element_id = 'password'
            locator_method = 'id'
        elif 'submit' in prompt_lower:
            element_id = 'submitBtn'
            locator_method = 'id'
        else:
            element_id = 'elementId'
            locator_method = 'id'
            
        value = re.search(r'(?:enter|type)\s+([^\s]+)', prompt, re.IGNORECASE)
        value = value.group(1) if value else ''
        
        # Handle different action types
        if action == 'click':
            # Determine element type for comment
            if 'button' in prompt.lower():
                element_comment = 'button'
            elif 'link' in prompt.lower():
                element_comment = 'link'
            else:
                element_comment = 'element'
            
            if comprehensive_mode:
                return self._generate_comprehensive_click(element_comment, locator_method, element_id, language)
            else:
                # Use template for simple mode
                return self.template_engine.generate_code(
                    action='click',
                    mode='simple',
                    language=language,
                    element_desc=element_comment,
                    by_method=locator_method,
                    locator=element_id
                )
        
        elif action == 'input':
            # Determine field name
            prompt_lower = prompt.lower()
            if 'email' in prompt_lower:
                field_name = 'email'
            elif 'password' in prompt_lower:
                field_name = 'password'
            elif 'username' in prompt_lower:
                field_name = 'username'
            else:
                field_name = 'input'
            
            if comprehensive_mode:
                return self._generate_comprehensive_input(field_name, element_id, value, None, None, language)
            else:
                # Use template for simple mode
                return self.template_engine.generate_code(
                    action='input',
                    mode='simple',
                    language=language,
                    field_name=field_name,
                    by_method=locator_method,
                    locator=element_id,
                    value=value
                )
        
        elif action == 'select':
            option_text = value or "Option"
            
            if comprehensive_mode:
                return self._generate_comprehensive_select(element_id, option_text, language)
            else:
                # Use template for simple mode
                return self.template_engine.generate_code(
                    action='select',
                    mode='simple',
                    language=language,
                    by_method=locator_method,
                    locator=element_id,
                    option=option_text
                )
        
        elif action == 'verify' or action == 'verify_title' or action == 'verify_text':
            expected_value = value or "Expected"
            
            # Detect specific sub-types
            if 'title' in prompt.lower():
                action = 'verify_title'
                # Extract expected title value from prompt
                title_match = re.search(r'(?:title|page title)\s+(?:is|equals?|contains?)\s+([^\s,]+(?:\s+[^\s,]+)*)', prompt, re.IGNORECASE)
                if title_match:
                    expected_value = title_match.group(1).strip()
            
            elif 'checkbox' in prompt.lower():
                # This is actually a checkbox action, not verification
                element_id = 'agreeCheckbox' if 'agree' in prompt.lower() else 'checkbox'
                
                if comprehensive_mode:
                    if language == 'java':
                        return f"""// Check checkbox with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement checkbox = wait.until(ExpectedConditions.elementToBeClickable(By.id("{element_id}")));
if (!checkbox.isSelected()) {{
    checkbox.click();
}}"""
                    elif language == 'python':
                        return f"""# Check checkbox with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
checkbox = wait.until(EC.element_to_be_clickable((By.ID, "{element_id}")))
if not checkbox.is_selected():
    checkbox.click()"""
                else:
                    return f"""// Check checkbox
WebElement checkbox = driver.findElement(By.id("{element_id}"));
if (!checkbox.isSelected()) {{
    checkbox.click();
}}"""
            
            if action == 'verify_title':
                if comprehensive_mode:
                    return self._generate_comprehensive_verify_title(expected_value, language)
                else:
                    # Simple title verification
                    if language == 'python':
                        return f"""# Verify page title
actual_title = driver.title
assert actual_title == "{expected_value}", f"Expected '{expected_value}' but got '{{actual_title}}'" """
                    elif language == 'java':
                        return f"""// Verify page title
String actualTitle = driver.getTitle();
Assert.assertEquals("{expected_value}", actualTitle);"""
                    elif language == 'javascript':
                        return f"""// Verify page title
let actualTitle = await driver.getTitle();
assert.strictEqual(actualTitle, "{expected_value}");"""
                    else:  # C#
                        return f"""// Verify page title
string actualTitle = driver.Title;
Assert.AreEqual("{expected_value}", actualTitle);"""
            
            elif action == 'verify_text':
                if comprehensive_mode:
                    return self._generate_comprehensive_verify_text(element_id, expected_value, language)
                else:
                    # Simple text verification
                    if language == 'python':
                        return f"""# Verify element text
element = driver.find_element(By.ID, "{element_id}")
actual_text = element.text
assert actual_text == "{expected_value}" """
                    elif language == 'java':
                        return f"""// Verify element text
WebElement element = driver.findElement(By.id("{element_id}"));
String actualText = element.getText();
Assert.assertEquals("{expected_value}", actualText);"""
                    elif language == 'javascript':
                        return f"""// Verify element text
let element = await driver.findElement(By.id("{element_id}"));
let text = await element.getText();
assert.strictEqual(text, "{expected_value}");"""
                    else:  # C#
                        return f"""// Verify element text
IWebElement element = driver.FindElement(By.Id("{element_id}"));
string text = element.Text;
Assert.AreEqual("{expected_value}", text);"""
            
            else:  # General verify
                if comprehensive_mode:
                    return self._generate_comprehensive_verify_element(element_id, language)
                else:
                    # Simple element verification using template
                    return self.template_engine.generate_code(
                        action='verify',
                        mode='simple',
                        language=language,
                        by_method=locator_method,
                        locator=element_id
                    )
        
        elif action == 'navigate':
            url = value or "https://example.com"
            
            if comprehensive_mode:
                return self._generate_comprehensive_navigate(url, language)
            else:
                # Simple navigate using template
                return self.template_engine.generate_code(
                    action='navigate',
                    mode='simple',
                    language=language,
                    url=url
                )
        
        elif action == 'wait':
            if comprehensive_mode:
                return self._generate_comprehensive_wait(element_id, language)
            else:
                # Simple wait using template
                return self.template_engine.generate_code(
                    action='wait',
                    mode='simple',
                    language=language,
                    by_method=locator_method,
                    locator=element_id,
                    by_constant='ID'
                )
        
        elif action == 'file_upload':
            file_path = value or "path/to/file.txt"
            
            if comprehensive_mode:
                return self._generate_comprehensive_file_upload(file_path, locator_method, element_id, language)
            else:
                # Simple file upload using template
                return self.template_engine.generate_code(
                    action='file_upload',
                    mode='simple',
                    language=language,
                    file_path=file_path,
                    by_method=locator_method,
                    locator=element_id
                )
        
        # If action not handled, return None to trigger fallback
        print(f"[PATTERN GEN] ⚠️ Action '{action}' not fully implemented in pattern generator")
        return None
    
    # ===== PHASE 3 REFACTORING: Parameter Extraction Consolidation =====
    class ParameterExtractor:
        """Unified parameter extraction from prompts (Phase 3 optimization).
        Extracts all parameters in ONE PASS for better performance.
        """
        
        # Compiled regex patterns for faster matching
        VALUE_PATTERNS = [
            re.compile(r'select\s+([^\s]+(?:\s+[^\s]+)*?)\s+from\s+', re.IGNORECASE),
            re.compile(r'enter\s+([^\s]+(?:\s+[^\s]+)*?)\s+in\s+', re.IGNORECASE),
            re.compile(r'type\s+([^\s]+(?:\s+[^\s]+)*?)\s+in(?:to)?\s+', re.IGNORECASE),
            re.compile(r'input\s+([^\s]+(?:\s+[^\s]+)*?)\s+in(?:to)?\s+', re.IGNORECASE),
            re.compile(r'enter\s+"([^"]+)"\s+in\s+', re.IGNORECASE),
            re.compile(r"enter\s+'([^']+)'\s+in\s+", re.IGNORECASE),
        ]
        
        EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        QUOTED_PATTERN = re.compile(r'"([^"]+)"|\'([^\']+)\'')
        
        # Generic placeholder words to ignore
        GENERIC_PLACEHOLDERS = {
            'text', 'data', 'value', 'information', 'content', 'input',
            'string', 'characters', 'words', 'details', 'info'
        }
        
        STOP_WORDS = {'the', 'a', 'an', 'field', 'input', 'box', 'text'}
        
        def __init__(self, dataset_cache: dict, find_dataset_match_func):
            """Initialize with reference to parent's dataset cache and matching function."""
            self.dataset_cache = dataset_cache
            self.find_dataset_match = find_dataset_match_func
        
        def extract_all(self, prompt: str) -> dict:
            """Extract all parameters in one pass (optimized).
            
            Returns:
                dict with keys: element_id, value, locator_type, locator_value, quoted_value
            """
            prompt_lower = prompt.lower()
            
            result = {
                'element_id': None,
                'value': None,
                'locator_type': None,
                'locator_value': None,
                'quoted_value': None
            }
            
            # Extract element ID (tries dataset first, then fallback rules)
            result['element_id'] = self._extract_element_from_prompt(prompt, prompt_lower)
            
            # Extract input value (using compiled patterns)
            result['value'] = self._extract_value_from_prompt(prompt, prompt_lower)
            
            # Extract quoted value if present
            quoted_match = self.QUOTED_PATTERN.search(prompt)
            if quoted_match:
                result['quoted_value'] = quoted_match.group(1) or quoted_match.group(2)
            
            return result
        
        def _extract_element_from_prompt(self, prompt: str, prompt_lower: str) -> str:
            """Extract element ID/locator from prompt."""
            # Try dataset match first
            dataset_match = self.find_dataset_match(prompt, return_alternatives=False)
            if dataset_match:
                locator = dataset_match.get('locator', '')
                if locator:
                    # Extract from By.id("element-id")
                    id_match = re.search(r'By\.id\s*\(\s*"([^"]+)"\s*\)', locator)
                    if id_match:
                        return id_match.group(1)
                    
                    # Extract from By.xpath("xpath")
                    xpath_match = re.search(r'By\.xpath\s*\(\s*"([^"]+)"\s*\)', locator)
                    if xpath_match:
                        return f"xpath:{xpath_match.group(1)}"
                    
                    # Extract from By.cssSelector("css")
                    css_match = re.search(r'By\.cssSelector\s*\(\s*"([^"]+)"\s*\)', locator)
                    if css_match:
                        return f"css:{css_match.group(1)}"
                    
                    # Extract from By.name("name")
                    name_match = re.search(r'By\.name\s*\(\s*"([^"]+)"\s*\)', locator)
                    if name_match:
                        return f"name:{name_match.group(1)}"
            
            # Fallback to rule-based extraction
            return self._extract_element_fallback(prompt_lower)
        
        def _extract_element_fallback(self, prompt_lower: str) -> str:
            """Fallback element extraction using hardcoded rules."""
            # Producer-specific elements
            if 'producer-email' in prompt_lower or 'producer email' in prompt_lower:
                return 'producer-email'
            elif 'producer-password' in prompt_lower or 'producer password' in prompt_lower:
                return 'producer-password'
            elif 'producer-login' in prompt_lower or 'producer login' in prompt_lower:
                return 'xpath://button[@type="submit" and contains(@class, "primary-btn")]'
            
            # Common elements
            if 'login' in prompt_lower:
                return 'loginBtn' if 'button' in prompt_lower else 'username'
            elif 'submit' in prompt_lower:
                return 'submitBtn'
            elif 'success' in prompt_lower or 'message' in prompt_lower:
                return 'successMsg'
            elif 'error' in prompt_lower:
                return 'errorMsg'
            elif 'username' in prompt_lower:
                return 'username'
            elif 'password' in prompt_lower:
                return 'css:[type="password"]' if 'field' in prompt_lower else 'password'
            elif 'email' in prompt_lower:
                return 'css:[type="email"]' if 'field' in prompt_lower else 'email'
            elif 'search' in prompt_lower:
                return 'searchBox'
            elif 'country' in prompt_lower or 'dropdown' in prompt_lower:
                return 'countrySelect'
            else:
                return 'elementId'
        
        def _extract_value_from_prompt(self, prompt: str, prompt_lower: str) -> str:
            """Extract input value from prompt using compiled patterns."""
            # Try each compiled pattern
            for pattern in self.VALUE_PATTERNS:
                match = pattern.search(prompt)
                if match:
                    value = match.group(1).strip()
                    # Filter stop words
                    words = value.split()
                    filtered_words = [w for w in words if w.lower() not in self.STOP_WORDS]
                    extracted_value = ' '.join(filtered_words) if filtered_words else value
                    
                    # Check if it's a generic placeholder
                    if extracted_value.lower() in self.GENERIC_PLACEHOLDERS:
                        return ""  # Return empty for {VALUE} placeholder
                    
                    return extracted_value
            
            # Try email pattern
            email_match = self.EMAIL_PATTERN.search(prompt)
            if email_match:
                return email_match.group(0)
            
            # Try quoted values
            quoted_match = self.QUOTED_PATTERN.search(prompt)
            if quoted_match:
                return quoted_match.group(1) or quoted_match.group(2)
            
            return "your_text_here"  # Fallback placeholder
    
    # ===== END PHASE 3 EXTRACTION CLASS =====
    
    def _extract_element_name(self, prompt: str) -> str:
        """Extract element name from prompt using dataset first, then fallback to rules.
        
        REFACTORED (Phase 3): Now delegates to ParameterExtractor for optimized extraction.
        """
        # Use unified parameter extractor (single-pass extraction)
        params = self.param_extractor_unified.extract_all(prompt)
        return params['element_id']
    
    def _split_compound_prompt(self, prompt: str) -> list:
        """Split a compound prompt into individual actions."""
        import re
        
        # Split by " and " but be careful with "and" within field names or values
        # Use regex to split on " and " that's followed by action verbs
        action_verbs = ['enter', 'type', 'click', 'select', 'verify', 'wait', 'navigate', 'open', 'check']
        
        # Create pattern: " and " followed by action verb
        pattern = r'\s+and\s+(?=' + '|'.join(action_verbs) + r')'
        
        # Split the prompt
        actions = re.split(pattern, prompt, flags=re.IGNORECASE)
        
        # Clean up each action
        actions = [action.strip() for action in actions if action.strip()]
        
        return actions
    
    def _generate_java_style_code(self, prompt: str, locator: str, action_type: str, element_type: str, language: str) -> str:
        """Generate Java, JavaScript, or C# style code."""
        # Parse locator
        locator_match = re.match(r'By\.(\w+)\("([^"]+)"\)', locator)
        if not locator_match:
            locator_match = re.match(r'By\.(\w+)\(\'([^\']+)\'\)', locator)
        
        if not locator_match:
            return f"// {prompt}\ndriver.findElement(By.id(\"elementId\")).click();"
        
        by_method = locator_match.group(1)
        locator_value = locator_match.group(2)
        
        # Java/C# style
        if language in ['java', 'csharp']:
            prefix = "driver.FindElement" if language == 'csharp' else "driver.findElement"
            by_class = "By"
            
            # Map methods
            method_map = {
                'id': 'Id',
                'name': 'Name',
                'className': 'ClassName',
                'cssSelector': 'CssSelector',
                'xpath': 'XPath',
                'linkText': 'LinkText',
                'partialLinkText': 'PartialLinkText',
                'tagName': 'TagName'
            }
            
            by_method_formatted = method_map.get(by_method, by_method.capitalize())
            
            if action_type == 'sendKeys' or 'enter' in prompt.lower() or 'type' in prompt.lower():
                value = self._extract_input_value(prompt)
                return f"""// {prompt}
{prefix}({by_class}.{by_method_formatted}("{locator_value}")).Clear();
{prefix}({by_class}.{by_method_formatted}("{locator_value}")).SendKeys("{value}");"""
            else:  # click
                return f"""// {prompt}
{prefix}({by_class}.{by_method_formatted}("{locator_value}")).Click();"""
        
        # JavaScript style
        elif language == 'javascript':
            by_method_js = by_method[0].upper() + by_method[1:]
            
            if action_type == 'sendKeys' or 'enter' in prompt.lower() or 'type' in prompt.lower():
                value = self._extract_input_value(prompt)
                return f"""// {prompt}
await driver.findElement(By.{by_method_js}("{locator_value}")).clear();
await driver.findElement(By.{by_method_js}("{locator_value}")).sendKeys("{value}");"""
            else:  # click
                return f"""// {prompt}
await driver.findElement(By.{by_method_js}("{locator_value}")).click();"""
        
        # Default Python
        return f"# {prompt}\ndriver.find_element(By.ID, \"{locator_value}\").click()"
    
    # ===== PHASE 3 REFACTORING: Dead code removed (_format_click_code) =====
    # The _format_click_code method was not being called anywhere and has been removed.
    # All click code generation now uses template_engine.generate_code() below.
    
    def _generate_comprehensive_click(self, element_comment: str, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive click code with wait and error handling.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use template engine to generate code from JSON templates
        # Template engine handles by_method and by_constant formatting automatically
        return self.template_engine.generate_code(
            action='click',
            mode='comprehensive',
            language=language,
            element_desc=element_comment,
            locator=locator_value,
            locator_method=locator_method,  # Used for both by_method and by_constant
            by_method=locator_method,        # Will be formatted per language
            by_constant='placeholder'        # Triggers formatting in template_engine
        )
    
    def _generate_comprehensive_input(self, field_name: str, element_id: str, value: str, 
                                      by_locator: str, locator_value: str, language: str) -> str:
        """Generate comprehensive input code with wait and clear.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use provided locator or fallback to element_id
        if by_locator and locator_value:
            locator_method = by_locator
            locator = locator_value
        else:
            locator_method = 'id'
            locator = element_id
        
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='input',
            mode='comprehensive',
            language=language,
            field_name=field_name,
            locator=locator,
            value=value,
            locator_method=locator_method,
            by_method=locator_method,
            by_constant='placeholder'  # Triggers formatting
        )
    
    def _generate_comprehensive_select(self, element_id: str, option_text: str, language: str) -> str:
        """Generate comprehensive select dropdown code with wait.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='select',
            mode='comprehensive',
            language=language,
            locator=element_id,
            option=option_text,
            locator_method='id',
            by_method='id',
            by_constant='placeholder'  # Triggers formatting
        )
    
    def _generate_comprehensive_verify_title(self, expected_title: str, language: str) -> str:
        """Generate comprehensive title verification with wait."""
        return self.template_engine.generate_code(
            action='verify_title',
            mode='comprehensive',
            language=language,
            expected_title=expected_title
        )
    
    def _generate_comprehensive_verify_message(self, element_id: str, expected_text: str, language: str) -> str:
        """Generate comprehensive message verification with wait."""
        by_method = 'id' if language != 'python' else 'id'
        by_constant = 'ID' if language == 'python' else 'id'
        return self.template_engine.generate_code(
            action='verify_message',
            mode='comprehensive',
            language=language,
            locator=element_id,
            by_method=by_method,
            by_constant=by_constant,
            expected_text=expected_text
        )
    
    def _generate_comprehensive_verify_text(self, element_id: str, expected_text: str, language: str) -> str:
        """Generate comprehensive text verification with wait."""
        by_method = 'id' if language != 'python' else 'id'
        by_constant = 'ID' if language == 'python' else 'id'
        return self.template_engine.generate_code(
            action='verify_text',
            mode='comprehensive',
            language=language,
            locator=element_id,
            by_method=by_method,
            by_constant=by_constant,
            expected_text=expected_text
        )
    
    def _generate_comprehensive_verify_element(self, element_id: str, language: str, xpath: str = None) -> str:
        """Generate comprehensive element verification with wait.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use xpath if provided, otherwise use ID
        if xpath:
            locator_method = 'xpath'
            locator_value = xpath
            by_method = 'xpath'
            by_constant = 'XPATH'
        else:
            locator_method = 'id'
            locator_value = element_id
            by_method = 'id'
            by_constant = 'ID'
        
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='verify',
            mode='comprehensive',
            language=language,
            element_desc=element_id,
            locator=locator_value,
            by_method=by_method,
            by_constant=by_constant
        )
    
    def _generate_comprehensive_file_upload(self, file_path: str, locator_method: str, locator_value: str, language: str) -> str:
        """Generate comprehensive file upload with wait.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Format by_method and by_constant based on locator_method
        by_method = locator_method
        by_constant = 'XPATH' if locator_method == 'xpath' else 'ID'
        
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='file_upload',
            mode='comprehensive',
            language=language,
            file_path=file_path,
            locator=locator_value,
            by_method=by_method,
            by_constant=by_constant
        )
    
    def _generate_comprehensive_scroll(self, element_ref: str, language: str) -> str:
        """Generate comprehensive scroll to element.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='scroll',
            mode='comprehensive',
            language=language,
            element_ref=element_ref
        )
    
    def _generate_comprehensive_navigate(self, url: str, language: str) -> str:
        """Generate comprehensive navigation with wait for page load.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='navigate',
            mode='comprehensive',
            language=language,
            url=url
        )
    
    def _generate_comprehensive_wait(self, element_id: str, language: str) -> str:
        """Generate comprehensive wait with multiple conditions.
        
        NOW USES TEMPLATE ENGINE - No hardcoded templates!
        """
        # Use template engine to generate code from JSON templates
        return self.template_engine.generate_code(
            action='wait',
            mode='comprehensive',
            language=language,
            locator=element_id,
            by_method='id',
            by_constant='ID'
        )
    
    def _format_close_dialog_code(self, language: str) -> str:
        """Generate comprehensive code for closing dialogs/modals with multiple strategies."""
        if language == 'python':
            return '''# Close dialog/modal with multiple strategies
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
dialog_closed = False

# Strategy 1: Try close button with common IDs
if not dialog_closed:
    try:
        close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'close') or contains(@class, 'close')]")))
        close_btn.click()
        dialog_closed = True
    except:
        pass

# Strategy 2: Try close icon (X button)
if not dialog_closed:
    try:
        close_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close' or @title='Close']")))
        close_icon.click()
        dialog_closed = True
    except:
        pass

# Strategy 3: Try dismiss/cancel button
if not dialog_closed:
    try:
        dismiss_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Cancel') or contains(text(), 'Close') or contains(text(), 'Dismiss')]")))
        dismiss_btn.click()
        dialog_closed = True
    except:
        pass

# Strategy 4: Try clicking overlay background
if not dialog_closed:
    try:
        overlay = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'modal-backdrop') or contains(@class, 'overlay')]")))
        overlay.click()
        dialog_closed = True
    except:
        pass

# Strategy 5: Press ESC key as fallback
if not dialog_closed:
    from selenium.webdriver.common.keys import Keys
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)'''
        
        elif language == 'java':
            return '''// Close dialog/modal with multiple strategies
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
boolean dialogClosed = false;

// Strategy 1: Try close button with common IDs
if (!dialogClosed) {
    try {
        WebElement closeBtn = wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//button[contains(@id, 'close') or contains(@class, 'close')]")));
        closeBtn.click();
        dialogClosed = true;
    } catch (Exception e) {}
}

// Strategy 2: Try close icon (X button)
if (!dialogClosed) {
    try {
        WebElement closeIcon = wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//button[@aria-label='Close' or @title='Close']")));
        closeIcon.click();
        dialogClosed = true;
    } catch (Exception e) {}
}

// Strategy 3: Try dismiss/cancel button
if (!dialogClosed) {
    try {
        WebElement dismissBtn = wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//button[contains(text(), 'Cancel') or contains(text(), 'Close') or contains(text(), 'Dismiss')]")));
        dismissBtn.click();
        dialogClosed = true;
    } catch (Exception e) {}
}

// Strategy 4: Try clicking overlay background
if (!dialogClosed) {
    try {
        WebElement overlay = wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//*[contains(@class, 'modal-backdrop') or contains(@class, 'overlay')]")));
        overlay.click();
        dialogClosed = true;
    } catch (Exception e) {}
}

// Strategy 5: Press ESC key as fallback
if (!dialogClosed) {
    driver.findElement(By.tagName("body")).sendKeys(Keys.ESCAPE);
}'''
        
        elif language == 'javascript':
            return '''// Close dialog/modal with multiple strategies
let wait = driver.wait;
let dialogClosed = false;

// Strategy 1: Try close button with common IDs
if (!dialogClosed) {
    try {
        let closeBtn = await wait(until.elementLocated(By.xpath("//button[contains(@id, 'close') or contains(@class, 'close')]")), 10000);
        await closeBtn.click();
        dialogClosed = true;
    } catch (e) {}
}

// Strategy 2: Try close icon (X button)
if (!dialogClosed) {
    try {
        let closeIcon = await wait(until.elementLocated(By.xpath("//button[@aria-label='Close' or @title='Close']")), 10000);
        await closeIcon.click();
        dialogClosed = true;
    } catch (e) {}
}

// Strategy 3: Try dismiss/cancel button
if (!dialogClosed) {
    try {
        let dismissBtn = await wait(until.elementLocated(By.xpath("//button[contains(text(), 'Cancel') or contains(text(), 'Close') or contains(text(), 'Dismiss')]")), 10000);
        await dismissBtn.click();
        dialogClosed = true;
    } catch (e) {}
}

// Strategy 4: Press ESC key as fallback
if (!dialogClosed) {
    await driver.findElement(By.css('body')).sendKeys(Key.ESCAPE);
}'''
        
        else:  # C#
            return '''// Close dialog/modal with multiple strategies
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
bool dialogClosed = false;

// Strategy 1: Try close button with common IDs
if (!dialogClosed) {
    try {
        IWebElement closeBtn = wait.Until(ExpectedConditions.ElementToBeClickable(
            By.XPath("//button[contains(@id, 'close') or contains(@class, 'close')]")));
        closeBtn.Click();
        dialogClosed = true;
    } catch { }
}

// Strategy 2: Try close icon (X button)
if (!dialogClosed) {
    try {
        IWebElement closeIcon = wait.Until(ExpectedConditions.ElementToBeClickable(
            By.XPath("//button[@aria-label='Close' or @title='Close']")));
        closeIcon.Click();
        dialogClosed = true;
    } catch { }
}

// Strategy 3: Try dismiss/cancel button
if (!dialogClosed) {
    try {
        IWebElement dismissBtn = wait.Until(ExpectedConditions.ElementToBeClickable(
            By.XPath("//button[contains(text(), 'Cancel') or contains(text(), 'Close') or contains(text(), 'Dismiss')]")));
        dismissBtn.Click();
        dialogClosed = true;
    } catch { }
}

// Strategy 4: Press ESC key as fallback
if (!dialogClosed) {
    driver.FindElement(By.TagName("body")).SendKeys(Keys.Escape);
}'''
    
    def _format_alert_action_code(self, action: str, language: str) -> str:
        """Generate code for handling JavaScript alerts."""
        if language == 'python':
            if action == 'accept':
                return '''# Accept JavaScript alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
alert = wait.until(EC.alert_is_present())
alert.accept()'''
            else:  # dismiss
                return '''# Dismiss JavaScript alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
alert = wait.until(EC.alert_is_present())
alert.dismiss()'''
        
        elif language == 'java':
            if action == 'accept':
                return '''// Accept JavaScript alert
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
Alert alert = wait.until(ExpectedConditions.alertIsPresent());
alert.accept();'''
            else:  # dismiss
                return '''// Dismiss JavaScript alert
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
Alert alert = wait.until(ExpectedConditions.alertIsPresent());
alert.dismiss();'''
        
        elif language == 'javascript':
            if action == 'accept':
                return '''// Accept JavaScript alert
await driver.wait(until.alertIsPresent(), 10000);
let alert = await driver.switchTo().alert();
await alert.accept();'''
            else:  # dismiss
                return '''// Dismiss JavaScript alert
await driver.wait(until.alertIsPresent(), 10000);
let alert = await driver.switchTo().alert();
await alert.dismiss();'''
        
        else:  # C#
            if action == 'accept':
                return '''// Accept JavaScript alert
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IAlert alert = wait.Until(ExpectedConditions.AlertIsPresent());
alert.Accept();'''
            else:  # dismiss
                return '''// Dismiss JavaScript alert
WebDriverWait wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
IAlert alert = wait.Until(ExpectedConditions.AlertIsPresent());
alert.Dismiss();'''
    
    def _extract_input_value(self, prompt: str) -> str:
        """Extract the actual value to be entered from the prompt.
        
        REFACTORED (Phase 3): Now delegates to ParameterExtractor for optimized extraction.
        """
        # Use unified parameter extractor (single-pass extraction)
        params = self.param_extractor_unified.extract_all(prompt)
        return params['value']
    
    def _extract_locator(self, prompt: str) -> tuple:
        """Extract By locator type and value from prompt.
        
        REFACTORED: Now delegates to locator_utils module.
        """
        return self.locator_utils.extract_locator(prompt)
    
    def suggest_locator_from_html(self, html: str) -> dict:
        """Suggest locator based on HTML element.
        
        REFACTORED: Now delegates to locator_utils module.
        """
        return self.locator_utils.suggest_locator_from_html(html)
    
    def suggest_action(self, element_type: str, context: str = "", language: str = "java") -> dict:
        """
        Enhanced action suggestion using ActionSuggestionEngine.
        Provides comprehensive, context-aware suggestions with confidence scoring.
        
        Args:
            element_type: Type of HTML element (button, input, etc.)
            context: Context information (element text, id, purpose, etc.)
            language: Target language for code generation (java, python, javascript)
        
        Returns:
            dict: Enhanced suggestions with confidence, test scenarios, and code samples
        """
        # Use enhanced action suggestion engine
        result = self.action_engine.suggest_action(element_type, context, language)
        
        # Add backward compatibility fields for existing API consumers
        result['ai_generated_code'] = result['code_samples'].get(language, result['code_samples'].get('java', ''))
        
        return result
    
    def _generate_from_ai_plan(self, ai_understanding: Dict, language: str, comprehensive_mode: bool, compact_mode: bool) -> Optional[str]:
        """
        Generate code from AI execution plan.
        
        Args:
            ai_understanding: AI understanding output with intent, entities, execution plan
            language: Target programming language
            comprehensive_mode: Whether to generate comprehensive code
            compact_mode: Whether to generate compact code
            
        Returns:
            Generated code or None if generation fails
        """
        try:
            intent = ai_understanding['intent']
            entities = ai_understanding['entities']
            execution_plan = ai_understanding['execution_plan']
            
            print(f"[AI-CODEGEN] Generating code for intent: {intent}")
            
            # Generate code based on intent
            if intent == 'navigate':
                url = entities.get('url')
                if not url:
                    return None
                
                if language == 'java':
                    return f'driver.get("{url}");'
                elif language == 'python':
                    return f'driver.get("{url}")'
                elif language == 'javascript':
                    return f'await driver.get("{url}");'
                elif language == 'csharp':
                    return f'driver.Navigate().GoToUrl("{url}");'
            
            elif intent == 'input_text':
                target = entities.get('target_element', 'field')
                value = entities.get('input_value', '')
                
                if language == 'java':
                    code = f'WebElement element = driver.findElement(By.id("{target}"));\n'
                    code += f'element.clear();\n'
                    code += f'element.sendKeys("{value}");'
                    return code
                elif language == 'python':
                    code = f'element = driver.find_element(By.ID, "{target}")\n'
                    code += f'element.clear()\n'
                    code += f'element.send_keys("{value}")'
                    return code
                elif language == 'javascript':
                    code = f'const element = await driver.findElement(By.id("{target}"));\n'
                    code += f'await element.clear();\n'
                    code += f'await element.sendKeys("{value}");'
                    return code
                elif language == 'csharp':
                    code = f'var element = driver.FindElement(By.Id("{target}"));\n'
                    code += f'element.Clear();\n'
                    code += f'element.SendKeys("{value}");'
                    return code
            
            elif intent == 'click':
                target = entities.get('target_element', 'button')
                
                if language == 'java':
                    code = f'WebElement element = driver.findElement(By.id("{target}"));\n'
                    if comprehensive_mode:
                        code += f'// Wait for element to be clickable\n'
                        code += f'WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));\n'
                        code += f'wait.until(ExpectedConditions.elementToBeClickable(element));\n'
                    code += f'element.click();'
                    return code
                elif language == 'python':
                    code = f'element = driver.find_element(By.ID, "{target}")\n'
                    if comprehensive_mode:
                        code += f'# Wait for element to be clickable\n'
                        code += f'wait = WebDriverWait(driver, 10)\n'
                        code += f'wait.until(EC.element_to_be_clickable(element))\n'
                    code += f'element.click()'
                    return code
                elif language == 'javascript':
                    code = f'const element = await driver.findElement(By.id("{target}"));\n'
                    if comprehensive_mode:
                        code += f'// Wait for element to be clickable\n'
                        code += f'await driver.wait(until.elementIsVisible(element), 10000);\n'
                    code += f'await element.click();'
                    return code
                elif language == 'csharp':
                    code = f'var element = driver.FindElement(By.Id("{target}"));\n'
                    if comprehensive_mode:
                        code += f'// Wait for element to be clickable\n'
                        code += f'var wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));\n'
                        code += f'wait.Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementToBeClickable(element));\n'
                    code += f'element.Click();'
                    return code
            
            elif intent == 'wait':
                wait_time = entities.get('wait_time', 5)
                
                if language == 'java':
                    return f'Thread.sleep({wait_time} * 1000);'
                elif language == 'python':
                    return f'time.sleep({wait_time})'
                elif language == 'javascript':
                    return f'await driver.sleep({wait_time} * 1000);'
                elif language == 'csharp':
                    return f'Thread.Sleep({wait_time} * 1000);'
            
            elif intent == 'get_text':
                target = entities.get('target_element', 'element')
                
                if language == 'java':
                    code = f'WebElement element = driver.findElement(By.id("{target}"));\n'
                    code += f'String text = element.getText();'
                    return code
                elif language == 'python':
                    code = f'element = driver.find_element(By.ID, "{target}")\n'
                    code += f'text = element.text'
                    return code
                elif language == 'javascript':
                    code = f'const element = await driver.findElement(By.id("{target}"));\n'
                    code += f'const text = await element.getText();'
                    return code
                elif language == 'csharp':
                    code = f'var element = driver.FindElement(By.Id("{target}"));\n'
                    code += f'var text = element.Text;'
                    return code
            
            return None
            
        except Exception as e:
            print(f"[AI-CODEGEN] Error generating code: {e}")
            return None
    
    def suggest_locator(self, element_type: str, action: str, attributes: dict) -> list:
        """
        Suggest optimal locators for an element based on its attributes.
        Used by the recorder to generate intelligent locator suggestions.
        
        REFACTORED: Now delegates to locator_utils module.
        
        Args:
            element_type: HTML tag name (e.g., 'button', 'input')
            action: Action being performed (e.g., 'click', 'input')
            attributes: Dictionary of element attributes (id, name, className, etc.)
        
        Returns:
            List of suggested locators in priority order
        """
        return self.locator_utils.suggest_locator(element_type, action, attributes)
    
    def generate_test_method(self, description: str) -> str:
        """Generate a complete test method structure."""
        
        method_name = description.lower().replace(' ', '_')
        
        template = f"""@Test
public void test_{method_name}() {{
    // {description}
    WebDriver driver = new ChromeDriver();
    
    // Generated steps:
    {self.generate_clean(description, max_tokens=40, temperature=0.4)}
    
    driver.quit();
}}"""
        
        return template

def main():
    """Demo the improved generator."""
    
    print("\n" + "="*70)
    print("🎯 IMPROVED SELENIUM CODE GENERATOR")
    print("="*70 + "\n")
    
    generator = ImprovedSeleniumGenerator()
    
    # Test 1: Clean generation
    print("\n" + "-"*70)
    print("Test 1: Generate Click Action")
    print("-"*70)
    result = generator.generate_clean("click login button", max_tokens=20, temperature=0.3)
    print(f"Generated: {result}\n")
    
    # Test 2: Locator suggestion
    print("-"*70)
    print("Test 2: Suggest Locator from HTML")
    print("-"*70)
    html = '<button id="submit-btn" class="btn btn-primary">Submit</button>'
    locator_result = generator.suggest_locator_from_html(html)
    print(f"Recommended Locators: {locator_result['recommended_locators']}")
    print(f"AI Suggestion: {locator_result['ai_suggestion']}\n")
    
    # Test 3: Action suggestion
    print("-"*70)
    print("Test 3: Suggest Action for Element")
    print("-"*70)
    action_result = generator.suggest_action("input", "login form")
    print(f"Element Type: {action_result['element_type']}")
    print(f"Recommended: {action_result['recommended_actions']}")
    print(f"AI Code: {action_result['ai_generated_code']}\n")
    
    # Test 4: Test method generation
    print("-"*70)
    print("Test 4: Generate Test Method")
    print("-"*70)
    test_method = generator.generate_test_method("verify login functionality")
    print(test_method)
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
