"""
Multi-Schema Validator for Text2Sim Model Builder.

This module provides generic validation capabilities for any simulation schema,
with LLM-optimized error messages and flexible validation modes.
"""

import json
import jsonschema
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .schema_registry import schema_registry
from DES.schema_validator import DESConfigValidator


@dataclass
class ValidationError:
    """Structured validation error with LLM-optimized information."""
    path: str
    message: str
    current_value: Any = None
    expected: str = ""
    quick_fix: str = ""
    example: Dict[str, Any] = None
    schema_reference: str = ""


@dataclass
class ValidationResult:
    """Complete validation result with actionable feedback."""
    valid: bool
    schema_type: str
    validation_mode: str
    completeness: float
    errors: List[ValidationError]
    missing_required: List[Dict[str, Any]]
    suggestions: List[str]
    next_steps: List[str]


class MultiSchemaValidator:
    """
    Generic validator that works with any registered simulation schema.
    
    Provides LLM-optimized validation with detailed error messages,
    quick fixes, and actionable suggestions for model improvement.
    """
    
    def __init__(self):
        """Initialize the multi-schema validator."""
        self.registry = schema_registry
        self._validators = {}
        self._initialize_validators()
    
    def _initialize_validators(self):
        """Initialize specific validators for each schema type."""
        # Initialize DES validator
        try:
            self._validators["DES"] = DESConfigValidator()
        except Exception as e:
            print(f"Warning: Could not initialize DES validator: {e}")
        
        # Future: Initialize SD validator when available
        # self._validators["SD"] = SDConfigValidator()
    
    def validate_model(
        self,
        model: Dict[str, Any],
        schema_type: Optional[str] = None,
        validation_mode: str = "partial"
    ) -> ValidationResult:
        """
        Validate a simulation model against appropriate schema.
        
        Args:
            model: The model dictionary to validate
            schema_type: Optional schema type override (auto-detected if None)
            validation_mode: "partial", "strict", or "structure"
            
        Returns:
            ValidationResult with comprehensive feedback
        """
        # Detect schema type if not provided
        if schema_type is None:
            detected_type, confidence = self.registry.detect_schema_type(model)
            if detected_type is None:
                return ValidationResult(
                    valid=False,
                    schema_type="unknown",
                    validation_mode=validation_mode,
                    completeness=0.0,
                    errors=[ValidationError(
                        path="root",
                        message="Could not detect schema type from model structure",
                        quick_fix="Add 'schema_type' field or include required sections",
                        suggestions=["Add entity_types for DES", "Add stocks/flows for SD"]
                    )],
                    missing_required=[],
                    suggestions=["Specify schema_type explicitly in model"],
                    next_steps=["Add schema_type field or required sections"]
                )
            schema_type = detected_type
        
        # Check if schema is available
        if not self.registry.validate_schema_availability(schema_type):
            return ValidationResult(
                valid=False,
                schema_type=schema_type,
                validation_mode=validation_mode,
                completeness=0.0,
                errors=[ValidationError(
                    path="schema",
                    message=f"Schema type '{schema_type}' is not available or schema file not found",
                    quick_fix=f"Use available schema types: {self.registry.get_available_schemas()}"
                )],
                missing_required=[],
                suggestions=[f"Available schemas: {', '.join(self.registry.get_available_schemas())}"],
                next_steps=["Choose an available schema type"]
            )
        
        # Use specialized validator if available
        if schema_type in self._validators:
            return self._validate_with_specialized_validator(
                model, schema_type, validation_mode
            )
        else:
            return self._validate_with_generic_validator(
                model, schema_type, validation_mode
            )
    
    def _validate_with_specialized_validator(
        self,
        model: Dict[str, Any],
        schema_type: str,
        validation_mode: str
    ) -> ValidationResult:
        """Validate using a specialized validator (e.g., DESConfigValidator)."""
        validator = self._validators[schema_type]
        
        if schema_type == "DES":
            # Use existing DES validator
            normalized_config, errors = validator.validate_and_normalize(model)
            
            # Convert to our ValidationResult format
            validation_errors = []
            for error_msg in errors:
                validation_errors.append(self._parse_des_error(error_msg))
            
            # Calculate completeness
            completeness = self._calculate_completeness(model, schema_type)
            
            # Generate suggestions and next steps
            suggestions = self._generate_suggestions(model, schema_type, validation_errors)
            next_steps = self._generate_next_steps(validation_errors, completeness)
            
            return ValidationResult(
                valid=len(errors) == 0,
                schema_type=schema_type,
                validation_mode=validation_mode,
                completeness=completeness,
                errors=validation_errors,
                missing_required=self._find_missing_required(model, schema_type),
                suggestions=suggestions,
                next_steps=next_steps
            )
        
        # Fallback for other specialized validators
        return self._validate_with_generic_validator(model, schema_type, validation_mode)
    
    def _validate_with_generic_validator(
        self,
        model: Dict[str, Any],
        schema_type: str,
        validation_mode: str
    ) -> ValidationResult:
        """Validate using generic JSON Schema validation."""
        schema = self.registry.load_schema(schema_type)
        if not schema:
            return ValidationResult(
                valid=False,
                schema_type=schema_type,
                validation_mode=validation_mode,
                completeness=0.0,
                errors=[ValidationError(
                    path="schema",
                    message=f"Could not load schema for type '{schema_type}'"
                )],
                missing_required=[],
                suggestions=[],
                next_steps=[]
            )
        
        try:
            # Validate against JSON Schema
            if validation_mode == "strict":
                jsonschema.validate(model, schema)
            elif validation_mode == "partial":
                # Only validate provided sections
                self._validate_partial(model, schema)
            elif validation_mode == "structure":
                # Only validate structure, not business rules
                self._validate_structure(model, schema)
            
            return ValidationResult(
                valid=True,
                schema_type=schema_type,
                validation_mode=validation_mode,
                completeness=self._calculate_completeness(model, schema_type),
                errors=[],
                missing_required=self._find_missing_required(model, schema_type),
                suggestions=self._generate_suggestions(model, schema_type, []),
                next_steps=[]
            )
            
        except jsonschema.ValidationError as e:
            validation_error = self._format_jsonschema_error(e)
            
            return ValidationResult(
                valid=False,
                schema_type=schema_type,
                validation_mode=validation_mode,
                completeness=self._calculate_completeness(model, schema_type),
                errors=[validation_error],
                missing_required=self._find_missing_required(model, schema_type),
                suggestions=self._generate_suggestions(model, schema_type, [validation_error]),
                next_steps=self._generate_next_steps([validation_error], 0.5)
            )
    
    def _parse_des_error(self, error_msg: str) -> ValidationError:
        """Parse DES validator error message into structured format."""
        # This is a simplified parser - could be enhanced based on actual DES error formats
        return ValidationError(
            path="unknown",
            message=error_msg,
            quick_fix="Check the error message for specific guidance",
            example={}
        )
    
    def _format_jsonschema_error(self, error: jsonschema.ValidationError) -> ValidationError:
        """Format JSON Schema validation error for LLM consumption."""
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        
        return ValidationError(
            path=path,
            message=error.message,
            current_value=getattr(error, 'instance', None),
            schema_reference=path,
            quick_fix=self._generate_quick_fix(error),
            example=self._generate_example_for_error(error)
        )
    
    def _generate_quick_fix(self, error: jsonschema.ValidationError) -> str:
        """Generate a quick fix suggestion for a JSON Schema error."""
        if "required property" in error.message:
            missing_prop = error.message.split("'")[1]
            return f"Add required property '{missing_prop}'"
        elif "not of type" in error.message:
            return "Check the data type of this field"
        elif "does not match" in error.message:
            return "Check the format/pattern of this field"
        else:
            return "Review the field value against schema requirements"
    
    def _generate_example_for_error(self, error: jsonschema.ValidationError) -> Dict[str, Any]:
        """Generate an example for fixing a JSON Schema error."""
        # This would be enhanced with specific examples based on error type
        return {}
    
    def _calculate_completeness(self, model: Dict[str, Any], schema_type: str) -> float:
        """Calculate how complete a model is (0.0 to 1.0)."""
        schema_info = self.registry.get_schema_info(schema_type)
        if not schema_info:
            return 0.0
        
        # Simple completeness based on presence of key indicators
        indicators = schema_info.indicators
        present_indicators = sum(1 for indicator in indicators if self._has_nested_key(model, indicator))
        
        base_completeness = present_indicators / len(indicators) if indicators else 0.0
        
        # Adjust based on depth of provided sections
        depth_bonus = min(0.3, len(model.keys()) * 0.05)  # Up to 30% bonus for depth
        
        return min(1.0, base_completeness + depth_bonus)
    
    def _has_nested_key(self, data: dict, key_path: str) -> bool:
        """Check if a nested key exists in the data."""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False
        
        return True
    
    def _find_missing_required(self, model: Dict[str, Any], schema_type: str) -> List[Dict[str, Any]]:
        """Find missing required fields based on schema."""
        missing = []
        schema_info = self.registry.get_schema_info(schema_type)
        
        if schema_info:
            for indicator in schema_info.indicators:
                if not self._has_nested_key(model, indicator):
                    missing.append({
                        "path": indicator,
                        "description": f"Required section for {schema_type} models",
                        "example": self._get_example_for_section(schema_type, indicator)
                    })
        
        return missing
    
    def _get_example_for_section(self, schema_type: str, section: str) -> Any:
        """Get an example for a specific schema section."""
        # This would be enhanced with actual examples from schema or templates
        examples = {
            "DES": {
                "entity_types": {"customer": {"probability": 1.0}},
                "resources": {"server": {"capacity": 1}},
                "processing_rules": {"steps": ["server"]}
            }
        }
        
        return examples.get(schema_type, {}).get(section, {})
    
    def _generate_suggestions(
        self,
        model: Dict[str, Any],
        schema_type: str,
        errors: List[ValidationError]
    ) -> List[str]:
        """Generate helpful suggestions for improving the model."""
        suggestions = []
        
        # Schema-specific suggestions
        if schema_type == "DES":
            if not self._has_nested_key(model, "entity_types"):
                suggestions.append("Add entity_types to define different types of entities")
            if not self._has_nested_key(model, "resources"):
                suggestions.append("Add resources to define system capacity")
            if not self._has_nested_key(model, "processing_rules"):
                suggestions.append("Add processing_rules to define entity flow")
        
        # Error-based suggestions
        for error in errors:
            if "probability" in error.path and "sum" in error.message:
                suggestions.append("Adjust entity type probabilities to sum to 1.0")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _generate_next_steps(self, errors: List[ValidationError], completeness: float) -> List[str]:
        """Generate prioritized next steps for model development."""
        next_steps = []
        
        # Prioritize critical errors
        critical_errors = [e for e in errors if "required" in e.message.lower()]
        for error in critical_errors[:3]:  # Top 3 critical errors
            next_steps.append(f"Fix: {error.quick_fix}")
        
        # Suggest next development phase based on completeness
        if completeness < 0.3:
            next_steps.append("Add basic required sections to establish model structure")
        elif completeness < 0.7:
            next_steps.append("Add advanced features like balking, reneging, or routing")
        elif completeness < 1.0:
            next_steps.append("Fine-tune parameters and add optional features")
        
        return next_steps[:5]  # Limit to top 5 next steps
    
    def _validate_partial(self, model: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate only the sections that are present in the model."""
        # This would implement partial validation logic
        # For now, use standard validation
        jsonschema.validate(model, schema)
    
    def _validate_structure(self, model: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate only the structure, not business rules."""
        # This would implement structure-only validation
        # For now, use standard validation
        jsonschema.validate(model, schema)
