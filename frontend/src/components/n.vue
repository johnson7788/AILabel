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
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-500" fill="none"
                                    viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                </svg>
                            </div>
                            <!-- Waveform Animation -->
                            <div v-if="isRecording" class="waveform-container mt-4">
                                <div v-for="(barHeight, index) in barHeights" :key="index"
                                    :style="{ height: `${barHeight}px` }" class="waveform-bar"></div>
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
const barHeights = ref<number[]>(Array(20).fill(5)); // Initialize 20 bars with height 5px
let websocket: WebSocket | null = null;
let audioContext: AudioContext | null = null;
let audioSource: MediaStreamAudioSourceNode | null = null;
let analyser: AnalyserNode | null = null;
let dataArray: Uint8Array | null = null;

const toggleConnection = () => {
    if (isConnected.value) {
        websocket?.close();
        isConnected.value = false;
        isRecording.value = false;
        stopRecording();
    } else {
        connectWebSocket();
    }
};

const connectWebSocket = () => {
    websocket = new WebSocket('ws://127.0.0.1:8000/ws/voice-stream/dispatcher');

    websocket.onopen = () => {
        isConnected.value = true;
        messages.value.push({ type: 'system', content: 'Connected to server' });
        startRecording();
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

const startRecording = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        audioSource = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 64; // Lower FFT size to fit fewer bars
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        audioSource.connect(analyser);
        isRecording.value = true;
        updateWaveform(); // Start updating the waveform
    } catch (error) {
        console.error('Error accessing microphone:', error);
        messages.value.push({ type: 'system', content: 'Error accessing microphone. Please check your permissions.' });
    }
};

const updateWaveform = () => {
    if (analyser && dataArray) {
        analyser.getByteFrequencyData(dataArray);
        // Update bar heights based on frequency data
        for (let i = 0; i < barHeights.value.length; i++) {
            barHeights.value[i] = (dataArray[i] || 0) / 2; // Adjust scale as needed
        }
        if (isRecording.value) {
            requestAnimationFrame(updateWaveform); // Continue updating the waveform
        }
    }
};

const stopRecording = () => {
    if (audioSource && analyser) {
        audioSource.disconnect();
        analyser.disconnect();
        isRecording.value = false;
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
.waveform-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 50px;
    background-color: #2d2d2d;
    padding: 5px;
    border-radius: 8px;
}

.waveform-bar {
    width: 4px;
    background-color: #4a90e2;
    transition: height 0.05s;
    border-radius: 2px;
}
</style>