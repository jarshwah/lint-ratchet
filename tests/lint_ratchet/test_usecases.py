import pathlib

from lint_ratchet import configuration, usecases


class TestCheck:
    def test_check(self):
        check_dir = pathlib.Path(__file__).parent.parent / "examples/"
        config = configuration.Config(
            path=pathlib.Path("."),
            rules=[
                configuration.Rule(tool=configuration.Tool.NOQA, code="F401", violation_count=1),
            ],
            excluded_folders=[],
        )
        results = list(usecases.check(check_dir, config))
        assert results == [usecases.CheckResult(rule=config.rules[0], new_count=3)]

    def test_check_excluded(self):
        check_dir = pathlib.Path(__file__).parent.parent / "examples/"
        config = configuration.Config(
            path=pathlib.Path("."),
            rules=[
                configuration.Rule(tool=configuration.Tool.NOQA, code="F401", violation_count=1),
            ],
            excluded_folders=["excluded"],
        )
        results = list(usecases.check(check_dir, config))
        assert results == [usecases.CheckResult(rule=config.rules[0], new_count=2)]
