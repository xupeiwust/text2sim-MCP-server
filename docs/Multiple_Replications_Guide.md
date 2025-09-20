# Multiple Replications Tool - User Guide

## Overview

The Multiple Replications Tool enables users to run simulation studies with proper statistical rigor by executing multiple independent simulation runs and providing comprehensive statistical analysis. This is essential for reliable decision-making and meets industry standards for simulation studies.

## Key Features

### **MCP Client Integration**
Users can simply ask the LLM: *"Run the hospital triage simulation 10 times"* and get professional statistical analysis.

### **Industry-Standard Statistical Outputs**
- **Central Tendency:** Mean, median, mode
- **Variability:** Standard deviation, coefficient of variation, range
- **Confidence Intervals:** 90%, 95%, 99% (configurable)
- **Distribution Analysis:** Percentiles, normality tests, outlier detection
- **Sample Statistics:** Standard error, degrees of freedom, relative precision

### **Professional Reporting Format**
Results follow industry standard: `Mean ± Half-Width (CI%) [n=replications]`

Example: `Utilization: 0.785 ± 0.023 (95%) [n=20]`

## Usage Examples

### Basic Usage via MCP Client (ex. Claude Desktop etc)
```
"Run the single server queue template 15 times"
"Execute hospital triage simulation with 20 replications"
"Perform multiple runs of the manufacturing template with statistical analysis"
```

### Direct MCP Tool Call
```json
{
  "tool": "run_multiple_simulations",
  "arguments": {
    "config": {
      "run_time": 1000,
      "arrival_pattern": {"distribution": "exp(2.0)"},
      "entity_types": {
        "customer": {
          "probability": 1.0,
          "priority": 1,
          "value": {"min": 10, "max": 50}
        }
      },
      "resources": {
        "server": {"capacity": 1, "resource_type": "fifo"}
      },
      "processing_rules": {
        "steps": ["server"],
        "server": {"distribution": "exp(1.5)"}
      },
      "statistics": {
        "collect_wait_times": true,
        "collect_utilization": true,
        "warmup_period": 100
      }
    },
    "replications": 10,
    "random_seed_base": 12345
  }
}
```

## Parameters

### Required Parameters
- **`config`**: Complete simulation configuration (same format as single simulation)

### Optional Parameters
- **`replications`**: Number of independent runs (default: 10, minimum: 2, maximum: 100)
- **`random_seed_base`**: Base seed for reproducible results (default: current timestamp)
- **`confidence_levels`**: List of confidence levels (default: [0.90, 0.95, 0.99])

## Best Practices

### Choosing Number of Replications

- **Pilot Study**: Start with 5-10 replications to assess variability
- **Standard Study**: Use 10-20 replications for most applications
- **High-Precision Study**: Use 20-50 replications for critical decisions
- **Research Study**: Use 30+ replications for publication-quality results

### When to Use Multiple Replications

✅ **Always Use For:**
- Business decision-making
- Capacity planning
- Performance comparisons
- System optimization
- Research studies

⚠️ **Single Runs OK For:**
- Initial model testing
- Quick feasibility checks
- Educational demonstrations
- Model debugging

## Example Output

Here's what users see when running multiple replications:

```
SIMULATION REPLICATION ANALYSIS SUMMARY
==================================================
Total Replications: 10
Successful Runs: 10

Server Utilization:
  0.6844 ± 0.0597 (95%) [n=10]
  Std Dev: 0.0481, CV: 7.02%
  Range: [0.6391, 0.7428]
  Relative Precision: ±8.7%

Average Wait Time:
  4.6260 ± 1.0145 (95%) [n=10]
  Std Dev: 0.8171, CV: 17.66%
  Range: [3.5600, 5.3200]
  Relative Precision: ±21.9%
```

