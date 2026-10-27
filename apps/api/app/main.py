"""SENTINEL X API (prototype): registered-systems monitor + hash-chained audit log."""
import asyncio, hashlib, hmac, ipaddress, json, os, secrets, sqlite3, time, uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

TOKEN = os.getenv("SENTINEL_ADMIN_TOKEN") or secrets.token_urlsafe(24)
ALLOW_PRIVATE = os.getenv("SENTINEL_ALLOW_PRIVATE") == "1"  # lets you monitor your own LAN/localhost
SLOW_MS = 1500
GENESIS = "0" * 64
WEB = Path(__file__).resolve().parents[2] / "web" / "prototype" / "index.html"

# All handlers are async, so this single connection is only touched from the event-loop thread.
con = sqlite3.connect(os.getenv("SENTINEL_DB", "sentinel.db"), check_same_thread=False)
con.row_factory = sqlite3.Row
con.execute("PRAGMA foreign_keys=ON")
con.executescript("""
CREATE TABLE IF NOT EXISTS systems(id TEXT PRIMARY KEY, name TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL, interval_s INTEGER NOT NULL, expect_status INTEGER, created_at TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'pending', last_check REAL NOT NULL DEFAULT 0,
  latency_ms INTEGER, http_status INTEGER, error TEXT);
CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY AUTOINCREMENT,
  system_id TEXT NOT NULL REFERENCES systems(id) ON DELETE CASCADE,
  at TEXT NOT NULL, ok INTEGER NOT NULL, status INTEGER, latency_ms INTEGER, error TEXT);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL,
  event_type TEXT NOT NULL, system_id TEXT, outcome TEXT NOT NULL, reason_code TEXT, risk INTEGER NOT NULL DEFAULT 0,
  correlation_id TEXT NOT NULL, detail TEXT, prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL);
""")  # events.system_id has no FK on purpose: audit history must survive system removal

now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
FIELDS = ("occurred_at", "event_type", "system_id", "outcome", "reason_code", "risk", "correlation_id", "detail")
digest = lambda prev, body: hashlib.sha256((prev + json.dumps(body, sort_keys=True)).encode()).hexdigest()


