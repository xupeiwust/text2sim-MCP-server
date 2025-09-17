import simpy
import random
from collections import defaultdict

# === Entity ===
class Entity:
    """
    Represents an entity flowing through the simulation.
    
    Entities are the objects that flow through the simulation process steps.
    They can have attributes that affect how they are processed.
    
    Attributes:
        id: A unique identifier for the entity.
        env: The SimPy environment in which the entity exists.
        attributes: A dictionary of custom attributes that can be used for routing or processing logic.
        arrival_time: When the entity entered the system.
        balked: Whether the entity left without being served.
        served: Whether the entity was successfully served.
    """
    def __init__(self, id, env):
        """
        Initialize a new entity.
        
        Args:
            id: A unique identifier for the entity.
            env: The SimPy environment in which the entity exists.
        """
        self.id = id
        self.env = env
        self.attributes = {}
        self.arrival_time = env.now
        self.balked = False
        self.served = False

# === Metrics Collector ===
class MetricsCollector:
    """
    Collects and summarizes metrics from the simulation run.
    
    This class is responsible for recording metrics during simulation execution
    and providing summary statistics when the simulation is complete.
    """
    def __init__(self):
        """Initialize a new metrics collector with an empty data store."""
        self.data = defaultdict(list)
        self.custom_metrics = defaultdict(float)  # For business metrics like revenue
        self.entity_counts = defaultdict(int)     # For counting different entity types

    def record(self, step_name, metric_type, value):
        """
        Record a metric value for a specific process step.
        
        Args:
            step_name: The name of the process step.
            metric_type: The type of metric being recorded (e.g., 'wait_time', 'completed').
            value: The value of the metric.
        """
        self.data[(step_name, metric_type)].append(value)

    def record_custom(self, metric_name, value):
        """
        Record a custom business metric.
        
        Args:
            metric_name: Name of the custom metric (e.g., 'total_revenue', 'customers_balked').
            value: Value to add to the metric.
        """
        self.custom_metrics[metric_name] += value

    def count_entity(self, entity_type):
        """
        Count an entity of a specific type.
        
        Args:
            entity_type: Type of entity to count (e.g., 'arrived', 'served', 'balked').
        """
        self.entity_counts[entity_type] += 1

    def summarise(self):
        """
        Summarize all collected metrics.
        
        Returns:
            A dictionary containing summary statistics for each step and metric type,
            plus custom business metrics and entity counts.
        """
        summary = {}
        
        # Standard step-based metrics
        for (step, metric), values in self.data.items():
            if values and isinstance(values[0], (int, float)):
                summary[f"{step}_{metric}_avg"] = round(sum(values) / len(values), 2)
            summary[f"{step}_{metric}_count"] = len(values)
        
        # Custom business metrics
        for metric_name, value in self.custom_metrics.items():
            summary[metric_name] = round(value, 2) if isinstance(value, float) else value
            
        # Entity counts
        for entity_type, count in self.entity_counts.items():
            summary[f"{entity_type}_count"] = count
            
        return summary

# === Process Step ===
class ProcessStep:
    """
    Represents a single step in the simulation process flow.
    
    Each process step has a resource with limited capacity and a function
    that determines how long processing takes at this step.
    """
    def __init__(self, name, resource: simpy.Resource, duration_fn, metrics: MetricsCollector):
        """
        Initialize a new process step.
        
        Args:
            name: The name of the process step.
            resource: A SimPy resource with limited capacity.
            duration_fn: A function that returns the processing time for this step.
            metrics: A metrics collector to record performance metrics.
        """
        self.name = name
        self.resource = resource
        self.duration_fn = duration_fn
        self.metrics = metrics

    def run(self, env, entity: Entity):
        """
        Process an entity through this step.
        
        This method requests a resource, waits for availability, processes
        the entity, and records relevant metrics.
        
        Args:
            env: The SimPy environment.
            entity: The entity to process.
            
        Yields:
            SimPy events for resource request and processing time.
        """
        arrival = env.now
        with self.resource.request() as req:
            yield req
            wait = env.now - arrival
            self.metrics.record(self.name, "wait_time", wait)
            service_time = self.duration_fn()
            yield env.timeout(service_time)
            self.metrics.record(self.name, "completed", 1)

