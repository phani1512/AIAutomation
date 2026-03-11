from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginTestPage:
    """
    Page Object Model - Auto-generated from Screenshot
    Generated on: 2026-02-03 12:33:14
    """
    
    # Locators
    INPUT0_LOCATOR = (By.XPATH, "//input[@placeholder='Input 0' or @aria-label='Input 0']|//label[contains(text(),'Input 0')]/following-sibling::input[1]|//label[contains(text(),'Input 0')]/..//input")
    INPUT1_LOCATOR = (By.XPATH, "//input[@placeholder='Input 1' or @aria-label='Input 1']|//label[contains(text(),'Input 1')]/following-sibling::input[1]|//label[contains(text(),'Input 1')]/..//input")
    BUTTON0_LOCATOR = (By.XPATH, "//button[contains(text(),'Button 0')]|//input[@type='submit' and @value='Button 0']|//*[@role='button' and contains(text(),'Button 0')]")
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    @property
    def input0(self):
        return self.wait.until(EC.visibility_of_element_located(self.INPUT0_LOCATOR))

    @property
    def input1(self):
        return self.wait.until(EC.visibility_of_element_located(self.INPUT1_LOCATOR))

    def enter_input0(self, value):
        self.input0.clear()
        self.input0.send_keys(value)
        return self

    def enter_input1(self, value):
        self.input1.clear()
        self.input1.send_keys(value)
        return self

    def click_button0(self):
        element = self.wait.until(EC.element_to_be_clickable(self.BUTTON0_LOCATOR))
        element.click()
        return self

    
    def is_page_loaded(self):
        return self.driver.title is not None
    
    def get_page_title(self):
        return self.driver.title