def emit(event_type, outcome, system_id=None, reason=None, risk=0, detail=None):
    last = con.execute("SELECT event_hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    prev = last[0] if last else GENESIS
    body = dict(occurred_at=now(), event_type=event_type, system_id=system_id, outcome=outcome,
                reason_code=reason, risk=risk, correlation_id=uuid.uuid4().hex[:12], detail=detail)
    con.execute("INSERT INTO events(occurred_at,event_type,system_id,outcome,reason_code,risk,correlation_id,"
                "detail,prev_hash,event_hash) VALUES(:occurred_at,:event_type,:system_id,:outcome,:reason_code,"
                ":risk,:correlation_id,:detail,:prev,:h)", {**body, "prev": prev, "h": digest(prev, body)})
    con.commit()


async def guard(url: str):
    """SSRF defence: only http(s), and no private/loopback targets unless explicitly allowed."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ValueError("Only http:// or https:// URLs are allowed")
    if ALLOW_PRIVATE:
        return
    for info in await asyncio.get_running_loop().getaddrinfo(u.hostname, u.port or 80):
        if not ipaddress.ip_address(info[4][0]).is_global:
            raise ValueError("Private or loopback targets are blocked. Set SENTINEL_ALLOW_PRIVATE=1 to monitor your own network")


EVENTS = {"down": ("SYSTEM_DOWN", "alert", "SYSTEM_UNREACHABLE", 40),
          "degraded": ("SYSTEM_DEGRADED", "alert", "HIGH_LATENCY", 20),
          "up": ("SYSTEM_RECOVERED", "success", "HEALTHY", 0)}


async def check(s: dict):
    con.execute("UPDATE systems SET last_check=? WHERE id=?", (time.time(), s["id"]))
    status = err = None
    t = time.perf_counter()
    try:
        await guard(s["url"])  # re-checked every time: DNS can change
        async with httpx.AsyncClient(timeout=8) as c:  # redirects are not followed (SSRF hardening)
            status = (await c.get(s["url"], headers={"User-Agent": "SentinelX-Monitor/1.0"})).status_code
    except Exception as e:
        err = (str(e) or type(e).__name__)[:120]
    ms = int((time.perf_counter() - t) * 1000)
    ok = status is not None and (status == s["expect_status"] if s["expect_status"] else status < 400)
    state = "down" if not ok else "degraded" if ms > SLOW_MS else "up"
    err = err or (None if ok else f"HTTP {status}")
    con.execute("INSERT INTO checks(system_id,at,ok,status,latency_ms,error) VALUES(?,?,?,?,?,?)",
                (s["id"], now(), int(ok), status, ms, err))
    con.execute("UPDATE systems SET state=?,latency_ms=?,http_status=?,error=? WHERE id=?",
                (state, ms, status, err, s["id"]))
    con.commit()
    if state != s["state"] and not (state == "up" and s["state"] == "pending"):
        etype, outcome, reason, risk = EVENTS[state]
        emit(etype, outcome, s["id"], reason, risk, f"{s['name']}: {err or f'{ms} ms'}")


async def monitor():
    while True:
        try:
            due = con.execute("SELECT * FROM systems WHERE ? - last_check >= interval_s", (time.time(),)).fetchall()
            await asyncio.gather(*(check(dict(s)) for s in due), return_exceptions=True)
        except Exception as e:
            print("monitor error:", e)
        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(_):
    if not os.getenv("SENTINEL_ADMIN_TOKEN"):
        print(f"\n  SENTINEL X admin token (dev only): {TOKEN}\n")
    task = asyncio.create_task(monitor())
    yield
    task.cancel()


app = FastAPI(title="SENTINEL X", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def security_headers(request, call_next):
    r = await call_next(request)
    r.headers.update({"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer"})
    return r


async def auth(x_admin_token: str = Header(default="")):
    """Stand-in for passkey sessions (Phase 2). Deny by default."""
    if not hmac.compare_digest(x_admin_token.encode(), TOKEN.encode()):
        raise HTTPException(401, "AUTH_REQUIRED")


class NewSystem(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    url: str = Field(max_length=500)
    kind: str = Field(default="website", pattern="^(website|api|system)$")
    interval_s: int = Field(default=60, ge=10, le=3600)
    expect_status: int | None = Field(default=None, ge=100, le=599)


def view(s):
    d = dict(s)
    d["history"] = [[c[0], c[1]] for c in con.execute(
        "SELECT latency_ms, ok FROM checks WHERE system_id=? ORDER BY id DESC LIMIT 40", (s["id"],))][::-1]
    u = con.execute("SELECT AVG(ok)*100 FROM (SELECT ok FROM checks WHERE system_id=? ORDER BY id DESC LIMIT 200)",
                    (s["id"],)).fetchone()[0]
    d["uptime"] = None if u is None else round(u, 2)
    return d


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(WEB)


@app.get("/api/v1/systems")
async def list_systems(_=Depends(auth)):
    return [view(s) for s in con.execute("SELECT * FROM systems ORDER BY created_at")]


@app.post("/api/v1/systems", status_code=201)
async def register(b: NewSystem, _=Depends(auth)):
    url = b.url.strip()
    try:
        await guard(url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except OSError:
        raise HTTPException(400, "That host could not be resolved")
    sid = uuid.uuid4().hex[:10]
    try:
        con.execute("INSERT INTO systems(id,name,url,kind,interval_s,expect_status,created_at) VALUES(?,?,?,?,?,?,?)",
                    (sid, b.name.strip(), url, b.kind, b.interval_s, b.expect_status, now()))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "That URL is already registered")
    con.commit()
    emit("SYSTEM_REGISTERED", "success", sid, detail=f"{b.name.strip()} ({b.kind})")
    return {"id": sid}  # the monitor loop runs the first check within seconds


def find(sid):
    s = con.execute("SELECT * FROM systems WHERE id=?", (sid,)).fetchone()
    if not s:
        raise HTTPException(404, "NOT_FOUND")
    return s


@app.post("/api/v1/systems/{sid}/check")
async def check_now(sid: str, _=Depends(auth)):
    await check(dict(find(sid)))
    return {"ok": True}


@app.delete("/api/v1/systems/{sid}", status_code=204)
async def remove(sid: str, _=Depends(auth)):
    s = find(sid)
    con.execute("DELETE FROM systems WHERE id=?", (sid,))
    con.commit()
    emit("SYSTEM_REMOVED", "success", sid, detail=s["name"])


@app.get("/api/v1/events")
async def events(limit: int = Query(60, ge=1, le=200), _=Depends(auth)):
    return [dict(r) for r in con.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))]


@app.get("/api/v1/events/verify")
async def verify(_=Depends(auth)):
    prev = GENESIS
    for r in con.execute("SELECT * FROM events ORDER BY id"):
        if r["prev_hash"] != prev or digest(prev, {k: r[k] for k in FIELDS}) != r["event_hash"]:
            return {"valid": False, "broken_at": r["id"]}
        prev = r["event_hash"]
    return {"valid": True}
