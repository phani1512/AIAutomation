package com.testing.data;

/**
 * Test Data Provider - Auto-generated
 * Contains realistic test data for form fields
 */
public class TestDataProvider {
    
    public static Object[][] getValidData() {
        return new Object[][] {
            {"Testinput_01", "Testinput_11", "Testinput_21"},
            {"Validinput_0", "Validinput_1", "Validinput_2"},
            {"input_0_data", "input_1_data", "input_2_data"}
        };
    }
    
    public static Object[][] getInvalidData() {
        return new Object[][] {
            {"", "", ""},  // Empty values
            {"@invalid", "@invalid", "@invalid"},  // Invalid format
            {"<script>alert(1)</script>", "<script>alert(1)</script>", "<script>alert(1)</script>"}  // XSS attempt
        };
    }
}
