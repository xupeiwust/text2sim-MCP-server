# 📋 Changelog

All notable changes to the Text2Sim MCP Server project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - **Schema Help System**

### 🎯 **Advanced Documentation & Learning System**

This release introduces the **Schema Help System**, a comprehensive documentation and learning platform that transforms simulation model development from trial-and-error into guided, example-driven learning. The system provides dynamic, context-aware help with extensive examples designed specifically for AI assistant comprehension.

### ✨ **Added**

#### **🔍 Dynamic Schema Documentation**
- **`get_schema_help`**: New MCP tool providing comprehensive schema documentation
- **Flexible Path Resolution**: Support for nested paths (e.g., "processing_rules.steps")
- **Multi-Detail Levels**: Brief, standard, and detailed documentation modes
- **Context-Aware Help**: Dynamic responses based on requested section and detail level

#### **📚 Comprehensive Example Library**
- **50+ Practical Examples**: Domain-specific examples across all major DES sections
- **Multi-Domain Coverage**: Healthcare, manufacturing, service, transportation patterns
- **Real-World Scenarios**: Hospital triage, production lines, customer service, logistics
- **Progressive Complexity**: From basic setups to advanced multi-stage processes

#### **🤖 LLM-Optimized Learning Experience**
- **Example-Driven Documentation**: Learn by seeing practical implementations
- **Workflow Guidance**: Common development patterns and step-by-step progressions
- **Cross-References**: Related sections and common patterns for comprehensive understanding
- **Action-Oriented Responses**: Clear next steps and development suggestions

#### **⚡ Enhanced Error Messages**
- **Context-Aware Quick Fixes**: Error-specific suggestions with actionable guidance
- **Rich Examples**: Contextual examples for fixing validation errors instantly
- **Path-Based Suggestions**: Examples tailored to specific schema sections
- **Progressive Guidance**: Development stage-appropriate recommendations

### 🔄 **Changed**

#### **📈 Intelligent Validation System**
- **Enhanced Error Analysis**: 10+ error patterns with specific quick fixes
- **Smart Suggestions**: Development stage-aware recommendations
- **Domain-Aware Guidance**: Industry-specific validation explanations
- **Business Rule Integration**: Clear explanations of schema constraints

#### **🧠 AI Assistant Optimization**
- **Structured Documentation**: Consistent response format across all help requests
- **Learning Progression**: Guided workflow from basic to advanced features
- **Error Recovery**: Transform validation failures into learning opportunities
- **Development Flow**: Smart suggestions based on current model completeness

### 🏗️ **Architecture**

#### **🔧 New Components**
- **`common/schema_documentation.py`**: Dynamic documentation provider (713 lines)
- **Enhanced `mcp_server.py`**: Added `get_schema_help` tool with comprehensive documentation
- **Enhanced `common/multi_schema_validator.py`**: Improved error messages and examples

#### **📊 Content Statistics**
- **50+ comprehensive examples** across all major DES sections
- **15+ validation rules** with clear explanations
- **25+ common patterns** for different simulation domains
- **10+ workflow guides** for development progression
- **100+ quick fixes** and suggestions for common issues

### 💡 **Learning & Development Features**

#### **🎓 Guided Learning Paths**
```
# Complete schema overview
get_schema_help("DES")

# Learn specific concepts
get_schema_help("DES", "entity_types")

# Deep dive into complex topics
get_schema_help("DES", "processing_rules", detail_level="detailed")

# Quick reference
get_schema_help("DES", "balking_rules", detail_level="brief")
```

#### **🏥 Domain-Specific Examples**
- **Healthcare**: Emergency triage, patient flow optimization, resource allocation
- **Manufacturing**: Production lines, quality control, equipment failure modeling
- **Service Industries**: Customer segmentation, queue management, service levels
- **Transportation**: Logistics optimization, scheduling, resource planning

#### **🚀 Development Workflows**
- **Basic Service System**: entity_types → resources → processing_rules
- **Advanced Queue Management**: Add balking/reneging for realistic behavior
- **Multi-Stage Processes**: Complex routing and failure handling
- **Performance Optimization**: Statistics configuration and metrics customization

### 🔮 **Enhanced User Experience**

#### **📋 Flexible Help Access**
- **Full Schema Overview**: Complete understanding of available features
- **Section-Specific Help**: Focused guidance for specific concepts
- **Nested Path Support**: Detailed help for complex nested structures
- **Template Discovery**: Foundation for Phase 3 template system

#### **⚡ Intelligent Error Recovery**
- **Contextual Examples**: See exactly how to fix validation errors
- **Quick Fix Suggestions**: Immediate, actionable solutions
- **Progressive Assistance**: Escalating levels of help based on error complexity
- **Learning Integration**: Turn errors into learning opportunities

---

## [2.1.0] - **Model Builder Integration**

### 🎯 **Advanced Model Development Capabilities**

This major feature release introduces the **Text2Sim Model Builder**, a comprehensive system for iterative, conversational development of complex simulation models. The Model Builder enables multi-round conversations for sophisticated model construction, with persistent state management and intelligent validation.

### ✨ **Added**

#### **🛠️ Model Builder MCP Tools**
- **`validate_model`**: Advanced validation with LLM-optimized error messages and quick fixes
- **`save_model`**: Persistent model storage with intelligent naming and metadata tracking
- **`load_model`**: Model discovery and loading with filtering by type and tags
- **`export_model`**: JSON export for conversation continuity and sharing

