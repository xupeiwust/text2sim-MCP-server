import json
import pysd
from pathlib import Path

def load_model_metadata():
    """
    Load metadata for all registered System Dynamics models
    
    Returns:
        A dictionary containing model metadata
    """
    metadata_path = Path(__file__).parent / "models" / "metadata.json"
    try:
        with open(metadata_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create models directory if it doesn't exist
        models_dir = Path(__file__).parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Create an empty metadata file with a sample entry
        sample_metadata = {
            "penny_jar": {
                "path": "models/penny_jar.py",
                "description": "A simple SD model of penny distribution among jars",
                "parameters": {
                    "initial_pennies": {
                        "default": 100,
                        "description": "Initial number of pennies in the jar"
                    }
                },
                "outputs": ["jar1", "jar2"],
                "time": {
                    "start": 0,
                    "stop": 100,
                    "step": 1
                }
            }
        }
        
        with open(metadata_path, "w") as f:
            json.dump(sample_metadata, f, indent=2)
        
        return sample_metadata

def get_model_list():
    """
    Get a list of all available SD models with descriptions
    
    Returns:
        A dictionary mapping model names to descriptions
    """
    metadata = load_model_metadata()
    return {name: data.get("description", "No description") for name, data in metadata.items()}

def get_model_details(model_name):
    """
    Get detailed information about a specific model
    
    Args:
        model_name: Name of the model to retrieve
        
    Returns:
        A dictionary with model details or None if not found
    """
    metadata = load_model_metadata()
    return metadata.get(model_name)

def run_model_simulation(args):
    """
    Run a SD model simulation with specified parameters
    
    Args:
        args: Dictionary containing:
            model: Name of the model to run
            parameters: Dict of parameter values to set
            start: Start time for simulation
            stop: End time for simulation
            step: Time step size
            
    Returns:
        DataFrame with simulation results
        
    Raises:
        ValueError: If model not found or parameters are invalid
    """
    metadata = load_model_metadata()
    model_name = args["model"]
    
    if model_name not in metadata:
        raise ValueError(f"Unknown model: {model_name}")
        
    model_info = metadata[model_name]
    model_path = Path(__file__).parent / model_info["path"]
    
    if not model_path.exists():
        raise ValueError(f"Model file not found: {model_path}")
    
    # Load the model
    model = pysd.load(str(model_path))
    
    # Set parameters if provided
    parameters = args.get("parameters", {})
    if parameters:
        model.set_components(parameters)
    
    # Get simulation time settings, with fallbacks
    time_info = model_info.get("time", {})
    
    # Ensure we have valid integer values with proper fallbacks
    start = args.get("start") 
    if start is None:
        start = time_info.get("start")
    if start is None:  # If still None after checking metadata
        start = 0
        
    stop = args.get("stop")
    if stop is None:
        stop = time_info.get("stop")
    if stop is None:
        stop = 100
        
    step = args.get("step")
    if step is None:
        step = time_info.get("step")
    if step is None:
        step = 1
    
    # Run simulation with integer values
    return model.run(return_timestamps=range(int(start), int(stop) + 1, int(step))) 