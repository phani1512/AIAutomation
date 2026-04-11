describe('Field Length Boundary Testing', () => {
    it('Field Length Boundary Testing', () => {
        // Close any sticky popups that might interfere with actions
        cy.get("#sticky-close").then(($btn) => {
            if ($btn.is(":visible")) {
                cy.wrap($btn).click({ force: true });
                cy.wait(500);
            }
        }).catch(() => {
            // Popup might not exist
        });

        // Step 1: enter text in email field
        // Phase 1: Instant check for visible elements
WebElement element = null;
String[] selectors = {"input[id='producer-email']", "input[id='producerEmail']", "input[id='producer_email']", "input[id='username']", "input[id='email']", "[data-test='email-input']", "[data-testid='email']", "input[name='producer-email']", "input[name='producerEmail']", "input[type='email']"};
for (String selector : selectors) {
    try {
        List<WebElement> elements = driver.findElements(By.cssSelector(selector));
        for (WebElement el : elements) {
            if (el.isDisplayed() && el.isEnabled()) {
                element = el;
                break;
            }
        }
        if (element != null) break;
    } catch (Exception e) {
        continue;
    }
}

if (element == null) {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    for (String selector : selectors) {
        try {
            element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(selector)));
            break;
        } catch (Exception e) {
            continue;
        }
    }
}

if (element != null) {
    // Scroll element into view (consistent with recorder)
    try {
        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(false);", element);
        Thread.sleep(300);
    } catch (Exception e) {
        // Scroll not critical
    }
    element.clear();
    element.type('{VALUE}').click();
} else {
    throw new Exception("Could not find element').click();
}

        // Step 2: enter text in password field
        // Phase 1: Instant check for visible elements
WebElement element = null;
String[] selectors = {"input[id='producer-password']", "input[id='producerPassword']", "input[id='producer_password']", "input[id='password']", "[data-test='password-input']", "[data-testid='password']", "input[name='producer-password']", "input[name='producerPassword']", "input[type='password']", "input[name='password']"};
for (String selector : selectors) {
    try {
        List<WebElement> elements = driver.findElements(By.cssSelector(selector));
        for (WebElement el : elements) {
            if (el.isDisplayed() && el.isEnabled()) {
                element = el;
                break;
            }
        }
        if (element != null) break;
    } catch (Exception e) {
        continue;
    }
}

if (element == null) {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    for (String selector : selectors) {
        try {
            element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(selector)));
            break;
        } catch (Exception e) {
            continue;
        }
    }
}

if (element != null) {
    // Scroll element into view (consistent with recorder)
    try {
        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(false);", element);
        Thread.sleep(300);
    } catch (Exception e) {
        // Scroll not critical
    }
    element.clear();
    element.type('{VALUE}').click();
} else {
    throw new Exception("Could not find element').click();
}

        // Step 3: click login button
        // Phase 1: Instant check for visible elements
WebElement element = null;
String[] selectors = {"button[name='login']", "input[type='submit'][value*='Login']", "xpath://button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]", "xpath://button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]", "xpath://button[contains(@aria-label, 'Login')]", "button[id*='login']", "xpath://input[@value='Login']", ".login-row .primary-btn", ".btn-login", "login-button"};
for (String selector : selectors) {
    try {
        List<WebElement> elements = driver.findElements(By.cssSelector(selector));
        for (WebElement el : elements) {
            if (el.isDisplayed() && el.isEnabled()) {
                element = el;
                break;
            }
        }
        if (element != null) break;
    } catch (Exception e) {
        continue;
    }
}

if (element == null) {
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    for (String selector : selectors) {
        try {
            element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(selector)));
            break;
        } catch (Exception e) {
            continue;
        }
    }
}

if (element != null) {
    // Scroll element into view (consistent with recorder)
    try {
        ((JavascriptExecutor) driver).executeScript("arguments[0].scrollIntoView(false);", element);
        Thread.sleep(300);
    } catch (Exception e) {
        // Scroll not critical
    }
    element.click();
} else {
    throw new Exception("Could not find element').click();
}

    });
});
