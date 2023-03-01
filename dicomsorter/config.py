import logging
import pathlib
import sys
from dataclasses import dataclass, field, fields
from typing import Any, Dict, List

_default_path = [
    "SeriesDescription",
]


@dataclass
class Config:
    input_directory: pathlib.Path
    output_directory: pathlib.Path

    filename_format: str = "%(ImageType)s (%(InstanceNumber)04d)%(Extension)s"
    path: List[str] = field(default_factory=lambda: _default_path)
    concurrency: int = 2

    dry_run: bool = False
    move: bool = False
    original_filename: bool = False
    overwrite: bool = False
    verbose: bool = False

    anonymize: bool = False

    @classmethod
    def from_dict(cls, env: Dict[str, Any]) -> "Config":
        valid_fields = [f.name for f in fields(cls)]
        valid_values = {k: v for k, v in env.items() if k in valid_fields}

        return cls(**valid_values)

    @classmethod
    def default_path(cls) -> List[str]:
        return list(_default_path)


logger = logging.getLogger("dicomsorter")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
