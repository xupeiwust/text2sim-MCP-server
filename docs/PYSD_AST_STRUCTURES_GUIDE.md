# PySD AST Structures: Simple References vs Arithmetic Structures

## Overview

PySD's Abstract Syntax Tree (AST) system supports multiple approaches for defining mathematical expressions in System Dynamics models. Understanding the differences between simple references and structured arithmetic expressions is crucial for developing robust and maintainable models.

## Core Concepts

### Simple Reference Structure

Uses string-based mathematical expressions that PySD parses at runtime:

```json
{
  "syntaxType": "ReferenceStructure",
  "reference": "Birth_Rate - Death_Rate"
}
```

### Arithmetic Structure

Uses explicit mathematical structures with defined operators and arguments:

```json
{
  "syntaxType": "ArithmeticStructure",
  "operators": ["-"],
  "arguments": [
    {
      "syntaxType": "ReferenceStructure",
      "reference": "Birth_Rate"
    },
    {
      "syntaxType": "ReferenceStructure",
      "reference": "Death_Rate"
    }
  ]
}
```

## Functional Equivalence

### When Results Are Identical

For simple mathematical operations, both approaches produce identical simulation results:

**Population Stock Flow Example:**

Simple Reference:
```json
{
  "name": "Population",
  "components": [{
    "type": "Stock",
    "ast": {
      "syntaxType": "IntegStructure",
      "flow": {
        "syntaxType": "ReferenceStructure",
        "reference": "Birth_Rate - Death_Rate"
      },
      "initial": {
        "syntaxType": "ReferenceStructure",
        "reference": "1000"
      }
    }
  }]
}
```

Arithmetic Structure:
```json
{
  "name": "Population",
  "components": [{
    "type": "Stock",
    "ast": {
      "syntaxType": "IntegStructure",
      "flow": {
        "syntaxType": "ArithmeticStructure",
        "operators": ["-"],
        "arguments": [
          {"syntaxType": "ReferenceStructure", "reference": "Birth_Rate"},
          {"syntaxType": "ReferenceStructure", "reference": "Death_Rate"}
        ]
      },
      "initial": {
        "syntaxType": "ReferenceStructure",
        "reference": "1000"
      }
    }
  }]
}
```

Both produce identical simulation results when variables have the same values.

## Technical Differences

### Parsing and Execution

| Aspect | Simple Reference | Arithmetic Structure |
|--------|------------------|---------------------|
| **Runtime Processing** | String parsing required | Direct mathematical evaluation |
| **Expression Validation** | Delayed until execution | Immediate structural validation |
| **Error Detection** | Runtime parsing errors | Compile-time structure errors |
| **Performance** | Slight parsing overhead | Direct operation execution |

### Maintainability Characteristics

| Aspect | Simple Reference | Arithmetic Structure |
|--------|------------------|---------------------|
| **Readability** | Human-readable expressions | Explicit mathematical structure |
| **Programmatic Modification** | String manipulation required | Direct JSON structure editing |
| **Variable Renaming** | Manual string updates needed | Isolated reference updates |
| **Complexity Handling** | Can become unwieldy | Scales with nested structures |

## When Differences Matter

### Complex Mathematical Expressions

**Simple Reference Limitations:**
```json
{
  "syntaxType": "ReferenceStructure",
  "reference": "MIN(MAX(0, (Target - Current) / Time), Capacity * Efficiency)"
}
```

**Arithmetic Structure Benefits:**
```json
{
  "syntaxType": "ArithmeticStructure",
  "operators": ["MIN"],
  "arguments": [
    {
      "syntaxType": "ArithmeticStructure",
      "operators": ["MAX"],
      "arguments": [
        {"syntaxType": "ReferenceStructure", "reference": "0"},
        {
          "syntaxType": "ArithmeticStructure",
          "operators": ["/"],
          "arguments": [
            {
              "syntaxType": "ArithmeticStructure",
              "operators": ["-"],
              "arguments": [
                {"syntaxType": "ReferenceStructure", "reference": "Target"},
                {"syntaxType": "ReferenceStructure", "reference": "Current"}
              ]
            },
            {"syntaxType": "ReferenceStructure", "reference": "Time"}
          ]
        }
      ]
    },
    {
      "syntaxType": "ArithmeticStructure",
      "operators": ["*"],
      "arguments": [
        {"syntaxType": "ReferenceStructure", "reference": "Capacity"},
        {"syntaxType": "ReferenceStructure", "reference": "Efficiency"}
      ]
    }
  ]
}
```

### Error Handling Scenarios

**Simple Reference Issues:**
- Typos in variable names not caught until simulation
- Operator precedence ambiguities in complex expressions
- Parsing failures with special characters or formatting

**Arithmetic Structure Advantages:**
- Immediate validation of mathematical structure
- Clear operator precedence through explicit nesting
- Robust handling of variable reference changes

