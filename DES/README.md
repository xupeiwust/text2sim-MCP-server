# Discrete Event Simulation Module for the Text2Sim MCP Server

This module provides comprehensive Discrete Event Simulation (DES) capabilities for the Text2Sim MCP Server, built using SimPy. The engine supports complex multi-entity systems with advanced routing, resource management, and statistical analysis.

## Architecture Overview

The DES module follows a schema-driven architecture that provides professional-grade simulation capabilities:

- **Single Simulation Engine**: `SimulationModel` handles all DES scenarios
- **JSON Schema Validation**: Comprehensive configuration validation and normalization
- **Advanced Statistics**: Industry-standard metrics with confidence intervals
- **Multiple Replications**: Statistical analysis across multiple simulation runs
- **Professional Reporting**: Business-ready output formats

## File Structure

- `simulator.py`: Main simulation engine (`SimulationModel`) with enhanced metrics collection
- `des_simulator.py`: Core simulation components (Entity, legacy MetricsCollector, ProcessStep)
- `des_utils.py`: Utility functions for distribution parsing and simulation execution
- `schema_validator.py`: JSON Schema validation and configuration normalization
- `replication_analysis.py`: Statistical analysis engine for multiple simulation runs
g
## Core Components

### SimulationModel (Primary Engine)

The simulation engine that handles all DES scenarios:

**Key Features:**
- **Multi-entity types** with custom attributes, priorities, and value tracking
- **Advanced resource management** (FIFO, Priority, Preemptive queues)
- **Dynamic routing** with conditional logic and post-step routing
- **Comprehensive metrics** with warmup periods and confidence intervals
- **Professional statistics** including utilization, wait times, and throughput
- **Balking and reneging** support for realistic queue behavior

**Configuration-Driven:**
- JSON Schema validation ensures correct configurations
- Supports complex routing scenarios (hospital triage, manufacturing, services)
- Automatic normalization and error reporting

### Enhanced Metrics Collection

Professional-grade statistics collection:
- **Resource utilization** with proper capacity-adjusted calculations
- **Wait time analysis** with distributions and confidence intervals
- **Throughput metrics** with arrival/departure tracking
- **Custom business metrics** for domain-specific KPIs
- **Warmup period handling** to eliminate transient effects
- **Confidence metadata** with reliability scoring

### Entity Management

Sophisticated entity handling:
- **Custom attributes** for business logic and routing decisions
- **Priority systems** for realistic queue management  
- **Value tracking** for economic and business analysis
- **State management** throughout the simulation lifecycle

### Legacy Components (Minimal Use)

- **Entity Class**: Basic entity representation (used by both systems)
- **ProcessStep Class**: Legacy step-based processing (minimal usage)
- **MetricsCollector**: Basic metrics (superseded by Enhanced version)

## Supported Distributions

The simulation engine supports the following probability distributions for modeling arrival patterns and service times:

| Format | Description | Parameters | Example |
|--------|-------------|------------|---------|
| `"uniform(min, max)"` | Uniform distribution | min, max values | `"uniform(2, 10)"` |
| `"normal(mean, std)"` | Normal/Gaussian distribution | mean, standard deviation | `"normal(15, 5)"` |
| `"gauss(mean, std)"` | Alias for normal distribution | mean, standard deviation | `"gauss(10, 3)"` |
| `"exp(mean)"` | Exponential distribution | mean inter-arrival/service time | `"exp(2.5)"` |

**Important Notes:**
- **Exponential parameters**: `exp(x)` uses `x` as the mean time (not rate)
- **Security**: All distributions parsed via regex - no code evaluation
- **Validation**: Parameters validated against realistic ranges
- **Usage**: Common in arrival patterns (`exp`) and service times (`normal`, `uniform`)

## Modern Configuration Schema

The current DES engine uses a comprehensive JSON schema that supports advanced features:

```json
{
  "run_time": 480,
  "arrival_pattern": {
    "distribution": "exp(2.5)"
  },
  "entity_types": {
    "emergency_patient": {
      "probability": 0.2,
      "priority": 1,
      "value": {"min": 2000, "max": 5000},
      "attributes": {"severity": "high"}
    },
    "routine_patient": {
      "probability": 0.8, 
      "priority": 3,
      "value": {"min": 100, "max": 500},
      "attributes": {"severity": "low"}
    }
  },
  "resources": {
    "triage_nurse": {"capacity": 1, "resource_type": "priority"},
    "emergency_doctor": {"capacity": 2, "resource_type": "priority"},
    "routine_doctor": {"capacity": 1, "resource_type": "priority"}
  },
  "processing_rules": {
    "steps": ["triage_nurse"],
    "triage_nurse": {"distribution": "uniform(2, 10)"},
    "emergency_doctor": {"distribution": "normal(30, 10)"},
    "routine_doctor": {"distribution": "normal(15, 5)"}
  },
  "simple_routing": {
    "after_triage_nurse": {
      "conditions": [
        {"attribute": "priority", "operator": "<=", "value": 1, "destination": "emergency_doctor"}
      ],
      "default_destination": "routine_doctor"
    }
  },
  "statistics": {
    "collect_wait_times": true,
    "collect_utilization": true,
    "collect_queue_lengths": true,
    "warmup_period": 60
  }
}
```

### Key Configuration Sections

**Core Simulation:**
- `run_time`: Total simulation time units
- `arrival_pattern`: Entity generation pattern with distribution

**Entity Management:**
- `entity_types`: Multiple entity types with probabilities, priorities, values, and attributes
- Custom attributes enable sophisticated routing and business logic

