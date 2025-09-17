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

if __name__ == "__main__":
    mcp.run(transport='stdio')
