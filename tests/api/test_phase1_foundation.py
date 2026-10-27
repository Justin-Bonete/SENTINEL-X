import pytest


@pytest.mark.skip(reason="Phase 1")
def test_health():
    """GET /health returns ok"""


@pytest.mark.skip(reason="Phase 1")
def test_register_system():
    """Registering a system returns 201 and it appears in the list"""


@pytest.mark.skip(reason="Phase 1")
def test_private_target_blocked():
    """A private or loopback URL is rejected (SSRF guard)"""
