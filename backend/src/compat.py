from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any


def dataclass_with_slots(*args: Any, **kwargs: Any):
    """Use slots on Python 3.10+, silently ignore on 3.9."""
    if sys.version_info >= (3, 10):
        kwargs.setdefault("slots", True)
    else:
        kwargs.pop("slots", None)
    return dataclass(*args, **kwargs)