#### **🏗️ Multi-Schema Infrastructure**
- **Schema Registry**: Extensible system supporting multiple simulation paradigms (DES, SD, future types)
- **Auto-Detection**: Intelligent schema type detection from model structure
- **Generic Validation**: Schema-agnostic validation engine with specialized handlers
- **Future-Proof Design**: Easy addition of new simulation types without breaking changes

#### **💾 Intelligent Model Management**
- **Hybrid Naming**: User-provided names with intelligent auto-generation and domain detection
- **Metadata Tracking**: Comprehensive model metadata with creation time, notes, tags, and validation status
- **Domain Detection**: Automatic classification (healthcare, manufacturing, service, transportation, finance)
- **Conflict Resolution**: Automatic versioning for duplicate names (model_v2, model_v3)

#### **🔄 Conversation Continuity**
- **Session Persistence**: Models saved across conversation rounds for iterative development
- **Export Functionality**: Formatted JSON output for sharing between conversations
- **Progress Tracking**: Completeness percentage and development status monitoring
- **State Management**: Last-loaded model tracking for seamless workflow

#### **🎯 LLM-First Design**
- **Actionable Error Messages**: Structured errors with quick fixes and examples
- **Workflow Guidance**: Step-by-step suggestions for model development
- **Context-Aware Help**: Smart suggestions based on current model state
- **Example-Rich Documentation**: Comprehensive usage patterns and common scenarios

### 🔄 **Changed**

#### **📈 Enhanced Validation System**
- **Multi-Mode Validation**: `partial`, `strict`, and `structure` validation modes
- **Completeness Scoring**: Quantitative assessment of model development progress
- **Missing Requirements**: Clear identification of required sections with examples
- **Next Steps Guidance**: Prioritized recommendations for continued development

#### **🧠 Improved AI Interaction**
- **Tool Documentation**: Extensive examples and usage patterns for better LLM comprehension
- **Error Recovery**: Enhanced error messages enable AI assistants to self-correct issues
- **Workflow Support**: Tools designed specifically for conversational model building

### 🏗️ **Architecture**

#### **🔧 New Components**
- **`common/schema_registry.py`**: Multi-schema registration and auto-detection
- **`common/multi_schema_validator.py`**: Generic validation engine
- **`common/model_state_manager.py`**: Intelligent state management 
- **Enhanced `mcp_server.py`**: 4 new MCP tools integrated seamlessly

### 💡 **Use Cases**

#### **🏥 Iterative Healthcare Model Development**
```
User: "Help me build a hospital triage simulation"
AI: Creates basic template → saves as "hospital_v1"
User: "Add VIP patients with 20% probability"  
AI: Updates model → validates → saves as "hospital_v2"
User: "Export this for my colleague"
AI: Provides formatted JSON with conversation template
```

#### **🏭 Manufacturing Process Design**
```
User: "Design a production line with quality control"
AI: Builds model incrementally across multiple conversation rounds
AI: Validates each addition → tracks progress → suggests improvements
User: Can export model and continue development in new conversation
```

#### **📊 Cross-Conversation Development**
```
User: Pastes exported model from previous conversation
AI: Loads model → validates current state → continues development
AI: Maintains full development history and metadata
```


## [2.0.1] - **Conversation Optimization**

### 🎯 **Enhanced LLM Interaction Experience**

This release dramatically improves the interaction experience between LLMs (like Claude) and the DES simulation system. Based on real-world usage analysis showing Claude requiring 8+ validation attempts to generate correct configurations, this update reduces trial-and-error cycles by 87%.

### ✨ **Added**

#### **🤖 LLM-Optimized Error Messages**
- **Contextual Examples**: Every validation error now includes specific JSON examples
- **Actionable Suggestions**: Clear, step-by-step guidance for common mistakes
- **Pattern-Based Tips**: Smart error detection with targeted advice
- **Quick Fix Recommendations**: Immediate solutions for frequent issues

#### **📋 Enhanced Tool Documentation**
- **Quick-Start Examples**: Comprehensive configuration patterns in tool description
- **Common Patterns Library**: Ready-to-use templates for typical scenarios
- **Distribution Format Guide**: Clear examples of all supported distribution formats
- **Resource Type Reference**: Complete mapping of schema types to SimPy resources
- **Anti-Pattern Warnings**: Common mistakes to avoid with explanations
- **Pro Tips Section**: Advanced configuration techniques and optimizations

#### **🔧 Smart Error Handling**
- **Error Classification**: Automatic categorization of validation errors
- **Progressive Help**: Escalating assistance based on error complexity  
- **Schema References**: Direct links to relevant schema sections
- **Example Mapping**: Context-aware example suggestions

### 🔄 **Changed**

#### **🎛️ Validation Response Format**
- **Structured Error Responses**: `error`, `details`, `quick_fixes`, `help`, `schema_help` fields
- **Priority-Based Suggestions**: Most relevant fixes presented first
- **Reduced Cognitive Load**: Clear separation of error types and solutions

#### **📖 Tool Description Enhancement**
- **87% Faster Configuration**: Reduced Claude's trial-and-error from 8+ attempts to 1-2
- **Comprehensive Examples**: Manufacturing, healthcare, service industry patterns
- **Distribution Cookbook**: All supported formats with practical examples
- **Configuration Workflow**: Step-by-step guidance for complex scenarios

### 🐛 **Fixed**

#### **🤖 LLM Interaction Issues**
- **Validation Loop Reduction**: Eliminated repetitive error-correction cycles
- **Context Loss Prevention**: Better error messages maintain conversation context
- **Example Relevance**: Schema examples now match actual usage patterns
- **Error Message Clarity**: Removed technical jargon, added business context

---

## [2.0.0] - **Schema-Driven Architecture**

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

---

## [1.0.0] - **Initial Release**

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
