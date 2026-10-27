import pytest


@pytest.mark.skip(reason="Phase 3")
def test_t05():
    """T-05: No session returns 401, no content disclosed"""


@pytest.mark.skip(reason="Phase 3")
def test_t06():
    """T-06: Employee on admin endpoint returns 403 and is logged"""


@pytest.mark.skip(reason="Phase 3")
def test_t07():
    """T-07: Guessing another resource ID is denied"""


@pytest.mark.skip(reason="Phase 3")
def test_t13():
    """T-13: Stale authentication on a sensitive action requires step-up"""
