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

# Legacy validation functions removed - now using JSON Schema validation

def run_simulation(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run unified DES simulation with schema validation.
    
    This function uses the new schema-driven unified simulation model that
    handles all scenarios through comprehensive configuration validation.
    
    Args:
        config: A dictionary with simulation configuration
        
    Returns:
        Simulation results dictionary or error message
    """
    try:
        from DES.schema_validator import DESConfigValidator
        from DES.unified_simulator import UnifiedSimulationModel
        
        # Validate configuration
        validator = DESConfigValidator()
        normalized_config, errors = validator.validate_and_normalize(config)
        
        if errors:
            return {
                "error": "Configuration validation failed", 
                "details": errors,
                "suggestion": "Please check the configuration format against the schema examples"
            }
        
        # Run unified simulation
        model = UnifiedSimulationModel(normalized_config)
        return model.run()
        
    except ImportError:
        # Fallback for missing dependencies during transition
        return {"error": "Unified simulation model not available. Please check dependencies."}
        
    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}

# Legacy functions removed - now using unified schema-driven approach 