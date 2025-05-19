<template>
    <navHeader></navHeader>
    <div class="main">
        <!-- //一些统计信息 -->
        <div class="stats shadow">

            <div class="stat">
                <div class="stat-figure text-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                        class="inline-block w-8 h-8 stroke-current">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z">
                        </path>
                    </svg>
                </div>
                <div class="stat-title">总量</div>
                <div class="stat-value text-secondary">{{ total_num }}</div>
                <div class="stat-desc">标注的总数量</div>
            </div>

            <div class="stat">
                <div class="stat-figure text-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                        class="inline-block w-8 h-8 stroke-current">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                </div>
                <div class="stat-title">工具数量</div>
                <div class="stat-value text-secondary">{{ tool_num }}</div>
                <div class="stat-desc">总得工具数量</div>
            </div>

            <div class="stat">
                <div class="stat-figure text-secondary">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                        class="inline-block w-8 h-8 stroke-current">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                </div>
                <div class="stat-title">Sample数量</div>
                <div class="stat-value text-secondary">{{ sample_num }}</div>
                <div class="stat-desc">问题样本数量</div>
            </div>
        </div>
        <!-- 这里进行绘图，展示统计结果 ，下面是控制按钮-->
        <div
            class='flex items-center flex-row justify-center h-20 from-teal-100 via-teal-200 to-teal-300 bg-gradient-to-br'>
            <div className="rounded-3xl m-4 text-center flex flex-row w-full ">
                <button type="button" @click="drawLabelCount"
                    class="text-white bg-[#25D366] hover:bg-green-500 focus:ring-4 focus:outline-none focus:ring-[#3b5998]/50 font-medium rounded-2xl  text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#3b5998]/55 mr-2 mb-2">
                    <div class='text-xl font-mono font-bold pt-0.5'>
                        标注数量统计
                    </div>
                </button>
            </div>
        </div>
        <!-- 绘图 -->
        <div id="labelCount" class="w-full h-96 my-10" v-show="show_labelCount"></div>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import navHeader from './navHeader.vue';
import * as echarts from 'echarts';
import { ElNotification } from 'element-plus';
import { getAllData, getAllNumber, getTools, getAllQuestion, deleteMessage, updateMessage, queryMessageData} from './api.ts'
const tableData = ref([]);
const total_num = ref(0); //总的标注数量
const tool_num = ref(0);
const sample_num = ref(0); //问题的数量
const show_labelCount = ref(false); //显示标注数量



async function drawLabelCount() {
    show_labelCount.value = true;
    const data = await getFullData()
    console.log(data)
    // 所有的prompt名称
    const all_prompts = data.map(item => item.prompt_name);
    //去重prompts
    const uniquePrompts = [...new Set(all_prompts)];
    //统计每个用户每个维度的数据的数量
    console.log("标注数量用到的prompts是：", uniquePrompts)
    const plot_data = {};
    for (let one of data) {
        for (let name of uniquePrompts) {
            if (!plot_data[name]) {
                plot_data[name] = 0;
            }
        };
        const prompt_name = one.prompt_name;
        if (uniquePrompts.includes(prompt_name)) {
            plot_data[prompt_name] += 1
        }
    }
    console.log("得到的标注数量统计绘图数据是：", plot_data);
    const label_name = Object.keys(plot_data);
    const label_value = Object.values(plot_data);
    plotLabelCount(label_name, label_value);
};

const plotLabelCount = (label_name, label_value) => {
    document.getElementById('labelCount').setAttribute('_echarts_instance_', '')
    var chartDom = document.getElementById('labelCount')
    var myChart = echarts.init(chartDom)
    const colors_mapers = ["red", "green", "blue", "yellow", "purple", "pink", "orange", "gray", "black", "brown", "cyan", "magenta", "olive", "lime", "teal", "navy", "fuchsia", "maroon", "aqua", "gold", "silver"]
    const data = label_value.map((item, index) => {
        return {
            value: item,
            itemStyle: {
                color: colors_mapers[index]
            }
        };
    });
    const option = {
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

async function getFullData() {
    try {
        const result = await getAllData({ mode: "full", limit: -1 });
        return result.data;
    } catch (error) {
        console.log(error);
    }
};

async function getTableData(limit) {
    const result = await getAllData({ mode: "sample", limit: limit });
    console.log(result);
    tableData.value = result.data;
}

onMounted(async () => {
    await getTableData(200);
    const number = await getAllNumber()
    total_num.value = number.data;
    const tools = await getTools()
    console.log(tools);
    tool_num.value = Object.keys(tools.data).length;
    const allQuestions = await getAllQuestion({ "keyword": "empty" });
    console.log(allQuestions)
    sample_num.value = allQuestions.data.length;
});
</script>

<style lang="scss" scoped></style>