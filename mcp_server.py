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

@mcp.tool()
def simulate_des(config: dict) -> dict:
    """
    Run a discrete-event simulation with comprehensive configuration using SimPy.
    
    This tool enables complex discrete-event simulations through a schema-driven
    configuration system optimized for SimPy's native capabilities. The configuration
    is validated against a comprehensive JSON schema to ensure correctness.
    
    Configuration Structure:
        run_time: Total simulation runtime (required)
        entity_types: Different types of entities with probabilities and values
        resources: System resources with capacity and type (fifo/priority/preemptive)
        processing_rules: Processing steps and service time distributions
        arrival_pattern: How entities arrive (mutually exclusive with num_entities)
        num_entities: Fixed number of entities (mutually exclusive with arrival_pattern)
        balking_rules: Rules for entities leaving without service
        reneging_rules: Rules for entities abandoning queues after waiting
        simple_routing: Basic conditional routing based on entity attributes
        basic_failures: Simple resource failure and repair cycles
        metrics: Custom names for simulation metrics
        statistics: Additional statistics collection settings
    
    Coffee Shop Example:
    {
      "run_time": 480,
      "entity_types": {
        "regular_customer": {"probability": 0.7, "value": {"min": 3, "max": 6}, "priority": 5},
        "vip_customer": {"probability": 0.3, "value": {"min": 5, "max": 12}, "priority": 2}
      },
      "resources": {
        "barista": {"capacity": 1, "resource_type": "priority"}
      },
      "processing_rules": {
        "steps": ["barista"],
        "barista": {"distribution": "normal(5, 1)"}
      },
      "balking_rules": {
        "overcrowding": {"type": "queue_length", "resource": "barista", "max_length": 5}
      },
      "arrival_pattern": {"distribution": "uniform(1, 5)"}
    }
    
    Hospital Example:
    {
      "run_time": 720,
      "entity_types": {
        "emergency": {"probability": 0.1, "priority": 1, "value": {"min": 2000, "max": 5000}},
        "urgent": {"probability": 0.3, "priority": 3, "value": {"min": 500, "max": 2000}},
        "routine": {"probability": 0.6, "priority": 7, "value": {"min": 100, "max": 500}}
      },
      "resources": {
        "triage": {"capacity": 2, "resource_type": "priority"},
        "treatment": {"capacity": 8, "resource_type": "preemptive"},
        "discharge": {"capacity": 1, "resource_type": "fifo"}
      },
      "processing_rules": {
        "steps": ["triage", "treatment", "discharge"],
        "triage": {"distribution": "uniform(5, 15)"},
        "treatment": {
          "conditional_distributions": {
            "emergency": "normal(60, 20)",
            "urgent": "normal(30, 10)",
            "routine": "normal(30, 10)"
          }
        },
        "discharge": {"distribution": "uniform(5, 10)"}
      },
      "arrival_pattern": {"distribution": "exp(2)"}
    }
    
    Supported Distributions:
        - "uniform(min, max)": Uniform distribution between min and max
        - "normal(mean, std)" or "gauss(mean, std)": Normal distribution  
        - "exp(mean)": Exponential distribution with given mean (not rate)
    
    Resource Types:
        - "fifo": Standard FIFO queue (SimPy Resource)
        - "priority": Priority queue without preemption (SimPy PriorityResource)
        - "preemptive": Priority queue with preemption (SimPy PreemptiveResource)
    
    Returns:
        Dictionary with simulation results including:
        - Entity arrival, served, balked, and reneged counts
        - Total value/revenue generated
        - Processing efficiency percentages
        - Average values per entity
        - Resource utilization statistics (if enabled)
        - Wait time statistics (if enabled)
        
        If validation fails, returns: {"error": "message", "details": [error_list]}
        If simulation fails, returns: {"error": "Simulation error: message"}
    """
    try:
        # Validate and normalize configuration
        validator = DESConfigValidator()
        normalized_config, errors = validator.validate_and_normalize(config)
        
        if errors:
            return {
                "error": "Configuration validation failed",
                "details": errors,
                "suggestion": "Please check the configuration format against the schema examples"
            }
        
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
