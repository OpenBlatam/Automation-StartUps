from __future__ import annotations

from typing import TypedDict, Optional


class ExtractPayload(TypedDict, total=False):
	rows: int
	transformed: bool
	since: Optional[str]
	until: Optional[str]
	checksum: Optional[int]
	null_rate: Optional[float]


DEFAULT_ROWS: int = 1000
DEFAULT_RUN_NAME: str = "etl_example"
