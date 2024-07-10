import io
import pathlib
from collections.abc import Collection, Iterable, Set

from .checkers import Checker, Violation, get_checkers
from .configuration import Config
from .parsing import extract_comments


def check_recursive(root: pathlib.Path, config: Config) -> Iterable[Violation]:
    """
    Check all python files in the given project directory for matching violation counts.

    Searches the configured directory from the root, recursively, for all python files.
    It then extracts the comments from each file, and checks them against all rules
    in the configuration. If a rule is matched, it is returned as a violation with the
    number of matches.
    """
    checkers = get_checkers(config.rules)
    check = (root / config.path).resolve()
    violations: list[Violation] = []
    for path in _recurse_paths([check], config.excluded_folders):
        with path.open("rb") as file_like:
            violations.extend(list(check_file(file_like, checkers)))
    return violations


def check_file(file_like: io.BufferedIOBase, checkers: Set[Checker]) -> Iterable[Violation]:
    """
    Check a given file like object for matching violation counts.

    `file_like` is expected to be a binary file-like object such as io.BytesIO or
    the result of `open(fp, "rb")`.

    Comments are extracted from the file like object and scanned for matching
    violations.
    """
    comments = list(extract_comments(file_like))
    if not comments:
        return
    for checker in checkers:
        yield from checker.check(comments)


def _recurse_paths(
    children: Iterable[pathlib.Path], excluded_folders: Collection[str]
) -> Iterable[pathlib.Path]:
    for child in children:
        if child.is_file() and child.suffix == ".py":
            yield child
        elif child.is_dir() and child.name not in excluded_folders:
            yield from _recurse_paths(child.iterdir(), excluded_folders)
