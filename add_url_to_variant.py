"""
Add driver.get(URL) to the beginning of each prompt's generated_code for ALL semantic variants.
"""
import json
import glob
import os

# URL to add
url = "https://www.sircontest.non-prod.sircon.com/login.jsp"

# Find all variant JSON files
variant_files = glob.glob("test_suites/**/builder/*variant*.json", recursive=True)

print(f"Found {len(variant_files)} variant files:")
for f in variant_files:
    print(f"  - {f}")
print()

# Find all variant JSON files
variant_files = glob.glob("test_suites/**/builder/*variant*.json", recursive=True)

print(f"Found {len(variant_files)} variant files:")
for f in variant_files:
    print(f"  - {f}")
print()

# Process each variant file
for file_path in variant_files:
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(file_path)}")
    print('='*60)
    
    # Read the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Test: {data['name']}")
    print(f"URL in data: {data.get('url', 'NOT FOUND')}")
    print(f"Prompts: {len(data.get('prompts', []))}")

    # Skip if no prompts
    if 'prompts' not in data or len(data['prompts']) == 0:
        print("⚠️  No prompts found, skipping")
        continue

    # Add driver.get() to the beginning of each prompt's generated_code
    url_line = f'driver.get("{url}")\n\n'
    updated_count = 0

    for i, prompt in enumerate(data['prompts']):
        if 'generated_code' in prompt:
            old_code = prompt['generated_code']
            
            # Check if driver.get() is already there
            if 'driver.get(' not in old_code:
                # Add header comment and driver.get()
                header = f"# Execution-ready code (no pytest fixtures)\n# Test: {data['name']}\n# Test ID: {data['test_case_id']}\n# URL: {url}\n\n"
                new_code = header + url_line + old_code
                prompt['generated_code'] = new_code
                print(f"  Prompt {i+1}: ✓ Added driver.get()")
                updated_count += 1
            else:
                print(f"  Prompt {i+1}: Already has driver.get()")
        else:
            print(f"  Prompt {i+1}: ❌ No generated_code field")

    # Save the updated JSON if changes were made
    if updated_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Updated {updated_count} prompts in {os.path.basename(file_path)}")
        
        # Verify
        with open(file_path, 'r', encoding='utf-8') as f:
            verify_data = json.load(f)
            first_code = verify_data['prompts'][0]['generated_code']
            print(f"\nFirst 200 chars of prompt 1 code:")
            print(first_code[:200])
    else:
        print(f"\n⏭️  No changes needed for {os.path.basename(file_path)}")

print(f"\n{'='*60}")
print("🎉 All variant files processed!")
print('='*60)
