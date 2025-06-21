"""Pytest configuration for Atlas.

This plugin provides legacy support for test cases that *return* a boolean
value instead of using bare ``assert`` statements.  In upstream pytest such
return values are treated as failures.  Older Atlas tests relied on a legacy
wrapper that interpreted a returned ``True`` as success and ``False`` as
failure.  The wrapper was inadvertently removed during recent refactors,
resulting in widespread test breakages ("Expected None, but test returned …").

The hook below reinstates that behaviour while remaining fully compatible
with normal pytest semantics:

* If a test function returns ``None`` (the common case) we leave execution to
  pytest's default handling.
* If a test returns any other value we interpret it as a pass/fail signal:
    - Truthy value  -> test passes.
    - Falsy value   -> test fails via an assertion.

This minimises churn by avoiding edits to dozens of legacy test files while
ensuring future tests continue to use standard ``assert`` statements.
"""

from __future__ import annotations

import inspect
from typing import Any

import pytest


def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:  # noqa: D401
    """Custom test runner that interprets a boolean return value.

    The hook short-circuits pytest's default function execution.  We execute
    the test function ourselves; if it returns *None* we hand control back to
    pytest to perform normal result handling.  For any non-``None`` return we
    treat the value as a success flag (truthy = pass).
    """

    testfunc = pyfuncitem.obj

    # Let pytest handle async tests / generators / parametrisation normally.
    if inspect.iscoroutinefunction(testfunc) or inspect.isgeneratorfunction(testfunc):
        return None  # fall through to the default implementation

    # Collect required fixture values for the test function.
    fixture_names = pyfuncitem._fixtureinfo.argnames  # type: ignore[attr-defined]
    kwargs = {name: pyfuncitem._request.getfixturevalue(name) for name in fixture_names}  # type: ignore[attr-defined]

    # Execute the test function.
    result: Any = pyfuncitem.obj(**kwargs)

    # Evaluate legacy return-value convention
    if result is None:
        # Test did not use the legacy convention → treat as normal success.
        return True

    # Non-None return: truthy == pass, falsy == fail.
    assert bool(result), (
        "Test signalled failure via return value: "
        f"{result!r}.  Update the test to use 'assert' for clarity."
    )
    return True
