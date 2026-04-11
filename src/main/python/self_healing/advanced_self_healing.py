"""
Advanced Self-Healing Locator System with Element Identity & Confidence Scoring
100% Rule-Based - No AI/ML Dependencies

This module provides enhanced self-healing capabilities:
- Element identity storage (not just locators)
- Confidence scoring using fuzzy matching algorithms
- History tracking for healing events
- Visual highlighting support
- Approval workflow integration

IMPORTANT: This is v2 of self-healing. The original self_healing_locator.py (v1)
remains untouched and continues to work. This module is opt-in only.
"""

import json
import os
import logging
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from difflib import SequenceMatcher
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logger = logging.getLogger(__name__)


class ElementIdentity:
    """
    Stores element identity based on multiple characteristics (not just locator).
    This is the core concept: identify elements by WHAT they are, not HOW we find them.
    """
    
    def __init__(self, element: Optional[WebElement] = None, driver: Optional[WebDriver] = None):
        """
        Initialize element identity.
        
        Args:
            element: WebElement to extract identity from (optional)
            driver: WebDriver instance for context extraction (optional)
        """
        self.primary_locator = None
        self.attributes = {}
        self.context = {}
        self.fingerprint = None
        
        if element and driver:
            self.extract_from_element(element, driver)
    
    def extract_from_element(self, element: WebElement, driver: WebDriver):
        """
        Extract identity characteristics from a WebElement.
        
        Args:
            element: WebElement to analyze
            driver: WebDriver instance for context analysis
        """
        try:
            # Extract basic attributes
            self.attributes = {
                'id': element.get_attribute('id'),
                'name': element.get_attribute('name'),
                'class': element.get_attribute('class'),
                'type': element.get_attribute('type'),
                'value': element.get_attribute('value'),
                'placeholder': element.get_attribute('placeholder'),
                'text': element.text.strip() if element.text else None,
                'tag': element.tag_name,
                'role': element.get_attribute('role'),
                'aria_label': element.get_attribute('aria-label'),
                'title': element.get_attribute('title'),
                'href': element.get_attribute('href'),
                'alt': element.get_attribute('alt')
            }
            
            # Remove None values
            self.attributes = {k: v for k, v in self.attributes.items() if v}
            
            # Extract context (DOM position)
            try:
                context_script = """
                var elem = arguments[0];
                var parent = elem.parentElement;
                var siblings = parent ? Array.from(parent.children) : [];
                var position = siblings.indexOf(elem) + 1;
                var depth = 0;
                var temp = elem;
                while (temp.parentElement) {
                    depth++;
                    temp = temp.parentElement;
                }
                
                return {
                    parent_tag: parent ? parent.tagName.toLowerCase() : null,
                    parent_class: parent ? parent.className : null,
                    siblings_count: siblings.length,
                    position: position,
                    depth: depth,
                    is_visible: elem.offsetParent !== null
                };
                """
                self.context = driver.execute_script(context_script, element)
            except Exception as e:
                logger.debug(f"[IDENTITY] Could not extract context: {e}")
                self.context = {}
            
            # Generate fingerprint (SHA256 hash of key attributes)
            self.fingerprint = self._generate_fingerprint()
            
            logger.debug(f"[IDENTITY] Extracted: {len(self.attributes)} attributes, fingerprint: {self.fingerprint[:8]}...")
            
        except Exception as e:
            logger.error(f"[IDENTITY] Failed to extract element identity: {e}")
    
    def _generate_fingerprint(self) -> str:
        """
        Generate unique fingerprint for element based on attributes.
        Uses SHA256 hash of stable attributes.
        
        Returns:
            SHA256 hash string
        """
        # Use stable attributes that are less likely to change
        stable_attrs = [
            self.attributes.get('id', ''),
            self.attributes.get('name', ''),
            self.attributes.get('text', ''),
            self.attributes.get('aria_label', ''),
            self.attributes.get('role', ''),
            self.attributes.get('tag', ''),
            str(self.context.get('parent_tag', ''))
        ]
        
        fingerprint_string = '|'.join(stable_attrs)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to dictionary for storage."""
        return {
            'primary_locator': self.primary_locator,
            'attributes': self.attributes,
            'context': self.context,
            'fingerprint': self.fingerprint
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElementIdentity':
        """Create ElementIdentity from dictionary."""
        identity = cls()
        identity.primary_locator = data.get('primary_locator')
        identity.attributes = data.get('attributes', {})
        identity.context = data.get('context', {})
        identity.fingerprint = data.get('fingerprint')
        return identity


class ConfidenceCalculator:
    """
    Calculate confidence scores for element matches using fuzzy matching algorithms.
    100% algorithmic - no AI/ML required.
    """
    
    def __init__(self):
        """Initialize confidence calculator with configurable weights."""
        # Weights for different matching criteria (sum = 1.0)
        self.weights = {
            'id_match': 0.30,           # ID matches are strongest signal
            'name_match': 0.20,         # Name attribute matches
            'text_match': 0.20,         # Button/link text matches
            'class_similarity': 0.10,   # CSS classes similarity
            'context_match': 0.10,      # Parent/sibling structure matches
            'attributes_match': 0.10    # Other attributes match
        }
    
    def calculate_match_confidence(self, element: WebElement, identity: ElementIdentity) -> float:
        """
        Calculate how confident we are that this element matches the identity.
        
        Args:
            element: WebElement to check
            identity: ElementIdentity to match against
            
        Returns:
            Confidence score from 0.0 to 1.0 (0% to 100%)
        """
        score = 0.0
        
        try:
            # 1. ID match (strongest signal)
            element_id = element.get_attribute('id')
            if element_id and element_id == identity.attributes.get('id'):
                score += self.weights['id_match']
                logger.debug(f"[CONFIDENCE] ID match: +{self.weights['id_match']}")
            
            # 2. Name attribute match
            element_name = element.get_attribute('name')
            if element_name and element_name == identity.attributes.get('name'):
                score += self.weights['name_match']
                logger.debug(f"[CONFIDENCE] Name match: +{self.weights['name_match']}")
            
            # 3. Text content match (fuzzy)
            element_text = element.text.strip() if element.text else ''
            identity_text = identity.attributes.get('text', '')
            if element_text and identity_text:
                text_similarity = self._fuzzy_match(element_text, identity_text)
                text_score = self.weights['text_match'] * text_similarity
                score += text_score
                logger.debug(f"[CONFIDENCE] Text similarity: {text_similarity:.2f} -> +{text_score:.3f}")
            
            # 4. CSS class similarity (fuzzy)
            element_class = element.get_attribute('class') or ''
            identity_class = identity.attributes.get('class', '')
            if element_class or identity_class:
                class_similarity = self._fuzzy_match(element_class, identity_class)
                if class_similarity > 0.7:  # Only count if reasonably similar
                    class_score = self.weights['class_similarity'] * class_similarity
                    score += class_score
                    logger.debug(f"[CONFIDENCE] Class similarity: {class_similarity:.2f} -> +{class_score:.3f}")
            
            # 5. Context match (parent tag, position)
            context_score = self._calculate_context_match(element, identity)
            score += context_score
            
            # 6. Other attributes match
            attr_score = self._calculate_attributes_match(element, identity)
            score += attr_score
            
            # Cap at 1.0
            final_score = min(score, 1.0)
            logger.info(f"[CONFIDENCE] Final score: {final_score:.2f} ({final_score * 100:.0f}%)")
            
            return final_score
            
        except Exception as e:
            logger.error(f"[CONFIDENCE] Error calculating confidence: {e}")
            return 0.0
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """
        Calculate fuzzy string similarity using SequenceMatcher.
        Pure algorithmic - no AI needed.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio from 0.0 to 1.0
        """
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0
        
        # Use difflib.SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _calculate_context_match(self, element: WebElement, identity: ElementIdentity) -> float:
        """
        Calculate context similarity (DOM position, parent, etc.).
        
        Args:
            element: WebElement to check
            identity: ElementIdentity to match against
            
        Returns:
            Score contribution from context matching
        """
        try:
            # Get parent tag
            parent = element.find_element(By.XPATH, '..')
            parent_tag = parent.tag_name.lower() if parent else None
            
            identity_parent = identity.context.get('parent_tag', '').lower()
            
            if parent_tag and identity_parent and parent_tag == identity_parent:
                logger.debug(f"[CONFIDENCE] Context match (parent): +{self.weights['context_match']}")
                return self.weights['context_match']
            
        except Exception as e:
            logger.debug(f"[CONFIDENCE] Context match failed: {e}")
        
        return 0.0
    
    def _calculate_attributes_match(self, element: WebElement, identity: ElementIdentity) -> float:
        """
        Calculate similarity of other attributes (type, role, aria-label, etc.).
        
        Args:
            element: WebElement to check
            identity: ElementIdentity to match against
            
        Returns:
            Score contribution from attribute matching
        """
        matched_attrs = 0
        total_attrs = 0
        
        # Check various attributes
        attr_names = ['type', 'role', 'aria_label', 'placeholder', 'title', 'alt']
        
        for attr in attr_names:
            identity_value = identity.attributes.get(attr)
            if identity_value:  # Only check if identity has this attribute
                total_attrs += 1
                element_value = element.get_attribute(attr.replace('_', '-'))
                if element_value == identity_value:
                    matched_attrs += 1
        
        if total_attrs > 0:
            match_ratio = matched_attrs / total_attrs
            score = self.weights['attributes_match'] * match_ratio
            logger.debug(f"[CONFIDENCE] Attributes match: {matched_attrs}/{total_attrs} -> +{score:.3f}")
            return score
        
        return 0.0
    
    def get_confidence_level(self, score: float) -> str:
        """
        Convert confidence score to human-readable level.
        
        Args:
            score: Confidence score (0.0 to 1.0)
            
        Returns:
            Confidence level string
        """
        if score >= 0.9:
            return "Very High"
        elif score >= 0.75:
            return "High"
        elif score >= 0.5:
            return "Medium"
        elif score >= 0.3:
            return "Low"
        else:
            return "Very Low"


class HealingStrategy:
    """Represents a healing strategy with priority."""
    
    def __init__(self, strategy_type: str, locator: str, priority: int):
        self.type = strategy_type
        self.locator = locator
        self.priority = priority
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'locator': self.locator,
            'priority': self.priority
        }


class AdvancedSelfHealingLocator:
    """
    Advanced self-healing locator with element identity and confidence scoring.
    
    This is v2 of the self-healing system. The original SelfHealingLocator (v1)
    remains untouched and continues to work. This class provides additional
    features but requires opt-in activation.
    """
    
    def __init__(self):
        """Initialize advanced self-healing locator."""
        self.confidence_calculator = ConfidenceCalculator()
        self.healing_history = []  # Will be integrated with database later
        
        # Confidence threshold for auto-approval
        self.auto_approve_threshold = 0.80  # 80% confidence or higher
        self.minimum_threshold = 0.50       # 50% minimum to consider match
        
        logger.info("[ADVANCED-HEAL] Initialized (v2)")
    
    def find_element_with_healing(
        self, 
        driver: WebDriver, 
        step_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find element with advanced healing and confidence scoring.
        
        Args:
            driver: Selenium WebDriver instance
            step_data: Step data containing either:
                       - 'locator' (old format - backward compatible)
                       - 'element_identity' (new format)
            
        Returns:
            Dictionary containing:
                - element: WebElement (if found)
                - healed: bool (whether healing was used)
                - confidence: float (0.0 to 1.0)
                - original_locator: str
                - working_locator: str
                - requires_approval: bool
                - healing_event: dict (if healed)
            
            Returns None if element cannot be found.
        """
        # Check if this is old format (backward compatible)
        if 'locator' in step_data and 'element_identity' not in step_data:
            logger.debug("[ADVANCED-HEAL] Old format detected, using legacy path")
            return self._find_with_legacy_format(driver, step_data)
        
        # New format with element identity
        if 'element_identity' not in step_data:
            logger.error("[ADVANCED-HEAL] No element_identity or locator in step data")
            return None
        
        element_identity = step_data['element_identity']
        if isinstance(element_identity, dict):
            element_identity = ElementIdentity.from_dict(element_identity)
        
        original_locator = element_identity.primary_locator
        
        # Try primary locator first
        try:
            by_type, value = self._parse_locator(original_locator)
            if by_type and value:
                element = driver.find_element(by_type, value)
                logger.info(f"[ADVANCED-HEAL] ✓ Primary locator succeeded: {original_locator}")
                
                return {
                    'element': element,
                    'healed': False,
                    'confidence': 1.0,
                    'original_locator': original_locator,
                    'working_locator': original_locator,
                    'requires_approval': False
                }
        except NoSuchElementException:
            logger.warning(f"[ADVANCED-HEAL] ✗ Primary locator failed: {original_locator}")
        
        # Generate and try healing strategies
        strategies = self._generate_healing_strategies(element_identity)
        
        for strategy in strategies:
            try:
                by_type, value = self._parse_locator(strategy.locator)
                if not by_type or not value:
                    continue
                
                element = driver.find_element(by_type, value)
                
                # Calculate confidence score
                confidence = self.confidence_calculator.calculate_match_confidence(
                    element, 
                    element_identity
                )
                
                if confidence >= self.minimum_threshold:
                    logger.info(f"[ADVANCED-HEAL] ✓ Healing succeeded with {confidence * 100:.0f}% confidence")
                    logger.info(f"[ADVANCED-HEAL] Strategy: {strategy.type}, Locator: {strategy.locator}")
                    
                    # Record healing event
                    healing_event = {
                        'timestamp': datetime.now().isoformat(),
                        'original_locator': original_locator,
                        'healed_locator': strategy.locator,
                        'confidence': confidence,
                        'confidence_level': self.confidence_calculator.get_confidence_level(confidence),
                        'strategy': strategy.type,
                        'status': 'auto_approved' if confidence >= self.auto_approve_threshold else 'pending_approval'
                    }
                    
                    self.healing_history.append(healing_event)
                    
                    return {
                        'element': element,
                        'healed': True,
                        'confidence': confidence,
                        'original_locator': original_locator,
                        'working_locator': strategy.locator,
                        'requires_approval': confidence < self.auto_approve_threshold,
                        'healing_event': healing_event
                    }
                else:
                    logger.debug(f"[ADVANCED-HEAL] ✗ Confidence too low ({confidence * 100:.0f}%), skipping")
            
            except NoSuchElementException:
                logger.debug(f"[ADVANCED-HEAL] ✗ Strategy '{strategy.type}' failed")
                continue
        
        # All strategies failed
        logger.error(f"[ADVANCED-HEAL] ✗ All healing strategies failed")
        return None
    
    def _find_with_legacy_format(self, driver: WebDriver, step_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle old format for backward compatibility.
        Simply tries the locator without advanced healing.
        """
        locator = step_data['locator']
        try:
            by_type, value = self._parse_locator(locator)
            if by_type and value:
                element = driver.find_element(by_type, value)
                return {
                    'element': element,
                    'healed': False,
                    'confidence': 1.0,
                    'original_locator': locator,
                    'working_locator': locator,
                    'requires_approval': False
                }
        except NoSuchElementException:
            pass
        
        return None
    
    def _generate_healing_strategies(self, element_identity: ElementIdentity) -> List[HealingStrategy]:
        """
        Generate alternative locator strategies based on element identity.
        Uses RULE-BASED algorithms - no AI needed.
        
        Args:
            element_identity: ElementIdentity to generate strategies for
            
        Returns:
            List of HealingStrategy objects sorted by priority
        """
        strategies = []
        attrs = element_identity.attributes
        context = element_identity.context
        
        # Strategy 1: By ID (if available)
        if attrs.get('id'):
            strategies.append(HealingStrategy(
                'id_direct',
                f'By.id("{attrs["id"]}")',
                priority=1
            ))
        
        # Strategy 2: By name (if available)
        if attrs.get('name'):
            strategies.append(HealingStrategy(
                'name_direct',
                f'By.name("{attrs["name"]}")',
                priority=2
            ))
        
        # Strategy 3: By text content (for buttons/links)
        if attrs.get('text'):
            text = attrs['text'].replace('"', '\\"')
            strategies.append(HealingStrategy(
                'text_match',
                f'By.xpath("//*[contains(text(), \\"{text}\\")]")',
                priority=3
            ))
        
        # Strategy 4: By aria-label
        if attrs.get('aria_label'):
            aria_label = attrs['aria_label'].replace('"', '\\"')
            strategies.append(HealingStrategy(
                'aria_label',
                f'By.cssSelector("[aria-label=\\"{aria_label}\\"]")',
                priority=4
            ))
        
        # Strategy 5: By class name (partial match)
        if attrs.get('class'):
            # Get first class from class list
            first_class = attrs['class'].split()[0] if attrs['class'] else None
            if first_class:
                strategies.append(HealingStrategy(
                    'class_partial',
                    f'By.cssSelector(".{first_class}")',
                    priority=5
                ))
        
        # Strategy 6: By type attribute (for inputs)
        if attrs.get('type') and attrs.get('tag') == 'input':
            strategies.append(HealingStrategy(
                'type_match',
                f'By.cssSelector("input[type=\\"{attrs["type"]}\\"]")',
                priority=6
            ))
        
        # Strategy 7: By role attribute
        if attrs.get('role'):
            strategies.append(HealingStrategy(
                'role_match',
                f'By.cssSelector("[role=\\"{attrs["role"]}\\"]")',
                priority=7
            ))
        
        # Strategy 8: By tag + text combination
        if attrs.get('tag') and attrs.get('text'):
            tag = attrs['tag']
            text = attrs['text'].replace('"', '\\"')
            strategies.append(HealingStrategy(
                'tag_text_combo',
                f'By.xpath("//{tag}[contains(text(), \\"{text}\\")]")',
                priority=8
            ))
        
        # Strategy 9: By placeholder (for inputs)
        if attrs.get('placeholder'):
            placeholder = attrs['placeholder'].replace('"', '\\"')
            strategies.append(HealingStrategy(
                'placeholder_match',
                f'By.cssSelector("[placeholder=\\"{placeholder}\\"]")',
                priority=9
            ))
        
        # Sort by priority (lower number = higher priority)
        strategies.sort(key=lambda s: s.priority)
        
        logger.debug(f"[ADVANCED-HEAL] Generated {len(strategies)} healing strategies")
        return strategies
    
    def _parse_locator(self, locator_string: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Parse locator string to (By type, value) tuple.
        Reuses logic from original self_healing_locator.py for compatibility.
        
        Args:
            locator_string: Locator string like 'By.id("email")'
            
        Returns:
            Tuple of (By type, value) or (None, None) if parsing fails
        """
        import re
        
        if not locator_string:
            return None, None
        
        # Remove outer quotes if present
        locator_string = locator_string.strip()
        if (locator_string.startswith('"') and locator_string.endswith('"')) or \
           (locator_string.startswith("'") and locator_string.endswith("'")):
            locator_string = locator_string[1:-1]
        
        # Match pattern: By.METHOD("value")
        match = re.search(r'By\.(\w+)\((["\'])(.+?)\2\)\s*$', locator_string)
        
        if match:
            method = match.group(1)
            value = match.group(3)
            # Unescape quotes
            value = value.replace('\\"', '"').replace("\\'", "'")
        else:
            # Fallback parsing
            if 'By.' not in locator_string:
                return None, None
            
            try:
                method_match = re.search(r'By\.(\w+)', locator_string)
                if not method_match:
                    return None, None
                method = method_match.group(1)
                
                paren_start = locator_string.index('(')
                paren_end = locator_string.rindex(')')
                value_with_quotes = locator_string[paren_start+1:paren_end].strip()
                
                # Remove quotes
                if (value_with_quotes.startswith('"') and value_with_quotes.endswith('"')) or \
                   (value_with_quotes.startswith("'") and value_with_quotes.endswith("'")):
                    value = value_with_quotes[1:-1]
                else:
                    value = value_with_quotes
                
                value = value.replace('\\"', '"').replace("\\'", "'")
            except (ValueError, IndexError):
                return None, None
        
        # Map method names to By constants
        by_map = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'cssSelector': By.CSS_SELECTOR,
            'className': By.CLASS_NAME,
            'tagName': By.TAG_NAME,
            'linkText': By.LINK_TEXT,
            'partialLinkText': By.PARTIAL_LINK_TEXT
        }
        
        by_type = by_map.get(method)
        return by_type, value
    
    def get_healing_history(self) -> List[Dict[str, Any]]:
        """Get healing history (will be integrated with database later)."""
        return self.healing_history
    
    def highlight_healed_element(
        self, 
        driver: WebDriver, 
        element: WebElement, 
        healing_data: Dict[str, Any]
    ) -> bool:
        """
        Inject JavaScript to visually highlight a healed element.
        
        Args:
            driver: WebDriver instance
            element: Healed element to highlight
            healing_data: Healing event data with confidence score
            
        Returns:
            True if highlight succeeded, False otherwise
        """
        try:
            confidence = healing_data.get('confidence', 0.0)
            confidence_pct = int(confidence * 100)
            
            # Determine badge color based on confidence
            if confidence >= 0.8:
                badge_color = '#10b981'  # Green - high confidence
            elif confidence >= 0.6:
                badge_color = '#f59e0b'  # Orange - medium confidence
            else:
                badge_color = '#ef4444'  # Red - low confidence
            
            # JavaScript to highlight element with confidence badge
            highlight_script = f"""
            (function() {{
                var element = arguments[0];
                if (!element) return false;
                
                // Add visual highlight to element
                element.style.outline = '3px solid {badge_color}';
                element.style.outlineOffset = '2px';
                element.style.backgroundColor = 'rgba(16, 185, 129, 0.05)';
                element.style.transition = 'all 0.3s ease';
                
                // Create confidence badge
                var badge = document.createElement('div');
                badge.innerHTML = '🔧 Healed ({confidence_pct}%)';
                badge.className = 'self-healing-badge';
                badge.style.cssText = `
                    position: absolute;
                    top: -35px;
                    left: 0;
                    background: {badge_color};
                    color: white;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    z-index: 10000;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    animation: fadeIn 0.3s ease;
                `;
                
                // Ensure element has relative positioning
                var originalPosition = window.getComputedStyle(element).position;
                if (originalPosition === 'static') {{
                    element.style.position = 'relative';
                }}
                
                // Append badge to element
                element.appendChild(badge);
                
                // Scroll element into view smoothly
                element.scrollIntoView({{ 
                    behavior: 'smooth', 
                    block: 'center',
                    inline: 'nearest'
                }});
                
                // Remove badge after 5 seconds
                setTimeout(function() {{
                    if (badge && badge.parentNode) {{
                        badge.style.opacity = '0';
                        setTimeout(function() {{
                            if (badge && badge.parentNode) {{
                                badge.parentNode.removeChild(badge);
                            }}
                        }}, 300);
                    }}
                }}, 5000);
                
                return true;
            }})();
            """
            
            driver.execute_script(highlight_script, element)
            logger.info(f"[HIGHLIGHT] ✓ Element highlighted with {confidence_pct}% confidence badge")
            return True
            
        except Exception as e:
            logger.error(f"[HIGHLIGHT] ✗ Failed to highlight element: {e}")
            return False
    
    def find_element(self, driver: WebDriver, locator: str, context: Optional[str] = None) -> Optional[WebElement]:
        """
        Compatibility wrapper for v1 API.
        This method matches the signature of SelfHealingLocator.find_element()
        so that test_executor.py code doesn't need to change.
        
        Args:
            driver: Selenium WebDriver instance
            locator: Locator string (e.g., 'By.id("email")')
            context: Optional context (currently unused for compatibility)
            
        Returns:
            WebElement if found, None otherwise
        """
        # Create step data in expected format
        step_data = {
            'locator': locator  # Old format for backward compatibility
        }
        
        # Call advanced healing method
        result = self.find_element_with_healing(driver, step_data)
        
        if result:
            element = result.get('element')
            
            # Log healing information if it occurred
            if result.get('healed'):
                confidence = result.get('confidence', 0.0)
                confidence_pct = confidence * 100
                logging.info(f"[ADVANCED-HEAL] ✓ Element healed with {confidence_pct:.0f}% confidence")
                
                if result.get('requires_approval'):
                    logging.warning(f"[ADVANCED-HEAL] ⚠ Low confidence - requires manual approval")
            
            return element
        
        return None


# Export main classes
__all__ = [
    'ElementIdentity',
    'ConfidenceCalculator',
    'AdvancedSelfHealingLocator',
    'HealingStrategy'
]
