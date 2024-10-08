from __future__ import annotations

import dataclasses
import enum
import pathlib
from collections.abc import Collection
from typing import IO, NotRequired, Sequence, TypedDict

import toml as tomllib


TOML_EXAMPLE = """
path = "src"
exclude = ["__pycache__", ".git", ".venv", "node_modules", ".mypy_cache"]

[noqa]
F401 = 0

[fixit]
FixitRule = 43

[fixit-ignore]
FixitRuleIgnoreOnly = 3

[fixit-fixme]
FixitRuleFixmeOnly = 43

[mypy]
assignment = 2
"""

RatchetConfig = TypedDict(
    "RatchetConfig",
    {
        "path": str,
        "exclude": NotRequired[Sequence[str]],
        "noqa": NotRequired[dict[str, int]],
        "fixit": NotRequired[dict[str, int]],
        "fixit-ignore": NotRequired[dict[str, int]],
        "fixit-fixme": NotRequired[dict[str, int]],
        "mypy": NotRequired[dict[str, int]],
    },
)


class RatchetMisconfiguredError(Exception):
    pass


class ProjectFileNotFoundError(FileNotFoundError):
    pass


@enum.unique
class Tool(str, enum.Enum):
    NOQA = "noqa"
    FIXIT_FIXME = "fixit-fixme"
    FIXIT_IGNORE = "fixit-ignore"
    FIXIT_ANY = "fixit"
    MYPY = "mypy"


@dataclasses.dataclass(frozen=True, slots=True)
class Rule:
    tool: Tool
    code: str
    violation_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class Config:
    path: pathlib.Path
    rules: Sequence[Rule]
    excluded_folders: Collection[str] = dataclasses.field(default_factory=list)

    def to_toml_dict(self) -> RatchetConfig:
        config = RatchetConfig(path=str(self.path))
        if self.excluded_folders:
            config["exclude"] = list(self.excluded_folders)
        for rule in self.rules:
            config.setdefault(rule.tool.value, {})[rule.code] = rule.violation_count  # type: ignore[misc]
        return config


def read_configuration(toml_config: RatchetConfig) -> Config:
    """
    Read the configuration from a parsed TOML file.
    """
    rules: list[Rule] = []

    if "path" not in toml_config:
        raise RatchetMisconfiguredError("Key `path` not found")

    path = toml_config["path"]
    exclude = toml_config.get(
        "exclude", ["__pycache__", ".git", ".venv", "node_modules", ".mypy_cache"]
    )

    for tool in Tool:
        tool_section = toml_config.get(tool.value)
        if isinstance(tool_section, dict):
            for code, violation_count in tool_section.items():
                if not isinstance(violation_count, int):
                    raise RatchetMisconfiguredError(
                        f"Violation count for `{tool.value}.{code}` must be a number"
                    )
                rules.append(Rule(tool, code, int(violation_count)))
    return Config(pathlib.Path(path), rules=rules, excluded_folders=exclude)


def open_configuration(root_path: pathlib.Path, config_file_name: str = ".ratchet.toml") -> Config:
    """
    Open and parse the configuration file.
    """
    config_file = get_configuration_path(root_path, config_file_name)

    if not config_file.exists():
        raise ProjectFileNotFoundError(f"Configuration file {config_file} not found")

    with config_file.open("r") as fp:
        toml = tomllib.load(fp)
    return read_configuration(toml)  # type: ignore [arg-type]


def write_configuration(config: Config, destination: IO[str]) -> str:
    """
    Write the configuration to the file.
    """
    return tomllib.dump(config.to_toml_dict(), destination)


def get_configuration_path(
    root_path: pathlib.Path, config_file_name: str = ".ratchet.toml"
) -> pathlib.Path:
    """
    Return the path to the configuration file.

    Given a root directory and a filename, return the path to the configuration file.

    If the root directory is a file and has the same name as the configuration file,
    use that. Otherwise, append the configuration file name to the root directory and return.
    """
    if root_path.is_file() and root_path.name == config_file_name:
        return root_path.resolve()
    return (root_path / config_file_name).resolve()