## Best Practice Guidelines

### Use Simple References When:

1. **Prototype Development**: Quick model iteration and testing
2. **Simple Expressions**: Basic arithmetic with 2-3 variables
3. **Human Readability Priority**: Models reviewed primarily by humans
4. **Legacy Compatibility**: Working with existing string-based models

### Use Arithmetic Structures When:

1. **Production Models**: Deployed systems requiring reliability
2. **Complex Mathematics**: Multi-level nested expressions
3. **Programmatic Generation**: Models built by code rather than manually
4. **Team Development**: Multiple developers modifying expressions
5. **Validation Requirements**: Strict mathematical verification needed

### Migration Strategy

**From Simple to Structured:**

1. **Identify Complex Expressions**: Target multi-operator expressions first
2. **Validate Equivalence**: Test that structured version produces identical results
3. **Incremental Conversion**: Convert one expression at a time
4. **Maintain Documentation**: Document mathematical intent during conversion

## Implementation Examples

### Basic Arithmetic Operations

**Addition:**
```json
// Simple
{"syntaxType": "ReferenceStructure", "reference": "A + B"}

// Structured
{
  "syntaxType": "ArithmeticStructure",
  "operators": ["+"],
  "arguments": [
    {"syntaxType": "ReferenceStructure", "reference": "A"},
    {"syntaxType": "ReferenceStructure", "reference": "B"}
  ]
}
```

**Multiplication with Constants:**
```json
// Simple
{"syntaxType": "ReferenceStructure", "reference": "Population * 0.05"}

// Structured
{
  "syntaxType": "ArithmeticStructure",
  "operators": ["*"],
  "arguments": [
    {"syntaxType": "ReferenceStructure", "reference": "Population"},
    {"syntaxType": "ReferenceStructure", "reference": "0.05"}
  ]
}
```

### Function Calls

**MIN/MAX Functions:**
```json
// Simple
{"syntaxType": "ReferenceStructure", "reference": "MAX(0, Value)"}

// Structured
{
  "syntaxType": "ArithmeticStructure",
  "operators": ["MAX"],
  "arguments": [
    {"syntaxType": "ReferenceStructure", "reference": "0"},
    {"syntaxType": "ReferenceStructure", "reference": "Value"}
  ]
}
```

## Development Workflow Recommendations

### Model Development Process

1. **Initial Development**: Use simple references for rapid prototyping
2. **Expression Validation**: Test mathematical correctness with simple format
3. **Complexity Assessment**: Identify expressions requiring structure
4. **Incremental Structuring**: Convert complex expressions to arithmetic structures
5. **Final Validation**: Verify identical results between formats

### Code Generation Guidelines

When programmatically generating PySD JSON models:

1. **Default to Arithmetic Structures**: More reliable for automated generation
2. **Validate Mathematical Correctness**: Ensure proper operator precedence
3. **Handle Variable References**: Maintain reference integrity during generation
4. **Test Expression Equivalence**: Verify against expected mathematical behavior

## Performance Considerations

### Runtime Characteristics

**Simple References:**
- String parsing overhead on first evaluation
- Potential repeated parsing in iterative simulations
- Memory allocation for parsed expression trees

**Arithmetic Structures:**
- Direct mathematical evaluation
- Pre-validated expression structure
- Consistent performance across simulation runs

### Memory Usage

**Simple References:**
- Compact JSON representation
- Runtime memory for parsed expressions
- String storage overhead

**Arithmetic Structures:**
- Larger JSON structures
- Direct mathematical object representation
- No parsing memory overhead

## Debugging and Troubleshooting

### Common Issues with Simple References

1. **Variable Name Typos**: Runtime errors during simulation
2. **Operator Precedence**: Unexpected mathematical results
3. **Special Characters**: Parsing failures with unusual symbols

### Common Issues with Arithmetic Structures

1. **Structural Complexity**: Difficult to read nested expressions
2. **JSON Verbosity**: Large file sizes for complex mathematics
3. **Manual Construction**: Error-prone when built by hand

### Debugging Strategies

1. **Expression Validation**: Test both formats produce identical results
2. **Incremental Complexity**: Build expressions step by step
3. **Mathematical Verification**: Validate against known analytical solutions
4. **Format Conversion**: Switch between formats to isolate issues

## Conclusion

Both simple references and arithmetic structures have their place in PySD model development. Simple references offer readability and rapid development for straightforward expressions, while arithmetic structures provide robustness and maintainability for complex mathematical relationships.

The choice between approaches should be guided by model complexity, development workflow, and maintenance requirements. For production systems and complex models, arithmetic structures are generally preferred for their reliability and explicit mathematical representation.

Understanding both approaches enables developers to choose the most appropriate method for their specific use case while maintaining compatibility with PySD's JSON schema requirements.