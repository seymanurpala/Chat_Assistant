from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
import json
import logging

from backend.config import DEFAULT_TITLE, HISTORY_FILE

logger = logging.getLogger(__name__)

VALID_MESSAGE_ROLES = {"user", "assistant"}
history_lock = RLock()
conversations = {}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def normalize_messages(messages):
    normalized = []
    for message in messages:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")
        if role in VALID_MESSAGE_ROLES and isinstance(content, str):
            normalized.append({"role": role, "content": content})

    return normalized


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
            "messages": normalize_messages(item.get("messages") or []),
            "created_at": item.get("created_at") or now_iso(),
            "updated_at": item.get("updated_at") or now_iso(),
        }

    return loaded


def save_conversations():
    temp_path = HISTORY_FILE.with_name(f".{HISTORY_FILE.name}.{uuid4().hex}.tmp")

    with history_lock:
        data = {
            "conversations": sorted(
                conversations.values(),
                key=lambda conversation: conversation["updated_at"],
                reverse=True,
            )
        }
        payload = json.dumps(data, ensure_ascii=False, indent=2)

        try:
            temp_path.write_text(payload, encoding="utf-8")
            temp_path.replace(HISTORY_FILE)
        except OSError:
            HISTORY_FILE.write_text(payload, encoding="utf-8")
        finally:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                logger.warning("Temporary history file could not be removed: %s", temp_path)


def initialize_conversations():
    with history_lock:
        conversations.clear()
        conversations.update(load_conversations())


def conversation_summaries():
    with history_lock:
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


def has_conversations():
    with history_lock:
        return bool(conversations)


def latest_conversation():
    with history_lock:
        if not conversations:
            return None

        return sorted(
            conversations.values(),
            key=lambda conversation: conversation["updated_at"],
            reverse=True,
        )[0]


def get_conversation(conversation_id):
    with history_lock:
        return conversations.get(conversation_id)


def add_conversation(conversation):
    with history_lock:
        conversations[conversation["id"]] = conversation
        save_conversations()

    return conversation


def remove_conversation(conversation_id):
    with history_lock:
        if conversation_id not in conversations:
            return False

        del conversations[conversation_id]
        save_conversations()
        return True
