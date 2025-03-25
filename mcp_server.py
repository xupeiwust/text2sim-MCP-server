from mcp.server.fastmcp import FastMCP
from des_simulator import SimulationModel
import random
import re  # Added for the regex parser

# Initialise the MCP server
mcp = FastMCP("text2sim-mcp-server")

def parse_distribution(dist_str):
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
    # Apply defaults
    sim_config = {
        "interarrival": config.get("interarrival", 2),
        "num_entities": config.get("num_entities", 100),
        "run_time": config.get("run_time", 120)
    }

    model = SimulationModel(sim_config)

    # Validate and add steps
    steps = config.get("steps", [])
    if not steps:
        return {"error": "No process steps defined. Please include a 'steps' list."}

    for step in steps:
        name = step.get("name")
        if not name:
            return {"error": "Each step must have a 'name' property"}
            
        capacity = step.get("capacity", 1)
        dist = step.get("distribution", "uniform(1, 3)")

        try:
            # Use the secure parser instead of eval()
            fn = parse_distribution(dist)
            model.add_step(name, capacity, fn)
        except Exception as e:
            return {"error": f"Error processing step '{name}': {str(e)}"}

    return model.run()

if __name__ == "__main__":
    mcp.run(transport='stdio')
