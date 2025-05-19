<template>
    <div class="w-full h-80 border border-gray-100 overflow-auto bg-green-100" v-show="show_graph">
        <div id="plotContainer" class="w-full h-96 my-10"></div>
    </div>
</template>

<script setup>
//使用echarts绘图，根据不同的数据和要求绘制不同的图像
import { ref, onMounted, computed, watch, toRefs, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts';
import { ElNotification } from 'element-plus';
import { useMessageStore, useSettings } from './store.ts';
const { display_plot_meta } = toRefs(useMessageStore());
const show_graph = computed(() => {
    if (display_plot_meta.value) {
        return true;
    }
    return false;
});

watch(display_plot_meta, (newValue, oldValue) => {
    if (newValue) {
        //如果display_plot_meta有数据，那么开始绘图
        console.log("开始绘图", newValue);
        const info = newValue.info;
        const title = info.title
        const data = newValue.data;
        if (info["type"] === "bar") {
            drawBar(data, title)
        }else {
            ElNotification.warning("抱歉，暂不支持该类型的数据的绘图")
        }
    };
});

function drawBar(data, title) {
    console.log(data, title)
    // 所有的prompt名称
    const label_name = Object.keys(data);
    const label_value = Object.values(data);
    plotBarCount(label_name, label_value, title);
};

const plotBarCount = (label_name, label_value, title) => {
    document.getElementById('plotContainer').setAttribute('_echarts_instance_', '')
    var chartDom = document.getElementById('plotContainer')
    var myChart = echarts.init(chartDom)
    const colors_mapers = ["red", "green", "blue", "yellow", "purple", "pink", "orange", "gray", "black", "brown", "cyan", "magenta", "olive", "lime", "teal", "navy", "fuchsia", "maroon", "aqua", "gold", "silver"]
    const data = label_value.map((item, index) => {
        return {
            value: item,
            itemStyle: {
                color: colors_mapers[index % colors_mapers.length]
            }
        };
    });
    const option = {
        title: {
            text: title,
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                // Use axis to trigger tooltip
                type: 'shadow' // 'shadow' as default; can also be 'line' or 'shadow'
            }
        },
        legend: {},
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value'
        },
        yAxis: {
            type: 'category',
            data: label_name
        },
        series: [
            {
                name: '统计',
                type: 'bar',
                stack: 'total',
                label: {
                    show: true
                },
                emphasis: {
                    focus: 'series'
                },
                data: data
            },
        ]
    };
    option && myChart.setOption(option)
    window.onresize = () => {
        myChart.resize()
    }
};

</script>

<style lang="scss" scoped></style>