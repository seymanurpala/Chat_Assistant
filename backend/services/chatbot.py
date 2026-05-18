from dotenv import load_dotenv
from functools import lru_cache
from groq import Groq
import httpx
import os

from backend.config import GROQ_MODEL, GROQ_TEMPERATURE, REQUEST_TIMEOUT_SECONDS, SYSTEM_PROMPT

load_dotenv()


class ChatbotConfigurationError(RuntimeError):
    pass


def get_api_key():
    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key:
        raise ChatbotConfigurationError("GROQ_API_KEY bulunamadı.")

    if not api_key.startswith("gsk_"):
        raise ChatbotConfigurationError("GROQ_API_KEY geçerli bir Groq anahtarı gibi görünmüyor.")

    if any(char.isspace() or ord(char) > 127 for char in api_key):
        raise ChatbotConfigurationError(
            "GROQ_API_KEY içinde boşluk veya Türkçe karakter var. .env dosyasında sadece anahtar olmalı."
        )

    return api_key


@lru_cache(maxsize=1)
def get_client():
    return Groq(
        api_key=get_api_key(),
        http_client=httpx.Client(
            trust_env=False,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ),
    )


def get_bot_reply(messages):
    response = get_client().chat.completions.create(
        model=GROQ_MODEL,
        temperature=GROQ_TEMPERATURE,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    )
    return response.choices[0].message.content
