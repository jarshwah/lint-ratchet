import dataclasses
import pathlib
from collections import Counter
from collections.abc import Iterable

from . import check as check_module
from . import configuration


@dataclasses.dataclass
class CheckResult:
    rule: configuration.Rule
    new_count: int

    @property
    def failure(self) -> bool:
        return self.new_count > self.rule.violation_count


def check(check_dir: pathlib.Path, config: configuration.Config) -> Iterable[CheckResult]:
    """
    Scan the project for matching rule violations and yield the results.
    """
    counts: Counter[str] = Counter()
    for violation in check_module.check_recursive(check_dir, config):
        counts[violation.rule] += violation.count

    for rule in config.rules:
        yield CheckResult(rule, counts[rule.code])
