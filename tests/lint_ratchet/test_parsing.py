import io
from textwrap import dedent

from lint_ratchet import parsing


class TestExtractComments:
    def test_produces_all_comments(self):
        source = dedent(
            """
            # a module comment
            import a  # noqa: F401

            class B:  # classb
                l = []  # noqa: RUF012
                def something(self):  # noqa: ANN001
                    # ignore-this-1
                    return 7  # it's 7

                # a method comment
                def other(self):  # noqa: ANN002
                    # ignore-this-2
                    return 8  # it's 8

            # you got to the bottom?
            """
        )
        num_comments = source.count("#")
        suppressions = list(parsing.extract_comments(io.BytesIO(source.encode())))
        assert num_comments == len(suppressions)
        assert suppressions == [
            "# a module comment",
            "# noqa: F401",
            "# classb",
            "# noqa: RUF012",
            "# noqa: ANN001",
            "# ignore-this-1",
            "# it's 7",
            "# a method comment",
            "# noqa: ANN002",
            "# ignore-this-2",
            "# it's 8",
            "# you got to the bottom?",
        ]
