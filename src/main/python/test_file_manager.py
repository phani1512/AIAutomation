"""
Test File Manager
Automatically saves generated test scripts to project structure
Makes tests immediately executable without manual copying
"""

import os
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class TestFileManager:
    """Manages automatic saving and organization of generated test files."""
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize test file manager.
        
        Args:
            workspace_root: Root directory of the workspace (defaults to current)
        """
        if workspace_root is None:
            workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        self.workspace_root = Path(workspace_root)
        self.java_base = self.workspace_root / 'src' / 'test' / 'java' / 'com' / 'testing'
        self.python_base = self.workspace_root / 'tests'
        
        logger.info(f"[FILE-MGR] Workspace root: {self.workspace_root}")
    
    def save_test_suite(self, test_suite: Dict, test_name: str) -> Dict:
        """
        Save complete test suite to project structure.
        Makes tests immediately executable.
        
        Args:
            test_suite: Generated test suite (from CompleteTestGenerator)
            test_name: Base name for test files
            
        Returns:
            Dict with saved file paths and execution instructions
        """
        language = test_suite.get('language', 'java')
        
        if language.lower() == 'java':
            return self._save_java_suite(test_suite, test_name)
        else:
            return self._save_python_suite(test_suite, test_name)
    
    def _save_java_suite(self, test_suite: Dict, test_name: str) -> Dict:
        """Save Java test suite to proper Maven structure."""
        
        saved_files = {}
        
        # Create directories
        pages_dir = self.java_base / 'pages'
        tests_dir = self.java_base / 'tests'
        data_dir = self.java_base / 'data'
        
        pages_dir.mkdir(parents=True, exist_ok=True)
        tests_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Page Object
        page_file = pages_dir / f"{test_name}Page.java"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(test_suite['page_object'])
        saved_files['page_object'] = str(page_file)
        logger.info(f"[FILE-MGR] ✓ Saved Page Object: {page_file}")
        
        # Save Test Class
        test_file = tests_dir / f"{test_name}Test.java"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_suite['test_class'])
        saved_files['test_class'] = str(test_file)
        logger.info(f"[FILE-MGR] ✓ Saved Test Class: {test_file}")
        
        # Save Data Provider
        if test_suite.get('data_provider'):
            data_file = data_dir / "TestDataProvider.java"
            with open(data_file, 'w', encoding='utf-8') as f:
                f.write(test_suite['data_provider'])
            saved_files['data_provider'] = str(data_file)
            logger.info(f"[FILE-MGR] ✓ Saved Data Provider: {data_file}")
        
        # Generate TestNG suite XML
        suite_xml = self._generate_testng_xml(test_name)
        xml_file = self.workspace_root / 'testng.xml'
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(suite_xml)
        saved_files['testng_xml'] = str(xml_file)
        logger.info(f"[FILE-MGR] ✓ Saved TestNG XML: {xml_file}")
        
        # Generate run script
        run_script = self._generate_java_run_script(test_name)
        script_file = self.workspace_root / 'run_tests.bat'
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(run_script)
        saved_files['run_script'] = str(script_file)
        logger.info(f"[FILE-MGR] ✓ Saved Run Script: {script_file}")
        
        return {
            'status': 'success',
            'files': saved_files,
            'test_count': test_suite.get('test_count', 0),
            'ready_to_run': True,
            'execution': {
                'command': 'mvn test',
                'alternative': f'run_tests.bat',
                'ide': f'Right-click {test_name}Test.java -> Run as TestNG Test'
            },
            'message': f'✅ {len(saved_files)} files saved. Tests ready to execute!'
        }
    
    def _save_python_suite(self, test_suite: Dict, test_name: str) -> Dict:
        """Save Python test suite to proper pytest structure."""
        
        saved_files = {}
        
        # Create directories
        self.python_base.mkdir(parents=True, exist_ok=True)
        pages_dir = self.python_base / 'pages'
        pages_dir.mkdir(exist_ok=True)
        
        # Save Page Object
        page_file = pages_dir / f"{test_name.lower()}_page.py"
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(test_suite['page_object'])
        saved_files['page_object'] = str(page_file)
        logger.info(f"[FILE-MGR] ✓ Saved Page Object: {page_file}")
        
        # Save Test Class
        test_file = self.python_base / f"test_{test_name.lower()}.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_suite['test_class'])
        saved_files['test_class'] = str(test_file)
        logger.info(f"[FILE-MGR] ✓ Saved Test Class: {test_file}")
        
        # Save/Update conftest.py (fixtures)
        conftest_file = self.python_base / 'conftest.py'
        if not conftest_file.exists():
            with open(conftest_file, 'w', encoding='utf-8') as f:
                f.write(test_suite['fixtures'])
            saved_files['fixtures'] = str(conftest_file)
            logger.info(f"[FILE-MGR] ✓ Saved Fixtures: {conftest_file}")
        
        # Generate requirements.txt
        requirements = self._generate_python_requirements()
        req_file = self.workspace_root / 'test_requirements.txt'
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(requirements)
        saved_files['requirements'] = str(req_file)
        logger.info(f"[FILE-MGR] ✓ Saved Requirements: {req_file}")
        
        # Generate run script
        run_script = self._generate_python_run_script(test_name)
        script_file = self.workspace_root / 'run_tests.ps1'
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(run_script)
        saved_files['run_script'] = str(script_file)
        logger.info(f"[FILE-MGR] ✓ Saved Run Script: {script_file}")
        
        return {
            'status': 'success',
            'files': saved_files,
            'test_count': test_suite.get('test_count', 0),
            'ready_to_run': True,
            'execution': {
                'command': f'pytest tests/test_{test_name.lower()}.py -v',
                'alternative': f'powershell ./run_tests.ps1',
                'ide': f'Right-click test_{test_name.lower()}.py -> Run pytest'
            },
            'message': f'✅ {len(saved_files)} files saved. Tests ready to execute!'
        }
    
    def _generate_testng_xml(self, test_name: str) -> str:
        """Generate TestNG suite XML."""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Screenshot Generated Test Suite" parallel="false">
    <test name="{test_name} Tests">
        <classes>
            <class name="com.testing.tests.{test_name}Test"/>
        </classes>
    </test>
</suite>
"""
    
    def _generate_java_run_script(self, test_name: str) -> str:
        """Generate Windows batch script to run Java tests."""
        return f"""@echo off
echo ========================================
echo Running Screenshot Generated Tests
echo Test: {test_name}
echo Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
echo ========================================
echo.

REM Run tests with Maven
mvn clean test -Dtest={test_name}Test

echo.
echo ========================================
echo Test execution completed!
echo Check target/surefire-reports for results
echo ========================================
pause
"""
    
    def _generate_python_requirements(self) -> str:
        """Generate Python requirements.txt for tests."""
        return """# Test Dependencies - Generated by Screenshot AI
selenium>=4.15.0
pytest>=7.4.0
pytest-html>=4.1.0
pytest-xdist>=3.5.0
"""
    
    def _generate_python_run_script(self, test_name: str) -> str:
        """Generate PowerShell script to run Python tests."""
        return f"""# Screenshot Generated Tests - PowerShell Runner
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Screenshot Generated Tests" -ForegroundColor Cyan
Write-Host "Test: {test_name}" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {{
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\\venv\\Scripts\\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q -r test_requirements.txt

# Run tests
Write-Host ""
Write-Host "Running tests..." -ForegroundColor Green
pytest tests/test_{test_name.lower()}.py -v --html=test_report.html --self-contained-html

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test execution completed!" -ForegroundColor Green
Write-Host "Report: test_report.html" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Keep window open
Read-Host -Prompt "Press Enter to exit"
"""
    
    def get_test_summary(self) -> Dict:
        """Get summary of all saved tests."""
        java_tests = []
        python_tests = []
        
        # Scan Java tests
        if self.java_base.exists():
            tests_dir = self.java_base / 'tests'
            if tests_dir.exists():
                java_tests = [f.stem for f in tests_dir.glob('*Test.java')]
        
        # Scan Python tests
        if self.python_base.exists():
            python_tests = [f.stem[5:] for f in self.python_base.glob('test_*.py')]
        
        return {
            'java_tests': java_tests,
            'python_tests': python_tests,
            'total_count': len(java_tests) + len(python_tests)
        }
    
    def create_test_index(self) -> str:
        """Create an index of all generated tests."""
        summary = self.get_test_summary()
        
        index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Generated Test Suite Index</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #6366f1; }}
        .test-section {{ margin: 30px 0; }}
        .test-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #6366f1; }}
        .test-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .test-card p {{ margin: 5px 0; color: #666; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 20px; border-radius: 10px; flex: 1; text-align: center; }}
        .stat .number {{ font-size: 2em; font-weight: bold; }}
        .stat .label {{ font-size: 0.9em; margin-top: 5px; }}
        .command {{ background: #1e293b; color: #10b981; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Generated Test Suite Index</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat">
                <div class="number">{summary['total_count']}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="number">{len(summary['java_tests'])}</div>
                <div class="label">Java Tests</div>
            </div>
            <div class="stat">
                <div class="number">{len(summary['python_tests'])}</div>
                <div class="label">Python Tests</div>
            </div>
        </div>
        
        <div class="test-section">
            <h2>☕ Java Tests (TestNG)</h2>
"""
        
        for test in summary['java_tests']:
            index_html += f"""
            <div class="test-card">
                <h3>{test}</h3>
                <p><strong>Location:</strong> src/test/java/com/testing/tests/{test}.java</p>
                <p><strong>Run:</strong></p>
                <div class="command">mvn test -Dtest={test}</div>
            </div>
"""
        
        index_html += """
        </div>
        
        <div class="test-section">
            <h2>🐍 Python Tests (pytest)</h2>
"""
        
        for test in summary['python_tests']:
            index_html += f"""
            <div class="test-card">
                <h3>{test}</h3>
                <p><strong>Location:</strong> tests/test_{test.lower()}.py</p>
                <p><strong>Run:</strong></p>
                <div class="command">pytest tests/test_{test.lower()}.py -v</div>
            </div>
"""
        
        index_html += """
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #e0f2fe; border-radius: 8px;">
            <h3>🚀 Quick Start</h3>
            <p><strong>Run All Java Tests:</strong></p>
            <div class="command">mvn test</div>
            <p><strong>Run All Python Tests:</strong></p>
            <div class="command">pytest tests/ -v</div>
        </div>
    </div>
</body>
</html>
"""
        
        # Save index
        index_file = self.workspace_root / 'test_index.html'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        logger.info(f"[FILE-MGR] ✓ Created test index: {index_file}")
        return str(index_file)