# === Simulation Model ===
class SimulationModel:
    """
    Represents a complete discrete-event simulation model.
    
    This class encapsulates the SimPy environment, process steps,
    and metrics collection for a complete simulation run.
    """
    def __init__(self, config: dict):
        """
        Initialize a new simulation model.
        
        Args:
            config: A dictionary containing simulation configuration parameters.
                   Expected keys include:
                   - interarrival: Mean time between entity arrivals.
                   - num_entities: Total number of entities to generate.
                   - run_time: Total simulation runtime.
        """
        self.env = simpy.Environment()
        self.config = config
        self.metrics = MetricsCollector()
        self.steps = []

    def add_step(self, name, capacity, duration_fn):
        """
        Add a process step to the simulation model.
        
        Args:
            name: The name of the process step.
            capacity: The number of entities that can be processed simultaneously.
            duration_fn: A function that returns the processing time for this step.
        """
        resource = simpy.Resource(self.env, capacity=capacity)
        step = ProcessStep(name, resource, duration_fn, self.metrics)
        self.steps.append(step)

    def entity_process(self, id):
        """
        Define the process flow for a single entity.
        
        This generator function creates an entity and processes it
        through each step in the simulation sequentially.
        
        Args:
            id: A unique identifier for the entity.
            
        Yields:
            SimPy processes for each process step the entity goes through.
        """
        entity = Entity(id, self.env)
        for step in self.steps:
            yield self.env.process(step.run(self.env, entity))

    def run(self):
        """
        Run the simulation until completion.
        
        This method creates entities according to the configured arrival rate,
        runs the simulation for the specified duration, and returns the metrics.
        
        Returns:
            A dictionary containing summary statistics for the simulation run.
        """
        interarrival = self.config.get("interarrival", 2)
        num_entities = self.config.get("num_entities", 100)
        run_time = self.config.get("run_time", 120)

        # Create a separate generator function for entity arrivals
        def entity_arrivals():
            for i in range(num_entities):
                self.env.process(self.entity_process(i))
                yield self.env.timeout(random.expovariate(1 / interarrival))

        # Start the entity arrival process
        self.env.process(entity_arrivals())
        
        # Run the simulation
        self.env.run(until=run_time)
        return self.metrics.summarise()


