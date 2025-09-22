"""
Model serialization module for PySD JSON extensions.

Provides serialization capabilities for converting between different
model formats and ensuring consistent data representation.
"""

import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SerializationResult:
    """Result of model serialization."""
    success: bool
    data: Optional[Union[str, Dict[str, Any]]]
    error_message: Optional[str]
    metadata: Dict[str, Any]


class ModelSerializer:
    """
    Serializer for PySD-compatible model formats.

    Handles conversion between JSON, dictionary, and other model
    representations with proper formatting and validation.
    """

    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """
        Initialize the model serializer.

        Args:
            indent: JSON indentation level
            ensure_ascii: Whether to ensure ASCII encoding
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def serialize_to_json(
        self,
        model: Dict[str, Any],
        output_path: Optional[str] = None,
        pretty: bool = True
    ) -> SerializationResult:
        """
        Serialize model to JSON format.

        Args:
            model: The model dictionary to serialize
            output_path: Optional output file path
            pretty: Whether to use pretty formatting

        Returns:
            SerializationResult with serialized data
        """
        try:
            # Configure JSON serialization
            json_kwargs = {
                "ensure_ascii": self.ensure_ascii,
                "sort_keys": True
            }

            if pretty:
                json_kwargs["indent"] = self.indent
                json_kwargs["separators"] = (",", ": ")

            # Serialize to JSON string
            json_data = json.dumps(model, **json_kwargs)

            # Write to file if path provided
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)

            metadata = {
                "format": "json",
                "size_bytes": len(json_data.encode('utf-8')),
                "pretty_formatted": pretty,
                "output_file": output_path
            }

            return SerializationResult(
                success=True,
                data=json_data,
                error_message=None,
                metadata=metadata
            )

        except Exception as e:
            return SerializationResult(
                success=False,
                data=None,
                error_message=f"JSON serialization failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def deserialize_from_json(
        self,
        json_data: Union[str, Path],
        validate: bool = True
    ) -> SerializationResult:
        """
        Deserialize model from JSON format.

        Args:
            json_data: JSON string or path to JSON file
            validate: Whether to validate the deserialized model

        Returns:
            SerializationResult with deserialized data
        """
        try:
            # Handle file path vs string
            if isinstance(json_data, (str, Path)) and Path(json_data).exists():
                with open(json_data, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                source = str(json_data)
            else:
                data = json.loads(str(json_data))
                source = "string"

            # Basic validation if requested
            validation_errors = []
            if validate:
                validation_errors = self._basic_validation(data)

            metadata = {
                "format": "json",
                "source": source,
                "validation_performed": validate,
                "validation_errors": validation_errors
            }

            return SerializationResult(
                success=len(validation_errors) == 0,
                data=data,
                error_message=None if len(validation_errors) == 0 else f"Validation errors: {validation_errors}",
                metadata=metadata
            )

        except json.JSONDecodeError as e:
            return SerializationResult(
                success=False,
                data=None,
                error_message=f"JSON parsing failed: {str(e)}",
                metadata={"error_type": "JSONDecodeError", "source": str(json_data)[:100]}
            )
        except Exception as e:
            return SerializationResult(
                success=False,
                data=None,
                error_message=f"Deserialization failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def normalize_model(self, model: Dict[str, Any]) -> SerializationResult:
        """
        Normalize model structure for consistency.

        Args:
            model: The model to normalize

        Returns:
            SerializationResult with normalized model
        """
        try:
            normalized = self._deep_copy_and_normalize(model)

            # Ensure required structure
            if "abstractModel" in normalized:
                self._normalize_abstract_model(normalized["abstractModel"])

            metadata = {
                "normalization_applied": True,
                "original_keys": list(model.keys()),
                "normalized_keys": list(normalized.keys())
            }

            return SerializationResult(
                success=True,
                data=normalized,
                error_message=None,
                metadata=metadata
            )

        except Exception as e:
            return SerializationResult(
                success=False,
                data=None,
                error_message=f"Normalization failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def _deep_copy_and_normalize(self, obj: Any) -> Any:
        """Deep copy and normalize an object."""
        if isinstance(obj, dict):
            return {key: self._deep_copy_and_normalize(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy_and_normalize(item) for item in obj]
        else:
            return obj

    def _normalize_abstract_model(self, abstract_model: Dict[str, Any]):
        """Normalize abstract model structure."""
        # Ensure required fields exist
        if "sections" not in abstract_model:
            abstract_model["sections"] = []

        # Normalize sections
        for section in abstract_model["sections"]:
            self._normalize_section(section)

    def _normalize_section(self, section: Dict[str, Any]):
        """Normalize a section structure."""
        # Ensure required section fields
        required_fields = {
            "params": [],
            "returns": [],
            "subscripts": [],
            "constraints": [],
            "testInputs": [],
            "split": False,
            "viewsDict": {},
            "elements": []
        }

        for field, default_value in required_fields.items():
            if field not in section:
                section[field] = default_value

        # Normalize elements
        if "elements" in section:
            for element in section["elements"]:
                self._normalize_element(element)

    def _normalize_element(self, element: Dict[str, Any]):
        """Normalize an element structure."""
        # Ensure components exist
        if "components" not in element:
            element["components"] = []

        # Normalize components
        for component in element["components"]:
            self._normalize_component(component, element.get("name", ""))

    def _normalize_component(self, component: Dict[str, Any], element_name: str):
        """Normalize a component structure."""
        # Ensure component name matches element name
        if "name" not in component and element_name:
            component["name"] = element_name

        # Ensure required component fields
        if "subscripts" not in component:
            component["subscripts"] = [[], []]

        if "ast" not in component:
            component["ast"] = {
                "syntaxType": "ReferenceStructure",
                "reference": "0"
            }

    def _basic_validation(self, model: Dict[str, Any]) -> List[str]:
        """Perform basic model validation."""
        errors = []

        if not isinstance(model, dict):
            errors.append("Model must be a dictionary")
            return errors

        if "abstractModel" not in model:
            errors.append("Model must contain 'abstractModel' property")
            return errors

        abstract_model = model["abstractModel"]
        if not isinstance(abstract_model, dict):
            errors.append("abstractModel must be a dictionary")
            return errors

        required_fields = ["originalPath", "sections"]
        for field in required_fields:
            if field not in abstract_model:
                errors.append(f"abstractModel missing required field: {field}")

        return errors

    def export_for_conversation(
        self,
        model: Dict[str, Any],
        include_metadata: bool = True,
        format_for_llm: bool = True
    ) -> SerializationResult:
        """
        Export model in format suitable for LLM conversations.

        Args:
            model: The model to export
            include_metadata: Whether to include template metadata
            format_for_llm: Whether to format for optimal LLM parsing

        Returns:
            SerializationResult with conversation-ready format
        """
        try:
            export_data = {}

            # Include core model structure
            if "abstractModel" in model:
                export_data["abstractModel"] = model["abstractModel"]

            # Include metadata if requested
            if include_metadata:
                metadata_fields = [
                    "template_info", "usage_notes", "customization_tips",
                    "common_modifications", "examples", "related_concepts",
                    "extensions", "learning_objectives"
                ]
                for field in metadata_fields:
                    if field in model:
                        export_data[field] = model[field]

            # Format for LLM if requested
            if format_for_llm:
                export_data = self._format_for_llm(export_data)

            # Serialize with optimal formatting
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False, sort_keys=True)

            metadata = {
                "format": "conversation_export",
                "include_metadata": include_metadata,
                "llm_formatted": format_for_llm,
                "size_bytes": len(json_data.encode('utf-8')),
                "estimated_tokens": len(json_data.split()) * 1.3  # Rough token estimate
            }

            return SerializationResult(
                success=True,
                data=json_data,
                error_message=None,
                metadata=metadata
            )

        except Exception as e:
            return SerializationResult(
                success=False,
                data=None,
                error_message=f"Conversation export failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def _format_for_llm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for optimal LLM parsing."""
        # Remove excessively verbose fields that don't help LLMs
        formatted_data = {}

        for key, value in data.items():
            if key in ["abstractModel"]:
                # Keep core model structure but simplify if needed
                formatted_data[key] = value
            elif key in ["template_info", "usage_notes", "examples"]:
                # Keep important metadata
                formatted_data[key] = value
            elif key in ["customization_tips", "common_modifications"]:
                # Include but limit length if too verbose
                if isinstance(value, list) and len(value) > 5:
                    formatted_data[key] = value[:5] + ["... (truncated for brevity)"]
                else:
                    formatted_data[key] = value
            else:
                # Include other fields as-is
                formatted_data[key] = value

        return formatted_data


# Convenience functions
def serialize_model_to_json(model: Dict[str, Any], **kwargs) -> SerializationResult:
    """Serialize model to JSON using default serializer."""
    serializer = ModelSerializer()
    return serializer.serialize_to_json(model, **kwargs)


def deserialize_model_from_json(json_data: Union[str, Path], **kwargs) -> SerializationResult:
    """Deserialize model from JSON using default serializer."""
    serializer = ModelSerializer()
    return serializer.deserialize_from_json(json_data, **kwargs)