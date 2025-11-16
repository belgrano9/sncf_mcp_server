"""Data models for SNCF price scraper."""

from datetime import datetime, time
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class TrainOffer:
    """Represents a single train offer with pricing."""

    # Journey details
    train_number: str
    train_type: str  # TGV, TER, Intercités, etc.
    departure_time: time
    arrival_time: time
    duration_minutes: int

    # Station details
    origin_station: str
    destination_station: str

    # Pricing
    price: Optional[float] = None  # In euros
    currency: str = "EUR"
    available: bool = True
    fare_class: Optional[str] = None  # 1st, 2nd class
    fare_type: Optional[str] = None  # Standard, Flexible, etc.

    # Additional info
    transfers: int = 0
    comfort_class: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "train_number": self.train_number,
            "train_type": self.train_type,
            "departure_time": self.departure_time.strftime("%H:%M"),
            "arrival_time": self.arrival_time.strftime("%H:%M"),
            "duration_minutes": self.duration_minutes,
            "origin_station": self.origin_station,
            "destination_station": self.destination_station,
            "price": self.price,
            "currency": self.currency,
            "available": self.available,
            "fare_class": self.fare_class,
            "fare_type": self.fare_type,
            "transfers": self.transfers,
            "comfort_class": self.comfort_class,
        }


@dataclass
class PriceSearchResult:
    """Results from a price search."""

    origin: str
    destination: str
    date: datetime
    offers: List[TrainOffer]
    search_timestamp: datetime
    total_results: int

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "date": self.date.strftime("%Y-%m-%d"),
            "offers": [offer.to_dict() for offer in self.offers],
            "search_timestamp": self.search_timestamp.isoformat(),
            "total_results": self.total_results,
        }
