package com.test.automation;

/**
 * Test Case: Logintestone
 * Test ID: TC002
 * Description: Test: Logintestone
 * Priority: high
 * Generated: 2026-03-23T23:31:30.121574
 */
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.*;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;
import static org.junit.jupiter.api.Assertions.*;

@Tag("automation")
@Tag("generated")
@DisplayName("Logintestone")
public class LogintestoneTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("--disable-notifications");
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        
        // Close sticky popup - simple direct approach
        try {
            WebElement closeBtn = driver.findElement(By.id("sticky-close"));
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", closeBtn);
            Thread.sleep(1000);
        } catch (Exception e) {
            // Popup might not exist
        }
    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    @DisplayName("Test: Logintestone")
    public void testLogintestone() throws InterruptedException {
        // Navigate to application
        driver.get("https://www.sircontest.non-prod.sircon.com/");
        Thread.sleep(2000);

        // Close any sticky popups that might interfere with actions
        try {
            WebElement closeBtn = driver.findElement(By.id("sticky-close"));
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", closeBtn);
            Thread.sleep(500);
        } catch (Exception e) {
            // Popup might not exist
        }

        // Step 1: enter text in producer email
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, "producer-email")))
        element.clear()
        element.send_keys("text")

        // Step 2: enter text in producer password
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.ID, "producer-password")))
        element.clear()
        element.send_keys("text")

        // Add assertions as needed
        // assertTrue(driver.getPageSource().contains("expected text"));
    }
}
