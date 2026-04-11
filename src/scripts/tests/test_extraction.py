import sys
sys.path.insert(0, 'src/main/python')
from template_parameter_extractor import TemplateParameterExtractor

extractor = TemplateParameterExtractor()

# Test both prompts
prompts = [
    'click Carrier Account 2 button',
    'click Beneficiaries button'  
]

for prompt in prompts:
    result = extractor.extract_parameter(prompt, '')
    print(f'\nPrompt: "{prompt}"')
    if result:
        print(f'  ✅ Extracted successfully')
        print(f'     Placeholder: {result.get("placeholder")}')
        print(f'     Value: {result.get("value")}')
    else:
        print(f'  ❌ No extraction (not matching any pattern)')
