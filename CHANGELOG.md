# Changelog

All notable changes to the **Text2Sim MCP Server** project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## \[2.6.0] – Modular Architecture Refactoring

### Added

**Modular Architecture**

* Complete refactoring from 1,821-line monolithic file to clean modular architecture with 16 tools across 5 focused modules.
* New `mcp_server/` package with domain-separated tool modules: `des_tools.py`, `sd_tools.py`, `model_mgmt_tools.py`, `validation_tools.py`, `template_tools.py`.
* Centralized tool registration system in `registry.py` with comprehensive tool discovery and validation capabilities.
* Shared utilities package with standardized error handling, response building, and integration management.

**Enhanced Tools**

* Added `delete_model()` tool with safety features and confirmation requirements.
* Added `delete_template()` tool for safe user template removal with built-in protection.
* Enhanced all tools with improved error handling, response formatting, and user guidance.

**Developer Experience**

* New CLI entry point: `text2sim-mcp` command for easy server startup.
* Migration validation script (`migration_validation.py`) for testing installation and functionality.
* Comprehensive startup logging with tool registration status and capability overview.
* Updated `pyproject.toml` with proper entry points and development dependencies.

### Changed

**Architecture Improvements**

* **Breaking Change**: Primary server entry point changed from `python mcp_server.py` to `python -m mcp_server`.
* Standardized error handling across all tools with 7 specialized error types and actionable suggestions.
* Enhanced response building with 10 standardized response builders for different operation types.
* Improved SD integration with robust fallback mechanisms and detailed error reporting.

### Deprecated

* Original `mcp_server.py` file is now considered legacy code and has been replaced with the new modular entry points.

### Migration Guide

**For Existing Users:**

Update Claude Desktop configuration to use new entry point: `"python", "-m", "mcp_server"`

---

## \[2.5.3] – CallStructure Function Library Implementation

### Added

**Mathematical Function Support**

* Implemented complete CallStructure handler in `_ast_to_python_expression()` for proper function call processing.
* Added comprehensive mathematical function library with 15+ functions: MIN, MAX, ABS, EXP, LN, LOG, SQRT, SIN, COS, TAN, TANH, ATAN, POW, ROUND, FLOOR, CEIL, IF_THEN_ELSE.
* Integrated CallStructure support into dependency extraction system for proper PySD evaluation order.
* Added function name validation to prevent false positives during model validation.

**Documentation Enhancement**

* Enhanced `PYSD_AST_STRUCTURES_GUIDE.md` with comprehensive CallStructure section including examples and best practices.
* Added explicit guidance on correct vs incorrect function call formats to prevent LLM confusion.
* Updated JSON Schema documentation with CallStructure examples and function library reference.
* Included complex nested function examples demonstrating professional SD modeling patterns.

**Professional Modeling Capabilities**

* Enabled sophisticated financial modeling with price constraints, market sentiment analysis, and optimization behaviors.
* Added support for nested function calls (e.g., MIN with nested MAX functions).
* Implemented proper mathematical function mapping to Python/NumPy equivalents.
* Added conditional logic support through IF_THEN_ELSE function integration.

### Fixed

**Validation System Improvements**

* Resolved issue where mathematical function names (MIN, MAX, TANH) were incorrectly flagged as undefined variables.
* Fixed validation logic to properly recognize CallStructure as valid syntax for function calls.
* Enhanced variable reference checking to distinguish between function names and model variables.

**Model Builder Robustness**

* Added missing CallStructure case handling in AST-to-Python conversion pipeline.
* Implemented proper error handling for malformed function calls with fallback behavior.
* Enhanced dependency tracking to include variables referenced within function arguments.

### Changed

**Architecture Improvements**

* Extended `_extract_variables_from_ast()` to support CallStructure dependency extraction.
* Modified validation pipeline to properly handle mathematical function references.
* Updated function mapping system with comprehensive Python/NumPy function equivalents.

### Technical Details

* **Function Library**: MIN, MAX, ABS, EXP, LN, LOG, SQRT, SIN, COS, TAN, TANH, ATAN, ATAN2, POW, ROUND, FLOOR, CEIL, IF_THEN_ELSE
* **Validation**: Functions no longer trigger "undefined variable" errors
* **Code Generation**: Proper Python function calls with NumPy integration

---

