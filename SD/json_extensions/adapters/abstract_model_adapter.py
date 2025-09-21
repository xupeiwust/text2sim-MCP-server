"""
Adapter classes that provide dataclass-like interfaces over JSON data.

These adapters maintain backward compatibility with the existing PySD API
while working with JSON Schema-based model representation.
"""

from pathlib import Path
from typing import List, Dict, Any, Union, Tuple, Optional
from ..schema.validator import SchemaValidator


class AbstractSyntaxAdapter:
    """Adapter for AbstractSyntax structures from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        if json_data is None:
            self._data = None
        else:
            self._data = json_data
            self._type = json_data.get('syntaxType', 'Unknown')

    @property
    def syntax_type(self) -> str:
        """Get the syntax type."""
        return self._type if self._data else None

    def __getattr__(self, name: str) -> Any:
        """Provide access to all properties from JSON data."""
        if self._data is None:
            return None

        # Handle common property mappings
        if name == 'delay_time' and 'delayTime' in self._data:
            return AbstractSyntaxAdapter(self._data['delayTime'])
        elif name == 'smooth_time' and 'smoothTime' in self._data:
            return AbstractSyntaxAdapter(self._data['smoothTime'])
        elif name == 'average_time' and 'averageTime' in self._data:
            return AbstractSyntaxAdapter(self._data['averageTime'])
        elif name == 'x_row_or_col' and 'xRowOrCol' in self._data:
            return self._data['xRowOrCol']
        elif name == 'time_row_or_col' and 'timeRowOrCol' in self._data:
            return self._data['timeRowOrCol']

        value = self._data.get(name)

        # Recursively wrap nested structures
        if isinstance(value, dict) and 'syntaxType' in value:
            return AbstractSyntaxAdapter(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict) and 'syntaxType' in value[0]:
            return [AbstractSyntaxAdapter(item) for item in value]

        return value

    def __str__(self) -> str:
        if self._data is None:
            return "None"
        return f"{self._type}({self._data})"


class AbstractComponentAdapter:
    """Adapter for AbstractComponent from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def subscripts(self) -> Tuple[List[str], List[List[str]]]:
        """Get subscripts tuple."""
        subs_data = self._data.get('subscripts', [[], []])
        return (subs_data[0], subs_data[1])

    @property
    def ast(self) -> AbstractSyntaxAdapter:
        """Get AST as adapter."""
        return AbstractSyntaxAdapter(self._data.get('ast'))

    @property
    def type(self) -> str:
        """Get component type."""
        return self._data.get('type', 'Auxiliary')

    @property
    def subtype(self) -> str:
        """Get component subtype."""
        return self._data.get('subtype', 'Normal')

    @property
    def arguments(self) -> str:
        """Get lookup arguments (for lookup components)."""
        # Only lookup components should carry arguments (typically 'x').
        # Default to empty string for non-lookup components so they generate
        # zero-argument functions.
        return self._data.get('arguments', '')

    @property
    def keyword(self) -> Optional[str]:
        """Get data keyword (for data components)."""
        return self._data.get('keyword')


class AbstractElementAdapter:
    """Adapter for AbstractElement from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def name(self) -> str:
        """Get element name."""
        return self._data.get('name', '')

    @property
    def components(self) -> List[AbstractComponentAdapter]:
        """Get components as adapters."""
        components_data = self._data.get('components', [])
        return [AbstractComponentAdapter(comp) for comp in components_data]

    @property
    def units(self) -> str:
        """Get element units."""
        return self._data.get('units', '')

    @property
    def limits(self) -> Tuple[Optional[float], Optional[float]]:
        """Get element limits."""
        limits_data = self._data.get('limits', [None, None])
        return tuple(limits_data)

    @property
    def documentation(self) -> str:
        """Get element documentation."""
        return self._data.get('documentation', '')


class AbstractSubscriptRangeAdapter:
    """Adapter for AbstractSubscriptRange from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def name(self) -> str:
        """Get subscript range name."""
        return self._data.get('name', '')

    @property
    def subscripts(self) -> Union[List[str], str, Dict[str, Any]]:
        """Get subscripts definition."""
        return self._data.get('subscripts', [])

    @property
    def mapping(self) -> List[str]:
        """Get subscript mapping."""
        return self._data.get('mapping', [])


class AbstractConstraintAdapter:
    """Adapter for AbstractConstraint from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def name(self) -> str:
        """Get constraint name."""
        return self._data.get('name', '')

    @property
    def subscripts(self) -> Union[List[str], str, Dict[str, Any]]:
        """Get subscripts definition."""
        return self._data.get('subscripts', [])

    @property
    def expression(self) -> str:
        """Get constraint expression."""
        return self._data.get('expression', '')


class AbstractTestInputAdapter:
    """Adapter for AbstractTestInput from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def name(self) -> str:
        """Get test input name."""
        return self._data.get('name', '')

    @property
    def subscripts(self) -> Union[List[str], str, Dict[str, Any]]:
        """Get subscripts definition."""
        return self._data.get('subscripts', [])

    @property
    def expression(self) -> str:
        """Get test input expression."""
        return self._data.get('expression', '')


