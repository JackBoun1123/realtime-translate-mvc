# backend/controllers/signaling_controller.py
from services.asr_service import recognize
from services.translate_service import translate

def register_handlers(sio):
    @sio.event
    async def connect(sid, environ):
        print(f"Client {sid} connected")

    @sio.event
    async def audio_chunk(sid, data):
        print(f"Received audio chunk from {sid}, size: {len(data)} bytes")
        text = await recognize(data)
        print(f"Recognition result: '{text}'")
        
        if not text:
            return  # Bỏ qua partial hoặc lỗi

        translation = await translate(text, 'vi')
        print(f"Translation result: '{translation}'")
        await sio.emit('translation', {'text': translation}, room=sid)

    @sio.event
    async def disconnect(sid):
        print(f"Client {sid} disconnected")