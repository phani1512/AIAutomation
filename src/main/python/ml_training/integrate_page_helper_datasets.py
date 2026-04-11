"""
Integration script to prepare Page Helper datasets for training
Converts the new datasets to the format used by your existing training pipeline
"""

import json
import os
from pathlib import Path

def load_page_helper_datasets():
    """Load both Page Helper datasets."""
    base_path = Path('resources/ml_data/datasets')
    
    # Load patterns dataset
    with open(base_path / 'page-helper-patterns-dataset.json', 'r', encoding='utf-8') as f:
        patterns = json.load(f)
    
    # Load training dataset
    with open(base_path / 'page-helper-training-dataset.json', 'r', encoding='utf-8') as f:
        training = json.load(f)
    
    print(f"✓ Loaded {len(patterns)} patterns")
    print(f"✓ Loaded {len(training)} training examples")
    
    return patterns, training

def convert_to_training_format(patterns, training_examples):
    """
    Convert Page Helper datasets to format compatible with existing training pipeline.
    Creates entries similar to your existing dataset format.
    """
    converted_data = []
    
    # Convert training examples
    for example in training_examples:
        # Create a training entry
        entry = {
            "action": example.get('instruction', ''),
            "description": f"{example.get('category', 'page_helper')}: {example.get('instruction', '')}",
            "steps": [{
                "step": 1,
                "action": example.get('category', 'code_generation'),
                "code": example.get('output', ''),
                "prompt": example.get('input', ''),
                "pattern_type": example.get('method_pattern', 'page_helper'),
                "difficulty": example.get('difficulty', 'medium')
            }]
        }
        converted_data.append(entry)
    
    # Add pattern variations
    for pattern in patterns:
        for prompt_variation in pattern.get('prompt_variations', []):
            entry = {
                "action": pattern.get('method_name', ''),
                "description": pattern.get('description', ''),
                "steps": [{
                    "step": 1,
                    "action": pattern.get('category', ''),
                    "code": pattern.get('code_template', ''),
                    "prompt": prompt_variation,
                    "pattern_type": "page_helper_pattern",
                    "xpath": pattern.get('xpath_pattern', '')
                }]
            }
            converted_data.append(entry)
    
    print(f"✓ Converted {len(converted_data)} total training entries")
    return converted_data

def merge_with_existing_dataset(new_data, existing_dataset_path='resources/ml_data/datasets/common-web-actions-dataset.json'):
    """Merge new Page Helper data with existing dataset."""
    
    if not os.path.exists(existing_dataset_path):
        print(f"⚠ Existing dataset not found at {existing_dataset_path}")
        print("  Creating new combined dataset...")
        existing_data = []
    else:
        with open(existing_dataset_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"✓ Loaded {len(existing_data)} existing entries")
    
    # Merge datasets
    combined = existing_data + new_data
    
    # Save combined dataset
    output_path = 'resources/ml_data/datasets/combined-training-dataset.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved combined dataset to {output_path}")
    print(f"  Total entries: {len(combined)}")
    return output_path

def create_page_helper_prompts_file():
    """Create a prompts file specifically for Page Helper patterns."""
    
    patterns_path = Path('resources/ml_data/datasets/page-helper-patterns-dataset.json')
    with open(patterns_path, 'r', encoding='utf-8') as f:
        patterns = json.load(f)
    
    prompts = []
    
    for pattern in patterns:
        # Add all prompt variations
        for variation in pattern.get('prompt_variations', []):
            prompts.append({
                'prompt': variation,
                'expected_method': pattern.get('method_name', ''),
                'code_template': pattern.get('code_template', ''),
                'category': pattern.get('category', '')
            })
    
    output_path = 'resources/ml_data/datasets/page-helper-prompts.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Created {output_path} with {len(prompts)} prompts")
    return output_path

def generate_training_statistics(patterns, training_examples):
    """Generate statistics about the training data."""
    
    stats = {
        'total_patterns': len(patterns),
        'total_training_examples': len(training_examples),
        'categories': {},
        'difficulty_distribution': {},
        'prompt_variations': sum(len(p.get('prompt_variations', [])) for p in patterns)
    }
    
    # Count by category
    for example in training_examples:
        cat = example.get('category', 'unknown')
        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
        
        diff = example.get('difficulty', 'medium')
        stats['difficulty_distribution'][diff] = stats['difficulty_distribution'].get(diff, 0) + 1
    
    return stats

def main():
    """Main integration process."""
    
    print("=" * 60)
    print("🚀 Page Helper Dataset Integration")
    print("=" * 60)
    print()
    
    # Step 1: Load datasets
    print("📂 Step 1: Loading Page Helper datasets...")
    patterns, training = load_page_helper_datasets()
    print()
    
    # Step 2: Generate statistics
    print("📊 Step 2: Analyzing datasets...")
    stats = generate_training_statistics(patterns, training)
    print(f"  • Total patterns: {stats['total_patterns']}")
    print(f"  • Training examples: {stats['total_training_examples']}")
    print(f"  • Prompt variations: {stats['prompt_variations']}")
    print(f"  • Categories: {len(stats['categories'])}")
    print()
    
    # Step 3: Convert to training format
    print("🔄 Step 3: Converting to training format...")
    converted_data = convert_to_training_format(patterns, training)
    print()
    
    # Step 4: Merge with existing
    print("🔗 Step 4: Merging with existing dataset...")
    combined_path = merge_with_existing_dataset(converted_data)
    print()
    
    # Step 5: Create prompts file
    print("📝 Step 5: Creating Page Helper prompts file...")
    prompts_path = create_page_helper_prompts_file()
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Integration Complete!")
    print("=" * 60)
    print()
    print("📁 Files Created:")
    print(f"  • {combined_path}")
    print(f"  • {prompts_path}")
    print()
    print("🎯 Next Steps:")
    print("  1. Review the combined dataset")
    print("  2. Run: python src/main/python/tokenize_dataset.py")
    print("  3. Run: python src/main/python/train_simple.py")
    print("  4. Restart your API server")
    print()
    print("📊 Training Statistics:")
    print(f"  • Difficulty - Easy: {stats['difficulty_distribution'].get('easy', 0)}")
    print(f"  • Difficulty - Medium: {stats['difficulty_distribution'].get('medium', 0)}")
    print(f"  • Difficulty - Hard: {stats['difficulty_distribution'].get('hard', 0)}")
    print(f"  • Difficulty - Expert: {stats['difficulty_distribution'].get('expert', 0)}")
    print()

if __name__ == '__main__':
    main()
