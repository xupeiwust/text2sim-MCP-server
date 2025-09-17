# 🔄 From JSON to Simulation: The Complete Transformation

## 📋 **Overview: JSON → SimPy Code Flow**

```
JSON Config → Schema Validation → Normalization → SimPy Objects → Execution → Results
     ↓              ↓                 ↓              ↓           ↓         ↓
User Input    Error Checking    Apply Defaults   Create Resources  Run Sim   Metrics
```

## 🔍 **Step-by-Step Transformation**

### **Step 1: JSON Input**
```json
{
  "run_time": 480,
  "entity_types": {
    "premium": {"probability": 0.1, "value": {"min": 1200, "max": 1200}, "priority": 1}
  },
  "resources": {
    "final_assembly": {"capacity": 4, "resource_type": "preemptive"}
  },
  "processing_rules": {
    "steps": ["final_assembly"],
    "final_assembly": {"distribution": "normal(35, 10)"}
  }
}
```

### **Step 2: Schema Validation (`DESConfigValidator`)**
```python
# In schema_validator.py
validator = DESConfigValidator()
normalized_config, errors = validator.validate_and_normalize(config)

# This checks:
# - JSON Schema 2020-12 compliance
# - Business rules (probabilities sum to 1.0)
# - Resource references exist
# - Distribution formats are valid
```

### **Step 3: SimPy Object Creation (`UnifiedSimulationModel.__init__`)**
```python
# In unified_simulator.py
class UnifiedSimulationModel:
    def __init__(self, config):
        self.env = simpy.Environment()  # Create SimPy environment
        
        # Transform JSON resources into SimPy resources
        self.resources = self._setup_resources()
```

**JSON Resources → SimPy Resources:**
```python
def _setup_resources(self):
    resources = {}
    for name, config in self.config.get("resources", {}).items():
        capacity = config.get("capacity", 1)
        resource_type = config.get("resource_type", "fifo")
        
        # JSON "resource_type" → Actual SimPy classes
        if resource_type == "fifo":
            resources[name] = simpy.Resource(self.env, capacity=capacity)
        elif resource_type == "priority":
            resources[name] = simpy.PriorityResource(self.env, capacity=capacity)
        elif resource_type == "preemptive":
            resources[name] = simpy.PreemptiveResource(self.env, capacity=capacity)
    
    return resources
```

**Result:** `"final_assembly": {"capacity": 4, "resource_type": "preemptive"}` becomes:
```python
final_assembly = simpy.PreemptiveResource(env, capacity=4)
```

### **Step 4: Entity Creation Process**
```python
# JSON entity_types become Entity objects
def _determine_entity_type(self):
    rand = random.random()
    cumulative_prob = 0.0
    
    for entity_type, config in self.entity_types.items():
        cumulative_prob += config["probability"]
        if rand <= cumulative_prob:
            return entity_type

# JSON "premium": {"probability": 0.1, "priority": 1, "value": {...}}
# Becomes:
entity = Entity(id=1, type="premium", config=entity_config)
entity.priority = 1  # Used in SimPy priority queues
entity.value = random.uniform(1200, 1200)  # Random value from range
```

### **Step 5: Distribution String → Python Functions**
```python
# In des_utils.py
def parse_distribution(dist_str: str):
    # "normal(35, 10)" becomes:
    if dist_name == "normal":
        return lambda: max(0, random.gauss(args[0], args[1]))
    
    # So "normal(35, 10)" → function that returns random.gauss(35, 10)
```

**Usage in Simulation:**
```python
# JSON: "final_assembly": {"distribution": "normal(35, 10)"}
# Becomes:
service_time = parse_distribution("normal(35, 10)")()  # Calls the function
yield self.env.timeout(service_time)  # SimPy timeout with random time
```

### **Step 6: Processing Rules → SimPy Processes**
```python
def _entity_process(self, entity):
    # JSON "steps": ["final_assembly"] becomes loop:
    for step_name in self.processing_steps:
        # Process at each resource
        yield from self._process_at_resource(entity, step_name)

def _process_at_resource(self, entity, resource_name):
    resource = self.resources[resource_name]  # Get SimPy resource
    
    # JSON priority becomes SimPy priority request
    if isinstance(resource, simpy.PreemptiveResource):
        request = resource.request(priority=entity.priority)
    else:
        request = resource.request()
    
    yield request  # SimPy: wait for resource
    
    # JSON distribution becomes actual processing time
    service_time = self._get_service_time(entity, resource_name)
    yield self.env.timeout(service_time)  # SimPy: process for time
    
    resource.release(request)  # SimPy: release resource
```

### **Step 7: Balking Rules → Python Logic**
```json
"balking_rules": {
  "overcrowding": {
    "type": "queue_length",
    "resource": "final_assembly",
    "max_length": 12,
    "priority_multipliers": {"1": 0.0, "5": 1.0}
  }
}
```

