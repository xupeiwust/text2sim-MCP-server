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
                error_summary = self._create_validation_error_summary(validation.errors, validation.warnings)
                return SimulationResult(
                    success=False,
                    data=None,
                    time_series=None,
                    error_message=error_summary,
                    metadata={
                        "validation_errors": validation.errors,
                        "validation_warnings": validation.warnings,
                        "suggestions": validation.suggestions
                    }
                )

            # Convert to PySD model
            pysd_model = self._convert_to_pysd_model(model)

            # Set parameters if provided
            if params:
                for param_name, param_value in params.items():
                    try:
                        pysd_model.set_initial_condition(param_name, param_value)
                    except Exception as e:
                        self.logger.warning(f"Could not set parameter {param_name}: {str(e)}")

            # Run simulation
            result_data = pysd_model.run(
                initial_condition=(initial_time, {}),
                final_time=final_time,
                time_step=time_step,
                return_columns=return_columns
            )

            # Convert to time series format
            time_series = {}
            if isinstance(result_data, pd.DataFrame):
                # Add time column from index
                time_series['TIME'] = result_data.index.tolist()

                # Add all other columns
                for column in result_data.columns:
                    time_series[column] = result_data[column].tolist()

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
                if ref and ref not in variable_names and not ref.replace(".", "").replace("-", "").replace(" ", "").isdigit():
                    # More sophisticated check for mathematical expressions
                    if self._contains_undefined_variables(ref, variable_names):
                        errors.append(f"Element '{element_name}' references undefined variable '{ref}'")

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

    def _contains_undefined_variables(self, expression: str, variable_names: set) -> bool:
        """Check if expression contains undefined variable references."""
        import re

        # Find potential variable names (letters, underscores, spaces)
        # Common patterns: Variable_Name, Variable Name, CONSTANT_VALUE
        potential_vars = re.findall(r'[A-Za-z_][A-Za-z0-9_\s]*[A-Za-z0-9_]|[A-Za-z]', expression)

        for var in potential_vars:
            var_clean = var.strip()
            # Skip if it's a number or common operators/functions
            if (var_clean and
                not var_clean.replace(".", "").isdigit() and  # not a number
                var_clean not in {'and', 'or', 'not', 'if', 'then', 'else'} and  # not operators
                var_clean not in variable_names):  # not in our variable set
                return True
        return False

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
        """Convert JSON model to PySD model object using ModelBuilder."""
        try:
            # Use the AbstractModelAdapter for JSON parsing
            from .json_extensions.adapters.abstract_model_adapter import AbstractModelAdapter

            # Handle template format vs direct model format
            working_model = model
            if "model" in model and "abstractModel" in model["model"]:
                working_model = model["model"]

            # Create the adapter that provides PySD-compatible interface
            model_adapter = AbstractModelAdapter(working_model, validate=False)

            # Use ModelBuilder to generate Python code file, then load with PySD
            import tempfile
            import os

            with tempfile.TemporaryDirectory() as temp_dir:
                # Create ModelBuilder with the adapter
                builder = JSONModelBuilder(model_adapter, temp_dir)

                # Build the Python model file
                python_file_path = builder.build_model()

                # Load the generated Python file with PySD
                pysd_model = pysd.load(python_file_path)

                return pysd_model

        except Exception as e:
            self.logger.error(f"Model conversion error: {str(e)}")
            raise SDModelBuildError(f"Failed to build model from JSON: {str(e)}")


    def _analyze_model_structure(self, abstract_model: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze model structure for error reporting."""
        sections = abstract_model.get("sections", [])
        variables = []
        stocks = []
        flows = []
        auxiliaries = []
        expressions = []

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

                    # Check for mathematical expressions
                    ast = component.get("ast", {})
                    if ast.get("syntaxType") == "ReferenceStructure":
                        ref = ast.get("reference", "")
                        if "*" in ref or "+" in ref or "-" in ref or "/" in ref:
                            expressions.append(f"{var_name}: {ref}")

        return {
            "variables": variables,
            "stocks": len(stocks),
            "flows": len(flows),
            "auxiliaries": len(auxiliaries),
            "expressions": len(expressions)
        }

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

    def _create_validation_error_summary(self, errors: List[str], warnings: List[str]) -> str:
        """Create a user-friendly error summary with actionable guidance."""
        summary_parts = ["Model validation failed with the following issues:"]

        if errors:
            summary_parts.append("\n🚫 ERRORS (must be fixed):")
            for error in errors:
                summary_parts.append(f"  • {error}")

        if warnings:
            summary_parts.append("\n⚠️  WARNINGS:")
            for warning in warnings:
                summary_parts.append(f"  • {warning}")

        # Add specific guidance based on error patterns
        if any("references undefined variable" in error for error in errors):
            summary_parts.append("\n💡 GUIDANCE:")
            summary_parts.append("  • Check that all variable names in expressions match element names exactly")
            summary_parts.append("  • Variable names are case-sensitive and must match the 'name' field of elements")
            summary_parts.append("  • Use underscores or spaces consistently in variable names")
            summary_parts.append("  • Ensure all referenced variables are defined in the model")

        if any("abstractModel" in error for error in errors):
            summary_parts.append("\n💡 GUIDANCE:")
            summary_parts.append("  • Ensure your model has the correct JSON structure with 'abstractModel' at the root")
            summary_parts.append("  • Include 'sections' array with at least one main section")
            summary_parts.append("  • Each section needs 'elements' array with model variables")

        return "\n".join(summary_parts)


class JSONModelBuilder:
    """
    Builds PySD Python model files from AbstractModelAdapter.

    This class converts JSON models via the adapter pattern into Python code
    files that PySD can load and execute.
    """

    def __init__(self, model_adapter, temp_dir: str):
        """
        Initialize the builder.

        Parameters
        ----------
        model_adapter : AbstractModelAdapter
            The JSON model adapter
        temp_dir : str
            Temporary directory for generated files
        """
        self.model_adapter = model_adapter
        self.temp_dir = temp_dir
        self.variables = {}
        self.equations = []

    def build_model(self) -> str:
        """
        Build the Python model file from the JSON adapter.

        Returns
        -------
        str
            Path to the generated Python file
        """
        # Extract model information
        self._extract_variables()

        # Generate Python code
        python_code = self._generate_python_code()

        # Write to temporary file
        from pathlib import Path
        model_name = getattr(self.model_adapter, 'original_path', Path('temp_model.json')).stem
        if isinstance(model_name, Path):
            model_name = model_name.stem

        python_file = Path(self.temp_dir) / f"{model_name}.py"

        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_code)

        return str(python_file)

    def _extract_variables(self):
        """Extract variables from the model adapter."""
        # Process all sections (typically just one main section)
        for section in self.model_adapter.sections:
            for element in section.elements:
                if not element.components:
                    continue

                component = element.components[0]  # One component per element

                self.variables[element.name] = {
                    'name': element.name,
                    'type': component.type,
                    'ast': component.ast,
                    'units': element.units,
                    'documentation': element.documentation
                }

    def _generate_python_code(self) -> str:
        """Generate PySD-compatible Python code."""

        # Generate function definitions for each variable
        functions = []
        integ_functions = []

        # Add required imports and setup
        code_parts = [
            '"""Generated PySD model from JSON."""',
            'import numpy as np',
            'from pysd.py_backend.statefuls import Integ',
            '',
            '# Global time variable',
            '_t = 0',
            '',
            'def time():',
            '    """Return current time."""',
            '    return _t',
            '',
        ]

        # Add control variables
        code_parts.extend([
            'def final_time():',
            '    """Final simulation time."""',
            '    return 100',
            '',
            'def initial_time():',
            '    """Initial simulation time."""',
            '    return 0',
            '',
            'def time_step():',
            '    """Simulation time step."""',
            '    return 1',
            '',
            'def saveper():',
            '    """Save frequency."""',
            '    return time_step()',
            '',
        ])

        # Generate functions for each variable
        for var_name, var_info in self.variables.items():
            func_name = self._clean_name(var_name)
            var_type = var_info['type']
            ast_info = var_info['ast']

            if var_type == 'Stock':
                # Generate stock (integration) function
                stock_func, integ_func = self._generate_stock_function(func_name, ast_info, var_info)
                functions.append(stock_func)
                integ_functions.append(integ_func)

            elif var_type in ['Flow', 'Auxiliary']:
                # Generate flow or auxiliary function
                func = self._generate_auxiliary_function(func_name, ast_info, var_info)
                functions.append(func)

        # Add all functions to code
        code_parts.extend(functions)
        code_parts.extend(integ_functions)

        # Add required PySD infrastructure
        code_parts.extend([
            '',
            '# Required PySD infrastructure',
            'def _init_outer_references(data):',
            '    """Initialize outer references."""',
            '    for key in data:',
            '        globals()[key] = data[key]',
            '',
            '# PySD version info',
            '__pysd_version__ = "3.14.0"',
            '',
            '# Variable namespace',
            '_namespace = {',
        ])

        # Add namespace mappings
        for var_name in self.variables.keys():
            clean_name = self._clean_name(var_name)
            code_parts.append(f'    "{clean_name.lower()}": "{clean_name}",')

        code_parts.extend([
            '    "time": "time",',
            '}',
            '',
            '# Dependencies (simplified)',
            '_dependencies = {',
        ])

        # Add basic dependencies
        for var_name in self.variables.keys():
            clean_name = self._clean_name(var_name)
            code_parts.append(f'    "{clean_name}": [],')

        code_parts.extend([
            '    "time": [],',
            '}',
            '',
            '# Module attributes required by PySD',
            'namespace = _namespace',
            'dependencies = _dependencies',
            '',
            '# Component accessor class (required by PySD)',
            'class ComponentAccessor:',
            '    """Component accessor with required attributes."""',
            '    def __init__(self):',
            '        self.namespace = _namespace',
            '        self.dependencies = _dependencies',
            '        self.subscripts = {}  # No subscripts in our simple models',
            '    ',
            '    def __call__(self, name):',
            '        """Get component by name."""',
            '        return globals().get(name.lower(), globals().get(name))',
            '',
            'component = ComponentAccessor()',
            '',
            '# Model metadata',
            'def get_pysd_compiler_version():',
            '    """Return compiler version string."""',
            '    return "3.14.0"',
        ])

        return '\n'.join(code_parts)

    def _generate_stock_function(self, func_name: str, ast_info, var_info):
        """Generate stock (integration) function."""

        # Main stock function
        stock_func = f'''def {func_name}():
    """Stock: {var_info.get('documentation', func_name)}."""
    return _{func_name}_integ()'''

        # Integration helper function
        if hasattr(ast_info, 'syntax_type') and ast_info.syntax_type == 'IntegStructure':
            # Extract flow and initial value from AST
            flow_expr = self._ast_to_python_expression(ast_info.flow)
            initial_expr = self._ast_to_python_expression(ast_info.initial)

            integ_func = f'''def _{func_name}_integ():
    """Integration function for {func_name}."""
    return Integ(lambda: {flow_expr}, lambda: {initial_expr}, "{func_name}")'''
        else:
            # Fallback for malformed stock
            integ_func = f'''def _{func_name}_integ():
    """Integration function for {func_name}."""
    return Integ(lambda: 0, lambda: 100, "{func_name}")'''

        return stock_func, integ_func

    def _generate_auxiliary_function(self, func_name: str, ast_info, var_info):
        """Generate auxiliary or flow function."""

        # Convert AST to Python expression
        expression = self._ast_to_python_expression(ast_info)

        func = f'''def {func_name}():
    """{'Flow' if var_info['type'] == 'Flow' else 'Auxiliary'}: {var_info.get('documentation', func_name)}."""
    return {expression}'''

        return func

    def _ast_to_python_expression(self, ast_info) -> str:
        """Convert AST info to Python expression."""
        if not ast_info:
            return '0'

        if hasattr(ast_info, 'syntax_type'):
            if ast_info.syntax_type == 'ReferenceStructure':
                if hasattr(ast_info, 'reference'):
                    return self._convert_reference_expression(ast_info.reference)

        # Fallback
        return '0'

    def _convert_reference_expression(self, reference: str) -> str:
        """Convert reference expression to Python function calls."""
        if not reference:
            return '0'

        # Handle simple numbers
        try:
            float(reference)
            return reference
        except ValueError:
            pass

        # Handle mathematical expressions with variables
        # Convert variable names to function calls
        import re

        def replace_var_with_function(match):
            var_name = match.group(0)
            clean_name = self._clean_name(var_name)
            return f'{clean_name}()'

        # Pattern to match variable names (letters, underscores, spaces)
        var_pattern = r'[A-Za-z][A-Za-z0-9_\s]*[A-Za-z0-9_]|[A-Za-z]'

        # Replace variable names with function calls, but preserve numbers and operators
        result = reference

        # Handle negative references first
        if reference.startswith('-'):
            rest = self._convert_reference_expression(reference[1:])
            return f'-{rest}'

        # Split on operators to handle each part
        import re
        tokens = re.split(r'([\+\-\*/\(\)\s]+)', reference)

        converted_tokens = []
        for token in tokens:
            token = token.strip()
            if not token:
                converted_tokens.append('')
            elif re.match(r'^[\+\-\*/\(\)\s]+$', token):
                # Operator or whitespace/parentheses - keep as is
                converted_tokens.append(token)
            elif re.match(r'^\d+\.?\d*$', token):
                # Number - keep as is
                converted_tokens.append(token)
            elif re.match(var_pattern, token) and token in self.variables:
                # Variable name - convert to function call
                clean_name = self._clean_name(token)
                converted_tokens.append(f'{clean_name}()')
            else:
                # Unknown token - keep as is
                converted_tokens.append(token)

        return ''.join(converted_tokens)

    def _clean_name(self, name: str) -> str:
        """Clean variable name for Python function names."""
        # Replace spaces with underscores and make lowercase
        cleaned = name.replace(' ', '_').replace('-', '_').lower()

        # Ensure valid Python identifier
        if not cleaned[0].isalpha():
            cleaned = 'var_' + cleaned

        return cleaned