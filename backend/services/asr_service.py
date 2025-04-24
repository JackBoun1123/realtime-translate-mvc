import os
import asyncio
import json
from vosk import Model, KaldiRecognizer
from concurrent.futures import ThreadPoolExecutor

# Xác định đường dẫn đến thư mục model tương đối từ backend/
dir_base = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(dir_base, "models", "vosk-small-en-us")

if not os.path.isdir(model_path):
    raise FileNotFoundError(f"Vosk model folder not found: {model_path}")

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
executor = ThreadPoolExecutor()

def recognize_sync(audio_bytes: bytes) -> str:
    # Bỏ qua chunk nhỏ quá (8192 bytes = 4096 samples với 16-bit PCM)
    if len(audio_bytes) < 4000:
        return ""

    try:
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result()).get("text", "")
            recognizer.Reset()
            return result
        else:
            return ""
    except Exception as e:
        print("Vosk error, resetting recognizer:", e)
        recognizer.Reset()
        return ""

async def recognize(audio_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, recognize_sync, audio_bytes)
