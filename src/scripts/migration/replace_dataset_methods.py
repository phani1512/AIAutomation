"""Replace dataset and PageHelper methods with delegations"""
import re

with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:
    content = f.read()

original_lines = len(content.split('\n'))
print(f"📊 Original: {original_lines} lines")

# Replace _normalize_with_synonyms
pattern1 = re.compile(
    r'(\n    def _normalize_with_synonyms\(self, text: str\) -> str:)'
    r'(.*?)'
    r'(\n    def _find_dataset_match)',
    re.DOTALL
)
content, count1 = pattern1.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher.normalize_with_synonyms(text)\n\3',
    content
)
if count1:
    print(f"✅ Replaced _normalize_with_synonyms")

# Replace _find_dataset_match
pattern2 = re.compile(
    r'(\n    def _find_dataset_match\(self, prompt: str, return_alternatives: bool = True\):)'
    r'(.*?)'
    r'(\n    def _is_template)',
    re.DOTALL
)
content, count2 = pattern2.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher.find_dataset_match(prompt, return_alternatives)\n\3',
    content
)
if count2:
    print(f"✅ Replaced _find_dataset_match")

# Replace _is_template
pattern3 = re.compile(
    r'(\n    def _is_template\(self, entry: dict\) -> bool:)'
    r'(.*?)'
    r'(\n    def get_last_alternatives)',
    re.DOTALL
)
content, count3 = pattern3.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher._is_template(entry)\n\3',
    content
)
if count3:
    print(f"✅ Replaced _is_template")

# Replace get_last_alternatives
pattern4 = re.compile(
    r'(\n    def get_last_alternatives\(self\).*?:)'
    r'(.*?)'
    r'(\n    def _find_pagehelper_match)',
    re.DOTALL
)
content, count4 = pattern4.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher.get_last_alternatives()\n\3',
    content
)
if count4:
    print(f"✅ Replaced get_last_alternatives")

# Replace _find_pagehelper_match
pattern5 = re.compile(
    r'(\n    def _find_pagehelper_match\(self, prompt: str\):)'
    r'(.*?)'
    r'(\n    def _generate_from_pagehelper)',
    re.DOTALL
)
content, count5 = pattern5.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher.find_pagehelper_match(prompt)\n\3',
    content
)
if count5:
    print(f"✅ Replaced _find_pagehelper_match")

# Replace _generate_from_pagehelper
pattern6 = re.compile(
    r'(\n    def _generate_from_pagehelper\(self, prompt: str, pagehelper_match: dict, language: str, comprehensive_mode: bool\) -> str:)'
    r'(.*?)'
    r'(\n    def _extract_pagehelper_params)',
    re.DOTALL
)
content, count6 = pattern6.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        preserve_placeholder = getattr(self, \'_preserve_data_placeholder\', False)\n        return self.dataset_matcher.generate_from_pagehelper(prompt, pagehelper_match, language, comprehensive_mode, preserve_placeholder)\n\3',
    content
)
if count6:
    print(f"✅ Replaced _generate_from_pagehelper")

# Replace _extract_pagehelper_params
pattern7 = re.compile(
    r'(\n    def _extract_pagehelper_params\(self, prompt: str, pagehelper_match: dict\) -> dict:)'
    r'(.*?)'
    r'(\n    def _handle_universal_input_pattern)',
    re.DOTALL
)
content, count7 = pattern7.subn(
    r'\1\n        """REFACTORED: Now delegates to dataset_matcher module."""\n        return self.dataset_matcher.extract_pagehelper_params(prompt, pagehelper_match)\n\3',
    content
)
if count7:
    print(f"✅ Replaced _extract_pagehelper_params")

# Write back
with open('src/main/python/inference_improved.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

new_lines = len(content.split('\n'))
removed = original_lines - new_lines

print(f"\n📊 Result: {new_lines} lines")
print(f"🎯 Removed: {removed} lines")
print(f"✅ Total reduction from start: {2822 - new_lines} lines ({(2822-new_lines)/2822*100:.1f}%)")
