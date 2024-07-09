from collections import deque
from collections.abc import Iterable, Sequence

import libcst as cst


def extract_comments(source_code: str | bytes) -> Iterable[str]:
    """
    Extract all of the comments from the source code.

    Of note, this does *not* produce the comments in the order they appear in the source code, as
    it works by extracting the head, middle, and foot of each node as it works down the tree.

    We don't care about the order though, so no attempt to produce comments in the
    correct order is taken.
    """
    module = cst.parse_module(source_code)
    nodes: deque[cst.CSTNode] = deque([module])
    nodes.extend(module.children)
    while nodes:
        node = nodes.popleft()

        # Adapted from fixit.LintRule.node_comments
        if isinstance(node, cst.Module):
            for line in node.header:
                if line.comment:
                    yield line.comment.value
            for line in node.footer:
                if line.comment:
                    yield line.comment.value
            continue

        tw: cst.TrailingWhitespace | None = getattr(node, "trailing_whitespace", None)
        if tw is None:
            body: cst.BaseSuite | None = getattr(node, "body", None)
            if isinstance(body, cst.SimpleStatementSuite):
                tw = body.trailing_whitespace
            elif isinstance(body, cst.IndentedBlock):
                tw = body.header

        if tw and tw.comment:
            yield tw.comment.value

        ll: Sequence[cst.EmptyLine] | None = getattr(node, "leading_lines", None)
        if ll is not None:
            for line in ll:
                if line.comment:
                    yield line.comment.value

        # Recurse into the node's children
        nodes.extend(node.children)
