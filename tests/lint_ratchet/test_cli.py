import pathlib

from click.testing import CliRunner

from lint_ratchet.cli import main


class TestCheckCommand:
    def test_check_command(self):
        root_path = (pathlib.Path(__file__).parent.parent / "examples").resolve()
        runner = CliRunner()
        result = runner.invoke(main, ["--root", f"{root_path}", "check"])
        assert result.exit_code == 1
        assert "noqa.F401 failed: 2 > 1" in result.output
