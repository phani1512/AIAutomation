"""Replace universal pattern methods with delegations"""
import re

with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original: {len(content.split(chr(10)))} lines")

# Replace _handle_universal_input_pattern with delegation
pattern1 = re.compile(
    r'(\n    def _handle_universal_input_pattern\(self, prompt: str, language: str, comprehensive_mode: bool\) -> str:)'
    r'(.*?)'
    r'(\n    def _generate_field_selectors)',
    re.DOTALL
)

delegation1 = r'''\1
        """REFACTORED: Now delegates to universal_patterns module."""
        preserve_placeholder = getattr(self, '_preserve_data_placeholder', False)
        return self.universal_handler.handle_universal_input_pattern(
            prompt, language, comprehensive_mode, preserve_placeholder
        )
\3'''

content, count1 = pattern1.subn(delegation1, content)
if count1:
    print(f"✅ Replaced _handle_universal_input_pattern (~91 lines)")

# Remove the 4 _generate_*_with_fallbacks methods
# They come after _generate_field_selectors and before _generate_code_with_fallbacks
pattern2 = re.compile(
    r'(\n    def _generate_field_selectors.*?return self\.locator_utils\.generate_field_selectors\(field_name\))'
    r'(\n    \n    def _generate_python_with_fallbacks.*?)'
    r'(def _generate_code_with_fallbacks)',
    re.DOTALL
)

delegation2 = r'''\1
\3'''

content, count2 = pattern2.subn(delegation2, content)
if count2:
    print(f"✅ Removed 4 _generate_*_with_fallbacks methods (~120 lines)")

# Write back
with open('src/main/python/inference_improved.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

new_lines = len(content.split('\n'))
print(f"\n📊 Result: {new_lines} lines")
print(f"🎯 Removed: ~{211} lines")
