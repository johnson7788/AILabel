<template>
  <div class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
    <div class="relative py-3 sm:max-w-xl sm:mx-auto">
      <div class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
      <div class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
        <div class="max-w-md mx-auto">
          <div class="divide-y divide-gray-200">
            <div class="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
              <h2 class="text-3xl font-extrabold text-gray-900">Voice LLM Client</h2>
              <p class="text-gray-500">Click the button below to start/stop recording</p>
              <button
                @click="toggleRecording"
                :class="[
                  'px-4 py-2 font-semibold text-sm rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2',
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 focus:ring-red-500 text-white'
                    : 'bg-cyan-500 hover:bg-cyan-600 focus:ring-cyan-500 text-white'
                ]"
              >
                {{ isRecording ? 'Stop Recording' : 'Start Recording' }}
              </button>
              <div class="mt-6 border-t border-gray-200 pt-4">
                <h3 class="text-lg font-medium text-gray-900">Messages</h3>
                <div class="mt-2 max-h-60 overflow-y-auto">
                  <div v-for="(message, index) in messages" :key="index" class="text-sm text-gray-500">
                    <span class="font-medium text-gray-900">{{ message.sender }}:</span> {{ message.content }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isRecording = ref(false)
const messages = ref([])
const websocket = ref(null)
const mediaRecorder = ref(null)
const audioContext = ref(null)
const audioSource = ref(null)
const audioProcessor = ref(null)

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
    audioSource.value = audioContext.value.createMediaStreamSource(stream)
    audioProcessor.value = audioContext.value.createScriptProcessor(4096, 1, 1)

    audioSource.value.connect(audioProcessor.value)
    audioProcessor.value.connect(audioContext.value.destination)

    audioProcessor.value.onaudioprocess = processAudioData
    
    isRecording.value = true
  } catch (error) {
    console.error('Error accessing microphone:', error)
    messages.value.push({ sender: 'System', content: 'Error accessing microphone. Please check your permissions.' })
  }
}

const stopRecording = () => {
  if (audioProcessor.value) {
    audioProcessor.value.disconnect()
    audioSource.value.disconnect()
    isRecording.value = false
  }
}

const floatTo16BitPCM = (float32Array) => {
  const buffer = new ArrayBuffer(float32Array.length * 2)
  const view = new DataView(buffer)
  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i]))
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true)
  }
  return buffer
}

const base64EncodeAudio = (float32Array) => {
  const arrayBuffer = floatTo16BitPCM(float32Array)
  const bytes = new Uint8Array(arrayBuffer)
  let binary = ''
  const chunkSize = 0x8000 // 32KB chunk size
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize)
    binary += String.fromCharCode.apply(null, chunk)
  }
  return btoa(binary)
}

const processAudioData = (e) => {
  const inputData = e.inputBuffer.getChannelData(0)
  const base64AudioData = base64EncodeAudio(inputData)
  sendAudioData(base64AudioData)
}

const sendAudioData = (base64AudioData) => {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    const event = {
      event: 'media',
      media: {
        payload: base64AudioData
      }
    }
    websocket.value.send(JSON.stringify(event))
  }
}

const connectWebSocket = () => {
  const wsUrl = `ws://${window.location.hostname}:8000/ws/voice-stream/dispatcher`
  websocket.value = new WebSocket(wsUrl)

  websocket.value.onopen = () => {
    messages.value.push({ sender: 'System', content: 'Connected to server' })
  }

  websocket.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.event === 'media') {
      // 返回的格式也是 base64 编码的音频数据，读取media.payload字段，然后播放
      messages.value.push({ sender: 'System', content: 'Received audio response' })
    } else {
      messages.value.push({ sender: 'Agent', content: data.content || JSON.stringify(data) })
    }
  }

  websocket.value.onclose = () => {
    messages.value.push({ sender: 'System', content: 'Disconnected from server' })
  }

  websocket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    messages.value.push({ sender: 'System', content: 'WebSocket error occurred' })
  }
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.close()
  }
  if (audioContext.value) {
    audioContext.value.close()
  }
})
</script>