"""
SNCF Price Scraper Implementation

⚠️ EDUCATIONAL PROOF OF CONCEPT ONLY ⚠️

This scraper attempts to extract price information from SNCF's booking system.
It may:
- Violate SNCF's Terms of Service
- Break when SNCF updates their website
- Be blocked by anti-scraping measures
- Not work in production environments

For production use, please use:
- Official SNCF APIs (if available)
- Commercial providers (e.g., Lyko, Trainline)
- Licensed reseller partnerships
"""

import logging
import time
from datetime import datetime, time as dt_time
from typing import List, Optional
import httpx
import json

from .models import TrainOffer, PriceSearchResult

logger = logging.getLogger(__name__)


class SNCFPriceScraper:
    """
    Experimental SNCF price scraper.

    This is a proof-of-concept that attempts to scrape prices from SNCF.
    It uses the SNCF Connect (formerly Oui.sncf) booking API.
    """

    # SNCF Connect API endpoints (may change)
    BASE_URL = "https://www.sncf-connect.com"
    API_BASE = "https://www.sncf-connect.com/bff/api/v1"

    # User agent to avoid immediate blocking
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 30):
        """
        Initialize the scraper.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout

        # HTTP client with realistic headers
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": self.BASE_URL,
                "Origin": self.BASE_URL,
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        )

    def search_prices(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: datetime,
        passenger_count: int = 1
    ) -> PriceSearchResult:
        """
        Search for train prices.

        Args:
            origin_code: Origin station code (e.g., "FRPNO" for Paris Nord)
            destination_code: Destination station code
            departure_date: Departure date
            passenger_count: Number of passengers (default: 1)

        Returns:
            PriceSearchResult with available offers

        Raises:
            httpx.HTTPError: On network errors
            ValueError: On parsing errors
        """
        logger.info(
            f"Searching prices: {origin_code} → {destination_code} on {departure_date.strftime('%Y-%m-%d')}"
        )

        try:
            # Step 1: Attempt to use the search API
            offers = self._fetch_offers(
                origin_code, destination_code, departure_date, passenger_count
            )

            result = PriceSearchResult(
                origin=origin_code,
                destination=destination_code,
                date=departure_date,
                offers=offers,
                search_timestamp=datetime.now(),
                total_results=len(offers),
            )

            logger.info(f"Found {len(offers)} train offers")
            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("Access forbidden - anti-scraping measures detected")
                raise ValueError(
                    "SNCF has blocked the request. This scraper may not work due to anti-bot measures. "
                    "Consider using official APIs or commercial providers."
                )
            elif e.response.status_code == 404:
                logger.error("API endpoint not found - SNCF may have changed their API")
                raise ValueError(
                    "SNCF API endpoint not found. The website structure may have changed. "
                    "This scraper needs to be updated."
                )
            else:
                logger.error(f"HTTP error: {e}")
                raise

        except Exception as e:
            logger.error(f"Unexpected error during price scraping: {e}", exc_info=True)
            raise

    def _fetch_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: datetime,
        passenger_count: int
    ) -> List[TrainOffer]:
        """
        Fetch train offers from SNCF API.

        Note: This is a simplified implementation. The actual SNCF API
        may require additional steps like:
        - Authentication/session tokens
        - Multi-step booking flow
        - CSRF tokens
        - Complex request payloads

        Returns:
            List of TrainOffer objects
        """
        # Format date for API
        date_str = departure_date.strftime("%Y-%m-%d")

        # Construct search parameters (this is a guess - real API may differ)
        params = {
            "origin": origin_code,
            "destination": destination_code,
            "outwardDate": date_str,
            "passengers": str(passenger_count),
            "directTravel": "false",
            "travelClass": "SECOND",  # or FIRST
        }

        # Attempt to call a potential search endpoint
        # Note: This URL is speculative and may not work
        search_url = f"{self.API_BASE}/travel-offers/search"

        logger.debug(f"Attempting to fetch from: {search_url}")
        logger.debug(f"Parameters: {params}")

        # Add a small delay to be respectful
        time.sleep(1)

        try:
            response = self.client.get(search_url, params=params)
            response.raise_for_status()

            # Try to parse JSON response
            data = response.json()

            # Parse the response into TrainOffer objects
            offers = self._parse_offers(data, origin_code, destination_code)

            return offers

        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to fetch offers: HTTP {e.response.status_code}")
            logger.debug(f"Response body: {e.response.text[:500]}")
            raise

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response.text[:500]}")
            # Return empty list instead of crashing
            return []

    def _parse_offers(
        self, data: dict, origin: str, destination: str
    ) -> List[TrainOffer]:
        """
        Parse API response into TrainOffer objects.

        Note: This is highly speculative as the actual SNCF API
        response structure is unknown.

        Args:
            data: JSON response from API
            origin: Origin station code
            destination: Destination station code

        Returns:
            List of TrainOffer objects
        """
        offers = []

        # This is a guess at the response structure
        # Real SNCF API will have different field names
        travel_offers = data.get("travelOffers", []) or data.get("offers", []) or data.get("journeys", [])

        for offer_data in travel_offers:
            try:
                # Extract journey details (field names are guesses)
                train_number = offer_data.get("trainNumber", "UNKNOWN")
                train_type = offer_data.get("trainType", "TRAIN")

                # Parse times
                dep_time_str = offer_data.get("departureTime", "00:00")
                arr_time_str = offer_data.get("arrivalTime", "00:00")

                dep_time = datetime.strptime(dep_time_str, "%H:%M").time()
                arr_time = datetime.strptime(arr_time_str, "%H:%M").time()

                # Duration
                duration = offer_data.get("durationMinutes", 0)

                # Price
                price_data = offer_data.get("price", {})
                price = float(price_data.get("amount", 0))

                # Availability
                available = offer_data.get("available", True)

                offer = TrainOffer(
                    train_number=train_number,
                    train_type=train_type,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    duration_minutes=duration,
                    origin_station=origin,
                    destination_station=destination,
                    price=price if price > 0 else None,
                    available=available,
                    fare_class=offer_data.get("fareClass"),
                    fare_type=offer_data.get("fareType"),
                )

                offers.append(offer)

            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse offer: {e}")
                logger.debug(f"Offer data: {offer_data}")
                continue

        return offers

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
