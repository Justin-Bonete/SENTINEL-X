"""Settings read from environment variables (see .env.example)."""
import os


class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///sentinel.db")
    redis_url = os.getenv("REDIS_URL", "")
    rp_id = os.getenv("WEBAUTHN_RP_ID", "localhost")
    rp_name = os.getenv("WEBAUTHN_RP_NAME", "SENTINEL X")
    origin = os.getenv("WEBAUTHN_ORIGIN", "http://localhost:5173")
    session_ttl_min = int(os.getenv("SESSION_TTL_MINUTES", "60"))
    step_up_max_age_s = int(os.getenv("STEP_UP_MAX_AGE_SECONDS", "300"))


settings = Settings()
