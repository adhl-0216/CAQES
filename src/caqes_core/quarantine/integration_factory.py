import logging
from typing import Dict, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

class IntegrationFactory:
    """Generic factory for quarantine modules."""
    
    def __init__(self):
        self._registry: Dict[str, Dict[str, Type[T]]] = {
            "protocol": {},
            "network": {}
        }
        
    def register(self, type_: str, name: str):
        """Decorator to register a quarantine module."""
        def decorator(subclass):
            self._registry[type_][name] = subclass
            logger.debug(f"Registering {type_} module: {name} -> {subclass.__name__}")
            return subclass
        return decorator

    def create(self, type_: str, module_type: str, **kwargs) -> T:
        """Factory method to create a module instance."""
        if module_type not in self._registry[type_]:
            raise ValueError(f"Unknown {type_} quarantine module: {module_type}")
        return self._registry[type_][module_type](**kwargs)

# Global factory instance
integration_factory = IntegrationFactory()
