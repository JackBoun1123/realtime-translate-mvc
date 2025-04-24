from services.asr_service import recognize
from services.translate_service import translate

def register_handlers(sio):
    @sio.event
    async def connect(sid, environ):
        print(f"Client {sid} connected")

    @sio.event
    async def audio_chunk(sid, data):
        text = await recognize(data)
        if not text:
            return  # Bỏ qua partial hoặc lỗi

        translation = await translate(text, 'vi')
        await sio.emit('translation', {'text': translation}, room=sid)

    @sio.event
    async def disconnect(sid):
        print(f"Client {sid} disconnected")
