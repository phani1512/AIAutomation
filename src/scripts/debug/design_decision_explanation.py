"""
DESIGN DECISION: Concrete Examples vs. Templates

USER'S IMPORTANT POINT:
"If we have templates, we can use for any label name irrespective of hardcoded values"

This is TRUE and reveals a key architectural choice!

================================================================================
APPROACH 1: CONCRETE EXAMPLES ONLY (Current - 716 entries)
================================================================================

Dataset Examples:
  "click the submit button" → By.xpath("//button[text()='Submit']")
  "click the cancel button" → By.xpath("//button[text()='Cancel']")
  "click the save button" → By.xpath("//button[text()='Save']")

HOW IT WORKS:
  1. ML model trains on concrete examples
  2. Model learns pattern: "click the X button" → By.xpath("//button[text()='X']")
  3. At runtime: "click the confirm button" → Model generates new locator

PROS:
  ✅ Pure ML approach - model learns patterns
  ✅ Can generalize to unseen elements (if trained well)
  ✅ More "intelligent" - understands context

CONS:
  ❌ Limited to patterns it learned
  ❌ Needs LARGE dataset to generalize well
  ❌ May fail on edge cases not in training
  ❌ Less predictable/deterministic

REALISTIC LIMITATION:
  Your 716 entries cover maybe 100-200 unique element names
  What about the other 1000+ elements in your app? Model must guess.

================================================================================
APPROACH 2: TEMPLATE-BASED (What you're suggesting)
================================================================================

Dataset Examples:
  "click {button}" → By.xpath("//button[text()='{BUTTON_TEXT}']")
  "click the {tab} tab" → By.xpath("//button[@role='tab']/span[contains(.,'{TAB_NAME}')]")
  "enter {text} in {field}" → element.sendKeys("{TEXT}")

HOW IT WORKS:
  1. System matches prompt pattern: "click {button}"
  2. Extracts parameter: button = "confirm"
  3. Substitutes into template: By.xpath("//button[text()='confirm']")

PROS:
  ✅ Works with ANY element name immediately
  ✅ Deterministic and predictable
  ✅ No training needed for new elements
  ✅ Perfect for rapid test creation

CONS:
  ❌ Not true ML - just template matching
  ❌ Requires exact pattern match
  ❌ Less flexible with natural language variations

================================================================================
APPROACH 3: HYBRID (RECOMMENDED FOR YOUR USE CASE)
================================================================================

Combine BOTH approaches:

DATASET STRUCTURE:
  [
    // Concrete examples (for ML training)
    {"prompt": "click the submit button", "code": "By.xpath(\"//button[text()='Submit']\")"},
    {"prompt": "click the cancel button", "code": "By.xpath(\"//button[text()='Cancel']\")"},
    
    // Templates (for direct substitution)
    {"prompt": "click {button}", "code": "By.xpath(\"//button[text()='{BUTTON_TEXT}']\")"},
    {"prompt": "click the {tab} tab", "code": "By.xpath(\"//button[@role='tab']/span[contains(.,'{TAB_NAME}')]\")"
  ]

RUNTIME LOGIC:
  1. First try exact template match with parameter extraction
  2. If no match, use ML model to generate code
  3. Fall back to self-healing locators if both fail

PROS:
  ✅ Best of both worlds
  ✅ Covers specific elements (concrete) AND generic patterns (templates)
  ✅ ML learns from examples, templates provide fallback
  ✅ Maximum flexibility

================================================================================
REAL-WORLD EXAMPLE
================================================================================

User says: "click the SignOut button"

APPROACH 1 (Concrete Only - 716 entries):
  - Searches dataset: No exact match for "SignOut"
  - ML model generates: By.xpath("//button[text()='SignOut']")
  - Success rate: ~70-80% (depends on training quality)

APPROACH 2 (Template - your suggestion):
  - Matches pattern: "click {button}"
  - Extracts: button = "SignOut"
  - Substitutes: By.xpath("//button[text()='SignOut']")
  - Success rate: ~95% (deterministic)

APPROACH 3 (Hybrid):
  - Tries template first: MATCH! → By.xpath("//button[text()='SignOut']")
  - Success rate: ~95%, with ML backup for complex cases

================================================================================
RECOMMENDATION FOR YOUR SYSTEM
================================================================================

Given that you're building a TEST AUTOMATION system where users need to:
  - Test ANY element in the application
  - Use natural language prompts
  - Get reliable, consistent results

YOU SHOULD USE: HYBRID APPROACH (Approach 3)

RESTORE these template categories:
  ✅ Generic button clicks: "click {button}"
  ✅ Generic tab navigation: "click the {tab} tab"
  ✅ Generic links: "click {link} link"
  ✅ Generic menu items: "select {menu} option"
  ✅ Generic input fields: "enter {text} in {field}"
  ✅ Generic file upload: "upload {filename}"

KEEP the concrete examples for:
  ✅ ML model training
  ✅ Complex multi-step patterns
  ✅ Application-specific workflows

FINAL DATASET SIZE: ~750-800 entries
  - 716 concrete examples (current)
  - ~40-80 template patterns (restored + new)

================================================================================
WANT ME TO RESTORE THE TEMPLATE ENTRIES?
================================================================================

I can restore the 40 template entries we removed, giving you:
  1. 716 concrete training examples
  2. 40 generic templates for any element name
  3. Total: 756 entries with maximum flexibility

This gives you the best of both approaches!
"""

print(__doc__)

print("\n" + "=" * 70)
print("DECISION NEEDED:")
print("=" * 70)
print("""
Option A: Keep current (716 concrete only) - Pure ML approach
Option B: Restore templates (756 total) - Hybrid ML + Templates

For a test automation system, Option B is recommended.

Should I restore the 40 template entries?
""")
