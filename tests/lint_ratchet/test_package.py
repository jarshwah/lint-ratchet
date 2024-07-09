import lint_ratchet as package  # fmt: skip


def test_has_docstring():
    assert package.__doc__ is not None
