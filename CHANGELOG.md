# 📋 Changelog

All notable changes to the Text2Sim MCP Server project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2024-09-17 - **Schema-Driven Architecture**

### 🎯 **Major Release: Complete System Redesign**

This release represents a fundamental transformation from a basic DES tool to a comprehensive, schema-driven simulation platform. The system now enables non-coders to create sophisticated simulations through declarative JSON configuration.

### ✨ **Added**

#### **🏗️ Core Architecture**
- **Schema-Driven Validation**: JSON Schema 2020-12 for comprehensive input validation
- **Unified Simulation Model**: Single model handling all complexity levels
- **Enhanced Metrics Collection**: Configurable metric names and advanced statistics
- **Comprehensive Error Handling**: Clear, actionable error messages

#### **📊 Schema Features**
- **Entity Management**: Multiple entity types with priorities, values, and custom attributes
- **Resource Types**: Full SimPy resource support (FIFO, Priority, Preemptive)
- **Processing Rules**: Sequential steps with conditional service time distributions
- **Behavioral Rules**: Balking and reneging with priority-based multipliers
- **Simple Routing**: Conditional routing based on entity attributes
- **Failure Modeling**: Basic resource failure and repair cycles
- **Arrival Patterns**: Both continuous arrival and fixed batch support
- **Custom Metrics**: Domain-specific terminology (customers, patients, orders)
- **Statistics Control**: Warmup periods, utilization tracking, queue length monitoring

#### **🔧 Implementation Components**
- **`DESConfigValidator`**: Schema loading, validation, and normalization
- **`UnifiedSimulationModel`**: Comprehensive SimPy-based simulation engine
- **`EnhancedMetricsCollector`**: Advanced metrics with custom naming
- **Distribution Parser**: Support for uniform, normal, exponential distributions

#### **📁 File Organization**
- **`schemas/DES/`**: Organized schema directory with comprehensive documentation
- **`des-simpy-compatible-schema.json`**: Complete JSON Schema specification
- **`schemas/DES/README.md`**: Detailed schema documentation with examples
- **`schemas/DES/json-to-simulation-flow.md`**: Technical transformation guide

#### **🎯 Example Configurations**
- **Coffee Shop**: Basic service system with balking and priority
- **Hospital Triage**: Complex multi-stage system with routing and preemption
- **Manufacturing**: Process flow with failures and quality control

### 🔄 **Changed**

#### **🎛️ API Evolution**
- **`simulate_des` tool**: Now accepts rich JSON configurations instead of simple parameters
- **Error Reporting**: Detailed schema validation errors with path information
- **Result Format**: Enhanced metrics with efficiency calculations and custom names

#### **🏗️ Architecture Improvements**
- **Single Model**: Replaced two-tier system (basic/advanced) with unified approach
- **Configuration-Driven**: Business logic now defined in JSON rather than code
- **Validation-First**: All inputs validated against schema before simulation

### 🗑️ **Removed**

#### **🧹 Legacy Components**
- **`SimulationModel`**: Replaced by `UnifiedSimulationModel`
- **`AdvancedSimulationModel`**: Functionality merged into unified model
- **`CoffeeShopModel`**: Replaced by generic, configurable approach
- **Two-Tier Detection**: No longer needed with unified architecture
- **Hard-coded Scenarios**: All scenarios now configuration-driven

#### **🔧 Deprecated Functions**
- **`validate_config()`**: Replaced by `DESConfigValidator`
- **`prepare_simulation_config()`**: Functionality integrated into validator
- **`_is_complex_scenario()`**: No longer needed with unified model

### 🐛 **Fixed**

#### **🔧 Simulation Engine**
- **Generator Return Issue**: Fixed `simulate_des` returning generator instead of results
- **Entity Accounting**: Corrected customer counting discrepancies
- **Metric Calculations**: Fixed efficiency and average value calculations
- **Priority Handling**: Proper SimPy priority implementation (lower = higher priority)

#### **📊 Schema Validation**
- **Pattern Properties**: Fixed regex conflicts in `processing_rules`
- **Distribution Parsing**: Corrected function vs. value return issues
- **Priority Multipliers**: Fixed regex validation for priority ranges
- **Mutual Exclusivity**: Proper enforcement of `arrival_pattern` XOR `num_entities`

#### **🎯 Configuration Handling**
- **Resource References**: Validated all resource references in rules
- **Probability Validation**: Ensured entity type probabilities sum to 1.0
- **Default Application**: Proper schema default value application

### 🚀 **Performance**

#### **⚡ Optimizations**
- **Single Validation Pass**: Efficient schema validation with default application
- **Streamlined Simulation**: Unified model reduces overhead
- **Selective Statistics**: Configurable statistics collection for performance tuning

