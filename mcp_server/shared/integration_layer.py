"""
Integration layer for external modules with fallback support.

This module manages integration with external simulation libraries (particularly
PySD for System Dynamics) while providing graceful fallback mechanisms when
dependencies are unavailable.
"""

import sys
from pathlib import Path
from typing import Optional, Any, Dict, List
import logging

# Configure logging for integration layer
logger = logging.getLogger(__name__)


class SDIntegrationError(Exception):
    """Base exception for SD integration errors."""
    pass


class SDValidationError(SDIntegrationError):
    """Exception for SD validation errors."""
    pass


class SDModelBuildError(SDIntegrationError):
    """Exception for SD model building errors."""
    pass


class SDSimulationError(SDIntegrationError):
    """Exception for SD simulation execution errors."""
    pass


class DummySDIntegration:
    """Fallback implementation when SD integration is unavailable."""

    def validate_json_model(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Dummy validation that always returns unavailable status."""
        return {
            "is_valid": False,
            "errors": ["SD integration not available"],
            "message": "PySD integration module not found"
        }

    def simulate_json_model(self, model: Dict[str, Any], **kwargs) -> Any:
        """Dummy simulation that raises unavailable error."""
        raise SDSimulationError("SD integration not available")

    def get_model_info(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Dummy model info that returns unavailable status."""
        return {
            "error": "SD integration not available",
            "available_features": [],
            "message": "Install PySD dependencies to enable SD simulation"
        }

    def convert_vensim_to_json(self, file_path: str) -> Dict[str, Any]:
        """Dummy conversion that raises unavailable error."""
        raise SDModelBuildError("SD integration not available")


class IntegrationManager:
    """
    Manages integration with external modules providing fallback support.

    Handles dynamic loading of simulation libraries with graceful degradation
    when dependencies are missing or incompatible.
    """

    def __init__(self):
        self._sd_integration = None
        self._sd_available = False
        self._initialization_attempted = False
        self._initialization_error = None
        self._initialize_sd_integration()

    def _initialize_sd_integration(self) -> None:
        """Initialize SD integration with comprehensive error handling."""
        if self._initialization_attempted:
            return

        self._initialization_attempted = True

        try:
            # Add current directory to Python path for local imports
            current_dir = Path(__file__).parent.parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))

            # Attempt to import SD integration
            from SD.sd_integration import PySDJSONIntegration

            # Initialize the integration
            self._sd_integration = PySDJSONIntegration()
            self._sd_available = True

            logger.info("SD JSON integration initialized successfully")
            print("[SUCCESS] SD JSON integration initialized successfully", file=sys.stderr)

        except ImportError as e:
            self._handle_import_error(e)
        except Exception as e:
            self._handle_initialization_error(e)

    def _handle_import_error(self, error: ImportError) -> None:
        """Handle SD integration import errors with detailed logging."""
        self._initialization_error = error
        self._sd_integration = DummySDIntegration()
        self._sd_available = False

        error_msg = f"SD integration import failed: {error}"
        logger.warning(error_msg)
        print(f"[ERROR] {error_msg}", file=sys.stderr)

        # Provide helpful context
        current_dir = Path(__file__).parent.parent
        print(f"   Current directory: {current_dir}", file=sys.stderr)
        print(f"   Python path includes: {current_dir in [Path(p) for p in sys.path]}", file=sys.stderr)

    def _handle_initialization_error(self, error: Exception) -> None:
        """Handle SD integration initialization errors."""
        self._initialization_error = error
        self._sd_integration = DummySDIntegration()
        self._sd_available = False

        error_msg = f"SD integration initialization failed: {error}"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}", file=sys.stderr)

    @property
    def sd_integration(self) -> Any:
        """
        Get SD integration instance.

        Returns either the real PySDJSONIntegration instance or a dummy
        fallback implementation depending on availability.
        """
        return self._sd_integration

    @property
    def sd_available(self) -> bool:
        """Check if SD integration is available and functional."""
        return self._sd_available

    @property
    def initialization_error(self) -> Optional[Exception]:
        """Get the initialization error if one occurred."""
        return self._initialization_error

    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all integrations.

        Returns:
            Dictionary with integration availability and error information
        """
        return {
            "sd_integration": {
                "available": self._sd_available,
                "initialized": self._initialization_attempted,
                "error": str(self._initialization_error) if self._initialization_error else None,
                "implementation": "PySDJSONIntegration" if self._sd_available else "DummySDIntegration"
            }
        }

    def validate_sd_availability(self) -> None:
        """
        Validate SD integration availability and raise appropriate error.

        Raises:
            SDIntegrationError: If SD integration is not available
        """
        if not self._sd_available:
            error_msg = "SD integration not available"
            if self._initialization_error:
                error_msg += f": {self._initialization_error}"
            raise SDIntegrationError(error_msg)

    def get_fallback_recommendations(self) -> List[str]:
        """
        Get recommendations for resolving integration issues.

        Returns:
            List of actionable recommendations
        """
        if self._sd_available:
            return ["SD integration is working correctly"]

        recommendations = [
            "Install PySD dependencies: pip install pysd>=3.12.0",
            "Verify SD module structure in project directory",
            "Check Python path includes project root directory"
        ]

        if self._initialization_error:
            if "ImportError" in str(type(self._initialization_error)):
                recommendations.extend([
                    "Ensure all PySD dependencies are installed",
                    "Check for module naming conflicts"
                ])
            else:
                recommendations.append(
                    f"Debug initialization error: {self._initialization_error}"
                )

        return recommendations

    def retry_initialization(self) -> bool:
        """
        Retry SD integration initialization.

        Returns:
            True if initialization succeeded, False otherwise
        """
        self._initialization_attempted = False
        self._initialization_error = None
        self._initialize_sd_integration()
        return self._sd_available


# Global integration manager instance
integration_manager = IntegrationManager()


def get_integration_manager() -> IntegrationManager:
    """Get the global integration manager instance."""
    return integration_manager


def ensure_sd_integration() -> Any:
    """
    Ensure SD integration is available and return the instance.

    Returns:
        SD integration instance

    Raises:
        SDIntegrationError: If SD integration is not available
    """
    integration_manager.validate_sd_availability()
    return integration_manager.sd_integration