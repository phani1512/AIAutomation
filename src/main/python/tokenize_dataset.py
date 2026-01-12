"""
Tokenize Selenium datasets using sub-word tokenizer and save to binary file.
This script processes all JSON datasets and creates a single .bin file with token IDs.
"""

import json
import struct
import os
from pathlib import Path
from typing import List, Dict, Any
import tiktoken

class DatasetTokenizer:
    def __init__(self, datasets_dir: str = "src/resources"):
        self.datasets_dir = datasets_dir
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        self.all_tokens = []
        self.dataset_metadata = {}  # Track tokens per dataset for analysis
        
    def load_json_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Load JSON dataset file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_jsonl_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Load JSONL dataset file (line-delimited JSON)."""
        data = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Skipping invalid JSON at line {line_num}: {e}")
                    continue
        return data
    
    def serialize_to_text(self, data: Any, prefix: str = "") -> str:
        """Convert JSON data to structured text format for tokenization."""
        text_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    text_parts.append(f"{prefix}{key}:")
                    text_parts.append(self.serialize_to_text(value, prefix + "  "))
                else:
                    text_parts.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    text_parts.append(f"{prefix}[{i}]")
                    text_parts.append(self.serialize_to_text(item, prefix + "  "))
                else:
                    text_parts.append(f"{prefix}- {item}")
        else:
            text_parts.append(f"{prefix}{data}")
        
        return "\n".join(text_parts)
    
    def tokenize_dataset(self, dataset: List[Dict[str, Any]]) -> List[int]:
        """Tokenize entire dataset and return token IDs."""
        tokens = []
        
        for entry in dataset:
            # Convert entry to text representation
            text = self.serialize_to_text(entry)
            
            # Add separator tokens
            text = f"\n<|entry_start|>\n{text}\n<|entry_end|>\n"
            
            # Tokenize
            entry_tokens = self.tokenizer.encode(text)
            tokens.extend(entry_tokens)
        
        return tokens
    
    def process_all_datasets(self):
        """Process all JSON and JSONL datasets in the resources directory."""
        dataset_configs = [
            {
                "filename": "selenium-methods-dataset.json",
                "type": "json",
                "weight": 1.0,  # Standard weight
                "description": "Selenium WebDriver API methods and signatures"
            },
            {
                "filename": "common-web-actions-dataset.json",
                "type": "json",
                "weight": 1.5,  # Higher weight - frequently used patterns
                "description": "Generic web UI action patterns"
            },
            {
                "filename": "element-locator-patterns.json",
                "type": "json",
                "weight": 1.2,  # Medium weight - locator strategy learning
                "description": "HTML element locator strategy examples"
            },
            {
                "filename": "sircon_ui_dataset.json",
                "type": "json",
                "weight": 2.0,  # Highest weight - real application patterns
                "description": "Sircon application-specific UI patterns"
            }
        ]
        
        print("Starting dataset tokenization...")
        print("=" * 60)
        
        for config in dataset_configs:
            filepath = os.path.join(self.datasets_dir, config["filename"])
            
            if not os.path.exists(filepath):
                print(f"⚠️  Warning: {config['filename']} not found, skipping...")
                continue
            
            print(f"\n📄 Processing: {config['filename']}")
            print(f"   Type: {config['type'].upper()}")
            print(f"   Description: {config['description']}")
            print(f"   Weight: {config['weight']}x")
            
            # Load dataset based on type
            if config["type"] == "json":
                dataset = self.load_json_file(filepath)
            elif config["type"] == "jsonl":
                dataset = self.load_jsonl_file(filepath)
            else:
                print(f"❌ Unknown dataset type: {config['type']}")
                continue
            
            print(f"   Loaded {len(dataset)} entries")
            
            # Tokenize
            tokens = self.tokenize_dataset(dataset)
            base_token_count = len(tokens)
            print(f"   Generated {base_token_count:,} tokens")
            
            # Track metadata
            self.dataset_metadata[config['filename']] = {
                'entries': len(dataset),
                'base_tokens': base_token_count,
                'weight': config['weight'],
                'description': config['description']
            }
            
            # Add to global token list
            self.all_tokens.extend(tokens)
            
            # Apply weight by duplicating tokens
            if config["weight"] > 1.0:
                duplicate_count = int(config["weight"]) - 1
                for _ in range(duplicate_count):
                    self.all_tokens.extend(tokens)
                weighted_count = base_token_count * config['weight']
                self.dataset_metadata[config['filename']]['weighted_tokens'] = int(weighted_count)
                print(f"   Applied {config['weight']}x weight: {int(weighted_count):,} tokens total")
            else:
                self.dataset_metadata[config['filename']]['weighted_tokens'] = base_token_count
        
        print("\n" + "=" * 60)
        print(f"✅ Total tokens across all datasets: {len(self.all_tokens):,}")
        
    def save_to_bin(self, output_file: str = "selenium_dataset.bin"):
        """Save all token IDs to a binary file."""
        output_path = os.path.join(self.datasets_dir, output_file)
        
        print(f"\n💾 Saving tokens to: {output_path}")
        
        with open(output_path, 'wb') as f:
            # Write header: number of tokens (8 bytes)
            f.write(struct.pack('Q', len(self.all_tokens)))
            
            # Write all token IDs (4 bytes each as unsigned int)
            for token_id in self.all_tokens:
                f.write(struct.pack('I', token_id))
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Binary file created successfully!")
        print(f"   File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        print(f"   Token count: {len(self.all_tokens):,}")
        
    def generate_statistics(self):
        """Generate statistics about the tokenized dataset."""
        if not self.all_tokens:
            print("⚠️  No tokens to analyze")
            return
        
        print("\n" + "=" * 60)
        print("📊 TOKENIZATION STATISTICS")
        print("=" * 60)
        
        # Dataset breakdown
        print("\n📚 Dataset Breakdown:")
        print("-" * 60)
        total_weighted = 0
        for filename, metadata in self.dataset_metadata.items():
            weighted = metadata.get('weighted_tokens', metadata['base_tokens'])
            total_weighted += weighted
            percentage = (weighted / len(self.all_tokens)) * 100 if self.all_tokens else 0
            print(f"\n{filename}:")
            print(f"  Entries: {metadata['entries']}")
            print(f"  Base tokens: {metadata['base_tokens']:,}")
            print(f"  Weight: {metadata['weight']}x")
            print(f"  Weighted tokens: {weighted:,}")
            print(f"  Percentage of corpus: {percentage:.1f}%")
            print(f"  Description: {metadata['description']}")
        
        # Vocabulary statistics
        print("\n" + "-" * 60)
        print("\n📖 Vocabulary Statistics:")
        unique_tokens = set(self.all_tokens)
        print(f"  Total tokens:        {len(self.all_tokens):,}")
        print(f"  Unique tokens:       {len(unique_tokens):,}")
        print(f"  Vocabulary usage:    {len(unique_tokens) / 100000 * 100:.2f}% of cl100k_base")
        
        # Token frequency
        from collections import Counter
        token_freq = Counter(self.all_tokens)
        most_common = token_freq.most_common(10)
        
        print(f"\n  Most frequent tokens:")
        for token_id, count in most_common:
            try:
                decoded = self.tokenizer.decode([token_id])
                print(f"   Token {token_id:6d}: {count:6,} times - '{decoded}'")
            except:
                print(f"   Token {token_id:6d}: {count:6,} times")
        
        print("=" * 60)
    
    def load_from_bin(self, input_file: str = "selenium_dataset.bin") -> List[int]:
        """Load token IDs from binary file (for verification)."""
        input_path = os.path.join(self.datasets_dir, input_file)
        
        print(f"\n📂 Loading tokens from: {input_path}")
        
        with open(input_path, 'rb') as f:
            # Read header: number of tokens
            num_tokens = struct.unpack('Q', f.read(8))[0]
            print(f"   Expected tokens: {num_tokens:,}")
            
            # Read all token IDs
            tokens = []
            for _ in range(num_tokens):
                token_id = struct.unpack('I', f.read(4))[0]
                tokens.append(token_id)
        
        print(f"✅ Loaded {len(tokens):,} tokens")
        return tokens
    
    def verify_binary_file(self, bin_file: str = "selenium_dataset.bin"):
        """Verify the binary file can be loaded correctly."""
        print("\n" + "=" * 60)
        print("🔍 VERIFYING BINARY FILE")
        print("=" * 60)
        
        loaded_tokens = self.load_from_bin(bin_file)
        
        if loaded_tokens == self.all_tokens:
            print("✅ Verification successful! Binary file matches original tokens.")
        else:
            print("❌ Verification failed! Token mismatch.")
            print(f"   Original: {len(self.all_tokens):,} tokens")
            print(f"   Loaded:   {len(loaded_tokens):,} tokens")

def main():
    """Main execution function."""
    print("🚀 Selenium Dataset Tokenizer")
    print("=" * 60)
    
    # Initialize tokenizer
    tokenizer = DatasetTokenizer()
    
    # Process all datasets
    tokenizer.process_all_datasets()
    
    # Generate statistics
    tokenizer.generate_statistics()
    
    # Save to binary file
    tokenizer.save_to_bin("selenium_dataset.bin")
    
    # Verify the binary file
    tokenizer.verify_binary_file("selenium_dataset.bin")
    
    print("\n✨ Tokenization complete!")

if __name__ == "__main__":
    main()