# === Advanced Simulation Model ===
class AdvancedSimulationModel:
    """
    Generic advanced simulation model that supports complex scenarios through configuration.
    
    This model extends the basic DES capabilities to handle:
    - Configurable balking behavior based on queue length or other conditions
    - Different entity types with custom attributes and behaviors
    - Custom business metrics tracking
    - Flexible resource management
    - Conditional processing and routing
    """
    
    def __init__(self, config: dict):
        """
        Initialize an advanced simulation model.
        
        Args:
            config: Configuration dictionary with advanced parameters:
                - entities: Configuration for entity generation and types
                - resources: Configuration for simulation resources
                - balking_rules: Rules for when entities leave without being served
                - custom_metrics: Custom metrics to track
                - processing_rules: Rules for how entities are processed
        """
        self.env = simpy.Environment()
        self.config = config
        self.metrics = MetricsCollector()
        
        # Initialize resources based on configuration
        self.resources = {}
        self._setup_resources()
        
        # Initialize entity type configurations
        self.entity_types = self._setup_entity_types()
        
        # Initialize balking rules
        self.balking_rules = config.get("balking_rules", {})
        
        # Initialize processing rules
        self.processing_rules = config.get("processing_rules", {})
    
    def _setup_resources(self):
        """Setup simulation resources based on configuration."""
        resources_config = self.config.get("resources", {})
        
        # Handle generic resource configuration
        for resource_name, resource_config in resources_config.items():
            capacity = resource_config.get("capacity", 1)
            self.resources[resource_name] = simpy.Resource(self.env, capacity=capacity)
        
        # Default service resource if none specified
        if not self.resources:
            self.resources["service"] = simpy.Resource(self.env, capacity=1)
    
    def _setup_entity_types(self):
        """Setup entity type configurations."""
        # Handle generic entity types
        entity_types = self.config.get("entity_types", {})
        
        # Default entity type if none specified
        if not entity_types:
            entity_types = {
                "default": {
                    "probability": 1.0,
                    "attributes": {}
                }
            }
        
        return entity_types
    
    def determine_entity_type(self):
        """Randomly determine entity type based on configured probabilities."""
        rand = random.random()
        cumulative = 0
        for entity_type, info in self.entity_types.items():
            cumulative += info["probability"]
            if rand <= cumulative:
                return entity_type
        # Fallback to first entity type
        return list(self.entity_types.keys())[0]
    
    def calculate_entity_value(self, entity_type):
        """Calculate entity value based on their type."""
        type_info = self.entity_types[entity_type]
        
        # Handle generic value configuration
        value_config = type_info.get("value", {})
        if "min" in value_config and "max" in value_config:
            return random.uniform(value_config["min"], value_config["max"])
        elif "fixed" in value_config:
            return value_config["fixed"]
        
        return 0  # Default value
    
    def check_balking_conditions(self, entity):
        """Check if an entity should balk based on configured rules."""
        # Handle generic balking rules
        for rule_name, rule_config in self.balking_rules.items():
            if self._evaluate_balking_rule(rule_config, entity):
                return True
        
        return False
    
    def _evaluate_balking_rule(self, rule_config, entity):
        """Evaluate a specific balking rule."""
        rule_type = rule_config.get("type", "queue_length")
        
        if rule_type == "queue_length":
            resource_name = rule_config.get("resource", "service")
            max_length = rule_config.get("max_length", 5)
            resource = self.resources.get(resource_name)
            if resource:
                queue_length = len(resource.queue) + len(resource.users)
                return queue_length >= max_length
        
        elif rule_type == "probability":
            balk_probability = rule_config.get("probability", 0.1)
            return random.random() < balk_probability
        
        elif rule_type == "time_based":
            max_wait_time = rule_config.get("max_wait_time", 30)
            current_time = self.env.now
            arrival_time = entity.arrival_time
            return (current_time - arrival_time) >= max_wait_time
        
        return False
    
    def entity_process(self, entity_id):
        """
        Process a single entity through the simulation.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Yields:
            SimPy events for entity processing
        """
        # Entity arrives
        entity = Entity(entity_id, self.env)
        entity.attributes["type"] = self.determine_entity_type()
        entity.attributes["value"] = self.calculate_entity_value(entity.attributes["type"])
        
        # Count arrival
        arrival_metric = self.config.get("arrival_metric", "entities_arrived")
        self.metrics.count_entity(arrival_metric)
        
        # Check if entity balks
        if self.check_balking_conditions(entity):
            entity.balked = True
            balk_metric = self.config.get("balk_metric", "entities_balked")
            self.metrics.count_entity(balk_metric)
            return  # Entity leaves
        
        # Process entity through resources
        yield from self._process_entity_through_resources(entity)
    
    def _process_entity_through_resources(self, entity):
        """Process entity through the configured resources."""
        # Handle generic resource processing
        processing_steps = self.processing_rules.get("steps", ["service"])
        
        for step_name in processing_steps:
            resource = self.resources.get(step_name)
            if not resource:
                continue
                
            yield from self._process_at_resource(entity, step_name, resource)
    
    
    def _process_at_resource(self, entity, resource_name, resource):
        """Process entity at a specific resource."""
        arrival_time = self.env.now
        
        with resource.request() as req:
            yield req
            
            # Record wait time
            wait_time = self.env.now - arrival_time
            self.metrics.record(resource_name, "wait_time", wait_time)
            
            # Get processing time for this resource
            processing_time = self._get_processing_time(resource_name)
            yield self.env.timeout(processing_time)
            
            # Record completion
            self.metrics.record(resource_name, "completed", 1)
            
            # If this is the final step, mark entity as served and record value
            processing_steps = self.processing_rules.get("steps", ["service"])
            if resource_name == processing_steps[-1]:  # Last step
                entity.served = True
                served_metric = self.config.get("served_metric", "entities_served")
                self.metrics.count_entity(served_metric)
                
                # Record value
                value = entity.attributes["value"]
                if value > 0:
                    value_metric = self.config.get("value_metric", "total_value")
                    self.metrics.record_custom(value_metric, value)
                
                # Record entity type statistics
                entity_type = entity.attributes["type"]
                self.metrics.count_entity(f"served_{entity_type}")
    
    def _get_processing_time(self, resource_name):
        """Get processing time for a resource."""
        from DES.des_utils import parse_distribution
        
        # Check processing rules for this resource
        resource_config = self.processing_rules.get(resource_name, {})
        distribution = resource_config.get("distribution", "uniform(1, 3)")
        
        # Parse and return processing time
        time_fn = parse_distribution(distribution)
        return time_fn()
    
    def run(self):
        """
        Run the advanced simulation.
        
        Returns:
            Dictionary containing simulation results and business metrics
        """
        # Get configuration parameters with flexible naming
        num_entities = (self.config.get("num_entities") or 
                       self.config.get("num_customers") or 
                       self.config.get("entities_to_generate", 100))
        
        run_time = self.config.get("run_time", 480)
        
        # Handle different arrival patterns
        arrival_config = self.config.get("arrival_pattern", {})
        
        def entity_arrivals():
            """Generator for entity arrivals."""
            entities_generated = 0
            for i in range(num_entities):
                # Check if we still have time left in the simulation
                if self.env.now >= run_time:
                    break
                    
                self.env.process(self.entity_process(i))
                entities_generated += 1
                
                # Get arrival interval
                arrival_interval = self._get_arrival_interval()
                yield self.env.timeout(arrival_interval)
            
            # Record how many entities were actually generated
            self.metrics.custom_metrics["entities_generated"] = entities_generated
        
        # Start entity arrival process
        self.env.process(entity_arrivals())
        
        # Run simulation
        self.env.run(until=run_time)
        
        # Return comprehensive metrics
        results = self.metrics.summarise()
        
        # Add calculated metrics
        self._add_calculated_metrics(results)
        
        return results
    
    def _get_arrival_interval(self):
        """Get the next arrival interval based on configuration."""
        # Handle configured arrival patterns
        arrival_config = self.config.get("arrival_pattern", {})
        
        if "distribution" in arrival_config:
            from DES.des_utils import parse_distribution
            arrival_fn = parse_distribution(arrival_config["distribution"])
            return arrival_fn()
        
        # Default interarrival time
        interarrival = self.config.get("interarrival", 3)
        return random.expovariate(1 / interarrival)
    
    def _add_calculated_metrics(self, results):
        """Add calculated metrics to results."""
        # Find served/treated and arrived metrics dynamically
        served_metrics = [k for k in results.keys() if k.endswith('_served_count') or k.endswith('_treated_count') or k.endswith('_completed_count')]
        arrived_metrics = [k for k in results.keys() if k.endswith('_arrived_count')]
        value_metrics = [k for k in results.keys() if k.startswith('total_') and not k.endswith('_count')]
        
        if served_metrics and arrived_metrics:
            # Prioritize custom metric names over generic ones
            served_key = None
            for metric in served_metrics:
                if '_treated_count' in metric or '_served_count' in metric:
                    served_key = metric
                    break
            if not served_key:
                served_key = served_metrics[0]
                
            arrived_key = arrived_metrics[0]
            served_count = results[served_key]
            total_arrived = results[arrived_key]
            
            if served_count > 0:
                # Calculate average value per entity if value metrics exist
                if value_metrics:
                    total_value = results[value_metrics[0]]
                    if total_value > 0:
                        avg_value = total_value / served_count
                        # Create appropriate average metric name
                        base_name = served_key.replace('_served_count', '').replace('_treated_count', '').replace('_completed_count', '')
                        value_name = value_metrics[0].replace('total_', '')
                        results[f"average_{value_name}_per_{base_name}"] = round(avg_value, 2)
                
                # Calculate processing efficiency
                if total_arrived > 0:
                    efficiency_rate = served_count / total_arrived
                    base_name = served_key.replace('_served_count', '').replace('_treated_count', '').replace('_completed_count', '')
                    results[f"{base_name}_processing_efficiency"] = round(efficiency_rate * 100, 1)
