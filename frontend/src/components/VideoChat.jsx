// frontend/src/components/VideoChat.jsx
import React, { useRef, useEffect, useState } from 'react';
import useSocket from '../hooks/useSocket';

export default function VideoChat() {
  const localVideo = useRef(null);
  const [translation, setTranslation] = useState('');
  const [status, setStatus] = useState('Initializing...');
  const [isProcessing, setIsProcessing] = useState(false);
  const socket = useSocket();
  
  // Create an audio buffer to accumulate enough audio for recognition
  const audioChunks = useRef([]);
  const chunkCounter = useRef(0);

  useEffect(() => {
    if (!socket) return;

    // Debug: khi kết nối thành công
    socket.on('connect', () => {
      console.log('Socket.IO connected, id=', socket.id);
      setStatus('Connected, waiting for speech...');
    });
    socket.on('connect_error', (err) => {
      console.error('Socket.IO connect_error', err);
      setStatus('Connection error!');
    });

    // Nhận bản dịch từ server
    socket.on('translation', (data) => {
      console.log('Received translation:', data.text);
      if (data.text) {
        setTranslation(data.text);
        setStatus('Received translation');
      }
      setIsProcessing(false);
    });

    // Lấy media và khởi audio processing
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      .then((stream) => {
        localVideo.current.srcObject = stream;
        setStatus('Media stream started, speak to translate');

        // Tạo AudioContext với sampleRate 16000
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContextClass();
        
        // Create a gain node to adjust volume
        const gainNode = audioContext.createGain();
        gainNode.gain.value = 1.5; // Boost volume
        
        // Create an audio stream source from the user media stream
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(gainNode);
        
        // Create a script processor node
        const bufferSize = 4096;
        const processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
        gainNode.connect(processor);
        processor.connect(audioContext.destination);
        
        // Create a resampler if needed
        let resampler;
        if (audioContext.sampleRate !== 16000) {
          console.log(`Resampling from ${audioContext.sampleRate}Hz to 16000Hz`);
          // Simple resampling by taking every nth sample
          const ratio = Math.ceil(audioContext.sampleRate / 16000);
          resampler = (audioData) => {
            const result = new Float32Array(Math.ceil(audioData.length / ratio));
            for (let i = 0; i < result.length; i++) {
              result[i] = audioData[i * ratio];
            }
            return result;
          };
        } else {
          resampler = (audioData) => audioData;
        }

        // Process audio data
        processor.onaudioprocess = (e) => {
          // Skip if we're still processing the previous chunk
          if (isProcessing) return;
          
          // Get audio data and resample if needed
          const inputData = e.inputBuffer.getChannelData(0);
          const resampledData = resampler(inputData);
          
          // Convert to 16-bit PCM
          const pcmData = new Int16Array(resampledData.length);
          for (let i = 0; i < resampledData.length; i++) {
            let s = Math.max(-1, Math.min(1, resampledData[i]));
            pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
          }
          
          // Add to our buffer
          audioChunks.current.push(pcmData.buffer);
          chunkCounter.current++;
          
          // When we have enough audio (about 1-2 seconds worth), send it
          if (chunkCounter.current >= 10) {
            // Concatenate all chunks
            const concatenated = new Uint8Array(
              audioChunks.current.reduce((acc, chunk) => acc + chunk.byteLength, 0)
            );
            
            let offset = 0;
            audioChunks.current.forEach(chunk => {
              concatenated.set(new Uint8Array(chunk), offset);
              offset += chunk.byteLength;
            });
            
            // Send to server
            setIsProcessing(true);
            setStatus('Processing audio...');
            console.log('Sending accumulated audio, bytes:', concatenated.buffer.byteLength);
            socket.emit('audio_chunk', concatenated.buffer);
            
            // Clear buffer
            audioChunks.current = [];
            chunkCounter.current = 0;
            
            // Reset processing state after a timeout (fallback)
            setTimeout(() => {
              if (isProcessing) {
                setIsProcessing(false);
                setStatus('Ready for next chunk');
              }
            }, 5000);
          }
        };
      })
      .catch((err) => {
        console.error('getUserMedia error:', err);
        setStatus('Error accessing media: ' + err.message);
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
      <p className="text-base mb-2">
        <strong>Status:</strong> {status}
      </p>
      <p className="text-base">
        <strong>Translation:</strong> {translation || "(No translation yet)"}
      </p>
    </div>
  );
}