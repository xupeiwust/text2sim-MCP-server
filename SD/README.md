# System Dynamics Module for Text2Sim MCP server

This module provides System Dynamics simulation capabilities to the Text2Sim MCP server using PySD with JSON-based model building.

## Modern JSON-Based Approach

The SD integration now uses a modern, conversational approach where models are built through JSON configuration instead of pre-converted files:

- **JSON Model Building**: Create SD models through conversational JSON definition
- **Real-time Validation**: JSON Schema validation with detailed error reporting
- **Integrated Simulation**: Direct JSON-to-PySD conversion and simulation
- **Model Builder Integration**: Works seamlessly with the unified model builder tools

## Available MCP Tools

The following tools enable conversational SD modeling:

- `simulate_sd`: Create and simulate SD models from JSON configuration
- `validate_sd_model`: Validate SD model JSON against schema
- `convert_vensim_to_sd_json`: Convert Vensim .mdl files to JSON format
- `get_sd_model_info`: Analyze JSON model structure and complexity

## Creating SD Models

Instead of pre-converting models, you now create them conversationally:

## Example Usage

### 1. Simple Population Model
```json
{
  "abstractModel": {
    "originalPath": "population_growth.json",
    "sections": [
      {
        "name": "__main__",
        "type": "main",
        "elements": [
          {
            "name": "Population Dynamics",
            "components": [
              {
                "type": "Stock",
                "subtype": "Normal",
                "name": "population",
                "initial_value": 1000
              },
              {
                "type": "Flow",
                "subtype": "Normal",
                "name": "birth_rate",
                "equation": "population * 0.02"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 2. Converting Vensim Models
Use the `convert_vensim_to_sd_json` tool to convert existing .mdl files:
- Automatically converts Vensim syntax to JSON format
- Preserves model structure and relationships
- Ready for simulation with `simulate_sd`

### 3. Model Validation
Before simulation, validate your JSON structure:
- Real-time schema checking
- Detailed error messages with suggestions
- Component relationship validation

## Benefits of JSON Approach

- **Conversational**: Build models through natural language interaction
- **Iterative**: Modify and test models incrementally
- **Validated**: Immediate feedback on model structure
- **Portable**: JSON models work across platforms
- **Version Control**: Easy to track and share model changes
- **Integration**: Works seamlessly with model builder tools

## Migration from File-Based Models

If you have existing PySD models or Vensim files:
1. Use `convert_vensim_to_sd_json` for .mdl files
2. Manually convert PySD models to JSON format using the schema
3. Test converted models with `validate_sd_model`
4. Simulate with the new `simulate_sd` tool

The JSON approach provides much more flexibility and better integration with conversational AI tools. 
