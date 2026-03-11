package com.sircon.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.FindBy;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;

/**
 * Page Object Model for Sircon Login Page
 * Represents the login page with all elements and actions
 */
public class LoginPage {
    
    private WebDriver driver;
    private WebDriverWait wait;
    
    // Page Elements with multiple locator strategies for robustness
    @FindBy(id = "email")
    private WebElement emailInput;
    
    @FindBy(id = "password")
    private WebElement passwordInput;
    
    @FindBy(xpath = "//button[contains(text(), 'Sign In')]")
    private WebElement signInButton;
    
    @FindBy(linkText = "Forgot password or lost access to your email? Get help signing in")
    private WebElement forgotPasswordLink;
    
    @FindBy(linkText = "Sign Up")
    private WebElement signUpLink;
    
    @FindBy(xpath = "//h1[contains(text(), 'Sign In')]")
    private WebElement pageTitle;
    
    @FindBy(className = "error-message")
    private WebElement errorMessage;
    
    /**
     * Constructor - Initializes page elements
     */
    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        PageFactory.initElements(driver, this);
    }
    
    /**
     * Enter email address
     */
    public LoginPage enterEmail(String email) {
        wait.until(ExpectedConditions.visibilityOf(emailInput));
        emailInput.clear();
        emailInput.sendKeys(email);
        return this;
    }
    
    /**
     * Enter password
     */
    public LoginPage enterPassword(String password) {
        wait.until(ExpectedConditions.visibilityOf(passwordInput));
        passwordInput.clear();
        passwordInput.sendKeys(password);
        return this;
    }
    
    /**
     * Click Sign In button
     */
    public void clickSignIn() {
        wait.until(ExpectedConditions.elementToBeClickable(signInButton));
        signInButton.click();
    }
    
    /**
     * Complete login flow with credentials
     */
    public void login(String email, String password) {
        enterEmail(email);
        enterPassword(password);
        clickSignIn();
    }
    
    /**
     * Click Forgot Password link
     */
    public void clickForgotPassword() {
        wait.until(ExpectedConditions.elementToBeClickable(forgotPasswordLink));
        forgotPasswordLink.click();
    }
    
    /**
     * Click Sign Up link
     */
    public void clickSignUp() {
        wait.until(ExpectedConditions.elementToBeClickable(signUpLink));
        signUpLink.click();
    }
    
    /**
     * Verify login page is displayed
     */
    public boolean isLoginPageDisplayed() {
        try {
            wait.until(ExpectedConditions.visibilityOf(pageTitle));
            return pageTitle.isDisplayed() && emailInput.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * Get error message text
     */
    public String getErrorMessage() {
        try {
            wait.until(ExpectedConditions.visibilityOf(errorMessage));
            return errorMessage.getText();
        } catch (Exception e) {
            return "";
        }
    }
    
    /**
     * Verify email field is enabled
     */
    public boolean isEmailFieldEnabled() {
        return emailInput.isEnabled();
    }
    
    /**
     * Verify password field is enabled
     */
    public boolean isPasswordFieldEnabled() {
        return passwordInput.isEnabled();
    }
    
    /**
     * Verify Sign In button is enabled
     */
    public boolean isSignInButtonEnabled() {
        return signInButton.isEnabled();
    }
    
    /**
     * Get email input value
     */
    public String getEmailValue() {
        return emailInput.getAttribute("value");
    }
    
    /**
     * Get password input value
     */
    public String getPasswordValue() {
        return passwordInput.getAttribute("value");
    }
    
    /**
     * Clear all fields
     */
    public void clearAllFields() {
        emailInput.clear();
        passwordInput.clear();
    }
}
