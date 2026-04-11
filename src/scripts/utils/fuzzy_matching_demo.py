import json
from difflib import SequenceMatcher
import re

def normalize_prompt(prompt):
    """Normalize prompt for better matching"""
    # Convert to lowercase
    prompt = prompt.lower().strip()
    # Remove extra whitespace
    prompt = ' '.join(prompt.split())
    # Remove common filler words
    filler_words = ['the', 'a', 'an', 'please', 'can you', 'could you']
    words = prompt.split()
    words = [w for w in words if w not in filler_words]
    return ' '.join(words)

def calculate_similarity(prompt1, prompt2):
    """Calculate similarity between two prompts (0.0 to 1.0)"""
    norm1 = normalize_prompt(prompt1)
    norm2 = normalize_prompt(prompt2)
    
    # String similarity
    string_sim = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Word overlap similarity
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    if len(words1) == 0 or len(words2) == 0:
        word_sim = 0
    else:
        word_sim = len(words1 & words2) / max(len(words1), len(words2))
    
    # Combined similarity (weighted average)
    similarity = (string_sim * 0.6) + (word_sim * 0.4)
    return similarity

def find_best_match(user_prompt, dataset, threshold=0.6):
    """
    Find best matching entry in dataset using fuzzy matching
    
    Args:
        user_prompt: The user's input prompt
        dataset: List of dataset entries
        threshold: Minimum similarity score (0.6 = 60% match)
    
    Returns:
        Best matching entry or None
    """
    best_match = None
    best_score = 0.0
    
    for entry in dataset:
        dataset_prompt = entry.get('prompt', '')
        similarity = calculate_similarity(user_prompt, dataset_prompt)
        
        if similarity > best_score:
            best_score = similarity
            best_match = entry
    
    # Return match only if above threshold
    if best_score >= threshold:
        return best_match, best_score
    
    return None, 0.0

# Load dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print("FUZZY MATCHING DEMONSTRATION")
print("=" * 70)

# Test various partial prompts
test_prompts = [
    "click submit",                           # Partial: should match "click the submit button"
    "click save",                             # Partial: should match "click the save button"  
    "press cancel button",                    # Similar: should match "click the cancel button"
    "type email",                             # Partial: should match input field entries
    "open overview tab",                      # Partial: should match "click the overview tab"
    "select dropdown",                        # Partial: should match dropdown entries
    "click confirmation id",                  # Partial: should match specific field
    "get error text",                         # Partial: should match "get error message"
]

print("\nTesting Fuzzy Matching:\n")

for user_prompt in test_prompts:
    match, score = find_best_match(user_prompt, dataset, threshold=0.5)
    
    print(f"User: \"{user_prompt}\"")
    if match:
        print(f"  ✅ Match: \"{match['prompt']}\" (Score: {score:.2%})")
        code_preview = match['code'][:80].replace('\n', ' ')
        print(f"  📝 Code: {code_preview}...")
    else:
        print(f"  ❌ No match found (use generic template)")
    print()

print("=" * 70)
print("IMPLEMENTATION GUIDE")
print("=" * 70)
print("""
INTEGRATE THIS INTO YOUR API SERVER:

1. When user sends a prompt, first try fuzzy matching:
   
   match, score = find_best_match(user_prompt, dataset, threshold=0.6)
   
   if match:
       # Use the matched code directly
       return match['code']
   else:
       # Fall back to template or ML generation
       return generate_generic_code(user_prompt)

2. Adjust threshold based on your needs:
   - 0.8-1.0: Very strict (exact matches)
   - 0.6-0.8: Moderate (recommended)
   - 0.4-0.6: Loose (more matches but less accurate)

3. Advanced: Try multiple strategies:
   
   # Strategy 1: Exact match
   exact = find_exact_match(prompt, dataset)
   if exact: return exact['code']
   
   # Strategy 2: Template match with parameters
   template = match_template(prompt, dataset)
   if template: return substitute_template(template, prompt)
   
   # Strategy 3: Fuzzy match (this solution)
   fuzzy = find_best_match(prompt, dataset, threshold=0.6)
   if fuzzy: return fuzzy['code']
   
   # Strategy 4: ML generation
   return ml_model.generate(prompt)

INTEGRATION LOCATION:
  File: src/main/python/api_server_modular.py
  Function: generate_test_code() or similar
  
  Replace:
    return generic_template_code()
  
  With:
    match, score = find_best_match(user_prompt, dataset)
    if match:
        return match['code']
    return generic_template_code()
""")

print("\n💡 Want me to integrate fuzzy matching into your API server?")
