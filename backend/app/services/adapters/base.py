from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import datetime

class BaseSourceAdapter(ABC):
    """
    Abstract Base Class for Veloxa Data Room Source Adapters.
    Defines the contract for parsing or loading data room release assets.
    """

    def __init__(self, file_name: str, release_day: str = "Day1", released_at: Optional[datetime.datetime] = None):
        self.file_name = file_name
        self.release_day = release_day
        self.released_at = released_at or datetime.datetime(2026, 11, 16, 10, 0, 0)

    @abstractmethod
    def get_source_metadata(self) -> Dict[str, Any]:
        """Returns metadata dictionary for the Source record."""
        pass

    @abstractmethod
    def extract_evidence(self) -> List[Dict[str, Any]]:
        """Extracts structured evidence items with exact sheet/page and row citations."""
        pass
