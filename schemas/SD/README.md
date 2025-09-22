# System Dynamics Schema Documentation

This directory contains JSON Schema definitions for System Dynamics models used by the Text2Sim MCP Server.

## Schema Files

### abstract_model_v2.json

The primary JSON Schema for PySD-compatible System Dynamics models. This schema defines the structure and validation rules for the `abstractModel` format used throughout the Text2Sim MCP Server.

**Schema Version**: 2.0
**JSON Schema Draft**: 2020-12
**Compatibility**: PySD 3.12.0+

## Schema Structure Overview

The schema enforces the following hierarchical structure:

```
abstractModel
├── originalPath (string)
└── sections (array)
    └── section
        ├── name (string)
        ├── type (string)
        ├── path (string)
        ├── params (array)
        ├── returns (array)
        ├── subscripts (array)
        ├── constraints (array)
        ├── testInputs (array)
        ├── split (boolean)
        ├── viewsDict (object)
        └── elements (array)
            └── element
                ├── name (string)
                ├── components (array)
                │   └── component
                │       ├── type (Stock|Flow|Auxiliary)
                │       ├── subtype (string)
                │       ├── subscripts (array)
                │       └── ast (object)
                │           ├── syntaxType (string)
                │           ├── reference (string)
                │           ├── flow (object, for stocks)
                │           └── initial (object, for stocks)
                ├── units (string)
                ├── limits (array)
                └── documentation (string)
```

## Component Types

### Stock Components
Represent accumulation variables that integrate flows over time.

**Required AST Structure**:
- `syntaxType`: "IntegStructure"
- `flow`: Reference to flow expression
- `initial`: Reference to initial value

### Flow Components
Represent rate variables that change stock values.

**Required AST Structure**:
- `syntaxType`: "ReferenceStructure"
- `reference`: Mathematical expression

### Auxiliary Components
Represent algebraic variables computed from other variables.

**Required AST Structure**:
- `syntaxType`: "ReferenceStructure"
- `reference`: Mathematical expression or constant value

## Validation Rules

### Structural Validation
- Root object must contain `abstractModel` property
- At least one section is required in the `sections` array
- Each section must have a `name` and `elements` array
- Elements must have unique names within their section

### Component Validation
- Each element must have at least one component
- Component `type` must be one of: "Stock", "Flow", "Auxiliary"
- Stock components require both `flow` and `initial` in AST
- Flow and Auxiliary components require `reference` in AST

### Business Rules
- Variable names in expressions must reference existing elements
- Circular dependencies are detected and prevented
- Mathematical expressions are validated for syntax correctness

## Usage in Text2Sim MCP Server

### Schema Detection
Models are automatically identified as System Dynamics when they contain the `abstractModel` root property.

### Validation Process
1. **Structural Validation**: JSON Schema compliance check
2. **Semantic Validation**: PySD-specific business rule validation
3. **Expression Validation**: Mathematical expression syntax checking
4. **Dependency Analysis**: Variable reference validation

### Integration Points

**Schema Registry** (`model_builder/schema_registry.py`)
```python
sd_schema_path = project_root / "schemas" / "SD" / "abstract_model_v2.json"
```

**Multi-Schema Validator** (`model_builder/multi_schema_validator.py`)
- Validates models against this schema
- Provides detailed error messages with correction suggestions
- Calculates model completeness percentages

**MCP Tools**
- `validate_model`: Uses schema for SD model validation
- `simulate_sd`: Expects input conforming to this schema
- `get_schema_help`: Provides documentation based on schema structure

## Example Usage

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

### Validation
```python
from model_builder.multi_schema_validator import MultiSchemaValidator

validator = MultiSchemaValidator()
result = validator.validate_model(model_data)

if result.valid:
    print(f"Model is valid (completeness: {result.completeness})")
else:
    for error in result.errors:
        print(f"Error at {error.path}: {error.message}")
```

## Development Guidelines

### Schema Modifications
When updating the schema:

1. **Version Management**: Increment schema version for breaking changes
2. **Backward Compatibility**: Maintain compatibility with existing models when possible
3. **Documentation Updates**: Update this README and integration documentation
4. **Testing**: Validate against existing model templates and examples

### Model Development
When creating models that conform to this schema:

1. **Structure**: Always wrap content in `abstractModel` container
2. **Sections**: Use single `__main__` section for standard models
3. **Elements**: Create one element per System Dynamics variable
4. **Components**: Use appropriate component types (Stock/Flow/Auxiliary)
5. **Documentation**: Include units and descriptions for all elements

### Error Handling
The schema provides detailed validation errors including:

- **Path Information**: Exact location of validation failures
- **Error Context**: Current value and expected format
- **Quick Fixes**: Actionable suggestions for correction
- **Examples**: Correct format demonstrations

## Technical Specifications

### File Format
- **Format**: JSON Schema Draft 2020-12
- **Encoding**: UTF-8
- **Size**: ~26KB
- **Definitions**: 90+ schema definitions for comprehensive validation

### Performance Characteristics
- **Validation Time**: < 50ms for typical models
- **Memory Usage**: < 1MB for schema loading
- **Scalability**: Supports models with 100+ elements efficiently

### Dependencies
- **JSON Schema**: Draft 2020-12 compliance
- **PySD Integration**: Compatible with PySD 3.12.0+
- **Python Version**: Requires Python 3.9+ (PySD requirement)

## Maintenance

### Regular Tasks
- **Schema Validation**: Verify schema correctness with JSON Schema validators
- **Example Testing**: Validate all example models against current schema
- **Documentation Sync**: Keep README aligned with schema changes
- **Performance Monitoring**: Track validation performance metrics

### Update Process
1. Create schema modifications in development branch
2. Update validation tests and example models
3. Run comprehensive test suite including integration tests
4. Update documentation and version numbers
5. Deploy through standard release process

For technical support or schema-related questions, refer to the main project documentation or create an issue in the project repository.