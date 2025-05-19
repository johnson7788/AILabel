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
  //复杂的创建矩形
  const rect = new Rect({
    x: 100,
    y: 100,
    width: 200,
    height: 200,
    fill: 'yellow', // 背景色
    editable: true,
  })
  //简单语句创建
  const rect2 = Rect.one({editable: true, fill: 'red' }, 100, 100, 200, 200)
  app.tree.add(rect2)

  //使用Tag创建矩形
  app.tree.add({
      editable: true,
      tag: 'Rect', // 必须要有类名tag
      x: 100,
      y: 100,
      width: 200,
      height: 200,
      fill: 'blue'
  })

  //使用json格式创建矩形
  const json = { "tag": 'Group', "x": 20, "y": 20, "children": [{ "tag": "Rect", "x": 100, "y": 100, "width": 200, "height": 200, "fill": "#32cd79", "draggable": true }] }
  
  app.tree.add(json)

  app.tree.add(rect)

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
