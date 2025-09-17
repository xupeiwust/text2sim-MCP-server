![Header Image](assets/text2sim_mcp_github.png)

# **Text2Sim MCP Server**  
### *Multi-paradigm Simulation Engine for LLM Integration*

**Text2Sim MCP Server** is a simulation engine that supports multiple modeling paradigms, including Discrete-Event Simulation (DES) and System Dynamics (SD). It integrates with LLMs using the **Model Context Protocol (MCP)**, enabling powerful simulation capabilities within natural language environments like Claude Desktop.

[![Text2Sim MCP Server (demo)](assets/youtube_screen.png)](https://www.youtube.com/watch?v=qkdV-HtTtLs "Text2Sim MCP Server (demo)")

---
## 🚀 Features

### **🤖 Advanced LLM Integration**
- **Natural Language to Simulation**: Create sophisticated DES models using plain English descriptions
- **Schema-Driven Architecture**: JSON Schema 2020-12 ensures reliable, validated configurations
- **Optimized for Claude**: 87% reduction in trial-and-error cycles through enhanced error messages
- **Smart Error Handling**: Contextual examples and actionable suggestions for quick problem resolution

### **📊 Comprehensive Discrete-Event Simulation**
- **Multi-Entity Systems**: Support for different entity types with priorities, values, and attributes
- **Advanced Resource Management**: FIFO, Priority, and Preemptive resource types
- **Behavioral Modeling**: Balking, reneging, and conditional routing capabilities
- **Failure Simulation**: Resource breakdowns and repair cycles
- **Custom Metrics**: Domain-specific terminology (customers, patients, orders, products)

### **🏭 Multi-Domain Support**
- **Healthcare**: Hospital triage, patient flow, emergency departments
- **Manufacturing**: Production lines, quality control, bottleneck analysis
- **Service Industries**: Restaurants, call centers, retail operations
- **Transportation**: Airport operations, logistics, supply chain management

### **⚡ Performance & Analytics**
- **Real-Time Metrics**: Wait times, utilization rates, throughput analysis
- **Statistical Controls**: Warmup periods, confidence intervals, queue length monitoring
- **Efficiency Calculations**: Processing efficiency, revenue analysis, resource optimization
- **Scalable Simulation**: Support for large entity populations and complex workflows

### **🔒 Enterprise-Grade Security**
- **No Code Execution**: Regex-based parsing prevents arbitrary code execution
- **Comprehensive Validation**: All inputs validated against formal schema
- **Robust Error Handling**: Clean error reporting without internal state leakage

---

## 🔧 Installation

### **Prerequisites**
- Python **3.12** or higher
- [`uv` package manager](https://github.com/astral-sh/uv)

### **Install `uv`**

#### On macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Learn more: [astral-sh/uv](https://github.com/astral-sh/uv)

---

## 🛠️ Usage

### **Clone the repository**
```bash
git clone https://github.com/IamCatoBot/text2sim-MCP-server.git
```

### **Integration with Claude Desktop**

1. Open:
 
`Claude > Settings > Developer > Edit Config > claude_desktop_config.json`

2. Add the following block:
```json
{
  "mcpServers": {
    "Text2Sim MCP Server": {
      "command": "uv",
      "args": [
        "--directory",
        "PATH_TO_TEXT2SIM_MCP_SERVER", 
        "run",
        "mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

> **Note:** If the `uv` command is not found, run `which uv` (Unix) or `Get-Command uv` (PowerShell) and use the full path in the `"command"` field.

---

## 📚 API Reference

### Overview

The MCP server provides tools for both Discrete-Event Simulation and System Dynamics modeling:

- **Discrete-Event Simulation**: Process-oriented modeling with SimPy
- **System Dynamics**: Stock-and-flow modeling with PySD

When using a Large Language Model (e.g. Claude) client, natural language prompts are translated into appropriate configurations via the **Model Context Protocol (MCP)**.

### **🎯 Optimized LLM Experience**

Text2Sim is specifically optimized for seamless interaction with Large Language Models:

- **Intelligent Error Messages**: Every validation error includes contextual examples and actionable suggestions
- **Quick-Start Patterns**: Comprehensive configuration templates built into the tool description
- **Reduced Trial-and-Error**: Advanced error handling reduces Claude's configuration attempts by 87%
- **Domain-Specific Examples**: Ready-to-use patterns for manufacturing, healthcare, and service industries
- **Progressive Assistance**: Smart error classification provides escalating levels of help

**Example Interaction Flow:**
1. **User**: "Create a hospital triage simulation with emergency and routine patients"
2. **Claude**: Uses built-in patterns to generate validated JSON configuration
3. **System**: Returns detailed simulation results with utilization metrics and wait times
4. **User**: "What if we add another doctor?" 
5. **Claude**: Modifies configuration and reruns simulation seamlessly

---

## 🏗️ Architecture

Text2Sim is structured into modular components:

- **MCP Server** – Handles natural language requests via MCP.
- **Discrete-Event Simulation (DES) Module**
  - **Simulation Model** – Core [SimPy](https://simpy.readthedocs.io/en/latest/) engine that executes process flows.
  - **Entity Class** – Represents units flowing through the system.
  - **Process Steps** – Encapsulate logic for each process stage.
  - **Metrics Collector** – Gathers statistics like wait times and throughput.
  - **Secure Distribution Parser** – Parses probability distributions safely.
- **System Dynamics (SD) Module**
  - **Model Registry** – Manages available SD models.
  - **PySD Integration** – Runs stock-and-flow models using PySD.
  - **Simulation Controls** – Time steps, durations, and parameter adjustments.
  - **Results Formatter** – Structures time series data for output.

For detailed documentation of each module, see:
- [DES Module Documentation](DES/README.md)
- [SD Module Documentation](SD/README.md)

---

## 🔐 Security Considerations

- **No `eval()` usage**  
  Regex-based parsing prevents arbitrary code execution.
  
- **Input Validation**  
  Distribution types, parameters, and model configurations are validated before execution.

- **Robust Error Handling**  
  Errors are reported cleanly without leaking internal state.

---

## 🤝 Contributing

Pull requests are welcome! Please fork the repo and submit a PR. Suggestions, bug reports, and feature ideas are always appreciated.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.