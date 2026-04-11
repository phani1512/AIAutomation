"""
Aggressive cleanup script - Remove all legacy methods from inference_improved.py
"""
import re

def remove_legacy_methods():
    with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:content = f.read()
    
    original_lines = len(content.split('\n'))
    print(f"📊 Original file: {original_lines:,} lines")
    
    # Find and remove _convert_code_to_language_legacy
    pattern1 = re.compile(
        r'(\n    def _convert_code_to_language_legacy\(.*?\n)(.+?)(\n    def _java_to_python_by\()',
        re.DOTALL
    )
    content, count1 = pattern1.subn(r'\3', content)
    if count1:
        print(f"✅ Removed _convert_code_to_language_legacy() - {count1} occurrence(s)")
    
    # Find and remove suggest_locator_from_html_legacy
    pattern2 = re.compile(
        r'(\n    def suggest_locator_from_html_legacy\(.*?\n)(.+?)(\n    def suggest_action\()',
        re.DOTALL
    )
    content, count2 = pattern2.subn(r'\3', content)
    if count2:
        print(f"✅ Removed suggest_locator_from_html_legacy() - {count2} occurrence(s)")
    
    # Find and remove suggest_action_legacy
    pattern3 = re.compile(
        r'(\n    def suggest_action_legacy\(.*?\n)(.+?)(\n    def suggest_locator\()',
        re.DOTALL
    )
    content, count3 = pattern3.subn(r'\3', content)
    if count3:
        print(f"✅ Removed suggest_action_legacy() - {count3} occurrence(s)")
    
    # Find and remove suggest_locator_legacy
    pattern4 = re.compile(
        r'(\n    def suggest_locator_legacy\(.*?\n)(.+?)(\n    def generate_test_method\()',
        re.DOTALL
    )
    content, count4 = pattern4.subn(r'\3', content)
    if count4:
        print(f"✅ Removed suggest_locator_legacy() - {count4} occurrence(s)")
    
    # Write back
    with open('src/main/python/inference_improved.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_lines = len(content.split('\n'))
    removed = original_lines - new_lines
    print(f"\n📊 New file: {new_lines:,} lines")
    print(f"🎯 Removed: {removed:,} lines ({removed/original_lines*100:.1f}%)")
    print(f"\n{'SUCCESS!' if removed > 400 else 'WARNING: Less than expected'}")

if __name__ == '__main__':
    remove_legacy_methods()