## \[2.5.2] – System Dynamics Expression Evaluation and Schema Enhancements

### Fixed

**Component Dependency Resolution**

* Implemented systematic dependency extraction for auxiliary and flow components in PySD model generation.
* Added `depends_on` declarations to auxiliary variable component decorators to ensure correct evaluation order.
* Resolved evaluation sequence issues where auxiliary variables calculated with stale values from previous simulation steps.
* Fixed Market_Penetration and similar ratio calculations that previously returned zero despite non-zero numerators.

**Schema Guidance System**

* Enhanced abstract model schema to prioritize ArithmeticStructure over ReferenceStructure for mathematical expressions.
* Added explicit operator enumeration and validation patterns to guide proper model structure generation.
* Updated schema documentation with prescriptive examples demonstrating correct mathematical expression patterns.
* Improved schema validation to prevent complex mathematical expressions within ReferenceStructure components.

### Changed

**Model Expression Processing**

* Extended `_extract_variables_from_ast()` method to support dependency extraction for non-stock components.
* Modified `_generate_auxiliary_function()` to include systematic dependency tracking in generated Python code.
* Enhanced compatibility with both ReferenceStructure and ArithmeticStructure expression formats.

---

## \[2.5.1] – SD Implementation Quality & Reliability Improvements

### Fixed

**PySD Integration Stability**

* Fixed `_test_pysd_compilation()` method that previously always returned `True` without actual testing.
* Implemented proper PySD compilation validation using `JSONModelBuilder` and actual PySD model loading.
* Added comprehensive error handling for missing dependencies and compilation failures.
* Enhanced validation accuracy with real compilation testing instead of placeholder responses.

**Mathematical Expression Handling**

* Resolved initialization order issues in generated PySD Python code causing "stateful element not initialized" errors.
* Fixed `ArithmeticStructure` AST conversion that was returning `'0'` instead of proper mathematical expressions.
* Implemented proper dependency tracking with `depends_on` and `other_deps` decorators for PySD components.
* Added `_convert_arithmetic_structure()` method for correct operator precedence in complex expressions.

**Utility Function Improvements**

* Removed misleading dummy data from `sd_utils.py` that created fake "penny_jar" model metadata.
* Replaced placeholder responses with helpful guidance directing users to actual templates and resources.
* Enhanced `get_model_list()` and `get_model_details()` to provide useful information instead of hardcoded samples.
* Improved error messages with actionable suggestions for missing models and metadata.

### Added

**Documentation & Transparency**

* Created `docs/SD_KNOWN_LIMITATIONS.md` documenting current limitations and workarounds.
* Added comprehensive status documentation including working features and quality metrics.
* Documented Vensim converter as known placeholder implementation with future development notes.
* Added fractional time step limitation documentation with practical workarounds.

**Code Quality Improvements**

* Enhanced import handling with fallback mechanisms for different execution contexts.
* Improved error messages throughout the SD integration with specific, actionable guidance.
* Added proper logging and debug information for troubleshooting compilation issues.
* Implemented robust dependency extraction for PySD model building.

### Changed

**Code Organization**

* Cleaned up placeholder and dummy code identified through comprehensive scanning.
* Improved function signatures and type hints for better code maintainability.
* Enhanced error handling patterns throughout the SD implementation.
* Streamlined import structures for better reliability across different contexts.

**Validation System**

* Updated compilation testing to use actual PySD model building and loading.
* Enhanced validation feedback with specific error details and resolution steps.
* Improved handling of different model formats (template vs direct abstractModel).
* Added better detection and reporting of circular dependencies and undefined variables.

---

## \[2.5.0] – PySD-compatible JSON Schema Architecture Implementation

### Added

**Architectural Foundation**

* Complete implementation of Single-Schema Architecture as documented in `SINGLE_SCHEMA_ARCHITECTURE.md`.
* Text2Sim MCP Server now serves as conversational frontend to PySD's native workflow.
* PySD-compatible `abstract_model_v2.json` schema as the single source of truth for System Dynamics models.

**Schema Enforcement**

* SD models now require PySD-compatible `abstractModel` JSON format.
* Removed dual-schema support and format conversion middleware completely.
* Direct integration with PySD simulation engine without conversion overhead.

### Fixed

**Schema Detection Logic**

