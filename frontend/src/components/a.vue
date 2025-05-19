<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="p-6 bg-white rounded-lg shadow-md">
      <h1 class="text-2xl font-semibold mb-4">Current Outline ID</h1>
      <p class="text-lg">The outline ID is: <span class="font-bold text-blue-500">{{ outlineId }}</span></p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
// 引入 Vue Router
import { useRoute } from 'vue-router';

// 使用 Vue Router 获取 URL 查询参数
const route = useRoute();
const outlineId = computed(() => {
  // 获取 URL 中的 outlineid 参数，若不存在则使用默认值 1
  return route.query.outlineid ? Number(route.query.outlineid) : 1;
});
</script>

<style scoped>
/* 在这里可以添加你的自定义样式 */
</style>
