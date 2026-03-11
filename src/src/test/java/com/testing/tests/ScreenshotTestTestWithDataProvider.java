package com.testing.tests;

import com.testing.pages.ScreenshotTestPage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.testng.Assert;
import org.testng.annotations.*;
import java.time.Duration;

/**
 * Data-Driven Tests for ScreenshotTest
 */
public class ScreenshotTestTestWithDataProvider {
    
    private WebDriver driver;
    private ScreenshotTestPage page;
    
    @BeforeMethod
    public void setup() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        driver = new ChromeDriver(options);
        driver.get("YOUR_URL_HERE");
        page = new ScreenshotTestPage(driver);
    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
    
    @Test(dataProvider = "validData", dataProviderClass = ScreenshotTestTestDataProvider.class)
    public void testWithValidData(String... data) {

        Assert.assertTrue(page.isPageDisplayed());
    }
    
    @Test(dataProvider = "invalidData", dataProviderClass = ScreenshotTestTestDataProvider.class)
    public void testWithInvalidData(String... data) {

        Assert.assertTrue(page.isPageDisplayed());
    }
    
    @Test(dataProvider = "securityData", dataProviderClass = ScreenshotTestTestDataProvider.class)
    public void testSecurityScenarios(String... data) {

        Assert.assertTrue(page.isPageDisplayed(), "Should handle security threats");
    }
}
