<template>
    <navHeader></navHeader>
    <div class="main">
        <div class="rounded-t mb-0 px-4 py-3 border-0">
            <div class="flex flex-wrap items-center">
                <div class="relative w-full px-1 max-w-full flex-grow flex-1">
                    <h3 class="font-semibold text-base text-blueGray-700 center">为了不卡顿，初始仅显示最后200条数据，点击按钮获可以取所有数据</h3>
                </div>
                <div class="relative w-full px-4 max-w-full flex-grow flex-1 text-right">
                    <button
                        class="bg-indigo-400 text-white active:bg-indigo-600 text-xs font-bold uppercase px-4 py-3 rounded outline-none focus:outline-none mr-1 mb-1 ease-linear transition-all duration-150"
                        type="button" @click="getTableData(-1)">获取所有数据</button>
                </div>
            </div>
            <div class="container bg-slate-600 mx-auto rounded-lg">
                <form>
                    <div class="sm:flex items-center bg-white rounded-lg overflow-hidden px-2 py-1 justify-between">
                        <input class="text-base text-gray-400 flex-grow outline-none px-2 " type="text" v-model="searchWord"
                            placeholder="搜索已标注数据" />
                        <div class="ms:flex items-center px-2 rounded-lg space-x-4 mx-auto ">
                            <select id="field" class="text-base text-gray-800 outline-none border-2 px-4 py-2 rounded-lg" v-model="selectedField">
                                <option value="all" selected>all</option>
                                <option value="prompt_name">prompt_name</option>
                                <option value="prompt">prompt</option>
                                <option value="tools">tools</option>
                                <option value="messages">messages</option>
                            </select>
                            <button @click.prevent="SearchData"
                                class="bg-indigo-500 text-white text-base rounded-lg px-4 py-2 font-thin">搜索</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <el-table :data="tableData" style="width: 100%" class="mt-10">
            <el-table-column prop="id" label="id" width="150" />
            <el-table-column prop="time" label="time" width="150" />
            <el-table-column prop="prompt_name" label="prompt_name" width="150" />
            <el-table-column prop="prompt" label="prompt" width="150" />
            <el-table-column prop="tools_concat" label="tools_concat" width="150" />
            <el-table-column prop="messages_concat" label="messages_concat" width="700" />
            <el-table-column fixed="right" label="Operations" width="120">
                <template #default="scope">
                    <el-button link type="primary" size="small"
                        @click.prevent="startModify(scope.$index)">修改</el-button>
                    <el-button link type="primary" size="small"
                        @click.prevent="deleteOneMessage(scope.$index)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        <!-- drawer 侧边栏,用于修改数据 -->
        <nav class="fixed z-20 h-screen w-1/4 bg-green-200 p-8 right-0 top-0 overflow-auto" v-show="showSidenav"
            x-transition:enter="transition ease-out duration-300" x-transition:enter-start="-translate-x-72"
            x-transition:enter-end="translate-x-0" x-transition:leave="transition ease-in duration-300 "
            x-transition:leave-start="translate-x-0" x-transition:leave-end="-translate-x-72" x-cloak>
            <div class="h-screen">
                <button @click="showSidenav = false">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="black" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
                <label class="form-control w-full max-w-xs mb-6">
                    <div class="label">
                        <span class="label-text">Prompt name</span>
                    </div>
                    <input type="text" v-model="modifiedMessage.prompt_name" placeholder="Type here"
                        class="input input-bordered w-full max-w-xs" />
                </label>
                <label class="form-control w-full max-w-xs mb-6">
                    <div class="label">
                        <span class="label-text">Prompt</span>
                    </div>
                    <input type="text" v-model="modifiedMessage.prompt" placeholder="Type here"
                        class="input input-bordered w-full max-w-xs" />
                </label>
                <label class="form-control w-full max-w-xs mb-6" v-for="(message, index) in modifiedMessage.messages"
                    :key="index">
                    <div class="label">
                        <span class="label-text">{{ message.role }}: {{ message.id }}</span>
                    </div>
                    <textarea type="text" v-model="message.content" placeholder="Type here"
                        class="input input-bordered w-full max-w-xs" />
                </label>
                <label class="form-control w-full max-w-xs mb-6" v-for="(tool, index) in modifiedMessage.tools"
                    :key="index">
                    <div class="label">
                        <span class="label-text">{{ tool.description }}</span>
                    </div>
                    <input type="text" v-model="tool.name" placeholder="Type here"
                        class="input input-bordered w-full max-w-xs" />
                </label>
                <div class="flex justify-center pb-10">
                    <button class="btn btn-outline btn-info mt-6" @click="updateOneMessage">确认</button>
                </div>
            </div>
        </nav>
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
const showSidenav = ref(false);
const modifiedMessage = ref({
    "prompt": "",
    "prompt_name": "",
    "messages": "",
    "tools": "",
    "id": "",
});
const show_labelCount = ref(false); //显示标注数量
const selectedField = ref('all'); //搜索时的搜索字段
const searchWord = ref(''); //搜索时的搜索词

async function SearchData() {
    //搜索数据
    const result = await queryMessageData({ mode: "sample", limit: -1, keyword:searchWord.value, field: selectedField.value });
    console.log(result);
    tableData.value = result.data;
}

function startModify(index) {
    const indexData = tableData.value[index];
    console.log('修改数据,索引是', index, '数据是', indexData);
    showSidenav.value = true;
    modifiedMessage.value = indexData;
};

async function updateOneMessage() {
    //更新Message
    const result = await updateMessage({ "id": modifiedMessage.value.id, "prompt": modifiedMessage.value.prompt, "prompt_name": modifiedMessage.value.prompt_name, "messages": modifiedMessage.value.messages, "tools": modifiedMessage.value.tools });
    console.log('更新数据的结果是', result);
    if (result.code === 0) {
        ElNotification({
            message: `更新数据成功`,
            type: 'info',
        });
        showSidenav.value = false;
        await getTableData(200);
        modifiedMessage.value = { "prompt": "", "prompt_name": "", "messages": "", "tools": "", "id": "" }
    }
    else {
        ElNotification({
            message: `更新数据失败，${result.msg}，请检查接口`,
            type: 'info',
        });
    };
}

async function deleteOneMessage(index) {
    console.log('删除数据', index);
    const indexData = tableData.value[index];
    const data_id = indexData.id;
    const response = await deleteMessage({ id: data_id })
    if (response.code === 0) {
        ElNotification.info("删除数据成功")
        await getTableData(200); //更新下数据
    } else {
        ElNotification.error("删除数据失败")
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