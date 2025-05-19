<template>
  <div id="chart"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import axios from 'axios';

function Pack(data, {
    value,
    label,
    title,
    link,
    width = 1152,
    height = 1152,
    margin = 1,
    padding = 3,
} = {}) {
    // ... 保持原有的数据处理逻辑 ...
    const root = d3.hierarchy(data)
        .sum(d => d.size)
        .sort((a, b) => b.value - a.value);

    // 计算布局
    d3.pack()
        .size([width - margin * 2, height - margin * 2])
        .padding(padding)
        (root);

    const color = d3.scaleLinear()
        .domain([0, 5])
        .range(["hsl(152,80%,80%)", "hsl(228,30%,40%)"])
        .interpolate(d3.interpolateHcl)

    const svg = d3.create("svg")
        .attr("viewBox", [0, 0, width, height])
        .attr("width", width)
        .attr("height", height)
        .style("background", color(0))
        .style("cursor", "pointer");

    // 添加缩放功能的容器
    const g = svg.append("g");

    // 创建节点
    const node = g.selectAll("g")
        .data(root.descendants())
        .join("g")
        .attr("transform", d => `translate(${d.x},${d.y})`);

    // 添加圆形
    node.append("circle")
        .attr("fill", d => d.children ? color(d.depth) : "white")
        .attr("fill-opacity", d => d.children ? 1 : 0.7)
        .attr("r", d => d.r);

    // 添加文本标签
    const leaf = node.filter(d => !d.children && d.r > 10);
    leaf.append("text")
        .selectAll("tspan")
        .data(d => `${d.data.name}`.split(/(?=[A-Z][a-z])/g))
        .join("tspan")
        .attr("x", 0)
        .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.8}em`)
        .text(d => d);

    // 添加缩放功能
    const zoom = d3.zoom()
        .scaleExtent([1, 8])
        .on("zoom", zoomed);

    function zoomed(event) {
        g.attr("transform", event.transform);
    }

    svg.call(zoom);

    // 双击节点时缩放到该节点
    node.on("dblclick", (event, d) => {
        event.stopPropagation();
        const scale = height / (d.r * 2);
        const translate = [width / 2 - d.x * scale, height / 2 - d.y * scale];
        
        svg.transition()
            .duration(750)
            .call(zoom.transform, 
                d3.zoomIdentity
                    .translate(translate[0], translate[1])
                    .scale(scale)
            );
    });

    return svg.node();
}

async function fetchData(url) {
    try {
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        throw error;
    }
}

onMounted(async () => {
    const flare = await fetchData('http://127.0.0.1:8080/flare.json');
    const chart = Pack(flare, {
        width: 1152,
        height: 1152
    });
    d3.select('#chart').append(() => chart);
});
</script>

<style scoped>
#chart {
    width: 100%;
    height: 100%;
}

text {
    font-family: sans-serif;
    font-size: 10px;
    text-anchor: middle;
    pointer-events: none;
}
</style>