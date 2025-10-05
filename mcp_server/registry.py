"""
Centralized tool registration for MCP server.

This module manages the registration of all simulation tools with the FastMCP server,
providing organized registration by domain and comprehensive tool discovery capabilities.
"""

from typing import Dict, List
from mcp.server.fastmcp import FastMCP

from .tools.des_tools import register_des_tools
from .tools.sd_tools import register_sd_tools
from .tools.model_mgmt_tools import register_model_mgmt_tools
from .tools.validation_tools import register_validation_tools
from .tools.template_tools import register_template_tools


def register_all_tools(mcp: FastMCP) -> None:
    """
    Register all MCP tools with the server in logical order.

    This function orchestrates the registration of all tool domains,
    ensuring dependencies are available and tools are organized properly.

    Registration Order:
    1. Validation tools - Core validation functionality needed by other tools
    2. DES tools - Discrete-Event Simulation capabilities
    3. SD tools - System Dynamics simulation capabilities
    4. Model management tools - Model lifecycle and persistence
    5. Template tools - Template management and discovery

    Args:
        mcp: FastMCP server instance to register tools with
    """
    print("[INFO] Registering MCP tools...", file=sys.stderr)

    try:
        # Register validation tools first (used by other tool domains)
        register_validation_tools(mcp)
        print("  [SUCCESS] Validation tools registered", file=sys.stderr)

        # Register simulation tools
        register_des_tools(mcp)
        print("  [SUCCESS] DES simulation tools registered", file=sys.stderr)

        register_sd_tools(mcp)
        print("  [SUCCESS] SD simulation tools registered", file=sys.stderr)

        # Register model management tools
        register_model_mgmt_tools(mcp)
        print("  [SUCCESS] Model management tools registered", file=sys.stderr)

        # Register template management tools
        register_template_tools(mcp)
        print("  [SUCCESS] Template management tools registered", file=sys.stderr)

        print("[SUCCESS] All MCP tools registered successfully", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Tool registration failed: {e}", file=sys.stderr)
        raise


def get_registered_tools() -> Dict[str, List[str]]:
    """
    Get information about registered tools organized by category.

    Returns a dictionary mapping tool categories to lists of tool names,
    useful for documentation, testing, and tool discovery.

    Returns:
        Dictionary with tool categories as keys and tool name lists as values
    """
    return {
        "validation": [
            "validate_model",
            "get_schema_help",
            "help_validation"
        ],
        "des_simulation": [
            "simulate_des",
            "run_multiple_simulations"
        ],
        "sd_simulation": [
            "simulate_sd",
            "convert_vensim_to_sd_json",
            "get_sd_model_info"
        ],
        "model_management": [
            "save_model",
            "load_model",
            "export_model",
            "delete_model"
        ],
        "template_management": [
            "list_templates",
            "load_template",
            "save_template",
            "delete_template"
        ]
    }


def get_tool_count() -> int:
    """
    Get total number of registered tools.

    Returns:
        Total count of all registered MCP tools
    """
    tools = get_registered_tools()
    return sum(len(tool_list) for tool_list in tools.values())


def get_tools_by_category(category: str) -> List[str]:
    """
    Get tools for a specific category.

    Args:
        category: Tool category name

    Returns:
        List of tool names in the specified category

    Raises:
        KeyError: If category doesn't exist
    """
    tools = get_registered_tools()
    if category not in tools:
        available_categories = list(tools.keys())
        raise KeyError(f"Category '{category}' not found. Available: {available_categories}")

    return tools[category]


def validate_tool_registration(mcp: FastMCP) -> Dict[str, bool]:
    """
    Validate that all expected tools are properly registered.

    This function checks the MCP server to ensure all tools from
    get_registered_tools() are actually available.

    Args:
        mcp: FastMCP server instance to check

    Returns:
        Dictionary mapping tool names to registration status (True/False)
    """
    registered_tools = get_registered_tools()
    validation_results = {}

    for category, tool_names in registered_tools.items():
        for tool_name in tool_names:
            # Check if tool is registered in MCP server
            # Note: This is a simplified check - actual implementation
            # would depend on FastMCP's introspection capabilities
            try:
                # Attempt to access the tool (implementation-dependent)
                is_registered = hasattr(mcp, '_tools') and tool_name in getattr(mcp, '_tools', {})
                validation_results[tool_name] = is_registered
            except AttributeError:
                # Fallback: assume registered if no errors during registration
                validation_results[tool_name] = True

    return validation_results


def get_tool_summary() -> Dict[str, any]:
    """
    Get comprehensive summary of all registered tools.

    Returns:
        Dictionary with registration statistics and tool information
    """
    tools = get_registered_tools()

    return {
        "total_tools": get_tool_count(),
        "categories": list(tools.keys()),
        "category_counts": {category: len(tool_list) for category, tool_list in tools.items()},
        "tools_by_category": tools,
        "registration_order": [
            "validation",
            "des_simulation",
            "sd_simulation",
            "model_management",
            "template_management"
        ],
        "core_capabilities": {
            "simulation_paradigms": ["DES", "SD"],
            "model_lifecycle": ["create", "validate", "save", "load", "export"],
            "template_system": ["create", "discover", "customize", "share"],
            "documentation": ["schema_help", "validation_guide", "examples"]
        }
    }


# Import sys for stderr printing
import sys