# 📊 DES Schema Documentation

## 🎯 Overview

The **SimPy-Compatible Discrete-Event Simulation Schema** (`des-simpy-compatible-schema.json`) is a JSON Schema 2020-12 specification that enables non-coders to create sophisticated discrete-event simulations through declarative configuration. This schema is specifically designed to leverage SimPy's native capabilities while providing a user-friendly interface for complex simulation modeling.

## 🏗️ Schema Philosophy

### **Declarative Configuration**
Users describe **what** they want (business logic) rather than **how** to implement it (SimPy code). The schema translates business requirements into executable simulation logic.

### **SimPy-Native Compatibility**
Every feature in this schema maps directly to SimPy's built-in capabilities, ensuring reliable performance and maintainability without requiring custom extensions.

### **Progressive Complexity**
The schema supports both simple scenarios (single resource, basic flow) and complex systems (multiple entity types, priority queues, balking, reneging, routing, failures).

---

## 📋 Schema Structure

### **Required Fields**
- `run_time`: Simulation duration
- **Either** `arrival_pattern` **OR** `num_entities` (mutually exclusive)

### **Core Components**
1. **Entity Management**: Types, priorities, values, attributes
2. **Resource Definition**: Capacity, queuing disciplines
3. **Process Flow**: Sequential steps, service times, routing
4. **Behavioral Rules**: Balking, reneging, failures
5. **Metrics Collection**: Custom names, statistics

---

## 🎭 Entity Types

Defines different classes of entities flowing through the system.

```json
{
  "entity_types": {
    "vip_customer": {
      "probability": 0.2,
      "value": {"min": 100, "max": 500},
      "priority": 1,
      "attributes": {"membership": "gold", "urgent": true}
    },
    "regular_customer": {
      "probability": 0.8,
      "value": {"min": 10, "max": 50},
      "priority": 5
    }
  }
}
```

### **Properties**
- **`probability`** *(required)*: Must sum to 1.0 across all entity types
- **`value`**: Economic value range (min/max) for revenue calculations
- **`priority`**: SimPy priority (1=highest, 10=lowest)
- **`attributes`**: Custom properties for conditional routing

### **Use Cases**
- Customer segments (VIP, regular, staff)
- Job types (urgent, standard, batch)
- Patient categories (emergency, routine)

---

## 🏭 Resources

Defines system capacity and queuing behavior using SimPy's native resource types.

```json
{
  "resources": {
    "reception": {"capacity": 2, "resource_type": "fifo"},
    "service": {"capacity": 3, "resource_type": "priority"},
    "specialist": {"capacity": 1, "resource_type": "preemptive"}
  }
}
```

### **Resource Types**
- **`fifo`**: First-In-First-Out (SimPy `Resource`)
- **`priority`**: Priority queue (SimPy `PriorityResource`)
- **`preemptive`**: Priority with preemption (SimPy `PreemptiveResource`)

### **Properties**
- **`capacity`** *(required)*: Number of parallel servers
- **`resource_type`**: Queuing discipline (default: "fifo")

---

## 🔄 Processing Rules

Defines the flow of entities through resources and service time distributions.

```json
{
  "processing_rules": {
    "steps": ["reception", "service", "checkout"],
    "reception": {"distribution": "uniform(2, 5)"},
    "service": {
      "distribution": "normal(10, 2)",
      "conditional_distributions": {
        "vip_customer": "normal(5, 1)",
        "regular_customer": "normal(12, 3)"
      }
    },
    "checkout": {"distribution": "exp(3)"}
  }
}
```

### **Components**
- **`steps`** *(required)*: Ordered list of resource names
- **Resource configurations**: Service time distributions per resource
- **`conditional_distributions`**: Different service times by entity type

### **Distribution Formats**
- `uniform(min, max)`: Uniform distribution
- `normal(mean, std)`: Normal distribution (negative values clamped to 0)
- `exp(mean)`: Exponential distribution (mean, not rate)
- `gauss(mean, std)`: Alias for normal

---

## 🚪 Balking Rules

Defines conditions under which entities leave without joining queues.

```json
{
  "balking_rules": {
    "overcrowding": {
      "type": "queue_length",
      "resource": "service",
      "max_length": 8,
      "priority_multipliers": {"1": 0.1, "5": 1.0, "10": 2.0}
    },
    "random_balking": {
      "type": "probability",
      "probability": 0.05
    }
  }
}
```

