import pytest
from logintest_page import LoginTestPage

class TestLoginTest:
    """
    Automated Test Suite - Generated from Screenshot
    Generated on: 2026-02-03 12:33:14
    """
    
    @pytest.mark.parametrize("test_data", [
        ["TestData0", "TestData1"],
        ["Valid1", "Valid2", "Valid3"],
    ])
    def test_fill_form(self, driver, test_data):
        page = LoginTestPage(driver)
        
        page.enter_input_0(test_data[0])
        page.enter_input_1(test_data[1])
        
        assert page.is_page_loaded(), "Page should be loaded"

    def test_button_0_click(self, driver):
        page = LoginTestPage(driver)
        page.click_button_0()
        
        assert page.is_page_loaded(), "Page should remain loaded"

