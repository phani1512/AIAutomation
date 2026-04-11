# Main Python module - Re-export all submodules for backward compatibility

# Core
from core.action_suggestion_engine import *
from core.dataset_matcher import *
from core.fallback_strategy import *
from core.inference_improved import *
from core.local_ai_engine import *
from core.locator_utils import *
from core.universal_patterns import *

# AI Vision
from ai_vision.ai_vision_detector import *
from ai_vision.annotate_screenshots import *
from ai_vision.custom_ocr_engine import *
from ai_vision.local_ai_vision import *
from ai_vision.ocr_text_extractor import *
from ai_vision.screenshot_handler_enhanced import *
from ai_vision.simple_ocr import *
from ai_vision.trained_vision_detector import *
from ai_vision.visual_element_detector import *

# Test Management
from test_management.test_case_builder import *
from test_management.test_executor import *
from test_management.test_file_manager import *
from test_management.test_session_manager import *
from test_management.test_suite_handler import *
from test_management.test_suite_runner import *
# Note: test_data_generator might conflict with code_generation version

# Self Healing
from self_healing.advanced_self_healing import *
from self_healing.element_resolver import *
from self_healing.healing_approval import *
from self_healing.self_healing_locator import *

# Semantic Analysis
from semantic_analysis.intelligent_analyzer import *
from semantic_analysis.intelligent_prompt_matcher import *
from semantic_analysis.semantic_analyzer_enhanced import *
from semantic_analysis.semantic_analyzer_optimized import *
from semantic_analysis.semantic_handler import *

# Generators
from generators.code_generator import *
from generators.comprehensive_code_generator import *
from generators.comprehensive_test_generator import *
from generators.direct_test_generator import *
from generators.fallback_code_generator import *
from generators.generation_handler import *
from generators.multimodal_generator import *
from generators.page_object_generator import *
from generators.simple_screenshot_test_generator import *
from generators.smart_locator_generator import *
from generators.universal_test_generator import *

# Browser
from browser.browser_executor import *
from browser.browser_handler import *
from browser.smart_browser_manager import *
from browser.url_monitor import *

# NLP
from nlp.language_converter import *
from nlp.natural_language_processor import *
from nlp.smart_prompt_handler import *
from nlp.template_engine import *
from nlp.template_parameter_extractor import *

# ML Training
from ml_training.create_finetuning_data import *
from ml_training.integrate_page_helper_datasets import *
from ml_training.test_page_helper_training import *
from ml_training.train_simple import *
from ml_training.train_vision_model import *
from ml_training.validate_and_clean_datasets import *

# Recorder
from recorder.recorder_handler import *

# This allows old-style imports like "from test_case_builder import TestCaseBuilder"
# to continue working after file reorganization
