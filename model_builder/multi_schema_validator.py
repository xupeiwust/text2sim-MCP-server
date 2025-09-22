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

# Import SD integration
try:
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    sys.path.append(str(current_dir.parent.parent))
    from SD.sd_integration import PySDJSONIntegration
    SD_INTEGRATION_AVAILABLE = True
except ImportError:
    SD_INTEGRATION_AVAILABLE = False


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

        # Initialize SD validator
        if SD_INTEGRATION_AVAILABLE:
            try:
                self._validators["SD"] = PySDJSONIntegration()
            except Exception as e:
                print(f"Warning: Could not initialize SD validator: {e}")
        else:
            print("Warning: SD integration not available")
    
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
                        quick_fix="Add 'schema_type' field or include required sections"
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

        elif schema_type == "SD":
            # Use SD validator (PySDJSONIntegration)
            # Handle different input formats - template vs raw model
            model_to_validate = model

            if isinstance(model, dict):
                if "template_info" in model and "model" in model:
                    # Full template format - extract model section
                    model_to_validate = model["model"]
                elif "abstractModel" in model:
                    # Direct model format
                    model_to_validate = model
                elif "sections" in model:
                    # Direct abstractModel format
                    model_to_validate = {"abstractModel": model}

            validation_result = validator.validate_json_model(model_to_validate)

            # Convert to our ValidationResult format
            validation_errors = []
            if not validation_result["is_valid"]:
                for error_msg in validation_result["errors"]:
                    validation_errors.append(ValidationError(
                        path="unknown",  # SD validator doesn't provide path info yet
                        message=error_msg,
                        quick_fix="Check SD model structure and component definitions",
                        example={}
                    ))

            # Calculate completeness
            completeness = self._calculate_completeness(model, schema_type)

            # Generate suggestions and next steps
            suggestions = self._generate_suggestions(model, schema_type, validation_errors)
            next_steps = self._generate_next_steps(validation_errors, completeness)

            return ValidationResult(
                valid=validation_result["is_valid"],
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
            return f"Add required property '{missing_prop}' to this section"
        elif "not of type" in error.message:
            expected_type = error.schema.get("type", "unknown")
            return f"Change this field to type '{expected_type}'"
        elif "does not match" in error.message:
            if "pattern" in error.schema:
                return f"Format must match pattern: {error.schema['pattern']}"
            return "Check the format/pattern of this field"
        elif "not valid under any of the given schemas" in error.message:
            return "Check that this value matches one of the allowed formats"
        elif "is not one of" in error.message:
            if "enum" in error.schema:
                return f"Must be one of: {', '.join(map(str, error.schema['enum']))}"
            return "Value not in allowed list"
        elif "is greater than the maximum" in error.message:
            maximum = error.schema.get("maximum", "unknown")
            return f"Value must be <= {maximum}"
        elif "is less than the minimum" in error.message:
            minimum = error.schema.get("minimum", "unknown")
            return f"Value must be >= {minimum}"
        else:
            return "Review the field value against schema requirements"
    
    def _generate_example_for_error(self, error: jsonschema.ValidationError) -> Dict[str, Any]:
        """Generate an example for fixing a JSON Schema error."""
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        
        # Common examples based on path and error type
        if "entity_types" in path:
            return {
                "customer": {
                    "probability": 0.8,
                    "priority": 5,
                    "value": {"min": 10, "max": 50}
                },
                "vip": {
                    "probability": 0.2,
                    "priority": 1,
                    "value": {"min": 100, "max": 500}
                }
            }
        elif "resources" in path:
            return {
                "server": {
                    "capacity": 2,
                    "resource_type": "priority"
                }
            }
        elif "processing_rules" in path:
            if "steps" in path:
                return ["reception", "service", "checkout"]
            else:
                return {
                    "steps": ["server"],
                    "server": {"distribution": "uniform(3, 7)"}
                }
        elif "balking_rules" in path:
            return {
                "overcrowding": {
                    "type": "queue_length",
                    "resource": "server",
                    "max_length": 8
                }
            }
        elif "reneging_rules" in path:
            return {
                "impatience": {
                    "abandon_time": "normal(30, 10)",
                    "priority_multipliers": {"1": 5.0, "5": 1.0}
                }
            }
        elif error.schema.get("type") == "string" and "distribution" in path:
            return "uniform(5, 10)"
        elif error.schema.get("type") == "number":
            if "probability" in path:
                return 0.5
            elif "capacity" in path:
                return 1
            elif "priority" in path:
                return 5
            else:
                return 1.0
        elif error.schema.get("type") == "boolean":
            return True
        elif error.schema.get("type") == "array":
            return ["example_item"]
        
        return {}
    
    def _calculate_completeness(self, model: Dict[str, Any], schema_type: str) -> float:
        """Calculate how complete a model is (0.0 to 1.0)."""
        if schema_type == "SD":
            return self._calculate_sd_completeness(model)
        elif schema_type == "DES":
            return self._calculate_des_completeness(model)
        else:
            return self._calculate_generic_completeness(model, schema_type)

    def _calculate_sd_completeness(self, model: Dict[str, Any]) -> float:
        """Calculate completeness for SD models."""
        # For SD models, check if we have a proper structure with elements
        if "abstractModel" in model:
            abstract_model = model["abstractModel"]
            if "sections" in abstract_model and abstract_model["sections"]:
                section = abstract_model["sections"][0]
                if "elements" in section and section["elements"]:
                    # Model has elements - that's the main requirement
                    element_count = len(section["elements"])
                    # High completeness if we have multiple elements with proper structure
                    if element_count >= 3:  # At least 3 variables
                        return 0.9  # 90% complete
                    elif element_count >= 1:
                        return 0.7  # 70% complete
                    else:
                        return 0.3  # Basic structure only

        # Check if this is a template format
        if "model" in model and "abstractModel" in model["model"]:
            return self._calculate_sd_completeness(model["model"])

        return 0.1  # Minimal SD structure

    def _calculate_des_completeness(self, model: Dict[str, Any]) -> float:
        """Calculate completeness for DES models."""
        schema_info = self.registry.get_schema_info("DES")
        if not schema_info:
            return 0.0

        indicators = schema_info.indicators
        present_indicators = sum(1 for indicator in indicators if self._has_nested_key(model, indicator))

        base_completeness = present_indicators / len(indicators) if indicators else 0.0
        depth_bonus = min(0.3, len(model.keys()) * 0.05)

        return min(1.0, base_completeness + depth_bonus)

    def _calculate_generic_completeness(self, model: Dict[str, Any], schema_type: str) -> float:
        """Calculate completeness for generic schema types."""
        schema_info = self.registry.get_schema_info(schema_type)
        if not schema_info:
            return 0.0

        indicators = schema_info.indicators
        present_indicators = sum(1 for indicator in indicators if self.registry._has_nested_key(model, indicator))

        base_completeness = present_indicators / len(indicators) if indicators else 0.0
        depth_bonus = min(0.3, len(model.keys()) * 0.05)

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
        if schema_type == "SD":
            return self._find_missing_sd_required(model)
        elif schema_type == "DES":
            return self._find_missing_des_required(model)
        else:
            return []

    def _find_missing_sd_required(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find missing required fields for SD models."""
        missing = []

        # Check for abstractModel structure
        has_abstract_model = "abstractModel" in model
        if "model" in model and "abstractModel" in model["model"]:
            has_abstract_model = True

        if not has_abstract_model:
            missing.append({
                "path": "abstractModel",
                "description": "Required structure for SD models - contains sections with model elements",
                "example": {"sections": [{"name": "__main__", "elements": []}]}
            })

        return missing

    def _find_missing_des_required(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find missing required fields for DES models."""
        missing = []
        schema_info = self.registry.get_schema_info("DES")

        if schema_info:
            for indicator in schema_info.indicators:
                if not self._has_nested_key(model, indicator):
                    missing.append({
                        "path": indicator,
                        "description": f"Required section for DES models",
                        "example": self._get_example_for_section("DES", indicator)
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
            },
            "SD": {
                "abstractModel": {
                    "originalPath": "my_model.json",
                    "sections": [
                        {
                            "name": "__main__",
                            "type": "main",
                            "elements": [
                                {
                                    "name": "Population Growth Model",
                                    "components": [
                                        {
                                            "type": "Stock",
                                            "subtype": "Normal",
                                            "name": "population",
                                            "initial_value": 100
                                        },
                                        {
                                            "type": "Flow",
                                            "subtype": "Normal",
                                            "name": "birth_rate",
                                            "equation": "population * 0.02"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
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
        if schema_type == "SD":
            return self._generate_sd_suggestions(model, errors)
        elif schema_type == "DES":
            return self._generate_des_suggestions(model, errors)
        else:
            return []

    def _generate_sd_suggestions(self, model: Dict[str, Any], errors: List[ValidationError]) -> List[str]:
        """Generate suggestions for SD models."""
        suggestions = []

        # Check if model is valid and complete
        if not errors:
            # Model is valid - suggest enhancements
            element_count = 0
            if "abstractModel" in model:
                abstract_model = model["abstractModel"]
                if "sections" in abstract_model and abstract_model["sections"]:
                    section = abstract_model["sections"][0]
                    element_count = len(section.get("elements", []))

            if element_count >= 6:
                suggestions.append("SD model is well-structured with proper one-element-per-variable format")
                suggestions.append("Ready for simulation with PySD")
                suggestions.append("Consider adding time settings for simulation configuration")
            elif element_count >= 3:
                suggestions.append("Good SD model structure - consider adding more variables for complexity")
                suggestions.append("Add auxiliary variables for intermediate calculations")
            else:
                suggestions.append("Add more model elements (stocks, flows, auxiliaries) for a complete model")

        else:
            suggestions.append("Fix validation errors to ensure proper PySD-compatible JSON structure")
            suggestions.append("Ensure each variable is its own element (one-element-per-variable)")

        return suggestions

    def _generate_des_suggestions(self, model: Dict[str, Any], errors: List[ValidationError]) -> List[str]:
        """Generate suggestions for DES models."""
        suggestions = []

        if not self._has_nested_key(model, "entity_types"):
            suggestions.append("Add entity_types to define different types of entities (customers, patients, jobs)")
        if not self._has_nested_key(model, "resources"):
            suggestions.append("Add resources to define system capacity and queuing behavior")
        if not self._has_nested_key(model, "processing_rules"):
            suggestions.append("Add processing_rules to define how entities flow through resources")
        if not self._has_nested_key(model, "arrival_pattern") and not model.get("num_entities"):
            suggestions.append("Add arrival_pattern for continuous arrivals or num_entities for fixed batch")

        # Advanced feature suggestions based on completeness
        has_basic_structure = all(self._has_nested_key(model, key) for key in ["entity_types", "resources"])
        if has_basic_structure:
            if not self._has_nested_key(model, "balking_rules"):
                suggestions.append("Consider adding balking_rules for realistic customer behavior")
            if not self._has_nested_key(model, "reneging_rules"):
                suggestions.append("Consider adding reneging_rules for customer impatience modeling")
            if not self._has_nested_key(model, "statistics"):
                suggestions.append("Add statistics configuration to control data collection")
            if not self._has_nested_key(model, "metrics"):
                suggestions.append("Customize metrics names for domain-specific terminology")

        return suggestions

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
