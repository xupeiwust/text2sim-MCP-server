# Discrete Event Simulation Module for the Text2Sim MCP Server

This module adds Discrete Event Simulation (DES) capabilities to the Text2Sim MCP Server, built using SimPy.

## Structure

- `simulator.py`: Contains the comprehensive SimulationModel and enhanced metrics collection
- `des_simulator.py`: Contains core simulation components (Entity, ProcessStep, MetricsCollector)
- `des_utils.py`: Utility functions for distribution parsing, configuration validation, and simulation execution
- `schema_validator.py`: JSON Schema validation and configuration normalization

## Module Components

### SimulationModel

The main simulation engine that handles all DES scenarios through schema-driven configuration:
- Multi-entity type support with priorities and attributes
- Advanced resource management (FIFO, Priority, Preemptive)
- Conditional routing and multi-step processing flows
- Comprehensive statistics collection with customizable metrics
- Built-in support for balking, reneging, and resource failures

### Entity Class

Represents the units moving through the simulation system. Entities can have custom attributes and track their own state throughout the process.

### Process Step Class (Legacy)

Encapsulates the logic for a single step in a process flow. Used by legacy components:
- Resource management with capacity constraints
- Processing time determined by probability distributions
- Wait time and throughput metrics collection

### Metrics Collector (Legacy)

Basic metrics collection for simple simulations:
- Wait times for each process step  
- Throughput counts  
- Automatic calculation of averages and counts

### Enhanced Metrics Collector

Advanced metrics collection used by SimulationModel:
- Configurable metric names and terminology
- Resource utilization tracking
- Wait time distributions and statistics
- Custom business metrics support

## Supported Distributions

Use these in the `distribution` field of any step:

| Format | Description | Example |
|--------|-------------|---------|
| `"uniform(min, max)"` | Uniform between `min` and `max` | `"uniform(1, 3)"` |
| `"normal(mean, std)"` or `"gauss(mean, std)"` | Normal/Gaussian distribution | `"normal(5, 2)"` |
| `"exp(mean)"` | Exponential distribution with mean | `"exp(4)"` |

All distributions are parsed using regular expressions for security. No unsafe code evaluation occurs.

## Configuration Schema

The simulation configuration follows this structure:

```json
{
  "interarrival": 3,
  "num_entities": 100,
  "run_time": 120,
  "steps": [
    {
      "name": "step_name",
      "capacity": 2,
      "distribution": "exp(4)",
      "description": "optional natural-language annotation"
    }
  ]
}
```

### Parameters

- `interarrival`: Average time between entity arrivals (default: 2)  
- `num_entities`: Total number of entities to generate (default: 100)  
- `run_time`: Total simulation runtime (default: 120)  
- `steps`: Array of process steps, each with:
  - `name`: Identifier for the step (required)  
  - `capacity`: Number of entities that can be processed simultaneously (default: 1)  
  - `distribution`: Processing time distribution as a string (default: `"uniform(1, 3)"`)  
  - `description`: Optional natural-language annotation  

## Returned Metrics

Each simulation returns a dictionary of performance metrics. The metric keys follow the pattern:

- `{step_name}_wait_time_avg`: Average wait time at this step  
- `{step_name}_completed_count`: Number of entities that completed this step

**Example output**:
```json
{
  "check_in_wait_time_avg": 2.1,
  "check_in_completed_count": 100,
  "boarding_wait_time_avg": 1.8,
  "boarding_completed_count": 100
}
```

---

## Prompting Guide

### Key Prompt Components

| Concept | What to Say |
|--------|--------------|
| **Process steps** | Use terms like *check-in*, *triage*, *screening* |
| **Capacities** | Mention staffing levels or number of stations |
| **Process durations** | Say things like *takes 5–10 minutes*, *around 6 minutes on average* |
| **Arrival rate** | Use phrases like *one every 2 minutes*, *roughly every 5 minutes* |
| **Simulation length** | *Simulate 12 hours*, *simulate 300 patients* |

---

### Prompt Example

> *“Simulate a small hospital with triage, diagnosis, and treatment. Triage takes 3–5 minutes, diagnosis around 10 minutes, and treatment about 20. There are two triage nurses, three doctors, and one treatment bed. Patients arrive every 6 minutes. Simulate 8 hours or 80 patients.”*

Will generate:
```json
{
  "interarrival": 6,
  "num_entities": 80,
  "run_time": 480,
  "steps": [
    {
      "name": "triage",
      "capacity": 2,
      "distribution": "uniform(3, 5)",
      "description": "Initial nurse triage"
    },
    {
      "name": "diagnosis",
      "capacity": 3,
      "distribution": "normal(10, 2)",
      "description": "Doctor diagnosis process"
    },
    {
      "name": "treatment",
      "capacity": 1,
      "distribution": "normal(20, 5)",
      "description": "Patient treatment"
    }
  ]
}
```

---

## Example

### Prompt

> *“Simulate passenger processing in a small airport with check-in, security screening, and boarding. Assume moderate staffing and that passengers arrive roughly every 3 minutes. Simulate 16 hours and 320 passengers.”*

### Output

```json
{
  "config": {
    "steps": [
      {
        "name": "check_in",
        "capacity": 4,
        "description": "Passenger check-in process with multiple counters",
        "distribution": "normal(5, 2)"
      },
      {
        "name": "security_screening",
        "capacity": 3,
        "description": "Security checkpoint with multiple lanes",
        "distribution": "normal(8, 3)"
      },
      {
        "name": "boarding",
        "capacity": 2,
        "description": "Boarding gate processing",
        "distribution": "normal(6, 2)"
      }
    ],
    "run_time": 960,
    "interarrival": 3,
    "num_entities": 320
  }
}
```

The Text2Sim Discrete-Event Simulation (DES) engine parses this configuration, executes the SimPy-based simulation, and returns performance metrics for interpretation.

---

## Security Considerations

- **No `eval()` usage**: Regular expression-based parsing prevents arbitrary code execution  
- **Input Validation**: Distribution types and parameters are validated before execution  
- **Robust Error Handling**: Errors are reported cleanly without leaking internal state  

