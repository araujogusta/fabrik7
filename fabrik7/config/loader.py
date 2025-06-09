import json
from pathlib import Path
from typing import Callable, Mapping

import yaml
from pydantic import ValidationError

from fabrik7.config.models import Config


class ConfigLoader:
    """Load config files (.yaml/.yml ou .json) and return a Config object."""

    __PARSERS: Mapping[str, Callable[[str], dict]] = {
        ".yaml": yaml.safe_load,
        ".yml": yaml.safe_load,
        ".json": json.loads,
    }

    @classmethod
    def load(cls, path: str | Path) -> Config:
        """Reads *path*, validates against the schema, and returns Config."""
        path = Path(path)
        parser = cls.__pick_parser(path)

        raw_text = path.read_text()
        try:
            data = parser(raw_text)
        except Exception as err:
            raise ValueError(f"Falha ao parsear '{path.name}': {err}") from err

        try:
            return Config.model_validate(data)
        except ValidationError as err:
            raise ValueError(f"Configuração inválida em '{path.name}':\n{err}") from err

    @classmethod
    def __pick_parser(cls, path: Path) -> Callable[[str], dict]:
        ext = path.suffix.lower()
        if parser := cls.__PARSERS.get(ext):
            return parser
        raise ValueError(
            f"Extensão não suportada: {ext}. "
            "Use .yaml, .yml ou .json."
        )
