from mcp.server.fastmcp import FastMCP, Context
from DES.schema_validator import DESConfigValidator
import json
from pathlib import Path
import sys
import os

# Ensure the SD module is in the path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Import SD utilities
try:
    from SD.sd_utils import load_model_metadata, run_model_simulation, get_model_list, get_model_details
except ImportError:
    # Create SD directory if it doesn't exist
    sd_dir = current_dir / "SD"
    sd_dir.mkdir(exist_ok=True)
    
    # Reattempt import after ensuring directory exists
    from SD.sd_utils import load_model_metadata, run_model_simulation, get_model_list, get_model_details

# Initialise the MCP server
mcp = FastMCP("text2sim-mcp-server")

def _generate_quick_fixes(errors):
    """Generate quick fix suggestions based on common error patterns."""
    fixes = []
    
    for error in errors:
        if "wait_times" in error and "collect_wait_times" not in error:
            fixes.append("🔧 Replace 'wait_times' with 'collect_wait_times' in statistics section")
        elif "resource_utilization" in error:
            fixes.append("🔧 Replace 'resource_utilization' with 'collect_utilization' in statistics section")
        elif "abandon_time" in error and "required property" in error:
            fixes.append("🔧 Add 'abandon_time': 'normal(30, 10)' to reneging rules (use distribution string)")
        elif "mtbf" in error and "not of type 'string'" in error:
            fixes.append("🔧 Change MTBF to distribution string: 'exp(300)' instead of 300")
        elif "conditions" in error and "required property" in error:
            fixes.append("🔧 Use 'conditions' array in simple_routing, not 'from_step'/'to_step'")
        elif "probabilities sum to" in error:
            fixes.append("🔧 Adjust entity_types probabilities to sum exactly to 1.0")
        elif "does not match" in error and "distribution" in error:
            fixes.append("🔧 Fix distribution format: use 'uniform(5,10)', 'normal(8,2)', or 'exp(5)'")
        elif "Additional properties are not allowed" in error:
            fixes.append("🔧 Check for typos in property names or unsupported properties")
        elif "resource" in error and "not found" in error:
            fixes.append("🔧 Ensure resource names in rules match those defined in 'resources' section")
    
    # Add generic helpful tips if no specific fixes found
    if not fixes:
        fixes.extend([
            "🔍 Check property names for typos",
            "📝 Ensure all distributions are strings: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'",
            "🎯 Verify resource names match between sections",
            "⚖️ Confirm entity probabilities sum to 1.0"
        ])
    
    return fixes[:3]  # Limit to top 3 most relevant fixes

