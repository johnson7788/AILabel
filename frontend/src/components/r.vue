<script setup lang="ts">
import { ref } from 'vue'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const searchQuery = ref('')
const emit = defineEmits(['search'])

const handleSearch = () => {
    emit('search', searchQuery.value)
}

const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Enter') {
        handleSearch()
    }
}
</script>

<template>
    <div class="w-full max-w-2xl mx-auto mb-12">
        <div class="relative flex items-center">
            <input v-model="searchQuery" type="text" placeholder="输入你的问题..." @keydown="handleKeydown" class="w-full px-6 py-4 text-lg rounded-full border border-gray-200 
               shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
               placeholder-gray-400 transition-all duration-300
               pr-[120px]" />
            <button @click="handleSearch" class="absolute right-2 inline-flex items-center px-6 py-2.5 rounded-full
               bg-gradient-to-r from-indigo-600 to-purple-600 text-white
               hover:from-indigo-700 hover:to-purple-700 transition-all duration-300
               font-medium text-sm shadow-sm hover:shadow-md">
                <MagnifyingGlassIcon class="w-4 h-4 mr-2" />
                搜索
            </button>
        </div>
    </div>
</template>