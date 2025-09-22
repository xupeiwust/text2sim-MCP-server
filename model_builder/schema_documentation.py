"""
Schema Documentation Provider for Text2Sim Model Builder.

This module provides dynamic schema help and documentation with flexible path resolution,
LLM-optimized responses, and comprehensive examples for AI assistant comprehension.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from .schema_registry import schema_registry


@dataclass
class SchemaSection:
    """Information about a specific schema section."""
    path: str
    description: str
    required: bool
    schema_type: str
    structure: Dict[str, Any]
    validation_rules: List[str]
    examples: List[Dict[str, Any]]
    related_sections: List[str]
    common_patterns: List[str]


class SchemaDocumentationProvider:
    """
    Dynamic schema documentation and help system.
    
    Provides flexible path resolution, comprehensive examples, and LLM-optimized
    responses for any registered simulation schema.
    """
    
    def __init__(self):
        """Initialize the schema documentation provider."""
        self.registry = schema_registry
        self._examples_cache = {}
        self._documentation_cache = {}
        self._initialize_examples()
    
    def _initialize_examples(self):
        """Initialize comprehensive examples for different schema sections."""
        self._examples_cache = {
            "DES": {
                "entity_types": [
                    {
                        "title": "Healthcare Triage",
                        "description": "Emergency and routine patients with priorities",
                        "example": {
                            "emergency": {
                                "probability": 0.1,
                                "priority": 1,
                                "value": {"min": 2000, "max": 5000},
                                "attributes": {"severity": "critical", "insurance": "premium"}
                            },
                            "urgent": {
                                "probability": 0.3,
                                "priority": 3,
                                "value": {"min": 500, "max": 2000},
                                "attributes": {"severity": "moderate"}
                            },
                            "routine": {
                                "probability": 0.6,
                                "priority": 7,
                                "value": {"min": 100, "max": 500},
                                "attributes": {"severity": "low"}
                            }
                        }
                    },
                    {
                        "title": "Manufacturing Jobs",
                        "description": "Different product types with varying processing needs",
                        "example": {
                            "standard": {
                                "probability": 0.7,
                                "priority": 5,
                                "value": {"min": 400, "max": 400},
                                "attributes": {"product_type": "standard", "quality_check": "basic"}
                            },
                            "premium": {
                                "probability": 0.2,
                                "priority": 2,
                                "value": {"min": 1200, "max": 1200},
                                "attributes": {"product_type": "premium", "quality_check": "detailed"}
                            },
                            "custom": {
                                "probability": 0.1,
                                "priority": 1,
                                "value": {"min": 2500, "max": 3000},
                                "attributes": {"product_type": "custom", "quality_check": "comprehensive"}
                            }
                        }
                    },
                    {
                        "title": "Service Customers",
                        "description": "Customer segments with different service levels",
                        "example": {
                            "vip": {
                                "probability": 0.15,
                                "priority": 1,
                                "value": {"min": 200, "max": 1000},
                                "attributes": {"membership": "platinum", "express_service": True}
                            },
                            "regular": {
                                "probability": 0.85,
                                "priority": 5,
                                "value": {"min": 20, "max": 100},
                                "attributes": {"membership": "standard"}
                            }
                        }
                    }
                ],
                "resources": [
                    {
                        "title": "Hospital Resources",
                        "description": "Medical staff and equipment with different capabilities",
                        "example": {
                            "triage_nurse": {
                                "capacity": 2,
                                "resource_type": "priority"
                            },
                            "doctor": {
                                "capacity": 5,
                                "resource_type": "preemptive"
                            },
                            "specialist": {
                                "capacity": 1,
                                "resource_type": "preemptive"
                            },
                            "discharge_desk": {
                                "capacity": 1,
                                "resource_type": "fifo"
                            }
                        }
                    },
                    {
                        "title": "Manufacturing Resources",
                        "description": "Production equipment with different capabilities",
                        "example": {
                            "inspection": {
                                "capacity": 3,
                                "resource_type": "fifo"
                            },
                            "assembly_line": {
                                "capacity": 4,
                                "resource_type": "priority"
                            },
                            "quality_control": {
                                "capacity": 2,
                                "resource_type": "priority"
                            },
                            "packaging": {
                                "capacity": 2,
                                "resource_type": "fifo"
                            }
                        }
                    }
                ],
                "processing_rules": [
                    {
                        "title": "Healthcare Flow",
                        "description": "Patient processing through medical departments",
                        "example": {
                            "steps": ["triage_nurse", "doctor", "discharge_desk"],
                            "triage_nurse": {
                                "distribution": "uniform(3, 7)",
                                "conditional_distributions": {
                                    "emergency": "uniform(1, 3)",
                                    "routine": "uniform(5, 10)"
                                }
                            },
                            "doctor": {
                                "distribution": "normal(20, 5)",
                                "conditional_distributions": {
                                    "emergency": "normal(45, 15)",
                                    "urgent": "normal(25, 8)",
                                    "routine": "normal(15, 5)"
                                }
                            },
                            "discharge_desk": {
                                "distribution": "uniform(5, 10)"
                            }
                        }
                    },
                    {
                        "title": "Manufacturing Flow",
                        "description": "Product processing through production stages",
                        "example": {
                            "steps": ["inspection", "assembly_line", "quality_control", "packaging"],
                            "inspection": {
                                "distribution": "uniform(2, 5)"
                            },
                            "assembly_line": {
                                "distribution": "normal(15, 3)",
                                "conditional_distributions": {
                                    "standard": "normal(12, 2)",
                                    "premium": "normal(20, 4)",
                                    "custom": "normal(35, 8)"
                                }
                            },
                            "quality_control": {
                                "distribution": "uniform(8, 12)",
                                "conditional_distributions": {
                                    "premium": "uniform(12, 18)",
                                    "custom": "uniform(15, 25)"
                                }
                            },
                            "packaging": {
                                "distribution": "uniform(3, 6)"
                            }
                        }
                    }
                ],
                "balking_rules": [
                    {
                        "title": "Queue Length Balking",
                        "description": "Customers leave when queues get too long",
                        "example": {
                            "overcrowding": {
                                "type": "queue_length",
                                "resource": "reception",
                                "max_length": 10,
                                "priority_multipliers": {
                                    "1": 0.1,
                                    "5": 1.0,
                                    "10": 2.0
                                }
                            }
                        }
                    },
                    {
                        "title": "Probability Balking",
                        "description": "Random customer balking on arrival",
                        "example": {
                            "random_balking": {
                                "type": "probability",
                                "probability": 0.05
                            }
                        }
                    }
                ],
                "reneging_rules": [
                    {
                        "title": "Patient Impatience",
                        "description": "Patients abandon queues after waiting too long",
                        "example": {
                            "patient_impatience": {
                                "abandon_time": "normal(30, 10)",
                                "priority_multipliers": {
                                    "1": 5.0,
                                    "3": 2.0,
                                    "7": 1.0
                                }
                            }
                        }
                    }
                ],
                "simple_routing": [
                    {
                        "title": "Priority-Based Routing",
                        "description": "Route entities based on priority levels",
                        "example": {
                            "priority_routing": {
                                "conditions": [
                                    {"attribute": "priority", "operator": "<=", "value": 2, "destination": "express_lane"},
                                    {"attribute": "priority", "operator": "<=", "value": 5, "destination": "regular_service"}
                                ],
                                "default_destination": "standard_service"
                            }
                        }
                    },
                    {
                        "title": "Attribute-Based Routing",
                        "description": "Route based on custom entity attributes",
                        "example": {
                            "membership_routing": {
                                "conditions": [
                                    {"attribute": "membership", "operator": "==", "value": "platinum", "destination": "vip_service"},
                                    {"attribute": "insurance", "operator": "==", "value": "premium", "destination": "premium_care"}
                                ],
                                "default_destination": "standard_care"
                            }
                        }
                    }
                ],
                "basic_failures": [
                    {
                        "title": "Equipment Failures",
                        "description": "Resource breakdowns and repair cycles",
                        "example": {
                            "assembly_machine": {
                                "mtbf": "exp(480)",
                                "repair_time": "uniform(30, 60)"
                            },
                            "quality_scanner": {
                                "mtbf": "exp(720)",
                                "repair_time": "normal(45, 15)"
                            }
                        }
                    }
                ],
                "statistics": [
                    {
                        "title": "Comprehensive Statistics",
                        "description": "Full statistics collection with warmup period",
                        "example": {
                            "collect_wait_times": True,
                            "collect_queue_lengths": True,
                            "collect_utilization": True,
                            "warmup_period": 120
                        }
                    }
                ],
                "metrics": [
                    {
                        "title": "Healthcare Metrics",
                        "description": "Medical terminology for simulation results",
                        "example": {
                            "arrival_metric": "patients_arrived",
                            "served_metric": "patients_treated",
                            "balk_metric": "patients_left_immediately",
                            "reneged_metric": "patients_abandoned_queue",
                            "value_metric": "total_treatment_revenue"
                        }
                    },
                    {
                        "title": "Manufacturing Metrics",
                        "description": "Production terminology for simulation results",
                        "example": {
                            "arrival_metric": "jobs_received",
                            "served_metric": "products_completed",
                            "balk_metric": "jobs_rejected",
                            "reneged_metric": "jobs_cancelled",
                            "value_metric": "total_production_value"
                        }
                    }
                ]
            },
            "SD": {
                "description": "System Dynamics models using PySD-compatible Abstract Model JSON schema - CRITICAL: Each variable must be its own element",
                "schema_overview": {
                    "title": "PySD Abstract Model Schema Structure - Corrected",
                    "description": "SD models use abstractModel → sections → elements hierarchy where EACH VARIABLE IS ITS OWN ELEMENT",
                    "key_principle": "ONE ELEMENT PER VARIABLE - Element name becomes the variable name that can be referenced in equations",
                    "required_structure": {
                        "abstractModel": {
                            "originalPath": "string (required)",
                            "sections": [
                                {
                                    "name": "__main__ (required for main section)",
                                    "type": "main|macro|module",
                                    "path": "/ (required)",
                                    "params": "array (required)",
                                    "returns": "array (required)",
                                    "subscripts": "array (required)",
                                    "constraints": "array (required)",
                                    "testInputs": "array (required)",
                                    "split": "boolean (required)",
                                    "viewsDict": "object (required)",
                                    "elements": [
                                        {
                                            "name": "variable_name_1",
                                            "components": [
                                                "Single component defining computation"
                                            ],
                                            "units": "optional units",
                                            "limits": "optional [min, max]",
                                            "documentation": "optional description"
                                        },
                                        {
                                            "name": "variable_name_2",
                                            "components": [
                                                "Single component defining computation"
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                },
                "complete_examples": [
                    {
                        "title": "Population Model - CORRECTED Structure",
                        "description": "Demonstrates ONE ELEMENT PER VARIABLE - each variable gets its own element",
                        "example": {
                            "abstractModel": {
                                "originalPath": "population_growth.json",
                                "sections": [
                                    {
                                        "name": "__main__",
                                        "type": "main",
                                        "path": "/",
                                        "params": [],
                                        "returns": [],
                                        "subscripts": [],
                                        "constraints": [],
                                        "testInputs": [],
                                        "split": False,
                                        "viewsDict": {},
                                        "elements": [
                                            {
                                                "name": "population",
                                                "components": [
                                                    {
                                                        "type": "Stock",
                                                        "subtype": "Normal",
                                                        "subscripts": [[], []],
                                                        "ast": {
                                                            "syntaxType": "IntegStructure",
                                                            "flow": {
                                                                "syntaxType": "ArithmeticStructure",
                                                                "operators": ["-"],
                                                                "arguments": [
                                                                    {
                                                                        "syntaxType": "ReferenceStructure",
                                                                        "reference": "birth_rate"
                                                                    },
                                                                    {
                                                                        "syntaxType": "ReferenceStructure",
                                                                        "reference": "death_rate"
                                                                    }
                                                                ]
                                                            },
                                                            "initial": {
                                                                "syntaxType": "ReferenceStructure",
                                                                "reference": "1000"
                                                            }
                                                        }
                                                    }
                                                ],
                                                "units": "people",
                                                "limits": [0, None],
                                                "documentation": "Total population stock"
                                            },
                                            {
                                                "name": "birth_rate",
                                                "components": [
                                                    {
                                                        "type": "Flow",
                                                        "subtype": "Normal",
                                                        "subscripts": [[], []],
                                                        "ast": {
                                                            "syntaxType": "ArithmeticStructure",
                                                            "operators": ["*"],
                                                            "arguments": [
                                                                {
                                                                    "syntaxType": "ReferenceStructure",
                                                                    "reference": "population"
                                                                },
                                                                {
                                                                    "syntaxType": "ReferenceStructure",
                                                                    "reference": "birth_rate_fraction"
                                                                }
                                                            ]
                                                        }
                                                    }
                                                ],
                                                "units": "people/year",
                                                "documentation": "Rate of births"
                                            },
                                            {
                                                "name": "birth_rate_fraction",
                                                "components": [
                                                    {
                                                        "type": "Auxiliary",
                                                        "subtype": "Normal",
                                                        "subscripts": [[], []],
                                                        "ast": {
                                                            "syntaxType": "ReferenceStructure",
                                                            "reference": "0.02"
                                                        }
                                                    }
                                                ],
                                                "units": "1/year",
                                                "documentation": "Annual birth rate fraction"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                ],
                "component_patterns": {
                    "stocks": {
                        "description": "Accumulation variables that integrate flows over time using IntegStructure",
                        "required_fields": ["type", "subtype", "name", "subscripts", "ast"],
                        "ast_pattern": {
                            "syntaxType": "IntegStructure",
                            "flow": "expression (net flow = inflows - outflows)",
                            "initial": "initial value expression"
                        },
                        "example": {
                            "type": "Stock",
                            "subtype": "Normal",
                            "name": "inventory",
                            "subscripts": [[], []],
                            "ast": {
                                "syntaxType": "IntegStructure",
                                "flow": {
                                    "syntaxType": "ArithmeticStructure",
                                    "operators": ["-"],
                                    "arguments": [
                                        {"syntaxType": "ReferenceStructure", "reference": "inflow"},
                                        {"syntaxType": "ReferenceStructure", "reference": "outflow"}
                                    ]
                                },
                                "initial": {"syntaxType": "ReferenceStructure", "reference": "100"}
                            }
                        }
                    },
                    "flows": {
                        "description": "Rate variables that change stocks over time",
                        "required_fields": ["type", "subtype", "name", "subscripts", "ast"],
                        "ast_patterns": ["ArithmeticStructure", "CallStructure", "ReferenceStructure"],
                        "examples": [
                            {
                                "title": "Simple Rate",
                                "component": {
                                    "type": "Flow",
                                    "subtype": "Normal",
                                    "name": "sales_rate",
                                    "subscripts": [[], []],
                                    "ast": {
                                        "syntaxType": "ArithmeticStructure",
                                        "operators": ["*"],
                                        "arguments": [
                                            {"syntaxType": "ReferenceStructure", "reference": "demand"},
                                            {"syntaxType": "ReferenceStructure", "reference": "fulfillment_rate"}
                                        ]
                                    }
                                }
                            },
                            {
                                "title": "Function Call",
                                "component": {
                                    "type": "Flow",
                                    "subtype": "Normal",
                                    "name": "constrained_flow",
                                    "subscripts": [[], []],
                                    "ast": {
                                        "syntaxType": "CallStructure",
                                        "function": {"syntaxType": "ReferenceStructure", "reference": "MIN"},
                                        "arguments": [
                                            {"syntaxType": "ReferenceStructure", "reference": "desired_flow"},
                                            {"syntaxType": "ReferenceStructure", "reference": "capacity"}
                                        ]
                                    }
                                }
                            }
                        ]
                    },
                    "auxiliaries": {
                        "description": "Helper variables for calculations and constants",
                        "required_fields": ["type", "subtype", "name", "subscripts", "ast"],
                        "ast_patterns": ["ReferenceStructure", "ArithmeticStructure", "CallStructure"],
                        "examples": [
                            {
                                "title": "Constant",
                                "component": {
                                    "type": "Auxiliary",
                                    "subtype": "Normal",
                                    "name": "growth_rate",
                                    "subscripts": [[], []],
                                    "ast": {"syntaxType": "ReferenceStructure", "reference": "0.05"}
                                }
                            },
                            {
                                "title": "Calculation",
                                "component": {
                                    "type": "Auxiliary",
                                    "subtype": "Normal",
                                    "name": "total_value",
                                    "subscripts": [[], []],
                                    "ast": {
                                        "syntaxType": "ArithmeticStructure",
                                        "operators": ["*"],
                                        "arguments": [
                                            {"syntaxType": "ReferenceStructure", "reference": "quantity"},
                                            {"syntaxType": "ReferenceStructure", "reference": "price"}
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
                "ast_syntax_guide": {
                    "description": "Abstract Syntax Tree patterns for mathematical expressions",
                    "reference": {
                        "title": "Variable Reference",
                        "pattern": {"syntaxType": "ReferenceStructure", "reference": "variable_name"}
                    },
                    "arithmetic": {
                        "title": "Mathematical Operations",
                        "pattern": {
                            "syntaxType": "ArithmeticStructure",
                            "operators": ["list of operators: +, -, *, /, ^"],
                            "arguments": ["array of expressions"]
                        },
                        "example": {
                            "syntaxType": "ArithmeticStructure",
                            "operators": ["+", "*"],
                            "arguments": [
                                {"syntaxType": "ReferenceStructure", "reference": "base_value"},
                                {
                                    "syntaxType": "ArithmeticStructure",
                                    "operators": ["*"],
                                    "arguments": [
                                        {"syntaxType": "ReferenceStructure", "reference": "rate"},
                                        {"syntaxType": "ReferenceStructure", "reference": "time"}
                                    ]
                                }
                            ]
                        }
                    },
                    "function_calls": {
                        "title": "Function Calls",
                        "pattern": {
                            "syntaxType": "CallStructure",
                            "function": {"syntaxType": "ReferenceStructure", "reference": "function_name"},
                            "arguments": ["array of expressions"]
                        },
                        "common_functions": ["MIN", "MAX", "ABS", "EXP", "LN", "SIN", "COS", "SQRT", "IF_THEN_ELSE"]
                    },
                    "integration": {
                        "title": "Stock Integration",
                        "pattern": {
                            "syntaxType": "IntegStructure",
                            "flow": "net flow expression",
                            "initial": "initial value expression"
                        }
                    }
                },
                "validation_checklist": [
                    "Root object must have 'abstractModel' property",
                    "abstractModel must have 'originalPath' and 'sections' properties",
                    "Main section must have name='__main__', type='main', path='/'",
                    "All required section fields must be present: params, returns, subscripts, constraints, testInputs, split, viewsDict",
                    "Elements must contain components array",
                    "Components must have: type, subtype, name, subscripts (as [[], []]), ast",
                    "AST must have syntaxType field matching the expression structure",
                    "Stock components must use IntegStructure with flow and initial",
                    "All variable references must match component names"
                ]
            }
        }
    
    def get_schema_help(
        self,
        schema_type: str,
        section_path: Optional[str] = None,
        include_examples: bool = True,
        detail_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Get comprehensive schema documentation for any section.
        
        Args:
            schema_type: The schema type ("DES", "SD", etc.)
            section_path: Optional path to specific section (e.g., "entity_types", "processing_rules.steps")
            include_examples: Whether to include examples
            detail_level: Level of detail ("brief", "standard", "detailed")
            
        Returns:
            Comprehensive documentation dictionary
        """
        # Validate schema type
        if schema_type not in self.registry.get_available_schemas():
            return {
                "error": f"Schema type '{schema_type}' not available",
                "available_schemas": self.registry.get_available_schemas()
            }
        
        # Load schema
        schema = self.registry.load_schema(schema_type)
        if not schema:
            return {
                "error": f"Could not load schema for type '{schema_type}'",
                "suggestion": "Check if schema file exists and is valid JSON"
            }
        
        # Handle different section requests
        if section_path is None:
            return self._get_full_schema_overview(schema_type, schema, include_examples, detail_level)
        elif section_path == "templates":
            return self._get_template_overview(schema_type)
        else:
            return self._get_section_documentation(schema_type, section_path, schema, include_examples, detail_level)
    
    def _get_full_schema_overview(
        self,
        schema_type: str,
        schema: Dict[str, Any],
        include_examples: bool,
        detail_level: str
    ) -> Dict[str, Any]:
        """Get overview of the entire schema."""
        overview = {
            "schema_type": schema_type,
            "title": schema.get("title", f"{schema_type} Simulation Schema"),
            "description": schema.get("description", f"Schema for {schema_type} simulation models"),
            "version": schema.get("version", "1.0")
        }
        
        # Add main sections
        properties = schema.get("properties", {})
        main_sections = []
        
        for section_name, section_schema in properties.items():
            section_info = {
                "name": section_name,
                "description": section_schema.get("description", f"{section_name} configuration"),
                "required": section_name in schema.get("required", []),
                "type": section_schema.get("type", "object")
            }
            
            if detail_level == "detailed":
                section_info["properties"] = list(section_schema.get("properties", {}).keys())
            
            main_sections.append(section_info)
        
        overview["main_sections"] = main_sections
        
        # Add schema indicators
        schema_info = self.registry.get_schema_info(schema_type)
        if schema_info:
            overview["key_indicators"] = schema_info.indicators
            overview["description"] = schema_info.description
        
        # Add examples if requested
        if include_examples and schema_type in self._examples_cache:
            overview["quick_examples"] = self._get_quick_examples(schema_type)
        
        # Add common workflows
        overview["common_workflows"] = self._get_common_workflows(schema_type)
        
        return overview
    
    def _get_section_documentation(
        self,
        schema_type: str,
        section_path: str,
        schema: Dict[str, Any],
        include_examples: bool,
        detail_level: str
    ) -> Dict[str, Any]:
        """Get documentation for a specific schema section."""
        # Parse section path
        path_parts = section_path.split('.')
        current_schema = schema
        current_path = []
        
        # Navigate to the requested section
        try:
            for part in path_parts:
                current_path.append(part)
                if part in current_schema.get("properties", {}):
                    current_schema = current_schema["properties"][part]
                elif part in current_schema:
                    current_schema = current_schema[part]
                else:
                    return {
                        "error": f"Section '{'.'.join(current_path)}' not found in schema",
                        "available_sections": list(current_schema.get("properties", {}).keys()) if "properties" in current_schema else []
                    }
        except Exception as e:
            return {
                "error": f"Error navigating to section '{section_path}': {str(e)}",
                "suggestion": "Check section path format (e.g., 'entity_types', 'processing_rules.steps')"
            }
        
        # Build documentation
        doc = {
            "schema_type": schema_type,
            "section_path": section_path,
            "description": current_schema.get("description", f"Configuration for {section_path}"),
            "required": section_path in schema.get("required", []),
            "type": current_schema.get("type", "object")
        }
        
        # Add structure information
        if detail_level in ["standard", "detailed"]:
            doc["structure"] = self._extract_structure_info(current_schema)
        
        # Add validation rules
        doc["validation_rules"] = self._extract_validation_rules(section_path, current_schema)
        
        # Add examples
        if include_examples:
            doc["examples"] = self._get_section_examples(schema_type, section_path)
        
        # Add related sections
        doc["related_sections"] = self._get_related_sections(schema_type, section_path)
        
        # Add common patterns
        doc["common_patterns"] = self._get_common_patterns(schema_type, section_path)
        
        return doc
    
    def _get_template_overview(self, schema_type: str) -> Dict[str, Any]:
        """Get overview of available templates for a schema type."""
        # This would integrate with the template system (Phase 3)
        # For now, return basic template information
        return {
            "schema_type": schema_type,
            "templates_available": False,
            "message": "Template system will be available in Phase 3",
            "basic_examples": self._get_quick_examples(schema_type) if schema_type in self._examples_cache else []
        }
    
    def _extract_structure_info(self, schema_section: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structural information from schema section."""
        structure = {
            "type": schema_section.get("type", "object")
        }
        
        if "properties" in schema_section:
            structure["properties"] = {}
            for prop_name, prop_schema in schema_section["properties"].items():
                structure["properties"][prop_name] = {
                    "type": prop_schema.get("type", "unknown"),
                    "required": prop_name in schema_section.get("required", [])
                }
                
                # Add constraints
                if "minimum" in prop_schema:
                    structure["properties"][prop_name]["minimum"] = prop_schema["minimum"]
                if "maximum" in prop_schema:
                    structure["properties"][prop_name]["maximum"] = prop_schema["maximum"]
                if "enum" in prop_schema:
                    structure["properties"][prop_name]["allowed_values"] = prop_schema["enum"]
        
        if "patternProperties" in schema_section:
            structure["pattern_properties"] = True
            structure["pattern_description"] = "Dynamic property names allowed"
        
        return structure
    
    def _extract_validation_rules(self, section_path: str, schema_section: Dict[str, Any]) -> List[str]:
        """Extract validation rules from schema section."""
        rules = []
        
        # Type-specific rules
        if schema_section.get("type") == "object":
            if "required" in schema_section:
                rules.append(f"Required properties: {', '.join(schema_section['required'])}")
        
        # Number constraints
        if "minimum" in schema_section:
            rules.append(f"Minimum value: {schema_section['minimum']}")
        if "maximum" in schema_section:
            rules.append(f"Maximum value: {schema_section['maximum']}")
        
        # String patterns
        if "pattern" in schema_section:
            rules.append(f"Must match pattern: {schema_section['pattern']}")
        
        # Array constraints
        if schema_section.get("type") == "array":
            if "minItems" in schema_section:
                rules.append(f"Minimum items: {schema_section['minItems']}")
            if "maxItems" in schema_section:
                rules.append(f"Maximum items: {schema_section['maxItems']}")
        
        # Section-specific business rules
        if section_path == "entity_types":
            rules.append("All entity type probabilities must sum to 1.0")
            rules.append("Entity names must start with letter, contain only letters, numbers, underscores")
            rules.append("Priority 1 = highest, 10 = lowest")
        elif section_path == "resources":
            rules.append("Resource capacity must be positive integer")
            rules.append("Resource type must be 'fifo', 'priority', or 'preemptive'")
        elif section_path == "processing_rules":
            rules.append("All step names must reference defined resources")
            rules.append("Distributions must be valid strings: 'uniform(a,b)', 'normal(mean,std)', 'exp(mean)'")
        
        return rules
    
    def _get_section_examples(self, schema_type: str, section_path: str) -> List[Dict[str, Any]]:
        """Get examples for a specific section."""
        if schema_type not in self._examples_cache:
            return []
        
        # Handle nested paths
        section_key = section_path.split('.')[0]
        
        return self._examples_cache[schema_type].get(section_key, [])
    
    def _get_quick_examples(self, schema_type: str) -> List[Dict[str, Any]]:
        """Get quick examples for schema overview."""
        if schema_type not in self._examples_cache:
            return []
        
        quick_examples = []
        examples_data = self._examples_cache[schema_type]
        
        # Get first example from key sections
        key_sections = ["entity_types", "resources", "processing_rules"]
        for section in key_sections:
            if section in examples_data and examples_data[section]:
                example = examples_data[section][0]
                quick_examples.append({
                    "section": section,
                    "title": example["title"],
                    "example": example["example"]
                })
        
        return quick_examples
    
    def _get_related_sections(self, schema_type: str, section_path: str) -> List[str]:
        """Get sections related to the current section."""
        relationships = {
            "DES": {
                "entity_types": ["resources", "processing_rules", "balking_rules", "reneging_rules"],
                "resources": ["entity_types", "processing_rules", "basic_failures"],
                "processing_rules": ["entity_types", "resources", "simple_routing"],
                "balking_rules": ["entity_types", "resources"],
                "reneging_rules": ["entity_types", "resources"],
                "simple_routing": ["entity_types", "processing_rules"],
                "basic_failures": ["resources"],
                "statistics": ["metrics"],
                "metrics": ["statistics"]
            }
        }
        
        section_key = section_path.split('.')[0]
        return relationships.get(schema_type, {}).get(section_key, [])
    
    def _get_common_patterns(self, schema_type: str, section_path: str) -> List[str]:
        """Get common patterns for a section."""
        patterns = {
            "DES": {
                "entity_types": [
                    "VIP/Regular customer segmentation",
                    "Priority-based service levels",
                    "Value-based revenue tracking",
                    "Emergency/Urgent/Routine classification"
                ],
                "resources": [
                    "Reception -> Service -> Checkout flow",
                    "Priority queues for VIP customers",
                    "Preemptive resources for emergencies",
                    "Multiple parallel servers"
                ],
                "processing_rules": [
                    "Sequential processing steps",
                    "Conditional service times by entity type",
                    "Uniform distributions for consistent processes",
                    "Normal distributions for variable processes"
                ],
                "balking_rules": [
                    "Queue length thresholds",
                    "Priority-based balking multipliers",
                    "Random balking probability"
                ],
                "reneging_rules": [
                    "Patience time distributions",
                    "Priority affects patience levels",
                    "Normal distribution for abandon times"
                ]
            }
        }
        
        section_key = section_path.split('.')[0]
        return patterns.get(schema_type, {}).get(section_key, [])
    
    def _get_common_workflows(self, schema_type: str) -> List[Dict[str, str]]:
        """Get common development workflows for a schema type."""
        workflows = {
            "DES": [
                {
                    "name": "Basic Service System",
                    "steps": "1. Define entity_types -> 2. Add resources -> 3. Configure processing_rules -> 4. Run simulation"
                },
                {
                    "name": "Advanced Queue Management",
                    "steps": "1. Basic setup -> 2. Add balking_rules -> 3. Add reneging_rules -> 4. Configure statistics"
                },
                {
                    "name": "Multi-Stage Process",
                    "steps": "1. Define entity_types -> 2. Create resource chain -> 3. Add routing logic -> 4. Configure failures"
                }
            ]
        }
        
        return workflows.get(schema_type, [])


# Global documentation provider instance
schema_documentation_provider = SchemaDocumentationProvider()
