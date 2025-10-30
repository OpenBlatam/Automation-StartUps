from __future__ import annotations

from typing import TypedDict


class ExtractPayload(TypedDict):
	rows: int
	transformed: bool


DEFAULT_ROWS: int = 1000
DEFAULT_RUN_NAME: str = "etl_example"
