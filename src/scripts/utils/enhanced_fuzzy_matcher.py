#!/usr/bin/env python3
"""
Enhanced Fuzzy Matching with Action Synonyms and Multiple Match Support

Two modes:
1. SINGLE_BEST (current): Returns one specific best match
2. ALL_MATCHES (new): Returns all matches above threshold for user selection
"""
import json
from difflib import SequenceMatcher
from typing import List, Dict

class EnhancedFuzzyMatcher:
    """Enhanced matcher with synonym support"""
    
    # Action verb synonyms - treat these as equivalent
    ACTION_SYNONYMS = {
        'click': ['click', 'press', 'tap', 'select', 'choose', 'hit'],
        'enter': ['enter', 'type', 'input', 'fill', 'write'],
        'open': ['open', 'activate', 'show', 'display'],
        'get': ['get', 'read', 'fetch', 'retrieve', 'extract'],
        'verify': ['verify', 'check', 'validate', 'confirm', 'assert'],
    }
    
    def __init__(self):
        # Build reverse mapping for quick lookup
        self.synonym_map = {}
        for canonical, synonyms in self.ACTION_SYNONYMS.items():
            for synonym in synonyms:
                self.synonym_map[synonym] = canonical
    
    def normalize_with_synonyms(self, text: str) -> str:
        """Normalize text with action synonym replacement"""
        text = text.lower().strip()
        words = text.split()
        
        # Replace first word if it's an action verb
        if words and words[0] in self.synonym_map:
            words[0] = self.synonym_map[words[0]]
        
        # Remove filler words
        filler_words = ['the', 'a', 'an', 'please', 'can you', 'could you', 'would you']
        words = [w for w in words if w not in filler_words]
        
        return ' '.join(words)
    
    def find_all_matches(self, user_prompt: str, dataset: List[Dict], 
                        threshold: float = 0.6, max_results: int = 10) -> List[Dict]:
        """Find ALL matches above threshold, sorted by score"""
        
        user_normalized = self.normalize_with_synonyms(user_prompt)
        user_words = set(user_normalized.split())
        
        all_matches = []
        
        for entry in dataset:
            if 'prompt' not in entry:
                continue
            
            cached_prompt = entry['prompt']
            cached_normalized = self.normalize_with_synonyms(cached_prompt)
            cached_words = set(cached_normalized.split())
            
            if not user_words or not cached_words:
                continue
            
            # Calculate similarities
            overlap = len(user_words & cached_words)
            total = len(user_words | cached_words)
            word_sim = overlap / total if total > 0 else 0
            
            string_sim = SequenceMatcher(None, user_normalized, cached_normalized).ratio()
            containment = overlap / len(user_words) if len(user_words) > 0 else 0
            
            # Combined score
            combined_score = (string_sim * 0.4) + (word_sim * 0.3) + (containment * 0.3)
            
            if combined_score >= threshold:
                all_matches.append({
                    'prompt': cached_prompt,
                    'score': combined_score,
                    'code': entry.get('code', ''),
                    'xpath': entry.get('xpath', ''),
                    'category': entry.get('category', 'N/A'),
                    'full_entry': entry
                })
        
        # Sort by score and limit results
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        return all_matches[:max_results]
    
    def find_best_match(self, user_prompt: str, dataset: List[Dict], 
                        threshold: float = 0.6) -> Dict:
        """Find single best match (current behavior)"""
        matches = self.find_all_matches(user_prompt, dataset, threshold, max_results=1)
        return matches[0] if matches else None


def test_enhanced_matching():
    """Test enhanced matching with synonym support"""
    
    # Load dataset
    with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    matcher = EnhancedFuzzyMatcher()
    
    # Previously failing test cases
    failing_cases = [
        "press save",
        "press continue",
        "click sign out",
        "open errors",
        "select overview",
        "search customer",
    ]
    
    print("="*80)
    print("ENHANCED FUZZY MATCHING WITH ACTION SYNONYMS")
    print("="*80)
    print("\nTesting previously FAILING cases with synonym support:\n")
    
    for i, prompt in enumerate(failing_cases, 1):
        print(f"\n[{i}] Testing: '{prompt}'")
        print("-" * 80)
        
        # Find all matches
        matches = matcher.find_all_matches(prompt, dataset, threshold=0.6, max_results=5)
        
        if matches:
            print(f"✅ FOUND {len(matches)} MATCHES")
            print(f"\nTop match:")
            best = matches[0]
            print(f"   [{best['score']:.1%}] {best['prompt']}")
            print(f"   Code: {best['code'][:80].replace(chr(10), ' ')}...")
            
            if len(matches) > 1:
                print(f"\n   Alternative matches:")
                for alt in matches[1:]:
                    print(f"      • [{alt['score']:.1%}] {alt['prompt'][:70]}")
        else:
            # Try with lower threshold
            matches_lower = matcher.find_all_matches(prompt, dataset, threshold=0.5, max_results=3)
            if matches_lower:
                print(f"⚠️  NO MATCH at 60%, but found {len(matches_lower)} at 50% threshold:")
                for match in matches_lower:
                    print(f"   • [{match['score']:.1%}] {match['prompt'][:70]}")
            else:
                print(f"❌ NO MATCH FOUND (even at 50% threshold)")
    
    # Compare both modes
    print("\n" + "="*80)
    print("MODE COMPARISON")
    print("="*80)
    
    test_prompt = "click submit"
    
    print(f"\nTest prompt: '{test_prompt}'")
    print(f"\n1. SINGLE BEST MODE (current):")
    best = matcher.find_best_match(test_prompt, dataset, threshold=0.6)
    if best:
        print(f"   Returns: '{best['prompt']}' (score: {best['score']:.1%})")
    
    print(f"\n2. ALL MATCHES MODE (new):")
    all_matches = matcher.find_all_matches(test_prompt, dataset, threshold=0.6, max_results=5)
    print(f"   Returns: {len(all_matches)} matches")
    for match in all_matches[:3]:
        print(f"      • [{match['score']:.1%}] {match['prompt']}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("""
Option 1: KEEP SINGLE BEST (Current)
   ✅ Simple, deterministic
   ✅ No user decision needed
   ❌ User doesn't see alternatives

Option 2: SHOW ALL MATCHES (New)
   ✅ User sees all options
   ✅ Better coverage discovery
   ❌ Requires UI for selection
   ❌ More complex

Option 3: HYBRID (Recommended)
   - Return best match automatically
   - Show top 3 alternatives in UI as suggestions
   - User can click to use alternative
   
Implementation:
   - Modify inference_improved.py to return all matches
   - Add 'alternatives' field to API response
   - UI shows "Did you mean?" with alternatives
""")
    
    return matches

if __name__ == "__main__":
    test_enhanced_matching()