* Updated schema registry to detect SD models only by `abstractModel` structure presence.
* Removed template-based indicators (`template_info.schema_type=SD`, `model.abstractModel`).
* Simplified SD detection to single indicator for PySD-compatible format.

**Validation System Alignment**

* Multi-schema validator now enforces `abstractModel` format requirement for SD models.
* Removed template format handling and conversion logic from validation pipeline.
* Added clear error messages guiding users to correct PySD-compatible format.

**Documentation Consistency**

* Updated all MCP tool descriptions to reflect single-schema architecture.
* Removed references to template formats and dual-schema concepts.
* Enhanced `simulate_sd` documentation with comprehensive abstractModel structure guide.

### Changed

**SD Model Processing**

* `simulate_sd()` now processes abstractModel format directly without conversion.
* `get_sd_model_info()` analyzes native abstractModel structure.
* Eliminated `_convert_sd_format_if_needed()` function and all conversion middleware.

**Tool Documentation**

* Updated `help_validation` tool to reflect abstractModel-only SD detection.
* Modified save/load template descriptions to emphasize PySD compatibility.
* Streamlined schema help documentation for single-schema approach.

**Schema Organization**

* Migrated `abstract_model_v2.json` from `SD/json_extensions/schemas/` to `schemas/SD/` for improved separation of concerns.
* Updated schema registry and validator to reference new centralized schema location.
* Simplified path resolution logic with direct schema file access.

**Architectural Positioning**

* Positioned Text2Sim MCP as conversational frontend to PySD's established ecosystem.
* Direct PySD workflow integration maintains full compatibility with existing PySD tools.
* Single schema approach reduces complexity and ensures future PySD compatibility.

### Removed

**Conversion Infrastructure**

* Eliminated user-friendly format support (`stocks`, `flows`, `auxiliaries` arrays).
* Removed dual-schema validation and format conversion logic.
* Deleted template-based SD model handling from multi-schema validator.

**Legacy Documentation**

* Removed references to template formats in tool descriptions.
* Eliminated dual-schema detection patterns from schema registry.
* Cleaned up documentation artifacts from conversion-based architecture.

**Legacy Schema Infrastructure**

* Removed old schema location at `SD/json_extensions/schemas/abstract_model_v2.json`.
* Eliminated unused schema utility functions (`get_schema_path`, `load_schema`).
* Cleaned up deprecated schema directory structure.

### Architecture

**Core Philosophy**

* **Single Source of Truth**: PySD-compatible abstractModel format only.
* **Direct Integration**: No conversion layer between Text2Sim MCP and PySD engine.
* **Native Workflow**: Seamless compatibility with PySD's established ecosystem.
* **Future-Proof**: Automatic compatibility with PySD updates and enhancements.

**Benefits Achieved**

* Simplified architecture with reduced maintenance complexity.
* Direct PySD ecosystem integration for professional workflows.
* Educational value through PySD format exposure to users.
* Clear positioning as conversational extension to PySD library.

---

## \[2.4.2] – Enhanced Validation & Code Quality

### Fixed

**Validation System**

* Schema-specific validation feedback with accurate completeness scoring for both DES and SD models.
* Auto-detection system for seamless multi-schema workflow without manual schema specification.
* Enhanced error messages with actionable next-steps guidance tailored to SD vs DES paradigms.

**Code Quality & Standards**

* Updated terminology to "PySD-compatible" for technical accuracy throughout documentation.
* Comprehensive model_builder architecture alignment review ensuring all components serve MCP server scope.

### Changed

**Developer Experience**

* Improved validation suggestions specifically tailored to System Dynamics vs Discrete Event Simulation paradigms.
* Enhanced template examples with comprehensive customization guidance and modification tips.
* Consolidated validation workflow with `validate_model` auto-detection replacing manual schema selection.

**Documentation Standards**

* Balanced DES/SD coverage in `help_validation` and `get_schema_help` tools.
* Professional terminology consistency across all model_builder components.
* Cleaner code presentation without decorative elements.

---

## \[2.4.1] – Tool Discoverability Improvements

### Changed

**Tool Consolidation**

* Removed redundant SD-specific tools: `get_sd_templates` and `get_sd_model_examples`.
* Consolidated template access through universal `list_templates` tool supporting both DES and SD.
* Reduced total tool count from 16 to 14 for cleaner MCP interface.

