package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Automated Test Cases for Application
 * Auto-generated from Screenshot Analysis
 * Professional Quality Test Suite
 * Total Test Cases: 20
 */
public class LoginPageTest {
    
    private WebDriver driver;
    private WebDriverWait wait;
    private static final String BASE_URL = "YOUR_URL_HERE";
    
    /**
     * Setup ChromeDriver configuration
     */
    @BeforeClass
    public void setupClass() {
        // Setup ChromeDriver - Update path as needed
        System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
    }
    
    /**
     * Initialize WebDriver and navigate to base URL before each test
     */
    @BeforeMethod
    public void setup() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        options.addArguments("--disable-blink-features=AutomationControlled");
        options.addArguments("--disable-popup-blocking");
        
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        driver.get(BASE_URL);
    }
    
    /**
     * Clean up WebDriver after each test
     */
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    /**
     * TC-001: Verify successful login with valid credentials
     */
    @Test(priority = 1)
    public void testSuccessfulLogin() {
        // Wait for email field and enter credentials
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("email")));
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("password")));
        driver.findElement(By.id("password")).sendKeys("Password123!");
        
        wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//input[1]")));
        driver.findElement(By.xpath("//input[1]")).click();
        
        wait.until(ExpectedConditions.not(ExpectedConditions.urlToBe(BASE_URL)));
        
        // Verify successful login redirect
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "User should be redirected to dashboard after successful login");
    }

    /**
     * TC-002: Verify login with different valid email formats
     */
    @Test(priority = 2)
    public void testLoginWithDifferentValidEmailFormat() {
        driver.findElement(By.id("email")).sendKeys("test.user+tag@company.co.uk");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should accept valid email formats with dots, plus signs, and multiple TLDs");
    }

    /**
     * TC-003: Verify both fields empty
     */
    @Test(priority = 3)
    public void testLoginWithEmptyFields() {
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Should remain on login page with empty fields");
    }

    /**
     * TC-004: Verify login fails with empty email
     */
    @Test(priority = 4)
    public void testLoginWithEmptyEmail() {
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email field is required - should remain on login page");
    }

    /**
     * TC-005: Verify login fails with empty password
     */
    @Test(priority = 5)
    public void testLoginWithEmptyPassword() {
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Password field is required - should remain on login page");
    }

    /**
     * TC-006: Verify login fails with invalid email format (missing @)
     */
    @Test(priority = 6)
    public void testLoginWithInvalidEmailMissingAt() {
        driver.findElement(By.id("email")).sendKeys("userexample.com");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Invalid email format should be rejected");
    }

    /**
     * TC-007: Verify login fails with invalid email (missing domain)
     */
    @Test(priority = 7)
    public void testLoginWithInvalidEmailMissingDomain() {
        driver.findElement(By.id("email")).sendKeys("user@");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Incomplete email should be rejected");
    }

    /**
     * TC-008: Verify login fails with invalid special characters in email
     */
    @Test(priority = 8)
    public void testLoginWithInvalidEmailSpecialChars() {
        driver.findElement(By.id("email")).sendKeys("user#$%@example.com");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email with invalid special characters should be rejected");
    }

    /**
     * TC-009: Verify login fails with invalid password
     */
    @Test(priority = 9)
    public void testLoginWithWrongPassword() {
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        driver.findElement(By.id("password")).sendKeys("WrongPassword123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Incorrect password should not allow login");
    }

    /**
     * TC-010: Verify login fails with unregistered email
     */
    @Test(priority = 10)
    public void testLoginWithUnregisteredEmail() {
        driver.findElement(By.id("email")).sendKeys("nonexistent@example.com");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Unregistered email should not allow login");
    }

    /**
     * TC-011: Verify login with SQL injection attempt in email
     */
    @Test(priority = 11)
    public void testSQLInjectionInEmail() {
        driver.findElement(By.id("email")).sendKeys("admin' OR '1'='1");
        driver.findElement(By.id("password")).sendKeys("password");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should reject SQL injection attempts");
    }

    /**
     * TC-012: Verify login with SQL injection attempt in password
     */
    @Test(priority = 12)
    public void testSQLInjectionInPassword() {
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        driver.findElement(By.id("password")).sendKeys("' OR '1'='1' --");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should prevent SQL injection via password field");
    }

    /**
     * TC-013: Verify login with XSS attempt in email
     */
    @Test(priority = 13)
    public void testXSSAttemptInEmail() {
        driver.findElement(By.id("email")).sendKeys("<script>alert('XSS')</script>");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertTrue(driver.getCurrentUrl().equals(BASE_URL), 
            "System should handle XSS attempts safely");
    }

    /**
     * TC-014: Verify login with XSS attempt in password
     */
    @Test(priority = 14)
    public void testXSSAttemptInPassword() {
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        driver.findElement(By.id("password")).sendKeys("<img src=x onerror=alert('XSS')>");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertTrue(driver.getCurrentUrl().equals(BASE_URL), 
            "System should sanitize XSS scripts safely");
    }

    /**
     * TC-015: Verify handling of extremely long email
     */
    @Test(priority = 15)
    public void testLoginWithVeryLongEmail() {
        String longEmail = "a".repeat(250) + "@example.com";
        driver.findElement(By.id("email")).sendKeys(longEmail);
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should handle boundary case for email length");
    }

    /**
     * TC-016: Verify handling of extremely long password
     */
    @Test(priority = 16)
    public void testLoginWithVeryLongPassword() {
        String longPassword = "P@ssw0rd" + "a".repeat(500);
        driver.findElement(By.id("email")).sendKeys("user@example.com");
        driver.findElement(By.id("password")).sendKeys(longPassword);
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "System should handle boundary case for password length");
    }

    /**
     * TC-017: Verify validation with single character email
     */
    @Test(priority = 17)
    public void testLoginWithSingleCharEmail() {
        driver.findElement(By.id("email")).sendKeys("a");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Single character should not be accepted as valid email");
    }

    /**
     * TC-018: Verify validation with spaces in email
     */
    @Test(priority = 18)
    public void testLoginWithSpacesInEmail() {
        driver.findElement(By.id("email")).sendKeys("user name@example.com");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(1000); } catch (InterruptedException e) { }
        
        Assert.assertEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email addresses should not contain spaces");
    }

    /**
     * TC-019: Verify email case sensitivity
     */
    @Test(priority = 19)
    public void testEmailCaseSensitivity() {
        driver.findElement(By.id("email")).sendKeys("USER@EXAMPLE.COM");
        driver.findElement(By.id("password")).sendKeys("Password123!");
        driver.findElement(By.xpath("//input[1]")).click();
        
        try { Thread.sleep(2000); } catch (InterruptedException e) { }
        
        // Email should be case-insensitive per RFC 5321
        Assert.assertNotEquals(driver.getCurrentUrl(), BASE_URL, 
            "Email should be case-insensitive for login");
    }

    /**
     * TC-020: Verify password field masks input
     */
    @Test(priority = 20)
    public void testPasswordFieldMasksInput() {
        driver.findElement(By.id("password")).sendKeys("Password123!");
        
        String passwordType = driver.findElement(By.id("password")).getAttribute("type");
        
        Assert.assertEquals(passwordType, "password", 
            "Password field should be masked (type='password')");
    }

}
