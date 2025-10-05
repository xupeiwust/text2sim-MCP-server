"""
Model lifecycle management tools for MCP server.

This module implements model persistence, versioning, and export functionality
with comprehensive metadata tracking for iterative development workflows.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import json

from ..shared.error_handlers import MCPErrorHandler
from ..shared.response_builders import ResponseBuilder
from model_builder.multi_schema_validator import MultiSchemaValidator
from model_builder.model_state_manager import model_state_manager


def register_model_mgmt_tools(mcp: FastMCP) -> None:
    """Register model lifecycle management tools."""

    @mcp.tool()
    def save_model(
        model: dict,
        name: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[list] = None,
        overwrite: bool = False
    ) -> dict:
        """
        Save simulation model with metadata for iterative development across conversations.

        This tool enables persistent model development across multiple conversation rounds,
        supporting both user-defined names and intelligent auto-generation with domain detection.

        HYBRID NAMING SYSTEM:
        - User-provided names have priority: save_model(model, "hospital_triage")
        - Auto-generated names when none provided: "DES_healthcare_20250118_143022"
        - Conflict resolution: Automatic versioning (hospital_triage_v2, hospital_triage_v3)
        - Domain detection: Analyzes model content for intelligent naming

        DOMAIN AUTO-DETECTION:
        The system detects domains from model content for better auto-naming:
        - Healthcare: hospital, patient, doctor, triage, emergency
        - Manufacturing: production, assembly, quality, inspection
        - Service: customer, restaurant, call_center, checkout
        - Transportation: airport, passenger, logistics, delivery
        - Finance: bank, transaction, account, investment

        METADATA TRACKING:
        - Creation and modification timestamps
        - User notes and descriptions
        - Tags for categorization and search
        - Schema type auto-detection
        - Validation status caching
        - Completeness percentage

        CONVERSATION CONTINUITY:
        Saved models persist across conversation sessions, enabling:
        - Resume development in new conversations
        - Share models between team members
        - Version tracking and comparison
        - Export for external use

        USAGE PATTERNS:

        # Save with user-defined name
        save_model(model, "my_hospital_simulation", "Added VIP patients")

        # Auto-generated name with notes
        save_model(model, notes="First version with basic flow")

        # Organized with tags
        save_model(model, "clinic_v2", tags=["healthcare", "priority", "testing"])

        # Overwrite existing model
        save_model(updated_model, "hospital_triage", overwrite=True)

        Args:
            model: Model dictionary to save
            name: Optional user-provided name (auto-generated if None)
            notes: Optional description or notes
            tags: Optional tags for categorization
            overwrite: Allow overwriting existing model with same name

        Returns:
            Save result with model ID, metadata, and confirmation message
        """
        try:
            # Validate model first to cache validation result
            validator = MultiSchemaValidator()
            validation_result = validator.validate_model(model)

            validation_dict = {
                "valid": validation_result.valid,
                "completeness": validation_result.completeness,
                "missing_required": validation_result.missing_required,
                "schema_type": validation_result.schema_type
            }

            # Save model with validation result
            result = model_state_manager.save_model(
                model=model,
                name=name,
                notes=notes,
                tags=tags,
                overwrite=overwrite,
                validation_result=validation_dict
            )

            return ResponseBuilder.model_operation_response(
                operation="save",
                success=True,
                model_name=result.get("model_name"),
                model_id=result.get("model_id"),
                validation_status=validation_dict,
                metadata=result.get("metadata", {}),
                message=result.get("message", "Model saved successfully")
            )

        except Exception as e:
            return ResponseBuilder.model_operation_response(
                operation="save",
                success=False,
                error=str(e),
                message="Failed to save model",
                suggestions=[
                    "Check model format is valid",
                    "Verify model_state_manager is accessible",
                    "Ensure sufficient storage space"
                ]
            )

    @mcp.tool()
    def load_model(
        name: Optional[str] = None,
        schema_type: Optional[str] = None,
        tags: Optional[list] = None
    ) -> dict:
        """
        Load saved simulation model or list available models with filtering capabilities.

        This tool supports both loading specific models and discovering available models
        with advanced filtering options for efficient model management.

        TWO OPERATION MODES:

        1. LOAD MODE (name provided):
           - Returns complete model with metadata
           - Includes cached validation status
           - Updates last-loaded reference
           - Ready for continued development

        2. LIST MODE (name=None):
           - Shows all available models
           - Supports filtering by schema type and tags
           - Sorted by last modified (newest first)
           - Includes metadata preview

        FILTERING OPTIONS:
        - schema_type: Filter by "DES", "SD", etc.
        - tags: Filter by any matching tags
        - Combined filters: Use both for precise selection

        MODEL METADATA INCLUDED:
        - Schema type and validation status
        - Creation and modification dates
        - User notes and tags
        - Completeness percentage
        - Domain classification

        USAGE PATTERNS:

        # Load specific model
        load_model("hospital_triage_v3")

        # List all models
        load_model()

        # Filter by schema type
        load_model(schema_type="DES")

        # Filter by tags
        load_model(tags=["healthcare", "testing"])

        # Combined filtering
        load_model(schema_type="DES", tags=["manufacturing"])

        CONVERSATION FLOW:
        After loading a model, you can:
        1. Continue development with validate_model()
        2. Make modifications and save_model() again
        3. Export with export_model() for sharing
        4. Run simulation when ready

        Args:
            name: Model name to load (None for list mode)
            schema_type: Filter by schema type in list mode
            tags: Filter by tags in list mode

        Returns:
            Model data with metadata or filtered list of available models
        """
        try:
            if name:
                # Load specific model
                result = model_state_manager.load_model(name)

                if result.get("loaded", False):
                    return ResponseBuilder.model_operation_response(
                        operation="load",
                        success=True,
                        model_name=name,
                        model=result.get("model"),
                        metadata=result.get("metadata", {}),
                        validation_status=result.get("validation_status", {}),
                        message=f"Model '{name}' loaded successfully"
                    )
                else:
                    return ResponseBuilder.model_operation_response(
                        operation="load",
                        success=False,
                        model_name=name,
                        error=result.get("error", f"Model '{name}' not found"),
                        available_models=list(model_state_manager.models.keys())
                    )
            else:
                # List mode with filtering
                result = model_state_manager.load_model(
                    name=None,
                    schema_type=schema_type,
                    tags=tags
                )

                return ResponseBuilder.list_response(
                    items=result.get("available_models", []),
                    total_count=result.get("total_count"),
                    filters_applied={
                        "schema_type": schema_type,
                        "tags": tags
                    }
                )

        except Exception as e:
            return ResponseBuilder.model_operation_response(
                operation="load",
                success=False,
                error=str(e),
                message="Failed to load model or list models",
                suggestions=[
                    "Check model name exists",
                    "Verify model_state_manager is accessible",
                    "Try listing all models first"
                ]
            )

    @mcp.tool()
    def export_model(
        name: Optional[str] = None,
        format: str = "pretty",
        include_metadata: bool = False
    ) -> dict:
        """
        Export simulation model as formatted JSON for copy-paste to new conversations.

        This tool enables conversation continuity by providing properly formatted JSON
        that can be easily copied and pasted into new conversation sessions for continued
        model development.

        EXPORT FORMATS:
        - "pretty": Human-readable with proper indentation (default)
        - "compact": Minimized JSON for token efficiency
        - "conversation": Includes template text for easy pasting

        CONVERSATION CONTINUITY:
        The exported JSON can be used to:
        - Continue development in new conversation sessions
        - Share models with team members
        - Create backups of work-in-progress
        - Transfer models between different AI assistants

        INCLUDES:
        - Complete model JSON in specified format
        - Character and estimated token counts
        - Copy-paste ready formatting
        - Optional metadata inclusion
        - Conversation template for easy use

        USAGE PATTERNS:

        # Export last loaded model (pretty format)
        export_model()

        # Export specific model
        export_model("hospital_triage_v3")

        # Compact format for token efficiency
        export_model("my_model", format="compact")

        # Include metadata for complete backup
        export_model("my_model", include_metadata=True)

        # Conversation-ready format
        export_model("my_model", format="conversation")

        CONVERSATION TEMPLATE:
        When format="conversation", includes ready-to-use text:
        "Here's my current simulation model:

        ```json
        {model_content}
        ```

        Please help me continue developing this model."

        Args:
            name: Model name to export (uses last loaded if None)
            format: Export format ("pretty", "compact", "conversation")
            include_metadata: Include model metadata in export

        Returns:
            Formatted JSON string with metadata and usage information
        """
        try:
            # Determine which model to export
            model_name = name or model_state_manager.get_last_loaded()

            if not model_name:
                return ResponseBuilder.export_response(
                    exported=False,
                    error="No model specified and no model previously loaded",
                    suggestions=[
                        "Specify model name explicitly",
                        "Load a model first using load_model()",
                        "Check available models with load_model()"
                    ]
                )

            # Load the model
            load_result = model_state_manager.load_model(model_name)
            if not load_result.get("loaded", False):
                return ResponseBuilder.export_response(
                    exported=False,
                    error=f"Model '{model_name}' not found",
                    available_models=list(model_state_manager.models.keys()),
                    suggestions=[
                        "Check model name spelling",
                        "Use load_model() to see available models"
                    ]
                )

            model_data = load_result["model"]
            metadata = load_result.get("metadata", {})

            # Prepare export data
            export_data = model_data
            if include_metadata:
                export_data = {
                    "model": model_data,
                    "metadata": metadata
                }

            # Format JSON based on requested format
            formatted_json = ResponseBuilder.format_json_export(
                export_data,
                format_type=format,
                include_metadata=include_metadata
            )

            return ResponseBuilder.export_response(
                exported=True,
                content=formatted_json["json_string"],
                format_type=format,
                metadata={
                    "model_name": model_name,
                    "character_count": formatted_json["character_count"],
                    "estimated_tokens": formatted_json["estimated_tokens"],
                    "metadata_included": include_metadata,
                    "export_timestamp": ResponseBuilder.add_timestamp({})["timestamp"]
                },
                conversation_template=formatted_json.get("conversation_template"),
                copy_paste_ready=True,
                usage_tip="Copy the content value and paste it into a new conversation"
            )

        except Exception as e:
            return ResponseBuilder.export_response(
                exported=False,
                error=str(e),
                suggestions=[
                    "Check model exists and is accessible",
                    "Verify export format is supported",
                    "Try with different format option"
                ]
            )

    @mcp.tool()
    def delete_model(name: str, confirm: bool = False) -> dict:
        """
        Delete a saved simulation model with confirmation requirement.

        This tool provides safe model deletion with confirmation requirements
        to prevent accidental loss of work.

        SAFETY FEATURES:
        - Requires explicit confirmation flag
        - Returns model metadata before deletion
        - Provides undo suggestions if available
        - Lists related models for reference

        Args:
            name: Name of model to delete
            confirm: Must be True to actually delete the model

        Returns:
            Deletion status with safety information
        """
        try:
            if not confirm:
                # Return model info and require confirmation
                load_result = model_state_manager.load_model(name)
                if not load_result.get("loaded", False):
                    return ResponseBuilder.model_operation_response(
                        operation="delete",
                        success=False,
                        model_name=name,
                        error=f"Model '{name}' not found",
                        available_models=list(model_state_manager.models.keys())
                    )

                return ResponseBuilder.model_operation_response(
                    operation="delete",
                    success=False,
                    model_name=name,
                    message="Confirmation required",
                    model_info=load_result.get("metadata", {}),
                    warning="Set confirm=True to actually delete this model",
                    suggestions=[
                        "Review model metadata above",
                        "Export model as backup before deletion",
                        "Use delete_model(name, confirm=True) to proceed"
                    ]
                )

            # Perform actual deletion
            result = model_state_manager.delete_model(name)

            if result.get("deleted", False):
                return ResponseBuilder.model_operation_response(
                    operation="delete",
                    success=True,
                    model_name=name,
                    message=f"Model '{name}' deleted successfully",
                    deleted_metadata=result.get("metadata", {}),
                    undo_info="Model data is permanently removed"
                )
            else:
                return ResponseBuilder.model_operation_response(
                    operation="delete",
                    success=False,
                    model_name=name,
                    error=result.get("error", "Deletion failed"),
                    suggestions=["Check model name exists", "Verify permissions"]
                )

        except Exception as e:
            return ResponseBuilder.model_operation_response(
                operation="delete",
                success=False,
                model_name=name,
                error=str(e),
                suggestions=[
                    "Check model_state_manager is accessible",
                    "Verify model name is correct"
                ]
            )