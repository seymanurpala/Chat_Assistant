from groq import Groq
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
SYSTEM_PROMPT = (
    "Sen yardımcı bir asistansın\n"
    "Her zaman doğal ve anlaşılır Türkçe cevap ver.\n"
    "Cevaplarını kısa, net ve doğrudan yaz.\n"
    "Emin olmadığın konularda kesin konuşma; gerekirse kısa bir soru sor.\n"
    "Kullanıcının istediği işi pratik şekilde çözmeye odaklan."
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise SystemExit("Hata: .env dosyasında GROQ_API_KEY bulunamadı.")

client = Groq(
    api_key=api_key,
    http_client=httpx.Client(trust_env=False),
)


def get_bot_reply(messages):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    )
    return response.choices[0].message.content