**Becomes:**
```python
def _check_balking(self, entity):
    for rule_name, rule in self.balking_rules.items():
        if rule["type"] == "queue_length":
            resource = self.resources[rule["resource"]]
            current_queue_length = len(resource.queue)  # SimPy queue length
            
            # Apply priority multipliers
            balk_threshold = rule["max_length"]
            if "priority_multipliers" in rule:
                priority_str = str(entity.priority)
                if priority_str in rule["priority_multipliers"]:
                    multiplier = rule["priority_multipliers"][priority_str]
                    balk_threshold = rule["max_length"] * multiplier
            
            if current_queue_length >= balk_threshold:
                return True  # Entity balks (leaves without service)
    return False
```

### **Step 8: Arrival Pattern → SimPy Generator**
```json
"arrival_pattern": {"distribution": "uniform(8, 15)"}
```

**Becomes:**
```python
def _entity_arrivals_continuous(self):
    entity_id = 0
    distribution = self.arrival_pattern["distribution"]
    
    while True:
        # JSON distribution → actual time delay
        interarrival_time = parse_distribution(distribution)()
        yield self.env.timeout(interarrival_time)  # SimPy: wait
        
        # Create new entity and start processing
        entity_id += 1
        entity = Entity(entity_id, entity_type, config)
        self.env.process(self._entity_process(entity))  # SimPy: start process
```

### **Step 9: Metrics Collection → Results**
```python
# JSON metrics config becomes data collection
class EnhancedMetricsCollector:
    def __init__(self, metrics_config):
        # JSON "arrival_metric": "orders_received" becomes:
        self.arrival_metric = metrics_config.get("arrival_metric", "entities_arrived")
        
    def record_arrival(self, entity, time):
        # Increment counter with custom name from JSON
        self.entity_counts[f"{self.arrival_metric}_count"] += 1
        
    def get_results(self):
        results = dict(self.entity_counts)  # Custom metric names
        results.update(self.custom_metrics)  # Revenue, costs, etc.
        self._add_calculated_metrics(results)  # Efficiency, averages
        return results
```

## 🎯 **Complete Example: JSON → SimPy Code**

### **Input JSON:**
```json
{
  "run_time": 120,
  "entity_types": {
    "customer": {"probability": 1.0, "value": {"min": 100, "max": 200}, "priority": 5}
  },
  "resources": {
    "server": {"capacity": 2, "resource_type": "priority"}
  },
  "processing_rules": {
    "steps": ["server"],
    "server": {"distribution": "normal(10, 2)"}
  },
  "arrival_pattern": {"distribution": "exp(5)"}
}
```

### **Generated SimPy Code (Conceptual):**
```python
import simpy
import random

# Create environment
env = simpy.Environment()

# Create resources (from JSON)
server = simpy.PriorityResource(env, capacity=2)

# Entity class (from JSON entity_types)
class Customer:
    def __init__(self, id):
        self.id = id
        self.priority = 5
        self.value = random.uniform(100, 200)

# Process function (from JSON processing_rules)
def customer_process(env, customer, server):
    # Request resource with priority
    request = server.request(priority=customer.priority)
    yield request
    
    # Service time from distribution
    service_time = max(0, random.gauss(10, 2))  # normal(10, 2)
    yield env.timeout(service_time)
    
    server.release(request)

# Arrival process (from JSON arrival_pattern)
def customer_arrivals(env, server):
    customer_id = 0
    while True:
        # Inter-arrival time
        interarrival = random.expovariate(1/5)  # exp(5)
        yield env.timeout(interarrival)
        
        # Create and start customer process
        customer_id += 1
        customer = Customer(customer_id)
        env.process(customer_process(env, customer, server))

# Run simulation
env.process(customer_arrivals(env, server))
env.run(until=120)  # run_time from JSON
```

## 🔧 **Key Transformation Points**

1. **JSON Schema → Python Types**
   - `"capacity": 4` → `simpy.Resource(env, capacity=4)`
   - `"resource_type": "preemptive"` → `simpy.PreemptiveResource`

2. **String Distributions → Random Functions**
   - `"normal(10, 2)"` → `lambda: random.gauss(10, 2)`
   - `"uniform(5, 15)"` → `lambda: random.uniform(5, 15)`

3. **Business Rules → Python Logic**
   - JSON balking rules → `if queue_length > threshold: return True`
   - JSON priority multipliers → `threshold * multiplier`

4. **Configuration → Behavior**
   - JSON steps array → Python for loop over resources
   - JSON metrics names → Dynamic result dictionary keys

## 🎉 **The Magic**

The beauty of our system is that **users write declarative JSON** (what they want) and our code generates **imperative SimPy processes** (how to do it). The JSON becomes a high-level specification that gets compiled into executable simulation logic!

**User thinks:** "I want a server with capacity 2 that takes 10±2 minutes per customer"
**System creates:** Full SimPy resource with priority queues, random service times, and metrics collection

This is why non-coders can create sophisticated simulations - they describe the system in business terms, and our schema-driven engine handles all the SimPy complexity! 🚀
