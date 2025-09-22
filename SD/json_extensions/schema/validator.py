"""
Schema validation module for PySD JSON extensions.

Provides validation capabilities for PySD-compatible JSON model structures
with detailed error reporting and suggestions.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error with context."""
    message: str
    path: str
    value: Any
    schema_path: str
    error_type: str


@dataclass
class ValidationResult:
    """Result of schema validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    suggestions: List[str]


class SchemaValidator:
    """
    JSON Schema validator for PySD Abstract Model format.

    Provides comprehensive validation with detailed error messages
    and actionable suggestions for model improvement.
    """

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the schema validator.

        Args:
            schema_path: Path to the JSON schema file. If None, uses default.
        """
        self.schema_path = schema_path or self._get_default_schema_path()
        self.schema = self._load_schema()

    def _get_default_schema_path(self) -> str:
        """Get the default schema path."""
        # Navigate to the new schema location
        current_dir = Path(__file__).parent
        # Go up to text2sim-MCP-server root, then to schemas/SD/
        mcp_root = current_dir.parent.parent.parent
        schema_file = mcp_root / "schemas" / "SD" / "abstract_model_v2.json"
        return str(schema_file)

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema."""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return a minimal schema if file doesn't exist
            return {
                "type": "object",
                "properties": {
                    "abstractModel": {
                        "type": "object",
                        "required": ["originalPath", "sections"],
                        "properties": {
                            "originalPath": {"type": "string"},
                            "sections": {
                                "type": "array",
                                "items": {"type": "object"}
                            }
                        }
                    }
                },
                "required": ["abstractModel"]
            }
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON schema file: {e}")

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against the schema.

        Args:
            data: The data to validate

        Returns:
            ValidationResult with detailed feedback
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            # Perform JSON schema validation
            validator = jsonschema.Draft7Validator(self.schema)
            schema_errors = list(validator.iter_errors(data))

            # Convert jsonschema errors to our format
            for error in schema_errors:
                validation_error = ValidationError(
                    message=error.message,
                    path='.'.join(str(p) for p in error.path),
                    value=error.instance,
                    schema_path='.'.join(str(p) for p in error.schema_path),
                    error_type=error.validator
                )
                errors.append(validation_error)

            # Additional SD-specific validations
            self._validate_sd_structure(data, errors, warnings, suggestions)

            is_valid = len(errors) == 0
            return ValidationResult(is_valid, errors, warnings, suggestions)

        except Exception as e:
            error = ValidationError(
                message=f"Validation failed: {str(e)}",
                path="",
                value=data,
                schema_path="",
                error_type="system_error"
            )
            return ValidationResult(False, [error], warnings, suggestions)

    def _validate_sd_structure(
        self,
        data: Dict[str, Any],
        errors: List[ValidationError],
        warnings: List[str],
        suggestions: List[str]
    ):
        """Perform SD-specific structure validation."""
        try:
            abstract_model = data.get("abstractModel", {})
            sections = abstract_model.get("sections", [])

            # Check for main section
            main_sections = [s for s in sections if s.get("name") == "__main__" and s.get("type") == "main"]
            if not main_sections:
                errors.append(ValidationError(
                    message="Missing main section with name='__main__' and type='main'",
                    path="abstractModel.sections",
                    value=sections,
                    schema_path="abstractModel.sections",
                    error_type="missing_main_section"
                ))
                return

            main_section = main_sections[0]
            elements = main_section.get("elements", [])

            # Validate elements structure
            for i, element in enumerate(elements):
                element_path = f"abstractModel.sections[0].elements[{i}]"
                self._validate_element(element, element_path, errors, warnings, suggestions)

        except Exception as e:
            warnings.append(f"Error during SD structure validation: {str(e)}")

    def _validate_element(
        self,
        element: Dict[str, Any],
        element_path: str,
        errors: List[ValidationError],
        warnings: List[str],
        suggestions: List[str]
    ):
        """Validate a single element."""
        element_name = element.get("name", "")
        components = element.get("components", [])

        # Check component count
        if len(components) == 0:
            warnings.append(f"Element '{element_name}' has no components")
        elif len(components) > 1:
            errors.append(ValidationError(
                message=f"Element '{element_name}' contains {len(components)} components. PySD requires one component per element.",
                path=f"{element_path}.components",
                value=components,
                schema_path="element.components",
                error_type="multiple_components"
            ))

        # Validate each component
        for j, component in enumerate(components):
            component_path = f"{element_path}.components[{j}]"
            self._validate_component(component, element_name, component_path, errors, warnings)

    def _validate_component(
        self,
        component: Dict[str, Any],
        element_name: str,
        component_path: str,
        errors: List[ValidationError],
        warnings: List[str]
    ):
        """Validate a single component."""
        # Check required fields
        required_fields = ["type", "subtype", "subscripts", "ast"]
        for field in required_fields:
            if field not in component:
                errors.append(ValidationError(
                    message=f"Component in element '{element_name}' missing required field: {field}",
                    path=f"{component_path}.{field}",
                    value=component,
                    schema_path=f"component.{field}",
                    error_type="missing_required_field"
                ))

        # Check component name matches element name
        comp_name = component.get("name")
        if not comp_name:
            errors.append(ValidationError(
                message=f"Component in element '{element_name}' missing required 'name' field",
                path=f"{component_path}.name",
                value=component,
                schema_path="component.name",
                error_type="missing_component_name"
            ))
        elif comp_name != element_name:
            errors.append(ValidationError(
                message=f"Component name '{comp_name}' must match element name '{element_name}'",
                path=f"{component_path}.name",
                value=comp_name,
                schema_path="component.name",
                error_type="name_mismatch"
            ))

        # Validate AST structure
        ast = component.get("ast", {})
        if ast:
            self._validate_ast(ast, element_name, f"{component_path}.ast", errors)

    def _validate_ast(
        self,
        ast: Dict[str, Any],
        element_name: str,
        ast_path: str,
        errors: List[ValidationError]
    ):
        """Validate AST structure."""
        if not isinstance(ast, dict):
            errors.append(ValidationError(
                message=f"AST in element '{element_name}' must be a dictionary",
                path=ast_path,
                value=ast,
                schema_path="component.ast",
                error_type="invalid_ast_type"
            ))
            return

        syntax_type = ast.get("syntaxType")
        if not syntax_type:
            errors.append(ValidationError(
                message=f"AST in element '{element_name}' missing 'syntaxType' field",
                path=f"{ast_path}.syntaxType",
                value=ast,
                schema_path="component.ast.syntaxType",
                error_type="missing_syntax_type"
            ))
            return

        valid_syntax_types = [
            "ReferenceStructure",
            "ArithmeticStructure",
            "IntegStructure",
            "CallStructure"
        ]
        if syntax_type not in valid_syntax_types:
            errors.append(ValidationError(
                message=f"Invalid syntaxType '{syntax_type}' in element '{element_name}'. Must be one of: {valid_syntax_types}",
                path=f"{ast_path}.syntaxType",
                value=syntax_type,
                schema_path="component.ast.syntaxType",
                error_type="invalid_syntax_type"
            ))


def validate_sd_json(data: Dict[str, Any], schema_path: Optional[str] = None) -> ValidationResult:
    """
    Convenience function to validate SD JSON data.

    Args:
        data: The data to validate
        schema_path: Optional path to schema file

    Returns:
        ValidationResult with validation details
    """
    validator = SchemaValidator(schema_path)
    return validator.validate(data)