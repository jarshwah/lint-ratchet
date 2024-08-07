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


def crank(
    check_dir: pathlib.Path, config: configuration.Config, root_dir: pathlib.Path
) -> Iterable[CheckResult]:
    """
    Recompute the violation counts and write the results back if they are lower.
    """
    counts: Counter[str] = Counter()
    for violation in check_module.check_recursive(check_dir, config):
        counts[violation.rule] += violation.count

    new_rules = []
    cranked = []
    for rule in config.rules:
        if (new_count := counts[rule.code]) < rule.violation_count:
            new_rules.append(dataclasses.replace(rule, violation_count=new_count))
            cranked.append(CheckResult(rule, new_count))

    if cranked:
        new_config = dataclasses.replace(config, rules=new_rules)
        config_path = configuration.get_configuration_path(root_dir)
        with config_path.open("w") as f:
            configuration.write_configuration(new_config, f)

    return cranked
