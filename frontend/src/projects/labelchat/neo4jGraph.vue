<template>
    <div class="w-full h-full border border-gray-100 overflow-auto bg-slate-500" v-show="show_graph">
        <div class="display_header flex justify-between items-center">
            <!-- 显示一些属性信息 -->
            <div class="properties w-full h-10 text-white">
            </div>
            <div class="form-control">
                <label class="cursor-pointer label">
                    <input type="checkbox" class="checkbox checkbox-info" v-model="boxSelect"
                        title="开启选择模式,ctrl+a快速开启" />
                </label>
            </div>
        </div>
        <!-- 显示知识图谱 -->
        <div class="knowledgeGraph" tabindex="0" @keydown.ctrl.a="toggleBoxSelect"></div>
    </div>
</template>

<script setup>
//用于绘制meta中返回的知识信息
//特点，点击节点后会查找后台该节点相关连的关系，然后重新刷新图谱
//鼠标放到节点上，节点会发光，同时左上角显示该节点的属性
//节点点击后该节点的边会变一下颜色，例如红色，然后恢复
//可以进行拖动节点和缩放知识图谱
//节点之间的关系有方向，并配有箭头
//节点之间的关系上显示关系的属性name,例如显示积极，消极,中性
import { ref, onMounted, computed, watch, toRefs, onBeforeUnmount } from 'vue'
import lodash from 'lodash'
import { useMessageStore, useSettings } from './store.ts';
import { queryNeo4j } from './api.ts'
const { display_neo4j_meta, select_nodes } = toRefs(useMessageStore());
import * as d3 from 'd3'
const boxSelect = ref(false);
const show_graph = computed(() => {
    if (display_neo4j_meta.value) {
        return true;
    }
    return false;
});

watch(select_nodes, (newValue, oldValue) => {
    console.log("select_nodes发生变化", newValue);
}, {deep:true});

const toggleBoxSelect = () => {
    boxSelect.value = !boxSelect.value;
    console.log("框选状态已切换！");
};

watch(display_neo4j_meta, (newValue, oldValue) => {
    if (newValue) {
        //如果display_neo4j_meta有数据，那么开始绘图
        console.log("开始绘图", newValue);
        const { nodes, links } = getNodeLinks(newValue);
        renderKG(nodes, links)
    };
});


function getNodeLinks(data) {
    //根据data中的数据，生成节点和边
    let node_ids = []; //用于去重
    let nodes = [];
    let links = [];
    data.forEach(item => {
        item.nodes.forEach(node => {
            //把不重复的放到nodes中
            if (!node_ids.includes(node.id)) {
                nodes.push(node);
                node_ids.push(node.id);
            };
        });
        links.push(item.links);
    });

    //这行代码创建了一个包含节点和链接信息的对象data。节点信息是从source_data中的source和target属性中提取的不重复值，链接信息则直接使用了source_data。
    console.log(new Date(), "节点信息", nodes)
    console.log(new Date(), "link信息", links)
    return { nodes, links };
};

