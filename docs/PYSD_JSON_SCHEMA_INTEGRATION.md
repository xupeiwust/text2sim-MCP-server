# PySD-compatible JSON Schema Integration

## Overview

The Text2Sim MCP Server implements direct integration with a PySD-compatible JSON format through the `abstract_model_v2.json` schema located at `schemas/SD/abstract_model_v2.json`. This integration provides System Dynamics simulation capabilities through PySD's established Python library ecosystem.

## Architecture

### Core Components

The integration consists of three primary components:

1. **Schema Registry**: Manages PySD-compatible JSON schema detection and validation
2. **SD Integration Module**: Handles PySD library interface and simulation execution
3. **MCP Tools**: Exposes PySD functionality through Model Context Protocol interface

### Data Flow

```
Conversation → JSON Input → Schema Validation → PySD Integration → Simulation Engine → Results
```

The system processes PySD-compatible JSON directly without format conversion or intermediate representation.

## Schema Structure

### Root Container

All System Dynamics models must conform to the following structure:

```json
{
  "abstractModel": {
    "originalPath": "string",
    "sections": []
  }
}
```

### Section Definition

Each model contains one or more sections, typically a single `__main__` section:

```json
{
  "name": "__main__",
  "type": "main",
  "path": "/",
  "params": [],
  "returns": [],
  "subscripts": [],
  "constraints": [],
  "testInputs": [],
  "split": false,
  "viewsDict": {},
  "elements": []
}
```

### Element Structure

Elements represent individual System Dynamics variables:

```json
{
  "name": "Variable_Name",
  "components": [
    {
      "type": "Stock|Flow|Auxiliary",
      "subtype": "Normal",
      "subscripts": [[], []],
      "ast": {
        "syntaxType": "IntegStructure|ReferenceStructure",
        "reference": "mathematical_expression"
      }
    }
  ],
  "units": "unit_string",
  "limits": [null, null],
  "documentation": "variable_description"
}
```

### Component Types

#### Stock Components

Accumulation variables that integrate flows over time:

```json
{
  "type": "Stock",
  "subtype": "Normal",
  "subscripts": [[], []],
  "ast": {
    "syntaxType": "IntegStructure",
    "flow": {
      "syntaxType": "ReferenceStructure",
      "reference": "flow_expression"
    },
    "initial": {
      "syntaxType": "ReferenceStructure",
      "reference": "initial_value"
    }
  }
}
```

#### Flow Components

Rate variables that change stock values:

```json
{
  "type": "Flow",
  "subtype": "Normal",
  "subscripts": [[], []],
  "ast": {
    "syntaxType": "ReferenceStructure",
    "reference": "mathematical_expression"
  }
}
```

#### Auxiliary Components

Algebraic variables computed from other variables:

```json
{
  "type": "Auxiliary",
  "subtype": "Normal",
  "subscripts": [[], []],
  "ast": {
    "syntaxType": "ReferenceStructure",
    "reference": "mathematical_expression"
  }
}
```

## Implementation Details

### Schema Detection

The system identifies System Dynamics models through the presence of the `abstractModel` key at the root level. Detection logic is implemented in `model_builder/schema_registry.py`:

```python
indicators=["abstractModel"]
```

### Validation Process

Validation occurs in two phases:

1. **Structural Validation**: Verifies JSON schema compliance
2. **Semantic Validation**: Validates PySD-specific business rules through `PySDJSONIntegration`

### Simulation Execution

The `simulate_sd` MCP tool processes models through the following sequence:

1. Extract time configuration parameters
2. Pass JSON directly to `PySDJSONIntegration.simulate_json_model()`
3. Return structured results with time series data and metadata

## MCP Tool Interface

### simulate_sd

Executes System Dynamics simulation using PySD engine.

**Parameters:**
- `config`: PySD-compatible JSON model
- `parameters`: Optional parameter overrides
- `time_settings`: Simulation time configuration

**Returns:**
- `success`: Boolean execution status
- `results`: Time series simulation data
- `model_info`: Model metadata and variable information
- `metadata`: Additional simulation metadata
- `error_message`: Error details if simulation fails

### validate_model

Validates System Dynamics model structure and semantics.

**Parameters:**
- `model`: PySD-compatible JSON model
- `schema_type`: Optional type override (auto-detected for SD)
- `validation_mode`: Validation strictness level

