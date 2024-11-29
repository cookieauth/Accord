# app/crud/__init__.py

import importlib
import pkgutil
import sys
from typing import List
import logging

logger = logging.getLogger(__name__)

__all__: List[str] = []

package_name = __name__

for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    try:
        module = importlib.import_module(f"{package_name}.{module_name}")

        crud_instance = getattr(module, "crud", None)

        if crud_instance:
            setattr(sys.modules[package_name], module_name, crud_instance)

            __all__.append(module_name)
            logger.info(f"Loaded CRUD module: {module_name}")
        else:
            logger.warning(f"No 'crud' instance found in module: {module_name}")
    except Exception as e:
        logger.error(f"Error loading module {module_name}: {e}")
