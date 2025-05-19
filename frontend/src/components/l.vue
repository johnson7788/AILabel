<template>
  <div class="min-h-screen bg-gray-900">
    <!-- Header -->
    <header class="bg-gray-800 p-4 flex justify-between items-center">
      <div class="flex items-center space-x-4">
        <h1 class="text-xl font-bold text-white">Voice Agent</h1>
      </div>
      <div class="flex items-center space-x-4">
        <button @click="toggleConnection" :class="[
          'px-4 py-2 rounded-md',
          isConnected ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
        ]">
          {{ isConnected ? 'Disconnect' : 'Connect' }}
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto p-4">
      <div class="grid grid-cols-2 gap-4">
        <!-- Left Panel -->
        <div class="bg-gray-800 rounded-lg p-4">
          <h2 class="text-xl mb-4">Agent</h2>
          <!-- Microphone Section -->
          <div class="mt-8">
            <div class="bg-gray-700 p-4 rounded-lg">
              <div class="flex items-center space-x-2">
                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">MICROPHONE</span>
                <button @click="toggleRecording" :disabled="!isConnected" class="text-blue-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Panel - Chat -->
        <div class="bg-gray-800 rounded-lg p-4">
          <div class="h-[600px] overflow-y-auto">
            <div v-for="(message, index) in messages" :key="index" class="mb-4 p-2 rounded" :class="{
          'bg-gray-700': message.type === 'system',
          'bg-blue-600': message.type === 'sent',
          'bg-green-600': message.type === 'received'
        }">
              {{ message.content }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const isConnected = ref(false);
const isRecording = ref(false);
const messages = ref<{ type: string; content: string }[]>([]);
let websocket: WebSocket | null = null;
let mediaRecorder: MediaRecorder | null = null;
let audioContext: AudioContext | null = null;
let audioSource: MediaStreamAudioSourceNode | null = null;
let audioProcessor: ScriptProcessorNode | null = null;

const toggleConnection = () => {
  if (isConnected.value) {
    websocket?.close();
    isConnected.value = false;
    isRecording.value = false;
  } else {
    connectWebSocket();
  }
};

const connectWebSocket = () => {
  websocket = new WebSocket('ws://127.0.0.1:8000/ws/voice-stream/dispatcher');

  websocket.onopen = () => {
    isConnected.value = true;
    messages.value.push({ type: 'system', content: 'Connected to server' });
  };

  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'media') {
      messages.value.push({ type: 'received', content: 'Received audio data' });
      playAudio(data.media.payload);
    }
  };

  websocket.onclose = () => {
    isConnected.value = false;
    messages.value.push({ type: 'system', content: 'Disconnected from server' });
  };
};

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording();
  } else {
    startRecording();
  }
};

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioSource = audioContext.createMediaStreamSource(stream);
    audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);

    audioSource.connect(audioProcessor);
    audioProcessor.connect(audioContext.destination);

    audioProcessor.onaudioprocess = processAudioData;
    isRecording.value = true;
  } catch (error) {
    console.error('Error accessing microphone:', error);
    messages.value.push({ type: 'system', content: 'Error accessing microphone. Please check your permissions.' });
  }
};

const stopRecording = () => {
  if (audioProcessor) {
    audioProcessor.disconnect();
    audioSource?.disconnect();
    isRecording.value = false;
  }
};

const processAudioData = (e) => {
  const inputData = e.inputBuffer.getChannelData(0);
  const base64AudioData = base64EncodeAudio(inputData);
  sendAudioData(base64AudioData);
};

const base64EncodeAudio = (float32Array) => {
  const arrayBuffer = floatTo16BitPCM(float32Array);
  const bytes = new Uint8Array(arrayBuffer);
  let binary = '';
  const chunkSize = 0x8000; // 32KB chunk size
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize);
    binary += String.fromCharCode.apply(null, chunk);
  }
  return btoa(binary);
};

const floatTo16BitPCM = (float32Array) => {
  const buffer = new ArrayBuffer(float32Array.length * 2);
  const view = new DataView(buffer);
  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i]));
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
};

const sendAudioData = (base64AudioData) => {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    const event = {
      event: 'media',
      media: { payload: base64AudioData }
    };
    websocket.send(JSON.stringify(event));
  }
};

const playAudio = (base64AudioData) => {
  const byteArray = Uint8Array.from(atob(base64AudioData), c => c.charCodeAt(0));
  const audioBuffer = audioContext.createBuffer(1, byteArray.length / 2, 44100);
  const bufferData = new Int16Array(byteArray.buffer);
  for (let i = 0; i < bufferData.length; i++) {
    audioBuffer.getChannelData(0)[i] = bufferData[i] / 0x8000;
  }

  const audioSourceNode = audioContext.createBufferSource();
  audioSourceNode.buffer = audioBuffer;
  audioSourceNode.connect(audioContext.destination);
  audioSourceNode.start();
};

onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  if (websocket) {
    websocket.close();
  }
  if (audioContext) {
    audioContext.close();
  }
});
</script>

<style scoped>
.animate-pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    height: 8px;
  }
  50% {
    opacity: .5;
    height: 16px;
  }
}
</style>
