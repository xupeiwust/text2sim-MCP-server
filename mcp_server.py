from mcp.server.fastmcp import FastMCP, Context
from DES.schema_validator import DESConfigValidator
import json
from pathlib import Path
import sys
import os
from typing import List

# Ensure the SD module is in the path
current_dir = Path(__file__).parent
root_dir = current_dir.parent  # Go up one level to the root where SD directory is
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import SD JSON integration (modern approach)
try:
    from SD.sd_integration import PySDJSONIntegration, SDIntegrationError, SDValidationError, SDModelBuildError, SDSimulationError
    print("✅ SD JSON integration imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"❌ Failed to import SD integration: {e}", file=sys.stderr)
    print(f"   Root directory: {root_dir}", file=sys.stderr)
    print(f"   Python path: {sys.path}", file=sys.stderr)
    # Provide fallback functionality for SD integration
    class DummySDIntegration:
        def validate_json_model(self, model): return {"is_valid": False, "errors": ["SD integration not available"]}
        def simulate_json_model(self, model, **kwargs): raise Exception("SD integration not available")
        def get_model_info(self, model): return {"error": "SD integration not available"}
        def convert_vensim_to_json(self, path): raise Exception("SD integration not available")
    PySDJSONIntegration = DummySDIntegration
    SDIntegrationError = Exception
    SDValidationError = Exception
    SDModelBuildError = Exception
    SDSimulationError = Exception

# Initialise the MCP server
mcp = FastMCP("text2sim-mcp-server")

def _generate_quick_fixes(errors):
    """Generate quick fix suggestions based on common error patterns."""
    fixes = []
    
    for error in errors:
        if "wait_times" in error and "collect_wait_times" not in error:
            fixes.append("Replace 'wait_times' with 'collect_wait_times' in statistics section")
        elif "resource_utilization" in error:
            fixes.append("Replace 'resource_utilization' with 'collect_utilization' in statistics section")
        elif "abandon_time" in error and "required property" in error:
            fixes.append("Add 'abandon_time': 'normal(30, 10)' to reneging rules (use distribution string)")
        elif "mtbf" in error and "not of type 'string'" in error:
            fixes.append("Change MTBF to distribution string: 'exp(300)' instead of 300")
        elif "conditions" in error and "required property" in error:
            fixes.append("Use 'conditions' array in simple_routing, not 'from_step'/'to_step'")
        elif "probabilities sum to" in error:
            fixes.append("Adjust entity_types probabilities to sum exactly to 1.0")
        elif "does not match" in error and "distribution" in error:
            fixes.append("Fix distribution format: use 'uniform(5,10)', 'normal(8,2)', or 'exp(5)'")
        elif "Additional properties are not allowed" in error:
            fixes.append("Check for typos in property names or unsupported properties")
        elif "resource" in error and "not found" in error:
            fixes.append("Ensure resource names in rules match those defined in 'resources' section")
    
    # Add generic helpful tips if no specific fixes found
    if not fixes:
        fixes.extend([
            "Check property names for typos",
            "Ensure all distributions are strings: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'",
            "Verify resource names match between sections",
            "Confirm entity probabilities sum to 1.0"
        ])
    
    return fixes[:3]  # Limit to top 3 most relevant fixes

@mcp.tool()
def simulate_des(config: dict) -> dict:
    """
    Advanced discrete-event simulation with comprehensive schema validation and SimPy integration.
    
    QUICK START - Basic Configuration:
    {
      "run_time": 480,
      "arrival_pattern": {"distribution": "exp(5)"},
      "entity_types": {
        "customer": {"probability": 1.0, "value": {"min": 10, "max": 50}, "priority": 5}
      },
      "resources": {
        "server": {"capacity": 1, "resource_type": "fifo"}
      },
      "processing_rules": {
        "steps": ["server"],
        "server": {"distribution": "uniform(3, 7)"}
      }
    }
    
    COMMON CONFIGURATION PATTERNS:
    
    Statistics Collection:
    "statistics": {
      "collect_wait_times": true,
      "collect_utilization": true,
      "collect_queue_lengths": false,
      "warmup_period": 60
    }
    
    Balking (Customers Leave):
    "balking_rules": {
      "overcrowding": {"type": "queue_length", "resource": "server_name", "max_length": 8}
    }
    
    Reneging (Customers Abandon Queue):
    "reneging_rules": {
      "impatience": {
        "abandon_time": "normal(30, 10)",
        "priority_multipliers": {"1": 5.0, "5": 1.0, "10": 0.3}
      }
    }
    
    Resource Failures:
    "basic_failures": {
      "machine_name": {
        "mtbf": "exp(480)",
        "repair_time": "uniform(20, 40)"
      }
    }
    
    Conditional Routing:
    "simple_routing": {
      "priority_check": {
        "conditions": [
          {"attribute": "priority", "operator": "<=", "value": 2, "destination": "express_lane"}
        ],
        "default_destination": "regular_service"
      }
    }
    
    Custom Metrics Names:
    "metrics": {
      "arrival_metric": "customers_arrived",
      "served_metric": "customers_served",
      "value_metric": "total_revenue"
    }
    
    DISTRIBUTION FORMATS (All strings):
    - "uniform(5, 10)" - Uniform between 5 and 10
    - "normal(8, 2)" - Normal with mean=8, std=2
    - "exp(5)" - Exponential with mean=5 (NOT rate=5)
    - "gauss(10, 3)" - Same as normal
    
    RESOURCE TYPES:
    - "fifo" - First-in-first-out (default)
    - "priority" - Priority queue (1=highest, 10=lowest)
    - "preemptive" - Priority with preemption capability
    
    ENTITY CONFIGURATION:
    "entity_types": {
      "vip": {
        "probability": 0.2,           // Must sum to 1.0 across all types
        "priority": 1,                // 1=highest, 10=lowest
        "value": {"min": 100, "max": 500},
        "attributes": {"membership": "gold", "urgent": true}  // For routing
      }
    }
    
    PROCESSING FLOW:
    "processing_rules": {
      "steps": ["reception", "service", "checkout"],  // Sequential steps
      "reception": {"distribution": "uniform(2, 5)"},
      "service": {
        "distribution": "normal(10, 2)",              // Default for all entities
        "conditional_distributions": {               // Override by entity type
          "vip": "normal(5, 1)",
          "regular": "normal(12, 3)"
        }
      }
    }
    
    COMMON MISTAKES TO AVOID:
    - Don't use "wait_times" → Use "collect_wait_times"
    - Don't use numbers for distributions → Use strings like "exp(300)"
    - Don't use "from_step"/"to_step" → Use "conditions" array in routing
    - Don't forget "abandon_time" in reneging_rules
    - Ensure probabilities sum to exactly 1.0
    - Resource names in steps must match resource definitions
    
    PRO TIPS:
    - Start simple, add complexity gradually
    - Use priority 1-3 for urgent, 4-6 for normal, 7-10 for low priority
    - Set warmup_period to exclude initial transient behavior
    - Use conditional_distributions for different entity types
    - Resource failures use resource names as keys, not separate "resource" field
    
    COMPLETE MANUFACTURING EXAMPLE:
    {
      "run_time": 960,
      "entity_types": {
        "standard": {"probability": 0.6, "value": {"min": 400, "max": 400}, "priority": 5},
        "premium": {"probability": 0.1, "value": {"min": 1200, "max": 1200}, "priority": 1}
      },
      "resources": {
        "inspection": {"capacity": 2, "resource_type": "priority"},
        "assembly": {"capacity": 4, "resource_type": "priority"}
      },
      "processing_rules": {
        "steps": ["inspection", "assembly"],
        "inspection": {"distribution": "uniform(3, 7)"},
        "assembly": {
          "conditional_distributions": {
            "standard": "uniform(20, 30)",
            "premium": "uniform(35, 50)"
          }
        }
      },
      "balking_rules": {
        "overcrowding": {"type": "queue_length", "resource": "inspection", "max_length": 12}
      },
      "basic_failures": {
        "assembly": {"mtbf": "exp(300)", "repair_time": "uniform(20, 40)"}
      },
      "arrival_pattern": {"distribution": "uniform(8, 15)"}
    }
    
    Returns simulation results with counts, efficiency metrics, utilization, and wait times.
    Validation errors include helpful suggestions and examples for quick correction.
    """
    try:
        # Validate and normalize configuration
        validator = DESConfigValidator()
        normalized_config, errors = validator.validate_and_normalize(config)
        
        if errors:
            # Generate helpful response with quick fixes
            error_response = {
                "error": "Configuration validation failed",
                "details": errors,
                "quick_fixes": _generate_quick_fixes(errors),
                "help": "Common issues: Check property names, ensure distributions are strings, verify probabilities sum to 1.0"
            }
            
            # Add schema examples if validation failed
            if any("Schema validation error" in error for error in errors):
                error_response["schema_help"] = "Use the patterns shown in the tool description above for correct formatting"
            
            return error_response
        
        # Import and run simulation
        from DES.simulator import SimulationModel
        
        model = SimulationModel(normalized_config)
        return model.run()
        
    except ImportError:
        # Fallback to old system during transition
        from DES.des_utils import run_simulation
        return run_simulation(config)
        
    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}

