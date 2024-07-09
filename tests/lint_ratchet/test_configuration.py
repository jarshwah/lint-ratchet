from textwrap import dedent
from typing import cast

import pytest
import tomllib

from lint_ratchet import configuration


class TestReadConfiguration:
    def test_example_parsed(self):
        parsed = cast(configuration.ConfigDict, tomllib.loads(configuration.TOML_EXAMPLE))
        config = configuration.read_configuration(parsed)
        assert config.path.name == "src"
        assert config.excluded_folders == [
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            ".mypy_cache",
        ]
        rules = config.rules
        for tool in configuration.Tool:
            assert any(rule.tool == tool for rule in rules)

    def test_just_noqa_exists(self):
        toml = dedent("""
            [tool.lint-ratchet]
            path = "src/"

            [tool.lint-ratchet.noqa]
            F401 = 7
        """)
        parsed = cast(configuration.ConfigDict, tomllib.loads(toml))
        config = configuration.read_configuration(parsed)
        assert len(config.rules) == 1
        assert config.rules[0] == configuration.Rule(
            tool=configuration.Tool.NOQA, code="F401", violation_count=7
        )

    def test_no_configuration(self):
        with pytest.raises(configuration.RatchetNotConfigured):
            configuration.read_configuration({})  # type: ignore [typeddict-item]

    def test_violation_count_not_int(self):
        toml = dedent("""
            [tool.lint-ratchet.noqa]
            F401 = "wot"
        """)
        parsed = cast(configuration.ConfigDict, tomllib.loads(toml))
        with pytest.raises(configuration.RatchetMisconfigured):
            configuration.read_configuration(parsed)