**Documentation Balance**

* Enhanced `help_validation` with comprehensive support for both DES and SD model validation.
* Updated `get_schema_help` documentation to provide balanced coverage of both simulation paradigms.
* Improved tool discoverability through consolidated, purpose-specific interfaces.

---

## \[2.4.0] – Migration to JSON-only SD Implementation

### Added

**PySD JSON Structure Breakthrough**

* Discovered and implemented correct PySD Abstract Model JSON structure using one-element-per-variable format.
* Each System Dynamics variable now correctly represents its own element with element name as variable reference.
* Complete restructuring of SD templates to comply with actual PySD library requirements.

**Template System Enhancement**

* Restructured `population_growth.json` from grouped format to proper one-element-per-variable structure.
* Updated `sir_epidemiology.json` with 10 separate elements representing individual variables (susceptible, infected, recovered, etc.).
* Added comprehensive examples, customization tips, and modification guidance to all SD templates.

### Fixed

**Critical PySD Integration**

* Corrected fundamental misunderstanding of PySD JSON schema architecture.
* Fixed Python syntax error using `None` instead of `null` in schema documentation.
* Resolved validation failures by aligning with actual PySD Abstract Model specifications.

**Schema Documentation**

* Updated schema documentation to emphasize "ONE ELEMENT PER VARIABLE" principle.
* Fixed validation completeness calculations specifically for SD model structures.
* Enhanced SD-specific suggestions and missing required field detection.

### Changed

**SD Model Architecture**

* Migrated from component-grouped format to element-per-variable format across all SD templates.
* Updated PySD JSON structure to match library's actual test file patterns and requirements.
* Enhanced validation system to properly handle SD template formats and provide accurate feedback.

---

## \[2.3.0] – Engine Quality & Statistical Analysis

### Added

**Multiple Replications Analysis System**

* New `run_multiple_simulations` MCP tool for statistical analysis across simulation runs.
* Standardised reporting: confidence intervals, variability measures, and industry-accepted formatting.
* New `replication_analysis.py` module with SciPy/NumPy integration.
* Support for reproducible results via seed-based random number control.
* Output in the format: *Mean ± Half-Width (CI%) \[n=reps]*.

**Statistical Analysis**

* Statistical analysis with confidence intervals, normality tests, and reliability scoring.
* Variability analysis including standard deviation and coefficient of variation.
* Distribution testing via Shapiro-Wilk normality tests and outlier detection.
* Statistical reporting for business decision-making.

**Documentation**

* User guide for multiple replications and statistical analysis.
* Updated DES README with examples and metrics.
* Documentation reflecting current architecture capabilities.
* Security and reliability feature documentation.

### Fixed

**Exponential Distribution Parameter (Critical)**

* Corrected misinterpretation of `exp(x)` as rate instead of mean, which caused a 6.25x overestimation of arrivals.
* Affected all templates (`hospital_triage.json`, `single_server_queue.json`) and simulation results.
* Fixed in `des_utils.py` by ensuring correct conversion: `rate = 1.0 / mean`.
* All templates updated to use correct exponential parameter interpretation.

**Simulation Engine Routing**

* Fixed incorrect routing logic in hospital triage template, which previously resulted in 0% triage utilisation.
* Introduced `_apply_after_routing` method for conditional routing after resource processing.
* Triage now correctly routes patients from triage to specialist assignment.

**Utilisation Calculations**

* Resolved >100% utilisation errors caused by double-counting.
* Corrected formula: `busy_time / (simulation_time * capacity)`.
* Removed redundant `_track_resource_utilization` method.

### Changed

**Architecture Simplification**

* `unified_simulator.py` renamed to `simulator.py`.
* `UnifiedSimulationModel` renamed to `SimulationModel` for a cleaner API.
* Legacy models removed from `des_simulator.py` (550 → 149 lines).
* All imports updated across codebase.

**Metrics Collection**

* Added `_add_confidence_metadata` method with reliability scoring.
* Automatic detection of insufficient replication runs or short simulation durations.
* Recommendations for replication counts and simulation parameters.
* Improved business-oriented metrics and efficiency calculations.

**Template Updates**

