import logging

from backend.config import GENERIC_CHAT_ERROR, MAX_MESSAGE_LENGTH
from backend.services.chat_service import (
    add_user_message,
    append_assistant_reply,
    conversation_summaries,
    create_conversation,
    delete_conversation as delete_conversation_by_id,
    ensure_conversation,
    get_conversation,
    initialize_chat_service,
    messages_for_model,
    reset_conversation,
    rollback_pending_user_message,
)
from backend.services.chatbot import ChatbotConfigurationError, get_bot_reply
from flask import Blueprint, jsonify, render_template, request
from groq import AuthenticationError

bp = Blueprint("routes", __name__)
logger = logging.getLogger(__name__)

initialize_chat_service()


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
    active_conversation = delete_conversation_by_id(conversation_id)
    if not active_conversation:
        return jsonify({"error": "Sohbet bulunamadı."}), 404

    return jsonify(
        {
            "active_id": active_conversation["id"],
            "deleted_id": conversation_id,
            "conversations": conversation_summaries(),
        }
    )


@bp.post("/api/chat")
@bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    conversation_id = data.get("conversation_id")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Lütfen bir mesaj yaz."}), 400

    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": "Mesaj çok uzun. Lütfen daha kısa yaz."}), 400

    conversation = get_conversation(conversation_id)
    if not conversation:
        conversation = create_conversation()

    old_title = add_user_message(conversation, user_message)

    try:
        reply = get_bot_reply(messages_for_model(conversation))
    except ChatbotConfigurationError as error:
        logger.exception("Chatbot configuration is missing.")
        rollback_pending_user_message(conversation, old_title)
        return jsonify({"error": str(error)}), 500
    except AuthenticationError:
        logger.exception("Groq API key was rejected.")
        rollback_pending_user_message(conversation, old_title)
        return jsonify({"error": "Groq API anahtarı geçersiz. .env dosyasındaki GROQ_API_KEY değerini yenile."}), 401
    except Exception:
        logger.exception("Chat completion request failed.")
        rollback_pending_user_message(conversation, old_title)
        return jsonify({"error": GENERIC_CHAT_ERROR}), 502

    append_assistant_reply(conversation, reply)

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

    reset_conversation(conversation)

    return jsonify(
        {
            "conversation": conversation,
            "conversations": conversation_summaries(),
        }
    )
