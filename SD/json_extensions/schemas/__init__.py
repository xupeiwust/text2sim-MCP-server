"""
JSON Schema definitions for PySD abstract models.
"""

from pathlib import Path
import json

def get_schema_path(version: str = "v2") -> Path:
    """Get path to schema file."""
    return Path(__file__).parent / f"abstract_model_{version}.json"

def load_schema(version: str = "v2") -> dict:
    """Load schema as dictionary."""
    with open(get_schema_path(version), 'r') as f:
        return json.load(f)

__all__ = ["get_schema_path", "load_schema"]