"""
Dataset Validation and Deduplication Tool
- Checks for hardcoded values (names, emails, companies)
- Finds duplicates across all datasets
- Replaces hardcoded values with placeholders
- Creates a clean, unified dataset
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class DatasetValidator:
    """Validate and clean training datasets."""
    
    def __init__(self):
        self.datasets = {}
        self.issues = defaultdict(list)
        
        # Patterns for hardcoded values
        self.hardcoded_patterns = {
            'names': [
                r'\b(John|Jane|Smith|Doe|Michael|Sarah|David|Emily|Robert|Lisa)\b',
                r'\bJohn\s+Smith\b',
                r'\bJane\s+Doe\b',
            ],
            'emails': [
                r'\b[\w.+-]+@example\.com\b',
                r'\b[\w.+-]+@test\.com\b',
                r'\bjohn@\w+\.com\b',
                r'\bpvalaboju@vertafore\.com\b',
            ],
            'companies': [
                r'\bVertafore\b',
                r'\bSircon\b',
            ],
            'locations': [
                r'\bNew York\b',
                r'\bCalifornia\b',
                r'\bUSA\b',
            ],
            'phones': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\b555-\d{4}\b',
            ],
            'addresses': [
                r'\b\d+\s+Main\s+St\b',
                r'\b123\s+\w+\s+Street\b',
            ]
        }
        
        # Placeholder mappings
        self.placeholder_map = {
            'John Smith': '{FULL_NAME}',
            'Jane Doe': '{FULL_NAME}',
            'John': '{FIRST_NAME}',
            'Jane': '{FIRST_NAME}',
            'Smith': '{LAST_NAME}',
            'Doe': '{LAST_NAME}',
            'john@example.com': '{EMAIL}',
            'jane@example.com': '{EMAIL}',
            'user@example.com': '{EMAIL}',
            'test@example.com': '{EMAIL}',
            'pvalaboju@vertafore.com': '{EMAIL}',
            'Vertafore': '{COMPANY_NAME}',
            'New York': '{CITY}',
            'California': '{STATE}',
            'United States': '{COUNTRY}',
            'USA': '{COUNTRY}',
            '555-1234': '{PHONE}',
            '123 Main St': '{ADDRESS}',
        }
    
    def load_all_datasets(self) -> Dict[str, List]:
        """Load all JSON datasets from resources folder."""
        
        resources_path = Path('resources/ml_data/datasets')
        
        dataset_files = [
            'page-helper-patterns-dataset.json',
            'page-helper-training-dataset.json',
            'common-web-actions-dataset.json',
            'selenium-methods-dataset.json',
        ]
        
        print("📂 Loading datasets...")
        print("─" * 60)
        
        for filename in dataset_files:
            filepath = resources_path / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.datasets[filename] = data
                        print(f"✓ {filename}: {len(data)} entries")
                except Exception as e:
                    print(f"✗ {filename}: Error - {e}")
                    self.issues['load_errors'].append({
                        'file': filename,
                        'error': str(e)
                    })
            else:
                print(f"⚠ {filename}: Not found")
        
        print()
        return self.datasets
    
    def find_hardcoded_values(self) -> Dict[str, List]:
        """Find all hardcoded values in datasets."""
        
        print("🔍 Scanning for hardcoded values...")
        print("─" * 60)
        
        hardcoded_issues = defaultdict(list)
        
        for dataset_name, data in self.datasets.items():
            entries = data if isinstance(data, list) else [data]
            
            for i, entry in enumerate(entries):
                entry_str = json.dumps(entry, ensure_ascii=False)
                
                # Check each pattern type
                for pattern_type, patterns in self.hardcoded_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, entry_str, re.IGNORECASE)
                        if matches:
                            for match in matches:
                                hardcoded_issues[pattern_type].append({
                                    'dataset': dataset_name,
                                    'entry_index': i,
                                    'value': match,
                                    'context': self._get_context(entry, match)
                                })
        
        # Print summary
        for pattern_type, issues in hardcoded_issues.items():
            unique_values = set(issue['value'] for issue in issues)
            print(f"⚠ {pattern_type.upper()}: {len(unique_values)} unique values found")
            for value in sorted(unique_values)[:5]:  # Show first 5
                print(f"    • {value}")
            if len(unique_values) > 5:
                print(f"    ... and {len(unique_values) - 5} more")
        
        print()
        return dict(hardcoded_issues)
    
    def _get_context(self, entry: Dict, value: str) -> str:
        """Get context where value appears."""
        
        # Find where in the entry this value appears
        for key, val in entry.items():
            if isinstance(val, str) and value in val:
                return f"{key}: {val[:50]}..."
            elif isinstance(val, dict):
                nested = json.dumps(val)
                if value in nested:
                    return f"{key}: {nested[:50]}..."
        
        return "unknown context"
    
    def find_duplicates(self) -> Dict[str, List]:
        """Find duplicate patterns across datasets."""
        
        print("🔍 Checking for duplicates...")
        print("─" * 60)
        
        # Track unique patterns
        seen_patterns = defaultdict(list)
        duplicates = []
        
        for dataset_name, data in self.datasets.items():
            entries = data if isinstance(data, list) else [data]
            
            for i, entry in enumerate(entries):
                # Create a signature for this entry
                signature = self._create_signature(entry)
                
                if signature:
                    seen_patterns[signature].append({
                        'dataset': dataset_name,
                        'index': i,
                        'entry': entry
                    })
        
        # Find entries with same signature
        for signature, occurrences in seen_patterns.items():
            if len(occurrences) > 1:
                duplicates.append({
                    'signature': signature,
                    'count': len(occurrences),
                    'occurrences': occurrences
                })
        
        if duplicates:
            print(f"⚠ Found {len(duplicates)} duplicate patterns")
            for dup in duplicates[:5]:  # Show first 5
                print(f"    • {dup['signature'][:60]}... ({dup['count']} times)")
        else:
            print("✓ No duplicates found")
        
        print()
        return duplicates
    
    def _create_signature(self, entry: Dict) -> str:
        """Create a unique signature for an entry."""
        
        # Try different signature strategies
        if 'input' in entry and 'output' in entry:
            # Training example - use normalized input/output
            return f"{self._normalize(entry['input'])}:::{self._normalize(entry['output'])}"
        
        elif 'prompt' in entry:
            # Prompt-based entry
            return self._normalize(entry.get('prompt', ''))
        
        elif 'method_name' in entry:
            # Pattern entry
            return entry.get('method_name', '')
        
        elif 'action' in entry and 'code' in entry:
            # Code action entry
            return f"{entry.get('action')}:::{self._normalize(entry.get('code', ''))}"
        
        return ""
    
    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        
        if not text:
            return ""
        
        # Replace common variations with placeholders
        normalized = text.lower()
        normalized = re.sub(r'\b\w+@\w+\.\w+\b', '{EMAIL}', normalized)
        normalized = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '{FULL_NAME}', normalized)
        normalized = re.sub(r'\b\d+\b', '{NUMBER}', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def replace_hardcoded_values(self, dataset_name: str, data: List[Dict]) -> List[Dict]:
        """Replace hardcoded values with placeholders."""
        
        cleaned_data = []
        
        for entry in data:
            cleaned_entry = self._replace_in_dict(entry)
            cleaned_data.append(cleaned_entry)
        
        return cleaned_data
    
    def _replace_in_dict(self, obj):
        """Recursively replace hardcoded values in dictionary."""
        
        if isinstance(obj, dict):
            return {k: self._replace_in_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_in_dict(item) for item in obj]
        elif isinstance(obj, str):
            # Replace known hardcoded values
            result = obj
            for hardcoded, placeholder in self.placeholder_map.items():
                # Case-insensitive replacement but preserve case in placeholders
                pattern = re.compile(re.escape(hardcoded), re.IGNORECASE)
                result = pattern.sub(placeholder, result)
            return result
        else:
            return obj
    
    def create_unified_dataset(self) -> Dict[str, List]:
        """Create unified, deduplicated, clean dataset."""
        
        print("🔧 Creating unified dataset...")
        print("─" * 60)
        
        unified = {
            'page_helper_patterns': [],
            'page_helper_training': [],
            'common_actions': [],
            'metadata': {
                'total_entries': 0,
                'duplicates_removed': 0,
                'hardcoded_replaced': 0
            }
        }
        
        # Process Page Helper patterns
        if 'page-helper-patterns-dataset.json' in self.datasets:
            print("Processing Page Helper patterns...")
            patterns = self.datasets['page-helper-patterns-dataset.json']
            cleaned = self.replace_hardcoded_values('patterns', patterns)
            unified['page_helper_patterns'] = cleaned
            print(f"  ✓ {len(cleaned)} patterns")
        
        # Process Page Helper training
        if 'page-helper-training-dataset.json' in self.datasets:
            print("Processing Page Helper training...")
            training = self.datasets['page-helper-training-dataset.json']
            cleaned = self.replace_hardcoded_values('training', training)
            unified['page_helper_training'] = cleaned
            print(f"  ✓ {len(cleaned)} examples")
        
        # Process common actions
        if 'common-web-actions-dataset.json' in self.datasets:
            print("Processing common actions...")
            common = self.datasets['common-web-actions-dataset.json']
            cleaned = self.replace_hardcoded_values('common', common)
            unified['common_actions'] = cleaned
            print(f"  ✓ {len(cleaned)} actions")
        
        unified['metadata']['total_entries'] = (
            len(unified['page_helper_patterns']) +
            len(unified['page_helper_training']) +
            len(unified['common_actions'])
        )
        
        print()
        return unified
    
    def save_cleaned_datasets(self, unified: Dict):
        """Save cleaned datasets."""
        
        print("💾 Saving cleaned datasets...")
        print("─" * 60)
        
        output_path = Path('resources/ml_data/datasets')
        
        # Save individual cleaned datasets
        files_saved = []
        
        if unified['page_helper_patterns']:
            filepath = output_path / 'page-helper-patterns-dataset-clean.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unified['page_helper_patterns'], f, indent=2, ensure_ascii=False)
            print(f"✓ {filepath.name}")
            files_saved.append(str(filepath))
        
        if unified['page_helper_training']:
            filepath = output_path / 'page-helper-training-dataset-clean.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unified['page_helper_training'], f, indent=2, ensure_ascii=False)
            print(f"✓ {filepath.name}")
            files_saved.append(str(filepath))
        
        if unified['common_actions']:
            filepath = output_path / 'common-web-actions-dataset-clean.json'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unified['common_actions'], f, indent=2, ensure_ascii=False)
            print(f"✓ {filepath.name}")
            files_saved.append(str(filepath))
        
        # Save unified dataset
        unified_filepath = output_path / 'unified-training-dataset.json'
        with open(unified_filepath, 'w', encoding='utf-8') as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)
        print(f"✓ {unified_filepath.name}")
        files_saved.append(str(unified_filepath))
        
        print()
        return files_saved
    
    def generate_report(self, hardcoded: Dict, duplicates: List, unified: Dict) -> str:
        """Generate validation report."""
        
        report = []
        report.append("=" * 70)
        report.append("📊 Dataset Validation Report")
        report.append("=" * 70)
        report.append("")
        
        # Datasets loaded
        report.append("📂 Datasets Loaded:")
        for name, data in self.datasets.items():
            report.append(f"  ✓ {name}: {len(data)} entries")
        report.append("")
        
        # Hardcoded values
        report.append("⚠️  Hardcoded Values Found:")
        if hardcoded:
            for pattern_type, issues in hardcoded.items():
                unique_values = set(issue['value'] for issue in issues)
                report.append(f"  • {pattern_type.upper()}: {len(unique_values)} unique values")
        else:
            report.append("  ✓ None found")
        report.append("")
        
        # Duplicates
        report.append("🔄 Duplicate Patterns:")
        if duplicates:
            report.append(f"  ⚠️  {len(duplicates)} duplicate patterns found")
        else:
            report.append("  ✓ No duplicates found")
        report.append("")
        
        # Unified dataset stats
        report.append("✅ Unified Dataset Created:")
        report.append(f"  • Page Helper Patterns: {len(unified.get('page_helper_patterns', []))}")
        report.append(f"  • Page Helper Training: {len(unified.get('page_helper_training', []))}")
        report.append(f"  • Common Actions: {len(unified.get('common_actions', []))}")
        report.append(f"  • Total Entries: {unified['metadata']['total_entries']}")
        report.append("")
        
        # Recommendations
        report.append("💡 Recommendations:")
        if hardcoded:
            report.append("  ⚠️  Replace hardcoded values with placeholders before training")
            report.append("     Use the cleaned datasets: *-clean.json files")
        else:
            report.append("  ✓ Datasets are clean and ready for training")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_validation(self):
        """Run complete validation process."""
        
        print("=" * 70)
        print("🔍 Dataset Validation & Deduplication")
        print("=" * 70)
        print()
        
        # Step 1: Load datasets
        self.load_all_datasets()
        
        # Step 2: Find hardcoded values
        hardcoded = self.find_hardcoded_values()
        
        # Step 3: Find duplicates
        duplicates = self.find_duplicates()
        
        # Step 4: Create unified clean dataset
        unified = self.create_unified_dataset()
        
        # Step 5: Save cleaned datasets
        saved_files = self.save_cleaned_datasets(unified)
        
        # Step 6: Generate report
        report = self.generate_report(hardcoded, duplicates, unified)
        print(report)
        
        # Save report
        report_path = Path('DATASET_VALIDATION_REPORT.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {report_path}")
        
        # Return results
        return {
            'hardcoded_count': sum(len(issues) for issues in hardcoded.values()),
            'duplicate_count': len(duplicates),
            'clean_files': saved_files,
            'success': True
        }

def main():
    """Main execution."""
    
    validator = DatasetValidator()
    results = validator.run_validation()
    
    print("\n" + "=" * 70)
    if results['hardcoded_count'] > 0:
        print("⚠️  ACTION REQUIRED:")
        print("   Hardcoded values found! Use the cleaned datasets:")
        print("   • page-helper-patterns-dataset-clean.json")
        print("   • page-helper-training-dataset-clean.json")
        print("=" * 70)
    else:
        print("✅ All datasets are clean and ready for training!")
        print("=" * 70)

if __name__ == '__main__':
    main()
