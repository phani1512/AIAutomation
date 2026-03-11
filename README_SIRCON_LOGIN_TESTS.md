# Sircon Login Page - Automated Test Suite

## 📋 Overview
Complete automated test suite for Sircon Login page using **Page Object Model (POM)** design pattern.

## 🏗️ Project Structure
```
src/test/java/com/sircon/
├── pages/
│   └── LoginPage.java          # Page Object Model
└── tests/
    ├── LoginTest.java          # Main test cases (15 tests)
    ├── LoginTestDataProvider.java   # Test data provider
    └── LoginTestWithDataProvider.java  # Data-driven tests
```

## ✨ Features Generated from Screenshot

### Page Elements Identified:
- ✅ Email input field
- ✅ Password input field  
- ✅ Sign In button
- ✅ Forgot Password link
- ✅ Sign Up link
- ✅ Page title/header

### Test Coverage (15+ Test Cases):

#### 1. **Functional Tests**
- TC-001: Verify login page loads successfully
- TC-002: Verify successful login with valid credentials
- TC-003: Verify login fails with invalid email
- TC-004: Verify login fails with invalid password
- TC-005: Verify login fails with empty email
- TC-006: Verify login fails with empty password
- TC-007: Verify both fields empty

#### 2. **Navigation Tests**
- TC-008: Verify Forgot Password link functionality
- TC-009: Verify Sign Up link functionality

#### 3. **Field Validation Tests**
- TC-010: Verify email field accepts valid format
- TC-011: Verify password field masks input
- TC-012: Verify clear fields functionality
- TC-015: Verify special characters in password

#### 4. **Security Tests**
- TC-013: Verify SQL injection attempt is blocked
- TC-014: Verify XSS attempt is handled safely

#### 5. **Data-Driven Tests**
- Valid credentials testing
- Invalid email formats testing
- Invalid passwords testing
- Security vulnerabilities testing
- Boundary value testing

## 🚀 How to Run Tests

### Prerequisites
1. Java 11 or higher
2. Maven or Gradle
3. ChromeDriver (update path in test setup)
4. TestNG dependency

### Maven Dependencies (pom.xml)
```xml
<dependencies>
    <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>4.16.1</version>
    </dependency>
    <dependency>
        <groupId>org.testng</groupId>
        <artifactId>testng</artifactId>
        <version>7.8.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

### Run All Tests
```bash
# Using Maven
mvn clean test -DsuiteXmlFile=testng-sircon-login.xml

# Using TestNG directly
java -cp "lib/*" org.testng.TestNG testng-sircon-login.xml
```

### Run Specific Test Class
```bash
mvn test -Dtest=LoginTest

mvn test -Dtest=LoginTestWithDataProvider
```

### Run Single Test Method
```bash
mvn test -Dtest=LoginTest#testSuccessfulLogin
```

## 📊 Test Reports
After execution, TestNG generates HTML reports in:
```
target/surefire-reports/index.html
test-output/index.html
```

## 🔧 Configuration

### Update ChromeDriver Path
In `LoginTest.java` and `LoginTestWithDataProvider.java`:
```java
System.setProperty("webdriver.chrome.driver", "path/to/chromedriver");
```

### Update Base URL
```java
private static final String BASE_URL = "https://login.sircon.com"; // Your actual URL
```

### Update Test Credentials
In `LoginTestDataProvider.java`, update valid credentials:
```java
@DataProvider(name = "validCredentials")
public Object[][] getValidCredentials() {
    return new Object[][] {
        {"your.email@example.com", "YourPassword123!"}
    };
}
```

## 🎯 Page Object Model Benefits
- **Maintainability**: Changes to UI require updates only in LoginPage.java
- **Reusability**: Page methods can be used across multiple test classes
- **Readability**: Test code is cleaner and more business-focused
- **Reduced Duplication**: Locator strategies defined once

## 📝 Example Usage

### Simple Test
```java
@Test
public void testLogin() {
    LoginPage loginPage = new LoginPage(driver);
    loginPage.login("user@example.com", "password123");
    // Assert success
}
```

### Fluent Interface
```java
@Test
public void testLoginFluent() {
    new LoginPage(driver)
        .enterEmail("user@example.com")
        .enterPassword("password123")
        .clickSignIn();
}
```

## 🔍 What Gets Tested

### Positive Scenarios
- Valid login with correct credentials
- Email and password field acceptance
- Navigation links functionality

### Negative Scenarios  
- Invalid credentials
- Empty fields
- Malformed email addresses
- SQL injection attempts
- XSS attacks

### Edge Cases
- Very long email/password
- Special characters
- Whitespace handling
- Boundary values

## 📦 Files Created

1. **LoginPage.java** - Page Object Model with all elements and actions
2. **LoginTest.java** - 15 comprehensive test cases
3. **LoginTestDataProvider.java** - Test data for data-driven testing
4. **LoginTestWithDataProvider.java** - Data-driven test implementation
5. **testng-sircon-login.xml** - TestNG suite configuration
6. **README_SIRCON_LOGIN_TESTS.md** - This documentation

## ✅ Ready to Execute

All test files are created and ready to run. Just:
1. Update ChromeDriver path
2. Update BASE_URL with actual Sircon login URL
3. Add valid test credentials
4. Run: `mvn clean test -DsuiteXmlFile=testng-sircon-login.xml`

## 🎓 Best Practices Implemented
- ✅ Page Object Model design pattern
- ✅ Explicit waits for stability
- ✅ Data-driven testing with TestNG DataProvider
- ✅ Fluent interface for better readability
- ✅ Security testing (SQL injection, XSS)
- ✅ Comprehensive error handling
- ✅ Clear test naming conventions
- ✅ Parallel execution support
- ✅ Detailed test documentation

---
**Generated by AI Screenshot Analyzer** 📸 → 🤖 → ✅
