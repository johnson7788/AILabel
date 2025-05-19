<template>
    <navHeader></navHeader>
    <div class="main flex flex-col w-full lg:flex-row">
        <div class="left w-3/5 grid card bg-lime-50 rounded-box place-items-center h-screen">
            <div>选中1个prompt，修改，查看，或者生成更多问题, 当前选中的Agent是测试多个excel的Agent</div>
            <div class="w-full">
                <div class="flex flex-row justify-between items-center ml-2">
                    <select class="select select-bordered w-full max-w-xs" v-model="selectedPrompt">
                        <option disabled selected>所有prompt对应的问题指令</option>
                        <option v-for="item in prompts_questions"> {{ item.name }}</option>
                    </select>
                    <div class="mr-10">问题数量: {{ total_question_num }}</div>
                </div>
                <div class="divider"></div>
            </div>
            <!-- 加载状态 -->
            <button class="btn btn-square" v-show="loading">
                <span :class="{ 'loading loading-spinner': loading }"></span>
            </button>
            <!-- 重新生成和保存 -->
            <div class="flex flex-row justify-between items-center mt-2 w-72">
                <button class="btn btn-warning" @click="generateMoreQuestions">生成</button>
                <button class="btn btn-warning" :disabled="!can_saved" @click="saveOneQuestion">保存</button>
            </div>
        </div>
        <div class="divider lg:divider-horizontal"></div>
        <!-- 双击后改变编辑状态 -->
        <div
            class="right w-2/5 h-screen grid flex-grow card bg-lime-50 rounded-box place-items-center p-6 overflow-auto">
            <div class="whitespace-pre-wrap" @dblclick="editingContent" v-if="!editing">{{ content }}</div>
            <textarea v-else v-model="content" @blur="editing = false" class="w-full h-full" />
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, toRefs, watch } from 'vue';
import axios from 'axios';
import { ElNotification } from 'element-plus';
import navHeader from './navHeader.vue';
import { getPrompts, getTools, generateQuestion, saveQuestion, getAllQuestion, deleteQuestion, getPromptsQuestions } from './api.ts';
import { useMessageStore, useSettings } from './store.ts';
const { selectedLLM, usecache } = toRefs(useSettings());
const prompts_questions = ref();
const editing = ref(false); //是否是编辑状态
const content = ref('生成后的结果双击可以修改,也可以直接修改，支持按行的纯文本和json的数组格式');
const loading = ref(false);
const can_saved = ref(false); //已经生成了内容，可以执行保存或者重新生成
const selectedPrompt = ref('fragrence_agent');
const total_question_num = ref(0);
const GEN_API = import.meta.env.VITE_APP_GEN_QA_AGENT_API;

watch(selectedPrompt, (newVal, oldVal) => {
    //更细total_question_num, 根据all_questions中prompt等于newVal的中的内容来筛选
    total_question_num.value = prompts_questions.value.filter(item => item.name === newVal)[0].number;
    console.log("total_question_num", total_question_num.value);
    content.value = prompts_questions.value.filter(item => item.name === newVal)[0].question_content;
});

function editingContent() {
    editing.value = true;
    can_saved.value = true;
};

async function saveOneQuestion() {
    const result = await saveQuestion({ "prompt": selectedPrompt.value, "question_content": content.value, "llm": selectedLLM.value });
    if (result.code == 0) {
        ElNotification.info("保存成功");
        content.value = '生成后的结果双击可以修改';
        can_saved.value = false;
    } else {
        ElNotification.error("保存失败")
    }
};

async function generateMoreQuestions() {
    //根据提供prompt，直接生成问题: prompt的内容
    if (selectedPrompt.value == '' || selectedPrompt.value == "fragrence_agent") {
        ElNotification.error("请选择prompt或者选择的prompt不是agent的prompt，请在管理中进行修改对应的配置")
        return
    }
    loading.value = true;
    // 当前已有的questions，为了进行去过滤，相同的问题，没必要重复生成
    const current_questions = prompts_questions.value.filter(item => item.name === selectedPrompt.value)[0].questions;
    // 根据current_questions计算当前问题数量
    const current_questions_number = current_questions.length;
    // 每次增加20个新问题
    const response = await axios.post(
        `${GEN_API}/api/generate_questions`,
        { "questions": current_questions, "total_num": current_questions_number+ 20, "project": "beauty"},
    )
    console.log('response:', response);
    const data_code = response.data.code;
    if (data_code !== 0) {
        ElNotification.error("发生了错误，请联系管理员,"+ response.data.data)
        loading.value = false; //loading状态结束
        return
    }
    content.value = response.data.data.questions_content;
    loading.value = false; //loading状态结束
    can_saved.value = true;
}

onMounted(async () => {
    const result = await getPromptsQuestions()
    console.log(result.data)
    prompts_questions.value = result.data
});

</script>

<style lang="scss" scoped></style>