**Resource Definition:**
- `resources`: Named resources with capacity and queue discipline (fifo, priority, preemptive)
- Supports realistic resource constraints and queue management

**Process Flow:**
- `processing_rules`: Defines processing steps and service time distributions
- `simple_routing`: Conditional routing based on entity attributes
- Dynamic routing enables complex workflows (triage → specialist assignment)

**Statistics Collection:**
- `statistics`: Configurable metrics collection with warmup periods
- Professional-grade statistical analysis with confidence intervals

## Professional Output Metrics

The modern engine returns comprehensive business metrics:

```json
{
  "entities_served_count": 127,
  "entities_arrived_count": 150,
  "total_value": 45230.50,
  "entities_served_processing_efficiency": 84.67,
  "average_value_per_entities": 356.14,
  "triage_nurse_utilization": 87.5,
  "emergency_doctor_utilization": 92.3,
  "routine_doctor_utilization": 78.1,
  "average_wait_time": 12.4,
  "max_wait_time": 45.2,
  "min_wait_time": 0.5,
  "_metadata": {
    "confidence_level": "high",
    "simulation_run_time": 480,
    "sample_size": 127,
    "reliability_score": 0.85,
    "warnings": []
  }
}
```

**Key Metric Categories:**
- **Throughput**: Entity counts, processing efficiency, arrival rates
- **Financial**: Total value processed, average value per entity
- **Resource Performance**: Utilization rates for each resource
- **Service Quality**: Wait times (average, min, max)
- **Statistical Confidence**: Reliability indicators and warnings

## Multiple Replications Analysis

The DES engine includes professional statistical analysis via the `run_multiple_simulations` MCP tool:

### Industry-Standard Statistical Output

```
SIMULATION REPLICATION ANALYSIS SUMMARY
==================================================
Total Replications: 10
Successful Runs: 10

Server Utilization:
  88.9% ± 6.5% (95% CI) [n=10]
  Std Dev: 4.06, CV: 4.57%
  Range: [85.1%, 93.9%]
  Relative Precision: ±7.3%
  Normality (Shapiro-Wilk): Normal (p=0.123)

Average Wait Time:
  26.9 ± 9.2 minutes (95% CI) [n=10]
  Std Dev: 5.77, CV: 21.51%
  Range: [21.4, 33.4]
  Relative Precision: ±34.2%
```

**Key Features:**
- **Confidence Intervals**: 90%, 95%, 99% confidence levels
- **Variability Analysis**: Standard deviation, coefficient of variation
- **Distribution Testing**: Normality tests, percentiles, outlier detection
- **Professional Format**: Industry-standard "Mean ± Half-Width (CI%) [n=reps]"
- **Reproducible Results**: Seed-based random number control

### Usage via MCP Clients

Users can request multiple replications through natural language:

> *"Run the hospital triage simulation 15 times and show me the statistical analysis"*

> *"Execute 20 replications of the M/M/1 queue with 95% and 99% confidence intervals"*

---

## Modern Prompting Guide

### Advanced System Modeling

The current engine supports sophisticated scenarios:

| Scenario Type | Key Features | Example Use Cases |
|--------------|--------------|-------------------|
| **Multi-Priority Systems** | Priority queues, attribute-based routing | Hospital triage, customer service tiers |
| **Complex Routing** | Conditional logic, multi-step flows | Manufacturing, multi-stage services |
| **Resource Optimization** | Capacity planning, utilization analysis | Staffing decisions, equipment sizing |
| **Financial Analysis** | Value tracking, cost-benefit analysis | Revenue optimization, process costing |

### Example: Hospital Emergency Department

> *"Model an emergency department with triage nurse, emergency doctors, and routine doctors. Emergency patients (20%) have priority 1, routine patients (80%) have priority 3. Triage takes 2-10 minutes uniformly. Emergency treatment averages 30 minutes (std 10), routine treatment averages 15 minutes (std 5). Patients arrive every 2.5 minutes on average. Run for 8 hours with 1-hour warmup."*

**Generated Configuration Features:**
- Mixed entity types with probability distributions
- Priority-based resource allocation
- Realistic service time distributions
- Proper warmup period for statistical accuracy
- Comprehensive performance metrics

---

## Validation and Quality Assurance

The DES engine has been extensively validated:

- **Analytical Validation**: Tested against M/M/1, M/M/c queueing theory
- **Pass Rate**: 85.7% accuracy on standard queueing models
- **Quality Score**: 6.1/10 (good performance for complex scenarios)
- **Bug Fixes**: Critical exponential distribution parameter bug resolved
- **Statistical Rigor**: Professional confidence interval reporting

---

## Security and Reliability

**Security Features:**
- **No Code Execution**: Regex-based distribution parsing prevents code injection
- **Schema Validation**: Comprehensive JSON schema prevents malformed inputs
- **Error Isolation**: Graceful error handling without system exposure
- **Input Sanitization**: All parameters validated against realistic ranges

**Reliability Features:**
- **Confidence Metadata**: Automatic reliability scoring and warnings
- **Warmup Period Handling**: Proper transient effect removal
- **Statistical Validation**: Sample size adequacy checks
- **Reproducible Results**: Deterministic random number generation

---

## Performance Characteristics

- **Single Simulation**: Typically <1 second for most business scenarios
- **Multiple Replications**: 10 replications typically <5 seconds
- **Scalability**: Handles 10,000+ entities efficiently
- **Memory Usage**: Optimized for large-scale simulations
- **Statistical Analysis**: Industry-standard scipy/numpy backends

