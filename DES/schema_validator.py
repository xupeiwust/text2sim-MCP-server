"""
Schema validation for DES configurations using JSON Schema 2020-12.

This module provides comprehensive validation and normalization of DES simulation
configurations, ensuring they conform to the SimPy-compatible schema.
"""

import json
import jsonschema
import re
from pathlib import Path
from typing import Dict, Any, Tuple, List
from collections import defaultdict


class DESConfigValidator:
    """
    Validates and normalizes DES simulation configurations using JSON Schema.
    
    Provides:
    - Schema validation against SimPy-compatible JSON Schema
    - Business rule validation (probabilities sum to 1.0, etc.)
    - Configuration normalization with defaults
    - Clear error messages for invalid configurations
    """
    
    def __init__(self):
        """Load the SimPy-compatible schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "DES" / "des-simpy-compatible-schema.json"
        try:
            with open(schema_path) as f:
                self.schema = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
    
    def validate_and_normalize(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Validate configuration and return normalized version with any errors.
        
        Args:
            config: Raw configuration dictionary
            
        Returns:
            Tuple of (normalized_config, error_list)
        """
        errors = []
        
        try:
            # Apply defaults from schema
            normalized = self._apply_defaults(config.copy())
            
            # Validate against JSON schema
            jsonschema.validate(normalized, self.schema)
            
            # Additional business logic validation
            errors.extend(self._validate_business_rules(normalized))
            
            return normalized, errors
            
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {self._format_schema_error(e)}")
            return config, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return config, errors
    
    def _apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply schema defaults to configuration.
        
        This handles optional fields that have default values in the schema.
        """
        # Apply resource defaults
        if "resources" in config:
            for resource_name, resource_config in config["resources"].items():
                if "resource_type" not in resource_config:
                    resource_config["resource_type"] = "fifo"
        
        # Apply entity type defaults
        if "entity_types" in config:
            for entity_name, entity_config in config["entity_types"].items():
                if "priority" not in entity_config:
                    entity_config["priority"] = 5
        
        # Apply statistics defaults
        if "statistics" not in config:
            config["statistics"] = {}
        stats = config["statistics"]
        if "collect_wait_times" not in stats:
            stats["collect_wait_times"] = True
        if "collect_queue_lengths" not in stats:
            stats["collect_queue_lengths"] = False
        if "collect_utilization" not in stats:
            stats["collect_utilization"] = True
        if "warmup_period" not in stats:
            stats["warmup_period"] = 0
        
        # Apply metrics defaults
        if "metrics" not in config:
            config["metrics"] = {}
        metrics = config["metrics"]
        if "arrival_metric" not in metrics:
            metrics["arrival_metric"] = "entities_arrived"
        if "served_metric" not in metrics:
            metrics["served_metric"] = "entities_served"
        if "balk_metric" not in metrics:
            metrics["balk_metric"] = "entities_balked"
        if "reneged_metric" not in metrics:
            metrics["reneged_metric"] = "entities_reneged"
        if "value_metric" not in metrics:
            metrics["value_metric"] = "total_value"
        
        return config
    
    def _validate_business_rules(self, config: Dict[str, Any]) -> List[str]:
        """
        Additional validation beyond JSON schema.
        
        Validates business logic constraints that can't be expressed in JSON Schema.
        """
        errors = []
        
        # Check probabilities sum to 1.0
        if "entity_types" in config:
            total_prob = sum(et["probability"] for et in config["entity_types"].values())
            if abs(total_prob - 1.0) > 0.001:
                errors.append(
                    f"Entity type probabilities sum to {total_prob:.3f}, should be 1.0. "
                    f"Please adjust probabilities to sum exactly to 1.0."
                )
        
        # Validate resource references in processing rules
        if "processing_rules" in config and "resources" in config:
            resource_names = set(config["resources"].keys())
            processing_steps = config["processing_rules"].get("steps", [])
            
            for step in processing_steps:
                if step not in resource_names and step not in config["processing_rules"]:
                    errors.append(
                        f"Processing step '{step}' not found in resources or processing rules. "
                        f"Available resources: {', '.join(sorted(resource_names))}"
                    )
        
        # Validate resource references in balking rules
        if "balking_rules" in config and "resources" in config:
            resource_names = set(config["resources"].keys())
            for rule_name, rule in config["balking_rules"].items():
                if rule.get("type") in ["queue_length", "wait_time"] and "resource" in rule:
                    if rule["resource"] not in resource_names:
                        errors.append(
                            f"Balking rule '{rule_name}' references unknown resource '{rule['resource']}'. "
                            f"Available resources: {', '.join(sorted(resource_names))}"
                        )
        
        # Validate distribution strings
        errors.extend(self._validate_distributions(config))
        
        # Validate value ranges
        if "entity_types" in config:
            for entity_name, entity_config in config["entity_types"].items():
                if "value" in entity_config:
                    value_config = entity_config["value"]
                    if value_config["min"] > value_config["max"]:
                        errors.append(
                            f"Entity type '{entity_name}' has min value ({value_config['min']}) "
                            f"greater than max value ({value_config['max']})"
                        )
        
        return errors
    
    def _validate_distributions(self, config: Dict[str, Any]) -> List[str]:
        """Validate distribution string formats."""
        errors = []
        distribution_pattern = re.compile(r'^(uniform|normal|gauss|exp)\s*\(\s*[0-9.]+\s*(,\s*[0-9.]+\s*)?\)$')
        
        # Check arrival pattern
        if "arrival_pattern" in config:
            dist = config["arrival_pattern"].get("distribution", "")
            if not distribution_pattern.match(dist):
                errors.append(
                    f"Invalid arrival pattern distribution '{dist}'. "
                    f"Expected format: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'"
                )
        
        # Check processing rules distributions
        if "processing_rules" in config:
            for step_name, step_config in config["processing_rules"].items():
                if step_name == "steps":
                    continue
                    
                if "distribution" in step_config:
                    dist = step_config["distribution"]
                    if not distribution_pattern.match(dist):
                        errors.append(
                            f"Invalid processing rule distribution for '{step_name}': '{dist}'. "
                            f"Expected format: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'"
                        )
                
                if "conditional_distributions" in step_config:
                    for entity_type, dist in step_config["conditional_distributions"].items():
                        if not distribution_pattern.match(dist):
                            errors.append(
                                f"Invalid conditional distribution for '{step_name}' -> '{entity_type}': '{dist}'. "
                                f"Expected format: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'"
                            )
        
        # Check reneging rules
        if "reneging_rules" in config:
            for rule_name, rule in config["reneging_rules"].items():
                if "abandon_time" in rule:
                    dist = rule["abandon_time"]
                    if not distribution_pattern.match(dist):
                        errors.append(
                            f"Invalid reneging abandon_time for '{rule_name}': '{dist}'. "
                            f"Expected format: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'"
                        )
        
        # Check basic failures
        if "basic_failures" in config:
            for resource_name, failure_config in config["basic_failures"].items():
                for field in ["mtbf", "repair_time"]:
                    if field in failure_config:
                        dist = failure_config[field]
                        if not distribution_pattern.match(dist):
                            errors.append(
                                f"Invalid {field} distribution for resource '{resource_name}': '{dist}'. "
                                f"Expected format: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'"
                            )
        
        return errors
    
    def _format_schema_error(self, error: jsonschema.ValidationError) -> str:
        """
        Format JSON schema validation errors into user-friendly messages with examples.
        """
        path = " -> ".join(str(p) for p in error.path) if error.path else "root"
        base_message = f"At '{path}': {error.message}"
        
        # Generate helpful suggestions based on common error patterns
        suggestion = self._get_error_suggestion(error, path)
        
        if suggestion:
            return f"{base_message}\n💡 Suggestion: {suggestion['tip']}\n📋 Example: {json.dumps(suggestion['example'], indent=2)}"
        else:
            return base_message
    
    def _get_error_suggestion(self, error: jsonschema.ValidationError, path: str) -> Dict[str, Any]:
        """Generate helpful suggestions for common schema validation errors."""
        
        # Map of common error patterns to helpful examples
        error_suggestions = {
            # Statistics section errors
            "statistics": {
                "pattern": "Additional properties are not allowed",
                "tip": "Statistics section uses specific property names. Common mistake: 'wait_times' should be 'collect_wait_times'",
                "example": {
                    "statistics": {
                        "collect_wait_times": True,
                        "collect_utilization": True,
                        "collect_queue_lengths": False,
                        "warmup_period": 60
                    }
                }
            },
            
            # Reneging rules errors
            "reneging_rules": {
                "pattern": "'abandon_time' is a required property",
                "tip": "Reneging rules require 'abandon_time' as a distribution string, not a number",
                "example": {
                    "customer_impatience": {
                        "abandon_time": "normal(30, 10)",
                        "priority_multipliers": {"1": 3.0, "5": 1.0, "10": 0.5}
                    }
                }
            },
            
            # Basic failures errors  
            "basic_failures": {
                "pattern": "is not of type 'string'",
                "tip": "Failure times must be distribution strings, not numbers. Use 'exp(300)' instead of 300",
                "example": {
                    "resource_name": {
                        "mtbf": "exp(480)",
                        "repair_time": "uniform(20, 40)"
                    }
                }
            },
            
            # Simple routing errors
            "simple_routing": {
                "pattern": "'conditions' is a required property",
                "tip": "Simple routing requires 'conditions' array, not 'from_step'/'to_step' properties",
                "example": {
                    "quality_check": {
                        "conditions": [
                            {"attribute": "priority", "operator": "<=", "value": 2, "destination": "express_lane"}
                        ],
                        "default_destination": "regular_service"
                    }
                }
            },
            
            # Distribution format errors
            "distribution": {
                "pattern": "does not match",
                "tip": "Distributions must be formatted as 'type(params)'. Examples: 'uniform(5,10)', 'normal(8,2)', 'exp(5)'",
                "example": {
                    "valid_distributions": [
                        "uniform(1, 10)",
                        "normal(5, 1.5)", 
                        "exp(3)",
                        "gauss(10, 2)"
                    ]
                }
            },
            
            # Entity types probability errors
            "entity_types": {
                "pattern": "probability",
                "tip": "Entity type probabilities must sum to exactly 1.0",
                "example": {
                    "standard": {"probability": 0.7, "value": {"min": 100, "max": 200}, "priority": 5},
                    "premium": {"probability": 0.3, "value": {"min": 500, "max": 1000}, "priority": 2}
                }
            },
            
            # Resource type errors
            "resources": {
                "pattern": "resource_type",
                "tip": "Resource type must be one of: 'fifo', 'priority', 'preemptive'",
                "example": {
                    "server": {"capacity": 2, "resource_type": "priority"},
                    "machine": {"capacity": 1, "resource_type": "fifo"}
                }
            }
        }
        
        # Find matching suggestion based on path and error message
        for section_key, suggestion in error_suggestions.items():
            if (section_key in path.lower() and 
                (suggestion["pattern"] in error.message or section_key in error.message.lower())):
                return suggestion
        
        # Generic suggestions based on error message patterns
        if "Additional properties are not allowed" in error.message:
            return {
                "tip": "Check property names against the schema. Common issues: typos, wrong section, or unsupported properties",
                "example": {"note": "Refer to schema documentation for valid properties"}
            }
        elif "is a required property" in error.message:
            return {
                "tip": "This section is missing a required property. Check the schema for required fields",
                "example": {"note": "Add the missing required property to this section"}
            }
        elif "is not of type" in error.message:
            return {
                "tip": "Wrong data type. Check if you're using a string where a number is expected, or vice versa",
                "example": {"note": "Verify the expected data type in the schema"}
            }
        
        return None
    
    def get_schema_examples(self) -> List[Dict[str, Any]]:
        """
        Get example configurations from the schema.
        
        Returns:
            List of example configurations
        """
        return self.schema.get("examples", [])
    
    def validate_quick(self, config: Dict[str, Any]) -> bool:
        """
        Quick validation check without normalization.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            jsonschema.validate(config, self.schema)
            _, errors = self.validate_and_normalize(config)
            return len(errors) == 0
        except:
            return False
