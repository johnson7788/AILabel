<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="w-full max-w-2xl bg-white rounded-lg shadow-xl p-6">
      <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">Text Printer</h1>
      
      <textarea
        v-model="inputText"
        placeholder="粘贴一段文本，然后点击开始，即可实现打字机效果"
        class="w-full h-32 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
      ></textarea>
      
      <div class="flex justify-center space-x-4 mb-6">
        <button
          @click="startPrinting"
          :disabled="isPrinting"
          class="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
        >
          Start
        </button>
        <button
          @click="stopPrinting"
          :disabled="!isPrinting"
          class="px-6 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
        >
          Stop
        </button>
      </div>
      
      <div 
        class="bg-gray-100 p-4 rounded-md h-64 overflow-auto whitespace-pre-wrap"
        v-text="displayedText"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const inputText = ref('')
const displayedText = ref('')
const isPrinting = ref(false)
const currentIndex = ref(0)
const printInterval = ref(null)

const startPrinting = () => {
  if (inputText.value && !isPrinting.value) {
    isPrinting.value = true
    currentIndex.value = 0
    displayedText.value = ''
    printNextChar()
  }
}

const printNextChar = () => {
  if (currentIndex.value < inputText.value.length) {
    displayedText.value += inputText.value[currentIndex.value]
    currentIndex.value++
    printInterval.value = setTimeout(printNextChar, 100) // 调整这个值可以改变打印速度
  } else {
    isPrinting.value = false
  }
}

const stopPrinting = () => {
  clearTimeout(printInterval.value)
  isPrinting.value = false
}

watch(inputText, () => {
  displayedText.value = ''
  currentIndex.value = 0
  isPrinting.value = false
  clearTimeout(printInterval.value)
})
</script>