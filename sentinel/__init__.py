# sentinel/__init__.py

# Import all public symbols from each module
from .prompt_sentinel import *
from .sentinel_detectors import *
from .utils import *
from .wrappers import *

# Optionally, define __all__ to explicitly state your public API.
# If your individual modules already define __all__, you can combine them like so:
__all__ = []

# Helper to extend __all__ from a module if it defines one,
# otherwise include all names not starting with an underscore.
def _get_public_names(module):
    if hasattr(module, "__all__"):
        return module.__all__
    else:
        return [name for name in dir(module) if not name.startswith("_")]

import sentinel.prompt_sentinel
import sentinel.sentinel_detectors
import sentinel.wrappers

__all__.extend(_get_public_names(prompt_sentinel))
__all__.extend(_get_public_names(sentinel_detectors))
__all__.extend(_get_public_names(wrappers))
