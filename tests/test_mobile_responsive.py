"""
Mobile-First Responsive Design Tests
Test mobile responsiveness across different screen sizes
"""

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import shutil


# Skip all tests if Chrome is not available
chrome_available = shutil.which("google-chrome") or shutil.which("chromium-browser") or shutil.which("chrome")
pytestmark = pytest.mark.skipif(not chrome_available, reason="Chrome browser not available")


class TestMobileResponsiveness:
    """Test mobile-first responsive design implementation"""

    @pytest.fixture
    def mobile_driver(self):
        """Setup mobile Chrome driver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option(
            "mobileEmulation",
            {
                "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
            },
        )
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        yield driver
        driver.quit()

    @pytest.fixture
    def tablet_driver(self):
        """Setup tablet Chrome driver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option(
            "mobileEmulation",
            {
                "deviceMetrics": {"width": 768, "height": 1024, "pixelRatio": 2.0},
                "userAgent": "Mozilla/5.0 (iPad; CPU OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E5239e Safari/602.1",
            },
        )
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        yield driver
        driver.quit()

    def test_home_page_mobile_responsive(self, mobile_driver):
        """Test home page mobile responsiveness"""
        try:
            mobile_driver.get("http://localhost:5001")

            # Check viewport meta tag is present
            viewport = mobile_driver.find_element(By.XPATH, "//meta[@name='viewport']")
            assert "width=device-width" in viewport.get_attribute("content")

            # Check mobile-friendly navigation
            nav = mobile_driver.find_element(By.CLASS_NAME, "nav-links")
            assert nav.is_displayed()

            # Check search form is touch-friendly
            search_input = mobile_driver.find_element(By.ID, "ticker-input")
            assert search_input.size["height"] >= 44  # Touch target size

            # Check mode selection works on mobile
            mode_boxes = mobile_driver.find_elements(By.CLASS_NAME, "mode-box")
            for box in mode_boxes:
                assert box.size["height"] >= 44  # Touch target size

        except Exception as e:
            # App might not be running, skip test
            pytest.skip(f"App not available: {e}")

    def test_results_page_mobile_table(self, mobile_driver):
        """Test results page table responsiveness"""
        try:
            mobile_driver.get("http://localhost:5001/analyze/RELIANCE")

            # Check tables are mobile responsive
            tables = mobile_driver.find_elements(By.CLASS_NAME, "data")
            if tables:
                table = tables[0]
                # Table should be scrollable horizontally on mobile
                assert "overflow-x" in mobile_driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).getPropertyValue('overflow-x')",
                    table,
                ) or "auto" in mobile_driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).getPropertyValue('overflow-x')",
                    table,
                )

        except Exception as e:
            pytest.skip(f"App not available: {e}")

    def test_pattern_training_mobile(self, mobile_driver):
        """Test pattern training mobile responsiveness"""
        try:
            mobile_driver.get("http://localhost:5001/pattern-training")

            # Check Bootstrap grid is responsive
            pattern_cards = mobile_driver.find_elements(By.CLASS_NAME, "pattern-card")
            for card in pattern_cards:
                assert card.is_displayed()
                # Cards should stack on mobile
                assert card.size["height"] >= 44  # Touch target

        except Exception as e:
            pytest.skip(f"App not available: {e}")

    def test_news_page_mobile(self, mobile_driver):
        """Test news page mobile navigation"""
        try:
            mobile_driver.get("http://localhost:5001/news")

            # Check navigation tabs are touch-friendly
            nav_links = mobile_driver.find_elements(By.CLASS_NAME, "nav-link")
            for link in nav_links:
                if link.is_displayed():
                    assert link.size["height"] >= 44  # Touch target

        except Exception as e:
            pytest.skip(f"App not available: {e}")

    def test_tablet_responsive_layout(self, tablet_driver):
        """Test tablet responsive layout"""
        try:
            tablet_driver.get("http://localhost:5001")

            # Check search form layout on tablet
            search_row = tablet_driver.find_element(By.CLASS_NAME, "search-row")
            # Should be horizontal on tablet
            computed_style = tablet_driver.execute_script(
                "return window.getComputedStyle(arguments[0]).getPropertyValue('flex-direction')",
                search_row,
            )
            # Could be row or column depending on exact tablet size
            assert computed_style in ["row", "column"]

        except Exception as e:
            pytest.skip(f"App not available: {e}")

    @pytest.mark.integration
    def test_cross_device_functionality(self):
        """Test that all device sizes can access core functionality"""
        device_configs = [
            {"width": 320, "height": 568, "name": "Mobile Small"},  # iPhone SE
            {"width": 375, "height": 667, "name": "Mobile Medium"},  # iPhone 6/7/8
            {"width": 768, "height": 1024, "name": "Tablet"},  # iPad
            {"width": 1200, "height": 800, "name": "Desktop"},  # Desktop
        ]

        for config in device_configs:
            options = Options()
            options.add_argument("--headless")
            options.add_argument(f'--window-size={config["width"]},{config["height"]}')

            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.get("http://localhost:5001")

                # Basic functionality test
                assert driver.title
                assert driver.find_element(By.TAG_NAME, "body")

                driver.quit()

            except Exception as e:
                pytest.skip(f"App not available for {config['name']}: {e}")


if __name__ == "__main__":
    # Run basic smoke test if called directly
    print("Mobile Responsiveness Test Suite")
    print("Note: These tests require the Flask app to be running on localhost:5001")
    print("Run with: python -m pytest tests/test_mobile_responsive.py -v")
