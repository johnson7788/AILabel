<template>
  <div class="w-full h-full">
    <svg ref="svgRef" :width="width" :height="height" @click="handleBackgroundClick" @wheel="handleScroll"
      class="bg-gray-900"></svg>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

interface Node {
  id: string;
  topic: string;
  children?: Node[];
  x?: number;
  y?: number;
  r?: number;
}

const data = {
  "children": [
    {
      "children": [
        { "id": "103171681b8853e9", "topic": "第3层A" },
        { "id": "103173e9e0da3b05", "topic": "第3层B" }
      ],
      "id": "1031515bc584ffdb",
      "topic": "第2层A"
    },
    {
      "children": [
        {
          "children": [
            { "id": "288bf473d3dab9bf", "topic": "第4层A" },
            { "id": "288bf7048cf4f43a", "topic": "第4层B" }
          ],
          "id": "115f5108e5635e42",
          "topic": "第3层C"
        }
      ],
      "id": "papers",
      "topic": "第2层B"
    },
    {
      "children": [
        { "id": "191037c4kcfffaad", "topic": "第3层D" },
        { "id": "191037c4fcxffwad", "topic": "第3层E" }
      ],
      "id": "191037c4fcf30936",
      "topic": "第2层C"
    },
    {
      "children": [
        { "id": "191037d4fcfffavd", "topic": "第3层F" },
        { "id": "191037cqfcfffaxd", "topic": "第3层G" }
      ],
      "id": "191037c4fcf8ba85",
      "topic": "第2层D"
    }
  ],
  "id": "root",
  "topic": "第1层"
};

const svgRef = ref<SVGSVGElement | null>(null);
const currentNode = ref<Node>(data);
const width = 800;
const height = 600;
const nodeRadius = 50;

let simulation: d3.Simulation<Node, undefined>;

// 放大到节点，显示其子节点
const zoomToNode = (node: Node) => {
  if (!node.children) return;
  currentNode.value = node;
};

// 返回上一层节点
const zoomOut = () => {
  const parent = findParent(data, currentNode.value);
  if (parent) {
    currentNode.value = parent;
  }
};

// 查找目标节点的父节点
const findParent = (root: Node, target: Node): Node | null => {
  if (root.children) {
    for (const child of root.children) {
      if (child === target) return root;
      const found = findParent(child, target);
      if (found) return found;
    }
  }
  return null;
};

// 初始化节点力学模拟
const initializeSimulation = (nodes: Node[]) => {
  simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(nodeRadius * 1.5))
    .alpha(1)  // 初始的 alpha 值，用于强制快速开始
    .alphaDecay(0.05)  // 加速衰减速度，默认是 0.0228
    .on('tick', () => {
      updateNodes();
    });
};

// 更新节点显示
const updateNodes = () => {
  if (!svgRef.value) return;

  const svg = d3.select(svgRef.value);

  // 清除先前节点
  svg.selectAll('*').remove();

  // 创建节点组
  const nodes = svg
    .selectAll('g')
    .data(currentNode.value.children || [])
    .enter()
    .append('g')
    .attr('transform', d => `translate(${d.x},${d.y})`);

  // 添加节点圆形
  nodes
    .append('circle')
    .attr('r', nodeRadius)
    .attr('class', 'fill-blue-500 opacity-80 cursor-pointer hover:fill-blue-600 transition-colors');

  // 添加节点文本
  nodes
    .append('text')
    .text(d => d.topic)
    .attr('class', 'text-sm fill-white text-center pointer-events-none')
    .attr('dy', '0.3em')
    .attr('text-anchor', 'middle');

  // 添加点击事件处理
  nodes.on('click', (event, d) => {
    event.stopPropagation();
    zoomToNode(d);
  });
};

// 没有点击到节点上的时候，用于缩小视图
const handleBackgroundClick = (event: MouseEvent) => {
  if (event.target === svgRef.value) {
    zoomOut();
  }
};

// 设置滚轮敏感度阈值和累积滚动量
let scrollThreshold = 100; // 滚轮敏感度阈值
let scrollDelta = 0; // 累积滚动量
let currentScale = 1; // 当前缩放比例

const handleScroll = (event: WheelEvent) => {
  event.preventDefault();

  // 累加滚动量
  scrollDelta += event.deltaY;

  // 根据滚动量动态改变当前缩放比例
  currentScale = 1 + Math.abs(scrollDelta) / scrollThreshold;

  // 更新当前节点的缩放效果
  updateZoomTransform(currentScale);

  // 当滚动量达到阈值时，进入下一层或返回上一层
  if (Math.abs(scrollDelta) >= scrollThreshold) {
    if (scrollDelta < 0) {
      // 放大到下一层
      if (currentNode.value.children && currentNode.value.children.length > 0) {
        currentNode.value = currentNode.value.children[0]; // 展开第一个子节点层次
      }
    } else {
      // 缩小到上一层
      zoomOut();
    }

    // 重置缩放比例和滚动量
    currentScale = 1;
    scrollDelta = 0;
    updateZoomTransform(currentScale);
  }
};

// 更新当前视图的缩放
const updateZoomTransform = (scale) => {
  if (!svgRef.value) return;

  const svg = d3.select(svgRef.value);

  // 将当前节点应用缩放比例
  svg.selectAll('g')
    .attr('transform', d => `translate(${d.x}, ${d.y}) scale(${scale})`);
};

// 初始化视图和力学模拟
onMounted(() => {
  if (!currentNode.value.children) return;
  initializeSimulation(currentNode.value.children);
});

// 监听当前节点变化并重新应用力学模拟
watch(currentNode, () => {
  if (!currentNode.value.children) return;
  simulation.nodes(currentNode.value.children);
  simulation.alpha(1).restart();
});
</script>

<style>
.fill-blue-500 {
  fill: #4299e1;
}

.fill-blue-600 {
  fill: #2b6cb0;
}

.bg-gray-900 {
  background-color: #1a202c;
}

.text-sm {
  font-size: 0.875rem;
}

.fill-white {
  fill: #ffffff;
}
</style>
