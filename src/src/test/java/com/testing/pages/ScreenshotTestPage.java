package com.testing.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;

/**
 * Page Object Model - Auto-generated from Screenshot
 * Generated on: 2026-01-12 15:31:22
 */
public class ScreenshotTestPage {
    
    private WebDriver driver;
    private WebDriverWait wait;
    
    // Page Elements
    @FindBy(id = "business-accounts")
    private WebElement business_accounts;

    @FindBy(id = "input_1")
    private WebElement input_1;

    @FindBy(id = "button_0")
    private WebElement button_0;

    @FindBy(id = "button_1")
    private WebElement button_1;

    
    // Constructor
    public ScreenshotTestPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        PageFactory.initElements(driver, this);
    }
    
    // Page Methods
    public ScreenshotTestPage enterBusinessAccounts(String value) {
        wait.until(ExpectedConditions.visibilityOf(business_accounts));
        business_accounts.clear();
        business_accounts.sendKeys(value);
        return this;
    }

    public ScreenshotTestPage enterInput1(String value) {
        wait.until(ExpectedConditions.visibilityOf(input_1));
        input_1.clear();
        input_1.sendKeys(value);
        return this;
    }

    public void clickButton0() {
        wait.until(ExpectedConditions.elementToBeClickable(button_0));
        button_0.click();
    }

    public void clickButton1() {
        wait.until(ExpectedConditions.elementToBeClickable(button_1));
        button_1.click();
    }

    
    // Utility Methods
    public boolean isPageLoaded() {
        return driver.getTitle() != null;
    }
    
    public String getPageTitle() {
        return driver.getTitle();
    }
}
