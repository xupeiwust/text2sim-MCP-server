"""
Centralized error handling for MCP tools.

This module provides standardized error response formatting with user-friendly
messages and actionable suggestions for different error types commonly
encountered in simulation workflows.
"""

from typing import List, Dict, Any, Optional


class MCPErrorHandler:
    """Centralized error handling with standardized response formats."""

    @staticmethod
    def validation_error(
        errors: List[str],
        quick_fixes: Optional[List[str]] = None,
        help_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format validation errors with actionable guidance.

        Args:
            errors: List of validation error messages
            quick_fixes: Optional list of suggested fixes
            help_text: Optional general help information

        Returns:
            Standardized validation error response
        """
        return {
            "error": "Configuration validation failed",
            "details": errors,
            "quick_fixes": quick_fixes or [],
            "help": help_text or "Check property names, distributions, and required fields"
        }

    @staticmethod
    def simulation_error(
        error_msg: str,
        suggestions: Optional[List[str]] = None,
        error_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format simulation runtime errors with recovery suggestions.

        Args:
            error_msg: Primary error message
            suggestions: Optional recovery suggestions
            error_type: Optional error classification

        Returns:
            Standardized simulation error response
        """
        response = {
            "error": f"Simulation error: {error_msg}",
            "suggestions": suggestions or ["Check configuration and try again"]
        }

        if error_type:
            response["error_type"] = error_type

        return response

    @staticmethod
    def import_error(
        module_name: str,
        fallback_available: bool = False,
        fallback_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format module import errors with fallback information.

        Args:
            module_name: Name of the module that failed to import
            fallback_available: Whether a fallback implementation exists
            fallback_message: Optional message about fallback behavior

        Returns:
            Standardized import error response
        """
        response = {
            "error": f"Failed to import {module_name}",
            "fallback_available": fallback_available
        }

        if fallback_available and fallback_message:
            response["message"] = fallback_message
        elif fallback_available:
            response["message"] = f"Using fallback implementation for {module_name}"

        return response

    @staticmethod
    def file_operation_error(
        operation: str,
        file_path: str,
        error_msg: str,
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format file operation errors with path and suggestions.

        Args:
            operation: Type of file operation (read, write, save, load)
            file_path: Path to the problematic file
            error_msg: Underlying error message
            suggestions: Optional recovery suggestions

        Returns:
            Standardized file operation error response
        """
        return {
            "error": f"File {operation} failed: {error_msg}",
            "file_path": file_path,
            "operation": operation,
            "suggestions": suggestions or [
                "Check file path exists and is accessible",
                "Verify file permissions",
                "Ensure directory exists"
            ]
        }

    @staticmethod
    def schema_error(
        schema_type: str,
        validation_errors: List[str],
        completeness: float = 0.0
    ) -> Dict[str, Any]:
        """
        Format schema-specific validation errors.

        Args:
            schema_type: Type of schema (DES, SD, etc.)
            validation_errors: List of schema validation errors
            completeness: Model completeness percentage

        Returns:
            Standardized schema error response
        """
        return {
            "error": f"{schema_type} schema validation failed",
            "schema_type": schema_type,
            "validation_errors": validation_errors,
            "completeness": completeness,
            "suggestion": f"Check {schema_type} schema requirements and fix validation errors"
        }

    @staticmethod
    def parameter_error(
        parameter_name: str,
        current_value: Any,
        expected_type: str,
        valid_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format parameter validation errors with type and range information.

        Args:
            parameter_name: Name of the invalid parameter
            current_value: Current parameter value
            expected_type: Expected parameter type
            valid_range: Optional description of valid range

        Returns:
            Standardized parameter error response
        """
        response = {
            "error": f"Invalid parameter: {parameter_name}",
            "parameter": parameter_name,
            "current_value": current_value,
            "expected_type": expected_type
        }

        if valid_range:
            response["valid_range"] = valid_range
            response["suggestion"] = f"Set {parameter_name} to {expected_type} within {valid_range}"
        else:
            response["suggestion"] = f"Set {parameter_name} to valid {expected_type}"

        return response

    @staticmethod
    def dependency_error(
        missing_dependencies: List[str],
        install_commands: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Format dependency errors with installation guidance.

        Args:
            missing_dependencies: List of missing dependency names
            install_commands: Optional installation commands

        Returns:
            Standardized dependency error response
        """
        response = {
            "error": "Missing required dependencies",
            "missing_dependencies": missing_dependencies,
            "suggestion": "Install missing dependencies to enable full functionality"
        }

        if install_commands:
            response["install_commands"] = install_commands

        return response