@mcp.tool()
def simulate_des(config: dict) -> dict:
    """
    Advanced discrete-event simulation with comprehensive schema validation and SimPy integration.
    
    🎯 QUICK START - Basic Configuration:
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
    
    📋 COMMON CONFIGURATION PATTERNS:
    
    ✅ Statistics Collection:
    "statistics": {
      "collect_wait_times": true,
      "collect_utilization": true,
      "collect_queue_lengths": false,
      "warmup_period": 60
    }
    
    ✅ Balking (Customers Leave):
    "balking_rules": {
      "overcrowding": {"type": "queue_length", "resource": "server_name", "max_length": 8}
    }
    
    ✅ Reneging (Customers Abandon Queue):
    "reneging_rules": {
      "impatience": {
        "abandon_time": "normal(30, 10)",
        "priority_multipliers": {"1": 5.0, "5": 1.0, "10": 0.3}
      }
    }
    
    ✅ Resource Failures:
    "basic_failures": {
      "machine_name": {
        "mtbf": "exp(480)",
        "repair_time": "uniform(20, 40)"
      }
    }
    
    ✅ Conditional Routing:
    "simple_routing": {
      "priority_check": {
        "conditions": [
          {"attribute": "priority", "operator": "<=", "value": 2, "destination": "express_lane"}
        ],
        "default_destination": "regular_service"
      }
    }
    
    ✅ Custom Metrics Names:
    "metrics": {
      "arrival_metric": "customers_arrived",
      "served_metric": "customers_served",
      "value_metric": "total_revenue"
    }
    
    🔧 DISTRIBUTION FORMATS (All strings):
    - "uniform(5, 10)" - Uniform between 5 and 10
    - "normal(8, 2)" - Normal with mean=8, std=2
    - "exp(5)" - Exponential with mean=5 (NOT rate=5)
    - "gauss(10, 3)" - Same as normal
    
    🏭 RESOURCE TYPES:
    - "fifo" - First-in-first-out (default)
    - "priority" - Priority queue (1=highest, 10=lowest)
    - "preemptive" - Priority with preemption capability
    
    📊 ENTITY CONFIGURATION:
    "entity_types": {
      "vip": {
        "probability": 0.2,           // Must sum to 1.0 across all types
        "priority": 1,                // 1=highest, 10=lowest
        "value": {"min": 100, "max": 500},
        "attributes": {"membership": "gold", "urgent": true}  // For routing
      }
    }
    
    🔄 PROCESSING FLOW:
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
    
    ⚠️ COMMON MISTAKES TO AVOID:
    - Don't use "wait_times" → Use "collect_wait_times"
    - Don't use numbers for distributions → Use strings like "exp(300)"
    - Don't use "from_step"/"to_step" → Use "conditions" array in routing
    - Don't forget "abandon_time" in reneging_rules
    - Ensure probabilities sum to exactly 1.0
    - Resource names in steps must match resource definitions
    
    💡 PRO TIPS:
    - Start simple, add complexity gradually
    - Use priority 1-3 for urgent, 4-6 for normal, 7-10 for low priority
    - Set warmup_period to exclude initial transient behavior
    - Use conditional_distributions for different entity types
    - Resource failures use resource names as keys, not separate "resource" field
    
    🎯 COMPLETE MANUFACTURING EXAMPLE:
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
                "help": "💡 Common issues: Check property names, ensure distributions are strings, verify probabilities sum to 1.0"
            }
            
            # Add schema examples if validation failed
            if any("Schema validation error" in error for error in errors):
                error_response["schema_help"] = "📋 Use the patterns shown in the tool description above for correct formatting"
            
            return error_response
        
        # Import and run unified simulation (will be created in Phase 2)
        from DES.unified_simulator import UnifiedSimulationModel
        
        model = UnifiedSimulationModel(normalized_config)
        return model.run()
        
    except ImportError:
        # Fallback to old system during transition
        from DES.des_utils import run_simulation
        return run_simulation(config)
        
    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}

@mcp.tool()
def simulate_sd_model(model: str, parameters: dict = None, 
                     start: int = None, stop: int = None, step: int = None) -> dict:
    """
    Run a System Dynamics model simulation using PySD.
    
    This tool runs a registered System Dynamics model with the provided parameters
    and returns the simulation results. Models must be registered in the SD/models/metadata.json file.
    
    Args:
        model: Name of the model to simulate (must match an entry in metadata.json)
        parameters: Dictionary of parameter name-value pairs to override default values
        start: Start time for simulation (defaults to model's metadata setting)
        stop: End time for simulation (defaults to model's metadata setting)
        step: Time step for simulation (defaults to model's metadata setting)
    
    Returns:
        A dictionary containing simulation results with time series data for each model variable
        
        If an error occurs, returns: {"error": "Error message"}
    """
    try:
        # Run simulation with provided parameters
        result = run_model_simulation({
            "model": model,
            "parameters": parameters or {},
            "start": start,
            "stop": stop,
            "step": step
        })
        
        # Convert to a dictionary that's serializable
        return json.loads(result.to_json())
    except Exception as e:
        return {"error": f"SD simulation error: {str(e)}"}

@mcp.tool()
def list_sd_models() -> dict:
    """
    List all available System Dynamics models with their descriptions.
    
    Returns:
        A dictionary mapping model names to their descriptions, or
        {"error": "Error message"} if an error occurs
    """
    try:
        return get_model_list()
    except Exception as e:
        return {"error": f"Error listing SD models: {str(e)}"}

@mcp.tool()
def get_sd_model_info(model_name: str) -> dict:
    """
    Get detailed information about a specific System Dynamics model.
    
    This tool returns metadata about a registered model, including its
    available parameters, outputs, and time settings.
    
    Args:
        model_name: Name of the model to retrieve information for
    
    Returns:
        A dictionary containing model metadata, or
        {"error": "Error message"} if the model is not found or an error occurs
    """
    try:
        model_info = get_model_details(model_name)
        if not model_info:
            return {"error": f"Model not found: {model_name}"}
        return model_info
    except Exception as e:
        return {"error": f"Error retrieving model info: {str(e)}"}

# Import new model builder infrastructure
from common.multi_schema_validator import MultiSchemaValidator
from common.model_state_manager import model_state_manager
from common.schema_registry import schema_registry

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
    
    🎯 VALIDATION MODES:
    - "partial": Validate only provided sections (default for iterative development)
    - "strict": Full schema compliance required (use before simulation execution)
    - "structure": Check structure without business rules (quick structural check)
    
    🔍 SCHEMA AUTO-DETECTION:
    The tool automatically detects schema type from model structure:
    - DES: Looks for entity_types, resources, processing_rules
    - SD: Looks for stocks, flows, variables (future)
    - Explicit: Use "schema_type": "DES" in model for explicit declaration
    
    📊 RESPONSE INCLUDES:
    - Detailed validation errors with quick fixes
    - Missing required sections with examples
    - Completeness percentage (0.0 to 1.0)
    - Actionable suggestions for improvement
    - Prioritized next steps for development
    
    🛠️ LLM-OPTIMIZED ERROR MESSAGES:
    Each error includes:
    - Exact path to problematic field
    - Clear explanation of the issue
    - Quick fix suggestion
    - Correct example for reference
    - Schema reference for deeper understanding
    
    💡 COMMON USAGE PATTERNS:
    
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
    
    🏷️ HYBRID NAMING SYSTEM:
    - User-provided names have priority: save_model(model, "hospital_triage")
    - Auto-generated names when none provided: "DES_healthcare_20250118_143022"
    - Conflict resolution: Automatic versioning (hospital_triage_v2, hospital_triage_v3)
    - Domain detection: Analyzes model content for intelligent naming
    
    🏥 DOMAIN AUTO-DETECTION:
    The system detects domains from model content for better auto-naming:
    - Healthcare: hospital, patient, doctor, triage, emergency
    - Manufacturing: production, assembly, quality, inspection
    - Service: customer, restaurant, call_center, checkout
    - Transportation: airport, passenger, logistics, delivery
    - Finance: bank, transaction, account, investment
    
    📝 METADATA TRACKING:
    - Creation and modification timestamps
    - User notes and descriptions
    - Tags for categorization and search
    - Schema type auto-detection
    - Validation status caching
    - Completeness percentage
    
    🔄 CONVERSATION CONTINUITY:
    Saved models persist across conversation sessions, enabling:
    - Resume development in new conversations
    - Share models between team members
    - Version tracking and comparison
    - Export for external use
    
    💡 USAGE PATTERNS:
    
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
    
    🔍 TWO OPERATION MODES:
    
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
    
    🏷️ FILTERING OPTIONS:
    - schema_type: Filter by "DES", "SD", etc.
    - tags: Filter by any matching tags
    - Combined filters: Use both for precise selection
    
    📊 MODEL METADATA INCLUDED:
    - Schema type and validation status
    - Creation and modification dates
    - User notes and tags
    - Completeness percentage
    - Domain classification
    
    💡 USAGE PATTERNS:
    
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
    
    🔄 CONVERSATION FLOW:
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
    
    📋 EXPORT FORMATS:
    - "pretty": Human-readable with proper indentation (default)
    - "compact": Minimized JSON for token efficiency
    - "conversation": Includes template text for easy pasting
    
    🔄 CONVERSATION CONTINUITY:
    The exported JSON can be used to:
    - Continue development in new conversation sessions
    - Share models with team members
    - Create backups of work-in-progress
    - Transfer models between different AI assistants
    
    📊 INCLUDES:
    - Complete model JSON in specified format
    - Character and estimated token counts
    - Copy-paste ready formatting
    - Optional metadata inclusion
    - Conversation template for easy use
    
    💡 USAGE PATTERNS:
    
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
    
    🎯 CONVERSATION TEMPLATE:
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

if __name__ == "__main__":
    mcp.run(transport='stdio')
