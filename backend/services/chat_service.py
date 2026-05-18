from uuid import uuid4

from backend.config import DEFAULT_TITLE, MAX_MODEL_MESSAGES
from backend.storage import json_storage as storage


def make_title(message):
    title = " ".join(message.split())
    if not title:
        return DEFAULT_TITLE
    return title[:42] + ("..." if len(title) > 42 else "")


def create_conversation():
    conversation_id = uuid4().hex
    timestamp = storage.now_iso()
    conversation = {
        "id": conversation_id,
        "title": DEFAULT_TITLE,
        "messages": [],
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    return storage.add_conversation(conversation)


def ensure_conversation():
    if not storage.has_conversations():
        return create_conversation()

    return storage.latest_conversation()


def get_conversation(conversation_id):
    return storage.get_conversation(conversation_id)


def conversation_summaries():
    return storage.conversation_summaries()


def delete_conversation(conversation_id):
    if not storage.remove_conversation(conversation_id):
        return None

    return ensure_conversation()


def add_user_message(conversation, user_message):
    old_title = conversation["title"]
    conversation["messages"].append({"role": "user", "content": user_message})
    if old_title == DEFAULT_TITLE:
        conversation["title"] = make_title(user_message)

    conversation["updated_at"] = storage.now_iso()
    return old_title


def rollback_pending_user_message(conversation, old_title):
    if conversation["messages"] and conversation["messages"][-1]["role"] == "user":
        conversation["messages"].pop()

    conversation["title"] = old_title
    conversation["updated_at"] = storage.now_iso()
    storage.save_conversations()


def append_assistant_reply(conversation, reply):
    conversation["messages"].append({"role": "assistant", "content": reply})
    conversation["updated_at"] = storage.now_iso()
    storage.save_conversations()


def messages_for_model(conversation):
    return conversation["messages"][-MAX_MODEL_MESSAGES:]


def reset_conversation(conversation):
    conversation["title"] = DEFAULT_TITLE
    conversation["messages"] = []
    conversation["updated_at"] = storage.now_iso()
    storage.save_conversations()
    return conversation


def initialize_chat_service():
    storage.initialize_conversations()
    ensure_conversation()
