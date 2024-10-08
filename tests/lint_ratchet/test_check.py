import io
import pathlib
from textwrap import dedent

from lint_ratchet import check
from lint_ratchet.checkers import Violation, get_checkers
from lint_ratchet.configuration import Config, Rule, Tool


class TestCheckFile:
    def test_check_file(self):
        checkers = get_checkers(
            [
                Rule(tool=Tool.NOQA, code="F401", violation_count=1),
                Rule(tool=Tool.NOQA, code="G007", violation_count=2),
                Rule(tool=Tool.NOQA, code="B040", violation_count=3),
            ]
        )
        source = dedent(
            """
            import a  # noqa: F401
            import b  # noqa: F401

            def f(a) -> None:  # noqa: G007
                return None
            """
        )
        violations = list(check.check_file(io.BytesIO(source.encode()), checkers))
        assert violations == [
            Violation(rule="F401", count=2),
            Violation(rule="G007", count=1),
        ]


class TestRecursePaths:
    def test_paths_found_with_exclusion(self):
        root = pathlib.Path(__file__).parent.parent / "examples/"
        paths = {p.name for p in check._recurse_paths([root], ["excluded"])}
        assert paths == {"example.py", "basic.py", "__init__.py"}


class TestCheckRecursive:
    def test_violations_found(self):
        root = pathlib.Path(__file__).parent.parent
        config = Config(
            path=pathlib.Path("examples/"),
            rules=[
                Rule(tool=Tool.NOQA, code="F401", violation_count=1),
            ],
            excluded_folders=["excluded"],
        )
        check_dir = root / config.path
        violations = list(check.check_recursive(check_dir, config))
        assert violations == [Violation(rule="F401", count=2)]
