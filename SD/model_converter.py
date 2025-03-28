#!/usr/bin/env python3
"""
Model Converter for System Dynamics

This script converts Vensim .mdl files to PySD-compatible .py files
and can optionally add them to the model registry.

Usage:
    python model_converter.py my_model.mdl [options]
    
Options:
    --output-dir, -o      Directory to save the Python file
    --register, -r        Add the model to the registry
    --name, -n            Name to use in the registry (default: file name)
    --description, -d     Model description for the registry
    --author, -a          Author information for the model
    --version, -v         Version information for the model
    --documentation, -D   Documentation links for the model
    --reference-modes     Reference scenarios for the model (comma-separated list)
    --help, -h            Show this help message
    
Example:
    python model_converter.py models/teacup.mdl --register --name teacup_model
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
import pysd
import re
import shutil
from typing import List, Dict, Any, Optional, Set


def convert_mdl_to_py(mdl_file: str, output_dir: Optional[str] = None) -> str:
    """
    Converts a Vensim .mdl file to a PySD-compatible .py file.
    
    Args:
        mdl_file: Path to the .mdl file
        output_dir: Directory to save the .py file (defaults to same directory as .mdl)
        
    Returns:
        Path to the generated .py file
        
    Raises:
        FileNotFoundError: If the mdl_file doesn't exist
        ValueError: If conversion fails
    """
    mdl_path = Path(mdl_file)
    
    if not mdl_path.exists():
        raise FileNotFoundError(f"Model file not found: {mdl_file}")
        
    if output_dir is None:
        output_dir = mdl_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
    
    # Convert model
    try:
        model = pysd.read_vensim(str(mdl_path))
        py_filename = mdl_path.stem + '.py'
        output_path = output_dir / py_filename
        
        # PySD already writes the file during read_vensim
        # Copy it to the desired location if needed
        source_path = mdl_path.parent / py_filename
        if source_path != output_path and source_path.exists():
            shutil.copy(source_path, output_path)
            
        return str(output_path)
    except Exception as e:
        raise ValueError(f"Error converting model: {str(e)}")


def get_model_variables(py_file: str) -> Dict[str, Set[str]]:
    """
    Extracts variables from a PySD model file.
    
    Args:
        py_file: Path to the .py file
        
    Returns:
        Dictionary with 'parameters' and 'outputs' keys containing sets of variable names
    """
    try:
        model = pysd.load(py_file)
        
        # Get all variables
        all_vars = set(model.components.keys())
        
        # Filter out internal variables
        filtered_vars = {v for v in all_vars if not v.startswith('_') and 
                        v not in ('time', 'initial_time', 'final_time', 'time_step', 'saveper')}
        
        # Simple heuristic: outputs are typically calculated from other variables
        # Parameters are typically not calculated from other variables
        parameters = set()
        outputs = set()
        
        with open(py_file, 'r') as f:
            content = f.read()
        
        for var in filtered_vars:
            # Look for implementation pattern
            pattern = rf'def {re.escape(var)}\(\):'
            match = re.search(pattern, content)
            if match:
                # Find next non-comment, non-docstring line
                pos = match.end()
                lines = content[pos:].split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('"""'):
                        # If it directly returns a value, it's likely a parameter
                        if line.startswith('return ') and not any(v in line for v in filtered_vars):
                            parameters.add(var)
                        else:
                            outputs.add(var)
                        break
        
        # Variables not explicitly categorized go to outputs
        remaining = filtered_vars - parameters - outputs
        outputs.update(remaining)
        
        return {
            'parameters': parameters,
            'outputs': outputs
        }
    except Exception as e:
        print(f"Warning: Error analyzing model variables: {str(e)}")
        return {'parameters': set(), 'outputs': set()}


