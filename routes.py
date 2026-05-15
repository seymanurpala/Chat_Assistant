from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json

from chatbot import get_bot_reply
from flask import Blueprint, jsonify, render_template, request

bp = Blueprint("routes", __name__)

HISTORY_FILE = Path(__file__).with_name("chat_history.json")
DEFAULT_TITLE = "Yeni sohbet"
conversations = {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def make_title(message):
    title = " ".join(message.split())
    if not title:
        return DEFAULT_TITLE
    return title[:42] + ("..." if len(title) > 42 else "")


def conversation_summaries():
    items = sorted(
        conversations.values(),
        key=lambda conversation: conversation["updated_at"],
        reverse=True,
    )
    return [
        {
            "id": item["id"],
            "title": item["title"],
            "updated_at": item["updated_at"],
        }
        for item in items
    ]


def load_conversations():
    if not HISTORY_FILE.exists():
        return {}

    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    loaded = {}
    for item in data.get("conversations", []):
        conversation_id = item.get("id")
        if not conversation_id:
            continue

        loaded[conversation_id] = {
            "id": conversation_id,
            "title": item.get("title") or DEFAULT_TITLE,
            "messages": item.get("messages") or [],
            "created_at": item.get("created_at") or now_iso(),
            "updated_at": item.get("updated_at") or now_iso(),
        }

    return loaded


def save_conversations():
    # Tüm sohbetleri mesajlarıyla birlikte kaydet
    data = {
        "conversations": sorted(
            conversations.values(),
            key=lambda c: c["updated_at"],
            reverse=True,
        )
    }
    HISTORY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_conversation():
    conversation_id = uuid4().hex
    timestamp = now_iso()
    conversation = {
        "id": conversation_id,
        "title": DEFAULT_TITLE,
        "messages": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    conversations[conversation_id] = conversation
    save_conversations()
    return conversation


def get_conversation(conversation_id):
    if conversation_id in conversations:
        return conversations[conversation_id]
    return None


def ensure_conversation():
    if not conversations:
        return create_conversation()
    return sorted(
        conversations.values(),
        key=lambda c: c["updated_at"],
        reverse=True,
    )[0]


conversations.update(load_conversations())
ensure_conversation()


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/conversations")
def list_conversations():
    ensure_conversation()
    return jsonify({"conversations": conversation_summaries()})


@bp.post("/api/conversations")
def new_conversation():
    conversation = create_conversation()
    return jsonify(
        {
            "conversation": conversation,
            "conversations": conversation_summaries(),
        }
    )


@bp.get("/api/conversations/<conversation_id>")
def show_conversation(conversation_id):
    conversation = get_conversation(conversation_id)
    if not conversation:
        return jsonify({"error": "Sohbet bulunamadı."}), 404

    return jsonify({"conversation": conversation})


@bp.delete("/api/conversations/<conversation_id>")
def delete_conversation(conversation_id):
    if conversation_id not in conversations:
        return jsonify({"error": "Sohbet bulunamadı."}), 404

    del conversations[conversation_id]
    if not conversations:
        active_conversation = create_conversation()
    else:
        save_conversations()
        active_conversation = ensure_conversation()

    return jsonify(
        {
            "active_id": active_conversation["id"],
            "conversations": conversation_summaries(),
        }
    )


@bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    conversation_id = data.get("conversation_id")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Lütfen bir mesaj yaz."}), 400

    conversation = get_conversation(conversation_id)
    if not conversation:
        conversation = create_conversation()

    old_title = conversation["title"]
    conversation["messages"].append({"role": "user", "content": user_message})
    if old_title == DEFAULT_TITLE:
        conversation["title"] = make_title(user_message)
    conversation["updated_at"] = now_iso()

    try:
        reply = get_bot_reply(conversation["messages"])
    except Exception as error:
        conversation["messages"].pop()
        conversation["title"] = old_title
        conversation["updated_at"] = now_iso()
        save_conversations()
        return jsonify({"error": f"API hatası: {error}"}), 500

    conversation["messages"].append({"role": "assistant", "content": reply})
    conversation["updated_at"] = now_iso()
    save_conversations()

    return jsonify(
        {
            "conversation_id": conversation["id"],
            "reply": reply,
            "title": conversation["title"],
            "conversations": conversation_summaries(),
        }
    )


@bp.post("/reset")
def reset():
    data = request.get_json(silent=True) or {}
    conversation = get_conversation(data.get("conversation_id"))
    if not conversation:
        conversation = create_conversation()

    conversation["title"] = DEFAULT_TITLE
    conversation["messages"] = []
    conversation["updated_at"] = now_iso()
    save_conversations()

    return jsonify(
        {
            "conversation": conversation,
            "conversations": conversation_summaries(),
        }
    )