<template>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <Card v-for="card in cards" :key="card.id" v-bind="card" />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue'
  import Card from './Card.vue'
  
  export default defineComponent({
    name: 'CardGrid',
    components: {
      Card
    },
    props: {
      cards: Array
    }
  })
  </script>
  