def add_to_registry(py_file: str, model_name: Optional[str] = None, 
                   description: Optional[str] = None, author: Optional[str] = None,
                   version: Optional[str] = None, documentation: Optional[str] = None,
                   reference_modes: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Adds a converted model to the metadata registry.
    
    Args:
        py_file: Path to the .py file
        model_name: Name to use in the registry (defaults to file name without extension)
        description: Model description (defaults to "Converted from {original_file}")
        author: Author information for the model
        version: Version information for the model
        documentation: Documentation links for the model
        reference_modes: List of reference scenario descriptions
        
    Returns:
        A dictionary with model_name as key and metadata as value
    """
    py_path = Path(py_file)
    
    if not py_path.exists():
        raise FileNotFoundError(f"Python model file not found: {py_file}")
    
    # Use file name as model name if not provided
    if model_name is None:
        model_name = py_path.stem
    
    # Generate default description if not provided
    if description is None:
        description = f"Model converted from {py_path.stem}.mdl"
    
    # Get SD directory path
    sd_dir = Path(__file__).parent.absolute()
    
    # Determine relative path from SD directory to the model file
    try:
        rel_path = py_path.relative_to(sd_dir)
    except ValueError:
        # If the file is not in SD directory or subdirectory, copy it to models folder
        models_dir = sd_dir / "models"
        models_dir.mkdir(exist_ok=True)
        dest_path = models_dir / py_path.name
        shutil.copy(py_path, dest_path)
        rel_path = Path("models") / py_path.name
    
    # Extract model variables
    print("Analyzing model variables...")
    var_info = get_model_variables(py_file)
    
    # Create metadata entry
    metadata_entry = {
        "path": str(rel_path),
        "description": description,
        "parameters": {},
        "outputs": list(var_info['outputs']),
        "time": {
            "start": 0,
            "stop": 100,
            "step": 1
        }
    }
    
    # Add custom metadata fields if provided
    if author:
        metadata_entry["author"] = author
    
    if version:
        metadata_entry["version"] = version
    
    if documentation:
        metadata_entry["documentation"] = documentation
    
    if reference_modes:
        if isinstance(reference_modes, str):
            # Convert comma-separated string to dictionary with descriptions
            modes_dict = {}
            for mode in reference_modes.split(','):
                mode = mode.strip()
                if mode:
                    modes_dict[mode] = f"{mode} scenario"
            metadata_entry["reference_modes"] = modes_dict
        elif isinstance(reference_modes, dict):
            metadata_entry["reference_modes"] = reference_modes
        else:
            # Assume it's a list
            metadata_entry["reference_modes"] = {mode: f"{mode} scenario" for mode in reference_modes}
    
    # Add parameter defaults
    print("Extracting parameter defaults...")
    try:
        model = pysd.load(py_file)
        for param in var_info['parameters']:
            try:
                default_value = model.components[param]()
                metadata_entry["parameters"][param] = {
                    "default": default_value,
                    "description": f"Parameter {param}"
                }
            except Exception as e:
                print(f"  Warning: Couldn't get default for parameter '{param}': {str(e)}")
                # Add the parameter without a default value
                metadata_entry["parameters"][param] = {
                    "default": 0,  # Use 0 as fallback default
                    "description": f"Parameter {param} (default unknown)"
                }
    except Exception as e:
        print(f"  Warning: Error loading model: {str(e)}")
        # Add parameters without default values
        for param in var_info['parameters']:
            metadata_entry["parameters"][param] = {
                "default": 0,
                "description": f"Parameter {param} (default unknown)"
            }
    
    # Load existing metadata
    metadata_path = sd_dir / "models" / "metadata.json"
    
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = {}
    
    # Add or update model entry
    metadata[model_name] = metadata_entry
    
    # Save updated metadata
    print(f"Saving metadata to {metadata_path}...")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Return the model entry with its name as the key
    return {model_name: metadata_entry}


def print_summary(model_name: str, metadata: dict, py_file: str):
    """Print a summary of the converted model"""
    parameters = metadata.get("parameters", {})
    outputs = metadata.get("outputs", [])
    
    print("\n" + "="*70)
    print(f"MODEL SUMMARY: {model_name}")
    print("="*70)
    print(f"Description: {metadata.get('description', 'No description')}")
    print(f"File: {py_file}")
    print(f"Registry path: {metadata.get('path', 'Unknown')}")
    
    # Print custom metadata if available
    if "author" in metadata:
        print(f"Author: {metadata['author']}")
    
    if "version" in metadata:
        print(f"Version: {metadata['version']}")
    
    if "documentation" in metadata:
        print(f"Documentation: {metadata['documentation']}")
    
    if "reference_modes" in metadata:
        print("\nReference Modes:")
        for mode, desc in metadata["reference_modes"].items():
            print(f"  - {mode}: {desc}")
    
    print(f"\nParameters ({len(parameters)}):")
    if parameters:
        for name, info in parameters.items():
            default = info.get("default", "Unknown")
            description = info.get("description", "No description")
            print(f"  - {name}: {description} (default: {default})")
    else:
        print("  No parameters detected")
        
    print(f"\nOutputs ({len(outputs)}):")
    if outputs:
        for output in outputs[:10]:  # Show first 10 outputs
            print(f"  - {output}")
        if len(outputs) > 10:
            print(f"  ... and {len(outputs) - 10} more")
    else:
        print("  No outputs detected")
        
    print(f"\nTime settings:")
    time_settings = metadata.get("time", {})
    print(f"  Start: {time_settings.get('start', 0)}")
    print(f"  Stop: {time_settings.get('stop', 100)}")
    print(f"  Step: {time_settings.get('step', 1)}")
    
    print("\nTo use this model with the MCP server:")
    print(f"  list_sd_models()")
    print(f"  get_sd_model_info(\"{model_name}\")")
    print(f"  simulate_sd_model(\"{model_name}\")")
    print("="*70)


def print_help():
    """Print help message"""
    print(__doc__)


def main():
    parser = argparse.ArgumentParser(
        description='Convert Vensim .mdl files to PySD .py files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python model_converter.py models/teacup.mdl
  python model_converter.py models/teacup.mdl --register
  python model_converter.py models/teacup.mdl --register --name custom_name
  python model_converter.py models/teacup.mdl --output-dir ./converted_models
  python model_converter.py models/teacup.mdl --register --author "John Doe" --version "1.0"
  ''')
    parser.add_argument('mdl_file', help='Path to the Vensim .mdl file', nargs='?')
    parser.add_argument('--output-dir', '-o', help='Directory to save the Python file (default: same as input)')
    parser.add_argument('--register', '-r', action='store_true', help='Add the model to the registry')
    parser.add_argument('--name', '-n', help='Name to use in the registry (default: file name)')
    parser.add_argument('--description', '-d', help='Model description for the registry')
    
    # Add custom metadata parameters
    parser.add_argument('--author', '-a', help='Author information for the model')
    parser.add_argument('--version', '-v', help='Version information for the model')
    parser.add_argument('--documentation', '-D', help='Documentation links for the model')
    parser.add_argument('--reference-modes', help='Reference scenarios for the model (comma-separated list)')
    
    # If no arguments are provided, print help and exit
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # If mdl_file is not provided, print error and exit
    if not args.mdl_file:
        print("Error: mdl_file is required")
        parser.print_help()
        return 1
    
    try:
        print(f"Converting {args.mdl_file}...")
        start_time = time.time()
        py_file = convert_mdl_to_py(args.mdl_file, args.output_dir)
        conversion_time = time.time() - start_time
        print(f"Successfully converted to {py_file} in {conversion_time:.2f} seconds")
        
        if args.register:
            print("Adding to model registry...")
            start_time = time.time()
            metadata_dict = add_to_registry(
                py_file, 
                model_name=args.name, 
                description=args.description,
                author=args.author,
                version=args.version,
                documentation=args.documentation,
                reference_modes=args.reference_modes.split(',') if args.reference_modes else None
            )
            register_time = time.time() - start_time
            
            model_name = list(metadata_dict.keys())[0]
            metadata = metadata_dict[model_name]
            
            print(f"Model added to registry as '{model_name}' in {register_time:.2f} seconds")
            print_summary(model_name, metadata, py_file)
        else:
            print("\nModel was converted but not added to the registry.")
            print("To add to registry, run with --register flag:")
            print(f"  python model_converter.py {args.mdl_file} --register")
        
        print("\nDone!")
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 