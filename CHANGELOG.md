# Changelog

All notable changes to the **Text2Sim MCP Server** project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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