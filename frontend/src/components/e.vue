<template>
  <div class="w-full h-full">
    <svg ref="svgRef" :width="width" :height="height" @click="handleBackgroundClick" class="bg-gray-900"></svg>
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

// const props = defineProps<{
//   data: Node;
// }>();
// const currentNode = ref<Node>(props.data);

const data = {
  "children": [
    {
      "children": [
        {
          "id": "103171681b8853e9",
          "topic": "第3层A"
        },
        {
          "id": "103173e9e0da3b05",
          "topic": "第3层B"
        }
      ],
      "id": "1031515bc584ffdb",
      "topic": "第2层A"
    },
    {
      "children": [
        {
          "children": [
            {
              "id": "288bf473d3dab9bf",
              "topic": "第4层A"
            },
            {
              "id": "288bf7048cf4f43a",
              "topic": "第4层B"
            }
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
        {
          "id": "191037c4kcfffaad",
          "topic": "第3层D"
        },
        {
          "id": "191037c4fcxffwad",
          "topic": "第3层E"
        }
      ],
      "id": "191037c4fcf30936",
      "topic": "第2层C"
    },
    {
      "children": [
        {
          "id": "191037d4fcfffavd",
          "topic": "第3层F"
        },
        {
          "id": "191037cqfcfffaxd",
          "topic": "第3层G"
        }
      ],
      "id": "191037c4fcf8ba85",
      "topic": "第2层D"
    }
  ],
  "id": "root",
  "topic": "第1层"
}

const svgRef = ref<SVGSVGElement | null>(null);
const currentNode = ref<Node>(data);
const width = 800;
const height = 600;
const nodeRadius = 50;

let simulation: d3.Simulation<Node, undefined>;

const zoomToNode = (node: Node) => {
  if (!node.children) return;
  currentNode.value = node;
};

const zoomOut = () => {
  const parent = findParent(props.data, currentNode.value);
  if (parent) {
    currentNode.value = parent;
  }
};

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

const initializeSimulation = (nodes: Node[]) => {
  simulation = d3.forceSimulation(nodes)
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(nodeRadius * 1.5))
    .on('tick', () => {
      updateNodes();
    });
};

const updateNodes = () => {
  if (!svgRef.value) return;

  const svg = d3.select(svgRef.value);

  // Clear previous nodes
  svg.selectAll('*').remove();

  // Create groups for nodes
  const nodes = svg
    .selectAll('g')
    .data(currentNode.value.children || [])
    .enter()
    .append('g')
    .attr('transform', d => `translate(${d.x},${d.y})`);

  // Add circles
  nodes
    .append('circle')
    .attr('r', nodeRadius)
    .attr('class', 'fill-blue-500 opacity-80 cursor-pointer hover:fill-blue-600 transition-colors');

  // Add text
  nodes
    .append('text')
    .text(d => d.topic)
    .attr('class', 'text-sm fill-white text-center pointer-events-none')
    .attr('dy', '0.3em')
    .attr('text-anchor', 'middle');

  // Add click handlers
  nodes.on('click', (event, d) => {
    event.stopPropagation();
    zoomToNode(d);
  });
};

// Handle background click for zoom out
const handleBackgroundClick = (event: MouseEvent) => {
  if (event.target === svgRef.value) {
    zoomOut();
  }
};

// Initialize visualization
onMounted(() => {
  if (!currentNode.value.children) return;
  initializeSimulation(currentNode.value.children);
});

// Watch for changes in current node
watch(currentNode, () => {
  if (!currentNode.value.children) return;
  simulation.nodes(currentNode.value.children);
  simulation.alpha(1).restart();
});
</script>