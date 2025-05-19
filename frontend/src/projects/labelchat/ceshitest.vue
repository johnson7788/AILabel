<template>
    <navHeader></navHeader>
    <!-- 设置 -->
    <div class="main" v-if="isSetting">
        <button class="btn btn-circle" @click="closeOpenSetting">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>
        <section class="text-gray-600 body-font overflow-hidden">
            <div class="container px-5 py-10 mx-auto">
                <div class="py-2 divide-y-2 divide-gray-100">
                    <div class="md:w-64 md:mb-0 mb-6 flex-shrink-0 flex flex-col">
                        <span class="font-semibold title-font text-gray-700">选择可以使用的工具</span>
                    </div>
                    <div class="md:flex-grow">
                        <div class="py-8 flex flex-wrap">
                            <div class="inline-flex items-center" v-for="(tool_name, index) in tools_names"
                                :key="tool_name">
                                <label class="relative flex cursor-pointer items-center rounded-full p-3"
                                    :for="tool_name" data-ripple-dark="true">
                                    <input :id="tool_name" type="checkbox" v-model="selectedTools" :value="tool_name"
                                        class="before:content[''] peer relative h-5 w-5 cursor-pointer appearance-none rounded-md border border-blue-gray-200 transition-all before:absolute before:top-2/4 before:left-2/4 before:block before:h-12 before:w-12 before:-translate-y-2/4 before:-translate-x-2/4 before:rounded-full before:bg-blue-gray-500 before:opacity-0 before:transition-opacity checked:border-pink-500 checked:bg-pink-500 checked:before:bg-pink-500 hover:before:opacity-10" />
                                    <div
                                        class="pointer-events-none absolute top-2/4 left-2/4 -translate-y-2/4 -translate-x-2/4 text-white opacity-0 transition-opacity peer-checked:opacity-100">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" viewBox="0 0 20 20"
                                            fill="currentColor" stroke="currentColor" stroke-width="1">
                                            <path fill-rule="evenodd"
                                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                                clip-rule="evenodd"></path>
                                        </svg>
                                    </div>
                                </label>
                                <label class="mt-px cursor-pointer select-none font-light text-gray-700"
                                    :for="tool_name">
                                    {{ tool_name }}
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="py-8 flex flex-wrap md:flex-nowrap">
                    <div class="md:w-64 md:mb-0 mb-6 flex-shrink-0 flex flex-col">
                        <span class="font-semibold title-font text-gray-700">system prompt</span>
                        <span class="mt-1 text-gray-500 text-sm">系统的prompt</span>
                    </div>
                    <div class="md:flex-grow">
                        <textarea class="textarea textarea-accent w-full h-40" placeholder="Something"
                            v-model="system_prompt"></textarea>
                    </div>
                </div>
                <div class="py-8 flex flex-wrap md:flex-nowrap">
                    <span class="font-semibold title-font text-gray-700 mr-4">中间过程详细模式:</span>
                    <input type="checkbox" class="toggle toggle-success" checked v-model="detailMode" />
                </div>
            </div>
        </section>
    </div>
    <!-- 聊天 -->
    <div class="h-full lg:grid lg:grid-cols-2 bg-blue-100 md:flex md:flex-col" v-if="!isSetting"
        @keyup.ctrl.1="randomMessage" tabindex="0">
        <!-- 左侧 -->
        <div class="relative m-2 h-screen flex flex-col">
            <div class="bg-white">
                <button class="btn btn-sm w-32 h-10" @click="closeOpenSetting">
                    AgentAI
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
                        stroke="green">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </button>
            </div>
            <div class="scroll-smooth bg-white relative overflow-auto flex-grow" ref="messageRef">
                <div class="box-border flex flex-col pt-4 pb-0 px-4 last:pb-4" v-for="(item, index) in messages"
                    :key="index">
                    <div :class="item.role === 'user' ? 'flex flex-row justify-end' : 'flex flex-row-reverse justify-end'"
                        v-show='detailMode || !item.middle_process'>
                        <!-- 显示在左侧还是在右侧，跟msg.user_id有关 -->
                        <!-- getBackgroundClass设置不同的用户不同的颜色 -->
                        <div class="whitespace-pre-wrap rounded-md p-3 border"
                            :class="item.role == 'user' ? 'bg-blue-200' : ''"
                            v-html="item.display_content ? item.display_content : item.content">

                        </div>
                        <div class="relative w-20 shrink-0 flex flex-col items-center box-border">
                            <div v-if="item.role === 'user'" class="fill-blue-100 h-8">
                                <IconPerson />
                            </div>
                            <div v-else class="h-8">
                                <IconOpenAI />
                            </div>
                            <div class="text-ellipsis overflow-hidden w-full text-center leading-none">
                                <span class="text-sm">{{ item.role }}</span>
                            </div>
                        </div>
                    </div>
                    <div v-if="item.options" class="flex justify-center items-center mt-3">
                        <el-button type="danger" v-for="(option, index) in item.options" :key="option"
                            @click="handleOptionClick(option)">{{ option }}</el-button>
                    </div>
                    <div v-if="item.image">
                        <img :src="item.image" class="w-full object-cover h-52" />
                    </div>
                    <div v-if="item.echarts" class="my-4">
                        <!-- 如果存在echarts属性那么就绘图 -->
                        <component :is="getComponent(item.echarts.info.type)" :dataProps="item.echarts"></component>
                    </div>
                </div>
                <div v-if="showLoading" class="relative px-0 py-1.5">
                    <LoadingText />
                </div>
            </div>
            <div
                class="relative h-14 box-border bg-neutral-200 rounded-lg border-solid border-2  focus:border-neutral-900">
                <input @keyup.enter="handleSend" placeholder="输入问题,ctrl+1随机问题"
                    class="h-full w-full border-transparent text-inherit appearance-none text-base grow m-0 px-4 p-0 border-0"
                    type="text" v-model="question" />
                <div class="flex items-center absolute right-0 top-0 h-full">
                    <el-upload class="ml-3 mr-3" :show-file-list="true" :limit=1 :http-request="Upload"
                        :before-upload="BeforeUpload" ref="uploadFile" :on-exceed="HandleExceed"
                        :on-success="UploadSuccess" :on-error="UploadError" accept="image/*">
                        <div class="h-8 mt-2">
                            <IconFileUpload />
                        </div>
                    </el-upload>
                    <button :disabled="!question || showLoading" @click="handleSend"
                        class="text-inherit block appearance-none text-base cursor-pointer mr-3 p-0 border-0 active:opacity-100 disabled:opacity-30 duration-200">
                        <IconSend />
                    </button>
                </div>
            </div>
        </div>
        <!-- 右侧 -->
        <div class="bg-white m-2 overflow-auto h-screen scroll-smooth">
            <neo4jGraph></neo4jGraph>
        </div>
    </div>
