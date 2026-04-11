"""Test generator directly to see if tracing works."""
import sys
sys.path.insert(0, 'src/main/python')

from core.inference_improved import ImprovedSeleniumGenerator

print("Creating generator...")
gen = ImprovedSeleniumGenerator()

print("\nTesting prompt: 'click login button'")
print("Calling generate_clean()...\n")

code = gen.generate_clean(
    prompt="click login button",
    language="java",
    comprehensive_mode=True,
    ignore_fallbacks=True
)

print(f"\nGenerated code (first 200 chars):")
print(code[:200])

print("\nGetting alternatives...")
alternatives = gen.get_last_alternatives()

print(f"\nAlternatives ({len(alternatives)}):")
for i, alt in enumerate(alternatives, 1):
    score = alt.get('score', 0)
    prompt_text = alt.get('prompt', 'N/A')
    category = alt.get('category', 'N/A')
    print(f"  {i}. [{score:.1%}] {prompt_text} (category: {category})")

# Check if trace log was created
import os
if os.path.exists('dataset_matcher_trace.log'):
    print("\n✅ Trace log file was created!")
    with open('dataset_matcher_trace.log', 'r',encoding='utf-8') as f:
        content = f.read()
        print(f"Trace log size: {len(content)} bytes")
        print(f"First 500 chars:\n{content[:500]}")
else:
    print("\n❌ Trace log file was NOT created!")
