"""
Dataset and PageHelper Pattern Matching Module
Handles fuzzy matching, synonym normalization, and PageHelper pattern detection.
"""
import re
from difflib import SequenceMatcher
from typing import List, Dict, Optional


class DatasetMatcher:
    """Handles dataset fuzzy matching and PageHelper pattern matching."""
    
    def __init__(self, synonym_map: dict, dataset_cache: dict, pagehelper_cache: dict, param_extractor, language_converter):
        """Initialize with required dependencies."""
        self.synonym_map = synonym_map
        self.dataset_cache = dataset_cache
        self.pagehelper_cache = pagehelper_cache
        self.param_extractor = param_extractor
        self.language_converter = language_converter
        self._last_alternatives = []
    
    def normalize_with_synonyms(self, text: str) -> str:
        """Normalize text with action synonym replacement."""
        text = text.lower().strip()
        words = text.split()
        
        # Replace first word if it's an action verb
        if words and words[0] in self.synonym_map:
            words[0] = self.synonym_map[words[0]]
        
        # Remove filler words
        filler_words = ['the', 'a', 'an', 'please', 'can you', 'could you', 'would you']
        words = [w for w in words if w not in filler_words]
        
        return ' '.join(words)
    
    def find_dataset_match(self, prompt: str, return_alternatives: bool = True, preserve_value_placeholder: bool = False):
        """Find exact or fuzzy match in dataset cache with improved similarity scoring.
        
        Args:
            prompt: User's natural language prompt
            return_alternatives: Whether to return alternative matches
            preserve_value_placeholder: If True, keeps {VALUE} placeholder for input fields (value from UI)
        """
        # TRACE: Log every call to this method
        import traceback
        import datetime
        trace_msg = f"\n{'='*80}\n"
        trace_msg += f"[{datetime.datetime.now().strftime('%H:%M:%S')}] DATASET MATCHER CALLED\n"
        trace_msg += f"Prompt: '{prompt}'\n"
        trace_msg += f"return_alternatives: {return_alternatives}\n"
        trace_msg += f"CALL STACK:\n"
        stack = traceback.format_stack()
        for line in stack[-5:-1]:  # Last 4 frames
            trace_msg += f"{line}"
        trace_msg += f"{'='*80}\n"
        
        with open('dataset_matcher_trace.log', 'a', encoding='utf-8') as f:
            f.write(trace_msg)
        
        print(trace_msg)
        
        # Use synonym-aware normalization for better matching
        prompt_normalized = self.normalize_with_synonyms(prompt)
        
        # PRIORITY 1: Try exact match FIRST (highest priority)
        # "click login button" should match exact dataset entry, not template
        prompt_lower = prompt.lower().strip()
        exact_match = None
        if prompt_lower in self.dataset_cache:
            matched_entry = self.dataset_cache[prompt_lower]
            # Check if it's a template and needs parameter substitution
            if self._is_template(matched_entry):
                matched_entry = self.param_extractor.process_template_match(prompt, matched_entry, preserve_value_placeholder)
            
            print(f"[EXACT MATCH] Found exact match for '{prompt}'")
            if return_alternatives:
                # Even with exact match, find alternatives from similar prompts
                print(f"[EXACT MATCH] Also searching for alternatives...")
                exact_match = matched_entry
                # Continue to fuzzy matching to find alternatives
            else:
                return matched_entry
        
        # PRIORITY 2: Try template pattern matching (second priority)
        # This allows "click Carrier Account 2 button" to match "click {VALUE} button" template
        # when no exact match exists
        template_match = self._find_template_match(prompt, preserve_value_placeholder)
        if template_match:
            print(f"[TEMPLATE] Matched '{prompt}' to template pattern")
            if return_alternatives:
                # Even with template match, try to find alternatives from fuzzy matches
                print(f"[TEMPLATE] Also searching for alternatives...")
                # Continue to fuzzy matching to find alternatives
            else:
                return template_match
        
        # PRIORITY 3: Fuzzy matching (lowest priority - fallback)
        all_matches = []
        prompt_words = set(prompt_normalized.split())
        
        for cached_prompt, data in self.dataset_cache.items():
            cached_normalized = self.normalize_with_synonyms(cached_prompt)
            cached_words = set(cached_normalized.split())
            
            if not prompt_words or not cached_words:
                continue
            
            # Calculate multiple similarity metrics
            overlap = len(prompt_words & cached_words)
            total = len(prompt_words | cached_words)
            word_sim = overlap / total if total > 0 else 0
            
            # String similarity (sequence matching)
            string_sim = SequenceMatcher(None, prompt_normalized, cached_normalized).ratio()
            
            # Word containment (partial match bonus)
            containment = len(prompt_words & cached_words) / len(prompt_words) if prompt_words else 0
            
            # Combined score (weighted average)
            combined_score = (string_sim * 0.4) + (word_sim * 0.3) + (containment * 0.3)
            
            # Collect ALL matches (filter by threshold later for primary match/alternatives)
            # This ensures we can show alternatives even if no strong primary match exists
            all_matches.append({
                'score': combined_score,
                'prompt': cached_prompt,
                'data': data
            })
        
        # Sort by score
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        if not all_matches:
            # If we have an exact or template match but no fuzzy matches, still return with no alternatives
            if exact_match and return_alternatives:
                print(f"[ALTERNATIVES] Exact match but no fuzzy alternatives found")
                return {'match': exact_match, 'alternatives': []}
            if template_match and return_alternatives:
                print(f"[ALTERNATIVES] Template match but no fuzzy alternatives found")
                return {'match': template_match, 'alternatives': []}
            if return_alternatives:
                return {'match': None, 'alternatives': []}
            return None
        
        # **NEW: Even if primary match is weak, still return alternatives for "Did you mean?"**
        # This helps users when their prompt doesn't exactly match dataset
        if return_alternatives:
            # If we have an exact match, use it as primary
            if exact_match:
                best_match = exact_match
                used_exact = True
                print(f"[FUZZY] Using exact match as primary, finding alternatives from fuzzy matches")
            # If we have a template match, use it as primary
            elif template_match:
                best_match = template_match
                used_exact = False
                print(f"[FUZZY] Using template match as primary, finding alternatives from fuzzy matches")
            else:
                # Get best match from fuzzy matching (may be None if score < threshold for actual use)
                best = all_matches[0] if all_matches else None
                best_match = None
                used_exact = False
                
                # Only use best match if score is high enough (60%+)
                if best and best['score'] >= 0.6:
                    best_match = best['data'].copy()
                    
                    # Check if it's a template and needs parameter substitution
                    if self._is_template(best_match):
                        best_match = self.param_extractor.process_template_match(prompt, best_match, preserve_value_placeholder)
                    
                    print(f"[FUZZY] Matched '{prompt}' to '{best['prompt']}' (score: {best['score']:.2%})")
                else:
                    if best:
                        print(f"[FUZZY] No strong match for '{prompt}' (best score: {best['score']:.2%})")
                    else:
                        print(f"[FUZZY] No matches found for '{prompt}'")
            
            # **CRITICAL: Always try to return alternatives, even if primary match is weak**
            # This shows users similar prompts they might have meant
            alternatives_to_return = []
            
            # Extract action type from prompt for semantic filtering
            prompt_lower = prompt.lower()
            action_keywords = {
                'verify': ['verify', 'assert', 'check', 'validate', 'confirm'],
                'click': ['click', 'press', 'tap', 'button'],
                'input': ['enter', 'type', 'input', 'fill'],
                'select': ['select', 'choose', 'pick', 'dropdown'],
                'navigate': ['navigate', 'goto', 'visit', 'open'],
                'wait': ['wait', 'pause'],
                'get': ['get', 'fetch', 'retrieve', 'extract']
            }
            
            prompt_action_type = None
            for action_type, keywords in action_keywords.items():
                if any(kw in prompt_lower for kw in keywords):
                    prompt_action_type = action_type
                    break
            
            print(f"[SEMANTIC FILTER] Prompt: '{prompt}', detected action: {prompt_action_type}")
            
            # Use fuzzy search to find similar prompts
            # If primary match is from exact/template (not in fuzzy matches), start from 0
            # If primary match is from fuzzy matches, skip it (start from 1)
            start_idx = 0 if (best_match is None or used_exact) else 1
            
            # First pass: Try to get semantically matching alternatives
            print(f"[SEMANTIC FILTER] Checking {len(all_matches[start_idx:15])} candidates for semantic match...")
            for alt in all_matches[start_idx:15]:  # Check more alternatives
                # Skip very low scores
                if alt['score'] < 0.4:
                    print(f"[SEMANTIC FILTER] Skipping '{alt['prompt']}' - score too low ({alt['score']:.1%})")
                    continue
                
                # Check if alternative has matching action type
                alt_prompt_lower = alt['prompt'].lower()
                alt_action_type = None
                for action_type, keywords in action_keywords.items():
                    if any(kw in alt_prompt_lower for kw in keywords):
                        alt_action_type = action_type
                        break
                
                print(f"[SEMANTIC FILTER] Candidate: '{alt['prompt']}' (score: {alt['score']:.1%}, action: {alt_action_type})")
                
                # Filter by action type if we detected one
                if prompt_action_type and alt_action_type:
                    if prompt_action_type != alt_action_type:
                        print(f"[FILTER] Skipping '{alt['prompt']}' - action mismatch ({alt_action_type} != {prompt_action_type})")
                        continue
                
                print(f"[SEMANTIC FILTER] ✅ ACCEPTED: '{alt['prompt']}'")
                
                alt_data = alt['data'].copy()
                if self._is_template(alt_data):
                    alt_data = self.param_extractor.process_template_match(prompt, alt_data, preserve_value_placeholder)
                
                # Extract prompt variations from metadata
                # Check both root level and metadata.prompt_variations
                prompt_variations = alt_data.get('prompt_variations', [])
                if not prompt_variations and 'metadata' in alt_data:
                    prompt_variations = alt_data.get('metadata', {}).get('prompt_variations', [])
                
                # DEBUG: Log what we found
                print(f"[ALTERNATIVES DEBUG] Alternative '{alt['prompt']}' has {len(prompt_variations)} variations")
                if prompt_variations:
                    print(f"[ALTERNATIVES DEBUG] First 3 variations: {prompt_variations[:3]}")
                
                alternatives_to_return.append({
                    'prompt': alt['prompt'],
                    'score': alt['score'],
                    'code': alt_data.get('code', ''),
                    'xpath': alt_data.get('xpath', ''),
                    'category': alt_data.get('category', 'N/A'),
                    'prompt_variations': prompt_variations  # Include prompt variations for user reference
                })
                
                if len(alternatives_to_return) >= 3:
                    break
            
            # Fallback: ONLY if we found ZERO semantic matches, try without action filtering
            # This ensures we don't show wrong action types (e.g., dropdown for click)
            if len(alternatives_to_return) == 0 and len(all_matches) > start_idx:
                print(f"[FALLBACK] No semantic matches found, showing top scored alternatives (ignoring action type)")
                # Even in fallback, prefer higher scores and try to find at least some alternatives
                for alt in all_matches[start_idx:start_idx+10]:
                    if alt['score'] < 0.5:  # Higher threshold for fallback to maintain quality
                        continue
                    
                    alt_data = alt['data'].copy()
                    if self._is_template(alt_data):
                        alt_data = self.param_extractor.process_template_match(prompt, alt_data, preserve_value_placeholder)
                    
                    # Extract prompt variations from metadata
                    # Check both root level and metadata.prompt_variations
                    prompt_variations = alt_data.get('prompt_variations', [])
                    if not prompt_variations and 'metadata' in alt_data:
                        prompt_variations = alt_data.get('metadata', {}).get('prompt_variations', [])
                    
                    alternatives_to_return.append({
                        'prompt': alt['prompt'],
                        'score': alt['score'],
                        'code': alt_data.get('code', ''),
                        'xpath': alt_data.get('xpath', ''),
                        'category': alt_data.get('category', 'N/A'),
                        'prompt_variations': prompt_variations  # Include prompt variations for user reference
                    })
                    
                    if len(alternatives_to_return) >= 3:
                        break
            
            print(f"[ALTERNATIVES] Returning {len(alternatives_to_return)} alternatives (primary match: {best_match is not None})")
            
            # Store for get_last_alternatives()
            self._last_alternatives = alternatives_to_return
            
            # TRACE: Log what we're storing
            import datetime
            trace_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ALTERNATIVES STORED\n"
            trace_msg += f"Storing {len(alternatives_to_return)} alternatives in dataset_matcher._last_alternatives:\n"
            for i, alt in enumerate(alternatives_to_return, 1):
                trace_msg += f"  {i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')}\n"
            
            with open('dataset_matcher_trace.log', 'a', encoding='utf-8') as f:
                f.write(trace_msg + '\n')
            
            print(trace_msg)
            
            return {'match': best_match, 'alternatives': alternatives_to_return}
        
        # Non-alternatives path (original logic)
        best = all_matches[0]
        best_match = best['data']
        
        # Check if it's a template and needs parameter substitution
        if self._is_template(best_match):
            best_match = self.param_extractor.process_template_match(prompt, best_match, preserve_value_placeholder)
        
        print(f"[FUZZY] Matched '{prompt}' to '{best['prompt']}' (score: {best['score']:.2%})")
        
        return best_match
    
    def _is_template(self, entry: dict) -> bool:
        """Check if a dataset entry is a template requiring parameter substitution."""
        if not isinstance(entry, dict):
            return False
        metadata = entry.get('metadata', {})
        return metadata.get('entry_type') == 'template'
    
    def _find_template_match(self, prompt: str, preserve_value_placeholder: bool = False) -> Optional[dict]:
        """
        Find template match by checking if prompt matches template patterns.
        Templates with {VALUE}, {TAB}, {LINK}, etc. are matched using pattern structure.
        
        Example: "click Carrier Account 2 button" matches "click {VALUE} button"
        
        Args:
            prompt: User's prompt
            preserve_value_placeholder: If True, keeps {VALUE} for input fields (value from UI)
        """
        # Check if param_extractor can extract a parameter from this prompt
        extracted = self.param_extractor.extract_parameter(prompt, "")
        
        if not extracted or not extracted.get('value'):
            print(f"[TEMPLATE] No parameter extracted from '{prompt}'")
            return None
        
        print(f"[TEMPLATE] Extracted {extracted.get('placeholder')}='{extracted.get('value')}' from '{prompt}'")
        
        # We extracted a parameter! Now find the corresponding template in dataset
        # that matches BOTH placeholder AND structure
        best_match = None
        best_score = 0
        
        for cached_prompt, data in self.dataset_cache.items():
            # Check if this is a template entry
            if not self._is_template(data):
                continue
            
            # Check if the cached prompt has the placeholder we extracted
            placeholder = extracted.get('placeholder', '')
            if not placeholder or placeholder.lower() not in cached_prompt.lower():
                continue
            
            # Now check if the prompt structure matches the template structure
            # Remove the extracted value from prompt and placeholder from template
            # Then compare the remaining structure
            extracted_value = extracted.get('value', '').lower()
            prompt_structure = prompt.lower().replace(extracted_value, '').strip()
            template_structure = cached_prompt.lower()
            
            # Remove all placeholder variations from template
            for ph in ['{value}', '{tab}', '{link}', '{field}', '{option}']:
                template_structure = template_structure.replace(ph, '').strip()
            
            # Calculate similarity: how many words match
            prompt_words = set(prompt_structure.split())
            template_words = set(template_structure.split())
            if not template_words:
                continue
                
            common_words = prompt_words & template_words
            similarity = len(common_words) / len(template_words)
            
            print(f"[TEMPLATE] Checking '{cached_prompt}' - structure similarity: {similarity:.2f}")
            
            if similarity > best_score:
                best_score = similarity
                best_match = (cached_prompt, data)
        
        if best_match and best_score > 0.5:  # At least 50% structure match
            cached_prompt, data = best_match
            print(f"[TEMPLATE] ✅ Best match: '{cached_prompt}' (score: {best_score:.2f})")
            # Process the template with parameter substitution
            matched_entry = self.param_extractor.process_template_match(prompt, data, preserve_value_placeholder)
            if matched_entry:
                print(f"[TEMPLATE] ✅ Successfully matched and substituted")
                return matched_entry
            else:
                print(f"[TEMPLATE] ❌ Template substitution failed")
        else:
            print(f"[TEMPLATE] No matching template found with good structure match (best score: {best_score:.2f})")
        
        return None
    
    def get_last_alternatives(self) -> List[Dict]:
        """Get alternatives from the last fuzzy match (HYBRID MODE)."""
        # TRACE: Log what we're returning
        import datetime
        trace_msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] GET_LAST_ALTERNATIVES CALLED\n"
        trace_msg += f"Returning {len(self._last_alternatives)} alternatives:\n"
        for i, alt in enumerate(self._last_alternatives[:5], 1):
            trace_msg += f"  {i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')}\n"
        
        with open('dataset_matcher_trace.log', 'a', encoding='utf-8') as f:
            f.write(trace_msg + '\n')
            
        print(trace_msg)
        return self._last_alternatives.copy()
    
    def find_pagehelper_match(self, prompt: str):
        """Find exact or fuzzy match in PageHelper patterns."""
        prompt_lower = prompt.lower().strip()
        
        # Try exact match first
        if prompt_lower in self.pagehelper_cache:
            print(f"[PAGEHELPER] ✅ Exact match found: {self.pagehelper_cache[prompt_lower]['method_name']}")
            return self.pagehelper_cache[prompt_lower]
        
        # Try pattern matching with placeholders
        matched_patterns = []
        
        for cached_prompt, data in self.pagehelper_cache.items():
            # Context-aware filtering
            if 'dropdown' in prompt_lower or (' from ' in prompt_lower and 'select' in prompt_lower):
                if data['method_name'] not in ['setDropdownValue', 'getSelectedDropdownValue', 'isDropdownFieldDisabled']:
                    continue
            
            elif 'select' in prompt_lower and 'option' in prompt_lower and 'button' not in prompt_lower:
                if data['method_name'] not in ['setDropdownValue', 'getSelectedDropdownValue', 'isDropdownFieldDisabled']:
                    continue
            
            elif 'title' in prompt_lower and 'verify' in prompt_lower:
                if '{button}' in cached_prompt or '{link}' in cached_prompt:
                    continue
            
            elif 'checkbox' in prompt_lower:
                if 'Checkbox' not in data['method_name']:
                    continue
            
            elif 'dialog' in prompt_lower or 'modal' in prompt_lower:
                if 'Dialog' not in data['method_name'] and 'dialog' not in data['method_name'].lower():
                    continue
            
            # Convert pattern to regex
            pattern = cached_prompt
            pattern = pattern.replace(' the ', ' (?:the )?')
            pattern = re.sub(r'\{[^}]+\}', r'([^\\s]+(?:\\s+[^\\s]+)*?)', pattern)
            pattern = f'^{pattern}$'
            
            try:
                if re.match(pattern, prompt_lower, re.IGNORECASE):
                    specificity = len(cached_prompt)
                    matched_patterns.append((specificity, cached_prompt, data))
            except:
                pass
        
        # Return most specific match
        if matched_patterns:
            matched_patterns.sort(reverse=True, key=lambda x: x[0])
            best_match = matched_patterns[0]
            print(f"[PAGEHELPER] ✅ Pattern match found: {best_match[2]['method_name']}")
            return best_match[2]
        
        # Try fuzzy matching
        best_match = None
        best_score = 0
        prompt_words = set(prompt_lower.split())
        
        for cached_prompt, data in self.pagehelper_cache.items():
            if '{' in cached_prompt:
                continue
                
            cached_words = set(cached_prompt.split())
            overlap = len(prompt_words & cached_words)
            total = len(prompt_words | cached_words)
            score = overlap / total if total > 0 else 0
            
            if score > best_score and score >= 0.75:
                best_score = score
                best_match = data
        
        if best_match:
            print(f"[PAGEHELPER] 🔍 Fuzzy match found (score: {best_score:.2f}): {best_match['method_name']}")
        
        return best_match
    
    def generate_from_pagehelper(self, prompt: str, pagehelper_match: dict, language: str, comprehensive_mode: bool, preserve_placeholder: bool = False) -> str:
        """Generate PageHelper method call code."""
        method_name = pagehelper_match['method_name']
        code_template = pagehelper_match['code_template']
        category = pagehelper_match['category']
        
        print(f"[PAGEHELPER] Generating {language} code for: {method_name} (category: {category})")
        
        # Extract parameters from prompt
        params = self.extract_pagehelper_params(prompt, pagehelper_match)
        
        # Replace placeholders
        code = code_template
        
        if not preserve_placeholder:
            for key, value in params.items():
                placeholder = f"{{{key}}}"
                code = code.replace(placeholder, value)
        
        # Convert to target language
        if language != 'java' and self.language_converter:
            code = self.language_converter.convert_code_to_language(code, language)
        
        # Add comprehensive mode enhancements
        if comprehensive_mode:
            comment_prefix = '//' if language in ['java', 'javascript', 'csharp'] else '#'
            code = f"""{comment_prefix} PageHelper method with robust wait
WebDriverWait wait = new WebDriverWait(driver, 10);
{code}
{comment_prefix} Wait for page stabilization
waitForPageLoading();"""
        
        print(f"[PAGEHELPER] ✅ Generated code")
        return code
    
    def extract_pagehelper_params(self, prompt: str, pagehelper_match: dict) -> dict:
        """Extract parameters from prompt for PageHelper methods."""
        params = {}
        
        # Extract value pattern
        value_match = re.search(r'(?:enter|type|select)\s+([^\s]+(?:\s+[^\s]+)*?)\s+(?:in|from)', prompt, re.IGNORECASE)
        if value_match:
            params['VALUE'] = value_match.group(1).strip()
        
        # Extract field/label name
        label_match = re.search(r'in\s+([^\s]+(?:\s+[^\s]+)?)\s+(?:field|dropdown)', prompt, re.IGNORECASE)
        if label_match:
            params['LABEL'] = label_match.group(1).strip().title()
        
        # Extract button/link text
        click_match = re.search(r'click\s+([^\s]+(?:\s+[^\s]+)?)\s+(?:button|link)', prompt, re.IGNORECASE)
        if click_match:
            text = click_match.group(1).strip().title()
            params['BUTTON_TEXT'] = text
            params['LINK_TEXT'] = text
        
        # Extract checkbox label
        checkbox_match = re.search(r'(?:check|uncheck|select)(?:\s+the)?\s+(.+?)\s+checkbox', prompt, re.IGNORECASE)
        if checkbox_match:
            params['LABEL'] = checkbox_match.group(1).strip().title()
        
        # Defaults
        params.setdefault('LABEL', 'Label')
        params.setdefault('VALUE', 'value')
        params.setdefault('BUTTON_TEXT', 'Submit')
        params.setdefault('LINK_TEXT', 'Link')
        
        return params
