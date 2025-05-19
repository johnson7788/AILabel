<template>
    <navHeader></navHeader>
    <div class="main flex flex-col w-full lg:flex-row">
        <div class="left w-3/5 grid card bg-lime-50 rounded-box place-items-center h-screen">
            <div class="w-full">
                <div class="flex flex-col mt-5 space-y-4 justify-center items-center">
                    <div class="text text-lime-800 text-center">请选择或者输入生成更多问题的prompts?</div>
                    <div class="flex w-full flex-nowrap justify-center items-center">
                        <!-- 输入框和按钮 -->
                        <form class="w-full">
                            <label for="default-search"
                                class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-gray-300">Search</label>
                            <div class="relative w-full">
                                <input type="search" id="default-search" v-model="input_prompt" @input="searchPrompts"
                                    class="block p-4 pl-4 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="prompt" required>
                            </div>
                            <!-- 下拉搜索框 -->
                            <div class="dropdown-menu" v-show="load_is_open">
                                <div class="bg-white rounded-lg shadow-xl px-4 relative mt-2" v-for="item in matched_questions">
                                    <div class="py-4 flex items-center w-full hover:bg-gray-50" @click="changePrompt(item)">
                                        <a href="#" class="flex-1">
                                            <div class="text-gray-600 text-base">{{item.prompt}}</div>
                                        </a>
                                        <div>
                                            <svg width="40" height="20" viewBox="0 0 40 20"
                                                xmlns="http://www.w3.org/2000/svg">
                                                <line x1="30" y1="2" x2="40" y2="10" stroke="#9CA3AF" />
                                                <line x1="30" y1="18" x2="40" y2="10" stroke="#9CA3AF" />
                                                <line x1="20" y1="10" x2="40" y2="10" stroke="#9CA3AF" />
                                            </svg>
                                        </div>
                                    </div>
                                </div>

                            </div>

                        </form>
                        <!-- 生成和删除按钮 -->
                        <div class="text-white w-96 flex flex-nowrap justify-center items-center ">
                            <button type="submit" @click="generatePromptQuestions"
                                class=" bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">生成</button>
                            <button type="submit" @click="deleteOneQuestion"
                                class=" bg-yellow-700 hover:bg-yellow-800 focus:ring-4 focus:outline-none focus:ring-yellow-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-yellow-600 dark:hover:bg-yellow-700 dark:focus:ring-yellow-800">删除</button>
                        </div>
                    </div>
                    <div class="flex flex-row flex-wrap gap-2">
                        <button class="block text-sm ml-3 bg-slate-300 w-40 truncate hover:bg-slate-400"
                            v-for="(prompt, index) in prompts" :key="prompt.name"
                            v-on:mouseover="setPlaceholder(index, prompt.prompt)"
                            v-on:mouseleave="setDefaultPlaceholder(index)" @click="setInput(index, prompt.prompt)">
                            {{ prompt.name }}
                        </button>
                    </div>
                </div>
            </div>
            <!-- 加载状态 -->
            <button class="btn btn-square" v-show="loading">
                <span :class="{ 'loading loading-spinner': loading }"></span>
            </button>
            <!-- 重新生成和保存 -->
            <div>
                <button class="btn btn-warning" :disabled="!can_saved" @click="saveOneQuestion">保存</button>
            </div>
            <!--  搜索框 -->
            <div>
                <div class="text text-lime-800 text-center">根据工具的说明生成问题</div>
                <div class="flex flex-row justify-center items-center flex-wrap">
                    <button class="btn btn-outline btn-success btn-sm" v-for="(value, name) in tools_data"
                        @click="generateToolQuestions(name)" :key="name">
                        {{ name }}
                    </button>
                </div>
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
import { ref, onMounted, toRefs } from 'vue';
import { ElNotification } from 'element-plus';
import navHeader from './navHeader.vue';
import { getPrompts, getTools, generateQuestion, saveQuestion, getAllQuestion,deleteQuestion } from './api.ts';
import { useMessageStore, useSettings } from './store.ts';
const { selectedLLM,usecache } = toRefs(useSettings());
const { tools_data } = toRefs(useMessageStore());
const prompts = ref();
const input_prompt = ref('');
const placeholder_content = ref('');
const editing = ref(false); //是否是编辑状态
const content = ref('生成后的结果双击可以修改,也可以直接修改，支持按行的纯文本和json的数组格式');
const loading = ref(false);
const can_saved = ref(false); //已经生成了内容，可以执行保存或者重新生成
const load_is_open = ref(false); //加载数据的下拉菜单已经打开
const all_questions = ref(); //数据库中已存的所有问题
const matched_questions = ref(); //匹配到的所有问题

