package com.testing.data;

/**
 * Test Data Provider - Auto-generated
 * Contains realistic test data for form fields
 */
public class TestDataProvider {
    
    public static Object[][] getValidData() {
        return new Object[][] {
            {"Testbusiness_accounts1", "Testinput_11"},
            {"Validbusiness_accounts", "Validinput_1"},
            {"business_accounts_data", "input_1_data"}
        };
    }
    
    public static Object[][] getInvalidData() {
        return new Object[][] {
            {"", ""},  // Empty values
            {"@invalid", "@invalid"},  // Invalid format
            {"<script>alert(1)</script>", "<script>alert(1)</script>"}  // XSS attempt
        };
    }
}
