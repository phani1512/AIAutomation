"""
Natural Language Processor - Understands conversational English prompts

Handles ANY natural language input and extracts:
1. ACTION (what to do: click, type, verify, etc.)
2. TARGET (which element)
3. VALUE (what to enter, select, etc.)

Examples:
- "I want to click on the login button" → ACTION: click, TARGET: login button
- "Please type test@email.com in the username field" → ACTION: type, VALUE: test@email.com, TARGET: username field
- "Can you verify that the error message shows up?" → ACTION: verify, TARGET: error message
- "Hit the submit button" → ACTION: click, TARGET: submit button
"""

import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class NaturalLanguageProcessor:
    """
    Processes natural conversational English to extract test actions.
    """
    
    # Action verb mappings - different ways to say the same thing
    ACTION_SYNONYMS = {
        'click': ['click', 'press', 'hit', 'tap', 'select', 'choose', 'push', 'activate'],
        'type': ['type', 'enter', 'input', 'fill', 'write', 'put', 'set'],
        'verify': ['verify', 'check', 'confirm', 'assert', 'ensure', 'validate', 'see', 'look for'],
        'get': ['get', 'retrieve', 'fetch', 'read', 'extract', 'obtain'],
        'wait': ['wait', 'pause', 'hold', 'delay'],
        'select': ['select', 'choose', 'pick'],
        'clear': ['clear', 'erase', 'remove', 'delete', 'empty'],
        'hover': ['hover', 'mouse over', 'move to'],
    }
    
    # Conversational prefixes to strip
    CONVERSATIONAL_PREFIXES = [
        r'^(I want to|I need to|I would like to|Please|Can you|Could you|Would you|Try to|Go ahead and)\s+',
        r'^(Let\'s|Let us|Lets)\s+',
        r'^(Now|Next|Then|After that|Finally)\s+',
    ]
    
    # Element indicators - words that suggest element names
    ELEMENT_INDICATORS = [
        r'(?:the|a|an)\s+(\w+(?:\s+\w+)?)\s+(?:button|field|input|box|dropdown|menu|link|text|message|error|label|checkbox|radio)',
        r'(?:on|in|into|from|at)\s+(?:the|a|an)?\s*(\w+(?:\s+\w+)?)\s+(?:button|field|input|box|dropdown|menu|link)',
        r'(?:button|field|input|box|dropdown|menu|link|text|message|error|label|checkbox|radio)\s+(?:named|called|labeled|with id)?\s*["\']?(\w+)["\']?',
        r'(\w+)\s+(?:button|field|input|box|dropdown|menu|link|text|message|error|label|checkbox|radio)',
    ]
    
    def __init__(self):
        self.action_map = self._build_action_map()
    
    def _build_action_map(self) -> Dict[str, str]:
        """Build reverse map from synonym to canonical action."""
        action_map = {}
        for canonical, synonyms in self.ACTION_SYNONYMS.items():
            for synonym in synonyms:
                action_map[synonym.lower()] = canonical
        return action_map
    
    def parse(self, prompt: str) -> Dict:
        """
        Parse natural language prompt into structured action.
        
        Args:
            prompt: Natural language text (any format)
        
        Returns:
            {
                'action': 'click' | 'type' | 'verify' | etc.,
                'element': 'loginButton' | 'username' | etc.,
                'value': Optional text to enter/select,
                'raw_element': Original element phrase,
                'confidence': 'high' | 'medium' | 'low'
            }
        """
        logger.info(f"[NLP] Parsing prompt: {prompt}")
        
        # Step 1: Clean conversational prefixes
        cleaned = self._remove_conversational_prefixes(prompt)
        logger.info(f"[NLP] After cleaning: {cleaned}")
        
        # Step 2: Extract action
        action = self._extract_action(cleaned)
        logger.info(f"[NLP] Detected action: {action}")
        
        # Step 3: Extract value (for type/enter actions)
        value, remaining = self._extract_value(cleaned, action)
        logger.info(f"[NLP] Extracted value: {value}, remaining: {remaining}")
        
        # Step 4: Extract element
        element, raw_element = self._extract_element(remaining if value else cleaned)
        logger.info(f"[NLP] Extracted element: {element} (raw: {raw_element})")
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(action, element)
        
        result = {
            'action': action,
            'element': element,
            'value': value,
            'raw_element': raw_element,
            'confidence': confidence,
            'original_prompt': prompt
        }
        
        logger.info(f"[NLP] Parse result: {result}")
        return result
    
    def _remove_conversational_prefixes(self, text: str) -> str:
        """Remove conversational prefixes like 'I want to', 'Please', etc."""
        cleaned = text
        for pattern in self.CONVERSATIONAL_PREFIXES:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def _extract_action(self, text: str) -> str:
        """
        Extract the action verb from text.
        Returns canonical action type.
        """
        words = text.lower().split()
        
        # Check each word against action synonyms
        for word in words[:5]:  # Check first 5 words
            word_clean = re.sub(r'[^\w\s]', '', word)  # Remove punctuation
            if word_clean in self.action_map:
                return self.action_map[word_clean]
        
        # Default fallbacks based on patterns
        if re.search(r'\btype\b|\benter\b|\binput\b|\bfill\b|\bwrite\b', text, re.IGNORECASE):
            return 'type'
        elif re.search(r'\bclick\b|\bpress\b|\bhit\b|\btap\b', text, re.IGNORECASE):
            return 'click'
        elif re.search(r'\bverify\b|\bcheck\b|\bconfirm\b|\bsee\b|\blook\b', text, re.IGNORECASE):
            return 'verify'
        elif re.search(r'\bget\b|\bretrieve\b|\bread\b', text, re.IGNORECASE):
            return 'get'
        elif re.search(r'\bselect\b|\bchoose\b|\bpick\b', text, re.IGNORECASE):
            return 'select'
        elif re.search(r'\bwait\b', text, re.IGNORECASE):
            return 'wait'
        elif re.search(r'\bhover\b', text, re.IGNORECASE):
            return 'hover'
        
        # Default to click if unclear
        return 'click'
    
    def _extract_value(self, text: str, action: str) -> Tuple[Optional[str], str]:
        """
        Extract value to enter/type (for input actions).
        Returns: (value, remaining_text)
        """
        if action not in ['type', 'enter', 'input', 'fill']:
            return None, text
        
        # Pattern 1: Quoted values "value" or 'value'
        quoted_match = re.search(r'["\']([^"\']+)["\']', text)
        if quoted_match:
            value = quoted_match.group(1)
            remaining = text.replace(quoted_match.group(0), '', 1)
            return value, remaining
        
        # Pattern 2: "type VALUE in/into FIELD"
        type_in_match = re.search(r'(?:type|enter|input|fill|write|put)\s+([^\s]+)\s+(?:in|into|to)\s+', text, re.IGNORECASE)
        if type_in_match:
            value = type_in_match.group(1)
            remaining = text.replace(type_in_match.group(1), '', 1)
            return value, remaining
        
        # Pattern 3: "enter my email" -> extract "my email"
        possession_match = re.search(r'(?:type|enter|input|fill|write|put)\s+(my|the|your)\s+(\w+)', text, re.IGNORECASE)
        if possession_match:
            value = f"{possession_match.group(1)} {possession_match.group(2)}"
            remaining = text
            return value, remaining
        
        return None, text
    
    def _extract_element(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract element name from natural language.
        Returns: (normalized_element_name, raw_phrase)
        
        Examples:
        - "the login button" → ("loginButton", "login button")
        - "username field" → ("username", "username field")
        - "submit" → ("submit", "submit")
        """
        # Try each element indicator pattern
        for pattern in self.ELEMENT_INDICATORS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw_element = match.group(1).strip()
                normalized = self._normalize_element_name(raw_element)
                return normalized, raw_element
        
        # Fallback: Extract last significant word
        words = re.findall(r'\b[a-zA-Z]\w+\b', text)
        if words:
            # Skip common words
            skip_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'from', 'with', 'for', 'of', 'is', 'are', 'that', 'this', 'it'}
            significant_words = [w for w in words if w.lower() not in skip_words]
            if significant_words:
                raw = significant_words[-1]
                return raw, raw
        
        return None, None
    
    def _normalize_element_name(self, raw: str) -> str:
        """
        Convert natural element name to camelCase identifier.
        
        Examples:
        - "login button" → "loginButton"
        - "username field" → "usernameField"
        - "error message" → "errorMessage"
        """
        # Remove common suffixes
        raw = re.sub(r'\s+(button|field|input|box|dropdown|menu|link|text|message|error|label)$', '', raw, flags=re.IGNORECASE)
        
        # Convert to camelCase
        words = raw.split()
        if not words:
            return raw
        
        camel = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        return camel
    
    def _calculate_confidence(self, action: Optional[str], element: Optional[str]) -> str:
        """Calculate confidence level of the parse."""
        if action and element:
            return 'high'
        elif action or element:
            return 'medium'
        else:
            return 'low'
    
    def format_for_element_resolver(self, parsed: Dict) -> str:
        """
        Convert parsed result to format expected by ElementResolver.
        
        Returns a standardized prompt like:
        - "click loginButton"
        - "enter value in usernameField"
        - "verify errorMessage"
        """
        action = parsed['action']
        element = parsed['element']
        value = parsed.get('value')
        
        if action == 'type' and value:
            return f"enter {value} in {element}"
        elif action in ['click', 'verify', 'get', 'wait', 'hover']:
            return f"{action} {element}"
        elif action == 'select':
            return f"select {value or 'option'} from {element}"
        else:
            return f"{action} {element}"


def test_nlp():
    """Test the NLP processor with various natural language inputs."""
    nlp = NaturalLanguageProcessor()
    
    test_cases = [
        "I want to click on the login button",
        "Please type test@email.com in the username field",
        "Can you verify that the error message shows up?",
        "Hit the submit button",
        "Enter my password in the password box",
        "Check if the welcome text is displayed",
        "Select California from the state dropdown",
        "Wait for the loading spinner",
        "Click loginButton",  # Already formatted
        "type admin into username",
        "verify errorMsg is displayed",
        "I need to fill in the email address field with john@example.com",
        "Please press the Sign In button",
    ]
    
    print("=" * 80)
    print("Natural Language Processor Test Results")
    print("=" * 80)
    
    for i, test_prompt in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Input: {test_prompt}")
        result = nlp.parse(test_prompt)
        
        print(f"  ✓ Action: {result['action']}")
        print(f"  ✓ Element: {result['element']}")
        if result['value']:
            print(f"  ✓ Value: {result['value']}")
        print(f"  ✓ Confidence: {result['confidence']}")
        
        formatted = nlp.format_for_element_resolver(result)
        print(f"  → Formatted for resolver: {formatted}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    test_nlp()
