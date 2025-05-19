<template>
    <div class="w-full h-96 border border-gray-100 bg-green-100">
        <div ref="plotBarContainer" class="w-full h-96 my-10"></div>
    </div>
</template>

<script setup>
//使用echarts绘图，根据不同的数据和要求绘制不同的图像, 画1个柱状图
import { ref, onMounted, computed, watch, toRefs, defineProps } from 'vue'
import * as echarts from 'echarts';
import { ElNotification } from 'element-plus';
const plotBarContainer = ref(null);
let props = defineProps({
    dataProps: {
        type: Object,
        required: true,
        default: {
            "data": { 'Mon': 120, 'Tue': 200, 'Wed': 150, 'Thu': 80, 'Fri': 70, 'Sat': 110, 'Sun': 130 },
            "info": {
                "title": "测试统计bar图",
                "type": "Bar",
            }
        }
    }
});

const plotBarCount = (label_name, label_value, title) => {
    var myChart = echarts.init(plotBarContainer.value)
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

onMounted(() => {
    const xlabel = Object.keys(props.dataProps.data);
    const xvalue = Object.values(props.dataProps.data);
    const title = props.dataProps.info.title;
    plotBarCount(xlabel, xvalue, title);
});

</script>

<style lang="scss" scoped></style>