### **Balking Types**
- **`queue_length`**: Balk when queue exceeds threshold
- **`wait_time`**: Balk based on expected wait (implemented as reneging)
- **`probability`**: Random balking on arrival

### **Priority Multipliers**
Higher priority entities (lower numbers) are less likely to balk. Multipliers adjust balking probability by priority level.

---

## ⏰ Reneging Rules

Defines abandonment behavior for entities already in queues.

```json
{
  "reneging_rules": {
    "impatience": {
      "abandon_time": "normal(30, 10)",
      "priority_multipliers": {"1": 5.0, "5": 1.0, "10": 0.3}
    }
  }
}
```

### **Properties**
- **`abandon_time`**: Distribution for patience duration
- **`priority_multipliers`**: Higher priority = more patient (larger multipliers)

---

## 🗺️ Simple Routing

Conditional routing based on entity attributes.

```json
{
  "simple_routing": {
    "triage_routing": {
      "conditions": [
        {"attribute": "severity", "operator": "==", "value": "critical", "destination": "emergency_room"},
        {"attribute": "priority", "operator": "<=", "value": 3, "destination": "fast_track"}
      ],
      "default_destination": "regular_service"
    }
  }
}
```

### **Supported Operators**
- `==`, `!=`: Equality/inequality
- `>`, `<`, `>=`, `<=`: Numerical comparisons

---

## 🔧 Basic Failures

Simple resource failure and repair cycles.

```json
{
  "basic_failures": {
    "machine_a": {
      "mtbf": "exp(480)",
      "repair_time": "normal(60, 15)"
    }
  }
}
```

### **Properties**
- **`mtbf`**: Mean Time Between Failures
- **`repair_time`**: Time to repair (resource capacity → 0 → restored)

---

## 🎯 Arrival Patterns

Defines how entities enter the system.

### **Continuous Arrivals**
```json
{
  "arrival_pattern": {
    "distribution": "exp(5)"
  }
}
```

### **Fixed Batch**
```json
{
  "num_entities": 1000
}
```

**Note**: `arrival_pattern` and `num_entities` are mutually exclusive.

---

## 📊 Metrics Configuration

Customize metric names for domain-specific terminology.

```json
{
  "metrics": {
    "arrival_metric": "patients_arrived",
    "served_metric": "patients_treated", 
    "balk_metric": "patients_left_immediately",
    "reneged_metric": "patients_abandoned_queue",
    "value_metric": "total_treatment_cost"
  }
}
```

### **Available Metrics**
- **`arrival_metric`**: Entities entering system
- **`served_metric`**: Entities completing all steps
- **`balk_metric`**: Entities leaving without service
- **`reneged_metric`**: Entities abandoning queues
- **`value_metric`**: Total economic value

---

## 📈 Statistics Collection

Control what additional statistics to collect.

```json
{
  "statistics": {
    "collect_wait_times": true,
    "collect_queue_lengths": true,
    "collect_utilization": true,
    "warmup_period": 120
  }
}
```

### **Statistics Options**
- **`collect_wait_times`**: Average wait times per resource
- **`collect_queue_lengths`**: Time-weighted queue lengths
- **`collect_utilization`**: Resource utilization percentages
- **`warmup_period`**: Time to exclude from statistics (steady-state)

---

## 🎯 Complete Examples

### **Basic Coffee Shop**
```json
{
  "run_time": 480,
  "entity_types": {
    "regular_customer": {"probability": 0.8, "value": {"min": 3, "max": 6}, "priority": 5},
    "vip_customer": {"probability": 0.2, "value": {"min": 8, "max": 15}, "priority": 2}
  },
  "resources": {
    "barista": {"capacity": 1, "resource_type": "priority"}
  },
  "processing_rules": {
    "steps": ["barista"],
    "barista": {"distribution": "normal(5, 1)"}
  },
  "balking_rules": {
    "overcrowding": {"type": "queue_length", "resource": "barista", "max_length": 8}
  },
  "arrival_pattern": {"distribution": "uniform(2, 8)"},
  "metrics": {
    "arrival_metric": "customers_arrived",
    "served_metric": "customers_served",
    "value_metric": "total_revenue"
  }
}
```

