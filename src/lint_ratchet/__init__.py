"""
Provides a mechanism for incrementally improving code quality in a codebase.

Ratchet counts the number of lint violation comments (such as NOQA) in a codebase
and enforces that number does not increase over time.

Ratchet is useful where you begin with a large number of violations that you want
to gradually reduce over time.

The mapping of lint codes to violation counts are stored in the pyproject.toml
file.

Usage:

    ratchet add noqa F401   # Add a new lint code to the ratchet file
    ratchet crank           # Periodically recompute the violation counts, writing the results back if lower
    ratchet check           # Check for new violations and enforce the ratchet

"""
