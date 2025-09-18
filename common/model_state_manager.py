"""
Model State Manager for Text2Sim Model Builder.

This module provides in-memory storage and management of simulation models
with hybrid naming, metadata tracking, and version management.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from .schema_registry import schema_registry


@dataclass
class ModelMetadata:
    """Metadata for a saved model."""
    created: datetime
    last_modified: datetime
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    validation_status: str = "unknown"  # "valid", "partial", "invalid", "unknown"
    completeness: float = 0.0
    schema_type: str = "unknown"
    author: str = "user"
    version: str = "1.0"


@dataclass
class ModelState:
    """Complete state of a saved model."""
    model_id: str
    model: Dict[str, Any]
    metadata: ModelMetadata
    validation_cache: Optional[Dict[str, Any]] = None


class ModelStateManager:
    """
    In-memory storage and management system for simulation models.
    
    Features:
    - Hybrid naming (user-provided or auto-generated)
    - Metadata tracking and search
    - Version management
    - Domain detection for auto-naming
    - Conflict resolution
    """
    
    def __init__(self):
        """Initialize the model state manager."""
        self.models: Dict[str, ModelState] = {}
        self.counter: int = 0
        self.last_loaded: Optional[str] = None
        self._domain_keywords = self._initialize_domain_keywords()
    
    def _initialize_domain_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for domain detection."""
        return {
            "healthcare": [
                "hospital", "patient", "doctor", "nurse", "triage", "emergency",
                "clinic", "medical", "treatment", "diagnosis", "surgery"
            ],
            "manufacturing": [
                "production", "assembly", "factory", "machine", "quality",
                "inspection", "maintenance", "defect", "batch", "process"
            ],
            "service": [
                "customer", "service", "restaurant", "retail", "call_center",
                "queue", "server", "checkout", "reception", "support"
            ],
            "transportation": [
                "airport", "flight", "passenger", "cargo", "logistics",
                "shipping", "delivery", "route", "vehicle", "traffic"
            ],
            "finance": [
                "bank", "transaction", "account", "loan", "credit",
                "payment", "investment", "portfolio", "risk", "audit"
            ]
        }
    
    def save_model(
        self,
        model: Dict[str, Any],
        name: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
        overwrite: bool = False,
        validation_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a model with metadata.
        
        Args:
            model: The model dictionary to save
            name: User-provided name (priority) or None for auto-generation
            notes: Optional description/notes
            tags: Optional tags for categorization
            overwrite: Allow overwriting existing model with same name
            validation_result: Optional validation result to cache
            
        Returns:
            Dictionary with save result information
        """
        # Generate or validate name
        model_id = self._generate_model_id(model, name, overwrite)
        
        # Detect schema type
        schema_type, _ = schema_registry.detect_schema_type(model)
        if schema_type is None:
            schema_type = "unknown"
        
        # Create metadata
        now = datetime.now()
        metadata = ModelMetadata(
            created=now,
            last_modified=now,
            notes=notes or "",
            tags=tags or [],
            schema_type=schema_type,
            validation_status=self._extract_validation_status(validation_result),
            completeness=self._extract_completeness(validation_result)
        )
        
        # Update existing model or create new
        if model_id in self.models:
            existing_state = self.models[model_id]
            metadata.created = existing_state.metadata.created  # Preserve creation time
        
        # Create model state
        model_state = ModelState(
            model_id=model_id,
            model=model.copy(),
            metadata=metadata,
            validation_cache=validation_result
        )
        
        # Save model
        self.models[model_id] = model_state
        self.last_loaded = model_id
        
        return {
            "saved": True,
            "model_id": model_id,
            "auto_generated_name": name is None,
            "schema_type": schema_type,
            "metadata": {
                "created": metadata.created.isoformat(),
                "notes": metadata.notes,
                "tags": metadata.tags,
                "validation_status": metadata.validation_status,
                "completeness": metadata.completeness
            },
            "message": f"Model saved as '{model_id}'"
        }
    
    def load_model(
        self,
        name: Optional[str] = None,
        schema_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Load a model or list available models.
        
        Args:
            name: Model name to load (None for list mode)
            schema_type: Filter by schema type
            tags: Filter by tags
            
        Returns:
            Model data or list of available models
        """
        if name is None:
            # List mode
            return self._list_models(schema_type, tags)
        else:
            # Load specific model
            return self._load_specific_model(name)
    
    def _list_models(
        self,
        schema_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List available models with optional filtering."""
        filtered_models = []
        
        for model_id, model_state in self.models.items():
            # Apply filters
            if schema_type and model_state.metadata.schema_type != schema_type:
                continue
            
            if tags:
                if not any(tag in model_state.metadata.tags for tag in tags):
                    continue
            
            # Add to filtered list
            filtered_models.append({
                "name": model_id,
                "schema_type": model_state.metadata.schema_type,
                "created": model_state.metadata.created.isoformat(),
                "notes": model_state.metadata.notes,
                "tags": model_state.metadata.tags,
                "completeness": model_state.metadata.completeness,
                "last_modified": model_state.metadata.last_modified.isoformat(),
                "validation_status": model_state.metadata.validation_status
            })
        
        # Sort by last modified (newest first)
        filtered_models.sort(key=lambda x: x["last_modified"], reverse=True)
        
        return {
            "available_models": filtered_models,
            "total_count": len(self.models),
            "filtered_count": len(filtered_models)
        }
    
    def _load_specific_model(self, name: str) -> Dict[str, Any]:
        """Load a specific model by name."""
        if name not in self.models:
            return {
                "loaded": False,
                "error": f"Model '{name}' not found",
                "available_models": list(self.models.keys())
            }
        
        model_state = self.models[name]
        self.last_loaded = name
        
        # Include validation status if cached
        validation_status = {}
        if model_state.validation_cache:
            validation_status = {
                "valid": model_state.validation_cache.get("valid", False),
                "completeness": model_state.metadata.completeness,
                "missing_required": model_state.validation_cache.get("missing_required", [])
            }
        
        return {
            "loaded": True,
            "model_name": name,
            "model": model_state.model.copy(),
            "metadata": {
                "created": model_state.metadata.created.isoformat(),
                "last_modified": model_state.metadata.last_modified.isoformat(),
                "notes": model_state.metadata.notes,
                "tags": model_state.metadata.tags,
                "schema_type": model_state.metadata.schema_type,
                "validation_status": model_state.metadata.validation_status,
                "completeness": model_state.metadata.completeness
            },
            "validation_status": validation_status
        }
    
    def delete_model(self, name: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete a saved model.
        
        Args:
            name: Model name to delete
            confirm: Safety confirmation
            
        Returns:
            Deletion result
        """
        if not confirm:
            return {
                "deleted": False,
                "error": "Deletion requires confirmation",
                "message": "Set confirm=True to delete the model"
            }
        
        if name not in self.models:
            return {
                "deleted": False,
                "error": f"Model '{name}' not found"
            }
        
        # Clear last_loaded if it's the deleted model
        if self.last_loaded == name:
            self.last_loaded = None
        
        del self.models[name]
        
        return {
            "deleted": True,
            "model_name": name,
            "message": f"Model '{name}' deleted successfully"
        }
    
    def rename_model(
        self,
        old_name: str,
        new_name: str,
        update_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rename a saved model.
        
        Args:
            old_name: Current model name
            new_name: New model name
            update_notes: Optional notes update
            
        Returns:
            Rename result
        """
        if old_name not in self.models:
            return {
                "renamed": False,
                "error": f"Model '{old_name}' not found"
            }
        
        if new_name in self.models:
            return {
                "renamed": False,
                "error": f"Model '{new_name}' already exists"
            }
        
        # Move model to new name
        model_state = self.models[old_name]
        model_state.model_id = new_name
        model_state.metadata.last_modified = datetime.now()
        
        if update_notes:
            model_state.metadata.notes = update_notes
        
        self.models[new_name] = model_state
        del self.models[old_name]
        
        # Update last_loaded reference
        if self.last_loaded == old_name:
            self.last_loaded = new_name
        
        return {
            "renamed": True,
            "old_name": old_name,
            "new_name": new_name,
            "message": f"Model renamed from '{old_name}' to '{new_name}'"
        }
    
    def get_model_count(self) -> int:
        """Get the total number of saved models."""
        return len(self.models)
    
    def get_last_loaded(self) -> Optional[str]:
        """Get the name of the last loaded model."""
        return self.last_loaded
    
    def clear_all_models(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clear all saved models (for testing/cleanup).
        
        Args:
            confirm: Safety confirmation
            
        Returns:
            Clear result
        """
        if not confirm:
            return {
                "cleared": False,
                "error": "Clear all requires confirmation"
            }
        
        count = len(self.models)
        self.models.clear()
        self.last_loaded = None
        self.counter = 0
        
        return {
            "cleared": True,
            "models_cleared": count,
            "message": f"Cleared {count} models"
        }
    
    def _generate_model_id(
        self,
        model: Dict[str, Any],
        user_name: Optional[str],
        overwrite: bool
    ) -> str:
        """
        Generate a model ID using hybrid naming strategy.
        
        Args:
            model: The model to generate ID for
            user_name: User-provided name (priority)
            overwrite: Allow overwriting existing names
            
        Returns:
            Generated model ID
        """
        if user_name:
            # User-provided name has priority
            if user_name in self.models and not overwrite:
                # Handle conflict by appending counter
                base_name = user_name
                counter = 1
                while f"{base_name}_v{counter}" in self.models:
                    counter += 1
                return f"{base_name}_v{counter}"
            else:
                return user_name
        else:
            # Auto-generate name
            schema_type, _ = schema_registry.detect_schema_type(model)
            domain = self._detect_domain(model)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.counter += 1
            
            if schema_type and domain:
                base_name = f"{schema_type}_{domain}_{timestamp}"
            elif schema_type:
                base_name = f"{schema_type}_model_{self.counter}"
            else:
                base_name = f"model_{self.counter}"
            
            # Ensure uniqueness
            counter = 1
            final_name = base_name
            while final_name in self.models:
                final_name = f"{base_name}_{counter}"
                counter += 1
            
            return final_name
    
    def _detect_domain(self, model: Dict[str, Any]) -> Optional[str]:
        """
        Detect the domain/industry from model content.
        
        Args:
            model: Model to analyze
            
        Returns:
            Detected domain or None
        """
        # Convert model to lowercase text for analysis
        model_text = self._model_to_text(model).lower()
        
        # Score each domain
        domain_scores = {}
        for domain, keywords in self._domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in model_text)
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        
        return None
    
    def _model_to_text(self, model: Dict[str, Any]) -> str:
        """Convert model dictionary to text for analysis."""
        def extract_text(obj, texts=None):
            if texts is None:
                texts = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    texts.append(str(key))
                    extract_text(value, texts)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item, texts)
            else:
                texts.append(str(obj))
            
            return texts
        
        return " ".join(extract_text(model))
    
    def _extract_validation_status(self, validation_result: Optional[Dict[str, Any]]) -> str:
        """Extract validation status from validation result."""
        if not validation_result:
            return "unknown"
        
        if validation_result.get("valid", False):
            return "valid"
        elif validation_result.get("completeness", 0) > 0.5:
            return "partial"
        else:
            return "invalid"
    
    def _extract_completeness(self, validation_result: Optional[Dict[str, Any]]) -> float:
        """Extract completeness score from validation result."""
        if not validation_result:
            return 0.0
        
        return validation_result.get("completeness", 0.0)


# Global state manager instance
model_state_manager = ModelStateManager()