function editingContent() {
    editing.value = true;
    can_saved.value = true;
};

function setPlaceholder(index: number, placeholder: string) {
    placeholder_content.value = placeholder;
};
function setDefaultPlaceholder(index: number) {
    placeholder_content.value = ""
};
function setInput(index: number, prompt: string) {
    input_prompt.value = prompt;
}

async function deleteOneQuestion(){
    const response = await deleteQuestion({"prompt": input_prompt.value, "llm": selectedLLM.value});
    if (response.code == 0) {
        ElNotification.info("删除成功");
        content.value = '生成后的结果双击可以修改';
        can_saved.value = false;
        input_prompt.value = '';
    } else {
        ElNotification.error("删除失败")
    }
}

function changePrompt(item) {
    input_prompt.value = item.prompt;
    content.value = item.question_content;
    load_is_open.value = false;
    can_saved.value = true;
}

function searchPrompts(){
    //根据输入框中的內进行搜索
    const search_word = input_prompt.value.toLowerCase();
    if (search_word == "") {
        return
    }
    load_is_open.value = !load_is_open.value
    matched_questions.value = all_questions.value.filter(item => {
        const text = item.prompt.toLowerCase()
        if (text.includes(search_word)) {
            return item
        };
    });
    console.log("匹配到的问题:",matched_questions.value)
};

async function get_all_questions() {
    const allQuestions = await getAllQuestion({ "keyword": "empty" });
    console.log(allQuestions)
    all_questions.value = allQuestions.data;
}

async function saveOneQuestion() {
    const result = await saveQuestion({ "prompt": input_prompt.value, "question_content": content.value, "llm": selectedLLM.value });
    if (result.code == 0) {
        ElNotification.info("保存成功");
        content.value = '生成后的结果双击可以修改';
        can_saved.value = false;
    } else {
        ElNotification.error("保存失败")
    }
};


function getPromptsDict() {
    //根据prompts的内容，生成字典
    const prompts_dict = {};
    for (const prompt of prompts.value) {
        prompts_dict[prompt.name] = prompt.prompt;
    }
    return prompts_dict;
}

async function generateToolQuestions(name) {
    //根据提供的工具，生成问题,name:工具的名称
    const prompts_dict = getPromptsDict();
    if (!('gen_tool_question' in prompts_dict)) {
        ElNotification.error("还没有添加名字为gen_tool_question的prompt")
        return
    }
    loading.value = true;
    const prompt = prompts_dict["gen_tool_question"]
    const response = await generateQuestion({ "prompt": prompt, "tool_name": name, "llm": selectedLLM.value, "usecache":usecache.value })
    console.log('response:', response);
    content.value = response.data
    loading.value = false;
    can_saved.value = true;
    input_prompt.value = name;
}
async function generatePromptQuestions() {
    //根据提供prompt，直接生成问题: prompt的内容
    if (!input_prompt.value) {
        ElNotification.error("请输入prompt，然后点击确定")
        return
    }
    loading.value = true;
    const response = await generateQuestion({ "prompt": input_prompt.value, "llm": selectedLLM.value,"usecache":usecache.value })
    console.log('response:', response);
    content.value = response.data;
    loading.value = false; //loading状态结束
    can_saved.value = true;
}

onMounted(async () => {
    const result = await getPrompts()
    prompts.value = result.data
    const tools = await getTools()
    // console.log(tools);
    tools_data.value = tools.data;
    console.log("tools_data:", tools_data.value);
    await get_all_questions()
});

</script>

<style lang="scss" scoped></style>