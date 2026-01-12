# Dataset Tokenization Guide

This guide explains how to tokenize the Selenium datasets using sub-word tokenization and store the tokens in a binary file.

## Overview

The tokenization process converts all JSON datasets into token IDs using the `cl100k_base` tokenizer (same as GPT-4) and stores them in a single binary file for efficient training.

## Files

- **tokenize_dataset.py** - Main tokenization script
- **requirements.txt** - Python dependencies
- **selenium_dataset.bin** - Output binary file with token IDs (generated)

## Installation

1. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

## Usage

### Basic Tokenization

Run the tokenization script:
```powershell
python tokenize_dataset.py
```

This will:
1. Load all JSON datasets from `src/main/resources/`
2. Convert each entry to structured text format
3. Tokenize using sub-word tokenizer
4. Save all token IDs to `selenium_dataset.bin`
5. Generate statistics and verify the output

### Output

The script generates:
- **selenium_dataset.bin** - Binary file containing all token IDs
  - Header: 8 bytes (unsigned long) - number of tokens
  - Body: N × 4 bytes (unsigned int) - token IDs

## Binary File Format

```
[Header: 8 bytes]  - Number of tokens (uint64)
[Token 1: 4 bytes] - Token ID (uint32)
[Token 2: 4 bytes] - Token ID (uint32)
...
[Token N: 4 bytes] - Token ID (uint32)
```

## Tokenizer Details

- **Algorithm**: Byte Pair Encoding (BPE)
- **Encoding**: cl100k_base (GPT-4 tokenizer)
- **Vocabulary Size**: ~100,000 tokens
- **Special Tokens**: 
  - `<|entry_start|>` - Marks the beginning of each dataset entry
  - `<|entry_end|>` - Marks the end of each dataset entry

## Data Structure

Each JSON entry is converted to structured text before tokenization:

```
<|entry_start|>
category: WebDriverListener_ElementInteraction
method: beforeClick
signature: void beforeClick(WebElement element)
description: Called before clicking an element
example: element.click();
usage_pattern: Click on button, link, or interactive element
parameters:
  - WebElement element
action_type: click
<|entry_end|>
```

## Statistics

After tokenization, the script displays:
- Total number of tokens
- Number of unique tokens
- Vocabulary usage percentage
- Most frequent tokens
- File size information

## Loading Binary File

To load the binary file in your training code:

### Python Example
```python
import struct

def load_tokens(filepath):
    with open(filepath, 'rb') as f:
        # Read number of tokens
        num_tokens = struct.unpack('Q', f.read(8))[0]
        
        # Read all token IDs
        tokens = []
        for _ in range(num_tokens):
            token_id = struct.unpack('I', f.read(4))[0]
            tokens.append(token_id)
    
    return tokens

# Usage
tokens = load_tokens('src/main/resources/selenium_dataset.bin')
```

### Java Example
```java
import java.io.*;
import java.nio.*;
import java.util.*;

public class TokenLoader {
    public static List<Integer> loadTokens(String filepath) throws IOException {
        List<Integer> tokens = new ArrayList<>();
        
        try (DataInputStream dis = new DataInputStream(
                new FileInputStream(filepath))) {
            
            // Read number of tokens (8 bytes, long)
            long numTokens = dis.readLong();
            
            // Read all token IDs (4 bytes each, int)
            for (long i = 0; i < numTokens; i++) {
                int tokenId = dis.readInt();
                tokens.add(tokenId);
            }
        }
        
        return tokens;
    }
}
```

## Customization

### Using a Different Tokenizer

You can modify the tokenizer by changing this line in `tokenize_dataset.py`:

```python
# Current: GPT-4 tokenizer
self.tokenizer = tiktoken.get_encoding("cl100k_base")

# Alternative: GPT-3.5/GPT-3 tokenizer
self.tokenizer = tiktoken.get_encoding("p50k_base")

# Alternative: Use Hugging Face tokenizer
from transformers import AutoTokenizer
self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
```

### Adding Custom Datasets

To include additional JSON files:

```python
dataset_files = [
    "selenium-methods-dataset.json",
    "common-web-actions-dataset.json",
    "element-locator-patterns.json",
    "your-custom-dataset.json"  # Add here
]
```

### Changing Output Location

```python
# Change output file location
tokenizer.save_to_bin("path/to/output/custom_name.bin")
```

## Training Preparation

The binary file is ready for use in:
- Small Language Model (SLM) training
- Fine-tuning existing models
- Transfer learning pipelines
- Custom tokenizer training

### Recommended Next Steps

1. **Split the data** into train/validation/test sets
2. **Create batches** from token sequences
3. **Add padding** or truncation for fixed-length sequences
4. **Implement data loader** for your ML framework

## Performance

Expected performance metrics:
- **Processing Speed**: ~10,000 entries/second
- **Memory Usage**: ~100-200 MB during processing
- **Output Size**: ~4 bytes per token + 8 byte header

## Troubleshooting

### Module Not Found Error
```powershell
pip install tiktoken
```

### File Not Found
Ensure you're running the script from the project root:
```powershell
cd C:\Users\valaboph\WebAutomation
python tokenize_dataset.py
```

### Memory Issues
For very large datasets, consider processing in chunks:
```python
# Modify process_all_datasets() to process files one at a time
# and append to binary file incrementally
```

## Example Output

```
🚀 Selenium Dataset Tokenizer
============================================================

Starting dataset tokenization...
============================================================

📄 Processing: selenium-methods-dataset.json
   Loaded 150 entries
   Generated 45,230 tokens

📄 Processing: common-web-actions-dataset.json
   Loaded 15 entries
   Generated 8,450 tokens

📄 Processing: element-locator-patterns.json
   Loaded 20 entries
   Generated 12,780 tokens

============================================================
✅ Total tokens across all datasets: 66,460

============================================================
📊 TOKENIZATION STATISTICS
============================================================
Total tokens:        66,460
Unique tokens:       3,245
Vocabulary usage:    3.25% of cl100k_base

💾 Saving tokens to: src\main\resources\selenium_dataset.bin
✅ Binary file created successfully!
   File size: 265,848 bytes (0.25 MB)
   Token count: 66,460

✨ Tokenization complete!
```
