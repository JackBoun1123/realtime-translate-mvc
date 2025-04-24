import { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

// Luôn kết nối về máy host tại cổng 8000 (nơi backend đang lắng nghe)
const SOCKET_URL = 'http://localhost:8000';

export default function useSocket() {
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const s = io(SOCKET_URL, { transports: ['websocket', 'polling'] });
    setSocket(s);
    return () => {
      s.disconnect();
    };
  }, []);

  return socket;
}