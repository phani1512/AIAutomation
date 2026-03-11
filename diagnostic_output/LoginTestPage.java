package com.testing.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.time.Duration;

/**
 * Page Object Model - Auto-generated from Screenshot with OCR
 * Generated on: 2026-02-03 12:33:14
 * Elements: 2 input(s), 1 button(s)
 * Features: OCR Labels, Smart Locators, Page Factory
 */
public class LoginTestPage {
    
    private WebDriver driver;
    private WebDriverWait wait;
    private static final Logger logger = LoggerFactory.getLogger(LoginTestPage.class);
    
    // Page Elements (detected from screenshot)
    @FindBy(xpath = "//input[@placeholder='Input 0' or @aria-label='Input 0']|//label[contains(text(),'Input 0')]/following-sibling::input[1]|//label[contains(text(),'Input 0')]/..//input")
    private WebElement input0;

    @FindBy(xpath = "//input[@placeholder='Input 1' or @aria-label='Input 1']|//label[contains(text(),'Input 1')]/following-sibling::input[1]|//label[contains(text(),'Input 1')]/..//input")
    private WebElement input1;

    @FindBy(xpath = "//button[contains(text(),'Button 0')]|//input[@type='submit' and @value='Button 0']|//*[@role='button' and contains(text(),'Button 0')]")
    private WebElement button0;

    
    // Constructor
    public LoginTestPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        PageFactory.initElements(driver, this);
        logger.info("Initialized {} page object", "LoginTestPage");
    }
    
    // Action Methods
    /**
     * Enter value into Input 0 field
     * @param value The value to enter
     * @return This page object for chaining
     */
    public LoginTestPage enterInput0(String value) {
        wait.until(ExpectedConditions.visibilityOf(input0));
        input0.clear();
        input0.sendKeys(value);
        logger.debug("Entered '{}' into Input 0 field", value);
        return this;
    }

    /**
     * Enter value into Input 1 field
     * @param value The value to enter
     * @return This page object for chaining
     */
    public LoginTestPage enterInput1(String value) {
        wait.until(ExpectedConditions.visibilityOf(input1));
        input1.clear();
        input1.sendKeys(value);
        logger.debug("Entered '{}' into Input 1 field", value);
        return this;
    }

    /**
     * Click the 'Button 0' button
     */
    public void clickButton0() {
        wait.until(ExpectedConditions.elementToBeClickable(button0));
        button0.click();
        logger.debug("Clicked 'Button 0' button");
    }

    
    // Validation Methods
    public boolean isPageLoaded() {
        try {
            return driver.getTitle() != null && !driver.getTitle().isEmpty();
        } catch (Exception e) {
            return false;
        }
    }
    
    public String getPageTitle() {
        return driver.getTitle();
    }
    
    public String getCurrentUrl() {
        return driver.getCurrentUrl();
    }
}
