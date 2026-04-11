import json

with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print("=" * 70)
print("FINAL DATASET SUMMARY")
print("=" * 70)

print(f"\n📊 Total entries: {len(dataset)}")

# Quick checks
issues = {
    'empty': 0,
    'broken': 0,
    'conditional': 0,
    'placeholders': 0,
    'clean': 0
}

import re

placeholder_patterns = [r'\{[A-Z_a-z]+\}', r'<[a-z-]+>']

for entry in dataset:
    code = entry.get('code', '')
    
    if not code:
        issues['empty'] += 1
    elif len(code) < 50:
        issues['broken'] += 1
    elif any(kw in code for kw in ['if (', 'while (', 'for (', 'boolean ']):
        issues['conditional'] += 1
    elif any(re.search(p, code) for p in placeholder_patterns):
        issues['placeholders'] += 1
    else:
        issues['clean'] += 1

print("\n✅ QUALITY BREAKDOWN:")
print(f"   Clean entries: {issues['clean']}")
print(f"   Conditional logic: {issues['conditional']}")
print(f"   Placeholders: {issues['placeholders']}")
print(f"   Broken/Empty: {issues['broken'] + issues['empty']}")

print("\n" + "=" * 70)
quality_pct = (issues['clean'] / len(dataset) * 100)
print(f"QUALITY SCORE: {quality_pct:.1f}% clean")
print("=" * 70)

# Sample some entries
clicks = [e for e in dataset if 'click' in e.get('prompt', '').lower() and '.click()' in e.get('code', '')]
inputs = [e for e in dataset if any(kw in e.get('prompt', '').lower() for kw in ['enter', 'input', 'type']) and '.sendKeys(' in e.get('code', '')]

print(f"\n📋 CONTENT SUMMARY:")
print(f"   Click actions: {len(clicks)}")
print(f"   Input actions: {len(inputs)}")
print(f"   Other actions: {len(dataset) - len(clicks) - len(inputs)}")

if issues['placeholders'] == 0:
    print("\n✅ NO PLACEHOLDERS - All concrete examples!")
if issues['conditional'] == 0:
    print("✅ NO CONDITIONAL LOGIC - All simple actions!")
if issues['broken'] + issues['empty'] == 0:
    print("✅ NO BROKEN CODE - All valid!")

if quality_pct == 100:
    print("\n" + "=" * 70)
    print("🎉 PERFECT! 100% CLEAN PRODUCTION-READY DATASET! 🎉")
    print("=" * 70)
