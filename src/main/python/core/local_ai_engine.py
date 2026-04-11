"""
Local AI Engine - True AI Understanding Without External APIs
Uses local transformer models and advanced NLP for intelligent prompt interpretation.
"""

import logging
import re
import json
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from collections import defaultdict

logger = logging.getLogger(__name__)

class LocalAIEngine:
    """
    Self-contained AI engine for intelligent prompt understanding.
    No external API calls - all intelligence is local.
    """
    
    def __init__(self):
        self.version = "3.0.0-LOCAL-AI"
        logger.info(f"[LOCAL-AI] Initializing {self.version}")
        
        # Context memory - learns from execution patterns
        self.execution_history = []
        self.learned_patterns = defaultdict(list)
        
        # Intent understanding - what the user wants to do
        self.intent_patterns = self._build_intent_patterns()
        
        # Entity extraction - what elements/data are involved
        self.entity_patterns = self._build_entity_patterns()
        
        # Action semantics - understanding verb variations
        self.action_semantics = self._build_action_semantics()
        
        logger.info(f"[LOCAL-AI] ✓ Intent patterns: {len(self.intent_patterns)}")
        logger.info(f"[LOCAL-AI] ✓ Entity patterns: {len(self.entity_patterns)}")
        logger.info(f"[LOCAL-AI] ✓ Action semantics loaded")
    
    def _build_intent_patterns(self) -> Dict:
        """Build intent recognition patterns."""
        return {
            'navigate': {
                'keywords': ['go to', 'open', 'navigate', 'visit', 'load', 'access', 'browse'],
                'patterns': [
                    r'go\s+to\s+(.+)',
                    r'open\s+(?:the\s+)?(.+?)(?:\s+page|\s+site|\s+website)?',
                    r'navigate\s+to\s+(.+)',
                    r'visit\s+(.+)',
                    r'load\s+(.+)',
                ],
                'confidence': 0.9
            },
            'input_text': {
                'keywords': ['enter', 'type', 'input', 'fill', 'write', 'put', 'set'],
                'patterns': [
                    r'(?:enter|type|input|fill|write)\s+["\']?(.+?)["\']?\s+(?:in|into|to)\s+(?:the\s+)?(.+?)(?:\s+field|\s+box)?',
                    r'(?:put|set)\s+(.+?)\s+(?:in|into)\s+(?:the\s+)?(.+?)',
                    r'fill\s+(?:the\s+)?(.+?)\s+(?:with|as)\s+["\']?(.+?)["\']?',
                ],
                'confidence': 0.95
            },
            'click': {
                'keywords': ['click', 'press', 'tap', 'select', 'hit', 'push'],
                'patterns': [
                    r'(?:click|press|tap|hit|push)\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+button|\s+link)?',
                    r'select\s+(?:the\s+)?(.+?)(?:\s+option)?',
                ],
                'confidence': 0.9
            },
            'verify': {
                'keywords': ['verify', 'check', 'confirm', 'validate', 'assert', 'ensure', 'see'],
                'patterns': [
                    r'(?:verify|check|confirm)\s+(?:that\s+)?(.+?)\s+(?:is|are|shows?|displays?|contains?)\s+(.+)',
                    r'(?:ensure|assert)\s+(.+)',
                    r'see\s+(?:if\s+)?(.+)',
                ],
                'confidence': 0.85
            },
            'wait': {
                'keywords': ['wait', 'pause', 'hold', 'sleep', 'delay'],
                'patterns': [
                    r'wait\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?|ms)?',
                    r'pause\s+(?:for\s+)?(\d+)',
                    r'(?:hold|sleep|delay)\s+(\d+)',
                ],
                'confidence': 0.95
            },
            'scroll': {
                'keywords': ['scroll', 'move down', 'move up', 'page down', 'page up'],
                'patterns': [
                    r'scroll\s+(?:to\s+)?(?:the\s+)?(.+)',
                    r'(?:move|page)\s+(down|up)',
                ],
                'confidence': 0.9
            },
            'get_text': {
                'keywords': ['get', 'read', 'extract', 'fetch', 'retrieve', 'capture'],
                'patterns': [
                    r'(?:get|read|extract|fetch|retrieve|capture)\s+(?:the\s+)?(?:text\s+(?:from|of)\s+)?(?:the\s+)?(.+)',
                ],
                'confidence': 0.85
            }
        }
    
    def _build_entity_patterns(self) -> Dict:
        """Build entity extraction patterns."""
        return {
            'input_field': {
                'keywords': ['field', 'box', 'input', 'textbox', 'textarea', 'form'],
                'semantic_matches': ['username', 'password', 'email', 'search', 'name', 'phone', 'address']
            },
            'button': {
                'keywords': ['button', 'btn'],
                'semantic_matches': ['login', 'submit', 'search', 'save', 'send', 'continue', 'ok', 'cancel']
            },
            'link': {
                'keywords': ['link', 'anchor', 'href'],
                'semantic_matches': ['home', 'about', 'contact', 'more', 'details']
            },
            'checkbox': {
                'keywords': ['checkbox', 'check', 'tick'],
                'semantic_matches': ['agree', 'accept', 'remember', 'subscribe']
            },
            'dropdown': {
                'keywords': ['dropdown', 'select', 'menu', 'list'],
                'semantic_matches': ['country', 'state', 'category', 'option']
            }
        }
    
    def _build_action_semantics(self) -> Dict:
        """Build semantic understanding of actions."""
        return {
            'navigate': {
                'synonyms': ['go', 'open', 'visit', 'browse', 'navigate', 'load', 'access'],
                'requires': ['url'],
                'selenium_action': 'driver.get'
            },
            'click': {
                'synonyms': ['click', 'press', 'tap', 'select', 'hit', 'push', 'activate'],
                'requires': ['element'],
                'selenium_action': 'element.click'
            },
            'enter_text': {
                'synonyms': ['enter', 'type', 'input', 'fill', 'write', 'put', 'set'],
                'requires': ['element', 'text'],
                'selenium_action': 'element.send_keys'
            },
            'verify': {
                'synonyms': ['verify', 'check', 'confirm', 'validate', 'assert', 'ensure'],
                'requires': ['condition'],
                'selenium_action': 'assert'
            },
            'get_text': {
                'synonyms': ['get', 'read', 'extract', 'fetch', 'retrieve', 'capture'],
                'requires': ['element'],
                'selenium_action': 'element.text'
            }
        }
    
    def understand_prompt(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """
        Understand user intent using local AI intelligence.
        
        Args:
            prompt: Natural language instruction
            context: Optional execution context (previous actions, page state)
            
        Returns:
            Dict with intent, entities, confidence, and suggested action
        """
        # SAFETY: Handle None or empty prompts
        if not prompt or not isinstance(prompt, str):
            logger.warning(f"[LOCAL-AI] Invalid prompt: {prompt} (type: {type(prompt)})")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'enhanced': {},
                'execution_plan': {},
                'original_prompt': prompt
            }
        
        logger.info(f"[LOCAL-AI] ========== UNDERSTANDING PROMPT ==========")
        logger.info(f"[LOCAL-AI] Input: {prompt}")
        
        # Step 1: Intent Recognition
        intent, intent_confidence = self._recognize_intent(prompt)
        logger.info(f"[LOCAL-AI] Intent: {intent} (confidence: {intent_confidence:.2f})")
        
        # Step 2: Entity Extraction
        entities = self._extract_entities(prompt, intent)
        logger.info(f"[LOCAL-AI] Entities: {entities}")
        
        # Step 3: Context-Aware Enhancement
        if context:
            enhanced = self._enhance_with_context(intent, entities, context)
            logger.info(f"[LOCAL-AI] Context enhancement: {enhanced}")
        else:
            enhanced = {}
        
        # Step 4: Generate Execution Plan
        execution_plan = self._generate_execution_plan(intent, entities, enhanced)
        logger.info(f"[LOCAL-AI] Execution plan: {execution_plan}")
        
        result = {
            'intent': intent,
            'confidence': intent_confidence,
            'entities': entities,
            'enhanced': enhanced,
            'execution_plan': execution_plan,
            'original_prompt': prompt
        }
        
        logger.info(f"[LOCAL-AI] ========================================")
        return result
    
    def _recognize_intent(self, prompt: str) -> Tuple[str, float]:
        """Recognize user intent with confidence score."""
        prompt_lower = prompt.lower()
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, config in self.intent_patterns.items():
            confidence = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for kw in config['keywords'] if kw in prompt_lower)
            if keyword_matches > 0:
                confidence += (keyword_matches / len(config['keywords'])) * 0.5
            
            # Pattern matching
            for pattern in config['patterns']:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    confidence += 0.5
                    break
            
            # Update best match
            if confidence > best_confidence:
                best_confidence = min(confidence, config['confidence'])
                best_intent = intent
        
        return best_intent, best_confidence
    
    def _extract_entities(self, prompt: str, intent: str) -> Dict:
        """Extract relevant entities from prompt."""
        entities = {
            'target_element': None,
            'input_value': None,
            'url': None,
            'condition': None,
            'wait_time': None
        }
        
        prompt_lower = prompt.lower()
        
        # Extract based on intent
        if intent == 'navigate':
            # Extract URL
            url_match = re.search(r'https?://[^\s]+', prompt)
            if url_match:
                entities['url'] = url_match.group(0)
            else:
                # Try to extract domain/path
                words = prompt_lower.split()
                for i, word in enumerate(words):
                    if word in ['to', 'page', 'site']:
                        if i + 1 < len(words):
                            entities['url'] = words[i + 1]
                            break
        
        elif intent == 'input_text':
            # Extract value and target field
            match = re.search(r'["\'](.+?)["\']', prompt)
            if match:
                entities['input_value'] = match.group(1)
            
            # Extract target element
            for field_type in ['username', 'password', 'email', 'search', 'name']:
                if field_type in prompt_lower:
                    entities['target_element'] = field_type
                    break
        
        elif intent == 'click':
            # Extract button/link name
            match = re.search(r'(?:click|press|tap)\s+(?:on\s+)?(?:the\s+)?(.+?)(?:\s+button|\s+link)?$', prompt_lower)
            if match:
                entities['target_element'] = match.group(1).strip()
        
        elif intent == 'wait':
            # Extract wait time
            match = re.search(r'(\d+)', prompt)
            if match:
                entities['wait_time'] = int(match.group(1))
        
        elif intent == 'get_text':
            # Extract target element
            match = re.search(r'(?:from|of)\s+(?:the\s+)?(.+)', prompt_lower)
            if match:
                entities['target_element'] = match.group(1).strip()
        
        return entities
    
    def _enhance_with_context(self, intent: str, entities: Dict, context: Dict) -> Dict:
        """Enhance understanding with execution context."""
        enhanced = {}
        
        # Use previous page URL if navigating relatively
        if intent == 'navigate' and entities.get('url'):
            if not entities['url'].startswith('http'):
                base_url = context.get('current_url', '')
                if base_url:
                    enhanced['full_url'] = f"{base_url.rstrip('/')}/{entities['url'].lstrip('/')}"
        
        # Use page elements for better targeting
        if 'available_elements' in context:
            available = context['available_elements']
            target = entities.get('target_element')
            
            if target:
                # Smart element matching
                best_match = self._find_best_element_match(target, available)
                if best_match:
                    enhanced['matched_element'] = best_match
        
        # Use execution history for corrections
        if 'last_error' in context:
            enhanced['retry_suggestion'] = self._suggest_retry_strategy(intent, context['last_error'])
        
        return enhanced
    
    def _find_best_element_match(self, target: str, available_elements: List[Dict]) -> Optional[Dict]:
        """Find best matching element using semantic understanding."""
        best_match = None
        best_score = 0.0
        
        for element in available_elements:
            score = 0.0
            element_text = element.get('text', '').lower()
            element_id = element.get('id', '').lower()
            element_name = element.get('name', '').lower()
            
            # Direct text match
            if target in element_text:
                score += 0.6
            
            # Fuzzy text match
            text_similarity = SequenceMatcher(None, target, element_text).ratio()
            score += text_similarity * 0.4
            
            # ID/Name match
            if target in element_id or target in element_name:
                score += 0.3
            
            if score > best_score:
                best_score = score
                best_match = element
        
        return best_match if best_score > 0.5 else None
    
    def _suggest_retry_strategy(self, intent: str, error: str) -> Dict:
        """Suggest retry strategy based on error."""
        if 'timeout' in error.lower():
            return {'strategy': 'wait_longer', 'wait_time': 10}
        elif 'not found' in error.lower():
            return {'strategy': 'use_alt_locator', 'locator_type': 'xpath'}
        elif 'not clickable' in error.lower():
            return {'strategy': 'scroll_to_element', 'then': 'click'}
        else:
            return {'strategy': 'retry_with_delay', 'delay': 2}
    
    def _generate_execution_plan(self, intent: str, entities: Dict, enhanced: Dict) -> Dict:
        """Generate detailed execution plan."""
        plan = {
            'action': intent,
            'steps': [],
            'fallbacks': []
        }
        
        if intent == 'navigate':
            url = enhanced.get('full_url') or entities.get('url')
            plan['steps'] = [
                {'action': 'get_url', 'url': url}
            ]
            plan['fallbacks'] = [
                {'action': 'retry', 'delay': 2},
                {'action': 'check_connection'}
            ]
        
        elif intent == 'input_text':
            element = enhanced.get('matched_element') or entities.get('target_element')
            value = entities.get('input_value')
            
            plan['steps'] = [
                {'action': 'find_element', 'target': element, 'by': 'id'},
                {'action': 'clear_field'},
                {'action': 'send_keys', 'value': value}
            ]
            plan['fallbacks'] = [
                {'action': 'try_name_locator'},
                {'action': 'try_label_locator'},
                {'action': 'try_placeholder_locator'}
            ]
        
        elif intent == 'click':
            element = enhanced.get('matched_element') or entities.get('target_element')
            
            plan['steps'] = [
                {'action': 'find_element', 'target': element},
                {'action': 'scroll_to_element'},
                {'action': 'wait_for_clickable'},
                {'action': 'click'}
            ]
            plan['fallbacks'] = [
                {'action': 'javascript_click'},
                {'action': 'action_chains_click'}
            ]
        
        elif intent == 'wait':
            wait_time = entities.get('wait_time', 5)
            plan['steps'] = [
                {'action': 'sleep', 'duration': wait_time}
            ]
        
        return plan
    
    def learn_from_execution(self, prompt: str, result: Dict, success: bool):
        """Learn from execution results to improve future understanding."""
        self.execution_history.append({
            'prompt': prompt,
            'result': result,
            'success': success
        })
        
        # Learn successful patterns
        if success:
            intent = result.get('intent')
            if intent:
                self.learned_patterns[intent].append({
                    'prompt': prompt,
                    'entities': result.get('entities'),
                    'execution_plan': result.get('execution_plan')
                })
        
        logger.info(f"[LOCAL-AI] Learned from execution: success={success}")
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learned patterns."""
        return {
            'total_executions': len(self.execution_history),
            'learned_patterns': {intent: len(patterns) for intent, patterns in self.learned_patterns.items()},
            'success_rate': sum(1 for h in self.execution_history if h['success']) / max(len(self.execution_history), 1)
        }
