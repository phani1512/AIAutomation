package com.testing.tests;

import org.testng.annotations.DataProvider;

/**
 * Data Provider for ScreenshotTest Tests
 * Provides comprehensive test data scenarios
 */
public class ScreenshotTestTestDataProvider {
    
    @DataProvider(name = "validData")
    public Object[][] getValidData() {
        return new Object[][] {
            {""}
        };
    }
    
    @DataProvider(name = "invalidData")
    public Object[][] getInvalidData() {
        return new Object[][] {
            {""}
        };
    }
    
    @DataProvider(name = "securityData")
    public Object[][] getSecurityData() {
        return new Object[][] {
            {""}
        };
    }
    
    @DataProvider(name = "boundaryData")
    public Object[][] getBoundaryData() {
        return new Object[][] {
            {""}
        };
    }
}
