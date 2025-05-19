<template>
  <MindMap :data="knowledgeData" />
</template>

<script setup>
import MindMap from './w.vue';
import { ref } from 'vue';

const knowledgeData = ref({
  "id": "root",
  "name": "顶层节点",
  "description": "这是顶层节点的描述",
  "children": [
    {
      "id": "node1",
      "name": "子节点 1",
      "description": "这是子节点 1 的描述",
      "children": [
        {
          "id": "node1_1",
          "name": "子节点 1.1",
          "description": "这是子节点 1.1 的描述",
          "children": []
        }
      ]
    },
    {
      "id": "node2",
      "name": "子节点 2",
      "description": "这是子节点 2 的描述",
      "children": []
    }
  ]
});
</script>