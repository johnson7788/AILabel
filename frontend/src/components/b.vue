<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';

interface Message {
  id: number;
  sender: string;
  text: string;
  timestamp: Date;
}

const messages = ref<Message[]>([]);
const chatContainer = ref<HTMLElement | null>(null);

const users = ['Alice', 'Bob', 'Charlie', 'David', 'Eve'];
const randomTexts = [
  'Hello there!',
  'How are you?',
  'Nice weather today!',
  'What are you up to?',
  'Have a great day!',
  'Just checking in!',
  'Any plans for the weekend?',
  'Did you see that?',
  'Interesting...',
  'Let\'s catch up soon!'
];

const addRandomMessage = () => {
  const newMessage: Message = {
    id: Date.now(),
    sender: users[Math.floor(Math.random() * users.length)],
    text: randomTexts[Math.floor(Math.random() * randomTexts.length)],
    timestamp: new Date()
  };
  
  messages.value.push(newMessage);
  scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

onMounted(() => {
  setInterval(addRandomMessage, 500);
});
</script>

<template>
  <div class="max-w-md mx-auto p-4 h-screen flex flex-col">
    <div class="bg-white rounded-lg shadow-lg flex flex-col h-full">
      <div class="bg-blue-600 text-white p-4 rounded-t-lg">
        <h2 class="text-xl font-bold">Chat Room</h2>
      </div>
      
      <div 
        ref="chatContainer"
        class="flex-1 overflow-y-auto p-4 space-y-4"
        style="max-height: calc(100vh - 8rem);"
      >
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="flex flex-col"
        >
          <div class="flex items-baseline space-x-2">
            <span class="font-bold text-blue-600">{{ message.sender }}</span>
            <span class="text-xs text-gray-500">
              {{ message.timestamp.toLocaleTimeString() }}
            </span>
          </div>
          <div class="bg-gray-100 rounded-lg p-3 mt-1 max-w-[80%] break-words">
            {{ message.text }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>