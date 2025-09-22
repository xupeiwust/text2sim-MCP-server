"""
Schema Registry for Multi-Schema Validation System.

This module manages the registry of available simulation schemas and provides
auto-detection capabilities for determining schema types from model structure.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class SchemaInfo:
    """Information about a registered schema."""
    schema_type: str
    schema_path: Path
    indicators: List[str]
    validator_class: str
    description: str
    version: str = "1.0"


class SchemaRegistry:
    """
    Registry for managing multiple simulation schemas.
    
    Provides auto-detection capabilities and schema metadata management
    for different simulation paradigms (DES, SD, future ABM, etc.).
    """
    
    def __init__(self):
        """Initialize the schema registry with known schema types."""
        self.schemas: Dict[str, SchemaInfo] = {}
        self._loaded_schemas: Dict[str, dict] = {}
        self._initialize_schemas()
    
    def _initialize_schemas(self):
        """Initialize the registry with known schema types."""
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Register DES schema
        des_schema_path = project_root / "schemas" / "DES" / "des-simpy-compatible-schema.json"
        self.register_schema(SchemaInfo(
            schema_type="DES",
            schema_path=des_schema_path,
            indicators=["entity_types", "resources", "processing_rules"],
            validator_class="DESConfigValidator",
            description="Discrete-Event Simulation using SimPy",
            version="2.0"
        ))
        
        # Register SD schema
        sd_schema_path = project_root.parent / "SD" / "json_extensions" / "schemas" / "abstract_model_v2.json"
        self.register_schema(SchemaInfo(
            schema_type="SD",
            schema_path=sd_schema_path,
            indicators=["abstractModel", "model.abstractModel", "template_info.schema_type=SD"],
            validator_class="PySDJSONIntegration",
            description="System Dynamics simulation using PySD-compatible JSON extensions",
            version="2.0"
        ))
    
    def register_schema(self, schema_info: SchemaInfo) -> None:
        """
        Register a new schema type.
        
        Args:
            schema_info: Schema information to register
        """
        self.schemas[schema_info.schema_type] = schema_info
    
    def get_schema_info(self, schema_type: str) -> Optional[SchemaInfo]:
        """
        Get schema information for a specific type.
        
        Args:
            schema_type: The schema type to look up
            
        Returns:
            SchemaInfo object or None if not found
        """
        return self.schemas.get(schema_type)
    
    def load_schema(self, schema_type: str) -> Optional[dict]:
        """
        Load and return the JSON schema for a specific type.
        
        Args:
            schema_type: The schema type to load
            
        Returns:
            Loaded JSON schema or None if not found/error
        """
        if schema_type in self._loaded_schemas:
            return self._loaded_schemas[schema_type]
        
        schema_info = self.get_schema_info(schema_type)
        if not schema_info:
            return None
        
        try:
            if schema_info.schema_path.exists():
                with open(schema_info.schema_path, 'r') as f:
                    schema = json.load(f)
                self._loaded_schemas[schema_type] = schema
                return schema
            else:
                # Schema file doesn't exist yet (e.g., SD schema)
                return None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading schema {schema_type}: {e}")
            return None
    
    def detect_schema_type(self, model: dict) -> Tuple[Optional[str], float]:
        """
        Auto-detect schema type from model structure.
        
        Args:
            model: The model dictionary to analyze
            
        Returns:
            Tuple of (detected_schema_type, confidence_score)
            Returns (None, 0.0) if no schema type detected
        """
        # Check for explicit schema declaration
        if "schema_type" in model:
            declared_type = model["schema_type"]
            if declared_type in self.schemas:
                return declared_type, 1.0
        
        # Analyze structure for known patterns
        best_match = None
        best_score = 0.0
        
        for schema_type, schema_info in self.schemas.items():
            score = self._calculate_match_score(model, schema_info.indicators)
            if score > best_score:
                best_score = score
                best_match = schema_type
        
        # Only return match if confidence is above threshold
        if best_score >= 0.3:  # Minimum 30% confidence
            return best_match, best_score
        
        return None, 0.0
    
    def _calculate_match_score(self, model: dict, indicators: List[str]) -> float:
        """
        Calculate how well a model matches a schema's indicators.
        
        Args:
            model: The model to analyze
            indicators: List of key indicators for the schema
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if not indicators:
            return 0.0
        
        matches = 0
        for indicator in indicators:
            if self._has_nested_key(model, indicator):
                matches += 1
        
        return matches / len(indicators)
    
    def _has_nested_key(self, data: dict, key_path: str) -> bool:
        """
        Check if a nested key exists in the data.

        Args:
            data: Dictionary to search
            key_path: Dot-separated path (e.g., "processing_rules.steps") or
                     value check (e.g., "template_info.schema_type=SD")

        Returns:
            True if the key path exists or value matches
        """
        # Handle value check patterns (e.g., "template_info.schema_type=SD")
        if '=' in key_path:
            path, expected_value = key_path.split('=', 1)
            keys = path.split('.')
            current = data

            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False

            return str(current) == expected_value

        # Handle normal nested key checking
        keys = key_path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False

        return True
    
    def get_available_schemas(self) -> List[str]:
        """
        Get list of available schema types.
        
        Returns:
            List of schema type names
        """
        return list(self.schemas.keys())
    
    def get_schema_indicators(self, schema_type: str) -> List[str]:
        """
        Get the structural indicators for a schema type.
        
        Args:
            schema_type: The schema type to query
            
        Returns:
            List of indicator keys for the schema
        """
        schema_info = self.get_schema_info(schema_type)
        return schema_info.indicators if schema_info else []
    
    def validate_schema_availability(self, schema_type: str) -> bool:
        """
        Check if a schema type is available and its file exists.
        
        Args:
            schema_type: The schema type to check
            
        Returns:
            True if schema is available and file exists
        """
        schema_info = self.get_schema_info(schema_type)
        if not schema_info:
            return False
        
        return schema_info.schema_path.exists()


# Global registry instance
schema_registry = SchemaRegistry()
