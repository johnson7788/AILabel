<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount } from 'vue';
import Graph from 'graphology';
import Sigma from 'sigma';
import FA2Layout from 'graphology-layout-forceatlas2';

const graphData = {
  nodes: [
    { id: '1', label: 'AI', size: 15, color: '#3b82f6' },
    { id: '2', label: 'Machine Learning', size: 12, color: '#6366f1' },
    { id: '3', label: 'Deep Learning', size: 12, color: '#8b5cf6' },
    { id: '4', label: 'Neural Networks', size: 10, color: '#a78bfa' },
    { id: '5', label: 'Computer Vision', size: 10, color: '#ec4899' },
    { id: '6', label: 'Natural Language Processing', size: 10, color: '#f43f5e' },
    { id: '7', label: 'Reinforcement Learning', size: 10, color: '#10b981' }
  ],
  edges: [
    { source: '1', target: '2', id: 'e1', label: 'includes', color: '#64748b' },
    { source: '1', target: '3', id: 'e2', label: 'encompasses', color: '#64748b' },
    { source: '2', target: '4', id: 'e3', label: 'utilizes', color: '#64748b' },
    { source: '2', target: '5', id: 'e4', label: 'applies to', color: '#64748b' },
    { source: '3', target: '4', id: 'e5', label: 'based on', color: '#64748b' },
    { source: '2', target: '6', id: 'e6', label: 'enables', color: '#64748b' },
    { source: '2', target: '7', id: 'e7', label: 'incorporates', color: '#64748b' }
  ]
};

const container = ref<HTMLElement | null>(null);
let sigma: any = null;
let graph: Graph | null = null;
let fa2Layout: any = null;

onMounted(() => {
  if (!container.value) return;

  // Create graph instance
  graph = new Graph();

  // Add nodes
  graphData.nodes.forEach(node => {
    graph?.addNode(node.id, {
      ...node,
      x: Math.random() * 10,
      y: Math.random() * 10,
    });
  });

  // Add edges with labels
  graphData.edges.forEach(edge => {
    graph?.addEdge(edge.source, edge.target, {
      ...edge,
      type: 'arrow',
      size: 2,
    });
  });

  // Initialize ForceAtlas2 layout
  fa2Layout = FA2Layout.assign(graph, {
    iterations: 100,
    settings: {
      gravity: 0.5,
      scalingRatio: 10,
      strongGravityMode: true,
      slowDown: 2,
      barnesHutOptimize: true,
      barnesHutTheta: 0.5,
    }
  });

  // Initialize Sigma
  sigma = new Sigma(graph, container.value, {
    minCameraRatio: 0.1,
    maxCameraRatio: 10,
    labelColor: '#334155',
    labelSize: 14,
    labelWeight: 'bold',
    edgeLabelSize: 12,
    renderEdgeLabels: true,
    defaultEdgeType: 'arrow',
    defaultEdgeColor: '#64748b',
    nodeColor: 'color',
    edgeColor: 'color',
    borderSize: 2,
    borderColor: '#ffffff'
  });
});

onBeforeUnmount(() => {
  sigma?.kill();
});
</script>

<template>
  <div class="w-full h-full bg-slate-50 rounded-xl p-4">
    <div 
      ref="container" 
      class="w-full h-[700px] bg-white rounded-lg shadow-lg border border-slate-200"
    ></div>
  </div>
</template>

<style>
.sigma-edge-label {
  font-size: 12px;
  fill: #64748b;
  text-anchor: middle;
}

.sigma-node {
  transition: all 0.3s ease;
}

.sigma-node:hover {
  cursor: pointer;
  transform: scale(1.1);
}
</style>