<template>
  <div ref="editorContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { App, Rect } from 'leafer-editor'

// 创建对容器元素的引用
const editorContainer = ref(null)

onMounted(() => {
  const app = new App({
    view: editorContainer.value, // 使用 ref 作为视图
    editor: {} // 自动创建 editor实例、tree层、sky层
  })

  // 添加矩形元素到树层
  app.tree.add(
    Rect.one(
      { editable: true, fill: '#FEB027', cornerRadius: [20, 0, 0, 20] },
      100,
      100
    )
  )
  app.tree.add(
    Rect.one(
      { editable: true, fill: '#FFE04B', cornerRadius: [0, 20, 20, 0] },
      300,
      100
    )
  )
})
</script>

<style scoped>
/* 自定义样式，若有需要可补充 */
</style>
