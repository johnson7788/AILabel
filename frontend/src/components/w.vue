<template>
  <div class="w-full h-screen bg-gray-100">
    <svg ref="svg" class="w-full h-full"></svg>
    <div ref="tooltip" class="absolute hidden bg-white p-2 rounded shadow-lg border border-gray-200"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const svg = ref(null);
const tooltip = ref(null);
const width = ref(window.innerWidth);
const height = ref(window.innerHeight);

const zoom = d3.zoom()
  .scaleExtent([0.1, 4])
  .on('zoom', zoomed);

let root;
let g;

onMounted(() => {
  const svgElement = d3.select(svg.value);

  g = svgElement.append('g');
  
  svgElement.call(zoom);
  
  root = d3.hierarchy(props.data);
  root.x0 = height.value / 2;
  root.y0 = 0;
  update(root);
  
  // Only collapse if root has children
  if (root.children) {
    root.children.forEach(collapse);
  }

  window.addEventListener('resize', onResize);
});

watch(() => props.data, (newData) => {
  root = d3.hierarchy(newData);
  root.x0 = height.value / 2;
  root.y0 = 0;
  update(root);

  // Collapse all nodes when data changes
  if (root.children) {
    root.children.forEach(collapse);
  }
});

function collapse(d) {
  if (d.children) {
    d._children = d.children;
    d._children.forEach(collapse);
    d.children = null;
  }
}


function update(source) {
  const duration = 750;
  const treeLayout = d3.tree().size([height.value, width.value - 200]);
  
  const nodes = root.descendants();
  const links = root.links();
  
  treeLayout(root);
  
  const link = g.selectAll('.link')
    .data(links, d => d.target.id)
    .join(
      enter => enter.append('path')
        .attr('class', 'link')
        .attr('d', d => {
          const o = {x: source.x0, y: source.y0};
          return diagonal(o, o);
        }),
      update => update,
      exit => exit.transition().duration(duration)
        .attr('d', d => {
          const o = {x: source.x, y: source.y};
          return diagonal(o, o);
        })
        .remove()
    )
    .transition()
    .duration(duration)
    .attr('d', d => diagonal(d.source, d.target));
  
  const node = g.selectAll('.node')
    .data(nodes, d => d.id)
    .join(
      enter => {
        const nodeEnter = enter.append('g')
          .attr('class', 'node')
          .attr('transform', d => `translate(${source.y0},${source.x0})`)
          .on('click', (event, d) => {
            d.children = d.children ? null : d._children;
            update(d);
          });

        nodeEnter.append('circle')
          .attr('r', 5)
          .attr('fill', d => d._children ? '#fd9d3e' : '#01c5c4');

        nodeEnter.append('text')
          .attr('dy', '0.31em')
          .attr('x', d => d.children || d._children ? -8 : 8)
          .attr('text-anchor', d => d.children || d._children ? 'end' : 'start')
          .text(d => d.data.name)
          .attr('fill', '#333')
          .attr('font-size', '12px');

        return nodeEnter;
      },
      update => update,
      exit => exit.transition().duration(duration)
        .attr('transform', d => `translate(${source.y},${source.x})`)
        .remove()
    )
    .transition()
    .duration(duration)
    .attr('transform', d => `translate(${d.y},${d.x})`);

  node.select('circle')
    .attr('fill', d => d._children ? '#fd9d3e' : '#01c5c4');

  node
    .on('mouseover', (event, d) => {
      const tooltipContent = d.data.description || '';
      d3.select(tooltip.value)
        .style('display', 'block')
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY + 10}px`)
        .html(tooltipContent);
    })
    .on('mouseout', () => {
      d3.select(tooltip.value).style('display', 'none');
    });

  // Store the old positions for transition.
  nodes.forEach(d => {
    d.x0 = d.x;
    d.y0 = d.y;
  });
}

function diagonal(s, d) {
  return `M ${s.y} ${s.x}
          C ${(s.y + d.y) / 2} ${s.x},
            ${(s.y + d.y) / 2} ${d.x},
            ${d.y} ${d.x}`;
}

function zoomed(event) {
  g.attr('transform', event.transform);
}

function onResize() {
  width.value = window.innerWidth;
  height.value = window.innerHeight;
  update(root);
}

// Expand the node and its immediate children
function expand(d) {
  if (d._children) {
    d.children = d._children;
    d._children = null;
  }
}

</script>

<style scoped>
.link {
  fill: none;
  stroke: #999;
  stroke-width: 1px;
}
</style>