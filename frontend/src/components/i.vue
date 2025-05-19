<template>
  <div class="w-full h-screen bg-gray-100" ref="container">
    <svg class="w-full h-full" ref="svg"></svg>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

const container = ref(null);
const svg = ref(null);
const data = ref({
  children: [
    {
      children: [
        { id: "103171681b8853e9", topic: "生成数十个不同的创意" },
        { id: "103173e9e0da3b05", topic: "https://seenapse.ai/" }
      ],
      id: "1031515bc584ffdb",
      topic: "Seenapse"
    },
    {
      children: [
        {
          children: [
            { id: "288bf473d3dab9bf", topic: "CosyVoice：基于监督语义令牌的可扩展多语言零样本文本转语音合成器" },
            { id: "288bf7048cf4f43a", topic: "https://arxiv.org/abs/2407.05407" }
          ],
          id: "115f5108e5635e42",
          topic: "论文标题"
        }
      ],
      id: "group1",
      topic: "Group 1"
    },
    {
      children: [
        { id: "191037c4kcfffaad", topic: "创建产品概念（也是 Photoshop 插件）" },
        { id: "191037c4fcxffwad", topic: "https://stablediffusionweb.com/" }
      ],
      id: "191037c4fcf30936",
      topic: "Stable Diffusion"
    },
    {
      children: [
        { id: "191037d4fcfffavd", topic: "让你的绘图秒变成现实" },
        { id: "191037cqfcfffaxd", topic: "https://www.vizcom.co/" }
      ],
      id: "191037c4fcf8ba85",
      topic: "Vizcom"
    }
  ],
  id: "root",
  topic: "AI工具大全"
});

const zoom = d3.zoom().scaleExtent([0.1, 10]);
let currentDepth = 0;

onMounted(() => {
  const svgElement = d3.select(svg.value);
  const g = svgElement.append('g');

  zoom.on('zoom', (event) => {
    g.attr('transform', event.transform);
    updateVisibleNodes(event.transform.k);
  });

  svgElement.call(zoom);

  const root = d3.hierarchy(data.value);
  const treeLayout = d3.tree().size([2000, 1000]);
  treeLayout(root);

  function updateVisibleNodes(scale) {
    const newDepth = Math.floor(scale);
    if (newDepth !== currentDepth) {
      currentDepth = newDepth;
      updateNodes();
    }
  }

  function updateNodes() {
    const nodes = root.descendants().filter(d => d.depth <= currentDepth);
    
    const nodeElements = g.selectAll('.node')
      .data(nodes, d => d.data.id);

    const nodeEnter = nodeElements.enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y},${d.x})`);

    nodeEnter.append('circle')
      .attr('r', 5)
      .attr('fill', d => d.children ? '#69b3a2' : '#404080');

    nodeEnter.append('text')
      .attr('dy', '.31em')
      .attr('x', d => d.children ? -8 : 8)
      .style('text-anchor', d => d.children ? 'end' : 'start')
      .text(d => d.data.topic)
      .attr('fill', '#333')
      .attr('font-size', '12px');

    nodeElements.exit().remove();
  }

  updateNodes();
});
</script>