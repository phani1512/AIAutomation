package com.sircon.tests;

import org.testng.annotations.DataProvider;

/**
 * Data Provider for Login Tests
 * Provides test data for data-driven testing
 */
public class LoginTestDataProvider {
    
    /**
     * Valid login credentials
     */
    @DataProvider(name = "validCredentials")
    public Object[][] getValidCredentials() {
        return new Object[][] {
            {"user1@sircon.com", "Password123!"},
            {"user2@sircon.com", "SecurePass456@"},
            {"admin@sircon.com", "AdminPass789#"}
        };
    }
    
    /**
     * Invalid email formats
     */
    @DataProvider(name = "invalidEmails")
    public Object[][] getInvalidEmails() {
        return new Object[][] {
            {"invalid.email", "Password123!"},
            {"@example.com", "Password123!"},
            {"user@", "Password123!"},
            {"user @example.com", "Password123!"},
            {"", "Password123!"}
        };
    }
    
    /**
     * Invalid passwords
     */
    @DataProvider(name = "invalidPasswords")
    public Object[][] getInvalidPasswords() {
        return new Object[][] {
            {"user@example.com", ""},
            {"user@example.com", "123"},
            {"user@example.com", "short"},
            {"user@example.com", "          "}
        };
    }
    
    /**
     * Security test data (SQL Injection, XSS)
     */
    @DataProvider(name = "securityTestData")
    public Object[][] getSecurityTestData() {
        return new Object[][] {
            {"admin' OR '1'='1", "password"},
            {"admin'--", "password"},
            {"<script>alert('XSS')</script>", "password"},
            {"user@example.com", "<script>alert('XSS')</script>"},
            {"'; DROP TABLE users--", "password"}
        };
    }
    
    /**
     * Boundary test data
     */
    @DataProvider(name = "boundaryTestData")
    public Object[][] getBoundaryTestData() {
        return new Object[][] {
            // Very long email
            {"a".repeat(100) + "@example.com", "Password123!"},
            // Very long password
            {"user@example.com", "P@ss" + "a".repeat(200)},
            // Minimum length
            {"a@b.c", "Pass1!"},
            // Special characters
            {"user+tag@example.com", "P@ssw0rd!#$%^&*()"}
        };
    }
}
