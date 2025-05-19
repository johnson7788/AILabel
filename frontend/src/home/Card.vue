<template>
    <!-- 使用 <router-link> 包裹整个卡片，使其可点击 -->
    <router-link :to="link" class="group">
      <div :style="{ '--theme-color': color }" class="card rounded-lg overflow-hidden shadow-lg transition-transform duration-300 ease-in-out transform hover:scale-105">
        <!-- 图片容器 -->
        <div class="relative h-48">
          <img :src="image" :alt="title" class="w-full h-full object-cover transition-opacity duration-300 ease-in-out group-hover:opacity-75"/>
        </div>
        <!-- 文本内容容器 -->
        <div class="p-6">
          <h3 class="text-xl font-semibold mb-2 card-title">{{ title }}</h3>
          <p class="card-description">{{ description }}</p>
        </div>
      </div>
    </router-link>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue'
  
  export default defineComponent({
    name: 'Card',
    props: {
      image: String,
      color: String,
      title: String,
      description: String,
      link: String
    }
  })
  </script>
  
  <style scoped>
  .card {
    background-color: color-mix(in srgb, var(--theme-color) 10%, white);
  }
  
  .card-title {
    color: color-mix(in srgb, var(--theme-color) 70%, black);
  }
  
  .card-description {
    color: color-mix(in srgb, var(--theme-color) 60%, black);
  }
  </style>
  