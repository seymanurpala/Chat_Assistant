from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HISTORY_FILE = PROJECT_ROOT / "chat_history.json"

DEFAULT_TITLE = "Yeni sohbet"
GENERIC_CHAT_ERROR = "Şu an cevap alınamadı. Lütfen biraz sonra tekrar dene."
MAX_MESSAGE_LENGTH = 4000
MAX_MODEL_MESSAGES = 20

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.3
REQUEST_TIMEOUT_SECONDS = 45.0

SYSTEM_PROMPT = (
    "Sen yardımcı bir asistansın\n"
    "Her zaman doğal ve anlaşılır Türkçe cevap ver.\n"
    "Cevaplarını kısa, net ve doğrudan yaz.\n"
    "Emin olmadığın konularda kesin konuşma; gerekirse kısa bir soru sor.\n"
    "Kullanıcının istediği işi pratik şekilde çözmeye odaklan."
)
