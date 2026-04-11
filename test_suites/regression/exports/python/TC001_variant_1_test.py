# Execution-ready code (no pytest fixtures)
# Test: Field Length Boundary Testing
# Test ID: TC001_variant_1

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
    element.send_keys("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
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
    element.send_keys("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
else:
    raise Exception("Could not find element")

# Try multiple selectors until one works
element = None
selectors = ["button[name='login']", "input[type='submit'][value*='Login']", "xpath://button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]", "xpath://button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]", "xpath://button[contains(@aria-label, 'Login')]", "button[id*='login']", "xpath://input[@value='Login']", '.login-row .primary-btn', '.btn-login', 'login-button']
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
    element.click()
else:
    raise Exception("Could not find element")
