"""
Unified SimPy-based discrete-event simulation model.

This module provides a single, comprehensive simulation model that handles all DES
scenarios through schema-driven configuration, replacing the previous two-tier system.
"""

import simpy
import random
import re
from collections import defaultdict, namedtuple
from typing import Dict, Any, List, Optional, Union
from DES.des_utils import parse_distribution


class Entity:
    """
    Represents an entity flowing through the simulation system.
    
    Enhanced with priority, attributes, timing information, and status tracking.
    """
    
    def __init__(self, entity_id: int, entity_type: str, config: Dict[str, Any]):
        self.id = entity_id
        self.type = entity_type
        self.arrival_time = None
        self.departure_time = None
        self.served = False
        self.balked = False
        self.reneged = False
        
        # Priority (smaller numbers = higher priority in SimPy)
        self.priority = config.get("priority", 5)
        
        # Value/revenue for this entity
        value_config = config.get("value", {"min": 0, "max": 0})
        self.value = random.uniform(value_config["min"], value_config["max"])
        
        # Custom attributes for routing
        self.attributes = config.get("attributes", {}).copy()
        self.attributes["priority"] = self.priority
        self.attributes["entity_type"] = entity_type
        self.attributes["value"] = self.value
        
        # Processing tracking
        self.processing_times = {}
        self.wait_times = {}
        self.current_step = 0


