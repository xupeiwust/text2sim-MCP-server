"""
Template Manager for Text2Sim Model Builder

Provides template discovery, loading, and management functionality for simulation models.
Supports both built-in templates and user-created templates with comprehensive metadata.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import re

@dataclass
class TemplateInfo:
    """Template metadata and information"""
    template_id: str
    name: str
    description: str
    domain: str
    complexity: str  # "basic", "intermediate", "advanced"
    author: str
    version: str
    tags: List[str]
    schema_type: str  # "DES", "SD"
    category: str  # "basic", "healthcare", "manufacturing", etc.
    created: datetime
    last_modified: datetime
    use_count: int = 0
    is_user_template: bool = False
    file_path: Optional[str] = None

@dataclass
class Template:
    """Complete template with metadata and model content"""
    info: TemplateInfo
    model: Dict[str, Any]
    examples: List[Dict[str, Any]] = field(default_factory=list)
    usage_notes: str = ""
    customization_tips: List[str] = field(default_factory=list)

class TemplateManager:
    """
    Manages template discovery, loading, and user template operations.
    
    Features:
    - Built-in template discovery from templates/ directory
    - User template management with metadata
    - Template filtering and search
    - Usage tracking and recommendations
    - Template validation and error handling
    """
    
    def __init__(self, file_only_mode: bool = False):
        self.project_root = Path(__file__).parent.parent
        self.templates_dir = self.project_root / "templates"
        self.file_only_mode = file_only_mode
        self.user_templates: Dict[str, Template] = {}
        self._built_in_templates: Dict[str, Template] = {}
        self._template_cache: Dict[str, Template] = {}
        self._domain_keywords = self._initialize_domain_keywords()
        
        # Load built-in templates
        self._load_built_in_templates()
    
    def _initialize_domain_keywords(self) -> Dict[str, List[str]]:
        """Initialize domain detection keywords"""
        return {
            "healthcare": ["patient", "doctor", "nurse", "hospital", "clinic", "triage", "emergency", "treatment", "medical"],
            "manufacturing": ["production", "assembly", "factory", "machine", "quality", "defect", "batch", "inventory"],
            "service": ["customer", "service", "queue", "wait", "staff", "counter", "appointment", "booking"],
            "transportation": ["vehicle", "route", "logistics", "shipping", "delivery", "cargo", "freight", "dispatch"],
            "finance": ["transaction", "account", "payment", "loan", "credit", "bank", "investment", "portfolio"],
            "retail": ["store", "checkout", "cashier", "inventory", "product", "sale", "customer", "shopping"]
        }
    
    def _load_built_in_templates(self):
        """Load built-in templates from templates directory"""
        if not self.templates_dir.exists():
            if self.file_only_mode:
                # In file-only mode, don't create in-memory templates
                print(f"Warning: Templates directory not found at {self.templates_dir} and file_only_mode=True")
                return
            # Create built-in templates in memory if directory doesn't exist
            self._create_built_in_templates()
            return
            
        # Scan templates directory for JSON files
        for schema_dir in self.templates_dir.iterdir():
            if schema_dir.is_dir():
                schema_type = schema_dir.name
                
                # Load templates directly from schema directory (e.g., templates/DES/*.json)
                for template_file in schema_dir.glob("*.json"):
                    try:
                        template = self._load_template_file(template_file, schema_type, "general")
                        if template:
                            self._built_in_templates[template.info.template_id] = template
                    except Exception as e:
                        print(f"Warning: Failed to load template {template_file}: {e}")
                
                # Also scan category subdirectories (e.g., templates/DES/basic/*.json)
                for category_dir in schema_dir.iterdir():
                    if category_dir.is_dir() and category_dir.name != "user":
                        category = category_dir.name
                        for template_file in category_dir.glob("*.json"):
                            try:
                                template = self._load_template_file(template_file, schema_type, category)
                                if template:
                                    self._built_in_templates[template.info.template_id] = template
                            except Exception as e:
                                print(f"Warning: Failed to load template {template_file}: {e}")
    
    def _create_built_in_templates(self):
        """Create built-in templates in memory when file system is not available"""
        templates = [
            # DES Basic Templates
            {
                "template_info": {
                    "name": "Single Server Queue",
                    "description": "Basic single-server queueing system with FIFO processing",
                    "domain": "basic",
                    "complexity": "basic",
                    "author": "Text2Sim",
                    "version": "1.0",
                    "tags": ["basic", "single-server", "fifo", "queue"],
                    "schema_type": "DES",
                    "category": "basic"
                },
                "model": {
                    "entity_types": [
                        {
                            "name": "customer",
                            "arrival_distribution": {"type": "exponential", "rate": 1.0},
                            "attributes": {"priority": 1}
                        }
                    ],
                    "resources": [
                        {
                            "name": "server",
                            "capacity": 1,
                            "schedule": "24/7"
                        }
                    ],
                    "processing_rules": [
                        {
                            "entity_type": "customer",
                            "steps": [
                                {
                                    "resource": "server",
                                    "duration": {"type": "exponential", "rate": 2.0}
                                }
                            ]
                        }
                    ],
                    "simulation_parameters": {
                        "run_time": 100,
                        "warmup_time": 10,
                        "number_of_runs": 1
                    }
                },
                "usage_notes": "Perfect starting point for understanding basic queueing concepts",
                "customization_tips": [
                    "Adjust arrival_rate to change customer frequency",
                    "Modify service_rate to change processing speed",
                    "Add more servers by increasing capacity"
                ]
            },
            
            # DES Healthcare Template
            {
                "template_info": {
                    "name": "Hospital Triage System",
                    "description": "Emergency department triage with priority-based treatment",
                    "domain": "healthcare",
                    "complexity": "intermediate",
                    "author": "Text2Sim",
                    "version": "1.0",
                    "tags": ["healthcare", "triage", "priority", "emergency", "hospital"],
                    "schema_type": "DES",
                    "category": "healthcare"
                },
                "model": {
                    "entity_types": [
                        {
                            "name": "emergency_patient",
                            "arrival_distribution": {"type": "exponential", "rate": 0.5},
                            "attributes": {"priority": 1, "severity": "high"}
                        },
                        {
                            "name": "routine_patient", 
                            "arrival_distribution": {"type": "exponential", "rate": 2.0},
                            "attributes": {"priority": 3, "severity": "low"}
                        }
                    ],
                    "resources": [
                        {
                            "name": "triage_nurse",
                            "capacity": 1,
                            "schedule": "24/7"
                        },
                        {
                            "name": "emergency_doctor",
                            "capacity": 2,
                            "schedule": "24/7"
                        },
                        {
                            "name": "routine_doctor",
                            "capacity": 1,
                            "schedule": "8-18"
                        }
                    ],
                    "processing_rules": [
                        {
                            "entity_type": "emergency_patient",
                            "steps": [
                                {
                                    "resource": "triage_nurse",
                                    "duration": {"type": "triangular", "low": 2, "mode": 5, "high": 10}
                                },
                                {
                                    "resource": "emergency_doctor",
                                    "duration": {"type": "normal", "mean": 30, "std": 10}
                                }
                            ]
                        },
                        {
                            "entity_type": "routine_patient",
                            "steps": [
                                {
                                    "resource": "triage_nurse",
                                    "duration": {"type": "triangular", "low": 2, "mode": 5, "high": 10}
                                },
                                {
                                    "resource": "routine_doctor",
                                    "duration": {"type": "normal", "mean": 15, "std": 5}
                                }
                            ]
                        }
                    ],
                    "simulation_parameters": {
                        "run_time": 480,  # 8 hours
                        "warmup_time": 60,
                        "number_of_runs": 10
                    }
                },
                "usage_notes": "Models realistic hospital triage with different patient priorities and resource scheduling",
                "customization_tips": [
                    "Adjust patient arrival rates based on hospital size",
                    "Modify doctor schedules for different shifts",
                    "Add specialized resources like X-ray or lab equipment"
                ]
            },
            
            # DES Manufacturing Template
            {
                "template_info": {
                    "name": "Production Line with Quality Control",
                    "description": "Manufacturing line with assembly, inspection, and rework processes",
                    "domain": "manufacturing",
                    "complexity": "intermediate",
                    "author": "Text2Sim",
                    "version": "1.0",
                    "tags": ["manufacturing", "production", "quality", "assembly", "inspection"],
                    "schema_type": "DES",
                    "category": "manufacturing"
                },
                "model": {
                    "entity_types": [
                        {
                            "name": "product",
                            "arrival_distribution": {"type": "constant", "value": 5.0},
                            "attributes": {"batch_id": 1, "quality_grade": "A"}
                        }
                    ],
                    "resources": [
                        {
                            "name": "assembly_station",
                            "capacity": 2,
                            "schedule": "24/7"
                        },
                        {
                            "name": "quality_inspector",
                            "capacity": 1,
                            "schedule": "8-17"
                        },
                        {
                            "name": "rework_station",
                            "capacity": 1,
                            "schedule": "8-17"
                        }
                    ],
                    "processing_rules": [
                        {
                            "entity_type": "product",
                            "steps": [
                                {
                                    "resource": "assembly_station",
                                    "duration": {"type": "normal", "mean": 10, "std": 2}
                                },
                                {
                                    "resource": "quality_inspector",
                                    "duration": {"type": "uniform", "low": 2, "high": 5}
                                }
                            ]
                        }
                    ],
                    "simple_routing": [
                        {
                            "from_step": "quality_inspector",
                            "conditions": [
                                {
                                    "condition": "defect_detected",
                                    "probability": 0.15,
                                    "destination": "rework_station"
                                }
                            ],
                            "default_destination": "exit"
                        }
                    ],
                    "simulation_parameters": {
                        "run_time": 480,  # 8 hour shift
                        "warmup_time": 60,
                        "number_of_runs": 5
                    }
                },
                "usage_notes": "Demonstrates manufacturing workflow with quality control and rework processes",
                "customization_tips": [
                    "Adjust defect probability based on real quality data",
                    "Add multiple assembly stations for higher throughput",
                    "Include equipment failure and maintenance schedules"
                ]
            },
            
            # DES Service Template
            {
                "template_info": {
                    "name": "Customer Service Center",
                    "description": "Multi-channel customer service with different service types and agent skills",
                    "domain": "service",
                    "complexity": "intermediate",
                    "author": "Text2Sim",
                    "version": "1.0",
                    "tags": ["service", "customer", "call-center", "multi-channel", "skills"],
                    "schema_type": "DES",
                    "category": "service"
                },
                "model": {
                    "entity_types": [
                        {
                            "name": "phone_customer",
                            "arrival_distribution": {"type": "exponential", "rate": 3.0},
                            "attributes": {"channel": "phone", "issue_type": "general"}
                        },
                        {
                            "name": "chat_customer",
                            "arrival_distribution": {"type": "exponential", "rate": 2.0},
                            "attributes": {"channel": "chat", "issue_type": "technical"}
                        }
                    ],
                    "resources": [
                        {
                            "name": "phone_agent",
                            "capacity": 3,
                            "schedule": "9-17",
                            "skills": ["phone", "general"]
                        },
                        {
                            "name": "chat_agent",
                            "capacity": 2,
                            "schedule": "9-17",
                            "skills": ["chat", "technical"]
                        },
                        {
                            "name": "supervisor",
                            "capacity": 1,
                            "schedule": "9-17",
                            "skills": ["escalation"]
                        }
                    ],
                    "processing_rules": [
                        {
                            "entity_type": "phone_customer",
                            "steps": [
                                {
                                    "resource": "phone_agent",
                                    "duration": {"type": "lognormal", "mean": 8, "sigma": 0.5}
                                }
                            ]
                        },
                        {
                            "entity_type": "chat_customer",
                            "steps": [
                                {
                                    "resource": "chat_agent",
                                    "duration": {"type": "gamma", "shape": 2, "scale": 6}
                                }
                            ]
                        }
                    ],
                    "balking_rules": [
                        {
                            "entity_type": "phone_customer",
                            "queue_threshold": 10,
                            "balking_probability": 0.3
                        }
                    ],
                    "simulation_parameters": {
                        "run_time": 480,  # 8 hour workday
                        "warmup_time": 60,
                        "number_of_runs": 20
                    }
                },
                "usage_notes": "Models modern customer service with multiple channels and agent specialization",
                "customization_tips": [
                    "Adjust arrival rates based on actual call/chat volumes",
                    "Add escalation routing for complex issues",
                    "Include customer satisfaction tracking"
                ]
            }
        ]
        
        # Convert to Template objects
        for template_data in templates:
            template_info = TemplateInfo(
                template_id=str(uuid.uuid4()),
                name=template_data["template_info"]["name"],
                description=template_data["template_info"]["description"],
                domain=template_data["template_info"]["domain"],
                complexity=template_data["template_info"]["complexity"],
                author=template_data["template_info"]["author"],
                version=template_data["template_info"]["version"],
                tags=template_data["template_info"]["tags"],
                schema_type=template_data["template_info"]["schema_type"],
                category=template_data["template_info"]["category"],
                created=datetime.now(),
                last_modified=datetime.now(),
                is_user_template=False
            )
            
            template = Template(
                info=template_info,
                model=template_data["model"],
                usage_notes=template_data.get("usage_notes", ""),
                customization_tips=template_data.get("customization_tips", [])
            )
            
            self._built_in_templates[template_info.template_id] = template
    
    def _load_template_file(self, file_path: Path, schema_type: str, category: str) -> Optional[Template]:
        """Load a template from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract template info
            template_info_data = data.get("template_info", {})
            # Parse dates with fallback
            def parse_datetime(date_str, default=None):
                if not date_str:
                    return default or datetime.now()
                try:
                    # Handle ISO format with Z suffix
                    if date_str.endswith('Z'):
                        date_str = date_str[:-1] + '+00:00'
                    return datetime.fromisoformat(date_str)
                except ValueError:
                    return default or datetime.now()
            
            template_info = TemplateInfo(
                template_id=template_info_data.get("template_id", str(uuid.uuid4())),
                name=template_info_data.get("name", file_path.stem),
                description=template_info_data.get("description", ""),
                domain=template_info_data.get("domain", category),
                complexity=template_info_data.get("complexity", "intermediate"),
                author=template_info_data.get("author", "Unknown"),
                version=template_info_data.get("version", "1.0"),
                tags=template_info_data.get("tags", []),
                schema_type=schema_type,
                category=category,
                created=parse_datetime(template_info_data.get("created")),
                last_modified=parse_datetime(template_info_data.get("last_modified")),
                use_count=template_info_data.get("use_count", 0),
                is_user_template=category == "user",
                file_path=str(file_path)
            )
            
            template = Template(
                info=template_info,
                model=data.get("model", {}),
                examples=data.get("examples", []),
                usage_notes=data.get("usage_notes", ""),
                customization_tips=data.get("customization_tips", [])
            )
            
            return template
            
        except Exception as e:
            print(f"Error loading template {file_path}: {e}")
            return None
    
    def list_templates(
        self, 
        schema_type: Optional[str] = None,
        domain: Optional[str] = None,
        complexity: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_user: bool = True,
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available templates with filtering options.
        
        Args:
            schema_type: Filter by schema type ("DES", "SD")
            domain: Filter by domain (healthcare, manufacturing, etc.)
            complexity: Filter by complexity (basic, intermediate, advanced)
            tags: Filter by tags (must match all provided tags)
            include_user: Include user-created templates
            search_term: Search in name and description
            
        Returns:
            List of template summaries with metadata
        """
        all_templates = dict(self._built_in_templates)
        if include_user:
            all_templates.update(self.user_templates)
        
        filtered_templates = []
        
        for template in all_templates.values():
            # Apply filters
            if schema_type and template.info.schema_type != schema_type:
                continue
            if domain and template.info.domain != domain:
                continue
            if complexity and template.info.complexity != complexity:
                continue
            if tags and not all(tag in template.info.tags for tag in tags):
                continue
            if search_term:
                search_lower = search_term.lower()
                if (search_lower not in template.info.name.lower() and 
                    search_lower not in template.info.description.lower()):
                    continue
            
            # Create summary
            template_summary = {
                "template_id": template.info.template_id,
                "name": template.info.name,
                "description": template.info.description,
                "domain": template.info.domain,
                "complexity": template.info.complexity,
                "schema_type": template.info.schema_type,
                "category": template.info.category,
                "tags": template.info.tags,
                "author": template.info.author,
                "version": template.info.version,
                "use_count": template.info.use_count,
                "is_user_template": template.info.is_user_template,
                "created": template.info.created.isoformat(),
                "last_modified": template.info.last_modified.isoformat()
            }
            
            filtered_templates.append(template_summary)
        
        # Sort by use count (descending) then by name
        filtered_templates.sort(key=lambda x: (-x["use_count"], x["name"]))
        
        return filtered_templates
    
    def load_template(self, template_id: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a template by ID or name.
        
        Args:
            template_id: Unique template identifier
            name: Template name (uses first match if multiple exist)
            
        Returns:
            Dictionary with template data and metadata
        """
        if not template_id and not name:
            return {
                "error": "Either template_id or name must be provided",
                "available_templates": [t["name"] for t in self.list_templates()]
            }
        
        # Search all templates
        all_templates = dict(self._built_in_templates)
        all_templates.update(self.user_templates)
        
        template = None
        
        if template_id:
            template = all_templates.get(template_id)
        elif name:
            # Find by name
            for t in all_templates.values():
                if t.info.name.lower() == name.lower():
                    template = t
                    break
        
        if not template:
            search_key = template_id or name
            similar_templates = []
            for t in all_templates.values():
                if search_key.lower() in t.info.name.lower():
                    similar_templates.append(t.info.name)
            
            return {
                "error": f"Template not found: {search_key}",
                "suggestions": similar_templates[:5] if similar_templates else [],
                "available_templates": [t["name"] for t in self.list_templates()[:10]]
            }
        
        # Update use count
        template.info.use_count += 1
        
        return {
            "template_id": template.info.template_id,
            "name": template.info.name,
            "description": template.info.description,
            "domain": template.info.domain,
            "complexity": template.info.complexity,
            "schema_type": template.info.schema_type,
            "model": template.model,
            "metadata": {
                "author": template.info.author,
                "version": template.info.version,
                "tags": template.info.tags,
                "category": template.info.category,
                "use_count": template.info.use_count,
                "is_user_template": template.info.is_user_template,
                "created": template.info.created.isoformat(),
                "last_modified": template.info.last_modified.isoformat()
            },
            "usage_notes": template.usage_notes,
            "customization_tips": template.customization_tips,
            "examples": template.examples
        }
    
    def save_template(
        self,
        model: Dict[str, Any],
        name: str,
        description: str = "",
        domain: Optional[str] = None,
        complexity: str = "intermediate",
        tags: Optional[List[str]] = None,
        usage_notes: str = "",
        customization_tips: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Save a user template.
        
        Args:
            model: The simulation model configuration
            name: Template name
            description: Template description
            domain: Domain classification (auto-detected if None)
            complexity: Complexity level (basic, intermediate, advanced)
            tags: Template tags
            usage_notes: Usage instructions
            customization_tips: List of customization suggestions
            overwrite: Whether to overwrite existing template with same name
            
        Returns:
            Dictionary with save result and template info
        """
        if not model:
            return {
                "error": "Model cannot be empty",
                "success": False
            }
        
        # Check for existing template with same name
        existing_template = None
        for template in self.user_templates.values():
            if template.info.name.lower() == name.lower():
                existing_template = template
                break
        
        if existing_template and not overwrite:
            return {
                "error": f"Template '{name}' already exists. Use overwrite=True to replace it.",
                "success": False,
                "existing_template_id": existing_template.info.template_id
            }
        
        # Auto-detect domain if not provided
        if not domain:
            domain = self._detect_domain(model, name, description)
        
        # Auto-detect schema type from model structure
        schema_type = self._detect_schema_type(model)
        
        # Generate or reuse template ID
        template_id = existing_template.info.template_id if existing_template else str(uuid.uuid4())
        
        # Create template info
        template_info = TemplateInfo(
            template_id=template_id,
            name=name,
            description=description,
            domain=domain,
            complexity=complexity,
            author="User",
            version="1.0",
            tags=tags or [],
            schema_type=schema_type,
            category="user",
            created=existing_template.info.created if existing_template else datetime.now(),
            last_modified=datetime.now(),
            is_user_template=True
        )
        
        # Create template
        template = Template(
            info=template_info,
            model=model.copy(),  # Deep copy to avoid mutations
            usage_notes=usage_notes,
            customization_tips=customization_tips or [],
            examples=[]
        )
        
        # Save template
        self.user_templates[template_id] = template
        
        return {
            "success": True,
            "template_id": template_id,
            "name": name,
            "domain": domain,
            "schema_type": schema_type,
            "message": f"Template '{name}' saved successfully" + (" (overwritten)" if existing_template else ""),
            "metadata": {
                "author": template_info.author,
                "version": template_info.version,
                "tags": template_info.tags,
                "complexity": template_info.complexity,
                "created": template_info.created.isoformat(),
                "last_modified": template_info.last_modified.isoformat()
            }
        }
    
    def _detect_domain(self, model: Dict[str, Any], name: str, description: str) -> str:
        """Auto-detect domain based on model content and metadata"""
        text_to_analyze = f"{name} {description} {json.dumps(model)}".lower()
        
        domain_scores = {}
        for domain, keywords in self._domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def _detect_schema_type(self, model: Dict[str, Any]) -> str:
        """Auto-detect schema type from model structure"""
        # Check for DES indicators
        des_indicators = ["entity_types", "resources", "processing_rules"]
        if any(indicator in model for indicator in des_indicators):
            return "DES"
        
        # Check for SD indicators (future)
        sd_indicators = ["stocks", "flows", "variables"]
        if any(indicator in model for indicator in sd_indicators):
            return "SD"
        
        return "DES"  # Default to DES
    
    def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a user template"""
        if template_id not in self.user_templates:
            return {
                "error": f"Template not found or cannot be deleted: {template_id}",
                "success": False
            }
        
        template_name = self.user_templates[template_id].info.name
        del self.user_templates[template_id]
        
        return {
            "success": True,
            "message": f"Template '{template_name}' deleted successfully"
        }
    
    def get_template_recommendations(self, model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get template recommendations based on current model"""
        if not model:
            # Return popular basic templates
            templates = self.list_templates(complexity="basic")
            return templates[:3]
        
        # Detect domain and complexity
        domain = self._detect_domain(model, "", "")
        schema_type = self._detect_schema_type(model)
        
        # Find similar templates
        recommendations = self.list_templates(
            schema_type=schema_type,
            domain=domain if domain != "general" else None
        )
        
        return recommendations[:5]

# Create global instance
template_manager = TemplateManager()
