# System Dynamics Module for Text2Sim MCP server

This module provides System Dynamics simulation capabilities to the Text2Sim MCP server using PySD.

## Structure

- `models/`: Contains SD model files (PySD-compatible Python files)
- `models/metadata.json`: Defines metadata for all available SD models including parameters, outputs, and time settings
- `sd_utils.py`: Utility functions for loading and running SD models
- `model_converter.py`: Command-line tool for converting Vensim .mdl files to PySD .py files

## Adding New Models

To add a new SD model:

1. Convert your model to PySD format (from Vensim, XMILE, etc.)
2. Place the `.py` model file in the `models/` directory
3. Add an entry to `models/metadata.json` with:
   - `path`: Path to the model file relative to the SD directory
   - `description`: Brief description of the model
   - `parameters`: Dictionary of parameters that can be modified
   - `outputs`: List of key output variables
   - `time`: Default simulation time settings

Your model will automatically be available through the MCP server tools:
- `list_sd_models`: Shows all available models
- `simulate_sd_model`: Runs a simulation with your model

## Converting Vensim Models

The module includes a standalone conversion tool to simplify adding Vensim models:

```bash
# Show help message
python model_converter.py

# Basic conversion
python model_converter.py my_model.mdl

# Convert and automatically add to registry
python model_converter.py my_model.mdl --register

# Specify custom name and description
python model_converter.py my_model.mdl --register --name "climate_model" --description "Climate feedback model"

# Add metadata like author and version
python model_converter.py my_model.mdl --register --author "Jane Smith" --version "1.0.2"

# Add documentation links
python model_converter.py my_model.mdl --register --documentation "https://example.com/model-docs"

# Add reference modes (predefined scenarios)
python model_converter.py my_model.mdl --register --reference-modes "baseline,policy_a,policy_b"

# Specify output directory
python model_converter.py my_model.mdl --output-dir ./models
```

The converter will:
1. Convert the Vensim .mdl file to a PySD-compatible .py file
2. Automatically detect model parameters and outputs
3. Optionally add the model to the metadata registry with detailed information
4. Include any custom metadata fields you specify

### Running the Converter

The model converter is a standalone command-line tool that works independently from the MCP server. It handles:

- Parsing Vensim .mdl files into PySD compatible Python
- Extracting parameters and their default values
- Identifying model outputs
- Setting up metadata for use with the MCP server
- Error recovery and detailed reporting

After conversion, the tool provides a detailed summary of the model and instructions for using it with the MCP server.

## Extending Metadata

The metadata structure is flexible and can be extended with additional fields for your specific models.
You can add custom fields for additional metadata through the command line:

- `--author` or `-a`: Model creator information (e.g., "Jane Smith, University of Example")
- `--version` or `-v`: Model version number (e.g., "2.1.0")
- `--documentation` or `-D`: Links to model documentation (e.g., "https://example.com/docs")
- `--reference-modes`: Named scenario configurations (comma-separated list, e.g., "baseline,policy_a,policy_b")

These custom fields will be included in the model metadata and can be accessed through the MCP server's `get_sd_model_info` tool. 