class AbstractSectionAdapter:
    """Adapter for AbstractSection from JSON."""

    def __init__(self, json_data: Dict[str, Any]):
        self._data = json_data

    @property
    def name(self) -> str:
        """Get section name."""
        return self._data.get('name', '')

    @property
    def path(self) -> Path:
        """Get section path."""
        path_str = self._data.get('path', '')
        if path_str:
            path = Path(path_str)
            # For JSON models, generate Python output path
            if path.suffix.lower() == '.json':
                return path.with_suffix('.py')
            return path
        return Path()

    @property
    def type(self) -> str:
        """Get section type."""
        return self._data.get('type', 'main')

    @property
    def params(self) -> List[str]:
        """Get section parameters."""
        return self._data.get('params', [])

    @property
    def returns(self) -> List[str]:
        """Get section returns."""
        return self._data.get('returns', [])

    @property
    def subscripts(self) -> Tuple[AbstractSubscriptRangeAdapter, ...]:
        """Get subscripts as tuple of adapters."""
        subscripts_data = self._data.get('subscripts', [])
        return tuple(
            AbstractSubscriptRangeAdapter(sr)
            for sr in subscripts_data
        )

    @property
    def elements(self) -> Tuple[AbstractElementAdapter, ...]:
        """Get elements as tuple of adapters."""
        elements_data = self._data.get('elements', [])
        return tuple(
            AbstractElementAdapter(elem)
            for elem in elements_data
        )

    @property
    def constraints(self) -> Tuple[AbstractConstraintAdapter, ...]:
        """Get constraints as tuple of adapters."""
        constraints_data = self._data.get('constraints', [])
        return tuple(
            AbstractConstraintAdapter(constraint)
            for constraint in constraints_data
        )

    @property
    def test_inputs(self) -> Tuple[AbstractTestInputAdapter, ...]:
        """Get test inputs as tuple of adapters."""
        test_inputs_data = self._data.get('testInputs', [])
        return tuple(
            AbstractTestInputAdapter(ti)
            for ti in test_inputs_data
        )

    @property
    def split(self) -> bool:
        """Get split flag."""
        return self._data.get('split', False)

    @property
    def views_dict(self) -> Optional[Dict[str, Any]]:
        """Get views dictionary."""
        return self._data.get('viewsDict')


class AbstractModelAdapter:
    """
    Adapter that provides dataclass-like interface over JSON schema data.

    Maintains backward compatibility with existing PySD code while working
    with JSON Schema representation internally.
    """

    def __init__(self, json_data: Dict[str, Any], validate: bool = True):
        """
        Initialize adapter with JSON data.

        Parameters
        ----------
        json_data : Dict[str, Any]
            JSON model data conforming to schema
        validate : bool, optional
            Whether to validate JSON data, by default True
        """
        if validate:
            validator = SchemaValidator()
            result = validator.validate(json_data)
            if not result.is_valid:
                raise ValueError(f"Invalid JSON model data: {result}")

        self._data = json_data['abstractModel']
        self._full_data = json_data

    @property
    def original_path(self) -> Path:
        """Get original model file path."""
        path_str = self._data.get('originalPath', '')
        return Path(path_str) if path_str else Path()

    @property
    def sections(self) -> Tuple[AbstractSectionAdapter, ...]:
        """Get sections as tuple of adapters."""
        sections_data = self._data.get('sections', [])
        return tuple(
            AbstractSectionAdapter(section)
            for section in sections_data
        )

    def get_json_data(self) -> Dict[str, Any]:
        """
        Get the underlying JSON data.

        Returns
        -------
        Dict[str, Any]
            The complete JSON model data
        """
        return self._full_data

    def __getattr__(self, name: str) -> Any:
        """Provide access to any additional properties."""
        return self._data.get(name)

    def __str__(self) -> str:
        return f"AbstractModelAdapter: {self.original_path}"

    def dump(self, depth: Optional[int] = None, indent: str = "") -> str:
        """
        Dump the model to a printable version (compatibility method).

        Parameters
        ----------
        depth : Optional[int], optional
            Depth levels to show, by default None (all)
        indent : str, optional
            Indent string, by default ""

        Returns
        -------
        str
            String representation of the model
        """
        if depth == 0:
            return self.__str__()

        result = [self.__str__()]

        if depth is None or depth > 0:
            new_depth = None if depth is None else depth - 1
            for i, section in enumerate(self.sections):
                section_str = f"{indent}Section {i}: {section.name} ({section.type})"
                result.append(section_str)

                if new_depth != 0:
                    result.append(f"{indent}  Elements: {len(section.elements)}")
                    result.append(f"{indent}  Subscripts: {len(section.subscripts)}")

        return "\n".join(result)