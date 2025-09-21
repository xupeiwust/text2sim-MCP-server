"""
PySD JSON Extensions for Text2Sim MCP Server

This module provides the essential PySD JSON Schema extensions extracted from
the pysd-json project for integration with the Text2Sim MCP server.

Key Components:
- adapters: JSON ↔ PySD dataclass conversion
- schema: Validation and serialization system
- schemas: JSON Schema definitions
- utils: Helper utilities

These extensions enable the Text-to-JSON-to-PySD workflow for System Dynamics
modeling within the MCP server environment.
"""

from .adapters.abstract_model_adapter import (
    AbstractModelAdapter,
    AbstractSectionAdapter,
    AbstractElementAdapter,
    AbstractComponentAdapter,
    AbstractSyntaxAdapter
)

from .schema.validator import SchemaValidator, ValidationResult, ValidationError
from .schema.serialization import ModelSerializer

__all__ = [
    "AbstractModelAdapter",
    "AbstractSectionAdapter",
    "AbstractElementAdapter",
    "AbstractComponentAdapter",
    "AbstractSyntaxAdapter",
    "SchemaValidator",
    "ValidationResult",
    "ValidationError",
    "ModelSerializer"
]