# Old file-based SD tools removed - now using JSON-based approach exclusively

# Import new model builder infrastructure
from model_builder.multi_schema_validator import MultiSchemaValidator
from model_builder.model_state_manager import model_state_manager
from model_builder.schema_registry import schema_registry
from model_builder.schema_documentation import schema_documentation_provider
from model_builder.template_manager import template_manager

# Initialize model builder components
multi_validator = MultiSchemaValidator()

@mcp.tool()
def validate_model(
    model: dict,
    schema_type: str = None,
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
    - SD: Looks for abstractModel, template_info.schema_type=SD, model.abstractModel
    - Template: Supports full template format with template_info and model sections
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
        result = multi_validator.validate_model(model, schema_type, validation_mode)
        
        # Convert ValidationResult to dictionary for MCP response
        return {
            "valid": result.valid,
            "schema_type": result.schema_type,
            "validation_mode": result.validation_mode,
            "completeness": result.completeness,
            "errors": [
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
            "missing_required": result.missing_required,
            "suggestions": result.suggestions,
            "next_steps": result.next_steps
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "schema_type": "unknown",
            "validation_mode": validation_mode,
            "completeness": 0.0,
            "suggestions": ["Check model format and try again"]
        }

@mcp.tool()
def save_model(
    model: dict,
    name: str = None,
    notes: str = None,
    tags: list = None,
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
        validation_result = multi_validator.validate_model(model)
        validation_dict = {
            "valid": validation_result.valid,
            "completeness": validation_result.completeness,
            "missing_required": validation_result.missing_required
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
        
        return result
        
    except Exception as e:
        return {
            "saved": False,
            "error": f"Save error: {str(e)}",
            "message": "Failed to save model"
        }

@mcp.tool()
def load_model(
    name: str = None,
    schema_type: str = None,
    tags: list = None
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
        result = model_state_manager.load_model(name, schema_type, tags)
        return result
        
    except Exception as e:
        return {
            "loaded": False,
            "error": f"Load error: {str(e)}",
            "available_models": []
        }

@mcp.tool()
def export_model(
    name: str = None,
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
            return {
                "exported": False,
                "error": "No model specified and no model previously loaded",
                "suggestion": "Specify model name or load a model first"
            }
        
        # Load the model
        load_result = model_state_manager.load_model(model_name)
        if not load_result.get("loaded", False):
            return {
                "exported": False,
                "error": f"Model '{model_name}' not found",
                "available_models": list(model_state_manager.models.keys())
            }
        
        model_data = load_result["model"]
        metadata = load_result.get("metadata", {})
        
        # Format JSON based on requested format
        if format == "compact":
            json_string = json.dumps(model_data, separators=(',', ':'))
        elif format == "pretty":
            json_string = json.dumps(model_data, indent=2, separators=(',', ': '))
        elif format == "conversation":
            json_string = json.dumps(model_data, indent=2, separators=(',', ': '))
        else:
            json_string = json.dumps(model_data, indent=2, separators=(',', ': '))
        
        # Include metadata if requested
        if include_metadata:
            export_data = {
                "model": model_data,
                "metadata": metadata
            }
            if format == "compact":
                json_string = json.dumps(export_data, separators=(',', ':'))
            else:
                json_string = json.dumps(export_data, indent=2, separators=(',', ': '))
        
        # Calculate size estimates
        char_count = len(json_string)
        estimated_tokens = char_count // 4  # Rough estimate: 4 chars per token
        
        # Create conversation template
        conversation_template = ""
        if format == "conversation":
            conversation_template = f"""Here's my current simulation model:

```json
{json_string}
```

Please help me continue developing this model."""
        
        return {
            "exported": True,
            "model_name": model_name,
            "format": format,
            "json_string": json_string,
            "copy_paste_ready": True,
            "character_count": char_count,
            "estimated_tokens": estimated_tokens,
            "conversation_template": conversation_template,
            "metadata_included": include_metadata,
            "usage_tip": "Copy the json_string value and paste it into a new conversation"
        }
        
    except Exception as e:
        return {
            "exported": False,
            "error": f"Export error: {str(e)}"
        }

@mcp.tool()
def get_schema_help(
    schema_type: str,
    section_path: str = None,
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

    💡 COMMON USAGE PATTERNS:

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
        
        return result
        
    except Exception as e:
        return {
            "error": f"Schema help error: {str(e)}",
            "schema_type": schema_type,
            "section_path": section_path,
            "suggestion": "Check schema type and section path format"
        }


@mcp.tool()
def help_validation() -> dict:
    """
    🆘 VALIDATION HELP - Guide to finding the right validation tools.

    Shows all available validation tools and when to use each one.
    Perfect when you can't find the right tool or are getting validation errors.

    Returns:
        Complete guide to validation tools and usage examples
    """
    return {
        "primary_tool": {
            "validate_model": {
                "name": "🎯 validate_model - UNIFIED VALIDATION TOOL",
                "purpose": "Auto-detect and validate any simulation model (SD, DES, etc.)",
                "use_when": "ALWAYS use this - it handles everything automatically",
                "accepts": "Any simulation model: SD templates, DES configs, raw models",
                "features": [
                    "🔍 Auto-detects model type (SD/DES)",
                    "📋 Handles template format and raw models",
                    "✅ Schema-specific validation with detailed errors",
                    "🚀 One tool for all validation needs",
                    "📊 Proper completeness scoring per model type"
                ]
            }
        },
        "auto_detection": {
            "sd_indicators": [
                "abstractModel structure",
                "template_info.schema_type=SD",
                "model.abstractModel section",
                "PySD JSON format"
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
        "migration_note": "🔄 All validation consolidated into validate_model - no separate tools needed",
        "tip": "📋 Just use validate_model for everything - it detects SD vs DES automatically!"
    }


@mcp.tool()
def list_templates(
    schema_type: str = None,
    domain: str = None,
    complexity: str = None,
    tags: list = None,
    include_user: bool = True,
    search_term: str = None
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
        
        return {
            "templates": templates,
            "count": len(templates),
            "filters_applied": {
                "schema_type": schema_type,
                "domain": domain,
                "complexity": complexity,
                "tags": tags,
                "include_user": include_user,
                "search_term": search_term
            }
        }
        
    except Exception as e:
        return {
            "error": f"Template listing error: {str(e)}",
            "suggestion": "Check filter parameters and try again"
        }

@mcp.tool()
def load_template(
    template_id: str = None,
    name: str = None
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
    try:
        result = template_manager.load_template(
            template_id=template_id,
            name=name
        )
        
        return result
        
    except Exception as e:
        return {
            "error": f"Template loading error: {str(e)}",
            "suggestion": "Check template ID or name, use list_templates() to see available options"
        }

@mcp.tool()
def save_template(
    model: dict,
    name: str,
    description: str = "",
    domain: str = None,
    complexity: str = "intermediate",
    tags: list = None,
    usage_notes: str = "",
    customization_tips: list = None,
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
    - SD: System dynamics structures (stocks, flows) [future]
    
    💡 USAGE EXAMPLES:
    
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
        
        return result
        
    except Exception as e:
        return {
            "error": f"Template saving error: {str(e)}",
            "suggestion": "Check model validity and template name uniqueness"
        }

@mcp.tool()
def run_multiple_simulations(
    config: dict,
    replications: int = 10,
    random_seed_base: int = None,
    confidence_levels: List[float] = None
) -> dict:
    """
    Run multiple independent simulation replications with comprehensive statistical analysis.
    
    This tool provides industry-standard statistical reporting for simulation results,
    including confidence intervals, variability measures, and distribution analysis.
    Essential for reliable decision-making and professional simulation studies.
    
    Statistical Outputs Include:
    - Central tendency: Mean, median, mode
    - Variability: Standard deviation, coefficient of variation, range
    - Confidence intervals: 90%, 95%, 99% (configurable)
    - Distribution analysis: Percentiles, normality tests, outlier detection
    - Sample statistics: Standard error, degrees of freedom, relative precision
    
    Industry Standard Format:
    Results reported as "Mean ± Half-Width (CI%) [n=replications]"
    Example: "Utilization: 0.785 ± 0.023 (95%) [n=20]"
    
    Args:
        config: Complete simulation configuration (same as simulate_des)
        replications: Number of independent runs (default: 10, minimum: 2)
        random_seed_base: Base seed for reproducible results (optional)
        confidence_levels: List of confidence levels (default: [0.90, 0.95, 0.99])
        
    Returns:
        Comprehensive statistical analysis with individual replication data
    """
    try:
        # Import required modules
        from DES.replication_analysis import create_replication_analyzer
        import random
        import time
        
        # Validate inputs
        if replications < 2:
            return {
                "error": "Minimum 2 replications required for statistical analysis",
                "suggestion": "Increase replications to at least 2 for meaningful statistics"
            }
        
        if replications > 100:
            return {
                "error": "Maximum 100 replications allowed to prevent excessive computation",
                "suggestion": "Consider using 20-50 replications for most applications"
            }
        
        # Set up confidence levels
        if confidence_levels is None:
            confidence_levels = [0.90, 0.95, 0.99]
        
        # Validate configuration
        try:
            validator = DESConfigValidator()
            normalized_config, errors = validator.validate_and_normalize(config)
            
            if errors:
                return {
                    "error": "Invalid simulation configuration",
                    "validation_errors": errors,
                    "suggestion": "Fix configuration errors before running replications"
                }
            
            # Use the normalized configuration for simulations
            config = normalized_config
            
        except Exception as e:
            return {
                "error": f"Configuration validation failed: {str(e)}",
                "suggestion": "Check configuration format and required fields"
            }
        
        # Set up random seeds for reproducibility
        if random_seed_base is None:
            random_seed_base = int(time.time())
        
        # Run replications
        replication_results = []
        failed_replications = []
        
        print(f"Running {replications} simulation replications...")
        
        for i in range(replications):
            try:
                # Set unique seed for this replication
                replication_seed = random_seed_base + i * 1000
                random.seed(replication_seed)
                
                print(f"  Replication {i+1}/{replications}...")
                
                # Run single simulation
                result = simulate_des(config)
                
                if "error" in result:
                    failed_replications.append({
                        "replication": i + 1,
                        "error": result["error"],
                        "seed": replication_seed
                    })
                else:
                    # Add replication metadata
                    result["_replication_info"] = {
                        "replication_number": i + 1,
                        "random_seed": replication_seed,
                        "timestamp": time.time()
                    }
                    replication_results.append(result)
                    
            except Exception as e:
                failed_replications.append({
                    "replication": i + 1,
                    "error": str(e),
                    "seed": replication_seed
                })
        
        # Check if we have enough successful replications
        successful_count = len(replication_results)
        if successful_count < 2:
            return {
                "error": f"Only {successful_count} successful replications out of {replications}",
                "failed_replications": failed_replications,
                "suggestion": "Check simulation configuration or reduce complexity"
            }
        
        # Perform statistical analysis
        analyzer = create_replication_analyzer()
        statistical_analysis = analyzer.analyze_replications(replication_results)
        
        # Generate industry-standard summary
        summary_report = analyzer.format_industry_summary(statistical_analysis)
        
        # Prepare final results
        final_results = {
            "statistical_analysis": statistical_analysis,
            "summary_report": summary_report,
            "execution_info": {
                "total_replications_requested": replications,
                "successful_replications": successful_count,
                "failed_replications": len(failed_replications),
                "random_seed_base": random_seed_base,
                "confidence_levels": confidence_levels
            }
        }
        
        # Include failure details if any
        if failed_replications:
            final_results["failed_replications"] = failed_replications
        
        print(f"Completed {successful_count} replications successfully!")
        return final_results
        
    except ImportError as e:
        return {
            "error": f"Required statistical modules not available: {str(e)}",
            "suggestion": "Install required dependencies: pip install scipy numpy"
        }
    except Exception as e:
        return {
            "error": f"Multiple replications failed: {str(e)}",
            "suggestion": "Check configuration and try with fewer replications"
        }

# ============================================================================
# SYSTEM DYNAMICS MCP TOOLS
# ============================================================================

# Initialize SD integration
sd_integration = PySDJSONIntegration()

@mcp.tool()
def simulate_sd(config: dict, parameters: dict = None, time_settings: dict = None) -> dict:
    """
    Advanced System Dynamics simulation with JSON-based model building.

    Create and simulate SD models using natural language descriptions converted
    to JSON configurations. Supports stocks, flows, auxiliaries, constants, and
    complex model structures.

    QUICK START - Basic SD Model:
    {
      "model_name": "Population Growth",
      "time_settings": {
        "initial_time": 0,
        "final_time": 100,
        "time_step": 0.25
      },
      "stocks": [
        {
          "name": "Population",
          "initial_value": 1000,
          "inflows": ["Birth Rate"],
          "units": "people"
        }
      ],
      "flows": [
        {
          "name": "Birth Rate",
          "expression": "Population * Birth Fraction",
          "units": "people/year"
        }
      ],
      "constants": [
        {
          "name": "Birth Fraction",
          "value": 0.05,
          "units": "1/year"
        }
      ]
    }

    COMMON PATTERNS:

    Stock and Flow:
    "stocks": [
      {
        "name": "Inventory",
        "initial_value": 100,
        "inflows": ["Production Rate"],
        "outflows": ["Sales Rate"],
        "units": "items"
      }
    ]

    Auxiliaries (Calculated Variables):
    "auxiliaries": [
      {
        "name": "Desired Inventory",
        "expression": "Sales Rate * Inventory Coverage",
        "units": "items"
      }
    ]

    Time Functions:
    "auxiliaries": [
      {
        "name": "Step Input",
        "expression": "STEP(10, 5)",
        "documentation": "Step from 0 to 10 at time 5"
      }
    ]

    Args:
        config: SD model configuration in JSON format
        parameters: Parameter value overrides
        time_settings: Simulation time configuration overrides

    Returns:
        Dictionary with simulation results and model metadata
    """
    try:
        # Extract time settings without modifying the model config
        initial_time = 0
        final_time = 100
        time_step = 1

        if time_settings:
            initial_time = time_settings.get("initial_time", initial_time)
            final_time = time_settings.get("final_time", final_time)
            time_step = time_settings.get("time_step", time_step)

        # Also check config for time_settings (backward compatibility)
        if "time_settings" in config:
            ts = config["time_settings"]
            initial_time = ts.get("initial_time", initial_time)
            final_time = ts.get("final_time", final_time)
            time_step = ts.get("time_step", time_step)

        # Run simulation with individual parameters (not time_settings dict)
        results = sd_integration.simulate_json_model(
            config,
            initial_time=initial_time,
            final_time=final_time,
            time_step=time_step,
            params=parameters
        )

        return {
            "success": True,
            "results": results,
            "model_info": {
                "model_name": config.get("model_name", "Unnamed Model"),
                "time_range": f"{len(results.get('Time', [0]))} time steps" if 'Time' in results else "Unknown",
                "variables": list(results.keys())
            }
        }

    except (SDValidationError, SDModelBuildError, SDSimulationError) as e:
        return {"error": f"SD simulation error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error in SD simulation: {str(e)}"}




@mcp.tool()
def convert_vensim_to_sd_json(file_path: str) -> dict:
    """
    Convert Vensim .mdl file to SD JSON format for use with simulate_sd.

    Enables importing existing Vensim models into the conversational SD workflow.

    Args:
        file_path: Path to Vensim .mdl file

    Returns:
        SD model in JSON format ready for simulate_sd tool
    """
    try:
        json_model = sd_integration.convert_vensim_to_json(file_path)

        return {
            "success": True,
            "model_json": json_model,
            "info": {
                "original_file": file_path,
                "conversion_type": "Vensim → SD JSON",
                "ready_for_simulation": True
            }
        }

    except (SDModelBuildError, FileNotFoundError) as e:
        return {"error": f"Vensim conversion error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected conversion error: {str(e)}"}




@mcp.tool()
def get_sd_model_info(config: dict) -> dict:
    """
    Analyze SD model configuration and provide detailed information.

    Shows model structure, complexity metrics, and validation status
    without running simulation.

    Args:
        config: SD model configuration

    Returns:
        Detailed model analysis and information
    """
    try:
        # Get basic model info
        model_info = sd_integration.get_model_info(config)

        # Add structure analysis if available
        if isinstance(config, dict) and "abstractModel" in config:
            abstract_model = config["abstractModel"]
            sections = abstract_model.get("sections", [])

            model_info.update({
                "validation_status": "pending",
                "complexity": _calculate_sd_complexity(config),
                "time_settings": config.get("time_settings", {}),
                "section_details": [
                    {
                        "name": section.get("name", ""),
                        "elements": len(section.get("elements", []))
                    }
                    for section in sections
                ]
            })

        return model_info

    except Exception as e:
        return {"error": f"SD model analysis error: {str(e)}"}


def _generate_sd_suggestions(errors: list) -> list:
    """Generate helpful suggestions for SD validation errors."""
    suggestions = []

    for error in errors:
        error_str = str(error).lower()
        if "abstractmodel" in error_str:
            suggestions.append("Ensure JSON follows PySD abstract model schema structure")
        elif "sections" in error_str:
            suggestions.append("Check that 'sections' array contains at least one main section")
        elif "originalpath" in error_str:
            suggestions.append("Provide 'originalPath' field in abstractModel")
        elif "elements" in error_str:
            suggestions.append("Verify model elements have required fields (name, components)")
        elif "components" in error_str:
            suggestions.append("Check component structure with type, subtype, and ast fields")

    if not suggestions:
        suggestions.extend([
            "Check JSON structure matches PySD abstract model schema",
            "Ensure all required fields are present",
            "Verify nested object structures are correct"
        ])

    return suggestions[:3]  # Limit to top 3 suggestions


def _generate_sd_quick_fixes(errors: list) -> list:
    """Generate quick fix suggestions for common SD errors."""
    fixes = []

    for error in errors:
        error_str = str(error).lower()
        if "required" in error_str and "abstractmodel" in error_str:
            fixes.append("Wrap model definition in 'abstractModel' object")
        elif "required" in error_str and "sections" in error_str:
            fixes.append("Add 'sections' array with at least one section")
        elif "required" in error_str and "originalpath" in error_str:
            fixes.append("Add 'originalPath' field with model file path")

    if not fixes:
        fixes.extend([
            "Check for missing required fields",
            "Verify JSON structure is valid",
            "Ensure proper nesting of objects"
        ])

    return fixes[:3]  # Limit to top 3 fixes


def _calculate_sd_complexity(config: dict) -> dict:
    """Calculate model complexity metrics for SD models."""
    try:
        if "abstractModel" in config:
            abstract_model = config["abstractModel"]
            sections = abstract_model.get("sections", [])

            total_elements = sum(len(section.get("elements", [])) for section in sections)
            total_components = sum(
                len(element.get("components", []))
                for section in sections
                for element in section.get("elements", [])
            )

            return {
                "sections": len(sections),
                "total_elements": total_elements,
                "total_components": total_components,
                "complexity_score": min(10, (total_elements + total_components) // 10),
                "estimated_build_time": f"{max(1, total_elements // 5)} seconds"
            }
        else:
            return {
                "complexity_score": 1,
                "message": "Model structure not recognized"
            }

    except Exception:
        return {
            "complexity_score": 0,
            "message": "Unable to calculate complexity"
        }


if __name__ == "__main__":
    mcp.run(transport='stdio')
