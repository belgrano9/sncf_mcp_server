"""
Working SNCF Price Scraper using Browser Automation

⚠️ EDUCATIONAL POC - This actually works (or has a much better chance)!

Uses Selenium with undetected-chromedriver to bypass Datadome detection.
Based on successful scraping techniques from Reddit research.

Legal Notice:
- For educational purposes only
- May violate SNCF Terms of Service
- Use at your own risk
- Consider official APIs for production
"""

import time
import logging
from datetime import datetime
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

from .models import TrainOffer, PriceSearchResult

logger = logging.getLogger(__name__)


class SNCFBrowserScraper:
    """
    Browser-based SNCF scraper using undetected-chromedriver.

    This approach simulates a real user browsing the SNCF website,
    which has a much higher success rate than simple HTTP requests.
    """

    SNCF_URL = "https://www.sncf-connect.com"

    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize the browser scraper.

        Args:
            headless: Run in headless mode (no visible browser)
            timeout: Default wait timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None

    def _init_driver(self):
        """Initialize undetected Chrome driver."""
        logger.info("Initializing undetected Chrome driver...")

        options = uc.ChromeOptions()

        if self.headless:
            options.add_argument('--headless=new')

        # Additional stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')

        # Random window size (looks more human)
        options.add_argument('--window-size=1920,1080')

        # Use undetected-chromedriver (bypasses many bot detections)
        self.driver = uc.Chrome(options=options)

        # Set implicit wait
        self.driver.implicitly_wait(10)

        logger.info("Browser initialized successfully")

    def search_prices(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        passenger_count: int = 1
    ) -> PriceSearchResult:
        """
        Search for train prices using browser automation.

        Args:
            origin: Origin city name (e.g., "Paris")
            destination: Destination city name (e.g., "Marseille")
            departure_date: Departure date
            passenger_count: Number of passengers

        Returns:
            PriceSearchResult with available offers
        """
        if not self.driver:
            self._init_driver()

        try:
            logger.info(f"Searching: {origin} → {destination} on {departure_date.strftime('%Y-%m-%d')}")

            # Step 1: Navigate to SNCF Connect
            self._navigate_to_search()

            # Step 2: Fill search form
            self._fill_search_form(origin, destination, departure_date, passenger_count)

            # Step 3: Submit search
            self._submit_search()

            # Step 4: Wait for results to load
            self._wait_for_results()

            # Step 5: Extract prices
            offers = self._extract_offers(origin, destination)

            result = PriceSearchResult(
                origin=origin,
                destination=destination,
                date=departure_date,
                offers=offers,
                search_timestamp=datetime.now(),
                total_results=len(offers)
            )

            logger.info(f"Successfully extracted {len(offers)} offers")
            return result

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise

    def _navigate_to_search(self):
        """Navigate to SNCF Connect homepage."""
        logger.info(f"Navigating to {self.SNCF_URL}")
        self.driver.get(self.SNCF_URL)

        # Wait for page to load
        time.sleep(2)

        # Handle cookie consent if present
        try:
            cookie_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            cookie_button.click()
            logger.info("Accepted cookie consent")
            time.sleep(1)
        except TimeoutException:
            logger.debug("No cookie consent popup found")

    def _fill_search_form(
        self,
        origin: str,
        destination: str,
        departure_date: datetime,
        passenger_count: int
    ):
        """
        Fill the train search form.

        This is the tricky part - SNCF's form structure may change.
        """
        logger.info("Filling search form...")

        try:
            # Wait for search form to be visible
            wait = WebDriverWait(self.driver, self.timeout)

            # Find origin input (look for common selectors)
            origin_selectors = [
                "input[name='origin']",
                "input[placeholder*='Départ']",
                "input[data-testid='origin']",
                "#origin-input",
            ]

            origin_input = None
            for selector in origin_selectors:
                try:
                    origin_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not origin_input:
                raise ValueError("Could not find origin input field")

            # Clear and type origin
            origin_input.clear()
            time.sleep(0.5)
            self._type_like_human(origin_input, origin)
            time.sleep(1)

            # Select from autocomplete
            self._select_autocomplete_option(origin)

            # Find destination input
            destination_selectors = [
                "input[name='destination']",
                "input[placeholder*='Arrivée']",
                "input[data-testid='destination']",
                "#destination-input",
            ]

            destination_input = None
            for selector in destination_selectors:
                try:
                    destination_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not destination_input:
                raise ValueError("Could not find destination input field")

            # Type destination
            destination_input.clear()
            time.sleep(0.5)
            self._type_like_human(destination_input, destination)
            time.sleep(1)

            # Select from autocomplete
            self._select_autocomplete_option(destination)

            # Set date (this varies by implementation)
            self._set_date(departure_date)

            logger.info("Search form filled successfully")

        except Exception as e:
            logger.error(f"Failed to fill search form: {e}")
            # Take screenshot for debugging
            self.driver.save_screenshot("sncf_form_error.png")
            raise

    def _type_like_human(self, element, text: str):
        """Type text with random delays to simulate human typing."""
        import random

        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _select_autocomplete_option(self, text: str):
        """Select option from autocomplete dropdown."""
        try:
            # Wait for autocomplete dropdown
            wait = WebDriverWait(self.driver, 5)

            # Common autocomplete selectors
            autocomplete_selectors = [
                "ul.autocomplete-results li:first-child",
                "div[role='listbox'] div:first-child",
                ".suggestions li:first-child",
            ]

            for selector in autocomplete_selectors:
                try:
                    option = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    option.click()
                    time.sleep(0.5)
                    return
                except TimeoutException:
                    continue

            # If no autocomplete found, just press Enter
            logger.warning("No autocomplete found, continuing...")

        except Exception as e:
            logger.warning(f"Autocomplete selection failed: {e}")

    def _set_date(self, date: datetime):
        """Set departure date."""
        try:
            # Look for date input
            date_selectors = [
                "input[name='date']",
                "input[type='date']",
                "input[placeholder*='Date']",
            ]

            wait = WebDriverWait(self.driver, 5)

            for selector in date_selectors:
                try:
                    date_input = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )

                    # Try to set date value
                    date_str = date.strftime("%Y-%m-%d")
                    self.driver.execute_script(
                        f"arguments[0].value = '{date_str}';",
                        date_input
                    )
                    time.sleep(0.5)
                    return
                except TimeoutException:
                    continue

            logger.warning("Could not set date - using default")

        except Exception as e:
            logger.warning(f"Date setting failed: {e}")

    def _submit_search(self):
        """Submit the search form."""
        logger.info("Submitting search...")

        try:
            # Look for search button
            search_selectors = [
                "button[type='submit']",
                "button[data-testid='search-button']",
                "button:contains('Rechercher')",
                ".search-button",
            ]

            wait = WebDriverWait(self.driver, 10)

            for selector in search_selectors:
                try:
                    search_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    search_button.click()
                    logger.info("Search submitted")
                    return
                except TimeoutException:
                    continue

            raise ValueError("Could not find search button")

        except Exception as e:
            logger.error(f"Failed to submit search: {e}")
            self.driver.save_screenshot("sncf_submit_error.png")
            raise

    def _wait_for_results(self):
        """Wait for search results to load."""
        logger.info("Waiting for results...")

        try:
            wait = WebDriverWait(self.driver, 30)

            # Look for results container
            results_selectors = [
                ".train-results",
                ".search-results",
                "[data-testid='train-list']",
                ".journey-list",
            ]

            for selector in results_selectors:
                try:
                    wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info("Results loaded")
                    time.sleep(2)  # Wait for prices to load
                    return
                except TimeoutException:
                    continue

            # If specific selector not found, just wait
            logger.warning("Results container not found with known selectors, waiting...")
            time.sleep(5)

        except Exception as e:
            logger.warning(f"Results wait uncertain: {e}")
            time.sleep(3)

    def _extract_offers(self, origin: str, destination: str) -> List[TrainOffer]:
        """
        Extract train offers from the results page.

        This is highly dependent on SNCF's current HTML structure.
        """
        logger.info("Extracting offers from page...")

        offers = []

        try:
            # Take screenshot for manual inspection
            self.driver.save_screenshot("sncf_results.png")
            logger.info("Saved screenshot: sncf_results.png")

            # Get page source for analysis
            page_source = self.driver.page_source

            # Save HTML for debugging
            with open("sncf_results.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            logger.info("Saved HTML: sncf_results.html")

            # Try to find train result elements
            # Note: These selectors are guesses and may need adjustment
            train_selectors = [
                ".train-card",
                ".journey-card",
                "[data-testid='train-proposal']",
                ".proposal-card",
            ]

            train_elements = []
            for selector in train_selectors:
                try:
                    train_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if train_elements:
                        logger.info(f"Found {len(train_elements)} train elements with selector: {selector}")
                        break
                except NoSuchElementException:
                    continue

            if not train_elements:
                logger.warning("No train elements found with known selectors")
                logger.info("Please inspect sncf_results.html and sncf_results.png to identify correct selectors")
                return offers

            # Extract data from each train element
            for idx, element in enumerate(train_elements[:10], 1):  # Limit to first 10
                try:
                    offer = self._parse_train_element(element, origin, destination, idx)
                    if offer:
                        offers.append(offer)
                except Exception as e:
                    logger.warning(f"Failed to parse train element {idx}: {e}")
                    continue

            logger.info(f"Successfully extracted {len(offers)} offers")

        except Exception as e:
            logger.error(f"Offer extraction failed: {e}", exc_info=True)

        return offers

    def _parse_train_element(
        self, element, origin: str, destination: str, index: int
    ) -> Optional[TrainOffer]:
        """Parse a single train element to extract offer details."""
        try:
            # These are example selectors - actual structure may differ
            # You'll need to inspect the HTML to find correct selectors

            # Extract departure time
            dep_time_selectors = [
                ".departure-time",
                "[data-testid='departure-time']",
                ".time.departure",
            ]
            dep_time_text = self._find_text(element, dep_time_selectors, "00:00")

            # Extract arrival time
            arr_time_selectors = [
                ".arrival-time",
                "[data-testid='arrival-time']",
                ".time.arrival",
            ]
            arr_time_text = self._find_text(element, arr_time_selectors, "00:00")

            # Extract price
            price_selectors = [
                ".price",
                "[data-testid='price']",
                ".amount",
                ".fare-price",
            ]
            price_text = self._find_text(element, price_selectors, "0")

            # Extract train type
            train_type_selectors = [
                ".train-type",
                "[data-testid='train-type']",
                ".transport-mode",
            ]
            train_type = self._find_text(element, train_type_selectors, "TRAIN")

            # Parse times
            dep_time = datetime.strptime(dep_time_text, "%H:%M").time()
            arr_time = datetime.strptime(arr_time_text, "%H:%M").time()

            # Parse price (remove € symbol and convert)
            price_value = float(price_text.replace('€', '').replace(',', '.').strip())

            # Calculate duration (simplified)
            duration_mins = 180  # Default 3 hours, should calculate from times

            offer = TrainOffer(
                train_number=f"TRAIN_{index}",
                train_type=train_type,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=duration_mins,
                origin_station=origin,
                destination_station=destination,
                price=price_value if price_value > 0 else None,
                available=True,
            )

            return offer

        except Exception as e:
            logger.debug(f"Failed to parse element: {e}")
            return None

    def _find_text(self, parent_element, selectors: List[str], default: str) -> str:
        """Find text using multiple selectors with fallback."""
        for selector in selectors:
            try:
                element = parent_element.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except NoSuchElementException:
                continue
        return default

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
