# backend/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from socketio import AsyncServer, ASGIApp
from controllers.signaling_controller import register_handlers

# 1) Tạo FastAPI
fastapi_app = FastAPI()

# 2) CORS cho HTTP API (nếu có)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Tạo Socket.IO server
sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000"],  # match React
)

# 4) Đăng ký handlers lên đúng instance `sio`
register_handlers(sio)

# 5) Bọc FastAPI + Socket.IO vào 1 ASGIApp
#    -> LƯU Ý: phải truyền positional, không dùng keyword `other_asgi_app`
sio_app = ASGIApp(sio, fastapi_app)

if __name__ == "__main__":
    import uvicorn
    # Chạy đúng biến `sio_app` chứa ASGIApp
    uvicorn.run("backend.app:sio_app", host="0.0.0.0", port=8000, reload=True)
