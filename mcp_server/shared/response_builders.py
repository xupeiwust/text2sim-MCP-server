"""
Standardized response building utilities for MCP tools.

This module provides consistent response formatting across all simulation tools,
ensuring uniform structure and metadata handling for success and error cases.
"""

from typing import Dict, Any, Optional, List, Union
import json
from datetime import datetime


class ResponseBuilder:
    """Standardized response building utilities with consistent formatting."""

    @staticmethod
    def success_response(
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build successful operation response with optional metadata.

        Args:
            data: Primary response data
            metadata: Optional metadata dictionary
            message: Optional success message

        Returns:
            Standardized success response
        """
        response = {"success": True, **data}

        if metadata:
            response["metadata"] = metadata

        if message:
            response["message"] = message

        return response

    @staticmethod
    def validation_response(
        valid: bool,
        errors: List[Dict[str, Any]],
        completeness: float,
        suggestions: List[str],
        schema_type: Optional[str] = None,
        validation_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build validation result response with detailed error information.

        Args:
            valid: Whether validation passed
            errors: List of validation errors with structured details
            completeness: Model completeness percentage (0.0 to 1.0)
            suggestions: List of improvement suggestions
            schema_type: Optional schema type identifier
            validation_mode: Optional validation mode used

        Returns:
            Standardized validation response
        """
        response = {
            "valid": valid,
            "completeness": completeness,
            "errors": errors,
            "suggestions": suggestions
        }

        if schema_type:
            response["schema_type"] = schema_type

        if validation_mode:
            response["validation_mode"] = validation_mode

        return response

    @staticmethod
    def model_operation_response(
        operation: str,
        success: bool,
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build model operation response (save, load, export, etc.).

        Args:
            operation: Type of operation performed
            success: Whether operation succeeded
            model_name: Optional model name
            **kwargs: Additional operation-specific data

        Returns:
            Standardized model operation response
        """
        response = {
            f"{operation}": success,
            "operation": operation
        }

        if model_name:
            response["model_name"] = model_name

        response.update(kwargs)
        return response

    @staticmethod
    def simulation_response(
        success: bool,
        results: Optional[Dict[str, Any]] = None,
        model_info: Optional[Dict[str, Any]] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build simulation execution response with results and metadata.

        Args:
            success: Whether simulation completed successfully
            results: Simulation results data
            model_info: Information about the simulated model
            execution_metadata: Metadata about simulation execution
            error_message: Error message if simulation failed

        Returns:
            Standardized simulation response
        """
        response = {"success": success}

        if success and results:
            response["results"] = results

        if model_info:
            response["model_info"] = model_info

        if execution_metadata:
            response["execution_metadata"] = execution_metadata

        if not success and error_message:
            response["error_message"] = error_message

        return response

    @staticmethod
    def list_response(
        items: List[Dict[str, Any]],
        total_count: Optional[int] = None,
        filters_applied: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build list response for collections with filtering and pagination.

        Args:
            items: List of items to return
            total_count: Total count before filtering/pagination
            filters_applied: Dictionary of applied filters
            pagination: Pagination information

        Returns:
            Standardized list response
        """
        response = {
            "items": items,
            "count": len(items)
        }

        if total_count is not None:
            response["total_count"] = total_count

        if filters_applied:
            response["filters_applied"] = filters_applied

        if pagination:
            response["pagination"] = pagination

        return response

    @staticmethod
    def export_response(
        exported: bool,
        content: Optional[str] = None,
        format_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build export operation response with content and metadata.

        Args:
            exported: Whether export succeeded
            content: Exported content string
            format_type: Export format used
            metadata: Export metadata (size, encoding, etc.)
            **kwargs: Additional export-specific data

        Returns:
            Standardized export response
        """
        response = {"exported": exported}

        if exported and content:
            response["content"] = content

        if format_type:
            response["format"] = format_type

        if metadata:
            response["metadata"] = metadata

        response.update(kwargs)
        return response

    @staticmethod
    def statistical_response(
        analysis: Dict[str, Any],
        summary_report: Optional[str] = None,
        execution_info: Optional[Dict[str, Any]] = None,
        confidence_intervals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build statistical analysis response for multiple replications.

        Args:
            analysis: Statistical analysis results
            summary_report: Formatted summary report
            execution_info: Information about execution parameters
            confidence_intervals: Confidence interval data

        Returns:
            Standardized statistical response
        """
        response = {"statistical_analysis": analysis}

        if summary_report:
            response["summary_report"] = summary_report

        if execution_info:
            response["execution_info"] = execution_info

        if confidence_intervals:
            response["confidence_intervals"] = confidence_intervals

        return response

    @staticmethod
    def template_response(
        template_data: Dict[str, Any],
        usage_info: Optional[Dict[str, Any]] = None,
        customization_guidance: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build template response with usage guidance.

        Args:
            template_data: Core template data
            usage_info: Information about template usage
            customization_guidance: List of customization tips

        Returns:
            Standardized template response
        """
        response = template_data.copy()

        if usage_info:
            response["usage_info"] = usage_info

        if customization_guidance:
            response["customization_guidance"] = customization_guidance

        return response

    @staticmethod
    def help_response(
        help_data: Dict[str, Any],
        section_info: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        related_topics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build help/documentation response with examples and references.

        Args:
            help_data: Core help content
            section_info: Information about the help section
            examples: List of practical examples
            related_topics: List of related help topics

        Returns:
            Standardized help response
        """
        response = help_data.copy()

        if section_info:
            response["section_info"] = section_info

        if examples:
            response["examples"] = examples

        if related_topics:
            response["related_topics"] = related_topics

        return response

    @staticmethod
    def add_timestamp(response: Dict[str, Any], key: str = "timestamp") -> Dict[str, Any]:
        """
        Add timestamp to response for tracking and debugging.

        Args:
            response: Response dictionary to modify
            key: Key name for timestamp field

        Returns:
            Response with timestamp added
        """
        response[key] = datetime.utcnow().isoformat()
        return response

    @staticmethod
    def format_json_export(
        data: Dict[str, Any],
        format_type: str = "pretty",
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Format data for JSON export with various formatting options.

        Args:
            data: Data to format
            format_type: Format type (pretty, compact, conversation)
            include_metadata: Whether to include formatting metadata

        Returns:
            Formatted export response
        """
        if format_type == "compact":
            json_string = json.dumps(data, separators=(',', ':'))
        else:
            json_string = json.dumps(data, indent=2, separators=(',', ': '))

        response = {
            "json_string": json_string,
            "format": format_type,
            "character_count": len(json_string),
            "estimated_tokens": len(json_string) // 4
        }

        if include_metadata:
            response["formatting_metadata"] = {
                "encoding": "utf-8",
                "line_count": json_string.count('\n') + 1,
                "indent_spaces": 2 if format_type != "compact" else 0
            }

        if format_type == "conversation":
            response["conversation_template"] = f"""Here's my current model:

```json
{json_string}
```

Please help me continue developing this model."""

        return response