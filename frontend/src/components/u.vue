<template>
    <div class="relative w-full h-screen bg-gray-50">
        <svg ref="svg" class="w-full h-full">
            <defs>
                <marker id="arrowhead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6"
                    orient="auto">
                    <path d="M 0 0 L 10 5 L 0 10 z" class="fill-gray-400" />
                </marker>
            </defs>
        </svg>
        <div ref="tooltip"
            class="absolute pointer-events-none bg-white p-2 rounded shadow-lg border border-gray-200 text-sm opacity-0 transition-opacity duration-200">
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';

interface Node {
    id: string;
    name: string;
    description?: string;
    children?: Node[];
}

const props = defineProps<{
    data: Node;
}>();

const svg = ref<SVGElement | null>(null);
const tooltip = ref<HTMLDivElement | null>(null);
const width = ref(window.innerWidth);
const height = ref(window.innerHeight);

let root: d3.HierarchyNode<Node>;
let g: d3.Selection<SVGGElement, unknown, null, undefined>;

const zoom = d3.zoom<SVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
        g.attr('transform', event.transform);
    });

function diagonal(d: any) {
    return `M ${d.source.y} ${d.source.x}
          C ${(d.source.y + d.target.y) / 2} ${d.source.x},
            ${(d.source.y + d.target.y) / 2} ${d.target.x},
            ${d.target.y} ${d.target.x}`;
}

function showTooltip(event: MouseEvent, d: d3.HierarchyNode<Node>) {
    if (!tooltip.value || !d.data.description) return;

    const tooltipElement = d3.select(tooltip.value);
    tooltipElement
        .style('opacity', 1)
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY - 10}px`)
        .html(d.data.description);
}

function hideTooltip() {
    if (!tooltip.value) return;
    d3.select(tooltip.value).style('opacity', 0);
}

function toggleNode(event: MouseEvent, d: d3.HierarchyNode<Node>) {
    event.stopPropagation();
    if (!d.children && d._children) {
        d.children = d._children;
        d._children = null;
    } else if (d.children) {
        d._children = d.children;
        d.children = null;
    }
    update(d);
}

function update(source: d3.HierarchyNode<Node>) {
    const duration = 750;
    const nodeSpacing = 180;
    const levelWidth = width.value - 200;

    const treeLayout = d3.tree<Node>()
        .nodeSize([nodeSpacing, levelWidth / 2]);

    treeLayout(root);

    const nodes = root.descendants();
    const links = root.links();

    // Normalize for fixed-depth
    nodes.forEach(d => {
        d.y = d.depth * 180;
    });

    // Update links
    const link = g.selectAll('.link')
        .data(links, (d: any) => d.target.id);

    const linkEnter = link.enter()
        .append('path')
        .attr('class', 'link')
        .attr('d', d3.linkHorizontal()
            .x((d: any) => d.y)
            .y((d: any) => d.x))
        .attr('fill', 'none')
        .attr('stroke', '#999')
        .attr('stroke-width', 1.5);

    // Transition links to their new position
    link.merge(linkEnter)
        .transition()
        .duration(duration)
        .attr('d', d3.linkHorizontal()
            .x((d: any) => d.y)
            .y((d: any) => d.x));

    // Transition exiting links
    link.exit()
        .transition()
        .duration(duration)
        .attr('d', d3.linkHorizontal()
            .x((d: any) => d.y)
            .y((d: any) => d.x))
        .remove();

    // Update nodes
    const node = g.selectAll('g.node')
        .data(nodes, (d: any) => d.id || (d.id = ++i));

    // Enter new nodes
    const nodeEnter = node.enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', () => `translate(${source.y0 || source.y},${source.x0 || source.x})`)
        .on('click', toggleNode)
        .on('mouseover', showTooltip)
        .on('mouseout', hideTooltip);

    nodeEnter.append('circle')
        .attr('r', 6)
        .attr('class', 'node-circle')
        .attr('fill', d => d.children || d._children ? '#60A5FA' : '#34D399');

    nodeEnter.append('text')
        .attr('dy', '.31em')
        .attr('x', d => d.children || d._children ? -10 : 10)
        .attr('text-anchor', d => d.children || d._children ? 'end' : 'start')
        .text(d => d.data.name)
        .attr('class', 'text-sm fill-gray-700');

    // Update nodes to new positions
    const nodeUpdate = node.merge(nodeEnter)
        .transition()
        .duration(duration)
        .attr('transform', d => `translate(${d.y},${d.x})`);

    nodeUpdate.select('circle')
        .attr('fill', d => d.children || d._children ? '#60A5FA' : '#34D399');

    // Remove any exiting nodes
    const nodeExit = node.exit()
        .transition()
        .duration(duration)
        .attr('transform', () => `translate(${source.y},${source.x})`)
        .remove();

    nodeExit.select('circle')
        .attr('r', 0);

    // Store the old positions for transition
    nodes.forEach(d => {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}


let i = 0; // Used for generating unique IDs

onMounted(() => {
    const svgElement = d3.select(svg.value);

    g = svgElement.append('g')
        .attr('transform', 'translate(100,50)');

    svgElement.call(zoom as any);

    root = d3.hierarchy(props.data) as any;
    root.x0 = height.value / 2;
    root.y0 = 0;

    // Collapse all nodes initially except the root
    root.descendants().forEach(d => {
        if (d.depth > 0 && d.children) {
            d._children = d.children;
            d.children = null;
        }
    });

    update(root);
});

watch(() => props.data, (newData) => {
    root = d3.hierarchy(newData) as any;
    root.x0 = height.value / 2;
    root.y0 = 0;
    update(root);
});

// Handle window resize
window.addEventListener('resize', () => {
    width.value = window.innerWidth;
    height.value = window.innerHeight;
    update(root);
});
</script>

<style scoped>
.link {
    fill: none;
    stroke: #CBD5E1;
    stroke-width: 0.1px;
    marker-end: url(#arrowhead);
}

.node-circle {
    stroke: white;
    stroke-width: 2px;
    cursor: pointer;
}

.node text {
    font-family: system-ui, -apple-system, sans-serif;
}
</style>