class EnhancedMetricsCollector:
    """
    Schema-aware metrics collector with configurable metric names and comprehensive tracking.
    """
    
    def __init__(self, metrics_config: Dict[str, str], statistics_config: Dict[str, Any]):
        self.data = defaultdict(list)
        self.custom_metrics = defaultdict(float)
        self.entity_counts = defaultdict(int)
        self.resource_stats = defaultdict(lambda: {"total_time": 0, "busy_time": 0, "entities_served": 0})
        
        # Configurable metric names
        self.arrival_metric = metrics_config.get("arrival_metric", "entities_arrived")
        self.served_metric = metrics_config.get("served_metric", "entities_served")
        self.balk_metric = metrics_config.get("balk_metric", "entities_balked")
        self.reneged_metric = metrics_config.get("reneged_metric", "entities_reneged")
        self.value_metric = metrics_config.get("value_metric", "total_value")
        
        # Statistics collection settings
        self.collect_wait_times = statistics_config.get("collect_wait_times", True)
        self.collect_queue_lengths = statistics_config.get("collect_queue_lengths", False)
        self.collect_utilization = statistics_config.get("collect_utilization", True)
        self.warmup_period = statistics_config.get("warmup_period", 0)
        
        # Data storage
        self.wait_times_data = []
        self.queue_length_data = []
        self.entities = []
    
    def record_arrival(self, entity: Entity, time: float):
        """Record entity arrival."""
        if time >= self.warmup_period:
            self.entity_counts[f"{self.arrival_metric}_count"] += 1
            self.entities.append(entity)
    
    def record_service_start(self, entity: Entity, resource_name: str, time: float):
        """Record when entity starts being served at a resource."""
        if time >= self.warmup_period and self.collect_wait_times:
            wait_time = time - entity.arrival_time
            entity.wait_times[resource_name] = wait_time
            self.wait_times_data.append(wait_time)
    
    def record_service_complete(self, entity: Entity, resource_name: str, time: float, service_time: float):
        """Record when entity completes service at a resource."""
        if time >= self.warmup_period:
            entity.processing_times[resource_name] = service_time
            self.resource_stats[resource_name]["entities_served"] += 1
            self.resource_stats[resource_name]["busy_time"] += service_time
    
    def record_departure(self, entity: Entity, time: float):
        """Record entity departure (successful completion)."""
        if time >= self.warmup_period:
            entity.departure_time = time
            entity.served = True
            self.entity_counts[f"{self.served_metric}_count"] += 1
            self.custom_metrics[self.value_metric] += entity.value
    
    def record_balking(self, entity: Entity, time: float):
        """Record entity balking (leaving without service)."""
        if time >= self.warmup_period:
            entity.balked = True
            self.entity_counts[f"{self.balk_metric}_count"] += 1
    
    def record_reneging(self, entity: Entity, time: float):
        """Record entity reneging (abandoning queue)."""
        if time >= self.warmup_period:
            entity.reneged = True
            self.entity_counts[f"{self.reneged_metric}_count"] += 1
    
    def update_resource_time(self, resource_name: str, time_elapsed: float):
        """Update total time for resource utilization calculation."""
        if self.collect_utilization:
            self.resource_stats[resource_name]["total_time"] += time_elapsed
    
    def get_results(self, simulation_run_time: float = 0, resources: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive simulation results."""
        results = dict(self.entity_counts)
        results.update(self.custom_metrics)
        
        # Store resources reference for utilization calculation
        self.resources = resources or {}
        
        # Add calculated metrics
        self._add_calculated_metrics(results)
        
        # Add resource utilization
        if self.collect_utilization and simulation_run_time > 0:
            self._add_utilization_metrics(results, simulation_run_time)
        
        # Add wait time statistics
        if self.collect_wait_times and self.wait_times_data:
            self._add_wait_time_metrics(results)
        
        return results
    
    def _add_calculated_metrics(self, results: Dict[str, Any]):
        """Add calculated metrics like efficiency and averages."""
        served_count = results.get(f"{self.served_metric}_count", 0)
        arrived_count = results.get(f"{self.arrival_metric}_count", 0)
        total_value = results.get(self.value_metric, 0)
        
        # Processing efficiency
        if arrived_count > 0:
            efficiency = (served_count / arrived_count) * 100
            results[f"{self.served_metric.replace('_', '_')}_processing_efficiency"] = round(efficiency, 2)
        
        # Average value per served entity
        if served_count > 0 and total_value > 0:
            avg_value = total_value / served_count
            # Create clean metric name
            value_base = self.value_metric.replace("total_", "").replace("_", "")
            served_base = self.served_metric.replace("_served", "").replace("_", "")
            results[f"average_{value_base}_per_{served_base}"] = round(avg_value, 2)
    
    def _add_utilization_metrics(self, results: Dict[str, Any], simulation_run_time: float):
        """Add resource utilization metrics."""
        for resource_name, stats in self.resource_stats.items():
            if simulation_run_time > 0 and stats["busy_time"] > 0:
                # Calculate utilization based on actual busy time vs simulation time
                # For multi-capacity resources, divide by capacity
                resource = self.resources.get(resource_name)
                capacity = getattr(resource, 'capacity', 1) if resource else 1
                
                # Total available time = simulation_time * capacity
                total_available_time = simulation_run_time * capacity
                
                utilization = (stats["busy_time"] / total_available_time) * 100
                results[f"{resource_name}_utilization"] = round(utilization, 2)
    
    def _add_wait_time_metrics(self, results: Dict[str, Any]):
        """Add wait time statistics."""
        if self.wait_times_data:
            results["average_wait_time"] = round(sum(self.wait_times_data) / len(self.wait_times_data), 2)
            results["max_wait_time"] = round(max(self.wait_times_data), 2)
            results["min_wait_time"] = round(min(self.wait_times_data), 2)


class UnifiedSimulationModel:
    """
    Unified simulation model that handles all DES scenarios through schema-driven configuration.
    
    Replaces both SimulationModel and AdvancedSimulationModel with a single, comprehensive
    implementation that leverages SimPy's native capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.env = simpy.Environment()
        self.config = config
        self.metrics = EnhancedMetricsCollector(
            config.get("metrics", {}), 
            config.get("statistics", {})
        )
        
        # Setup simulation components
        self.entity_types = config.get("entity_types", {"default": {"probability": 1.0}})
        self.resources = self._setup_resources()
        self.processing_steps = config.get("processing_rules", {}).get("steps", list(self.resources.keys()))
        self.balking_rules = config.get("balking_rules", {})
        self.reneging_rules = config.get("reneging_rules", {})
        self.routing_rules = config.get("simple_routing", {})
        self.failure_rules = config.get("basic_failures", {})
        
        # Arrival configuration
        self.arrival_pattern = config.get("arrival_pattern")
        self.num_entities = config.get("num_entities")
        
        # Setup failure processes
        self._setup_failures()
    
    def _setup_resources(self) -> Dict[str, simpy.Resource]:
        """Create SimPy resources from configuration with proper types."""
        resources = {}
        resource_configs = self.config.get("resources", {"service": {"capacity": 1, "resource_type": "fifo"}})
        
        for name, config in resource_configs.items():
            capacity = config.get("capacity", 1)
            resource_type = config.get("resource_type", "fifo")
            
            if resource_type == "fifo":
                resources[name] = simpy.Resource(self.env, capacity=capacity)
            elif resource_type == "priority":
                resources[name] = simpy.PriorityResource(self.env, capacity=capacity)
            elif resource_type == "preemptive":
                resources[name] = simpy.PreemptiveResource(self.env, capacity=capacity)
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")
        
        return resources
    
    def _setup_failures(self):
        """Setup resource failure processes."""
        for resource_name, failure_config in self.failure_rules.items():
            if resource_name in self.resources:
                self.env.process(self._failure_process(resource_name, failure_config))
    
    def _failure_process(self, resource_name: str, failure_config: Dict[str, Any]):
        """Process that handles resource failures and repairs."""
        resource = self.resources[resource_name]
        original_capacity = resource.capacity
        
        while True:
            # Wait for failure
            mtbf_time = parse_distribution(failure_config["mtbf"])()
            yield self.env.timeout(mtbf_time)
            
            # Fail the resource (reduce capacity to 0)
            resource._capacity = 0
            
            # Wait for repair
            repair_time = parse_distribution(failure_config["repair_time"])()
            yield self.env.timeout(repair_time)
            
            # Restore the resource
            resource._capacity = original_capacity
    
    def run(self) -> Dict[str, Any]:
        """Execute the simulation and return results."""
        try:
            # Start entity arrival process
            if self.arrival_pattern:
                self.env.process(self._entity_arrivals_continuous())
            elif self.num_entities:
                self.env.process(self._entity_arrivals_fixed())
            else:
                raise ValueError("Must specify either arrival_pattern or num_entities")
            
            # Start resource utilization tracking
            if self.metrics.collect_utilization:
                for resource_name in self.resources:
                    self.env.process(self._track_resource_utilization(resource_name))
            
            # Run simulation
            run_time = self.config["run_time"]
            self.env.run(until=run_time)
            
            # Get actual simulation end time (might be less than run_time due to early completion)
            actual_run_time = self.env.now
            
            return self.metrics.get_results(actual_run_time, self.resources)
            
        except Exception as e:
            return {"error": f"Simulation execution error: {str(e)}"}
    
    def _entity_arrivals_continuous(self):
        """Generate entities based on arrival pattern."""
        entity_id = 0
        distribution = self.arrival_pattern["distribution"]
        
        while True:
            # Generate inter-arrival time
            interarrival_time = parse_distribution(distribution)()
            yield self.env.timeout(interarrival_time)
            
            # Create and process entity
            entity_id += 1
            entity_type = self._determine_entity_type()
            entity = Entity(entity_id, entity_type, self.entity_types[entity_type])
            entity.arrival_time = self.env.now
            
            self.metrics.record_arrival(entity, self.env.now)
            
            # Check for balking
            if self._check_balking(entity):
                self.metrics.record_balking(entity, self.env.now)
                continue
            
            # Start entity processing
            self.env.process(self._entity_process(entity))
    
    def _entity_arrivals_fixed(self):
        """Generate fixed number of entities."""
        for entity_id in range(1, self.num_entities + 1):
            entity_type = self._determine_entity_type()
            entity = Entity(entity_id, entity_type, self.entity_types[entity_type])
            entity.arrival_time = self.env.now
            
            self.metrics.record_arrival(entity, self.env.now)
            
            # Check for balking
            if self._check_balking(entity):
                self.metrics.record_balking(entity, self.env.now)
                continue
            
            # Start entity processing
            self.env.process(self._entity_process(entity))
            
            # Small delay between entity generations
            yield self.env.timeout(0.1)
    
    def _determine_entity_type(self) -> str:
        """Determine entity type based on probabilities."""
        rand = random.random()
        cumulative_prob = 0.0
        
        for entity_type, config in self.entity_types.items():
            cumulative_prob += config["probability"]
            if rand <= cumulative_prob:
                return entity_type
        
        # Fallback to first entity type
        return list(self.entity_types.keys())[0]
    
    def _check_balking(self, entity: Entity) -> bool:
        """Check if entity should balk (leave without service)."""
        for rule_name, rule in self.balking_rules.items():
            if rule["type"] == "queue_length":
                resource_name = rule["resource"]
                max_length = rule["max_length"]
                
                if resource_name in self.resources:
                    resource = self.resources[resource_name]
                    current_queue_length = len(resource.queue)
                    
                    # Apply priority multipliers
                    balk_threshold = max_length
                    if "priority_multipliers" in rule:
                        priority_str = str(entity.priority)
                        if priority_str in rule["priority_multipliers"]:
                            multiplier = rule["priority_multipliers"][priority_str]
                            balk_threshold = max_length * multiplier
                    
                    if current_queue_length >= balk_threshold:
                        return True
            
            elif rule["type"] == "probability":
                base_probability = rule["probability"]
                
                # Apply priority multipliers
                balk_probability = base_probability
                if "priority_multipliers" in rule:
                    priority_str = str(entity.priority)
                    if priority_str in rule["priority_multipliers"]:
                        multiplier = rule["priority_multipliers"][priority_str]
                        balk_probability = base_probability * multiplier
                
                if random.random() < balk_probability:
                    return True
        
        return False
    
    def _entity_process(self, entity: Entity):
        """Process entity through the system."""
        try:
            # Start with the initial processing steps
            steps_to_process = list(self.processing_steps)
            step_index = 0
            
            while step_index < len(steps_to_process):
                step_name = steps_to_process[step_index]
                entity.current_step = step_index
                
                # Apply pre-step routing rules
                actual_resource = self._apply_routing(entity, step_name)
                
                if actual_resource not in self.resources:
                    step_index += 1
                    continue
                
                # Process at resource
                yield from self._process_at_resource(entity, actual_resource)
                
                # Check if entity reneged during processing
                if entity.reneged:
                    return
                
                # Apply post-step routing to determine next steps
                next_steps = self._apply_after_routing(entity, actual_resource)
                
                if next_steps:
                    # Insert next steps after current position
                    for i, next_step in enumerate(reversed(next_steps)):
                        steps_to_process.insert(step_index + 1, next_step)
                
                step_index += 1
            
            # Entity completed all steps
            self.metrics.record_departure(entity, self.env.now)
            
        except Exception as e:
            # Entity processing failed
            pass
    
    def _apply_routing(self, entity: Entity, step_name: str) -> str:
        """Apply routing rules to determine actual resource."""
        # Check if there are routing rules for this step
        for routing_name, routing_config in self.routing_rules.items():
            # Skip "after_" routing rules - they're handled post-processing
            if routing_name.startswith("after_"):
                continue
                
            conditions = routing_config.get("conditions", [])
            default_destination = routing_config.get("default_destination", step_name)
            
            for condition in conditions:
                attribute = condition["attribute"]
                operator = condition.get("operator", "==")
                value = condition["value"]
                destination = condition["destination"]
                
                if attribute in entity.attributes:
                    entity_value = entity.attributes[attribute]
                    
                    if self._evaluate_condition(entity_value, operator, value):
                        return destination
            
            return default_destination
        
        return step_name
    
    def _apply_after_routing(self, entity: Entity, completed_step: str) -> List[str]:
        """Apply post-step routing rules to determine next processing steps."""
        after_key = f"after_{completed_step}"
        
        if after_key in self.routing_rules:
            routing_config = self.routing_rules[after_key]
            conditions = routing_config.get("conditions", [])
            default_destination = routing_config.get("default_destination")
            
            # Evaluate routing conditions
            for condition in conditions:
                attribute = condition["attribute"]
                operator = condition.get("operator", "==")
                value = condition["value"]
                destination = condition["destination"]
                
                if attribute in entity.attributes:
                    entity_value = entity.attributes[attribute]
                    
                    if self._evaluate_condition(entity_value, operator, value):
                        return [destination]
            
            # Use default destination if no conditions matched
            if default_destination:
                return [default_destination]
        
        # No routing rules found, continue with normal flow
        return []
    
    def _evaluate_condition(self, entity_value: Any, operator: str, condition_value: Any) -> bool:
        """Evaluate routing condition."""
        if operator == "==":
            return entity_value == condition_value
        elif operator == "!=":
            return entity_value != condition_value
        elif operator == ">":
            return entity_value > condition_value
        elif operator == "<":
            return entity_value < condition_value
        elif operator == ">=":
            return entity_value >= condition_value
        elif operator == "<=":
            return entity_value <= condition_value
        else:
            return False
    
    def _process_at_resource(self, entity: Entity, resource_name: str):
        """Process entity at a specific resource."""
        resource = self.resources[resource_name]
        
        # Determine service time
        service_time = self._get_service_time(entity, resource_name)
        
        # Request resource with priority (if supported)
        if hasattr(resource, 'request'):
            if isinstance(resource, (simpy.PriorityResource, simpy.PreemptiveResource)):
                request = resource.request(priority=entity.priority)
            else:
                request = resource.request()
        else:
            request = resource.request()
        
        # Handle reneging
        reneging_timeout = self._get_reneging_timeout(entity)
        
        if reneging_timeout:
            # Entity might renege
            result = yield request | self.env.timeout(reneging_timeout)
            
            if request.triggered:
                # Got the resource
                self.metrics.record_service_start(entity, resource_name, self.env.now)
                
                # Process the entity
                yield self.env.timeout(service_time)
                self.metrics.record_service_complete(entity, resource_name, self.env.now, service_time)
                
                resource.release(request)
            else:
                # Reneged
                entity.reneged = True
                self.metrics.record_reneging(entity, self.env.now)
                if request in resource.queue:
                    resource.queue.remove(request)
        else:
            # No reneging, standard processing
            yield request
            self.metrics.record_service_start(entity, resource_name, self.env.now)
            
            yield self.env.timeout(service_time)
            self.metrics.record_service_complete(entity, resource_name, self.env.now, service_time)
            
            resource.release(request)
    
    def _get_service_time(self, entity: Entity, resource_name: str) -> float:
        """Get service time for entity at resource."""
        processing_config = self.config.get("processing_rules", {})
        
        if resource_name in processing_config:
            resource_config = processing_config[resource_name]
            
            # Check for conditional distributions
            if "conditional_distributions" in resource_config:
                conditional_dists = resource_config["conditional_distributions"]
                if entity.type in conditional_dists:
                    return parse_distribution(conditional_dists[entity.type])()
            
            # Use default distribution
            if "distribution" in resource_config:
                return parse_distribution(resource_config["distribution"])()
        
        # Fallback to default
        return parse_distribution("uniform(1, 3)")()
    
    def _get_reneging_timeout(self, entity: Entity) -> Optional[float]:
        """Get reneging timeout for entity, if any."""
        for rule_name, rule in self.reneging_rules.items():
            if "abandon_time" in rule:
                base_timeout = parse_distribution(rule["abandon_time"])()
                
                # Apply priority multipliers
                if "priority_multipliers" in rule:
                    priority_str = str(entity.priority)
                    if priority_str in rule["priority_multipliers"]:
                        multiplier = rule["priority_multipliers"][priority_str]
                        return base_timeout * multiplier
                
                return base_timeout
        
        return None
    
    def _track_resource_utilization(self, resource_name: str):
        """Track resource utilization over time."""
        # This method is no longer needed - we'll calculate utilization 
        # based on actual simulation run time and busy time
        return
        yield  # Make it a generator for compatibility