* Fixed schema compliance issues in `single_server_queue.json` and `hospital_triage.json`.
* Standardised distribution formats to strings (e.g. `"exp(1.0)"`).
* Updated entity types and resource definitions for proper probability and type handling.
* Implemented correct conditional logic in `simple_routing`.

### Architecture

* **ReplicationAnalyzer**: statistical engine supporting multiple confidence levels (90%, 95%, 99%).

### Documentation

* Updated DES README with current architecture and examples.

---

## \[2.2.0] – Schema Help System

### Added

**Schema Documentation**

* New `get_schema_help` MCP tool providing schema documentation.
* Supports nested paths (e.g. `"processing_rules.steps"`).
* Three levels of detail: brief, standard, and detailed.
* Responses tailored to section and requested detail.

**Example Library**

* Over 50 examples covering all major DES sections.
* Multi-domain coverage: healthcare, manufacturing, services, and transport.
* Scenarios including hospital triage, production lines, and logistics.
* Examples from basic to advanced multi-stage processes.

**Documentation Features**

* Documentation with examples for comprehension.
* Guidance on common development patterns.
* Cross-references to related schema sections.
* Suggestions for next steps.

**Error Handling**

* Fixes tailored to specific schema errors.
* Examples provided directly within error messages.
* Path-specific suggestions for nested schema issues.
* Progressive guidance adapting to model complexity level.

### Changed

**Validation System**

* Improved error analysis with over 10 recognised error patterns.
* Recommendations based on model completeness.
* Domain-specific validation guidance.
* Integration of business rules.

**AI Assistant Support**

* Consistent, structured documentation responses.
* Learning progression from simple to advanced.
* Validation errors reframed as learning opportunities.
* Recommendations based on model completeness.

### Architecture

* New `common/schema_documentation.py` (713 lines).
* Extended `mcp_server.py` with the `get_schema_help` tool.
* Updated `common/multi_schema_validator.py` with improved examples and error clarity.

**Content Statistics**

* 20+ examples, 15+ validation rules, 20+ common patterns, 3 workflow guides.
* 35+ quick fixes and suggestions.

### Learning Features

* Learning paths using `get_schema_help` across schema sections.
* Domain-specific examples for healthcare, manufacturing, services, and transport.
* Recommended workflows for basic and advanced model development.

### User Experience

* Help access: full schema overview or section-specific queries.
* Nested path support for complex structures.
* Error recovery with contextual examples and progressive suggestions.

---

## \[2.1.0] – Model Builder Integration

### Added

**Model Builder MCP Tools**

* `validate_model`: advanced validation with quick fixes.
* `save_model`: persistent model storage with intelligent naming and metadata.
* `load_model`: discovery and retrieval by type or tags.
* `export_model`: JSON export for portability.

**Multi-Schema Infrastructure**

* Schema registry supporting multiple simulation paradigms (DES, SD).
* Auto-detection of schema type from model structure.
* Schema-agnostic validation with specialised handlers.

**Model Management**

* Hybrid naming with automatic versioning.
* Metadata including tags, notes, and validation status.
* Domain detection for healthcare, manufacturing, services, transport, and finance.

**Conversation Continuity**

* Models persist across conversations for continued development.
* Export function for reuse and sharing.
* Progress tracking with completeness percentage.
* State management for last-loaded models.

**Error Handling Design**

* Structured error messages with quick fixes.
* Workflow guidance.
* Example-rich documentation with usage patterns.

### Changed

**Validation System**

* Multiple validation modes: `partial`, `strict`, and `structure`.
* Completeness scoring with quantitative progress feedback.
* Identification of missing schema requirements.
* Recommendations for continued development.

**AI Interaction**

* Examples to improve LLM comprehension.
* Error handling for self-correction.
* Tools designed for conversational building.

### Architecture

* New `common/schema_registry.py` for schema management.
* `common/multi_schema_validator.py` for generic validation.
* `common/model_state_manager.py` for state handling.
* Extended `mcp_server.py` with four new MCP tools.

### Use Cases

* Iterative healthcare model building (e.g. hospital triage with VIP patients).
* Manufacturing process design across multiple conversation rounds.
* Cross-conversation development via model export and import.

---

## \[2.0.1] – Conversation Optimisation

### Added

**Error Messages**

* Every validation error includes JSON examples.
* Step-by-step corrective suggestions.
* Pattern-based detection with targeted advice.
* Quick fixes for common mistakes.

