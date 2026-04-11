"""
Unit tests for Advanced Self-Healing Locator System
Tests element identity, confidence scoring, and healing strategies
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from self_healing.advanced_self_healing import (
    ElementIdentity,
    ConfidenceCalculator,
    AdvancedSelfHealingLocator,
    HealingStrategy
)


class TestElementIdentity(unittest.TestCase):
    """Test ElementIdentity class."""
    
    def test_create_empty_identity(self):
        """Test creating empty element identity."""
        identity = ElementIdentity()
        self.assertIsNone(identity.primary_locator)
        self.assertEqual(identity.attributes, {})
        self.assertEqual(identity.context, {})
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Create identity
        identity = ElementIdentity()
        identity.primary_locator = 'By.id("submit")'
        identity.attributes = {
            'id': 'submit',
            'text': 'Submit',
            'class': 'btn btn-primary'
        }
        identity.context = {
            'parent_tag': 'form',
            'position': 2
        }
        identity.fingerprint = 'abc123def456'
        
        # Convert to dict
        data = identity.to_dict()
        self.assertEqual(data['primary_locator'], 'By.id("submit")')
        self.assertEqual(data['attributes']['id'], 'submit')
        
        # Convert back from dict
        restored = ElementIdentity.from_dict(data)
        self.assertEqual(restored.primary_locator, identity.primary_locator)
        self.assertEqual(restored.attributes, identity.attributes)
        self.assertEqual(restored.fingerprint, identity.fingerprint)
    
    def test_fingerprint_generation(self):
        """Test fingerprint generation is consistent."""
        identity1 = ElementIdentity()
        identity1.attributes = {'id': 'test', 'text': 'Hello'}
        identity1.context = {'parent_tag': 'div'}
        fp1 = identity1._generate_fingerprint()
        
        identity2 = ElementIdentity()
        identity2.attributes = {'id': 'test', 'text': 'Hello'}
        identity2.context = {'parent_tag': 'div'}
        fp2 = identity2._generate_fingerprint()
        
        # Same attributes should generate same fingerprint
        self.assertEqual(fp1, fp2)
        
        # Different attributes should generate different fingerprint
        identity3 = ElementIdentity()
        identity3.attributes = {'id': 'different', 'text': 'Hello'}
        identity3.context = {'parent_tag': 'div'}
        fp3 = identity3._generate_fingerprint()
        
        self.assertNotEqual(fp1, fp3)


class TestConfidenceCalculator(unittest.TestCase):
    """Test ConfidenceCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ConfidenceCalculator()
    
    def test_fuzzy_match_identical(self):
        """Test fuzzy matching with identical strings."""
        score = self.calculator._fuzzy_match("Submit", "Submit")
        self.assertEqual(score, 1.0)
    
    def test_fuzzy_match_similar(self):
        """Test fuzzy matching with similar strings."""
        score = self.calculator._fuzzy_match("Submit Form", "Submit")
        self.assertGreater(score, 0.5)  # Should be somewhat similar
    
    def test_fuzzy_match_different(self):
        """Test fuzzy matching with different strings."""
        score = self.calculator._fuzzy_match("Submit", "Cancel")
        self.assertLess(score, 0.5)  # Should be dissimilar
    
    def test_fuzzy_match_case_insensitive(self):
        """Test fuzzy matching is case insensitive."""
        score = self.calculator._fuzzy_match("SUBMIT", "submit")
        self.assertEqual(score, 1.0)
    
    def test_fuzzy_match_empty_strings(self):
        """Test fuzzy matching with empty strings."""
        score1 = self.calculator._fuzzy_match("", "")
        self.assertEqual(score1, 1.0)
        
        score2 = self.calculator._fuzzy_match("test", "")
        self.assertEqual(score2, 0.0)
    
    def test_confidence_level_labels(self):
        """Test confidence level categorization."""
        self.assertEqual(self.calculator.get_confidence_level(0.95), "Very High")
        self.assertEqual(self.calculator.get_confidence_level(0.85), "High")
        self.assertEqual(self.calculator.get_confidence_level(0.60), "Medium")
        self.assertEqual(self.calculator.get_confidence_level(0.40), "Low")
        self.assertEqual(self.calculator.get_confidence_level(0.20), "Very Low")


class TestHealingStrategy(unittest.TestCase):
    """Test HealingStrategy class."""
    
    def test_create_strategy(self):
        """Test creating healing strategy."""
        strategy = HealingStrategy('id_direct', 'By.id("submit")', priority=1)
        self.assertEqual(strategy.type, 'id_direct')
        self.assertEqual(strategy.locator, 'By.id("submit")')
        self.assertEqual(strategy.priority, 1)
    
    def test_strategy_to_dict(self):
        """Test strategy serialization."""
        strategy = HealingStrategy('text_match', 'By.xpath("//button")', priority=3)
        data = strategy.to_dict()
        
        self.assertEqual(data['type'], 'text_match')
        self.assertEqual(data['locator'], 'By.xpath("//button")')
        self.assertEqual(data['priority'], 3)


