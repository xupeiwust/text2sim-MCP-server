"""
Discrete-Event Simulation (DES) tools for MCP server.

This module implements DES-specific simulation tools using SimPy integration
with comprehensive schema validation and statistical analysis capabilities.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import random
import time

from ..shared.error_handlers import MCPErrorHandler
from ..shared.response_builders import ResponseBuilder
from DES.schema_validator import DESConfigValidator


def _generate_des_quick_fixes(errors: List[str]) -> List[str]:
    """Generate DES-specific quick fix suggestions based on error patterns."""
    fixes = []

    for error in errors:
        if "wait_times" in error and "collect_wait_times" not in error:
            fixes.append("Replace 'wait_times' with 'collect_wait_times' in statistics section")
        elif "resource_utilization" in error:
            fixes.append("Replace 'resource_utilization' with 'collect_utilization' in statistics section")
        elif "abandon_time" in error and "required property" in error:
            fixes.append("Add 'abandon_time': 'normal(30, 10)' to reneging rules (use distribution string)")
        elif "mtbf" in error and "not of type 'string'" in error:
            fixes.append("Change MTBF to distribution string: 'exp(300)' instead of 300")
        elif "conditions" in error and "required property" in error:
            fixes.append("Use 'conditions' array in simple_routing, not 'from_step'/'to_step'")
        elif "probabilities sum to" in error:
            fixes.append("Adjust entity_types probabilities to sum exactly to 1.0")
        elif "does not match" in error and "distribution" in error:
            fixes.append("Fix distribution format: use 'uniform(5,10)', 'normal(8,2)', or 'exp(5)'")
        elif "Additional properties are not allowed" in error:
            fixes.append("Check for typos in property names or unsupported properties")
        elif "resource" in error and "not found" in error:
            fixes.append("Ensure resource names in rules match those defined in 'resources' section")

    # Add generic helpful tips if no specific fixes found
    if not fixes:
        fixes.extend([
            "Check property names for typos",
            "Ensure all distributions are strings: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'",
            "Verify resource names match between sections",
            "Confirm entity probabilities sum to 1.0"
        ])

    return fixes[:3]  # Limit to top 3 most relevant fixes


def register_des_tools(mcp: FastMCP) -> None:
    """Register all DES-related MCP tools."""

    @mcp.tool()
    def simulate_des(config: dict) -> dict:
        """
        Advanced discrete-event simulation with comprehensive schema validation and SimPy integration.

        QUICK START - Basic Configuration:
        {
          "run_time": 480,
          "arrival_pattern": {"distribution": "exp(5)"},
          "entity_types": {
            "customer": {"probability": 1.0, "value": {"min": 10, "max": 50}, "priority": 5}
          },
          "resources": {
            "server": {"capacity": 1, "resource_type": "fifo"}
          },
          "processing_rules": {
            "steps": ["server"],
            "server": {"distribution": "uniform(3, 7)"}
          }
        }

        COMMON CONFIGURATION PATTERNS:

        Statistics Collection:
        "statistics": {
          "collect_wait_times": true,
          "collect_utilization": true,
          "collect_queue_lengths": false,
          "warmup_period": 60
        }

        Balking (Customers Leave):
        "balking_rules": {
          "overcrowding": {"type": "queue_length", "resource": "server_name", "max_length": 8}
        }

        Reneging (Customers Abandon Queue):
        "reneging_rules": {
          "impatience": {
            "abandon_time": "normal(30, 10)",
            "priority_multipliers": {"1": 5.0, "5": 1.0, "10": 0.3}
          }
        }

        Resource Failures:
        "basic_failures": {
          "machine_name": {
            "mtbf": "exp(480)",
            "repair_time": "uniform(20, 40)"
          }
        }

        Conditional Routing:
        "simple_routing": {
          "priority_check": {
            "conditions": [
              {"attribute": "priority", "operator": "<=", "value": 2, "destination": "express_lane"}
            ],
            "default_destination": "regular_service"
          }
        }

        Custom Metrics Names:
        "metrics": {
          "arrival_metric": "customers_arrived",
          "served_metric": "customers_served",
          "value_metric": "total_revenue"
        }

        DISTRIBUTION FORMATS (All strings):
        - "uniform(5, 10)" - Uniform between 5 and 10
        - "normal(8, 2)" - Normal with mean=8, std=2
        - "exp(5)" - Exponential with mean=5 (NOT rate=5)
        - "gauss(10, 3)" - Same as normal

        RESOURCE TYPES:
        - "fifo" - First-in-first-out (default)
        - "priority" - Priority queue (1=highest, 10=lowest)
        - "preemptive" - Priority with preemption capability

        ENTITY CONFIGURATION:
        "entity_types": {
          "vip": {
            "probability": 0.2,           // Must sum to 1.0 across all types
            "priority": 1,                // 1=highest, 10=lowest
            "value": {"min": 100, "max": 500},
            "attributes": {"membership": "gold", "urgent": true}  // For routing
          }
        }

        PROCESSING FLOW:
        "processing_rules": {
          "steps": ["reception", "service", "checkout"],  // Sequential steps
          "reception": {"distribution": "uniform(2, 5)"},
          "service": {
            "distribution": "normal(10, 2)",              // Default for all entities
            "conditional_distributions": {               // Override by entity type
              "vip": "normal(5, 1)",
              "regular": "normal(12, 3)"
            }
          }
        }

        COMMON MISTAKES TO AVOID:
        - Don't use "wait_times" → Use "collect_wait_times"
        - Don't use numbers for distributions → Use strings like "exp(300)"
        - Don't use "from_step"/"to_step" → Use "conditions" array in routing
        - Don't forget "abandon_time" in reneging_rules
        - Ensure probabilities sum to exactly 1.0
        - Resource names in steps must match resource definitions

        PRO TIPS:
        - Start simple, add complexity gradually
        - Use priority 1-3 for urgent, 4-6 for normal, 7-10 for low priority
        - Set warmup_period to exclude initial transient behavior
        - Use conditional_distributions for different entity types
        - Resource failures use resource names as keys, not separate "resource" field

        COMPLETE MANUFACTURING EXAMPLE:
        {
          "run_time": 960,
          "entity_types": {
            "standard": {"probability": 0.6, "value": {"min": 400, "max": 400}, "priority": 5},
            "premium": {"probability": 0.1, "value": {"min": 1200, "max": 1200}, "priority": 1}
          },
          "resources": {
            "inspection": {"capacity": 2, "resource_type": "priority"},
            "assembly": {"capacity": 4, "resource_type": "priority"}
          },
          "processing_rules": {
            "steps": ["inspection", "assembly"],
            "inspection": {"distribution": "uniform(3, 7)"},
            "assembly": {
              "conditional_distributions": {
                "standard": "uniform(20, 30)",
                "premium": "uniform(35, 50)"
              }
            }
          },
          "balking_rules": {
            "overcrowding": {"type": "queue_length", "resource": "inspection", "max_length": 12}
          },
          "basic_failures": {
            "assembly": {"mtbf": "exp(300)", "repair_time": "uniform(20, 40)"}
          },
          "arrival_pattern": {"distribution": "uniform(8, 15)"}
        }

        Returns simulation results with counts, efficiency metrics, utilization, and wait times.
        Validation errors include helpful suggestions and examples for quick correction.
        """
        try:
            # Validate and normalize configuration
            validator = DESConfigValidator()
            normalized_config, errors = validator.validate_and_normalize(config)

            if errors:
                return MCPErrorHandler.validation_error(
                    errors,
                    _generate_des_quick_fixes(errors),
                    "Common issues: Check property names, ensure distributions are strings, verify probabilities sum to 1.0"
                )

            # Import and run simulation
            from DES.simulator import SimulationModel

            model = SimulationModel(normalized_config)
            results = model.run()

            return ResponseBuilder.simulation_response(
                success=True,
                results=results,
                model_info={
                    "simulation_type": "DES",
                    "run_time": normalized_config.get("run_time", "Unknown"),
                    "entity_types": len(normalized_config.get("entity_types", {})),
                    "resources": len(normalized_config.get("resources", {}))
                }
            )

        except ImportError:
            # Fallback to old system during transition
            try:
                from DES.des_utils import run_simulation
                return run_simulation(config)
            except Exception as fallback_error:
                return MCPErrorHandler.simulation_error(
                    f"Both new and legacy simulation systems failed: {str(fallback_error)}",
                    ["Check DES module installation", "Verify configuration format"]
                )

        except Exception as e:
            return MCPErrorHandler.simulation_error(
                str(e),
                ["Check configuration format", "Verify all required fields are present"]
            )

    @mcp.tool()
    def run_multiple_simulations(
        config: dict,
        replications: int = 10,
        random_seed_base: Optional[int] = None,
        confidence_levels: Optional[List[float]] = None
    ) -> dict:
        """
        Run multiple independent simulation replications with comprehensive statistical analysis.

        This tool provides industry-standard statistical reporting for simulation results,
        including confidence intervals, variability measures, and distribution analysis.
        Essential for reliable decision-making and professional simulation studies.

        Statistical Outputs Include:
        - Central tendency: Mean, median, mode
        - Variability: Standard deviation, coefficient of variation, range
        - Confidence intervals: 90%, 95%, 99% (configurable)
        - Distribution analysis: Percentiles, normality tests, outlier detection
        - Sample statistics: Standard error, degrees of freedom, relative precision

        Industry Standard Format:
        Results reported as "Mean ± Half-Width (CI%) [n=replications]"
        Example: "Utilization: 0.785 ± 0.023 (95%) [n=20]"

        Args:
            config: Complete simulation configuration (same as simulate_des)
            replications: Number of independent runs (default: 10, minimum: 2)
            random_seed_base: Base seed for reproducible results (optional)
            confidence_levels: List of confidence levels (default: [0.90, 0.95, 0.99])

        Returns:
            Comprehensive statistical analysis with individual replication data
        """
        try:
            # Validate inputs
            if replications < 2:
                return MCPErrorHandler.parameter_error(
                    "replications", replications, "integer >= 2",
                    "2 to 100 replications"
                )

            if replications > 100:
                return MCPErrorHandler.parameter_error(
                    "replications", replications, "integer <= 100",
                    "2 to 100 replications"
                )

            # Set up confidence levels
            if confidence_levels is None:
                confidence_levels = [0.90, 0.95, 0.99]

            # Validate configuration
            validator = DESConfigValidator()
            normalized_config, errors = validator.validate_and_normalize(config)

            if errors:
                return MCPErrorHandler.validation_error(
                    errors,
                    ["Fix configuration errors before running replications"]
                )

            # Set up random seeds for reproducibility
            if random_seed_base is None:
                random_seed_base = int(time.time())

            # Run replications
            replication_results = []
            failed_replications = []

            for i in range(replications):
                try:
                    # Set unique seed for this replication
                    replication_seed = random_seed_base + i * 1000
                    random.seed(replication_seed)

                    # Run single simulation
                    result = simulate_des(normalized_config)

                    if "error" in result:
                        failed_replications.append({
                            "replication": i + 1,
                            "error": result["error"],
                            "seed": replication_seed
                        })
                    else:
                        # Add replication metadata
                        result["_replication_info"] = {
                            "replication_number": i + 1,
                            "random_seed": replication_seed,
                            "timestamp": time.time()
                        }
                        replication_results.append(result)

                except Exception as e:
                    failed_replications.append({
                        "replication": i + 1,
                        "error": str(e),
                        "seed": replication_seed
                    })

            # Check if we have enough successful replications
            successful_count = len(replication_results)
            if successful_count < 2:
                return MCPErrorHandler.simulation_error(
                    f"Only {successful_count} successful replications out of {replications}",
                    ["Check simulation configuration", "Reduce model complexity", "Verify resource constraints"]
                )

            # Perform statistical analysis
            try:
                from DES.replication_analysis import create_replication_analyzer
                analyzer = create_replication_analyzer()
                statistical_analysis = analyzer.analyze_replications(replication_results)
                summary_report = analyzer.format_industry_summary(statistical_analysis)

                return ResponseBuilder.statistical_response(
                    analysis=statistical_analysis,
                    summary_report=summary_report,
                    execution_info={
                        "total_replications_requested": replications,
                        "successful_replications": successful_count,
                        "failed_replications": len(failed_replications),
                        "random_seed_base": random_seed_base,
                        "confidence_levels": confidence_levels
                    }
                )

            except ImportError:
                return MCPErrorHandler.dependency_error(
                    ["DES replication analysis module"],
                    ["pip install scipy numpy for statistical analysis"]
                )

        except Exception as e:
            return MCPErrorHandler.simulation_error(
                f"Multiple replications failed: {str(e)}",
                ["Check configuration format", "Try with fewer replications", "Verify DES module installation"]
            )