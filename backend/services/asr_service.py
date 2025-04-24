import os
import asyncio
import json
import wave
import io
from vosk import Model, KaldiRecognizer
from concurrent.futures import ThreadPoolExecutor

# Xác định đường dẫn đến thư mục model tương đối từ backend/
dir_base = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(dir_base, "models", "vosk-small-en-us")

if not os.path.isdir(model_path):
    raise FileNotFoundError(f"Vosk model folder not found: {model_path}")

model = Model(model_path)
executor = ThreadPoolExecutor()

def recognize_sync(audio_bytes: bytes) -> str:
    # Bỏ qua chunk nhỏ quá
    if len(audio_bytes) < 4000:
        print("Audio chunk too small, skipping")
        return ""

    try:
        # Convert raw PCM to WAV format for better compatibility
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)
        
        wav_data = wav_buffer.getvalue()
        
        # Create a new recognizer for each request to prevent concurrency issues
        recognizer = KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)
        
        # Process the WAV data
        if recognizer.AcceptWaveform(wav_data):
            result = json.loads(recognizer.Result())
            print(f"Full recognition result: {result}")
            return result.get("text", "")
        else:
            partial = json.loads(recognizer.PartialResult())
            print(f"Partial recognition result: {partial}")
            return ""
    except Exception as e:
        print(f"Vosk error: {str(e)}")
        return ""

async def recognize(audio_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, recognize_sync, audio_bytes)