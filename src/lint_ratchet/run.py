import pathlib
from collections.abc import Iterable, Set

from .checkers import Checker, Violation, get_checkers
from .configuration import Config, Rule
from .parsing import extract_comments


def check_recursive(root: pathlib.Path, config: Config) -> Iterable[Violation]:
    """
    Checks all python files in the given project directory for matching violation counts.

    Searches the configured directory from the root, recursively, for all python files.
    It then extracts the comments from each file, and checks them against all rules
    in the configuration. If a rule is found, it is returned as a violation with the
    number of matches.
    """
    checkers = get_checkers(config.rules)
    check = (root / config.path).resolve()
    violations: list[Violation] = []
    for path in _children([check], config):
        violations.extend(list(_check_file(path, config.rules, checkers)))
    return violations


def _check_file(
    path: pathlib.Path, rules: Iterable[Rule], checkers: Set[Checker]
) -> Iterable[Violation]:
    comments = list(extract_comments(path.open("rb")))
    if not comments:
        return
    for checker in checkers:
        yield from checker.check(comments)


def _children(children: Iterable[pathlib.Path], config: Config) -> Iterable[pathlib.Path]:
    for child in children:
        if child.is_file() and child.suffix == ".py":
            yield child
        elif child.is_dir() and child.name not in config.excluded_folders:
            yield from _children(child.iterdir(), config)
