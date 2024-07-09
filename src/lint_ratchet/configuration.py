from __future__ import annotations

import dataclasses
import enum
import pathlib
from typing import NotRequired, Sequence, TypedDict


TOML_EXAMPLE = """
[tool.lint-ratchet]
path = "src"

[tool.lint-ratchet.noqa]
F401 = 0

[tool.lint-ratchet.fixit]
FixitRule = 43

[tool.lint-ratchet.fixit-ignore]
FixitRuleIgnoreOnly = 3

[tool.lint-ratchet.fixit-fixme]
FixitRuleFixmeOnly = 43

[tool.lint-ratchet.mypy]
assignment = 2
"""

RatchetDict = TypedDict(
    "RatchetDict",
    {
        "path": str,
        "noqa": NotRequired[dict[str, int]],
        "fixit": NotRequired[dict[str, int]],
        "fixit-ignore": NotRequired[dict[str, int]],
        "fixit-fixme": NotRequired[dict[str, int]],
        "mypy": NotRequired[dict[str, int]],
    },
)


ToolDict = TypedDict(
    "ToolDict",
    {
        "lint-ratchet": RatchetDict,
    },
)


class ConfigDict(TypedDict):
    tool: ToolDict


class RatchetNotConfigured(Exception):
    pass


class RatchetMisconfigured(Exception):
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


def read_configuration(toml_config: ConfigDict) -> Config:
    """
    Read the configuration from a parsed TOML file.
    """
    rules: list[Rule] = []
    try:
        ratchet_section = toml_config["tool"]["lint-ratchet"]
        if not isinstance(ratchet_section, dict):
            raise RatchetMisconfigured("[tool.lint-ratchet] section must be a dictionary")
    except KeyError:
        raise RatchetNotConfigured("[tool.lint-ratchet] section not found") from None

    if "path" not in ratchet_section:
        raise RatchetMisconfigured("[tool.lint-ratchet].path not found")

    path = ratchet_section["path"]

    for tool in Tool:
        tool_section = ratchet_section.get(tool.value)
        if isinstance(tool_section, dict):
            for code, violation_count in tool_section.items():
                if not isinstance(violation_count, int):
                    raise RatchetMisconfigured(
                        f"Violation count for tool.lint-ratchet.{tool.value}.{code} must be a number"
                    )
                rules.append(Rule(tool, code, int(violation_count)))
    return Config(path=pathlib.Path(path), rules=rules)
