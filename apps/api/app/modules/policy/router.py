"""Policy engine: deny by default, step-up freshness (Phase 3)."""
from fastapi import APIRouter

router = APIRouter(tags=["policy"])
