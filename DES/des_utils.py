import random
import re
from typing import Callable, Dict, Any, Optional

def parse_distribution(dist_str: str) -> Callable[[], float]:
    """
    Safely parse a distribution string into a function that generates random values.
    
    Args:
        dist_str: A string like "uniform(2, 5)" or "normal(10, 2)"
        
    Returns:
        A function that returns random values from the specified distribution
        
    Raises:
        ValueError: If the format is invalid or the distribution is unsupported
    """
    pattern = r'(\w+)\(([^)]+)\)'
    match = re.match(pattern, dist_str.strip())
    
    if not match:
        raise ValueError(f"Invalid distribution format: {dist_str}")
        
    dist_name, args_str = match.groups()
    args = [float(x.strip()) for x in args_str.split(',')]
    
    if dist_name == "uniform":
        if len(args) != 2:
            raise ValueError("Uniform distribution requires exactly 2 parameters: min and max")
        return lambda: random.uniform(args[0], args[1])
    elif dist_name in ["gauss", "normal"]:
        if len(args) != 2:
            raise ValueError("Normal distribution requires exactly 2 parameters: mean and std dev")
        return lambda: max(0, random.gauss(args[0], args[1]))
    elif dist_name == "exp":
        if len(args) != 1:
            raise ValueError("Exponential distribution requires exactly 1 parameter: mean")
        return lambda: random.expovariate(1 / args[0])
    else:
        raise ValueError(f"Unsupported distribution: {dist_name}")

def validate_config(config: Dict[str, Any]) -> Optional[str]:
    """
    Validate a simulation configuration dictionary.
    
    Args:
        config: A dictionary with simulation configuration
        
    Returns:
        None if valid, error message string if invalid
    """
    # Check for required steps
    steps = config.get("steps", [])
    if not steps:
        return "No process steps defined. Please include a 'steps' list."
    
    # Validate each step
    for i, step in enumerate(steps):
        # Check for name
        name = step.get("name")
        if not name:
            return f"Step {i+1} is missing a 'name' property"
        
        # Validate distribution if provided
        if "distribution" in step:
            try:
                parse_distribution(step["distribution"])
            except ValueError as e:
                return f"Error in step '{name}' distribution: {str(e)}"
    
    return None

def prepare_simulation_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare and standardize a simulation configuration with defaults.
    
    Args:
        config: User-provided configuration dictionary
        
    Returns:
        Configuration with defaults applied
    """
    # Apply defaults
    return {
        "interarrival": config.get("interarrival", 2),
        "num_entities": config.get("num_entities", 100),
        "run_time": config.get("run_time", 120),
        "steps": config.get("steps", [])
    }

def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a discrete-event simulation based on the provided configuration.
    
    Args:
        config: A dictionary with simulation configuration
        
    Returns:
        Simulation results dictionary or error message
    """
    from DES.des_simulator import SimulationModel
    
    # Validate config
    error = validate_config(config)
    if error:
        return {"error": error}
    
    # Prepare config with defaults
    sim_config = prepare_simulation_config(config)
    
    # Create model
    model = SimulationModel(sim_config)
    
    # Add steps to the model
    for step in sim_config["steps"]:
        name = step["name"]
        capacity = step.get("capacity", 1)
        dist_str = step.get("distribution", "uniform(1, 3)")
        
        try:
            # Use the secure parser instead of eval()
            fn = parse_distribution(dist_str)
            model.add_step(name, capacity, fn)
        except Exception as e:
            return {"error": f"Error processing step '{name}': {str(e)}"}
    
    # Run the simulation and return results
    try:
        return model.run()
    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"} 