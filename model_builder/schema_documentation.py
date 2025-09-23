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
                "abstractModel": [
                    {
                        "title": "Basic Population Model Container",
                        "description": "Root abstractModel structure with proper PySD format",
                        "example": {
                            "abstractModel": {
                                "originalPath": "population_growth.json",
                                "sections": [{
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
                                    "elements": []
                                }]
                            }
                        }
                    }
                ],
                "sections": [
                    {
                        "title": "Main Section Structure",
                        "description": "Standard main section for System Dynamics models",
                        "example": {
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
                            "elements": []
                        }
                    }
                ],
                "elements": [
                    {
                        "title": "Population Stock Element",
                        "description": "Stock variable element with proper PySD structure",
                        "example": {
                            "name": "Population",
                            "components": [{
                                "type": "Stock",
                                "subtype": "Normal",
                                "subscripts": [[], []],
                                "ast": {
                                    "syntaxType": "IntegStructure",
                                    "flow": {
                                        "syntaxType": "ArithmeticStructure",
                                        "operators": ["-"],
                                        "arguments": [
                                            {"syntaxType": "ReferenceStructure", "reference": "Birth_Rate"},
                                            {"syntaxType": "ReferenceStructure", "reference": "Death_Rate"}
                                        ]
                                    },
                                    "initial": {
                                        "syntaxType": "ReferenceStructure",
                                        "reference": "1000"
                                    }
                                }
                            }],
                            "units": "people",
                            "limits": [None, None],
                            "documentation": "Population stock"
                        }
                    },
                    {
                        "title": "Birth Rate Flow Element",
                        "description": "Flow variable element affecting population stock",
                        "example": {
                            "name": "Birth_Rate",
                            "components": [{
                                "type": "Flow",
                                "subtype": "Normal",
                                "subscripts": [[], []],
                                "ast": {
                                    "syntaxType": "ArithmeticStructure",
                                    "operators": ["*"],
                                    "arguments": [
                                        {"syntaxType": "ReferenceStructure", "reference": "Population"},
                                        {"syntaxType": "ReferenceStructure", "reference": "Birth_Fraction"}
                                    ]
                                }
                            }],
                            "units": "people/year",
                            "limits": [None, None],
                            "documentation": "Birth rate flow"
                        }
                    },
                    {
                        "title": "Birth Fraction Auxiliary Element",
                        "description": "Auxiliary variable element for birth rate calculation",
                        "example": {
                            "name": "Birth_Fraction",
                            "components": [{
                                "type": "Auxiliary",
                                "subtype": "Normal",
                                "subscripts": [[], []],
                                "ast": {
                                    "syntaxType": "ReferenceStructure",
                                    "reference": "0.05"
                                }
                            }],
                            "units": "1/year",
                            "limits": [None, None],
                            "documentation": "Birth fraction constant"
                        }
                    }
                ],
                "components": [
                    {
                        "title": "Stock Component",
                        "description": "Component definition for accumulation variables",
                        "example": {
                            "type": "Stock",
                            "subtype": "Normal",
                            "subscripts": [[], []],
                            "ast": {
                                "syntaxType": "IntegStructure",
                                "flow": {
                                    "syntaxType": "ArithmeticStructure",
                                    "operators": ["-"],
                                    "arguments": [
                                        {"syntaxType": "ReferenceStructure", "reference": "Inflow"},
                                        {"syntaxType": "ReferenceStructure", "reference": "Outflow"}
                                    ]
                                },
                                "initial": {
                                    "syntaxType": "ReferenceStructure",
                                    "reference": "Initial_Value"
                                }
                            }
                        }
                    },
                    {
                        "title": "Flow Component",
                        "description": "Component definition for rate variables",
                        "example": {
                            "type": "Flow",
                            "subtype": "Normal",
                            "subscripts": [[], []],
                            "ast": {
                                "syntaxType": "ArithmeticStructure",
                                "operators": ["*"],
                                "arguments": [
                                    {"syntaxType": "ReferenceStructure", "reference": "Factor_A"},
                                    {"syntaxType": "ReferenceStructure", "reference": "Factor_B"}
                                ]
                            }
                        }
                    },
                    {
                        "title": "Auxiliary Component",
                        "description": "Component definition for calculated variables",
                        "example": {
                            "type": "Auxiliary",
                            "subtype": "Normal",
                            "subscripts": [[], []],
                            "ast": {
                                "syntaxType": "ReferenceStructure",
                                "reference": "Calculation_or_Constant"
                            }
                        }
                    }
                ],
                "ast": [
                    {
                        "title": "Stock AST Structure",
                        "description": "IntegStructure for accumulation variables",
                        "example": {
                            "syntaxType": "IntegStructure",
                            "flow": {
                                "syntaxType": "ReferenceStructure",
                                "reference": "Inflow_Variable - Outflow_Variable"
                            },
                            "initial": {
                                "syntaxType": "ReferenceStructure",
                                "reference": "1000"
                            }
                        }
                    },
                    {
                        "title": "PREFERRED: ArithmeticStructure for Mathematical Expressions",
                        "description": "Use ArithmeticStructure for any calculation with operators. This ensures proper parsing and mathematical accuracy.",
                        "example": {
                            "syntaxType": "ArithmeticStructure",
                            "operators": ["+"],
                            "arguments": [
                                {
                                    "syntaxType": "ArithmeticStructure",
                                    "operators": ["*"],
                                    "arguments": [
                                        {"syntaxType": "ReferenceStructure", "reference": "Variable_A"},
                                        {"syntaxType": "ReferenceStructure", "reference": "Variable_B"}
                                    ]
                                },
                                {"syntaxType": "ReferenceStructure", "reference": "Constant"}
                            ]
                        }
                    },
                    {
                        "title": "ReferenceStructure for Simple Variables Only",
                        "description": "Use ReferenceStructure ONLY for single variable names or numeric constants. AVOID complex expressions.",
                        "example": {
                            "syntaxType": "ReferenceStructure",
                            "reference": "Population"
                        },
                        "bad_example": {
                            "syntaxType": "ReferenceStructure",
                            "reference": "Variable_A * Variable_B + Constant"
                        }
                    }
                ],
                "complete_examples": [
                    {
                        "title": "Simple Population Growth Model",
                        "description": "Complete model showing proper PySD JSON structure",
                        "example": {
                            "abstractModel": {
                                "originalPath": "population_growth.json",
                                "sections": [{
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
                                            "name": "Population",
                                            "components": [{
                                                "type": "Stock",
                                                "subtype": "Normal",
                                                "subscripts": [[], []],
                                                "ast": {
                                                    "syntaxType": "IntegStructure",
                                                    "flow": {
                                                        "syntaxType": "ReferenceStructure",
                                                        "reference": "Birth_Rate"
                                                    },
                                                    "initial": {
                                                        "syntaxType": "ReferenceStructure",
                                                        "reference": "1000"
                                                    }
                                                }
                                            }],
                                            "units": "people",
                                            "limits": [None, None],
                                            "documentation": "Population stock"
                                        },
                                        {
                                            "name": "Birth_Rate",
                                            "components": [{
                                                "type": "Flow",
                                                "subtype": "Normal",
                                                "subscripts": [[], []],
                                                "ast": {
                                                    "syntaxType": "ReferenceStructure",
                                                    "reference": "Population * Birth_Fraction"
                                                }
                                            }],
                                            "units": "people/year",
                                            "limits": [None, None],
                                            "documentation": "Birth rate flow"
                                        },
                                        {
                                            "name": "Birth_Fraction",
                                            "components": [{
                                                "type": "Auxiliary",
                                                "subtype": "Normal",
                                                "subscripts": [[], []],
                                                "ast": {
                                                    "syntaxType": "ReferenceStructure",
                                                    "reference": "0.05"
                                                }
                                            }],
                                            "units": "1/year",
                                            "limits": [None, None],
                                            "documentation": "Birth fraction constant"
                                        }
                                    ]
                                }]
                            }
                        }
                    }
                ],
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
                        "ast_patterns": ["ArithmeticStructure (PREFERRED for calculations)", "CallStructure", "ReferenceStructure (simple variables only)"],
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
                        "ast_patterns": ["ArithmeticStructure (PREFERRED for calculations)", "ReferenceStructure (constants only)", "CallStructure"],
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
            if schema_type == "SD":
                return self._create_sd_documentation(None, include_examples, detail_level)
            else:
                return self._get_full_schema_overview(schema_type, schema, include_examples, detail_level)
        elif section_path == "templates":
            return self._get_template_overview(schema_type)
        else:
            if schema_type == "SD":
                return self._create_sd_documentation(section_path, include_examples, detail_level)
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

    def _create_sd_documentation(
        self,
        section_path: Optional[str],
        include_examples: bool,
        detail_level: str
    ) -> Dict[str, Any]:
        """Create comprehensive SD documentation with examples and guidance."""
        base_sections = {
            "abstractModel": {
                "description": "Root container for PySD-compatible System Dynamics models",
                "required": True,
                "structure": {
                    "originalPath": "string - descriptive path for model identification",
                    "sections": "array - contains model sections (usually one '__main__' section)"
                },
                "validation_rules": [
                    "Must be present at root level",
                    "originalPath field is required",
                    "sections array must contain at least one section"
                ],
                "examples": self._examples_cache["SD"].get("abstractModel", []),
                "related_sections": ["sections", "elements"],
                "common_patterns": [
                    "Single '__main__' section for most models",
                    "Descriptive originalPath for model identification",
                    "Empty arrays for unused fields (params, returns, etc.)"
                ]
            },
            "sections": {
                "description": "Model sections containing System Dynamics variables",
                "required": True,
                "structure": {
                    "name": "string - section identifier (typically '__main__')",
                    "type": "string - section type ('main' for primary section)",
                    "path": "string - hierarchical path ('/' for main section)",
                    "elements": "array - System Dynamics variables in this section"
                },
                "validation_rules": [
                    "At least one section required",
                    "Each section must have name, type, and elements",
                    "Main section should use name='__main__' and type='main'"
                ],
                "examples": self._examples_cache["SD"].get("sections", []),
                "related_sections": ["abstractModel", "elements"],
                "common_patterns": [
                    "Single main section for most models",
                    "Empty params, returns, subscripts arrays",
                    "Elements array contains all model variables"
                ]
            },
            "elements": {
                "description": "Individual System Dynamics variables (stocks, flows, auxiliaries)",
                "required": True,
                "structure": {
                    "name": "string - variable name (must be unique within section)",
                    "components": "array - computation definitions (usually one component)",
                    "units": "string - physical units",
                    "limits": "array - [min, max] bounds (use null for unbounded)",
                    "documentation": "string - variable description"
                },
                "validation_rules": [
                    "Each variable must be its own element",
                    "Element name becomes variable reference in equations",
                    "Components array must contain exactly one component",
                    "Component type must be Stock, Flow, or Auxiliary"
                ],
                "examples": self._examples_cache["SD"].get("elements", []),
                "related_sections": ["components", "ast"],
                "common_patterns": [
                    "One element per variable (not grouped by type)",
                    "Element name matches variable name in equations",
                    "Single component defining computation"
                ]
            },
            "components": {
                "description": "Computation definitions for System Dynamics variables",
                "required": True,
                "structure": {
                    "type": "string - Stock, Flow, or Auxiliary",
                    "subtype": "string - typically 'Normal'",
                    "subscripts": "array - dimensionality [[],[]] for scalar",
                    "ast": "object - Abstract Syntax Tree defining computation"
                },
                "validation_rules": [
                    "Type must be Stock, Flow, or Auxiliary",
                    "Stock components require IntegStructure AST",
                    "Flow and Auxiliary use ReferenceStructure AST",
                    "Subscripts [[],[]] for scalar variables"
                ],
                "examples": self._examples_cache["SD"].get("components", []),
                "related_sections": ["elements", "ast"],
                "common_patterns": [
                    "Stock: IntegStructure with flow and initial",
                    "Flow/Auxiliary: ReferenceStructure with expression",
                    "Normal subtype for standard variables"
                ]
            },
            "ast": {
                "description": "Abstract Syntax Tree defining variable computations",
                "required": True,
                "structure": {
                    "syntaxType": "string - IntegStructure or ReferenceStructure",
                    "reference": "string - mathematical expression (for Reference)",
                    "flow": "object - flow expression (for IntegStructure)",
                    "initial": "object - initial value (for IntegStructure)"
                },
                "validation_rules": [
                    "Stock variables use IntegStructure syntax",
                    "Flow/Auxiliary variables use ArithmeticStructure for calculations, ReferenceStructure for simple variables",
                    "Use ArithmeticStructure for mathematical expressions with operators (+, -, *, /, ^)",
                    "Variable names must match element names exactly"
                ],
                "examples": self._examples_cache["SD"].get("ast", []),
                "related_sections": ["components", "elements"],
                "common_patterns": [
                    "Stock AST: flow + initial value references",
                    "Flow/Auxiliary AST: single mathematical expression",
                    "Variable references use exact element names"
                ]
            }
        }

        # Handle section-specific requests
        if section_path:
            path_parts = section_path.split('.')
            main_section = path_parts[0]

            if main_section in base_sections:
                section = base_sections[main_section]

                # Apply detail level filtering
                if detail_level == "brief":
                    section = {
                        "description": section["description"],
                        "examples": section["examples"][:2] if include_examples else []
                    }
                elif detail_level == "standard":
                    if not include_examples:
                        section["examples"] = []

                return {
                    "schema_type": "SD",
                    "section": main_section,
                    "path": section_path,
                    **section
                }

        # Full schema documentation
        workflows = {
            "basic_model": {
                "name": "Basic SD Model Development",
                "steps": [
                    "1. Create abstractModel container with originalPath",
                    "2. Define main section with name='__main__'",
                    "3. Add elements for each variable (stocks, flows, auxiliaries)",
                    "4. Define components with appropriate AST structures",
                    "5. Validate model structure and equations"
                ],
                "example": "Population growth with birth/death rates"
            },
            "stock_flow_model": {
                "name": "Stock and Flow Modeling",
                "steps": [
                    "1. Define stock elements with IntegStructure AST",
                    "2. Define flow elements with ArithmeticStructure AST for calculations",
                    "3. Connect flows to stocks via AST references",
                    "4. Add auxiliary variables for rates and fractions",
                    "5. Test with different time settings"
                ],
                "example": "Inventory management with production and sales"
            },
            "feedback_model": {
                "name": "Feedback Loop Development",
                "steps": [
                    "1. Identify key stocks in the system",
                    "2. Define flows affecting each stock",
                    "3. Create auxiliaries for feedback calculations",
                    "4. Link auxiliaries back to flow rates",
                    "5. Validate circular reference handling"
                ],
                "example": "Population dynamics with carrying capacity"
            }
        }

        domain_examples = {
            "population": [
                {
                    "name": "Population Growth",
                    "description": "Basic population model with birth and death rates",
                    "variables": ["population", "birth_rate", "death_rate", "birth_fraction", "death_fraction"],
                    "pattern": "Stock with inflows and outflows"
                },
                {
                    "name": "Predator-Prey Model",
                    "description": "Two-species interaction model",
                    "variables": ["rabbits", "foxes", "rabbit_birth_rate", "predation_rate", "fox_death_rate"],
                    "pattern": "Multiple stocks with cross-dependencies"
                }
            ],
            "economics": [
                {
                    "name": "Economic Growth Model",
                    "description": "Capital accumulation and production",
                    "variables": ["capital", "investment_rate", "depreciation_rate", "output", "savings_rate"],
                    "pattern": "Capital stock with investment and depreciation"
                },
                {
                    "name": "Market Dynamics",
                    "description": "Supply and demand interaction",
                    "variables": ["demand", "supply", "price", "demand_adjustment", "supply_response"],
                    "pattern": "Coupled adjustment processes"
                }
            ],
            "epidemiology": [
                {
                    "name": "SIR Disease Model",
                    "description": "Susceptible-Infected-Recovered compartment model",
                    "variables": ["susceptible", "infected", "recovered", "infection_rate", "recovery_rate"],
                    "pattern": "Sequential stock flow with compartments"
                },
                {
                    "name": "Vaccination Model",
                    "description": "Disease spread with vaccination intervention",
                    "variables": ["susceptible", "vaccinated", "infected", "vaccination_rate", "infection_rate", "waning_immunity"],
                    "pattern": "Multi-path stock flows with interventions"
                }
            ],
            "supply_chain": [
                {
                    "name": "Inventory Management",
                    "description": "Production and consumption with inventory buffer",
                    "variables": ["inventory", "production_rate", "consumption_rate", "target_inventory", "adjustment_time"],
                    "pattern": "Stock with goal-seeking flow control"
                },
                {
                    "name": "Supply Chain Network",
                    "description": "Multi-stage production and distribution",
                    "variables": ["raw_materials", "work_in_progress", "finished_goods", "manufacturing_rate", "shipping_rate"],
                    "pattern": "Sequential processing pipeline"
                }
            ]
        }

        result = {
            "schema_type": "SD",
            "description": "System Dynamics modeling using PySD-compatible JSON format",
            "sections": base_sections,
            "workflows": workflows,
            "domain_examples": domain_examples if include_examples else {}
        }

        # Apply detail level filtering
        if detail_level == "brief":
            # Reduce examples in each section
            for section_name, section_data in result["sections"].items():
                if "examples" in section_data:
                    section_data["examples"] = section_data["examples"][:1]
            result["workflows"] = {k: v for k, v in list(workflows.items())[:2]}
        elif not include_examples:
            # Remove examples but keep structure
            for section_data in result["sections"].values():
                section_data["examples"] = []

        return result


# Global documentation provider instance
schema_documentation_provider = SchemaDocumentationProvider()
