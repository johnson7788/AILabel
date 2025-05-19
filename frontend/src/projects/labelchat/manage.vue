<template>
    <navHeader></navHeader>
    <div>
        <div class="main my-6 flex ml-2">
            <button class="btn btn-outline btn-accent" @click="clearDatabase">清空标注数据库</button>
            <button class="btn btn-outline btn-accent" @click="exportDatabase">导出标注数据</button>
            <button class="btn btn-outline btn-accent" @click="backupDatabase">备份mongo</button>
        </div>
        <!-- 数据导出多选prompt -->
        <div class="main flex border rounded-xl overflow-hidden my-4 flex-wrap">
            <div class="title py-3 my-auto px-5 bg-green-400 text-white text-sm font-semibold mr-3 hover:bg-green-700 cursor-pointer"
                @click="downloadData" title="下载选中的prompt的数据">下载</div>
            <label class="flex p-2 cursor-pointer" v-for="(option, index) in prompts" :key="option">
                <input class="my-auto transform scale-125" type="checkbox" name="sfg" v-model="selectPrompts"
                    :value="option" />
                <div class="title px-2">{{ option }}</div>
            </label>
        </div>
        <!-- 模型多选 -->
        <div class="main flex flex-wrap flex-row  border rounded-full overflow-hidden my-4">
            <div class="title py-3 my-auto px-5 bg-blue-400 text-white text-sm font-semibold mr-3 hover:bg-blue-700 cursor-pointer"
                @click="toggleLLM" title="红色表示异常，绿色表示正常">LLM</div>
            <label class="flex p-2 cursor-pointer" v-for="(option, index) in llm_list" :key="option.name">
                <input class="my-auto transform scale-125" type="checkbox" name="sfg" v-model="selectedLLM"
                    :value="option.name" />
                <div class="title px-2"
                    :class="{   'text-red-500': option.status === 'error', 'text-green-500': option.status === 'ok' }">{{
                option.name }}</div>
            </label>
        </div>
        <!-- 是否使用模型缓存的开关 -->
        <div class="flex items-center m-2 cursor-pointer cm-toggle-wrapper mb-6">
            <span class="font-semibold text-xs mr-1">
                是否使用模型缓存：
            </span>
            <el-switch v-model="usecache" />
            <span class="font-semibold text-xs ml-6 mr-1">
                是否采样数据去重已标注：
            </span>
            <el-switch v-model="norepeat" />
        </div>
        <!-- 更改菜单的链接 -->
        <div class="flex flex-row items-center">
            <p class="ml-4">标注配置: </p>
            <label v-for="(value, key) in label2page">
                <input type="radio" :value="key" class="peer hidden" :name="key" v-model="defaultLabel" />
                <div
                    class="hover:bg-gray-50 flex items-center justify-between px-3 py-1 border-2 rounded-lg cursor-pointer text-sm border-gray-200 group peer-checked:border-blue-500">
                    <h2 class="font-medium text-gray-700">{{ key }}</h2>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-9 h-9 text-blue-600 invisible group-[.peer:checked+&]:visible">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
            </label>
        </div>
        <div class="divider"></div>
        <div class="flex flex-row justify-between items-center ml-2">
            <select class="select select-bordered w-full max-w-xs" v-model="selectedSample">
                <option disabled selected>使用哪个Sample</option>
                <option v-for="item in all_questions"> {{ item.prompt }}</option>
            </select>
            <div>问题序号: {{ sample_idx }} / {{ total_question_num }}</div>
            <input class="rounded-lg overflow-hidden appearance-none bg-gray-400 h-3 w-1/4" type="range" min=0
                :max="total_question_num" step="1" v-model="sample_idx" />
        </div>
        <div class="divider"></div>
        <p class="text-2xl text-green-800 text-center">可用tools函数展示:</p>
        <div class="p-24 flex flex-wrap items-center justify-center">
            <div class="flex-shrink-0 m-6 relative overflow-hidden bg-slate-200 rounded-lg max-w-xs shadow-lg"
                v-for="(value, key) in tools_data" :key="key">
                <svg class="absolute bottom-0 left-0 mb-8" viewBox="0 0 375 283" fill="none"
                    style="transform: scale(1.5); opacity: 0.1;">
                    <rect x="159.52" y="175" width="152" height="152" rx="8" transform="rotate(-45 159.52 175)"
                        fill="white" />
                    <rect y="107.48" width="152" height="152" rx="8" transform="rotate(-45 0 107.48)" fill="white" />
                </svg>
                <div class="relative pt-4 px-6 flex items-center justify-center">
                    <div class="block absolute w-48 h-48 bottom-0 left-0 -mb-24 ml-3"
                        style="background: radial-gradient(black, transparent 60%); transform: rotate3d(0, 0, 1, 20deg) scale3d(1, 0.6, 1); opacity: 0.2;">
                    </div>
                </div>
                <div class="relative text-black px-6 pb-6 mt-6">
                    <span class="block opacity-75 -mb-1 text-center text-2xl text-green-600">{{ key }}</span>
                    <div class="flex justify-between">
                        <span class="block font-semibold text-sm">{{ value }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, toRefs, watch } from 'vue';
