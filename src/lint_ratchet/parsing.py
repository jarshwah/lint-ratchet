import io
import tokenize
from collections.abc import Iterable


def extract_comments(reader: io.BufferedIOBase) -> Iterable[str]:
    """
    Extracts the comments from a python file byte stream.
    """
    tokens = tokenize.tokenize(reader.readline)
    for token in tokens:
        if token.type == tokenize.COMMENT:
            yield token.string
