<template>
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-6 text-center">AI Tools</h1>
      <CardGrid :cards="cardData" />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue'
  import CardGrid from './CardGrid.vue'
  import { cardData } from './cards.ts'
  
  export default defineComponent({
    name: 'Home',
    components: {
      CardGrid
    },
    data() {
      return {
        cardData
      }
    }
  })
  </script>
  