</template>


<script lang="ts" setup>
import navHeader from './navHeader.vue';
import { onMounted, ref, computed, watch, toRefs, nextTick } from 'vue';
import IconOpenAI from './IconOpenAI.vue';
import IconPerson from './IconPerson.vue';
import IconFileUpload from './IconFileUpload.vue';
import IconSend from './IconSend.vue';
import { ElNotification } from 'element-plus'
import LoadingText from './LoadingText.vue';
import neo4jGraph from './neo4jGraph.vue';
import Bar from './Bar.vue' //使用子组件绘图
import Pie from './Pie.vue'
import axios from 'axios';
import { useMessageStore, useSettings } from './store.ts';
const { selectedLLM, usecache } = toRefs(useSettings());
import { getPrompts, startChat, saveChat, getTools, getAllQuestion } from './api.ts'
const { need_summary, display_neo4j_meta, display_plot_meta, select_nodes } = toRefs(useMessageStore());
const system_prompt = ref("你是一个ai助手，使用中文回答用户问题。")
const tools_names = ref([]);
const isSetting = ref(false); //目前是否是设置状态
const selectedTools = ref(['today_date', 'perfume_knowledge', 'food_information_extraction', 'food_neo4j_query', 'food_neo4j_stats', 'operate_mtdnn_model']); //注意bool类型和数组类型，导致选中的状态不一样
const messageRef = ref(null)  //历史对话组件
const question = ref('')  //用户输入的问题
const showLoading = ref(false) //是否等待AI回复中
const uploadFile = ref(null)
const messages = ref([]) //问答列表
const detailMode = ref(true) //问答详情模式
const random_idx = ref(0) //按顺序的随机问答的索引

//根据不同名称传递的绘图组件
const getComponent = (name: string) => {
    if (name === 'Bar') {
        return Bar;
    } else if (name === 'Pie') {
        return Pie;
    } else {
        return null;
    }
}

function randomMessage() {
    //按顺序的随机生成1条消息,赋值给question
    const msgs = [
        "食品知识图谱中是否有关于大米饭的内容",
        "适合约会氛围的香水香调该如何设计",
        "食品知识图谱中是否有饭团相关的内容？",
        "解释下选中的节点",
        "打印一下当前知识图谱的状态",
        "提取下面食品评论中的知识和情感:\n最近给屁孩儿找到了一种好吃的食物。本来让她米饭就着菜和肉吃，吃的不太好，不让喂，自己手抓不好入口。后来想了个办法把饭菜揉成一团，饭团挺爱吃。后来又不喜欢了，老母亲又把饭团压扁裹上蛋黄液做成烤饼吃。屁孩儿又重新喜欢了吃得很开心。一波几折，米，肉菜算是都吃上了",
        "你好", "帮我查询下ip地址42.236.9.70的位置信息", "Song和Tang这2款汽车哪个价格更贵？", "今天是星期几？", "历史上的今天发生了什么事情",
    ]
    const randomMsg = msgs[random_idx.value % msgs.length]
    random_idx.value += 1
    question.value = randomMsg
    console.log(new Date().toLocaleString(), "随机生成消息", randomMsg)
}

