"""Shared HTTP/API contract literals.

Dependency-free so `client.py` can import supported operator states without pulling FastAPI.
"""

from typing import Literal

# Optional POST /compute field: activates trajectory / semantic annotation branches in api.py.
OperatorState = Literal["INTENTIONAL", "BLACK", "SSSEVERUS", "LILY", "PHOENIX", "MAP"]

OPERATOR_STATE_VALUES: frozenset[str] = frozenset(
    ("INTENTIONAL", "BLACK", "SSSEVERUS", "LILY", "PHOENIX", "MAP"),
)
