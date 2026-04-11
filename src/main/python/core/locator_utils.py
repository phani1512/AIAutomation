"""
Locator Utilities Module - Selector Generation and Locator Suggestions
Extracted from inference_improved.py for better modularity

Handles:
- Field selector generation (CSS/XPath)
- Locator suggestions from HTML
- Locator suggestions from element attributes  
- Locator extraction from prompts

VERSION: 1.0.0 - Extracted for modularity
"""

import re
from typing import Dict, List, Tuple, Optional


class LocatorUtils:
    """Utilities for generating and suggesting locators."""
    
    def __init__(self):
        """Initialize locator utilities."""
        pass
    
    def generate_field_selectors(self, field_name: str) -> list:
        """Generate multiple CSS selector strategies for a field name.
        
        Args:
            field_name: Field name (e.g., 'email', 'username', 'password')
        
        Returns:
            List of CSS selectors ordered by likelihood of success
        """
        field_lower = field_name.lower()
        field_title = field_name.title()
        
        selectors = [
            # Strategy 1: Angular Material style (app-input with label)
            f"app-input[label='{field_title}'] input",
            
            # Strategy 2: Name attribute
            f"input[name='{field_lower}']",
            
            # Strategy 3: ID attribute (exact)
            f"input[id='{field_lower}']",
            
            # Strategy 4: ID contains (more flexible)
            f"input[id*='{field_lower}']",
            
            # Strategy 5: Placeholder attribute
            f"input[placeholder*='{field_title}']",
            
            # Strategy 6: Type attribute (for password/email)
            f"input[type='{field_lower}']" if field_lower in ['password', 'email', 'text'] else f"input[name='{field_lower}']",
            
            # Strategy 7: Label + input (following sibling)
            f"label:contains('{field_title}') + input",
            
            # Strategy 8: Generic input by type
            f"input[type='text'][name*='{field_lower}']",
        ]
        
        return selectors
    
    def extract_locator(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract By locator type and value from prompt.
        
        Args:
            prompt: User's natural language prompt
        
        Returns:
            Tuple of (locator_type, locator_value) or (None, None) if not found
        """
        prompt_lower = prompt.lower()
        
        # Pattern: "with id VALUE", "with name VALUE", etc.
        id_match = re.search(r'with\s+id\s+([^\s,]+)', prompt_lower)
        if id_match:
            return ('id', id_match.group(1))
        
        name_match = re.search(r'with\s+name\s+([^\s,]+)', prompt_lower)
        if name_match:
            return ('name', name_match.group(1))
        
        class_match = re.search(r'with\s+class\s+([^\s,]+)', prompt_lower)
        if class_match:
            return ('className', class_match.group(1))
        
        xpath_match = re.search(r'with\s+xpath\s+(.+?)(?:\s+and|\s+then|$)', prompt_lower)
        if xpath_match:
            return ('xpath', xpath_match.group(1).strip())
        
        css_match = re.search(r'with\s+css\s+(.+?)(?:\s+and|\s+then|$)', prompt_lower)
        if css_match:
            return ('cssSelector', css_match.group(1).strip())
        
        type_match = re.search(r'with\s+type\s+([^\s,]+)', prompt_lower)
        if type_match:
            return ('cssSelector', f'[type="{type_match.group(1)}"]')
        
        # No specific locator found
        return (None, None)
    
    def suggest_locator_from_html(self, html: str) -> dict:
        """Suggest locator based on HTML element.
        
        Args:
            html: HTML string of the element
        
        Returns:
            Dict with recommended_locators, ai_suggestion, and element_analysis
        """
        # Clean up HTML input - remove extra whitespace and newlines
        html = html.strip()
        
        # Extract tag name - handle various input formats
        tag_match = re.search(r'<(\w+)', html, re.IGNORECASE)
        if not tag_match:
            tag_name = 'div'
        else:
            tag_name = tag_match.group(1)
        
        # Extract attributes
        id_match = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        name_match = re.search(r'\bname\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        class_match = re.search(r'\bclass\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        type_match = re.search(r'\btype\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        # Extract text content
        text_match = re.search(r'>([^<]+)<', html)
        text_content = text_match.group(1).strip() if text_match else ''
        
        locators = []
        # Check if ANY attribute exists
        has_attributes = bool(id_match or name_match or class_match or type_match or text_content)
        
        # Priority 1: ID attribute
        if id_match:
            id_value = id_match.group(1)
            locators.append(f'By.id("{id_value}")')
        
        # Priority 2: Name attribute
        if name_match:
            name_value = name_match.group(1)
            locators.append(f'By.name("{name_value}")')
        
        # Priority 3: Class attribute
        if class_match:
            class_value = class_match.group(1).split()[0]  # Use first class only
            locators.append(f'By.className("{class_value}")')
            locators.append(f'By.cssSelector(".{class_value}")')
        
        # Priority 4: Type attribute (for input elements)
        if type_match:
            type_value = type_match.group(1)
            locators.append(f'By.cssSelector("[type=\\"{type_value}\\"]")')
        
        # Priority 5: Text content (for links, buttons)
        if text_content and tag_name.lower() in ['a', 'button', 'span', 'div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            locators.append(f'By.linkText("{text_content}")')
            if len(text_content) > 10:
                locators.append(f'By.partialLinkText("{text_content[:10]}")')
            locators.append(f'By.xpath("//{tag_name}[contains(text(), \\"{text_content}\\")]")')
        
        # If NO attributes found, generate XPath AND CSS selectors
        if not has_attributes:
            locators.append(f'By.xpath("//{tag_name}")')
            locators.append(f'By.cssSelector("{tag_name}")')
            if tag_name.lower() == 'input':
                locators.append(f'By.xpath("//input[@type=\'text\']")')
            if tag_name.lower() == 'button':
                locators.append(f'By.xpath("//button[@type=\'submit\']")')
        
        return {
            'recommended_locators': locators,
            'ai_suggestion': f"Generated {len(locators)} locator strategies for {tag_name} element",
            'element_analysis': {
                'has_id': id_match is not None,
                'has_name': name_match is not None,
                'has_class': class_match is not None,
                'has_type': type_match is not None,
                'has_text': bool(text_content),
                'has_attributes': has_attributes,
                'tag_name': tag_name,
                'strategy': 'XPath & CSS (No Attributes)' if not has_attributes else 'CSS/ID/Name/Class'
            }
        }
    
    def suggest_locator(self, element_type: str, action: str, attributes: dict) -> list:
        """
        Suggest optimal locators for an element based on its attributes.
        Used by the recorder to generate intelligent locator suggestions.
        
        Args:
            element_type: HTML tag name (e.g., 'button', 'input')
            action: Action being performed (e.g., 'click', 'input')
            attributes: Dictionary of element attributes (id, name, className, etc.)
        
        Returns:
            List of suggested locators in priority order
        """
        locators = []
        
        # For input/select/textarea, prioritize name and ID (stable for forms)
        if element_type.lower() in ['input', 'select', 'textarea']:
            # Priority 1: Name (best for forms)
            if attributes.get('name'):
                locators.append(f'By.name("{attributes["name"]}")')
            
            # Priority 2: ID (secondary for inputs)
            if attributes.get('id'):
                locators.append(f'By.id("{attributes["id"]}")')
        
        # For links, prioritize linkText
        elif element_type.lower() == 'a':
            link_text = attributes.get('innerText') or attributes.get('text', '')
            link_text = link_text.strip()
            if link_text:
                locators.append(f'By.linkText("{link_text}")')
                if len(link_text) > 20:
                    locators.append(f'By.partialLinkText("{link_text[:20]}")')
        
        # For buttons and clickable elements, prioritize text-based locators
        elif element_type.lower() == 'button' or action == 'click':
            text = attributes.get('innerText') or attributes.get('text', '')
            text = text.strip() if text else ''
            if text:
                # Special handling for tab buttons with role='tab' and span children
                if attributes.get('role') == 'tab':
                    locators.append(f"By.xpath('//button[@role=\"tab\"]/span[contains(.,\"{text}\")]')")
                    locators.append(f"By.xpath('//button[@role=\"tab\" and contains(.,\"{text}\")]')")
                
                # Use text() for button direct text matching (more specific than normalize-space)
                locators.append(f"By.xpath('//button[contains(text(), \"{text}\")]')")
                # Fallback with any element and text()
                locators.append(f"By.xpath('//*/button[contains(text(), \"{text}\")]')")
                # If button has class, add class + text strategy for more specificity
                if attributes.get('className'):
                    class_name = attributes['className'].split()[0]  # Use first class
                    locators.append(f"By.xpath('//button[contains(@class, \"{class_name}\") and contains(text(), \"{text}\")]')")
                if attributes.get('type'):
                    locators.append(f"By.xpath('//button[@type=\"{attributes['type']}\" and contains(text(), \"{text}\")]')")
        
        # CSS Selector with classes (good alternative)
        if attributes.get('className'):
            classes = attributes['className'].split()
            if classes:
                # Use class-based selector
                non_generic = [cls for cls in classes if cls not in ['btn', 'form-control', 'input', 'button']]
                if non_generic:
                    locators.append(f'By.cssSelector("{element_type.lower()}.{non_generic[0]}")')
                else:
                    locators.append(f'By.cssSelector("{element_type.lower()}.{classes[0]}")')
        
        # ID as fallback for non-input elements (only if no text-based locators)
        if element_type.lower() not in ['input', 'select', 'textarea'] and not any('text()' in loc for loc in locators):
            if attributes.get('id'):
                locators.append(f'By.id("{attributes["id"]}")')
        
        # Priority 4: CSS Selector (combination)
        if attributes.get('id'):
            locators.append(f'By.cssSelector("#{attributes["id"]}")')
        elif attributes.get('className'):
            classes = attributes['className'].split()
            if classes:
                locators.append(f'By.cssSelector(".{classes[0]}")')
        
        # Priority 5: Text-based XPath (relative, not absolute)
        if attributes.get('text') or attributes.get('innerText'):
            text = attributes.get('innerText') or attributes.get('text')
            text = text.strip()
            if text:
                # For buttons, use text() for more specific matching
                if element_type.lower() == 'button':
                    locators.append(f"By.xpath('//button[contains(text(), \"{text}\")]')")
                    locators.append(f"By.xpath('//*/button[contains(text(), \"{text}\")]')")
                else:
                    # Use normalize-space(.) for other elements to handle whitespace and nested text
                    locators.append(f"By.xpath('//{element_type}[contains(normalize-space(.), \"{text}\")]')")
        
        # Priority 6: Attribute-based XPath (relative)
        if attributes.get('id'):
            locators.append(f'By.xpath("//*[@id=\\"{attributes["id"]}\\"]")')
        elif attributes.get('name'):
            locators.append(f'By.xpath("//*[@name=\\"{attributes["name"]}\\"]")')
        
        # If no locators found, create a generic tag-based one
        if not locators:
            locators.append(f'By.tagName("{element_type.lower()}")')
        
        # NEVER use absolute XPath from attributes.get('xpath') - it's too fragile
        
        return locators