function closeOpenSetting() {
    isSetting.value = !isSetting.value
};


//发送问答消息
const handleSend = async () => {
    if (!question.value.length) {
        return;
    }
    //来发送用户消息，如果AI正在思考中，那么就直接返回
    if (showLoading.value) {
        return
    }
    console.log(new Date().toLocaleString(), "用户开始发送消息")
    console.log("选中的节点包括: ", select_nodes.value)
    const question_content = question.value
    messages.value.push({
        content: question_content,
        role: 'user',
    });
    question.value = ''; //清空输入框
    resetScroll();
    showLoading.value = true;
    const additional = { "neo4j": select_nodes.value } //额外的信息
    const response = await startChat({ "prompt": system_prompt.value, "messages": messages.value, "llm": selectedLLM.value[0], "tools": selectedTools.value, "usecache": usecache.value, "additional": additional })
    console.log("Chat response:", response)
    if (response.code === 0) {
        const data_messages = response.data;
        for (let one of data_messages) {
            const role = one["role"]
            const tool_calls = one["tool_calls"]
            if (role === "tool" || (role === "assistant" && tool_calls)) {
                one["middle_process"] = true //标识着是否是中间过程，用于显示详情,detailMode
            } else {
                one["middle_process"] = false
            }
            if (tool_calls) {
                let tools_content = []
                for (let tool_call of tool_calls) {
                    const function_name_args = tool_call["function"]
                    const function_name_args_string = JSON.stringify(function_name_args)
                    const id = tool_call["id"]
                    tools_content.push(`${id}: ${function_name_args_string}`)
                }
                one["display_content"] = tools_content.join("\n")
            }
            const meta = one["meta"]
            if (role === "tool" && meta) {
                //判断meta信息，进行绘图
                if (meta.plot === "neo4j") {
                    display_neo4j_meta.value = meta.data; //获取结果中的meta信息，用于显示和绘图等
                } else if (meta.plot === "echarts") {
                    one["echarts"] = meta; //获取结果中的meta信息，用于显示和绘图等
                }
            }
            messages.value.push(one)
        }
    } else {
        const msg = response.msg
        ElNotification({
            message: `AI系统出错，请联系管理员！报错信息: ${msg}`,
            type: 'error',
        });
        // 弹出最后一个messages
        messages.value.pop()
        question.value = question_content; //如果出错了，那么问题还变回去，不用动了
    }
    showLoading.value = false;
};


function resetScroll() {
    console.log(new Date().toLocaleString(), "滚动屏幕")
    //函数来滚动消息列表, setTimeout() 方法将消息列表滚动到底部
    setTimeout(() => {
        messageRef.value.scrollTop = messageRef.value.scrollHeight
    }, 300)
}

//上传图片文件的处理开始
const Upload = (param) => {
    console.log(new Date().toLocaleString(), "开始上传文件，收到的组件传入参数是", param)
    const file_content = param.file
    console.log(new Date().toLocaleString(), "文件名称是", file_content.name);
    const reader = new FileReader();
    reader.onloadend = () => {
        const image_base64 = reader.result;
        console.log(new Date().toLocaleString(), "文件base64内容是", image_base64);
        // imgBase64.value = image_base64;
    };
    reader.readAsDataURL(file_content);
}
const BeforeUpload = (file) => { }

// 文件数超出提示
const HandleExceed = () => {
    ElNotification({
        message: '最多只能上传一个文件！',
        type: 'warning',
    })
}

// 上传错误提示
const UploadError = () => {
    ElNotification({
        message: '上传文件失败！',
        type: 'error',
    })
}

// 上传成功提示
const UploadSuccess = () => {
    ElNotification({
        message: '上传文件成功',
        type: 'success',
    })
}

onMounted(async () => {
    const tools = await getTools()
    tools_names.value = Object.keys(tools.data)
    if (selectedLLM.value.length > 1) {
        ElNotification({
            message: '测试只能选择一个LLM，默认使用选中的第一个！',
            type: 'warning',
        })
    } else if (selectedLLM.value.length == 0) {
        ElNotification({
            message: '请选择一个LLM进行测试,您目前没有选择任何1个LLM！',
            type: 'error',
        })
    }
});

</script>

<style lang="scss" scoped>
@import url('https://cdn.staticfile.org/font-awesome/4.7.0/css/font-awesome.css');
</style>