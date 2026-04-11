"""
Create fine-tuning dataset for OpenAI/Anthropic APIs
Converts Page Helper training data to various AI provider formats
"""

import json
from pathlib import Path
from typing import List, Dict

def load_training_data():
    """Load Page Helper training dataset."""
    training_path = Path('resources/ml_data/datasets/page-helper-training-dataset.json')
    
    with open(training_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} training examples")
    return data

def create_openai_format(training_data: List[Dict]) -> List[Dict]:
    """Convert to OpenAI fine-tuning format (JSONL)."""
    
    system_message = (
        "You are an expert Selenium test automation developer. "
        "Convert natural language test instructions into Java code using Page Helper methods. "
        "Use high-level Page Helper methods that find elements by their visible labels, not technical IDs. "
        "Always use methods like setInputFieldValue(), setDropdownValue(), clickButton(), etc."
    )
    
    openai_examples = []
    
    for example in training_data:
        # Create message format
        messages = [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": example['input']
            },
            {
                "role": "assistant",
                "content": example['output']
            }
        ]
        
        openai_examples.append({"messages": messages})
    
    return openai_examples

def create_anthropic_format(training_data: List[Dict]) -> List[Dict]:
    """Convert to format for Anthropic Claude prompting."""
    
    system_prompt = (
        "You are an expert Selenium test automation developer. "
        "Convert natural language test instructions into Java code using Page Helper methods."
    )
    
    anthropic_examples = []
    
    for example in training_data:
        # Claude format for few-shot learning
        anthropic_examples.append({
            "system": system_prompt,
            "human": example['input'],
            "assistant": example['output'],
            "metadata": {
                "category": example.get('category', ''),
                "difficulty": example.get('difficulty', ''),
                "id": example.get('id', '')
            }
        })
    
    return anthropic_examples

def create_few_shot_examples(training_data: List[Dict], n_examples: int = 10) -> str:
    """Create few-shot prompt examples for in-context learning."""
    
    # Select diverse examples across categories
    categories_seen = set()
    selected = []
    
    for example in training_data:
        category = example.get('category', '')
        if category not in categories_seen and len(selected) < n_examples:
            selected.append(example)
            categories_seen.add(category)
    
    # Build few-shot prompt
    prompt = "Here are examples of converting test instructions to Page Helper code:\n\n"
    
    for i, example in enumerate(selected, 1):
        prompt += f"Example {i}:\n"
        prompt += f"Instruction: {example['input']}\n"
        prompt += f"Code: {example['output']}\n\n"
    
    prompt += "Now convert this instruction:\n"
    
    return prompt

def save_openai_format(data: List[Dict], output_path: str = 'page-helper-openai-finetuning.jsonl'):
    """Save in OpenAI JSONL format (one JSON object per line)."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✓ Saved OpenAI format to: {output_path}")
    print(f"  Format: JSONL (one JSON per line)")
    print(f"  Examples: {len(data)}")
    
    return output_path

def save_anthropic_format(data: List[Dict], output_path: str = 'page-helper-anthropic-examples.json'):
    """Save in Anthropic Claude format."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved Anthropic format to: {output_path}")
    print(f"  Format: JSON with human/assistant pairs")
    print(f"  Examples: {len(data)}")
    
    return output_path

def save_few_shot_prompt(prompt: str, output_path: str = 'page-helper-few-shot-prompt.txt'):
    """Save few-shot prompt template."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"✓ Saved few-shot prompt to: {output_path}")
    print(f"  Use this as a prompt prefix for better results")
    
    return output_path

def create_validation_split(training_data: List[Dict], val_ratio: float = 0.2):
    """Split data into training and validation sets."""
    
    import random
    random.seed(42)
    
    # Shuffle data
    shuffled = training_data.copy()
    random.shuffle(shuffled)
    
    # Split
    split_idx = int(len(shuffled) * (1 - val_ratio))
    train_data = shuffled[:split_idx]
    val_data = shuffled[split_idx:]
    
    print(f"✓ Split dataset:")
    print(f"  Training: {len(train_data)} examples")
    print(f"  Validation: {len(val_data)} examples")
    
    return train_data, val_data

def generate_openai_commands(jsonl_file: str):
    """Generate OpenAI CLI commands for fine-tuning."""
    
    commands = f"""
    
🤖 OpenAI Fine-Tuning Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Install OpenAI CLI (if not already installed):
   pip install --upgrade openai

2. Set your API key:
   $env:OPENAI_API_KEY = "sk-your-key-here"

3. Upload training file:
   openai files create --file {jsonl_file} --purpose fine-tune

4. Create fine-tuning job (use file-id from step 3):
   openai fine-tuning create --model gpt-4o-mini --file file-abc123xyz

5. Monitor progress:
   openai fine-tuning list
   openai fine-tuning retrieve <job-id>

6. Use fine-tuned model:
   # In your code, use the fine-tuned model name
   # Example: ft:gpt-4o-mini:your-org:page-helper:abc123

Cost Estimate:
  • Training: ~$0.008 per 1K tokens
  • 70 examples ≈ 35K tokens = ~$0.28
  • Inference: Standard API rates + small fine-tune premium

Recommended Settings:
  • Model: gpt-4o-mini (best cost/performance)
  • Epochs: 3 (default is good)
  • Batch size: auto

Expected Training Time: 10-30 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    
    return commands

def main():
    """Main execution."""
    
    print("=" * 60)
    print("🤖 AI Fine-Tuning Data Generator")
    print("=" * 60)
    print()
    
    # Load data
    print("📂 Loading training data...")
    training_data = load_training_data()
    print()
    
    # Split into train/val
    print("✂️ Creating train/validation split...")
    train_data, val_data = create_validation_split(training_data, val_ratio=0.15)
    print()
    
    # Create OpenAI format
    print("🔄 Converting to OpenAI format...")
    openai_train = create_openai_format(train_data)
    openai_val = create_openai_format(val_data)
    
    openai_train_path = save_openai_format(openai_train, 'page-helper-openai-train.jsonl')
    openai_val_path = save_openai_format(openai_val, 'page-helper-openai-val.jsonl')
    print()
    
    # Create Anthropic format
    print("🔄 Converting to Anthropic format...")
    anthropic_data = create_anthropic_format(training_data)
    anthropic_path = save_anthropic_format(anthropic_data)
    print()
    
    # Create few-shot prompt
    print("📝 Creating few-shot prompt template...")
    few_shot_prompt = create_few_shot_examples(training_data, n_examples=10)
    few_shot_path = save_few_shot_prompt(few_shot_prompt)
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Fine-Tuning Data Created!")
    print("=" * 60)
    print()
    print("📁 Files Created:")
    print(f"  • {openai_train_path} (training)")
    print(f"  • {openai_val_path} (validation)")
    print(f"  • {anthropic_path}")
    print(f"  • {few_shot_path}")
    print()
    
    # OpenAI Guide
    print(generate_openai_commands(openai_train_path))
    print()
    
    print("📚 Usage Options:")
    print()
    print("1️⃣ OpenAI Fine-Tuning (Recommended for Production)")
    print("   → Follow commands above")
    print("   → Best accuracy, costs ~$0.30 + usage")
    print()
    print("2️⃣ Anthropic Claude (Few-Shot)")
    print("   → Use anthropic_path for few-shot prompting")
    print("   → No fine-tuning yet, use examples in prompt")
    print()
    print("3️⃣ Local Model (Free)")
    print("   → Run: python src/main/python/integrate_page_helper_datasets.py")
    print("   → Good for development, no API costs")
    print()

if __name__ == '__main__':
    main()
