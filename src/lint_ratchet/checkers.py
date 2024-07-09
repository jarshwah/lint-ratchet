import dataclasses
from collections import Counter
from collections.abc import Sequence
from typing import Protocol, TypeAlias

from lint_ratchet.configuration import Rule, Tool


Comment: TypeAlias = str


@dataclasses.dataclass(frozen=True, slots=True)
class Violation:
    rule: str
    count: int


class Checker(Protocol):
    def __init__(self, rules: Sequence[Rule]) -> None: ...

    def check(self, comments: Sequence[Comment]) -> Sequence[Violation]: ...


class NoQAChecker:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = [rule for rule in rules if rule.tool == Tool.NOQA]
        self.codes = {rule.code for rule in self.rules}
        self.violations: Counter[str] = Counter()

    def check(self, comments: Sequence[Comment]) -> Sequence[Violation]:
        if not self.rules:
            return []

        self.violations.clear()
        for comment in comments:
            if not comment.startswith("# noqa:"):
                continue

            for violation in comment.removeprefix("# noqa: ").split(","):
                self.violations[violation.strip()] += 1

        return [
            Violation(rule=violation, count=count)
            for violation, count in self.violations.items()
            if violation in self.codes
        ]
