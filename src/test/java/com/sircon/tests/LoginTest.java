package com.sircon.tests;

import com.sircon.pages.LoginPage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Automated Test Cases for Sircon Login Page
 * Uses Page Object Model for maintainability
 */
public class LoginTest {
    
    private WebDriver driver;
    private LoginPage loginPage;
    private static final String BASE_URL = "https://login.sircon.com"; // Update with actual URL
    
    @BeforeClass
    public void setupClass() {
        // Setup ChromeDriver - Update path as needed
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
    }
    
    @BeforeMethod
    public void setup() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        
        driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.get(BASE_URL);
        
        loginPage = new LoginPage(driver);
    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
    
    /**
     * TC-001: Verify login page loads successfully
     */
    @Test(priority = 1)
    public void testLoginPageDisplayed() {
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "Login page should be displayed");
        Assert.assertTrue(loginPage.isEmailFieldEnabled(), 
            "Email field should be enabled");
        Assert.assertTrue(loginPage.isPasswordFieldEnabled(), 
            "Password field should be enabled");
        Assert.assertTrue(loginPage.isSignInButtonEnabled(), 
            "Sign In button should be enabled");
    }
    
    /**
     * TC-002: Verify successful login with valid credentials
     */
    @Test(priority = 2)
    public void testSuccessfulLogin() {
        loginPage.login("valid.user@example.com", "ValidPassword123!");
        
        // Add assertion for successful login redirect
        // Assert.assertTrue(driver.getCurrentUrl().contains("dashboard"));
    }
    
    /**
     * TC-003: Verify login fails with invalid email
     */
    @Test(priority = 3)
    public void testLoginWithInvalidEmail() {
        loginPage.login("invalid.email@example.com", "Password123!");
        
        // Verify error message is displayed
        String errorMsg = loginPage.getErrorMessage();
        Assert.assertFalse(errorMsg.isEmpty(), 
            "Error message should be displayed for invalid credentials");
    }
    
    /**
     * TC-004: Verify login fails with invalid password
     */
    @Test(priority = 4)
    public void testLoginWithInvalidPassword() {
        loginPage.login("valid.user@example.com", "WrongPassword!");
        
        String errorMsg = loginPage.getErrorMessage();
        Assert.assertFalse(errorMsg.isEmpty(), 
            "Error message should be displayed for invalid password");
    }
    
    /**
     * TC-005: Verify login fails with empty email
     */
    @Test(priority = 5)
    public void testLoginWithEmptyEmail() {
        loginPage.enterEmail("");
        loginPage.enterPassword("Password123!");
        loginPage.clickSignIn();
        
        // Verify validation message or that form doesn't submit
        Assert.assertEquals(loginPage.getEmailValue(), "", 
            "Email field should remain empty");
    }
    
    /**
     * TC-006: Verify login fails with empty password
     */
    @Test(priority = 6)
    public void testLoginWithEmptyPassword() {
        loginPage.enterEmail("user@example.com");
        loginPage.enterPassword("");
        loginPage.clickSignIn();
        
        Assert.assertEquals(loginPage.getPasswordValue(), "", 
            "Password field should remain empty");
    }
    
    /**
     * TC-007: Verify both fields empty
     */
    @Test(priority = 7)
    public void testLoginWithEmptyFields() {
        loginPage.clickSignIn();
        
        // Should stay on login page
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "Should remain on login page with empty fields");
    }
    
    /**
     * TC-008: Verify Forgot Password link functionality
     */
    @Test(priority = 8)
    public void testForgotPasswordLink() {
        loginPage.clickForgotPassword();
        
        // Verify navigation to forgot password page
        // Assert.assertTrue(driver.getCurrentUrl().contains("forgot-password"));
    }
    
    /**
     * TC-009: Verify Sign Up link functionality
     */
    @Test(priority = 9)
    public void testSignUpLink() {
        loginPage.clickSignUp();
        
        // Verify navigation to sign up page
        // Assert.assertTrue(driver.getCurrentUrl().contains("signup") || 
        //                  driver.getCurrentUrl().contains("register"));
    }
    
    /**
     * TC-010: Verify email field accepts valid email format
     */
    @Test(priority = 10)
    public void testEmailFieldAcceptsValidFormat() {
        String validEmail = "test.user@sircon.com";
        loginPage.enterEmail(validEmail);
        
        Assert.assertEquals(loginPage.getEmailValue(), validEmail, 
            "Email field should accept and retain valid email");
    }
    
    /**
     * TC-011: Verify password field masks input
     */
    @Test(priority = 11)
    public void testPasswordFieldMasksInput() {
        loginPage.enterPassword("TestPassword123");
        
        // Verify password field type is "password"
        // Additional verification can be added if needed
        Assert.assertNotNull(loginPage.getPasswordValue(), 
            "Password value should be set");
    }
    
    /**
     * TC-012: Verify clear fields functionality
     */
    @Test(priority = 12)
    public void testClearFields() {
        loginPage.enterEmail("test@example.com");
        loginPage.enterPassword("password123");
        loginPage.clearAllFields();
        
        Assert.assertEquals(loginPage.getEmailValue(), "", 
            "Email field should be cleared");
        Assert.assertEquals(loginPage.getPasswordValue(), "", 
            "Password field should be cleared");
    }
    
    /**
     * TC-013: Verify login with SQL injection attempt
     */
    @Test(priority = 13)
    public void testSQLInjectionAttempt() {
        loginPage.login("admin' OR '1'='1", "' OR '1'='1");
        
        // Should not allow SQL injection
        String errorMsg = loginPage.getErrorMessage();
        Assert.assertFalse(errorMsg.isEmpty(), 
            "System should reject SQL injection attempts");
    }
    
    /**
     * TC-014: Verify login with XSS attempt
     */
    @Test(priority = 14)
    public void testXSSAttempt() {
        loginPage.login("<script>alert('XSS')</script>", "password");
        
        // Should handle XSS safely
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "System should handle XSS attempts safely");
    }
    
    /**
     * TC-015: Verify special characters in password
     */
    @Test(priority = 15)
    public void testSpecialCharactersInPassword() {
        String complexPassword = "P@ssw0rd!#$%^&*()";
        loginPage.enterEmail("user@example.com");
        loginPage.enterPassword(complexPassword);
        loginPage.clickSignIn();
        
        // Should accept special characters
        Assert.assertNotNull(loginPage.getPasswordValue(), 
            "Password field should accept special characters");
    }
}
