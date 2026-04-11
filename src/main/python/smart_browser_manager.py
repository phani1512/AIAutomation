"""
Smart Browser Manager - AI-Powered Browser Detection & Auto-Installation
Automatically detects, installs, and manages browsers and WebDrivers
"""

import logging
import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, List
import requests

logger = logging.getLogger(__name__)

class   SmartBrowserManager:
    """Intelligent browser detection, installation, and WebDriver management."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.browsers_detected = {}
        self.drivers_detected = {}
        
        logger.info("[SMART-BROWSER] 🤖 AI Browser Manager initialized")
        logger.info(f"[SMART-BROWSER] System: {self.system}")
    
    def detect_available_browsers(self) -> Dict[str, Dict]:
        """
        Detect all installed browsers and their versions.
        
        Returns:
            Dict with browser name -> {path, version, available}
        """
        logger.info("[SMART-BROWSER] 🔍 Detecting installed browsers...")
        
        browsers = {
            'chrome': self._detect_chrome(),
            'edge': self._detect_edge(),
            'firefox': self._detect_firefox()
        }
        
        self.browsers_detected = browsers
        
        # Log results
        for name, info in browsers.items():
            if info['available']:
                logger.info(f"[SMART-BROWSER] ✓ {name.upper()}: {info['version']} at {info['path']}")
            else:
                logger.warning(f"[SMART-BROWSER] ✗ {name.upper()}: Not installed")
        
        return browsers
    
    def _detect_chrome(self) -> Dict:
        """Detect Chrome browser."""
        if self.system == 'windows':
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]
        elif self.system == 'darwin':  # macOS
            paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:  # Linux
            paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path, 'chrome')
                return {'available': True, 'path': path, 'version': version}
        
        return {'available': False, 'path': None, 'version': None}
    
    def _detect_edge(self) -> Dict:
        """Detect Edge browser."""
        if self.system == 'windows':
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        elif self.system == 'darwin':
            paths = ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
        else:
            paths = ["/usr/bin/microsoft-edge", "/usr/bin/microsoft-edge-stable"]
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path, 'edge')
                return {'available': True, 'path': path, 'version': version}
        
        return {'available': False, 'path': None, 'version': None}
    
    def _detect_firefox(self) -> Dict:
        """Detect Firefox browser."""
        if self.system == 'windows':
            paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
        elif self.system == 'darwin':
            paths = ["/Applications/Firefox.app/Contents/MacOS/firefox"]
        else:
            paths = ["/usr/bin/firefox"]
        
        for path in paths:
            if os.path.exists(path):
                version = self._get_browser_version(path, 'firefox')
                return {'available': True, 'path': path, 'version': version}
        
        return {'available': False, 'path': None, 'version': None}
    
    def _get_browser_version(self, path: str, browser: str) -> Optional[str]:
        """Get browser version."""
        try:
            if browser == 'chrome':
                if self.system == 'windows':
                    cmd = f'powershell "(Get-Item \'{path}\').VersionInfo.FileVersion"'
                else:
                    cmd = f'"{path}" --version'
            elif browser == 'edge':
                if self.system == 'windows':
                    cmd = f'powershell "(Get-Item \'{path}\').VersionInfo.FileVersion"'
                else:
                    cmd = f'"{path}" --version'
            elif browser == 'firefox':
                cmd = f'"{path}" --version'
            else:
                return None
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            version_str = result.stdout.strip()
            
            # Extract version number
            import re
            match = re.search(r'(\d+\.\d+\.\d+)', version_str)
            if match:
                return match.group(1)
            return version_str
        except Exception as e:
            logger.warning(f"[SMART-BROWSER] Could not get {browser} version: {e}")
            return "unknown"
    
    def get_best_available_browser(self) -> Optional[str]:
        """
        Get the best available browser.
        Priority: Chrome > Edge > Firefox
        
        Returns:
            Browser name or None if none available
        """
        if not self.browsers_detected:
            self.detect_available_browsers()
        
        # Priority order
        priority = ['chrome', 'edge', 'firefox']
        
        for browser in priority:
            if self.browsers_detected.get(browser, {}).get('available'):
                logger.info(f"[SMART-BROWSER] 🎯 Best available: {browser.upper()}")
                return browser
        
        logger.error("[SMART-BROWSER] ❌ No browsers detected!")
        return None
    
    def auto_install_webdriver(self, browser: str) -> bool:
        """
        Auto-install matching WebDriver for browser.
        
        Args:
            browser: Browser name (chrome, edge, firefox)
            
        Returns:
            True if successful
        """
        logger.info(f"[SMART-BROWSER] 📦 Auto-installing WebDriver for {browser}...")
        
        try:
            if browser == 'chrome':
                return self._install_chromedriver()
            elif browser == 'edge':
                return self._install_edgedriver()
            elif browser == 'firefox':
                return self._install_geckodriver()
            else:
                logger.error(f"[SMART-BROWSER] Unknown browser: {browser}")
                return False
        except Exception as e:
            logger.error(f"[SMART-BROWSER] WebDriver installation failed: {e}")
            return False
    
    def _install_chromedriver(self) -> bool:
        """Install ChromeDriver using webdriver-manager."""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            logger.info("[SMART-BROWSER] Installing ChromeDriver...")
            driver_path = ChromeDriverManager().install()
            logger.info(f"[SMART-BROWSER] ✓ ChromeDriver installed: {driver_path}")
            return True
        except Exception as e:
            logger.error(f"[SMART-BROWSER] ChromeDriver installation failed: {e}")
            return False
    
    def _install_edgedriver(self) -> bool:
        """Install EdgeDriver using webdriver-manager."""
        try:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            from selenium.webdriver.edge.service import Service
            
            logger.info("[SMART-BROWSER] Installing EdgeDriver...")
            driver_path = EdgeChromiumDriverManager().install()
            logger.info(f"[SMART-BROWSER] ✓ EdgeDriver installed: {driver_path}")
            return True
        except Exception as e:
            logger.error(f"[SMART-BROWSER] EdgeDriver installation failed: {e}")
            return False
    
    def _install_geckodriver(self) -> bool:
        """Install GeckoDriver using webdriver-manager."""
        try:
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.firefox.service import Service
            
            logger.info("[SMART-BROWSER] Installing GeckoDriver...")
            driver_path = GeckoDriverManager().install()
            logger.info(f"[SMART-BROWSER] ✓ GeckoDriver installed: {driver_path}")
            return True
        except Exception as e:
            logger.error(f"[SMART-BROWSER] GeckoDriver installation failed: {e}")
            return False
    
    def suggest_browser_installation(self, browser: str) -> Dict:
        """
        Provide installation instructions for browser.
        
        Args:
            browser: Browser name
            
        Returns:
            Dict with download_url, instructions
        """
        suggestions = {
            'chrome': {
                'download_url': 'https://www.google.com/chrome/',
                'instructions': [
                    '1. Visit https://www.google.com/chrome/',
                    '2. Click "Download Chrome"',
                    '3. Run the installer',
                    '4. Restart your application'
                ]
            },
            'edge': {
                'download_url': 'https://www.microsoft.com/edge',
                'instructions': [
                    '1. Visit https://www.microsoft.com/edge',
                    '2. Click "Download"',
                    '3. Run the installer',
                    '4. Restart your application',
                    'Note: Edge comes pre-installed on Windows 10+'
                ]
            },
            'firefox': {
                'download_url': 'https://www.mozilla.org/firefox/',
                'instructions': [
                    '1. Visit https://www.mozilla.org/firefox/',
                    '2. Click "Download Firefox"',
                    '3. Run the installer',
                    '4. Restart your application'
                ]
            }
        }
        
        return suggestions.get(browser, {
            'download_url': None,
            'instructions': ['Browser not supported']
        })
    
    def initialize_browser_auto(self, preferred_browser: str = None) -> Dict:
        """
        Auto-initialize browser with WebDriver.
        
        Args:
            preferred_browser: Preferred browser (chrome/edge/firefox) or None for auto
            
        Returns:
            Dict with browser, driver_service, success, message
        """
        logger.info("[SMART-BROWSER] 🚀 AI-Powered Browser Initialization...")
        
        # Detect browsers
        browsers = self.detect_available_browsers()
        
        # Determine browser to use
        if preferred_browser and browsers.get(preferred_browser, {}).get('available'):
            browser_name = preferred_browser
            logger.info(f"[SMART-BROWSER] Using preferred browser: {browser_name}")
        else:
            browser_name = self.get_best_available_browser()
            if not browser_name:
                return {
                    'success': False,
                    'browser': None,
                    'driver_service': None,
                    'message': 'No browsers detected. Please install Chrome, Edge, or Firefox.',
                    'suggestions': self.suggest_browser_installation('chrome')
                }
        
        # Auto-install WebDriver
        logger.info(f"[SMART-BROWSER] Ensuring WebDriver for {browser_name}...")
        driver_installed = self.auto_install_webdriver(browser_name)
        
        if not driver_installed:
            return {
                'success': False,
                'browser': browser_name,
                'driver_service': None,
                'message': f'Failed to install WebDriver for {browser_name}',
                'suggestions': None
            }
        
        # Create driver service
        try:
            if browser_name == 'chrome':
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
            elif browser_name == 'edge':
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                from selenium.webdriver.edge.service import Service
                service = Service(EdgeChromiumDriverManager().install())
            elif browser_name == 'firefox':
                from webdriver_manager.firefox import GeckoDriverManager
                from selenium.webdriver.firefox.service import Service
                service = Service(GeckoDriverManager().install())
            
            logger.info(f"[SMART-BROWSER] ✓ {browser_name.upper()} initialized successfully!")
            
            return {
                'success': True,
                'browser': browser_name,
                'driver_service': service,
                'message': f'{browser_name.upper()} ready (version: {browsers[browser_name]["version"]})',
                'suggestions': None
            }
        
        except Exception as e:
            logger.error(f"[SMART-BROWSER] Initialization failed: {e}")
            return {
                'success': False,
                'browser': browser_name,
                'driver_service': None,
                'message': f'Failed to initialize {browser_name}: {str(e)}',
                'suggestions': None
            }
    
    def get_initialization_status(self) -> Dict:
        """Get current browser/driver status."""
        browsers = self.detect_available_browsers()
        
        available_browsers = [name for name, info in browsers.items() if info['available']]
        
        return {
            'total_browsers': len(browsers),
            'available_browsers': available_browsers,
            'recommended_browser': self.get_best_available_browser(),
            'details': browsers
        }
