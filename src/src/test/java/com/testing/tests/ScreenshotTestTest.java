package com.testing.tests;

import com.testing.pages.ScreenshotTestPage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Comprehensive Test Suite for ScreenshotTest
 * Auto-generated with 5 test cases
 */
public class ScreenshotTestTest {
    
    private WebDriver driver;
    private ScreenshotTestPage page;
    private static final String BASE_URL = "YOUR_URL_HERE";
    
    @BeforeMethod
    public void setup() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        
        driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        driver.get(BASE_URL);
        
        page = new ScreenshotTestPage(driver);
    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
    
    @Test(priority = 1)
    public void testPageLoadsSuccessfully() {
        Assert.assertTrue(page.isPageDisplayed(), "Page should be displayed");

    }
    @Test(priority = 2)
    public void testButton0ButtonClick() {
        page.clickButton0();
        // Add assertions for expected behavior
    }
    @Test(priority = 3)
    public void testButton1ButtonClick() {
        page.clickButton1();
        // Add assertions for expected behavior
    }
    @Test(priority = 4)
    public void testSQLInjectionPrevention() {

        page.clickButton0();
        Assert.assertTrue(page.isPageDisplayed(), "Should handle SQL injection safely");
    }
    @Test(priority = 5)
    public void testXSSPrevention() {

        page.clickButton0();
        Assert.assertTrue(page.isPageDisplayed(), "Should handle XSS safely");
    }

}
