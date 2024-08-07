import pathlib
from textwrap import dedent
from typing import cast

import pytest
import tomllib

from lint_ratchet import configuration


class TestReadConfiguration:
    def test_example_parsed(self):
        parsed = cast(configuration.RatchetConfig, tomllib.loads(configuration.TOML_EXAMPLE))
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
            path = "src/"

            [noqa]
            F401 = 7
        """)
        parsed = cast(configuration.RatchetConfig, tomllib.loads(toml))
        config = configuration.read_configuration(parsed)
        assert len(config.rules) == 1
        assert config.rules[0] == configuration.Rule(
            tool=configuration.Tool.NOQA, code="F401", violation_count=7
        )

    def test_path_not_configured(self):
        toml = dedent("""
            [noqa]
            F401 = "wot"
        """)
        parsed = cast(configuration.RatchetConfig, tomllib.loads(toml))
        with pytest.raises(configuration.RatchetMisconfiguredError, match="`path`"):
            configuration.read_configuration(parsed)

    def test_violation_count_not_int(self):
        toml = dedent("""
            path = "src/"

            [noqa]
            F401 = "wot"
        """)
        parsed = cast(configuration.RatchetConfig, tomllib.loads(toml))
        with pytest.raises(configuration.RatchetMisconfiguredError, match="F401"):
            configuration.read_configuration(parsed)


class TestOpenConfiguration:
    def test_example_config_loads(self):
        root = pathlib.Path(__file__).parent.parent / "examples"
        config = configuration.open_configuration(root)
        assert config.path == pathlib.Path(".")

    def test_example_config_not_found(self):
        with pytest.raises(configuration.ProjectFileNotFoundError):
            configuration.open_configuration(pathlib.Path("/tmp/madeup"))

    def test_example_config_loads_when_path_is_file(self):
        root = pathlib.Path(__file__).parent.parent / "examples" / ".ratchet.toml"
        config = configuration.open_configuration(root)
        assert config.path == pathlib.Path(".")

    def test_not_found_when_not_configuration_file(self):
        root = pathlib.Path(__file__).parent.parent / "examples" / "__init__.py"
        with pytest.raises(configuration.ProjectFileNotFoundError):
            configuration.open_configuration(root)


class TestWriteConfiguration:
    def test_example_config_roundtrips(self, tmp_path: pathlib.Path) -> None:
        root = pathlib.Path(__file__).parent.parent / "examples"
        config = configuration.open_configuration(root)
        config_file = tmp_path / ".ratchet.toml"
        with config_file.open("w") as f:
            configuration.write_configuration(config, f)
        config2 = configuration.open_configuration(config_file)
        assert config == config2

    def test_full_config_writes(self, tmp_path: pathlib.Path) -> None:
        config = configuration.Config(
            path=pathlib.Path("src/"),
            rules=[
                configuration.Rule(configuration.Tool.NOQA, "F401", 7),
                configuration.Rule(configuration.Tool.NOQA, "F402", 8),
                configuration.Rule(configuration.Tool.FIXIT_FIXME, "FixMe", 9),
                configuration.Rule(configuration.Tool.FIXIT_IGNORE, "IgnoreMe", 2),
                configuration.Rule(configuration.Tool.FIXIT_ANY, "FixThis", 1),
                configuration.Rule(configuration.Tool.MYPY, "misc", 0),
            ],
            excluded_folders=["__pycache__", ".git"],
        )
        config_file = tmp_path / ".ratchet.toml"
        with config_file.open("w") as f:
            configuration.write_configuration(config, f)
        config2 = configuration.open_configuration(config_file)
        assert config == config2
