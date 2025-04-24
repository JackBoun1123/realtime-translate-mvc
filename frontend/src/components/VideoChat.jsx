// frontend/src/components/VideoChat.jsx
import React, { useRef, useEffect, useState } from 'react';
import useSocket from '../hooks/useSocket';

export default function VideoChat() {
  const localVideo = useRef(null);
  const [translation, setTranslation] = useState('');
  const socket = useSocket();

  useEffect(() => {
    if (!socket) return;

    // Debug: khi kết nối thành công
    socket.on('connect', () => {
      console.log('Socket.IO connected, id=', socket.id);
    });
    socket.on('connect_error', (err) => {
      console.error('Socket.IO connect_error', err);
    });

    // Nhận bản dịch từ server
    socket.on('translation', (data) => {
      console.log('Received translation:', data.text);
      setTranslation(data.text);
    });

    // Lấy media và khởi audio processing
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then((stream) => {
        localVideo.current.srcObject = stream;

        // Tạo AudioContext với sampleRate 16000
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContextClass({ sampleRate: 16000 });
        const source = audioContext.createMediaStreamSource(stream);

        // Deprecated nhưng đơn giản: ScriptProcessorNode
        // @ts-ignore: using deprecated API
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioContext.destination);

        // Mỗi khi có buffer mới, convert Float32 → Int16 và emit
        // @ts-ignore: deprecated onaudioprocess
        processor.onaudioprocess = (e) => {
          // @ts-ignore: deprecated inputBuffer
          const input = e.inputBuffer.getChannelData(0);
          const pcm = new Int16Array(input.length);
          for (let i = 0; i < input.length; i++) {
            let s = Math.max(-1, Math.min(1, input[i]));
            pcm[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          console.log('Sending audio chunk, bytes:', pcm.buffer.byteLength);
          socket.emit('audio_chunk', pcm.buffer);
        };
      })
      .catch((err) => {
        console.error('getUserMedia error:', err);
      });

    // Cleanup khi component unmount
    return () => {
      socket.off('connect');
      socket.off('connect_error');
      socket.off('translation');
    };
  }, [socket]);

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-2">Real-time Translate</h2>
      <video
        ref={localVideo}
        autoPlay
        muted
        className="w-80 h-60 rounded-md shadow-md mb-4"
      />
      <p className="text-base">
        <strong>Translation:</strong> {translation}
      </p>
    </div>
  );
}
