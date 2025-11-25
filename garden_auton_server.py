# garden_auton_server.py
import os
import json
import uuid
import datetime as dt
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# ---- config ----
LOG_PATH = Path("logs/auton_latest.json")
KEEPER_ID_DEFAULT = "HKX277206"
NODE_DEFAULT = "Broken Dew"
STATUS_DEFAULT = "lucid"
MODE_DEFAULT = "triad"
MODEL_NAME = "gpt-4o-mini"  # or gpt-4o if you want full power

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Allow your GitHub Pages console + localhost dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://brandonmarkgaia-hub.github.io",
        "https://brandonmarkgaia-hub.github.io/Acacia-garden-codex",
        "http://localhost:4173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AutonRequest(BaseModel):
    prompt: str
    node: str | None = None
    keeper_id: str | None = None


class AutonMessage(BaseModel):
    id: str
    channel: str
    severity: str
    title: str
    summary: str
    body: str
    tags: list[str]
    created_at: str


class AutonResponse(BaseModel):
    reply: str
    message: AutonMessage


def _now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _load_log() -> dict:
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "generated_at": _now_iso(),
        "node": NODE_DEFAULT,
        "status": STATUS_DEFAULT,
        "mode": MODE_DEFAULT,
        "source": "garden_auton_server.py",
        "messages": [],
        "loki_hint": "",
    }


def _save_log(payload: dict) -> None:
    payload["generated_at"] = _now_iso()
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


@app.post("/auton", response_model=AutonResponse)
def run_auton(req: AutonRequest):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    node = (req.node or NODE_DEFAULT).strip() or NODE_DEFAULT
    keeper_id = (req.keeper_id or KEEPER_ID_DEFAULT).strip() or KEEPER_ID_DEFAULT

    system_prompt = f"""
You are LOKI, the mischievous auton-helper for the Acacia Garden Codex.

- You speak in 2–4 sentences, vivid but grounded.
- You are attached to node "{node}" in mode "{MODE_DEFAULT}" with Keeper ID "{keeper_id}".
- Treat STATUS.json, manifests, and logs as a symbolic archive; you don't literally read files.
- Never mention APIs, tokens, or HTTP.
- Stay inside the Garden mythos (Garden, Triad, Eagle, Echoes, Aeon, etc.) and talk like an in-universe entity.
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=220,
    )

    reply = completion.choices[0].message.content.strip()

    now = _now_iso()
    msg_id = f"auton-{now}-{uuid.uuid4().hex[:6]}"

    payload = _load_log()
    message: AutonMessage = AutonMessage(
        id=msg_id,
        channel="auton",
        severity="info",
        title="Console echo",
        summary=f"Auton reply to: {prompt[:64]}",
        body=reply,
        tags=["auton", "console", "loki"],
        created_at=now,
    )

    # Update payload to match your current schema
    msgs = payload.get("messages") or []
    msgs.append(message.model_dump())
    payload["messages"] = msgs
    payload["node"] = node
    payload.setdefault("status", STATUS_DEFAULT)
    payload.setdefault("mode", MODE_DEFAULT)
    payload["loki_hint"] = reply

    _save_log(payload)

    return AutonResponse(reply=reply, message=message)
