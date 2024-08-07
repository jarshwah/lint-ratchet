import pathlib

from click.testing import CliRunner

from lint_ratchet import configuration
from lint_ratchet.cli import main


class TestCheckCommand:
    def test_check_command(self):
        root_path = (pathlib.Path(__file__).parent.parent / "examples").resolve()
        runner = CliRunner()
        result = runner.invoke(main, ["--root", f"{root_path}", "check"])
        assert result.exit_code == 1
        assert "noqa.F401 failed: 2 > 1" in result.output


class TestCrankCommand:
    def test_nothing_to_crank(self):
        root_path = (pathlib.Path(__file__).parent.parent / "examples").resolve()
        runner = CliRunner()
        result = runner.invoke(main, ["--root", f"{root_path}", "crank"])
        assert result.exit_code == 0
        assert "No rules were cranked" in result.output

    def test_writes_cranked_values_back(self, tmp_path: pathlib.Path) -> None:
        root_path = tmp_path
        config = configuration.Config(
            path=pathlib.Path("."),
            rules=[
                configuration.Rule(tool=configuration.Tool.NOQA, code="F401", violation_count=2)
            ],
        )
        with (root_path / ".ratchet.toml").open("w") as f:
            configuration.write_configuration(config, f)

        with (root_path / "foo.py").open("w") as f:
            f.write("import os  # noqa: F401\n")

        runner = CliRunner()
        result = runner.invoke(main, ["--root", f"{root_path}", "crank"])
        assert result.exit_code == 0
        assert "1 rules cranked" in result.output

        new_config = configuration.open_configuration(root_path)
        assert new_config.rules[0].code == "F401"
        assert new_config.rules[0].violation_count == 1
