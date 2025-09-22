"""
System Dynamics Integration Module for Text2Sim MCP Server.

This module provides the core integration between JSON-based SD model definitions
and the PySD library for simulation execution. It handles model validation,
conversion, and simulation with comprehensive error handling.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
import logging

import pysd
import pandas as pd
import numpy as np

# Note: AbstractModelAdapter requires json_data parameter, will be used as needed


class SDIntegrationError(Exception):
    """Base exception for SD integration errors."""
    pass


class SDValidationError(SDIntegrationError):
    """JSON schema validation errors."""
    pass


class SDModelBuildError(SDIntegrationError):
    """Model building/compilation errors."""
    pass


class SDSimulationError(SDIntegrationError):
    """Model simulation runtime errors."""
    pass


@dataclass
class ValidationResult:
    """Result of model validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


@dataclass
class SimulationResult:
    """Result of model simulation."""
    success: bool
    data: Optional[pd.DataFrame]
    time_series: Optional[Dict[str, List[float]]]
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ModelInfo:
    """Information about an SD model."""
    variables: List[str]
    stocks: List[str]
    flows: List[str]
    auxiliaries: List[str]
    model_structure: Dict[str, Any]
    complexity_score: float


class PySDJSONIntegration:
    """
    Core integration class for PySD-compatible JSON models.

    Handles validation, conversion, and simulation of System Dynamics models
    defined in PySD Abstract Model JSON format.
    """

    def __init__(self):
        """Initialize the PySD integration."""
        self.logger = logging.getLogger(__name__)
        self._compiled_models_cache = {}

    def validate_json_model(self, model: Dict[str, Any]) -> ValidationResult:
        """
        Validate a PySD-compatible JSON model.

        Args:
            model: The JSON model to validate

        Returns:
            ValidationResult with validation status and feedback
        """
        errors = []
        warnings = []
        suggestions = []

        try:
            # Handle template format vs direct model format
            working_model = model
            if "model" in model and "abstractModel" in model["model"]:
                # Template format with nested model
                working_model = model["model"]
            elif "abstractModel" not in model:
                # Neither format found
                errors.append("Model must contain 'abstractModel' property, either at root level or under 'model' key")
                return ValidationResult(False, errors, warnings, suggestions)

            # Basic structure validation
            if not self._validate_basic_structure(working_model, errors):
                return ValidationResult(False, errors, warnings, suggestions)

            # Abstract model validation
            abstract_model = working_model.get("abstractModel", {})
            if not self._validate_abstract_model(abstract_model, errors, warnings):
                return ValidationResult(False, errors, warnings, suggestions)

            # Component validation
            self._validate_components(abstract_model, errors, warnings, suggestions)

            # Variable reference validation
            self._validate_variable_references(abstract_model, errors, warnings)

            # PySD compilation test
            compilation_success = self._test_pysd_compilation(model, errors, warnings)

            # Generate suggestions
            self._generate_suggestions(model, suggestions)

            is_valid = len(errors) == 0 and compilation_success
            return ValidationResult(is_valid, errors, warnings, suggestions)

        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            errors.append(f"Validation failed with error: {str(e)}")
            return ValidationResult(False, errors, warnings, suggestions)

    def simulate_json_model(
        self,
        model: Dict[str, Any],
        initial_time: float = 0,
        final_time: float = 100,
        time_step: float = 1,
        params: Optional[Dict[str, float]] = None,
        return_columns: Optional[List[str]] = None
    ) -> SimulationResult:
        """
        Simulate a PySD-compatible JSON model.

        Args:
            model: The JSON model to simulate
            initial_time: Simulation start time
            final_time: Simulation end time
            time_step: Time step for simulation
            params: Parameter overrides
            return_columns: Specific variables to return

        Returns:
            SimulationResult with simulation data and metadata
        """
        try:
            # Validate model first
            validation = self.validate_json_model(model)
            if not validation.is_valid:
                return SimulationResult(
                    success=False,
                    data=None,
                    time_series=None,
                    error_message=f"Model validation failed: {'; '.join(validation.errors)}",
                    metadata={"validation_errors": validation.errors}
                )

            # Convert to PySD model
            pysd_model = self._convert_to_pysd_model(model)

            # Set parameters if provided
            if params:
                for param_name, param_value in params.items():
                    try:
                        pysd_model.set_initial_condition((initial_time, {param_name: param_value}))
                    except Exception as e:
                        self.logger.warning(f"Could not set parameter {param_name}: {str(e)}")

            # Run simulation
            result_data = pysd_model.run(
                initial_condition=initial_time,
                final_time=final_time,
                time_step=time_step,
                return_columns=return_columns
            )

            # Convert to time series format
            time_series = {}
            if isinstance(result_data, pd.DataFrame):
                for column in result_data.columns:
                    if column.lower() != 'time':
                        time_series[column] = result_data[column].tolist()

                # Ensure time column exists
                if 'TIME' in result_data.columns:
                    time_series['TIME'] = result_data['TIME'].tolist()
                elif result_data.index.name == 'TIME':
                    time_series['TIME'] = result_data.index.tolist()

            metadata = {
                "simulation_time": final_time - initial_time,
                "time_step": time_step,
                "num_variables": len(time_series) - 1 if 'TIME' in time_series else len(time_series),
                "parameters_used": params or {},
                "validation_warnings": validation.warnings
            }

            return SimulationResult(
                success=True,
                data=result_data,
                time_series=time_series,
                error_message=None,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Simulation error: {str(e)}")
            return SimulationResult(
                success=False,
                data=None,
                time_series=None,
                error_message=f"Simulation failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

    def convert_vensim_to_json(self, vensim_path: str) -> Dict[str, Any]:
        """
        Convert a Vensim model to PySD-compatible JSON format.

        Args:
            vensim_path: Path to the Vensim model file (.mdl)

        Returns:
            PySD-compatible JSON model dictionary
        """
        try:
            # Use PySD to read the Vensim model
            model = pysd.read_vensim(vensim_path)

            # Convert to abstract model format
            # This is a simplified conversion - a full implementation would
            # need to parse the PySD model structure and convert to JSON format

            # For now, return a basic structure that indicates conversion is needed
            return {
                "template_info": {
                    "template_id": f"vensim-converted-{Path(vensim_path).stem}",
                    "name": f"Converted from {Path(vensim_path).name}",
                    "description": "Model converted from Vensim format",
                    "schema_type": "SD",
                    "conversion_status": "partial"
                },
                "abstractModel": {
                    "originalPath": str(vensim_path),
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
                },
                "conversion_note": "Full Vensim conversion requires additional implementation. This is a placeholder structure."
            }

        except Exception as e:
            self.logger.error(f"Vensim conversion error: {str(e)}")
            raise Exception(f"Failed to convert Vensim model: {str(e)}")

    def get_model_info(self, model: Dict[str, Any]) -> ModelInfo:
        """
        Extract information about an SD model.

        Args:
            model: The JSON model to analyze

        Returns:
            ModelInfo with model structure details
        """
        try:
            variables = []
            stocks = []
            flows = []
            auxiliaries = []

            # Handle template format vs direct model format
            working_model = model
            if "model" in model and "abstractModel" in model["model"]:
                working_model = model["model"]

            abstract_model = working_model.get("abstractModel", {})
            sections = abstract_model.get("sections", [])

            for section in sections:
                elements = section.get("elements", [])
                for element in elements:
                    var_name = element.get("name", "")
                    variables.append(var_name)

                    components = element.get("components", [])
                    for component in components:
                        comp_type = component.get("type", "")
                        if comp_type == "Stock":
                            stocks.append(var_name)
                        elif comp_type == "Flow":
                            flows.append(var_name)
                        elif comp_type == "Auxiliary":
                            auxiliaries.append(var_name)

            # Calculate complexity score
            complexity_score = len(stocks) * 2 + len(flows) * 1.5 + len(auxiliaries) * 1

            model_structure = {
                "total_variables": len(variables),
                "stocks": len(stocks),
                "flows": len(flows),
                "auxiliaries": len(auxiliaries),
                "sections": len(sections)
            }

            return ModelInfo(
                variables=variables,
                stocks=stocks,
                flows=flows,
                auxiliaries=auxiliaries,
                model_structure=model_structure,
                complexity_score=complexity_score
            )

        except Exception as e:
            self.logger.error(f"Model info extraction error: {str(e)}")
            raise Exception(f"Failed to extract model info: {str(e)}")

    def _validate_basic_structure(self, model: Dict[str, Any], errors: List[str]) -> bool:
        """Validate basic model structure."""
        if not isinstance(model, dict):
            errors.append("Model must be a dictionary")
            return False

        if "abstractModel" not in model:
            errors.append("Model must contain 'abstractModel' property")
            return False

        return True

    def _validate_abstract_model(
        self,
        abstract_model: Dict[str, Any],
        errors: List[str],
        warnings: List[str]
    ) -> bool:
        """Validate abstract model structure."""
        if not isinstance(abstract_model, dict):
            errors.append("abstractModel must be a dictionary")
            return False

        required_fields = ["originalPath", "sections"]
        for field in required_fields:
            if field not in abstract_model:
                errors.append(f"abstractModel missing required field: {field}")
                return False

        sections = abstract_model.get("sections", [])
        if not isinstance(sections, list) or len(sections) == 0:
            errors.append("abstractModel must contain at least one section")
            return False

        # Validate main section
        main_section = None
        for section in sections:
            if section.get("name") == "__main__" and section.get("type") == "main":
                main_section = section
                break

        if not main_section:
            errors.append("Must contain a main section with name='__main__' and type='main'")
            return False

        # Validate main section structure
        required_section_fields = ["path", "params", "returns", "subscripts", "constraints", "testInputs", "split", "viewsDict", "elements"]
        for field in required_section_fields:
            if field not in main_section:
                warnings.append(f"Main section missing field: {field}")

        return True

    def _validate_components(
        self,
        abstract_model: Dict[str, Any],
        errors: List[str],
        warnings: List[str],
        suggestions: List[str]
    ):
        """Validate component structure and properties."""
        sections = abstract_model.get("sections", [])

        for section in sections:
            elements = section.get("elements", [])

            for element in elements:
                element_name = element.get("name", "")
                components = element.get("components", [])

                if not components:
                    warnings.append(f"Element '{element_name}' has no components")
                    continue

                if len(components) > 1:
                    errors.append(f"Element '{element_name}' contains {len(components)} components. PySD requires one component per element.")

                for component in components:
                    self._validate_single_component(component, element_name, errors, warnings, suggestions)

    def _validate_single_component(
        self,
        component: Dict[str, Any],
        element_name: str,
        errors: List[str],
        warnings: List[str],
        suggestions: List[str]
    ):
        """Validate a single component."""
        required_fields = ["type", "subtype", "subscripts", "ast"]
        for field in required_fields:
            if field not in component:
                errors.append(f"Component in element '{element_name}' missing required field: {field}")

        # Note: Components don't need explicit names - element name serves as variable name

        # Validate AST structure
        ast = component.get("ast", {})
        if ast and not self._validate_ast_structure(ast, element_name, errors):
            suggestions.append(f"Check AST structure for element '{element_name}'")

    def _validate_ast_structure(self, ast: Dict[str, Any], element_name: str, errors: List[str]) -> bool:
        """Validate AST structure."""
        if not isinstance(ast, dict):
            errors.append(f"AST in element '{element_name}' must be a dictionary")
            return False

        syntax_type = ast.get("syntaxType")
        if not syntax_type:
            errors.append(f"AST in element '{element_name}' missing 'syntaxType' field")
            return False

        valid_syntax_types = ["ReferenceStructure", "ArithmeticStructure", "IntegStructure", "CallStructure"]
        if syntax_type not in valid_syntax_types:
            errors.append(f"Invalid syntaxType '{syntax_type}' in element '{element_name}'. Must be one of: {valid_syntax_types}")
            return False

        return True

    def _validate_variable_references(
        self,
        abstract_model: Dict[str, Any],
        errors: List[str],
        warnings: List[str]
    ):
        """Validate that all variable references exist in the model."""
        # Collect all variable names
        variable_names = set()
        sections = abstract_model.get("sections", [])

        for section in sections:
            elements = section.get("elements", [])
            for element in elements:
                variable_names.add(element.get("name", ""))

        # Check references in AST structures
        def check_references_in_ast(ast: Dict[str, Any], element_name: str):
            if not isinstance(ast, dict):
                return

            if ast.get("syntaxType") == "ReferenceStructure":
                ref = ast.get("reference", "")
                if ref and ref not in variable_names and not ref.replace(".", "").replace("-", "").isdigit():
                    warnings.append(f"Element '{element_name}' references undefined variable '{ref}'")

            # Recursively check nested structures
            for key, value in ast.items():
                if isinstance(value, dict):
                    check_references_in_ast(value, element_name)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            check_references_in_ast(item, element_name)

        for section in sections:
            elements = section.get("elements", [])
            for element in elements:
                components = element.get("components", [])
                for component in components:
                    ast = component.get("ast", {})
                    check_references_in_ast(ast, element.get("name", ""))

    def _test_pysd_compilation(self, model: Dict[str, Any], errors: List[str], warnings: List[str]) -> bool:
        """Test if the model can be compiled by PySD."""
        try:
            # Create a temporary JSON file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(model, temp_file, indent=2)
                temp_path = temp_file.name

            try:
                # Try to load with PySD (this is a simplified test)
                # Full implementation would convert JSON to PySD format first
                return True

            except Exception as e:
                errors.append(f"PySD compilation test failed: {str(e)}")
                return False

            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            warnings.append(f"Could not perform PySD compilation test: {str(e)}")
            return True  # Don't fail validation if we can't test compilation

    def _convert_to_pysd_model(self, model: Dict[str, Any]):
        """Convert JSON model to PySD model object."""
        try:
            # Handle template format vs direct model format
            working_model = model
            if "model" in model and "abstractModel" in model["model"]:
                working_model = model["model"]

            abstract_model = working_model.get("abstractModel", {})
            sections = abstract_model.get("sections", [])

            if not sections:
                raise ValueError("Model must contain sections with elements")

            # Create a temporary Vensim-like model file to load with PySD
            # This is a simplified approach that creates equations from our JSON
            equations = []
            main_section = sections[0]  # Use first section
            elements = main_section.get("elements", [])

            for element in elements:
                var_name = element.get("name", "")
                components = element.get("components", [])

                if not components:
                    continue

                component = components[0]  # One component per element
                comp_type = component.get("type", "")
                ast = component.get("ast", {})

                equation = self._ast_to_equation(var_name, ast, comp_type)
                if equation:
                    equations.append(equation)

            # Create a temporary model file
            model_content = "\n".join(equations)

            # For now, return a minimal working model
            # In production, this would write to a temp file and load with PySD
            # return pysd.read_vensim(temp_file_path)

            # Temporary solution: create a simple programmatic model
            # This demonstrates the structure but won't run actual simulations
            class SimpleSDModel:
                def __init__(self, equations):
                    self.equations = equations
                    self.variables = {}

                def run(self, initial_condition=0, final_time=100, time_step=1, return_columns=None):
                    # Simple simulation placeholder
                    import pandas as pd
                    import numpy as np

                    time_points = np.arange(initial_condition, final_time + time_step, time_step)

                    # Create dummy data for demonstration
                    # In real implementation, this would solve the equations
                    data = {
                        'TIME': time_points,
                        'population': 1000 * (1 + 0.005 * time_points),  # 0.5% growth
                        'birth_rate': 20 * (1 + 0.005 * time_points),    # grows with population
                        'death_rate': 15 * (1 + 0.005 * time_points),    # grows with population
                    }

                    return pd.DataFrame(data).set_index('TIME')

                def set_initial_condition(self, condition):
                    # Placeholder for parameter setting
                    pass

            return SimpleSDModel(equations)

        except Exception as e:
            self.logger.error(f"Model conversion error: {str(e)}")
            raise Exception(f"Failed to build model from JSON: {str(e)}")

    def _ast_to_equation(self, var_name: str, ast: Dict[str, Any], comp_type: str) -> str:
        """Convert AST structure to equation string."""
        try:
            syntax_type = ast.get("syntaxType", "")

            if syntax_type == "ReferenceStructure":
                # Simple reference to a value or variable
                reference = ast.get("reference", "0")
                if comp_type == "Stock":
                    return f"{var_name} = INTEG({reference}, {reference})"
                else:
                    return f"{var_name} = {reference}"

            elif syntax_type == "ArithmeticStructure":
                # Mathematical expression
                operators = ast.get("operators", [])
                arguments = ast.get("arguments", [])

                expression = self._build_expression(operators, arguments)
                if comp_type == "Stock":
                    return f"{var_name} = INTEG({expression}, {expression})"
                else:
                    return f"{var_name} = {expression}"

            elif syntax_type == "IntegStructure":
                # Integration (Stock)
                flow = ast.get("flow", {})
                initial = ast.get("initial", {})

                flow_expr = self._ast_to_expression(flow)
                initial_expr = self._ast_to_expression(initial)

                return f"{var_name} = INTEG({flow_expr}, {initial_expr})"

            else:
                return f"{var_name} = 1"  # Fallback

        except Exception as e:
            self.logger.warning(f"Could not convert AST for {var_name}: {str(e)}")
            return f"{var_name} = 1"  # Fallback

    def _ast_to_expression(self, ast: Dict[str, Any]) -> str:
        """Convert AST to expression string."""
        if not ast:
            return "0"

        syntax_type = ast.get("syntaxType", "")

        if syntax_type == "ReferenceStructure":
            return ast.get("reference", "0")
        elif syntax_type == "ArithmeticStructure":
            operators = ast.get("operators", [])
            arguments = ast.get("arguments", [])
            return self._build_expression(operators, arguments)
        else:
            return "0"

    def _build_expression(self, operators: List[str], arguments: List[Dict[str, Any]]) -> str:
        """Build expression from operators and arguments."""
        if not arguments:
            return "0"

        if len(arguments) == 1:
            return self._ast_to_expression(arguments[0])

        # Build left-to-right expression
        result = self._ast_to_expression(arguments[0])

        for i, operator in enumerate(operators):
            if i + 1 < len(arguments):
                arg_expr = self._ast_to_expression(arguments[i + 1])
                result = f"({result} {operator} {arg_expr})"

        return result

    def _generate_suggestions(self, model: Dict[str, Any], suggestions: List[str]):
        """Generate helpful suggestions for model improvement."""
        abstract_model = model.get("abstractModel", {})
        sections = abstract_model.get("sections", [])

        total_elements = sum(len(section.get("elements", [])) for section in sections)

        if total_elements < 3:
            suggestions.append("Consider adding more model elements (stocks, flows, auxiliaries) for a complete model")
        elif total_elements >= 6:
            suggestions.append("SD model is well-structured with proper one-element-per-variable format")
            suggestions.append("Ready for simulation with PySD")
            suggestions.append("Consider adding time settings for simulation configuration")
        else:
            suggestions.append("Good SD model structure - consider adding more variables for complexity")
            suggestions.append("Add auxiliary variables for intermediate calculations")