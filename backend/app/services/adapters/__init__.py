from backend.app.services.adapters.base import BaseSourceAdapter
from backend.app.services.adapters.document_adapters import (
    TextManifestAdapter,
    TranscriptAdapter,
    BoardUpdateAdapter,
    EmailAdapter,
    SpreadsheetAdapter,
    ResignationLetterAdapter,
)

__all__ = [
    "BaseSourceAdapter",
    "TextManifestAdapter",
    "TranscriptAdapter",
    "BoardUpdateAdapter",
    "EmailAdapter",
    "SpreadsheetAdapter",
    "ResignationLetterAdapter",
]
