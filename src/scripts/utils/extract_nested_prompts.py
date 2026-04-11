"""
Extract prompts from nested structure datasets and add to final dataset.
These files have prompts inside steps arrays.
"""

import json
import os

def extract_nested_prompts():
    """Extract prompts from files with nested step structures."""
    
    print("=" * 100)
    print("EXTRACTING PROMPTS FROM NESTED STRUCTURE DATASETS")
    print("=" * 100)
    
    base_path = 'c:\\Users\\valaboph\\AIAutomation\\src\\resources\\'
    
    # Load final dataset
    final_file = base_path + 'combined-training-dataset-final.json'
    with open(final_file, 'r', encoding='utf-8') as f:
        final_data = json.load(f)
    
    final_prompts = {entry['prompt'].lower().strip() for entry in final_data}
    print(f"\n✓ Current final dataset: {len(final_data)} entries")
    
    # Files with nested structure
    nested_files = [
        'sircon_ui_dataset.json',
        'sircon_ui_dataset_enhanced.json',
        'combined-training-dataset.json',
        'common-web-actions-dataset.json',
    ]
    
    all_new_prompts = []
    
    for filename in nested_files:
        file_path = base_path + filename
        
        if not os.path.exists(file_path):
            continue
        
        print(f"\n{'─' * 100}")
        print(f"Processing: {filename}")
        print(f"{'─' * 100}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            extracted = 0
            unique = 0
            
            # Extract from nested steps
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                
                steps = entry.get('steps', [])
                action = entry.get('action', '')
                description = entry.get('description', '')
                
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    
                    prompt = step.get('prompt', '')
                    if not prompt:
                        continue
                    
                    extracted += 1
                    
                    # Check if already in final dataset
                    if prompt.lower().strip() in final_prompts:
                        continue
                    
                    unique += 1
                    
                    # Create standardized entry
                    new_entry = {
                        'prompt': prompt,
                        'code': step.get('code', ''),
                        'category': step.get('action', action),
                        'xpath': step.get('locator', ''),
                        'description': description,
                        'metadata': {
                            'page_object': step.get('page_object', ''),
                            'method_name': step.get('method_name', ''),
                            'element_type': step.get('element_type', ''),
                            'error_message': step.get('error_message', ''),
                            'source_dataset': filename,
                            'original_action': action
                        }
                    }
                    
                    all_new_prompts.append(new_entry)
                    final_prompts.add(prompt.lower().strip())
            
            print(f"  Total prompts extracted: {extracted}")
            print(f"  Unique new prompts: {unique}")
        
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
    
    # Summary
    print("\n" + "=" * 100)
    print("EXTRACTION SUMMARY")
    print("=" * 100)
    
    print(f"\nNew unique prompts found: {len(all_new_prompts)}")
    
    if all_new_prompts:
        # Show examples
        print("\nSample new prompts:")
        for i, entry in enumerate(all_new_prompts[:5], 1):
            print(f"  {i}. \"{entry['prompt'][:70]}...\"")
            print(f"     Category: {entry['category']}, Source: {entry['metadata']['source_dataset']}")
        
        # Add to final dataset
        final_data.extend(all_new_prompts)
        
        # Sort
        final_data.sort(key=lambda x: (x.get('category', ''), x.get('prompt', '')))
        
        # Save
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Updated final dataset: {len(final_data)} total entries")
        print(f"  File: {final_file}")
        
        # Now these files can be deleted
        print("\n" + "=" * 100)
        print("FILES CAN NOW BE DELETED")
        print("=" * 100)
        
        backup_path = 'c:\\Users\\valaboph\\AIAutomation\\backup_datasets\\'
        
        print(f"\nThe following files have been fully extracted and can be deleted:")
        for filename in nested_files:
            if os.path.exists(base_path + filename):
                size = os.path.getsize(base_path + filename) / 1024
                print(f"  • {filename} ({size:.1f} KB)")
        
        response = input("\nDelete these files? (yes/no): ")
        
        if response.lower() == 'yes':
            import shutil
            
            for filename in nested_files:
                source = base_path + filename
                backup = backup_path + filename
                
                if os.path.exists(source):
                    # Backup
                    shutil.copy2(source, backup)
                    # Delete
                    os.remove(source)
                    print(f"  ✓ Deleted: {filename}")
            
            print(f"\n✅ All nested structure files deleted and backed up")
        else:
            print("\n⊘ Deletion cancelled")
    
    else:
        print("\n✓ No new prompts found - all already included!")
    
    print("\n" + "=" * 100)
    print("FINAL DATASET COMPLETE!")
    print("=" * 100)
    print(f"\n📁 Your complete unified dataset:")
    print(f"   {final_file}")
    print(f"   Total entries: {len(final_data)}")
    print("\n" + "=" * 100)

if __name__ == "__main__":
    extract_nested_prompts()
