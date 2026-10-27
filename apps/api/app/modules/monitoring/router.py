"""Registered systems and health checks (move from app/main.py) (Phase 1)."""
from fastapi import APIRouter

router = APIRouter(tags=["monitoring"])
