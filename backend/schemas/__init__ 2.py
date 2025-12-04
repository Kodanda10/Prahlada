# Backend Schemas Package
# This package contains all Pydantic schemas for the API

from .event_schema import EventObject, NLQResponse, QuerySpec, LocationDetail, Announcements, Narrative

# Import legacy schemas from schemas_legacy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.schemas_legacy import *

__all__ = [
    # New event schemas
    "EventObject",
    "NLQResponse", 
    "QuerySpec",
    "LocationDetail",
    "Announcements",
    "Narrative",
]
