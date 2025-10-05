"""
Text2Sim MCP Server Package.

Multi-paradigm simulation engine supporting Discrete-Event Simulation (DES) with SimPy
and System Dynamics (SD) with PySD through the Model Context Protocol (MCP).

This package provides a modular architecture for simulation tools with domain separation,
shared utilities, and centralized registration.
"""

__version__ = "2.6.0"
__author__ = "Text2Sim Development Team"
__description__ = "Multi-paradigm simulation engine with MCP integration"

from .server import mcp, main, create_mcp_server, get_server_info
from .registry import (
    register_all_tools,
    get_registered_tools,
    get_tool_count,
    get_tools_by_category,
    get_tool_summary
)

# Shared utilities available at package level
from .shared import (
    MCPErrorHandler,
    ResponseBuilder,
    integration_manager,
    SDIntegrationError,
    SDValidationError,
    SDModelBuildError,
    SDSimulationError
)

__all__ = [
    # Core server functionality
    "mcp",
    "main",
    "create_mcp_server",
    "get_server_info",

    # Tool registration and discovery
    "register_all_tools",
    "get_registered_tools",
    "get_tool_count",
    "get_tools_by_category",
    "get_tool_summary",

    # Shared utilities
    "MCPErrorHandler",
    "ResponseBuilder",
    "integration_manager",
    "SDIntegrationError",
    "SDValidationError",
    "SDModelBuildError",
    "SDSimulationError"
]