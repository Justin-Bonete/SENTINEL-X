"""Stable machine-readable error codes (blueprint section 7)."""
from enum import Enum


class ErrorCode(str, Enum):
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_CHALLENGE_EXPIRED = "AUTH_CHALLENGE_EXPIRED"
    AUTHENTICATOR_INVALID = "AUTHENTICATOR_INVALID"
    SESSION_REVOKED = "SESSION_REVOKED"
    POLICY_DENY = "POLICY_DENY"
    STEP_UP_REQUIRED = "STEP_UP_REQUIRED"