**Returns:**
- `valid`: Boolean validation status
- `schema_type`: Detected or specified schema type
- `completeness`: Model completeness percentage
- `errors`: Detailed validation errors
- `suggestions`: Improvement recommendations

### get_sd_model_info

Analyzes System Dynamics model without simulation execution.

**Parameters:**
- `config`: PySD-compatible JSON model

**Returns:**
- Model structure analysis
- Complexity metrics
- Variable information
- Validation status

## Error Handling

### Validation Errors

The system provides structured error messages for common issues:

- Missing `abstractModel` container
- Invalid section structure
- Malformed element definitions
- Incorrect AST syntax

### Simulation Errors

Runtime errors are categorized as:

- `SDValidationError`: Schema validation failures
- `SDModelBuildError`: Model construction errors
- `SDSimulationError`: Simulation execution errors

## Time Configuration

Time settings can be specified in two ways:

1. **Parameter Override**: Via `time_settings` parameter in `simulate_sd`
2. **Embedded Configuration**: Within model JSON structure

Default values:
- `initial_time`: 0
- `final_time`: 100
- `time_step`: 1

## Example Implementation

### Basic Population Model

```json
{
  "abstractModel": {
    "originalPath": "population_growth.json",
    "sections": [{
      "name": "__main__",
      "type": "main",
      "path": "/",
      "params": [],
      "returns": [],
      "subscripts": [],
      "constraints": [],
      "testInputs": [],
      "split": false,
      "viewsDict": {},
      "elements": [
        {
          "name": "Population",
          "components": [{
            "type": "Stock",
            "subtype": "Normal",
            "subscripts": [[], []],
            "ast": {
              "syntaxType": "IntegStructure",
              "flow": {
                "syntaxType": "ReferenceStructure",
                "reference": "Birth_Rate"
              },
              "initial": {
                "syntaxType": "ReferenceStructure",
                "reference": "1000"
              }
            }
          }],
          "units": "people",
          "limits": [null, null],
          "documentation": "Population stock"
        },
        {
          "name": "Birth_Rate",
          "components": [{
            "type": "Flow",
            "subtype": "Normal",
            "subscripts": [[], []],
            "ast": {
              "syntaxType": "ReferenceStructure",
              "reference": "Population * Birth_Fraction"
            }
          }],
          "units": "people/year",
          "limits": [null, null],
          "documentation": "Birth rate flow"
        },
        {
          "name": "Birth_Fraction",
          "components": [{
            "type": "Auxiliary",
            "subtype": "Normal",
            "subscripts": [[], []],
            "ast": {
              "syntaxType": "ReferenceStructure",
              "reference": "0.05"
            }
          }],
          "units": "1/year",
          "limits": [null, null],
          "documentation": "Birth fraction constant"
        }
      ]
    }]
  }
}
```

### Execution

```python
result = simulate_sd(model, time_settings={
    "initial_time": 0,
    "final_time": 100,
    "time_step": 1
})
```

## Integration Points

### PySD Library Interface

The integration interfaces with PySD through:

- `SD/sd_integration.py`: Primary integration module
- `PySDJSONIntegration`: Class handling PySD library calls
- Direct JSON-to-PySD object mapping

### Schema Registry Integration

Schema detection and registration occurs through:

- `model_builder/schema_registry.py`: Schema type registration
- `model_builder/multi_schema_validator.py`: Validation coordination
- Automatic schema type detection based on JSON structure

### MCP Framework Integration

MCP tool exposure through:

- `@mcp.tool()` decorators on simulation functions
- FastMCP server framework integration
- Structured JSON request/response handling

## Development Guidelines

### Model Construction

1. Always wrap models in `abstractModel` container
2. Use single `__main__` section for standard models
3. Create one element per System Dynamics variable
4. Specify appropriate component types for each variable
5. Include units and documentation for all elements

### Validation

1. Validate models before simulation execution
2. Handle validation errors with structured responses
3. Provide actionable error messages with examples
4. Support both strict and partial validation modes

### Error Management

1. Catch and categorize PySD integration exceptions
2. Provide clear error messages without internal details
3. Include corrective suggestions in error responses
4. Maintain consistent error response format

## Performance Considerations

### Direct Processing

The system processes PySD-compatible JSON without conversion overhead, providing optimal performance for simulation execution.

### Caching

Validation results may be cached to avoid repeated validation of identical models during development iterations.

### Memory Management

Large models with extensive time series data should be processed with consideration for memory constraints in the MCP server environment.