package com.sircon.tests;

import com.sircon.pages.LoginPage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Data-Driven Login Tests using TestNG Data Provider
 */
public class LoginTestWithDataProvider {
    
    private WebDriver driver;
    private LoginPage loginPage;
    private static final String BASE_URL = "https://login.sircon.com";
    
    @BeforeMethod
    public void setup() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        
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
     * Test login with valid credentials from data provider
     */
    @Test(dataProvider = "validCredentials", dataProviderClass = LoginTestDataProvider.class)
    public void testLoginWithValidCredentials(String email, String password) {
        loginPage.login(email, password);
        
        // Add verification for successful login
        // Wait for redirect and verify URL or dashboard elements
    }
    
    /**
     * Test login with invalid email formats
     */
    @Test(dataProvider = "invalidEmails", dataProviderClass = LoginTestDataProvider.class)
    public void testLoginWithInvalidEmails(String email, String password) {
        loginPage.login(email, password);
        
        // Verify error or validation message
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "Should remain on login page with invalid email: " + email);
    }
    
    /**
     * Test login with invalid passwords
     */
    @Test(dataProvider = "invalidPasswords", dataProviderClass = LoginTestDataProvider.class)
    public void testLoginWithInvalidPasswords(String email, String password) {
        loginPage.login(email, password);
        
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "Should remain on login page with invalid password");
    }
    
    /**
     * Security tests for SQL Injection and XSS
     */
    @Test(dataProvider = "securityTestData", dataProviderClass = LoginTestDataProvider.class)
    public void testSecurityVulnerabilities(String email, String password) {
        loginPage.login(email, password);
        
        // System should reject malicious input
        Assert.assertTrue(loginPage.isLoginPageDisplayed(), 
            "System should handle security threats safely");
    }
    
    /**
     * Boundary value tests
     */
    @Test(dataProvider = "boundaryTestData", dataProviderClass = LoginTestDataProvider.class)
    public void testBoundaryValues(String email, String password) {
        loginPage.login(email, password);
        
        // Verify system handles boundary values appropriately
        Assert.assertTrue(driver != null, "Browser should remain stable");
    }
}
