"""
Validation and help tools for MCP server.

This module implements comprehensive validation functionality with schema detection,
error analysis, and documentation assistance for simulation models.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional, List

from ..shared.error_handlers import MCPErrorHandler
from ..shared.response_builders import ResponseBuilder
from model_builder.multi_schema_validator import MultiSchemaValidator
from model_builder.schema_documentation import schema_documentation_provider


def register_validation_tools(mcp: FastMCP) -> None:
    """Register validation and help tools."""

    @mcp.tool()
    def validate_model(
        model: dict,
        schema_type: Optional[str] = None,
        validation_mode: str = "partial"
    ) -> dict:
        """
        Validate simulation model JSON against appropriate schema with LLM-optimized feedback.

        This tool provides comprehensive validation for simulation models with detailed error
        messages, quick fixes, and actionable suggestions designed for AI assistant comprehension.

        VALIDATION MODES:
        - "partial": Validate only provided sections (default for iterative development)
        - "strict": Full schema compliance required (use before simulation execution)
        - "structure": Check structure without business rules (quick structural check)

        SCHEMA AUTO-DETECTION:
        The tool automatically detects schema type from model structure:
        - DES: Looks for entity_types, resources, processing_rules
        - SD: Looks for abstractModel structure (PySD-compatible JSON format)
        - Explicit: Use "schema_type" field in model for explicit declaration

        RESPONSE INCLUDES:
        - Detailed validation errors with quick fixes
        - Missing required sections with examples
        - Completeness percentage (0.0 to 1.0)
        - Actionable suggestions for improvement
        - Prioritized next steps for development

        LLM-OPTIMIZED ERROR MESSAGES:
        Each error includes:
        - Exact path to problematic field
        - Clear explanation of the issue
        - Quick fix suggestion
        - Correct example for reference
        - Schema reference for deeper understanding

        COMMON USAGE PATTERNS:

        # Basic validation during development
        validate_model({"entity_types": {"customer": {"probability": 0.8}}})

        # Strict validation before simulation
        validate_model(complete_model, validation_mode="strict")

        # Structure check for large models
        validate_model(model, validation_mode="structure")

        # Explicit schema type override
        validate_model(model, schema_type="DES")

        Args:
            model: JSON model dictionary to validate
            schema_type: Optional schema type override ("DES", "SD", etc.) - auto-detected if None
            validation_mode: Validation strictness level

        Returns:
            Comprehensive validation result with errors, suggestions, and next steps
        """
        try:
            validator = MultiSchemaValidator()
            result = validator.validate_model(model, schema_type, validation_mode)

            # Convert ValidationResult to standardized response
            return ResponseBuilder.validation_response(
                valid=result.valid,
                errors=[
                    {
                        "path": error.path,
                        "message": error.message,
                        "current_value": error.current_value,
                        "expected": error.expected,
                        "quick_fix": error.quick_fix,
                        "example": error.example or {},
                        "schema_reference": error.schema_reference
                    }
                    for error in result.errors
                ],
                completeness=result.completeness,
                suggestions=result.suggestions,
                schema_type=result.schema_type,
                validation_mode=result.validation_mode
            )

        except Exception as e:
            return ResponseBuilder.validation_response(
                valid=False,
                errors=[{
                    "path": "root",
                    "message": f"Validation error: {str(e)}",
                    "current_value": None,
                    "expected": "Valid model structure",
                    "quick_fix": "Check model format and syntax",
                    "example": {},
                    "schema_reference": "General validation"
                }],
                completeness=0.0,
                suggestions=["Check model format and try again"],
                schema_type="unknown",
                validation_mode=validation_mode
            )

    @mcp.tool()
    def get_schema_help(
        schema_type: str,
        section_path: Optional[str] = None,
        include_examples: bool = True,
        detail_level: str = "standard"
    ) -> dict:
        """
        Get comprehensive schema documentation and examples for any simulation type.

        This tool provides dynamic, context-aware help for building simulation models with
        extensive examples, validation rules, and LLM-optimized guidance for any schema section.
        Supports both System Dynamics (SD) and Discrete Event Simulation (DES) schemas.

        SUPPORTED SCHEMA TYPES:
        - "SD": System Dynamics models with PySD JSON format
        - "DES": Discrete Event Simulation models with SimPy integration

        FLEXIBLE PATH RESOLUTION:
        - Full schema: get_schema_help("SD") or get_schema_help("DES")
        - Main sections: get_schema_help("SD", "abstractModel") or get_schema_help("DES", "entity_types")
        - Nested paths: get_schema_help("SD", "abstractModel.sections") or get_schema_help("DES", "processing_rules.steps")

        COMPREHENSIVE DOCUMENTATION:
        Each response includes:
        - Clear descriptions and requirements
        - Structural information and constraints
        - Validation rules and business logic
        - Multiple practical examples
        - Related sections and common patterns
        - LLM-optimized guidance

        DOMAIN-SPECIFIC EXAMPLES:

        SD Examples cover:
        - Demographics: Population growth, birth/death rates
        - Economics: Capital accumulation, economic growth
        - Epidemiology: SIR models, disease spread
        - Supply Chain: Inventory management, delays

        DES Examples cover:
        - Healthcare: Hospital triage, patient flow, emergency departments
        - Manufacturing: Production lines, quality control, equipment failures
        - Service: Customer segments, queue management, service levels
        - Transportation: Logistics, scheduling, resource allocation

        DETAIL LEVELS:
        - "brief": Essential information only
        - "standard": Comprehensive documentation (default)
        - "detailed": Full technical specifications

        COMMON USAGE PATTERNS:

        # System Dynamics (SD) Examples:
        get_schema_help("SD")                           # Full SD schema overview
        get_schema_help("SD", "abstractModel")          # Learn about PySD JSON structure
        get_schema_help("SD", "abstractModel.sections") # Understanding sections and elements

        # Discrete Event Simulation (DES) Examples:
        get_schema_help("DES")                          # Full DES schema overview
        get_schema_help("DES", "entity_types")          # Learn about entity types
        get_schema_help("DES", "processing_rules")      # Understand processing rules
        get_schema_help("DES", "balking_rules", detail_level="brief") # Get examples without technical details

        SECTION COVERAGE:

        SD Sections:
        - abstractModel: Top-level PySD JSON container with sections
        - sections: Model sections containing elements (variables)
        - elements: Individual variables (stocks, flows, auxiliaries)
        - components: Variable computation definitions
        - ast: Abstract syntax trees for equations
        - time_settings: Simulation time configuration

        DES Sections:
        - entity_types: Different entity classes with priorities and attributes
        - resources: System capacity with FIFO, priority, preemptive queues
        - processing_rules: Sequential steps with service time distributions
        - balking_rules: Customer abandonment before joining queues
        - reneging_rules: Customer abandonment while waiting in queues
        - simple_routing: Conditional routing based on entity attributes
        - basic_failures: Resource breakdowns and repair cycles
        - statistics: Data collection configuration
        - metrics: Custom metric names for domain-specific terminology

        DEVELOPMENT WORKFLOWS:

        SD Workflows:
        - Basic Model: abstractModel → sections → elements (stocks/flows/auxiliaries)
        - Population Model: Define stocks (population), flows (birth/death rates), auxiliaries (fractions)
        - Complex Model: Add feedback loops, delays, and nonlinear relationships

        DES Workflows:
        - Basic Service System: entity_types → resources → processing_rules
        - Advanced Queue Management: Add balking/reneging rules
        - Multi-Stage Process: Complex routing and failure handling

        LEARNING PROGRESSION:

        For SD Models:
        - Start with schema overview to understand PySD JSON structure
        - Learn abstractModel and sections concepts
        - Focus on elements and one-element-per-variable principle
        - Add components with proper AST syntax

        For DES Models:
        - Start with schema overview to understand structure
        - Focus on entity_types and resources for basic setup
        - Add processing_rules to define flow
        - Enhance with balking/reneging for realism
        - Configure statistics and metrics for analysis

        Args:
            schema_type: Schema type ("DES", "SD", etc.)
            section_path: Optional path to specific section (e.g., "entity_types", "processing_rules.steps")
            include_examples: Whether to include practical examples
            detail_level: Level of detail ("brief", "standard", "detailed")

        Returns:
            Comprehensive documentation with examples, validation rules, and guidance
        """
        try:
            result = schema_documentation_provider.get_schema_help(
                schema_type=schema_type,
                section_path=section_path,
                include_examples=include_examples,
                detail_level=detail_level
            )

            return ResponseBuilder.help_response(
                help_data=result,
                section_info={
                    "schema_type": schema_type,
                    "section_path": section_path or "root",
                    "detail_level": detail_level,
                    "examples_included": include_examples
                }
            )

        except Exception as e:
            return MCPErrorHandler.parameter_error(
                "schema_help_request",
                {"schema_type": schema_type, "section_path": section_path},
                "valid schema help request",
                "Check schema type and section path format"
            )

    @mcp.tool()
    def help_validation() -> dict:
        """
        VALIDATION HELP - Guide to finding the right validation tools.

        Shows all available validation tools and when to use each one.
        Perfect when you can't find the right tool or are getting validation errors.

        Returns:
            Complete guide to validation tools and usage examples
        """
        validation_guide = {
            "primary_tool": {
                "validate_model": {
                    "name": "validate_model",
                    "purpose": "Auto-detect and validate any simulation model (SD, DES, etc.)",
                    "use_when": "ALWAYS use this - it handles everything automatically",
                    "accepts": "Any simulation model: SD abstractModel format, DES configs",
                    "features": [
                        "Auto-detects model type (SD/DES)",
                        "Handles PySD abstractModel and DES configurations",
                        "Schema-specific validation with detailed errors",
                        "One tool for all validation needs",
                        "Proper completeness scoring per model type"
                    ]
                }
            },
            "auto_detection": {
                "sd_indicators": [
                    "abstractModel structure",
                    "PySD JSON format with abstractModel container"
                ],
                "des_indicators": [
                    "entity_types section",
                    "resources section",
                    "processing_rules section",
                    "SimPy configuration format"
                ],
                "how_it_works": "validate_model examines your model structure and automatically applies the correct validation rules"
            },
            "usage_examples": {
                "sd_template": {
                    "example": "validate_model(loaded_sd_template)",
                    "description": "Validates SD template with PySD JSON structure"
                },
                "sd_model": {
                    "example": "validate_model({'abstractModel': {...}})",
                    "description": "Validates raw SD model in PySD format"
                },
                "des_model": {
                    "example": "validate_model({'entity_types': {...}, 'resources': {...}})",
                    "description": "Validates DES model with SimPy configuration"
                },
                "strict_validation": {
                    "example": "validate_model(model, validation_mode='strict')",
                    "description": "Full validation before simulation"
                }
            },
            "validation_modes": {
                "partial": "Validate only provided sections (default for development)",
                "strict": "Full schema compliance required (use before simulation)",
                "structure": "Quick structural check without business rules"
            },
            "troubleshooting": {
                "low_completeness": "Add more required sections for your model type",
                "auto_detection_failed": "Add explicit schema_type field or check model structure",
                "validation_errors": "Follow suggested quick fixes in error messages"
            },
            "migration_note": "All validation consolidated into validate_model - no separate tools needed",
            "tip": "Just use validate_model for everything - it detects SD vs DES automatically!"
        }

        return ResponseBuilder.help_response(
            help_data=validation_guide,
            section_info={
                "help_type": "validation_guide",
                "tools_covered": ["validate_model", "get_schema_help"],
                "comprehensive": True
            },
            related_topics=[
                "get_schema_help for detailed schema documentation",
                "simulate_des and simulate_sd for running validated models",
                "save_model for preserving validated models"
            ]
        )

