"""
Text2Sim MCP Server - Multi-paradigm simulation engine.

This module provides the main entry point for the Text2Sim MCP server,
supporting Discrete-Event Simulation (DES) with SimPy and System Dynamics (SD)
with PySD through the Model Context Protocol.

The server offers comprehensive simulation capabilities including:
- Model validation and schema support
- Template management and discovery
- Model lifecycle management
- Statistical analysis and replication studies
- Conversational model development workflows
"""

import sys
from mcp.server.fastmcp import FastMCP
from .registry import register_all_tools, get_tool_summary


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server instance.

    Returns:
        Configured FastMCP server instance with all tools registered
    """
    # Initialize MCP server
    mcp = FastMCP("text2sim-mcp-server")

    # Register all simulation tools
    register_all_tools(mcp)

    return mcp


def main() -> None:
    """
    Main entry point for the MCP server.

    Initializes the server, registers all tools, and starts the MCP transport.
    This function is designed to be called from the command line or as a module.
    """
    try:
        # Print startup information
        print("[INFO] Starting Text2Sim MCP Server...", file=sys.stderr)

        # Create and configure server
        mcp = create_mcp_server()

        # Print registration summary
        summary = get_tool_summary()
        print(f"[INFO] Server initialized: {summary['total_tools']} tools across {len(summary['categories'])} categories", file=sys.stderr)

        # Print capability overview
        capabilities = summary['core_capabilities']
        print(f"[INFO] Simulation paradigms: {', '.join(capabilities['simulation_paradigms'])}", file=sys.stderr)
        print(f"[INFO] Model lifecycle: {', '.join(capabilities['model_lifecycle'])}", file=sys.stderr)
        print(f"[INFO] Template system: {', '.join(capabilities['template_system'])}", file=sys.stderr)

        print("[SUCCESS] Text2Sim MCP Server startup complete", file=sys.stderr)
        print("[INFO] Waiting for MCP client connection...", file=sys.stderr)

        # Start the MCP server
        mcp.run(transport='stdio')

    except KeyboardInterrupt:
        print("\n[INFO] Text2Sim MCP Server shutdown requested", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Text2Sim MCP Server startup failed: {e}", file=sys.stderr)
        sys.exit(1)


def get_server_info() -> dict:
    """
    Get comprehensive information about the server configuration.

    Returns:
        Dictionary with server metadata and capabilities
    """
    summary = get_tool_summary()

    return {
        "server_name": "text2sim-mcp-server",
        "version": "2.6.0",
        "description": "Multi-paradigm simulation engine with MCP integration",
        "capabilities": summary['core_capabilities'],
        "tool_summary": summary,
        "supported_schemas": ["DES", "SD"],
        "transport": "stdio",
        "features": [
            "Schema auto-detection and validation",
            "Template-based model development",
            "Model persistence and versioning",
            "Statistical analysis and replication studies",
            "Conversational workflow support",
            "Comprehensive error handling and guidance",
            "Domain-specific examples and documentation"
        ]
    }


# Create global server instance for module-level access
mcp = create_mcp_server()


if __name__ == "__main__":
    main()


    