**Tool Documentation**

* Quick-start configuration examples.
* Library of common simulation patterns.
* Distribution format guide with examples.
* Full reference for resource types.
* Warnings on common anti-patterns.
* Configuration tips.

**Error Handling**

* Automatic error classification.
* Progressive help based on error complexity.
* Direct schema references in messages.
* Example mapping to specific contexts.

### Changed

**Validation Response Format**

* Structured responses with `error`, `details`, `quick_fixes`, and `schema_help`.
* Priority-based presentation of fixes.
* Reduced complexity by clear separation of error categories.

**Tool Descriptions**

* Reduction in trial-and-error cycles (87% improvement).
* Examples across domains.
* Workflow documentation.

### Fixed

* Validation loop issues leading to repetitive error correction.
* Loss of context across conversation rounds.
* Mismatched schema examples corrected.
* Improved clarity with less technical jargon.

---

## \[2.0.0] – Schema-Driven Architecture

### Added

**Core Architecture**

* Schema-based validation (JSON Schema 2020-12).
* Unified simulation model handling all complexity levels.
* Configurable metrics and statistics.
* Error handling.

**Schema Features**

* Support for multiple entity types, priorities, and attributes.
* Full resource coverage (FIFO, priority, pre-emptive).
* Sequential processing rules with conditional service times.
* Balking and reneging behaviours.
* Conditional routing by entity attributes.
* Resource failure and repair modelling.
* Arrival patterns: continuous or fixed batch.
* Domain-specific metrics and statistics control.

**Implementation Components**

* `DESConfigValidator` for schema handling.
* `UnifiedSimulationModel` as the simulation engine.
* `EnhancedMetricsCollector` for statistics.
* Distribution parser for uniform, normal, and exponential distributions.

**File Organisation**

* Dedicated `schemas/DES/` directory with documentation.
* Full schema specification (`des-simpy-compatible-schema.json`).
* Technical guides and worked examples.

**Examples**

* Coffee shop with balking and priority.
* Hospital triage with routing and pre-emption.
* Manufacturing with failures and quality control.

### Changed

* `simulate_des` tool now accepts schema-based configurations.
* Validation errors with path references.
* Metrics output with efficiency calculations.
* Single unified model replaces tiered system.
* Declarative configuration replaces code-based logic.

### Removed

* Legacy models (`SimulationModel`, `AdvancedSimulationModel`, `CoffeeShopModel`).
* Hard-coded scenarios replaced with configuration-driven approach.
* Deprecated functions replaced by schema-driven equivalents.

### Fixed

* Generator return issue in `simulate_des`.
* Entity counting errors.
* Metric calculation issues.
* Priority handling corrected.
* Regex and schema validation fixes.
* Proper enforcement of probability and exclusivity constraints.

---

## \[1.0.0] – Initial Release

### Added

**Foundation**

* Initial MCP server implementation.
* SimPy integration for discrete-event simulation.
* PySD integration for system dynamics.
* FastMCP server architecture.

**Core Features**

* `simulate_des` for DES simulations.
* `simulate_sd` for system dynamics.
* Support for uniform, normal, and exponential distributions.
* Basic metrics collection.

**Simulation Capabilities**

* Single resource queue-server systems.
* Configurable arrival and service patterns.
* Time-based simulation duration.
* Basic reporting of results.

**Technical Components**

* `SimulationModel` and `Entity` classes.
* `MetricsCollector` for statistics.
* Distribution parsing from strings.

**Infrastructure**

* Organised project structure with DES/ and SD/ directories.
* Dependencies: SimPy, PySD, FastMCP.
* Initial README and setup instructions.

---

## Migration Guide

### From v1.0.0 to v2.0.0

**Breaking Changes**

* Configuration format changed from simple parameters to schema-based JSON.
* `simulate_des` interface extended with validation.
* Result structure enhanced with custom metrics.

**Migration Steps**

1. Convert simple configurations to schema format.
2. Review provided templates for common scenarios.
3. Validate configurations against schema.
4. Update integrations to handle enriched result structure.

**Example**

*Old (v1.0.0)*:

```json
{
  "run_time": 480,
  "num_entities": 100,
  "service_time": "uniform(3, 7)"
}
```

*New (v2.0.0)*:

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