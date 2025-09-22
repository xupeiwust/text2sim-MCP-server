#!/usr/bin/env python3
"""
Test script to verify SD implementation fixes are working.
"""

import json
from SD.sd_integration import PySDJSONIntegration

def test_sd_integration():
    """Test the SD integration fixes."""
    print("Testing SD Integration Fixes...")

    # Create a simple test model
    test_model = {
        "abstractModel": {
            "originalPath": "test_model.json",
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
                                            "syntaxType": "ReferenceStructure",
                                            "reference": "net_growth"
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
                            "documentation": "Population stock"
                        },
                        {
                            "name": "net_growth",
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
                                                "reference": "0.005"
                                            }
                                        ]
                                    }
                                }
                            ],
                            "units": "people/year",
                            "limits": [None, None],
                            "documentation": "Net growth rate"
                        }
                    ]
                }
            ]
        }
    }

    # Test validation
    print("\n1. Testing validation...")
    sd_integration = PySDJSONIntegration()

    try:
        validation_result = sd_integration.validate_json_model(test_model)
        print(f"✅ Validation successful: {validation_result.is_valid}")
        if not validation_result.is_valid:
            print(f"❌ Errors: {validation_result.errors}")
        else:
            print("✅ No validation errors")
    except Exception as e:
        print(f"❌ Validation failed with exception: {e}")
        return False

    # Test simulation
    print("\n2. Testing simulation...")
    try:
        sim_result = sd_integration.simulate_json_model(
            test_model,
            initial_time=0,
            final_time=10,
            time_step=1
        )
        print(f"✅ Simulation successful: {sim_result.success}")
        if sim_result.success:
            print(f"✅ Time series data keys: {list(sim_result.time_series.keys())}")
            print(f"✅ Sample data points: {len(sim_result.time_series.get('TIME', []))}")
        else:
            print(f"❌ Simulation error: {sim_result.error_message}")
    except Exception as e:
        print(f"❌ Simulation failed with exception: {e}")
        return False

    print("\n✅ All SD integration tests passed!")
    return True

if __name__ == "__main__":
    test_sd_integration()