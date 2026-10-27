"""Hash-chained security events and chain verification (move from app/main.py) (Phase 1)."""
from fastapi import APIRouter

router = APIRouter(tags=["audit"])
