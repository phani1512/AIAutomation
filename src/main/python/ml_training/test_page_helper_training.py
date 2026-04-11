"""
Test script to validate Page Helper training effectiveness
Measures accuracy across different categories and difficulty levels
"""

import json
import requests
import time
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class PageHelperTrainingValidator:
    """Validate training results for Page Helper patterns."""
    
    def __init__(self, api_url: str = 'http://localhost:5001'):
        self.api_url = api_url
        self.results = defaultdict(list)
        
    def load_test_data(self) -> List[Dict]:
        """Load test data from training dataset."""
        test_path = Path('resources/ml_data/datasets/page-helper-training-dataset.json')
        
        with open(test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def load_prompts(self) -> List[Dict]:
        """Load prompts if available."""
        prompts_path = Path('resources/ml_data/datasets/page-helper-prompts.json')
        
        if prompts_path.exists():
            with open(prompts_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def test_single_prompt(self, prompt: str, expected_method: str = None, 
                          expected_code: str = None) -> Tuple[bool, str, str]:
        """Test a single prompt against the API."""
        
        try:
            response = requests.post(
                f'{self.api_url}/generate',
                json={'prompt': prompt},
                timeout=10
            )
            
            if response.ok:
                generated = response.json().get('code', '')
                
                # Check if expected method is in generated code
                if expected_method and expected_method in generated:
                    return True, generated, "Method match"
                elif expected_code and expected_code.strip() == generated.strip():
                    return True, generated, "Exact match"
                elif expected_code and self._similar_code(expected_code, generated):
                    return True, generated, "Similar match"
                else:
                    return False, generated, "No match"
            else:
                return False, "", f"API error: {response.status_code}"
                
        except Exception as e:
            return False, "", f"Exception: {str(e)}"
    
    def _similar_code(self, expected: str, generated: str) -> bool:
        """Check if code is similar enough (ignoring minor differences)."""
        
        # Remove whitespace and normalize
        exp_clean = ''.join(expected.split()).lower()
        gen_clean = ''.join(generated.split()).lower()
        
        # Check if at least 80% similar
        matches = sum(1 for a, b in zip(exp_clean, gen_clean) if a == b)
        similarity = matches / max(len(exp_clean), len(gen_clean))
        
        return similarity >= 0.8
    
    def test_all_examples(self, examples: List[Dict]) -> Dict:
        """Test all training examples."""
        
        results = {
            'total': len(examples),
            'passed': 0,
            'failed': 0,
            'by_category': defaultdict(lambda: {'passed': 0, 'failed': 0}),
            'by_difficulty': defaultdict(lambda: {'passed': 0, 'failed': 0}),
            'failures': []
        }
        
        print(f"Testing {len(examples)} examples...")
        print("─" * 60)
        
        for i, example in enumerate(examples, 1):
            prompt = example.get('input', '')
            expected_output = example.get('output', '')
            category = example.get('category', 'unknown')
            difficulty = example.get('difficulty', 'medium')
            method_pattern = example.get('method_pattern', '')
            
            # Extract method name from pattern
            expected_method = self._extract_method_name(method_pattern)
            
            # Test it
            passed, generated, reason = self.test_single_prompt(
                prompt, expected_method, expected_output
            )
            
            # Record results
            if passed:
                results['passed'] += 1
                results['by_category'][category]['passed'] += 1
                results['by_difficulty'][difficulty]['passed'] += 1
                status = '✓'
            else:
                results['failed'] += 1
                results['by_category'][category]['failed'] += 1
                results['by_difficulty'][difficulty]['failed'] += 1
                status = '✗'
                
                results['failures'].append({
                    'prompt': prompt,
                    'expected': expected_output,
                    'generated': generated,
                    'category': category,
                    'difficulty': difficulty,
                    'reason': reason
                })
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  {i}/{len(examples)} tested...")
            
            # Small delay to not overwhelm server
            time.sleep(0.1)
        
        return results
    
    def _extract_method_name(self, method_pattern: str) -> str:
        """Extract method name from pattern string."""
        if not method_pattern:
            return ""
        
        # Pattern like "setInputFieldValue(String, String)"
        if '(' in method_pattern:
            return method_pattern.split('(')[0].strip()
        
        # Pattern like "multiple methods"
        return ""
    
    def print_results(self, results: Dict):
        """Print test results in a nice format."""
        
        print("\n" + "═" * 60)
        print("📊 Test Results Summary")
        print("═" * 60)
        
        # Overall stats
        total = results['total']
        passed = results['passed']
        failed = results['failed']
        accuracy = (passed / total * 100) if total > 0 else 0
        
        print(f"\n🎯 Overall Accuracy: {accuracy:.1f}%")
        print(f"   Passed: {passed}/{total}")
        print(f"   Failed: {failed}/{total}")
        
        # Category breakdown
        print("\n📋 By Category:")
        print("─" * 60)
        for category, stats in sorted(results['by_category'].items()):
            cat_total = stats['passed'] + stats['failed']
            cat_accuracy = (stats['passed'] / cat_total * 100) if cat_total > 0 else 0
            status = "✓" if cat_accuracy >= 70 else "⚠️" if cat_accuracy >= 50 else "✗"
            
            print(f"  {status} {category:30s}: {cat_accuracy:5.1f}% ({stats['passed']}/{cat_total})")
        
        # Difficulty breakdown
        print("\n📊 By Difficulty:")
        print("─" * 60)
        for difficulty in ['easy', 'medium', 'hard', 'expert']:
            if difficulty in results['by_difficulty']:
                stats = results['by_difficulty'][difficulty]
                diff_total = stats['passed'] + stats['failed']
                diff_accuracy = (stats['passed'] / diff_total * 100) if diff_total > 0 else 0
                status = "✓" if diff_accuracy >= 70 else "⚠️" if diff_accuracy >= 50 else "✗"
                
                print(f"  {status} {difficulty.capitalize():10s}: {diff_accuracy:5.1f}% ({stats['passed']}/{diff_total})")
        
        # Failed examples
        if results['failures']:
            print(f"\n❌ Failed Examples ({len(results['failures'])}):")
            print("─" * 60)
            
            # Show first 5 failures
            for i, failure in enumerate(results['failures'][:5], 1):
                print(f"\n{i}. {failure['category']} ({failure['difficulty']})")
                print(f"   Prompt: {failure['prompt'][:60]}...")
                print(f"   Expected: {failure['expected'][:60]}...")
                print(f"   Got: {failure['generated'][:60] if failure['generated'] else 'No output'}...")
                print(f"   Reason: {failure['reason']}")
            
            if len(results['failures']) > 5:
                print(f"\n   ... and {len(results['failures']) - 5} more failures")
        
        # Recommendations
        print("\n💡 Recommendations:")
        print("─" * 60)
        
        if accuracy >= 90:
            print("  🌟 Excellent! Your model is production-ready.")
        elif accuracy >= 80:
            print("  ✓ Good! Consider adding more examples for failed categories.")
        elif accuracy >= 70:
            print("  ⚠️ Acceptable but needs improvement.")
            print("     → Add 5-10 more examples for each failing category")
            print("     → Review failed cases and similar examples")
        else:
            print("  ✗ Needs significant improvement.")
            print("     → Consider AI API fine-tuning (OpenAI/Anthropic)")
            print("     → Add 10-20 more examples per category")
            print("     → Review training data quality")
        
        # Save detailed results
        self.save_results(results)
    
    def save_results(self, results: Dict):
        """Save detailed results to file."""
        
        output_path = 'test_results_page_helper.json'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Detailed results saved to: {output_path}")
    
    def run_validation(self):
        """Run complete validation suite."""
        
        print("═" * 60)
        print("🧪 Page Helper Training Validation")
        print("═" * 60)
        print()
        
        # Check if server is running
        try:
            response = requests.get(f'{self.api_url}/health', timeout=2)
            if not response.ok:
                print("⚠️ Warning: Server health check failed")
        except:
            print("❌ Error: Cannot connect to API server")
            print(f"   Make sure server is running at {self.api_url}")
            return
        
        print(f"✓ Connected to API server at {self.api_url}")
        print()
        
        # Load test data
        print("📂 Loading test data...")
        examples = self.load_test_data()
        print(f"✓ Loaded {len(examples)} test examples")
        print()
        
        # Run tests
        results = self.test_all_examples(examples)
        
        # Print results
        self.print_results(results)
        
        print("\n" + "═" * 60)
        print("✅ Validation Complete")
        print("═" * 60)

def main():
    """Main execution."""
    
    # Check if API URL provided
    import sys
    api_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5001'
    
    # Create validator
    validator = PageHelperTrainingValidator(api_url)
    
    # Run validation
    validator.run_validation()

if __name__ == '__main__':
    main()
