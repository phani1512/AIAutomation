"""
Test Case: refactor
Test ID: TC003
Priority: high
Generated: 2026-03-30T19:54:15.831870
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser", default="chrome")
    if browser.lower() == "firefox":
        driver = webdriver.Firefox()
    elif browser.lower() == "edge":
        driver = webdriver.Edge()
    else:
        driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.mark.high
@pytest.mark.automation
@pytest.mark.generated
def test_refactor(driver):
    """Test: refactor"""
    driver.get("https://platform.sircontest.non-prod.sircon.com/#/login")
    # Try multiple selectors until one works
    element = None
    selectors = ["input[id='producer-email']", "input[id='producerEmail']", "input[id='producer_email']", "input[id='username']", "input[id='email']", "[data-test='email-input']", "[data-testid='email']", "input[name='producer-email']", "input[name='producerEmail']", "input[type='email']"]
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    element = el
                    break
            if element:
                break
        except:
            continue
    if not element:
        wait = WebDriverWait(driver, 10)
        for selector in selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break  # Found element
            except:
                continue  # Try next
    if element:
        # Scroll element into view (consistent with recorder)
        try:
            driver.execute_script("arguments[0].scrollIntoView(false);", element)
            time.sleep(0.3)
        except:
            pass  # Scroll not critical
        element.clear()
        element.send_keys("pvalaboju@vertafore.com")
    else:
        raise Exception("Could not find element")
    # Try multiple selectors until one works
    element = None
    selectors = ["input[id='producer-password']", "input[id='producerPassword']", "input[id='producer_password']", "input[id='password']", "[data-test='password-input']", "[data-testid='password']", "input[name='producer-password']", "input[name='producerPassword']", "input[type='password']", "input[name='password']"]
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    element = el
                    break
            if element:
                break
        except:
            continue
    if not element:
        wait = WebDriverWait(driver, 10)
        for selector in selectors:
            try:
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break  # Found element
            except:
                continue  # Try next
    if element:
        # Scroll element into view (consistent with recorder)
        try:
            driver.execute_script("arguments[0].scrollIntoView(false);", element)
            time.sleep(0.3)
        except:
            pass  # Scroll not critical
        element.clear()
        element.send_keys("Phanindraa@1512")
    else:
        raise Exception("Could not find element")