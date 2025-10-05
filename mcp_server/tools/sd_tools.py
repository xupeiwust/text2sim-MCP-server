"""
System Dynamics (SD) tools for MCP server.

This module implements SD-specific simulation tools using PySD integration
with comprehensive JSON schema support and model conversion capabilities.
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional, List

from ..shared.error_handlers import MCPErrorHandler
from ..shared.response_builders import ResponseBuilder
from ..shared.integration_layer import (
    integration_manager,
    ensure_sd_integration,
    SDValidationError,
    SDModelBuildError,
    SDSimulationError
)


def _generate_sd_suggestions(errors: List[str]) -> List[str]:
    """Generate helpful suggestions for SD validation errors."""
    suggestions = []

    for error in errors:
        error_str = str(error).lower()
        if "abstractmodel" in error_str:
            suggestions.append("Ensure JSON follows PySD abstract model schema structure")
        elif "sections" in error_str:
            suggestions.append("Check that 'sections' array contains at least one main section")
        elif "originalpath" in error_str:
            suggestions.append("Provide 'originalPath' field in abstractModel")
        elif "elements" in error_str:
            suggestions.append("Verify model elements have required fields (name, components)")
        elif "components" in error_str:
            suggestions.append("Check component structure with type, subtype, and ast fields")

    if not suggestions:
        suggestions.extend([
            "Check JSON structure matches PySD abstract model schema",
            "Ensure all required fields are present",
            "Verify nested object structures are correct"
        ])

    return suggestions[:3]  # Limit to top 3 suggestions


def _generate_sd_quick_fixes(errors: List[str]) -> List[str]:
    """Generate quick fix suggestions for common SD errors."""
    fixes = []

    for error in errors:
        error_str = str(error).lower()
        if "required" in error_str and "abstractmodel" in error_str:
            fixes.append("Wrap model definition in 'abstractModel' object")
        elif "required" in error_str and "sections" in error_str:
            fixes.append("Add 'sections' array with at least one section")
        elif "required" in error_str and "originalpath" in error_str:
            fixes.append("Add 'originalPath' field with model file path")

    if not fixes:
        fixes.extend([
            "Check for missing required fields",
            "Verify JSON structure is valid",
            "Ensure proper nesting of objects"
        ])

    return fixes[:3]  # Limit to top 3 fixes


def _calculate_sd_complexity(config: Dict) -> Dict:
    """Calculate model complexity metrics for SD models."""
    try:
        if "abstractModel" in config:
            abstract_model = config["abstractModel"]
            sections = abstract_model.get("sections", [])

            total_elements = sum(len(section.get("elements", [])) for section in sections)
            total_components = sum(
                len(element.get("components", []))
                for section in sections
                for element in section.get("elements", [])
            )

            return {
                "sections": len(sections),
                "total_elements": total_elements,
                "total_components": total_components,
                "complexity_score": min(10, (total_elements + total_components) // 10),
                "estimated_build_time": f"{max(1, total_elements // 5)} seconds"
            }
        else:
            return {
                "complexity_score": 1,
                "message": "Model structure not recognized"
            }

    except Exception:
        return {
            "complexity_score": 0,
            "message": "Unable to calculate complexity"
        }


def register_sd_tools(mcp: FastMCP) -> None:
    """Register all SD-related MCP tools."""

    @mcp.tool()
    def simulate_sd(
        config: dict,
        parameters: Optional[dict] = None,
        time_settings: Optional[dict] = None
    ) -> dict:
        """
        Advanced System Dynamics simulation using PySD-compatible JSON format.

        Simulate System Dynamics models using a PySD-compatible JSON schema that mirrors
        the library's internal Python dataclass structure. This format provides full
        compatibility with PySD's native workflow and ensures accurate model execution.

        QUICK START - Basic abstractModel Format:
        {
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
              "split": false,
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
                        "reference": "Birth Rate"
                      },
                      "initial": {
                        "syntaxType": "ReferenceStructure",
                        "reference": "1000"
                      }
                    }
                  }],
                  "units": "people",
                  "limits": [null, null],
                  "documentation": "Population stock"
                },
                {
                  "name": "Birth Rate",
                  "components": [{
                    "type": "Flow",
                    "subtype": "Normal",
                    "subscripts": [[], []],
                    "ast": {
                      "syntaxType": "ReferenceStructure",
                      "reference": "Population * Birth Fraction"
                    }
                  }],
                  "units": "people/year",
                  "limits": [null, null],
                  "documentation": "Birth rate flow"
                },
                {
                  "name": "Birth Fraction",
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
                  "limits": [null, null],
                  "documentation": "Birth fraction constant"
                }
              ]
            }]
          }
        }

        ABSTRACTMODEL STRUCTURE:

        Required Top-Level Fields:
        - abstractModel: Container for the entire model definition
        - abstractModel.originalPath: Original file path (can be descriptive)
        - abstractModel.sections: Array of model sections (usually one "__main__" section)

        Section Structure:
        - name: Section identifier (typically "__main__")
        - type: Section type ("main" for primary section)
        - elements: Array of model variables (stocks, flows, auxiliaries)

        Element Structure:
        - name: Variable name (must be unique within section)
        - components: Array of computation definitions (usually one component)
        - units: Physical units for the variable
        - limits: Minimum and maximum bounds [min, max] (use null for unbounded)
        - documentation: Description of the variable

        Component Types:
        - Stock: Accumulation variable (integrates flows over time)
        - Flow: Rate variable (changes stocks)
        - Auxiliary: Algebraic variable (calculated from other variables)

        AST (Abstract Syntax Tree) Patterns:
        - IntegStructure: For stocks with flow and initial value
        - ReferenceStructure: For references to other variables or constants
        - reference: Mathematical expression using variable names

        TIME CONFIGURATION:
        Time settings can be provided via time_settings parameter or embedded in config:
        {
          "time_settings": {
            "initial_time": 0,
            "final_time": 100,
            "time_step": 0.25
          }
        }

        PYSD COMPATIBILITY:
        This format exactly mirrors PySD's internal Python dataclass structure,
        ensuring seamless integration with the PySD simulation engine and
        maintaining full compatibility with existing PySD workflows.

        Args:
            config: SD model in PySD abstractModel JSON format
            parameters: Parameter value overrides for simulation
            time_settings: Simulation time configuration overrides

        Returns:
            Dictionary with simulation results and model metadata
        """
        if not integration_manager.sd_available:
            return MCPErrorHandler.import_error(
                "SD integration",
                fallback_available=False,
                fallback_message="Install PySD dependencies to enable SD simulation"
            )

        try:
            # Validate SD integration is available
            sd_integration = ensure_sd_integration()

            # Extract time settings without modifying the model config
            initial_time = 0
            final_time = 100
            time_step = 1

            if time_settings:
                initial_time = time_settings.get("initial_time", initial_time)
                final_time = time_settings.get("final_time", final_time)
                time_step = time_settings.get("time_step", time_step)

            # Also check config for time_settings (backward compatibility)
            if "time_settings" in config:
                ts = config["time_settings"]
                initial_time = ts.get("initial_time", initial_time)
                final_time = ts.get("final_time", final_time)
                time_step = ts.get("time_step", time_step)

            # Run simulation with individual parameters
            results = sd_integration.simulate_json_model(
                config,
                initial_time=initial_time,
                final_time=final_time,
                time_step=time_step,
                params=parameters
            )

            if results.success:
                return ResponseBuilder.simulation_response(
                    success=True,
                    results=results.time_series,
                    model_info={
                        "simulation_type": "SD",
                        "model_name": config.get("model_name", "Unnamed Model"),
                        "time_range": f"{len(results.time_series.get('TIME', [0]))} time steps",
                        "variables": list(results.time_series.keys()),
                        "time_settings": {
                            "initial_time": initial_time,
                            "final_time": final_time,
                            "time_step": time_step
                        }
                    },
                    execution_metadata=results.metadata
                )
            else:
                return ResponseBuilder.simulation_response(
                    success=False,
                    model_info={
                        "simulation_type": "SD",
                        "model_name": config.get("model_name", "Unnamed Model"),
                        "time_range": "Simulation failed",
                        "variables": []
                    },
                    execution_metadata=results.metadata,
                    error_message=results.error_message
                )

        except (SDValidationError, SDModelBuildError, SDSimulationError) as e:
            return MCPErrorHandler.simulation_error(
                str(e),
                _generate_sd_suggestions([str(e)]),
                "SD_ERROR"
            )
        except Exception as e:
            return MCPErrorHandler.simulation_error(
                f"Unexpected error in SD simulation: {str(e)}",
                ["Check model format", "Verify PySD integration", "Review configuration"]
            )

    @mcp.tool()
    def convert_vensim_to_sd_json(file_path: str) -> dict:
        """
        Convert Vensim .mdl file to SD JSON format for use with simulate_sd.

        Enables importing existing Vensim models into the conversational SD workflow.
        The converted JSON follows the PySD abstractModel schema for full compatibility.

        Args:
            file_path: Path to Vensim .mdl file

        Returns:
            SD model in JSON format ready for simulate_sd tool
        """
        if not integration_manager.sd_available:
            return MCPErrorHandler.import_error(
                "SD integration",
                fallback_available=False,
                fallback_message="Install PySD dependencies to enable Vensim conversion"
            )

        try:
            sd_integration = ensure_sd_integration()
            json_model = sd_integration.convert_vensim_to_json(file_path)

            return ResponseBuilder.success_response(
                {
                    "model_json": json_model,
                    "conversion_info": {
                        "original_file": file_path,
                        "conversion_type": "Vensim → SD JSON",
                        "ready_for_simulation": True,
                        "format": "PySD abstractModel JSON"
                    }
                },
                metadata={
                    "conversion_timestamp": ResponseBuilder.add_timestamp({})["timestamp"],
                    "file_format": "Vensim MDL",
                    "output_format": "PySD JSON"
                }
            )

        except (SDModelBuildError, FileNotFoundError) as e:
            return MCPErrorHandler.file_operation_error(
                "conversion",
                file_path,
                str(e),
                [
                    "Verify file path exists and is accessible",
                    "Check file is valid Vensim .mdl format",
                    "Ensure PySD can parse the model structure"
                ]
            )
        except Exception as e:
            return MCPErrorHandler.simulation_error(
                f"Unexpected conversion error: {str(e)}",
                ["Check file format", "Verify PySD installation", "Try with simpler model"]
            )

    @mcp.tool()
    def get_sd_model_info(config: dict) -> dict:
        """
        Analyze SD model configuration and provide detailed information.

        Shows model structure, complexity metrics, and validation status
        without running simulation. Useful for understanding model properties
        before simulation execution.

        Args:
            config: SD model configuration

        Returns:
            Detailed model analysis and information
        """
        if not integration_manager.sd_available:
            return MCPErrorHandler.import_error(
                "SD integration",
                fallback_available=True,
                fallback_message="Limited analysis available without SD integration"
            )

        try:
            # Get basic model info from integration
            sd_integration = integration_manager.sd_integration
            model_info = sd_integration.get_model_info(config)

            # Add structure analysis if available
            if isinstance(config, dict) and "abstractModel" in config:
                abstract_model = config["abstractModel"]
                sections = abstract_model.get("sections", [])

                # Enhanced analysis
                enhanced_info = {
                    "model_structure": {
                        "format": "PySD abstractModel JSON",
                        "sections_count": len(sections),
                        "original_path": abstract_model.get("originalPath", "Unknown")
                    },
                    "complexity_metrics": _calculate_sd_complexity(config),
                    "time_settings": config.get("time_settings", {}),
                    "section_details": [
                        {
                            "name": section.get("name", ""),
                            "type": section.get("type", "unknown"),
                            "elements_count": len(section.get("elements", [])),
                            "element_types": _analyze_element_types(section.get("elements", []))
                        }
                        for section in sections
                    ],
                    "validation_status": "pending"
                }

                # Merge with basic model info
                model_info.update(enhanced_info)

            return ResponseBuilder.success_response(
                model_info,
                metadata={
                    "analysis_timestamp": ResponseBuilder.add_timestamp({})["timestamp"],
                    "sd_integration_available": integration_manager.sd_available
                }
            )

        except Exception as e:
            return MCPErrorHandler.simulation_error(
                f"SD model analysis error: {str(e)}",
                ["Check model format", "Verify abstractModel structure", "Review JSON syntax"]
            )

    def _analyze_element_types(elements: List[Dict]) -> Dict[str, int]:
        """Analyze and count element types in a section."""
        type_counts = {"Stock": 0, "Flow": 0, "Auxiliary": 0, "Unknown": 0}

        for element in elements:
            components = element.get("components", [])
            if components:
                element_type = components[0].get("type", "Unknown")
                if element_type in type_counts:
                    type_counts[element_type] += 1
                else:
                    type_counts["Unknown"] += 1

        return type_counts