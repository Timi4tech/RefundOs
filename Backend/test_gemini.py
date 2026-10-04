import traceback
from google import genai
from app.core.config import settings as s

print("model:", s.GEMINI_MODEL)
print("key set:", bool(s.GEMINI_API_KEY), "| starts with AIza:", (s.GEMINI_API_KEY or "").startswith("AIza"))

try:
    client = genai.Client(api_key=s.GEMINI_API_KEY)
    resp = client.models.generate_content(model=s.GEMINI_MODEL, contents="Say hi in 3 words")
    print("RESPONSE:", repr(resp.text))
    print("finish_reason:", resp.candidates[0].finish_reason if resp.candidates else None)
except Exception:
    traceback.print_exc()