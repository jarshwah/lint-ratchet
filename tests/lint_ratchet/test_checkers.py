from lint_ratchet.checkers import NoQAChecker, Violation
from lint_ratchet.configuration import Rule, Tool


class TestNoQAChecker:
    def test_no_violations(self):
        checker = NoQAChecker([])
        assert checker.check([]) == []

    def test_no_rules(self):
        checker = NoQAChecker([])
        assert checker.check(["# noqa: F401"]) == []

    def test_multiple_comments(self):
        checker = NoQAChecker([Rule(tool=Tool.NOQA, code="F401", violation_count=1)])
        comments = ["# noqa: F401", "# noqa: F401", "# noqa: F401"]
        assert checker.check(comments) == [Violation(rule="F401", count=3)]

    def test_multiple_rules(self):
        rules = [
            Rule(tool=Tool.NOQA, code="F401", violation_count=1),
            Rule(tool=Tool.NOQA, code="BB12", violation_count=1),
        ]
        checker = NoQAChecker(rules)
        comments = ["# noqa: F401", "# noqa: F401", "# noqa: BB12"]
        assert checker.check(comments) == [
            Violation(rule="F401", count=2),
            Violation(rule="BB12", count=1),
        ]

    def test_comma_separated_violations(self):
        rules = [
            Rule(tool=Tool.NOQA, code="F401", violation_count=1),
            Rule(tool=Tool.NOQA, code="BB12", violation_count=1),
        ]
        checker = NoQAChecker(rules)
        comments = ["# noqa: F401, BB12, ignore", "# noqa: F401", "# noqa: BB12", "# noqa: ignore"]
        assert checker.check(comments) == [
            Violation(rule="F401", count=2),
            Violation(rule="BB12", count=2),
        ]