class TestAdvancedSelfHealingLocator(unittest.TestCase):
    """Test AdvancedSelfHealingLocator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.healer = AdvancedSelfHealingLocator()
    
    def test_initialization(self):
        """Test locator initializes correctly."""
        self.assertIsNotNone(self.healer.confidence_calculator)
        self.assertEqual(self.healer.auto_approve_threshold, 0.80)
        self.assertEqual(self.healer.minimum_threshold, 0.50)
        self.assertEqual(len(self.healer.healing_history), 0)
    
    def test_parse_locator_by_id(self):
        """Test parsing By.id locator."""
        by_type, value = self.healer._parse_locator('By.id("email")')
        from selenium.webdriver.common.by import By
        self.assertEqual(by_type, By.ID)
        self.assertEqual(value, "email")
    
    def test_parse_locator_by_css(self):
        """Test parsing By.cssSelector locator."""
        by_type, value = self.healer._parse_locator('By.cssSelector(".btn-primary")')
        from selenium.webdriver.common.by import By
        self.assertEqual(by_type, By.CSS_SELECTOR)
        self.assertEqual(value, ".btn-primary")
    
    def test_parse_locator_by_xpath(self):
        """Test parsing By.xpath locator."""
        by_type, value = self.healer._parse_locator('By.xpath("//button[@id=\\"submit\\"]")')
        from selenium.webdriver.common.by import By
        self.assertEqual(by_type, By.XPATH)
        self.assertIn("button", value)
    
    def test_parse_locator_invalid(self):
        """Test parsing invalid locator."""
        by_type, value = self.healer._parse_locator('invalid locator')
        self.assertIsNone(by_type)
        self.assertIsNone(value)
    
    def test_generate_healing_strategies(self):
        """Test generating healing strategies from element identity."""
        identity = ElementIdentity()
        identity.attributes = {
            'id': 'submit-btn',
            'name': 'submit',
            'text': 'Submit Form',
            'class': 'btn btn-primary',
            'aria_label': 'Submit the form',
            'tag': 'button'
        }
        identity.context = {'parent_tag': 'form'}
        
        strategies = self.healer._generate_healing_strategies(identity)
        
        # Should generate multiple strategies
        self.assertGreater(len(strategies), 0)
        
        # Strategies should be sorted by priority
        for i in range(len(strategies) - 1):
            self.assertLessEqual(strategies[i].priority, strategies[i + 1].priority)
        
        # Check that we have expected strategy types
        strategy_types = [s.type for s in strategies]
        self.assertIn('id_direct', strategy_types)
        self.assertIn('name_direct', strategy_types)
        self.assertIn('text_match', strategy_types)
    
    def test_generate_strategies_minimal_attributes(self):
        """Test strategy generation with minimal attributes."""
        identity = ElementIdentity()
        identity.attributes = {
            'text': 'Click Me'
        }
        
        strategies = self.healer._generate_healing_strategies(identity)
        
        # Should still generate at least text-based strategy
        self.assertGreater(len(strategies), 0)
        self.assertIn('text_match', [s.type for s in strategies])
    
    def test_get_healing_history(self):
        """Test retrieving healing history."""
        history = self.healer.get_healing_history()
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)  # Empty initially


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow."""
    
    def test_full_workflow_simulation(self):
        """Test complete workflow from identity to healing."""
        # Create element identity
        identity = ElementIdentity()
        identity.primary_locator = 'By.id("original-id")'
        identity.attributes = {
            'id': 'original-id',
            'text': 'Submit',
            'class': 'btn-primary',
            'tag': 'button'
        }
        identity.context = {'parent_tag': 'form'}
        identity.fingerprint = identity._generate_fingerprint()
        
        # Create healer
        healer = AdvancedSelfHealingLocator()
        
        # Generate strategies
        strategies = healer._generate_healing_strategies(identity)
        
        # Verify strategies generated
        self.assertGreater(len(strategies), 0)
        
        # Verify confidence calculator works
        calculator = ConfidenceCalculator()
        self.assertIsNotNone(calculator)
        
        # Test serialization
        data = identity.to_dict()
        restored = ElementIdentity.from_dict(data)
        self.assertEqual(restored.fingerprint, identity.fingerprint)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestElementIdentity))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestHealingStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedSelfHealingLocator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return True if all tests passed
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