import navHeader from './navHeader.vue';
import { ElNotification } from 'element-plus';
import { clearAllData, getAllData, getTools, exportAllData, getLLM, getAllQuestion, backupMongo } from './api.ts'
import { useSettings } from './store.ts';
const { selectedLLM, selectedSample, sample_idx, usecache, norepeat,label2page, defaultLabel } = toRefs(useSettings());
const llm_list = ref([]);
const tools_data = ref([]);
const all_questions = ref([]);
const total_question_num = ref(0);
const prompts = ref([]);  //用于数据下载，这里存储所有标注过的数据的prompts
const selectPrompts = ref([]);  //用于数据下载，选中的prompts有哪些
const all_label_data = ref(null);

watch(selectedSample,(newVal, oldVal) => {
    //更细total_question_num, 根据all_questions中prompt等于newVal的中的内容来筛选
    total_question_num.value = all_questions.value.filter(item => item.prompt === newVal)[0].number;
    console.log("total_question_num", total_question_num.value);
    sample_idx.value = 0; //如果改变，那么自动切换到第一条
});

async function downloadData() {
    console.log("下载数据，prompts包括", selectPrompts);
    //根据selectPrompts过滤数据all_label_data
    const filtered_data = all_label_data.value.filter(item => selectPrompts.value.includes(item.prompt_name));
    const jsonData = JSON.stringify(filtered_data, null, 2); //该方法生成格式化的JSON字符串。

    const blob = new Blob([jsonData], { type: 'application/json' }); //新建BLOB对象
    const url = URL.createObjectURL(blob); // 使用URL.createObjectURL方法生成BLOB的URL

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'output.json'); //为下载的文件设置名称

    document.body.appendChild(link);

    link.click(); //模拟链接点击，开始下载

    document.body.removeChild(link); //完成下载后，删除创建的链接
}

function toggleLLM() {
    //双击切换全选和取消全选LLM
    for (let llm of llm_list.value) {
        if (selectedLLM.value.includes(llm.name)) {
            const index = selectedLLM.value.indexOf(llm.name);
            selectedLLM.value.splice(index, 1);
        } else {
            if (llm.status === 'ok') {
                selectedLLM.value.push(llm.name);
            }
        }
    }
};

async function clearDatabase() {
    //清空数据库
    console.log('清空数据库');
    await clearAllData()
    const result = await getAllData({ "mode": "detail" })
    const data_length = result.data.length
    if (data_length === 0) {
        ElNotification({
            message: `清空数据库成功`,
            type: 'info',
        });
    } else {
        ElNotification({
            message: `清空数据库失败，还剩余 ${data_length} 条数据`,
            type: 'error',
        });
    }
}

async function exportDatabase() {
    const result = await exportAllData()
    ElNotification({
        message: `导出数据成功，请查看导出文件: ${result.data}`,
        type: 'info',
    });
}

async function backupDatabase() {
    const result = await backupMongo()
    ElNotification({
        message: `备份mongo数据成功，请查看导出文件: ${result.data}`,
        type: 'info',
    });
}


onMounted(async () => {
    const tools = await getTools()
    console.log(tools);
    tools_data.value = tools.data;
    const llm_res = await getLLM()
    console.log("llm_res", llm_res);
    llm_list.value = llm_res.data;
    const Questions = await getAllQuestion({ "keyword": "empty", "namelength": true });
    all_questions.value = Questions.data;
    console.log(all_questions.value)
    if (selectedSample.value !== "") {
        total_question_num.value = all_questions.value.filter(item => item.prompt === selectedSample.value)[0].number;
    }
    const all_data = await getAllData({ mode: "detail", limit: -1 });
    all_label_data.value = all_data.data;
    //获取所有prompt
    console.log(all_data);
    const all_prompts = all_data.data.map(item => item.prompt_name);
    //去重prompts
    const uniquePrompts = [...new Set(all_prompts)];
    prompts.value = uniquePrompts
});

</script>

<style lang="scss" scoped></style>