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

    def record(self, step_name, metric_type, value):
        """
        Record a metric value for a specific process step.
        
        Args:
            step_name: The name of the process step.
            metric_type: The type of metric being recorded (e.g., 'wait_time', 'completed').
            value: The value of the metric.
        """
        self.data[(step_name, metric_type)].append(value)

    def summarise(self):
        """
        Summarize all collected metrics.
        
        Returns:
            A dictionary containing summary statistics for each step and metric type.
            Keys are formatted as '{step_name}_{metric_type}_{statistic}'.
            Values are the corresponding statistical values.
        """
        summary = {}
        for (step, metric), values in self.data.items():
            if isinstance(values[0], (int, float)):
                summary[f"{step}_{metric}_avg"] = round(sum(values) / len(values), 2)
            summary[f"{step}_{metric}_count"] = len(values)
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

        for i in range(num_entities):
            self.env.process(self.entity_process(i))
            yield self.env.timeout(random.expovariate(1 / interarrival))

        self.env.run(until=run_time)
        return self.metrics.summarise()