function renderKG(nodes, links) {
    let nodesCopy = lodash.cloneDeep(nodes);
    let linksCopy = lodash.cloneDeep(links);

    function find_color(id) {
        //根据节点的id，返回节点的颜色，使用nodesCopy的数据，如果没有找到，返回黄色
        const color = nodesCopy.find(node => node.id === id)?.color || 'yellow';
        return color;
    };

    //渲染图表，根据data中的数据
    console.log(new Date(), `数据获取完成，共获取了${nodes.length}条节点数据，开始渲染`)
    console.log(new Date(), "nodesCopy", nodesCopy)
    console.log(new Date(), "linksCopy", linksCopy)
    //开始进行绘图
    let propertyTips = d3.select(".properties"); //用于显示属性信息
    const width = 928;
    const height = 680;
    //这是一个用于创建链接路径的函数，根据输入的链接数据d来生成路径的描述。
    //函数返回一个包含 SVG 路径字符串的模板字面量。路径字符串使用 M 命令指定起点的坐标，A 命令指定弧形路径的参数，其中包括半径 r、大型弧标志、顺时针方向标志以及终点的坐标。
    // 使用圆弧的画法代替直线，修改r就可以就该弧的半径，如果弧线的半径为0，就是直线了
    //2个节点之间的连线
    function linkArc(d) {
        const r = 0;
        // Math.hypot(d.target.x - d.source.x, d.target.y - d.source.y);
        return `
      M${d.source.x},${d.source.y}
      A${r},${r} 0 0,1 ${d.target.x},${d.target.y}
    `;
    }
    //一个用于定义拖拽行为的函数，返回一个D3拖拽对象，定义一个拖动函数
    const drag = simulation => {
        function dragStarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragEnded(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded);
    }
    //段代码使用D3的力导向图布局来创建一个模拟器，用于模拟节点之间的作用力。不错，现在显示完美了
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-2000))  // 调低这个值使得节点间的排斥力适中
        .force("x", d3.forceX(width / 2))  //沿 x 轴朝向给定位置 x 创建新的位置力
        .force("y", d3.forceY(height / 2))  //沿 y 轴朝向给定位置 y 创建新的位置力
        .force("link", d3.forceLink(links).id(d => d.id).distance(200)); //连线的力（link），以帮助把节点拉开一些距离
    // .force("center", d3.forceCenter(width / 2, height / 2)); // 新增一个居中的力使所有节点都能更好地在圆形区域内分布， 加上中心力就拖不动了


    const svg = d3.create("svg")
        .attr("viewBox", [-width / 2, -height / 2, width * 2, height * 2])
        .style("font", "10px sans-serif");

    // 添加这段代码来初始化一个 zoom 行为
    const zoom = d3.zoom()
        .scaleExtent([-5, 5]) // 设置最小和最大缩放范围
        .on("zoom", function (event) {
            svg.selectAll('g').attr("transform", event.transform); // 将当前变换应用到所有的 g 元素
            svg.selectAll('g').selectAll('g').attr("transform", event.transform); //所有g元素下的g元素也进行变换
        });
    //zoom的启用与否和框选有关，当使用框选时，禁用zoom    
    // 添加这段代码使 svg 的所有内容都在一个 g 元素下
    //------------设定节点的阴影代码--------------------
    const root = svg.append("g")
    const defs = root.append("defs");  // 添加定义元素

    const filter = defs.append("filter")
        .attr("id", "glow");  // 给滤镜设定一个唯一的ID

    filter.append("feGaussianBlur")
        .attr("stdDeviation", "5") // 设定模糊效果
        .attr("result", "coloredBlur");

    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    //------------设定节点的之间的连线代码--------------------
    const link = root.selectAll("path")
        .data(links)
        .join("path")
        .attr("fill", "none")
        .attr("stroke-width", 2.5)
        .attr("stroke", "pink")
        .attr("marker-end", d => `url(${new URL(`#arrow-${d.type}`, location)})`)
        .attr("id", (d, i) => `linkPath${i}`)
        .on("mouseover", function (event, d) {
            d3.select(this).style("filter", "url(#glow)");  // 在mouseover事件中，给节点应用滤镜
            propertyTips.html(`类型: ${d.relation_type}`)  // 在这里设置你想展示的信息，如ID
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .style("opacity", 1);  // 将 tooltip 设为可见
        })
        .on("mouseout", function () {
            d3.select(this).style("filter", "none");  // 在mouseout事件中，去除滤镜效果
            propertyTips.style("opacity", 0);  // 在mouseout事件中，将 tooltip 设为不可见
        });
    // 创建连线中间的关系文字，再添加链接文字
    const linkText = root
        .selectAll(".link-text")
        .data(links)
        .join("text")
        .attr("class", "link-text")
        .append("textPath")
        .attr("startOffset", "50%")
        .attr("fill", "white")
        .attr("xlink:href", (d, i) => `#linkPath${i}`)  // 引用对应的 path
        .text(d => d.relation);

    // 用于在SVG中创建标记（marker），用于表示链接的箭头。https://developer.mozilla.org/en-US/docs/Web/SVG/Element/marker
    root.selectAll("marker")
        .data(links)
        .join("marker")
        .attr("id", d => `arrow-${d.type}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 25) //refX" 属性设定了箭头的参考点相对于“markerUnits”坐标系统原点沿 x 轴方向的距离，偏移量越大箭头与连接线的末端距离就越远。"refY" 属性设定了箭头的参考点相对于“markerUnits”坐标系统原点沿 y 轴方向的距离，通常设为 0 就可以了。
        .attr("refY", -0.5)
        .attr("markerWidth", 10)
        .attr("markerHeight", 10)
        .attr("orient", "auto")
        .append("path")
        .attr("fill", "#add8e6")  //淡蓝色箭头
        .attr("d", "M0,-5L10,0L0,5");  //绘制箭头形状

    //创建了节点的SVG元素，并设置了节点的样式和拖拽行为。
    const node = root
        .selectAll("a")
        .data(nodes)
        .join("a")
        .on("mouseover", function (event, d) {
            d3.select(this).style("filter", "url(#glow)");  // 在mouseover事件中，给节点应用滤镜
            propertyTips.html(`名称: ${d.name}, 类型: ${d.node_type}`)  // 在这里设置你想展示的信息，如ID
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .style("opacity", 1);  // 将 tooltip 设为可见
        })
        .on("mouseout", function () {
            d3.select(this).style("filter", "none");  // 在mouseout事件中，去除滤镜效果
            propertyTips.style("opacity", 0);  // 在mouseout事件中，将 tooltip 设为不可见
        })
        .on("mousedown", function () {
            d3.select(this).select("circle").style("stroke", "red"); //改变点击节点边框颜色
        })
        .on("mouseup", function () {
            d3.select(this).select("circle").style("stroke", "white"); //恢复点击节点边框颜色
        })
        .on("click", async function (event, d) {
            // 在这里发请求，利用 d 中的数据作为 API 的参数，如果不报错，节点边框颜色会恢复
            const result = await queryNeo4j({ property_name: "id", property_value: d.id })
            console.log("查询结果", result)
            if (result.code === 0 && result.data.length > 0) {
                const { nodes: current_nodes, links: current_links } = getNodeLinks(result.data);
                console.log("current_nodes", current_nodes);
                // 合并时需要检查node是否重复，则不添加
                const merge_nodes = [...nodesCopy]
                current_nodes.forEach(node => {
                    const existNode = merge_nodes.find(n => n.id === node.id);
                    if (!existNode) {
                        merge_nodes.push(node);
                    }
                });
                if (merge_nodes.length > nodesCopy.length) {
                    console.log("有新的节点加入，需要重新渲染")
                    const merge_links = current_links.concat(linksCopy);
                    renderKG(merge_nodes, merge_links); //重新渲染
                };
            };
            d3.select(this).select("circle").style("stroke", "white"); //恢复点击节点边框颜色
        });

    node.append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1.5)
        .data(nodes)
        .attr("r", 40)
        .attr("fill", d => d.color);

    node.append("text")
        .text(d => d.id)
        .attr('text-anchor', 'middle')  //文本在起始点的中间
        .attr('dominant-baseline', 'middle') //字在x和y的中间
        .attr("fill", "#483D8B")
        .attr("stroke", "#483D8B")
        .attr("stroke-width", 1);
    //模拟器更新时的回调函数，用于更新链接和节点的位置。
    simulation.on("tick", () => {
        // 更新连接线的位置
        link.attr("d", linkArc);
        node.attr("transform", d => `translate(${d.x},${d.y})`);
    });
    //----------------框选的相关代码----------------
    // 添加一个矩形作为框选的背景
    const brush = () => {
        // 用于改变框选中节点的颜色
        let brushColor = "darkorange";

        // highlightNodes 函数为被框选中的节点改变颜色
        function highlightNodes(event) {
            let selection = event.selection;
            //node的节点颜色是使用的circle组件改变的，所以这里仍然需要使用circle组件的fill属性来改变颜色
            node.select("circle").style("fill", function (d) {
                //return函数进行拆解
                if (selection !== null
                    && selection[0][0] <= d.x && d.x < selection[1][0]
                    && selection[0][1] <= d.y && d.y < selection[1][1]) {
                    //框中的节点，把id放到select_nodes里面
                    if (select_nodes.value.includes(d.id) === false){
                        select_nodes.value.push(d.id);
                    }
                    return brushColor;
                }
                else {
                    return find_color(d.id);
                }
            });
        }

        //当随便单击1个框外的其它点的时候，所有节点应该恢复原有的颜色
        function persistHighlight(event) {
            if (event.selection !== null) return;
            node.select("circle").style("fill", d => find_color(d.id));
        }
        return d3.brush()
            .on("start brush", highlightNodes)
            .on("end", persistHighlight);
    };

    function OpenOrCloseBoxSelect(boxBoolean) {
        if (boxBoolean) {
            //开启框选
            node.on('.drag', null);  // 移除拖拽事件
            //禁用zoom缩放行为
            svg.on('.zoom', null);
            svg.append("g")
                .attr("class", "brush")
                .call(brush());  // 在 svg "g" 中创建框选
        } else {
            svg.select(".brush").remove();  // 清除框选
            node.call(drag(simulation));
            // 启用zoom
            svg.call(zoom);
        }
    }
    //初始化的时候，默认的是否开启框选
    OpenOrCloseBoxSelect(boxSelect.value)
    //----------------箭头框选按钮的状态，对框选进行切换----------------
    watch(boxSelect, (newValue) => {
        OpenOrCloseBoxSelect(newValue)
    });

    d3.select(".knowledgeGraph").select("svg").remove(); //删除旧的svg
    d3.select(".knowledgeGraph").append(() => svg.node());
};

</script>

<style lang="scss" scoped></style>