#### **📈 Scalability**
- **Memory Efficient**: Optimized entity and metrics handling
- **Warmup Support**: Steady-state analysis with configurable warmup periods
- **Batch Processing**: Support for large entity populations

### 🧪 **Testing & Validation**

#### **✅ Comprehensive Testing**
- **Schema Validation**: Extensive JSON Schema compliance testing
- **Simulation Accuracy**: Verified against known DES principles
- **Edge Cases**: Robust handling of boundary conditions
- **Performance Testing**: Validated with large-scale simulations

#### **📋 Example Scenarios**
- **Service Systems**: Coffee shops, restaurants, retail
- **Healthcare**: Hospital triage, clinics, emergency departments
- **Manufacturing**: Production lines, quality control, maintenance
- **Call Centers**: Queue management, agent routing, abandonment

---

## [1.0.0] - 2024-09-16 - **Initial Release**

### ✨ **Added**

#### **🏗️ Foundation**
- **MCP Server**: Basic Model Context Protocol server implementation
- **SimPy Integration**: Discrete-event simulation using SimPy library
- **PySD Integration**: System dynamics simulation capability
- **FastMCP Framework**: Modern MCP server architecture

#### **🎯 Core Features**
- **`simulate_des` Tool**: Basic discrete-event simulation
- **`simulate_sd` Tool**: System dynamics simulation
- **Distribution Support**: Uniform, normal, exponential distributions
- **Basic Metrics**: Entity counting and processing statistics

#### **📊 Simulation Capabilities**
- **Single Resource**: Basic queue-server systems
- **Entity Flow**: Simple arrival and service patterns
- **Time-based Simulation**: Configurable simulation duration
- **Result Reporting**: Basic metrics and statistics

#### **🔧 Technical Components**
- **`SimulationModel`**: Core DES simulation engine
- **`Entity` Class**: Basic entity representation
- **`MetricsCollector`**: Simple metrics gathering
- **Distribution Parsing**: String-to-function conversion

### 🏗️ **Infrastructure**
- **Project Structure**: Organized DES/ and SD/ directories
- **Dependencies**: SimPy, PySD, FastMCP integration
- **Documentation**: Basic README and setup instructions

---

## 📝 **Development Notes**

### **🎯 Design Principles**
1. **User-Centric**: Non-coders can create sophisticated simulations
2. **SimPy-Native**: Leverage SimPy's strengths without custom extensions
3. **Configuration-Driven**: Business logic in JSON, not code
4. **Validation-First**: Comprehensive error checking and helpful messages
5. **Progressive Complexity**: Simple start, sophisticated capabilities

### **🔮 Future Roadmap**
- **Advanced Routing**: Complex decision trees and probabilistic routing
- **Resource Scheduling**: Shift patterns, breaks, planned maintenance
- **Batch Processing**: Batch arrivals and processing
- **Network Topologies**: Multi-location simulations with transfers
- **Optimization Integration**: Parameter optimization and sensitivity analysis
- **Visualization**: Real-time simulation visualization and dashboards

### **🤝 Contributing**
- **Schema Evolution**: Propose new features through schema extensions
- **Example Scenarios**: Contribute domain-specific examples
- **Performance**: Optimize for larger simulations
- **Documentation**: Improve user guides and tutorials

---

## 📊 **Migration Guide**

### **From v1.0.0 to v2.0.0**

#### **⚠️ Breaking Changes**
- **Configuration Format**: JSON schema-based instead of simple parameters
- **Tool Interface**: Enhanced `simulate_des` with validation
- **Result Structure**: Enriched metrics with custom names

#### **🔄 Migration Steps**
1. **Update Configurations**: Convert simple parameters to schema format
2. **Review Examples**: Use provided templates for common scenarios
3. **Test Validation**: Ensure configurations pass schema validation
4. **Update Integrations**: Handle new result format structure

#### **📋 Example Migration**

**v1.0.0 (Old)**:
```json
{
  "run_time": 480,
  "num_entities": 100,
  "service_time": "uniform(3, 7)"
}
```

**v2.0.0 (New)**:
```json
{
  "run_time": 480,
  "num_entities": 100,
  "entity_types": {
    "customer": {"probability": 1.0, "value": {"min": 10, "max": 20}}
  },
  "resources": {
    "server": {"capacity": 1, "resource_type": "fifo"}
  },
  "processing_rules": {
    "steps": ["server"],
    "server": {"distribution": "uniform(3, 7)"}
  }
}
```

---

*For detailed technical documentation, see `schemas/DES/README.md` and `schemas/DES/json-to-simulation-flow.md`.*

---

**Legend:**
- ✨ Added: New features
- 🔄 Changed: Modifications to existing features  
- 🗑️ Removed: Deleted features
- 🐛 Fixed: Bug fixes
- 🚀 Performance: Performance improvements
- 🧪 Testing: Testing and validation
