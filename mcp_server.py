from mcp.server.fastmcp import FastMCP, Context
from DES.des_simulator import SimulationModel
from DES.des_utils import parse_distribution, run_simulation
import random
import re  # Added for the regex parser
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
    Run a discrete-event simulation based on the provided configuration.
    
    This tool converts a flexible configuration structure into a SimPy-based
    discrete-event simulation model and executes it. It supports various
    probability distributions for process times and provides summary metrics.
    
    Args:
        config: A dictionary defining the simulation parameters:
            interarrival: Average time between entity arrivals (default: 2)
            num_entities: Total number of entities to generate (default: 100)
            run_time: Total simulation runtime (default: 120)
            steps: List of process steps, each with:
                name: Identifier for the step (required)
                capacity: Number of entities that can be processed simultaneously (default: 1)
                distribution: Processing time distribution as a string (default: "uniform(1, 3)")
                    Supported formats:
                    - "uniform(min, max)": Uniform distribution between min and max
                    - "normal(mean, std)" or "gauss(mean, std)": Normal distribution
                    - "exp(mean)": Exponential distribution with given mean
    
    Returns:
        A dictionary containing simulation metrics:
            {step_name}_{metric_type}_avg: Average value for numeric metrics
            {step_name}_{metric_type}_count: Count of occurrences
            
        Example metrics include:
            - step1_wait_time_avg: Average wait time for step1
            - step1_completed_count: Number of entities that completed step1
            
        If an error occurs, returns: {"error": "Error message"}
    """
    from DES.des_utils import run_simulation
    
    try:
        # Use the run_simulation function from des_utils
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
