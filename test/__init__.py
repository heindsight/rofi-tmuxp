import re

import pytest


def match_logs(logger, level, pattern, record_tuples):
    """Assert that the given patten is matched in the logs.

    This assertion helper looks for a log message from the given `logger` at the given
    `level`, matching `pattern`.
    """
    __tracebackhide__ = True
    matches = any(
        lggr == logger and lvl == level and re.match(pattern, msg)
        for lggr, lvl, msg in record_tuples
    )

    if not matches:  # pragma: no cover
        pytest.fail(
            "{!r} not matched in {!r}".format((logger, level, pattern), record_tuples)
        )
