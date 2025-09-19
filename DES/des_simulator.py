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