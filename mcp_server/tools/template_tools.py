"""
Template management tools for MCP server.

This module implements template creation, discovery, and management functionality
with comprehensive metadata tracking and intelligent categorization.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional

from ..shared.error_handlers import MCPErrorHandler
from ..shared.response_builders import ResponseBuilder
from model_builder.template_manager import template_manager


def register_template_tools(mcp: FastMCP) -> None:
    """Register template management tools."""

    @mcp.tool()
    def list_templates(
        schema_type: Optional[str] = None,
        domain: Optional[str] = None,
        complexity: Optional[str] = None,
        tags: Optional[list] = None,
        include_user: bool = True,
        search_term: Optional[str] = None
    ) -> dict:
        """
        List available simulation templates with filtering and search capabilities.

        This tool provides access to a comprehensive collection of built-in and user-created
        templates covering major simulation domains. Templates serve as starting points for
        model development, offering tested configurations with domain-specific examples.

        BUILT-IN TEMPLATE COLLECTION:

        Basic Templates:
        - Single Server Queue: FIFO processing with exponential arrivals
        - Multi-Server System: Parallel processing with shared queues
        - Priority Queue: Service based on entity priority levels

        Healthcare Templates:
        - Hospital Triage System: Emergency and routine patient flow
        - Clinic Appointment System: Scheduled and walk-in patients
        - Emergency Department: Multi-priority patient classification

        Manufacturing Templates:
        - Production Line: Assembly with quality control
        - Batch Processing: Fixed-size batch operations
        - Flexible Manufacturing: Multi-product processing

        Service Templates:
        - Customer Service Center: Multi-channel support
        - Bank Teller System: Multiple service types
        - Restaurant Operations: Dining and takeout service

        FILTERING OPTIONS:

        By Schema Type:
        - "DES": Discrete-Event Simulation templates
        - "SD": System Dynamics templates (future)

        By Domain:
        - "healthcare": Medical and patient care systems
        - "manufacturing": Production and assembly operations
        - "service": Customer service and support systems
        - "basic": Fundamental queueing concepts

        By Complexity:
        - "basic": Simple single-resource systems
        - "intermediate": Multi-resource with routing
        - "advanced": Complex systems with failures

        SEARCH AND DISCOVERY:

        # List all templates
        list_templates()

        # Healthcare templates only
        list_templates(domain="healthcare")

        # Basic DES templates
        list_templates(schema_type="DES", complexity="basic")

        # Search by keyword
        list_templates(search_term="hospital")

        # Filter by multiple criteria
        list_templates(domain="manufacturing", complexity="intermediate")

        TAG-BASED FILTERING:
        Templates include descriptive tags for precise filtering:
        - Process types: ["queue", "batch", "priority", "scheduling"]
        - Industries: ["hospital", "factory", "call-center", "restaurant"]
        - Features: ["routing", "failures", "statistics", "multi-resource"]

        USER TEMPLATES:
        Include your own saved templates alongside built-in collection.
        Set include_user=False to see only built-in templates.

        USAGE TRACKING:
        Templates are sorted by popularity (use count) to highlight
        the most successful starting points for model development.

        Args:
            schema_type: Filter by simulation type ("DES", "SD")
            domain: Filter by application domain
            complexity: Filter by complexity level
            tags: Filter by tags (must match all provided tags)
            include_user: Include user-created templates
            search_term: Search in template names and descriptions

        Returns:
            List of matching templates with metadata and usage statistics
        """
        try:
            templates = template_manager.list_templates(
                schema_type=schema_type,
                domain=domain,
                complexity=complexity,
                tags=tags,
                include_user=include_user,
                search_term=search_term
            )

            return ResponseBuilder.list_response(
                items=templates,
                total_count=len(templates),
                filters_applied={
                    "schema_type": schema_type,
                    "domain": domain,
                    "complexity": complexity,
                    "tags": tags,
                    "include_user": include_user,
                    "search_term": search_term
                }
            )

        except Exception as e:
            return MCPErrorHandler.file_operation_error(
                "list",
                "template_collection",
                str(e),
                ["Check template_manager is accessible", "Verify filter parameters"]
            )

    @mcp.tool()
    def load_template(
        template_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> dict:
        """
        Load a simulation template by ID or name for model development.

        This tool retrieves complete template configurations including the validated
        model structure, metadata, usage notes, and customization guidance. Templates
        provide tested starting points that can be immediately used or customized.

        TEMPLATE ACCESS:

        By Template ID (recommended):
        load_template(template_id="abc123...")

        By Template Name:
        load_template(name="Hospital Triage System")

        COMPLETE TEMPLATE DATA:

        Each loaded template includes:
        - Full model configuration (ready for validation/simulation)
        - Comprehensive metadata (author, version, tags, domain)
        - Usage notes explaining the template's purpose
        - Customization tips for common modifications
        - Domain-specific examples and variations
        - Usage statistics and popularity metrics

        TEMPLATE EXAMPLES:

        Healthcare Templates:
        - Hospital Triage: Emergency vs routine patient prioritization
        - Clinic Operations: Appointment scheduling with walk-ins
        - Emergency Department: Multi-level triage with resource constraints

        Manufacturing Templates:
        - Production Line: Sequential processing with quality control
        - Batch Operations: Fixed-size batch processing with setup times
        - Assembly Line: Parallel stations with synchronization points

        Service Templates:
        - Call Center: Multi-skill agents with different service channels
        - Bank Branch: Multiple teller types with specialized services
        - Restaurant: Dining room and takeout with shared kitchen resources

        IMMEDIATE USAGE:

        # Load and validate template
        template = load_template(name="Single Server Queue")
        validate_model(template["model"])

        # Customize and save
        template["model"]["entity_types"][0]["arrival_distribution"]["rate"] = 2.0
        save_model(template["model"], "My Custom Queue")

        # Load and simulate
        template = load_template(name="Hospital Triage System")
        simulate_des(template["model"])

        CUSTOMIZATION GUIDANCE:

        Each template provides specific customization tips:
        - Parameter ranges and typical values
        - Common modifications for different scenarios
        - Extension points for additional complexity
        - Performance considerations and trade-offs

        TEMPLATE METADATA:

        Comprehensive information for informed selection:
        - Domain classification and use cases
        - Complexity level and prerequisites
        - Author and version information
        - Usage statistics and community feedback
        - Related templates and alternatives

        DEVELOPMENT WORKFLOW:

        1. Browse available templates: list_templates()
        2. Load promising template: load_template(name="...")
        3. Review model structure and usage notes
        4. Customize parameters for your scenario
        5. Validate customized model: validate_model()
        6. Save your version: save_model()
        7. Run simulation: simulate_des()

        Args:
            template_id: Unique template identifier (preferred)
            name: Template name (uses first match if multiple exist)

        Returns:
            Complete template with model configuration, metadata, and guidance
        """
        if not template_id and not name:
            return MCPErrorHandler.parameter_error(
                "template_identifier",
                None,
                "template_id or name",
                "Provide either template_id or name parameter"
            )

        try:
            result = template_manager.load_template(
                template_id=template_id,
                name=name
            )

            if result.get("loaded", False):
                return ResponseBuilder.template_response(
                    template_data=result,
                    usage_info={
                        "loaded_by": "template_id" if template_id else "name",
                        "identifier": template_id or name,
                        "ready_for_customization": True
                    },
                    customization_guidance=result.get("customization_tips", [])
                )
            else:
                return MCPErrorHandler.file_operation_error(
                    "load",
                    template_id or name,
                    result.get("error", "Template not found"),
                    [
                        "Check template identifier is correct",
                        "Use list_templates() to see available options",
                        "Verify template exists in collection"
                    ]
                )

        except Exception as e:
            return MCPErrorHandler.file_operation_error(
                "load",
                template_id or name,
                str(e),
                ["Check template_manager is accessible", "Verify template identifier format"]
            )

    @mcp.tool()
    def save_template(
        model: dict,
        name: str,
        description: str = "",
        domain: Optional[str] = None,
        complexity: str = "intermediate",
        tags: Optional[list] = None,
        usage_notes: str = "",
        customization_tips: Optional[list] = None,
        overwrite: bool = False
    ) -> dict:
        """
        Save a simulation model as a reusable template for future development.

        This tool creates user templates from validated simulation models, making successful
        configurations available for reuse and sharing. Templates include comprehensive
        metadata and guidance to facilitate future customization and learning.

        TEMPLATE CREATION WORKFLOW:

        1. Develop and validate your model
        2. Test through simulation to ensure correctness
        3. Save as template with descriptive metadata
        4. Add usage notes and customization guidance
        5. Template becomes available in list_templates()

        COMPREHENSIVE METADATA:

        Required Information:
        - name: Descriptive template name
        - model: Complete validated model configuration

        Optional Metadata:
        - description: Detailed explanation of template purpose
        - domain: Application area (auto-detected if not provided)
        - complexity: Difficulty level (basic, intermediate, advanced)
        - tags: Searchable keywords for discovery
        - usage_notes: Instructions and context for users
        - customization_tips: Specific guidance for modifications

        INTELLIGENT AUTO-DETECTION:

        Domain Detection:
        System analyzes model content to classify domain:
        - Healthcare: Detects medical terminology and patient flows
        - Manufacturing: Identifies production and quality processes
        - Service: Recognizes customer service patterns
        - Transportation: Finds logistics and routing elements

        Schema Type Detection:
        Automatically determines simulation paradigm:
        - DES: Discrete-event structures (entity_types, resources)
        - SD: System dynamics abstractModel structure

        USAGE EXAMPLES:

        # Save basic template
        save_template(
            model=my_model,
            name="My Custom Queue",
            description="Single server with custom arrival pattern"
        )

        # Save with comprehensive metadata
        save_template(
            model=hospital_model,
            name="ICU Patient Flow",
            description="Intensive care unit with bed management",
            domain="healthcare",
            complexity="advanced",
            tags=["hospital", "icu", "beds", "critical-care"],
            usage_notes="Designed for 20-bed ICU with 24/7 operations",
            customization_tips=[
                "Adjust bed capacity based on hospital size",
                "Modify patient acuity distributions for different populations",
                "Add specialized equipment resources as needed"
            ]
        )

        EFFECTIVE TAGGING:

        Process Tags: ["queue", "batch", "priority", "routing"]
        Industry Tags: ["hospital", "factory", "service", "logistics"]
        Feature Tags: ["failures", "scheduling", "multi-resource", "statistics"]
        Complexity Tags: ["beginner", "tutorial", "advanced", "research"]

        USAGE NOTES GUIDELINES:

        Effective usage notes include:
        - Template purpose and intended use cases
        - Key assumptions and limitations
        - Typical parameter ranges and values
        - Performance characteristics and scalability
        - Related templates and alternatives

        CUSTOMIZATION TIPS:

        Helpful customization guidance:
        - Common parameter modifications
        - Extension points for additional features
        - Performance optimization opportunities
        - Domain-specific variations
        - Integration with other templates

        TEMPLATE MANAGEMENT:

        Overwrite Protection:
        - Default: Prevents accidental overwrites
        - Set overwrite=True to replace existing template
        - Maintains creation date and usage statistics

        Version Control:
        - Templates track creation and modification dates
        - Usage statistics help identify popular patterns
        - User templates distinguished from built-in collection

        Args:
            model: Complete simulation model configuration
            name: Descriptive template name (must be unique)
            description: Detailed explanation of template purpose
            domain: Application domain (auto-detected if None)
            complexity: Difficulty level (basic, intermediate, advanced)
            tags: List of searchable keywords
            usage_notes: Instructions and context for template users
            customization_tips: Specific guidance for common modifications
            overwrite: Whether to replace existing template with same name

        Returns:
            Save confirmation with template metadata and assigned ID
        """
        if not name:
            return MCPErrorHandler.parameter_error(
                "name",
                None,
                "non-empty string",
                "Template name is required"
            )

        if not model:
            return MCPErrorHandler.parameter_error(
                "model",
                model,
                "non-empty dictionary",
                "Valid model configuration is required"
            )

        try:
            result = template_manager.save_template(
                model=model,
                name=name,
                description=description,
                domain=domain,
                complexity=complexity,
                tags=tags,
                usage_notes=usage_notes,
                customization_tips=customization_tips,
                overwrite=overwrite
            )

            if result.get("saved", False):
                return ResponseBuilder.model_operation_response(
                    operation="save_template",
                    success=True,
                    model_name=name,
                    template_id=result.get("template_id"),
                    metadata=result.get("metadata", {}),
                    message=f"Template '{name}' saved successfully",
                    usage_info={
                        "available_in": "list_templates()",
                        "load_with": f"load_template(name='{name}')",
                        "domain_detected": result.get("detected_domain"),
                        "schema_type": result.get("schema_type")
                    }
                )
            else:
                return ResponseBuilder.model_operation_response(
                    operation="save_template",
                    success=False,
                    model_name=name,
                    error=result.get("error", "Template save failed"),
                    suggestions=[
                        "Check template name is unique (or use overwrite=True)",
                        "Verify model is valid",
                        "Ensure template_manager is accessible"
                    ]
                )

        except Exception as e:
            return MCPErrorHandler.file_operation_error(
                "save_template",
                name,
                str(e),
                [
                    "Check model format is valid",
                    "Verify template name doesn't conflict",
                    "Ensure sufficient storage space"
                ]
            )

    @mcp.tool()
    def delete_template(name: str, confirm: bool = False) -> dict:
        """
        Delete a user template with confirmation requirement.

        This tool provides safe template deletion with confirmation requirements
        to prevent accidental loss of template work. Built-in templates cannot be deleted.

        SAFETY FEATURES:
        - Requires explicit confirmation flag
        - Returns template metadata before deletion
        - Only allows deletion of user templates
        - Provides backup suggestions

        Args:
            name: Name of template to delete
            confirm: Must be True to actually delete the template

        Returns:
            Deletion status with safety information
        """
        try:
            if not confirm:
                # Return template info and require confirmation
                load_result = template_manager.load_template(name=name)
                if not load_result.get("loaded", False):
                    return MCPErrorHandler.file_operation_error(
                        "delete_template",
                        name,
                        "Template not found",
                        ["Check template name", "Use list_templates() to see available templates"]
                    )

                # Check if it's a built-in template
                template_metadata = load_result.get("metadata", {})
                if template_metadata.get("template_type") == "built_in":
                    return MCPErrorHandler.parameter_error(
                        "template_type",
                        "built_in",
                        "user_template",
                        "Built-in templates cannot be deleted"
                    )

                return ResponseBuilder.model_operation_response(
                    operation="delete_template",
                    success=False,
                    model_name=name,
                    message="Confirmation required",
                    template_info=template_metadata,
                    warning="Set confirm=True to actually delete this template",
                    suggestions=[
                        "Review template metadata above",
                        "Export template as backup before deletion",
                        "Use delete_template(name, confirm=True) to proceed"
                    ]
                )

            # Perform actual deletion
            result = template_manager.delete_template(name)

            if result.get("deleted", False):
                return ResponseBuilder.model_operation_response(
                    operation="delete_template",
                    success=True,
                    model_name=name,
                    message=f"Template '{name}' deleted successfully",
                    deleted_metadata=result.get("metadata", {}),
                    undo_info="Template data is permanently removed"
                )
            else:
                return ResponseBuilder.model_operation_response(
                    operation="delete_template",
                    success=False,
                    model_name=name,
                    error=result.get("error", "Deletion failed"),
                    suggestions=["Check template exists", "Verify it's a user template"]
                )

        except Exception as e:
            return MCPErrorHandler.file_operation_error(
                "delete_template",
                name,
                str(e),
                ["Check template_manager is accessible", "Verify template name"]
            )