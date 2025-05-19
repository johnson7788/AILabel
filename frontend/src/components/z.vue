<template>
  <div>
    <ZJSX msg="Hello from TSX!"/>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import ZJSX from './ZJSX'

export default defineComponent({
  components: {
    ZJSX
  }
})
</script>