### **Hospital Triage System**
```json
{
  "run_time": 720,
  "entity_types": {
    "emergency": {"probability": 0.1, "priority": 1, "value": {"min": 2000, "max": 5000}},
    "urgent": {"probability": 0.3, "priority": 3, "value": {"min": 500, "max": 2000}},
    "routine": {"probability": 0.6, "priority": 7, "value": {"min": 100, "max": 500}}
  },
  "resources": {
    "triage": {"capacity": 2, "resource_type": "priority"},
    "treatment": {"capacity": 8, "resource_type": "preemptive"},
    "discharge": {"capacity": 1, "resource_type": "fifo"}
  },
  "processing_rules": {
    "steps": ["triage", "treatment", "discharge"],
    "triage": {"distribution": "uniform(5, 15)"},
    "treatment": {
      "conditional_distributions": {
        "emergency": "normal(60, 20)",
        "urgent": "normal(30, 10)",
        "routine": "normal(20, 5)"
      }
    },
    "discharge": {"distribution": "uniform(5, 10)"}
  },
  "balking_rules": {
    "overcrowding": {
      "type": "queue_length",
      "resource": "triage",
      "max_length": 15,
      "priority_multipliers": {"1": 0.0, "3": 0.2, "7": 1.0}
    }
  },
  "reneging_rules": {
    "patient_patience": {
      "abandon_time": "normal(45, 15)",
      "priority_multipliers": {"1": 10.0, "3": 3.0, "7": 1.0}
    }
  },
  "arrival_pattern": {"distribution": "exp(3)"},
  "metrics": {
    "arrival_metric": "patients_arrived",
    "served_metric": "patients_treated",
    "balk_metric": "patients_left_immediately",
    "reneged_metric": "patients_left_queue",
    "value_metric": "total_treatment_cost"
  },
  "statistics": {
    "collect_wait_times": true,
    "collect_utilization": true,
    "warmup_period": 120
  }
}
```

---

## ⚙️ Implementation Notes

### **SimPy Mapping**
- **Entity Types** → `Entity` class with priority/attributes
- **Resources** → `simpy.Resource`/`PriorityResource`/`PreemptiveResource`
- **Processing Rules** → SimPy processes with `yield request`/`timeout`/`release`
- **Balking** → Pre-request condition checks
- **Reneging** → `request | timeout` with conditional abandonment
- **Distributions** → Python random functions via `parse_distribution()`

### **Validation Rules**
- Entity type probabilities must sum to 1.0 (±0.001 tolerance)
- All resource references in rules must exist in `resources`
- Distribution strings must match regex patterns
- Priority values constrained to 1-10 range

### **Performance Considerations**
- Warmup periods exclude initial transient behavior
- Queue length collection can impact performance for large systems
- Resource utilization tracking adds minimal overhead

---

## 🚀 Getting Started

1. **Start Simple**: Begin with basic entity types and single resources
2. **Add Complexity Gradually**: Introduce priorities, balking, routing as needed
3. **Validate Configuration**: Schema provides comprehensive error checking
4. **Iterate and Refine**: Use warmup periods and statistics for steady-state analysis

### **Common Patterns**
- **Service Systems**: Reception → Service → Checkout
- **Manufacturing**: Queue → Process → Inspect → Ship
- **Healthcare**: Triage → Treatment → Discharge
- **Call Centers**: Queue → Agent → Follow-up

---

## 🔗 Related Files

- **`des-simpy-compatible-schema.json`**: The complete JSON Schema specification
- **`json-to-simulation-flow.md`**: Detailed explanation of JSON → SimPy transformation
- **`../DES/schema_validator.py`**: Schema validation and normalization
- **`../DES/unified_simulator.py`**: SimPy simulation implementation

---

## 📚 Additional Resources

- [SimPy Documentation](https://simpy.readthedocs.io/)
- [JSON Schema 2020-12 Specification](https://json-schema.org/draft/2020-12/schema)
- [Discrete-Event Simulation Concepts](https://en.wikipedia.org/wiki/Discrete-event_simulation)

---

*This schema enables sophisticated discrete-event simulations through simple JSON configuration, making advanced simulation modeling accessible to non-programmers while leveraging the full power of SimPy.* 🎯
