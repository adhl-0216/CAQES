import importlib
import pkgutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def discover_integrations():
    """Auto-discover and import all integration modules."""
    integration_path = Path(__file__).parent
    
    # Discover protocol integrations
    protocol_path = integration_path / "protocol"
    for module_info in pkgutil.iter_modules([str(protocol_path)]):
        if not module_info.name.startswith('_'):
            try:
                importlib.import_module(f"{__package__}.protocol.{module_info.name}")
                logger.debug(f"Loaded protocol integration: {module_info.name}")
            except Exception as e:
                raise e
    # Discover network integrations
    network_path = integration_path / "network"
    for module_info in pkgutil.iter_modules([str(network_path)]):
        if not module_info.name.startswith('_'):
            try:
                importlib.import_module(f"{__package__}.network.{module_info.name}")
                logger.debug(f"Loaded network integration: {module_info.name}")
            except Exception as e:
                raise e
discover_integrations()
