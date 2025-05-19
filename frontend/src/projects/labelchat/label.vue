<template>
    <navHeader></navHeader>
    <main class="w-screen flex mx-auto my-0 p-2">
        <div class="left h-screen w-1/2 rounded">
            <div class="w-full h-full overflow-auto border-r-2 border-gray-300 rounded-sm">
                <div class="leading-6 flex justify-between content-center relative grow"
                    v-for="(msg, index) in messages" :key="msg.id">
                    <!-- 显示在左侧还是在右侧 -->
                    <div class="w-full flex justify-between my-1 py-1 rounded-sm"
                        :class="msg.role === 'human' ? 'flex-row bg-green-200' : 'flex-row-reverse bg-blue-200'">
                        <div class="font-medium flex-grow" :class="{ 'bg-red-200': activeBgcolorIndex === index }">
                            <!-- getBackgroundClass设置不同的用户不同的颜色 -->
                            <div class="mx-2 whitespace-pre-wrap" :class="msg.role === 'human' ? '' : 'mr-8'"
                                :msgId="msg.id" @dblclick="changeContent(index)" v-if="activeBgcolorIndex !== index"
                                v-html="msg.display_content ? msg.display_content : msg.content">
                            </div>
                            <textarea v-else v-model="msg.content" @blur="activeBgcolorIndex = -1" class="w-full"
                                v-autogrow />
                        </div>
                        <div class="relative w-24 shrink-0 flex items-center box-border"
                            :class="msg.role === 'human' ? 'flex-row-reverse mr-8' : 'flex-row'">
                            <div v-if="msg.role === 'human'" class="w-6 h-6 mt-1">
                                <IconPerson />
                            </div>
                            <div v-else class="w-6 h-6 mt-1">
                                <IconOpenAI />
                            </div>
                            <div class="text-ellipsis overflow-hidden w-full text-center leading-4">
                                <span class="text-sm leading-4">{{ msg.role }}</span>
                            </div>
                        </div>
                    </div>
                    <el-button size="small" class="hover:scale-110 absolute right-0 top-3"
                        @click="deleteMessage(msg.id)" type="danger" icon="Delete" circle />
                </div>
            </div>
            <div class="flex w-full h-12 grow">
                <el-input v-model="currentQuestion.question" autosize type="textarea"
                    placeholder="请输入或双击对话修改,Shift+enter提交" @keyup.shift.enter="submitQuestion" />
                <el-button type="success" @click="submitQuestion" title="shift+enter提交">新增</el-button>
            </div>
        </div>
        <div class="right bg-white w-1/2">
            <div class="text-center mb-2">点击任何按钮生成对应的对话 </div>
            <div class="flex justify-between items-center flex-wrap w-4/5">
                <div>
                    <span>prompt:</span>
                    <el-select v-model="currentPrompt" placeholder="Select" style="width: 100px">
                        <el-option v-for="(prompt, index) in prompts" :key="prompt.name" :label="prompt.name"
                            :value="prompt.name" />
                    </el-select>
                </div>
                <el-row class="w-full">
                    <el-button :type="currentQuestion.question_type === 'human' ? 'primary' : 'success'" round
                        @click="AddHumanMsg">Human</el-button>
                    <el-button :type="currentQuestion.question_type === 'gpt' ? 'primary' : 'success'" round
                        @click="AddGptMsg">gpt</el-button>
                    <el-button :type="currentQuestion.question_type === 'function_call' ? 'primary' : 'success'" round
                        @click="AddFunctionMsg">function_call</el-button>
                    <el-button :type="currentQuestion.question_type === 'observation' ? 'primary' : 'success'" round
                        @click="AddObservationMsgOrRunFunction">observation</el-button>
                    <!-- 选择使用哪个prompt -->
                </el-row>
                <el-row>
                    <el-button type="danger" round @click="GetSample">sample</el-button>
                    <el-button type="warning" round @click="ClearMessage">clear</el-button>
                    <el-button type="danger" round @click="SaveMessage">save</el-button>
                    <el-button type="warning" round @click="AutoRun">auto</el-button>
                </el-row>
                <el-row class="w-full">
                    <button class="btn" @click="AnswerQuestion" :disabled="canNotAnswered">
                        <span class="loading loading-spinner" v-if="loading"></span>
                        answer
                    </button>
                    <el-icon style="align-self: center;" @click="show_answer_tools = !show_answer_tools">
                        <ArrowRight />
                    </el-icon>
                    <div v-show="show_answer_tools">
                        <div class="inline-flex items-center" v-for="(tool_name, index) in tools_names"
                            :key="tool_name">
                            <label class="relative flex cursor-pointer items-center rounded-full p-3" :for="tool_name"
                                data-ripple-dark="true">
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
                            <label class="mt-px cursor-pointer select-none font-light text-gray-700" :for="tool_name">
                                {{ tool_name }}
                            </label>
                        </div>
                    </div>
                </el-row>
            </div>
            <div v-if="currentQuestion.question_type === 'function_call'">
                <el-divider />
                <functionDrawer />
            </div>
            <div v-if="display_function_result">
                <el-divider />
                <div class="card w-96 bg-base-300 shadow-xl">
                    <div class="card-body btn my-2" @click="AddToObservation" v-show="function_results.length !== 0"
                        v-for="(function_result, index) in function_results">
                        {{ function_result.name }} --> {{ function_result.msg }}
                    </div>
                </div>
            </div>
            <div v-if="display_answer_results">
                <el-divider />
                <div>
                    <div class="card w-full bg-base-300 shadow-xl mb-5" v-for="llm_result in multi_llm_results"
                        :key="llm_result.llm">
                        <div class="card-body p-6">
                            <h3 class="card-title">{{ llm_result.llm }}</h3>
                            <button class="btn btn-outline btn-success h-full"
                                v-show="llm_result.response.tool_calls.length === 0"
                                @click="AddToResponse(llm_result.response.content)">{{ llm_result.response.content
                                }}</button>
                            <div v-show="llm_result.response.tool_calls.length !== 0">
                                <button class="btn btn-outline btn-success h-full"
                                    v-for="tool_call in llm_result.response.tool_calls"
                                    @click="AddToFunctionCall(tool_call)"> {{ tool_call }} </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <neo4jGraph></neo4jGraph>
            <plotEcharts></plotEcharts>
        </div>
    </main>
</template>

<script lang="ts" setup>
import navHeader from './navHeader.vue';
import IconOpenAI from './IconOpenAI.vue';
import IconPerson from './IconPerson.vue';
import neo4jGraph from './neo4jGraph.vue';
import plotEcharts from './plotEcharts.vue';
import { ElNotification } from 'element-plus';
import { ref, onMounted, reactive, toRefs, computed, watch } from 'vue';
import functionDrawer from './functionDrawer.vue';
import { RunFunction } from './utils.ts'
import { useMessageStore, useSettings } from './store.ts';
import { getPrompts, startLabelChat, saveChat, getTools, getAllQuestion, queryQuestionLabel } from './api.ts'
const { currentQuestion, messages, function_results, message_tool_names, tools_data, multi_llm_results } = toRefs(useMessageStore());
const { selectedLLM, sample_idx, selectedSample, usecache, currentPrompt } = toRefs(useSettings());
const { AddHumanMsg, AddGptMsg, AddFunctionMsg, AddObservationMsg } = useMessageStore();
const { display_neo4j_meta, display_plot_meta, need_summary } = toRefs(useMessageStore());
const activeBgcolorIndex = ref(-1); //默认任何问题和回答都不加背景色，即都没有选中
const display_function_result = computed(() => {
    return currentQuestion.value.question_type === 'observation' || currentQuestion.value.question_type === 'function_call'
});
const prompts = ref();
const show_answer_tools = ref(false);
const tools_names = ref();
const selectedTools = ref([]); //注意bool类型和数组类型，导致选中的状态不一样
const questions = ref(); //所有的问题
const display_answer_results = ref(false) //当使用多个模型时，答案有多个，那么就显示多个答案结果，供用户选择
const loading = ref(false);
const from_sample = ref(false); //当前数据的问题是否来自采样

function getType(value) {
  if (value instanceof Array) {
    return 'array';
  } else if (value instanceof Date) {
    return 'date';
  } else if (value instanceof RegExp) {
    return 'regexp';
  } else {
    return typeof value;
  }
}

function ClearMessage() {
    //清空当前的对话
    messages.value = []
    //清空当前问题记录
    currentQuestion.value.question = ''
    currentQuestion.value.question_id = -1
    currentQuestion.value.question_type = ''
    if (from_sample.value) {
        //记录下一个问题的样本, 只有当clear的时，下个sample_idx才加+1
        sample_idx.value += 1
    };
    from_sample.value = false; //重置是否来自采样的开关
    display_neo4j_meta.value = "";
    display_plot_meta.value = "";
    need_summary.value = true;
};
async function AutoRun() {
    //自动运行标注, 首先sample,然后运行answer,然后运行observation,然后运行answer
    GetSample()
    if (selectedTools.value.length > 0) {
        // 如果使用工具了，那么就会比没使用工具多2个流程，1个是工具的参数，1个是工具的观察结果
        await AnswerQuestion()
        await AddObservationMsgOrRunFunction()
        AddToObservation()
        await AnswerQuestion()
    } else {
        //没使用工具
        await AnswerQuestion()
    }
}

async function AddObservationMsgOrRunFunction() {
    //先设置当前的数据为Observation，然后根据时机判断
    //合并增加observation和RunFunction的功能，当最后一条信息role是function_call的时候，就自动运行RunFunction,
    AddObservationMsg()
    const last_message_role = messages.value[messages.value.length - 1].role
    if (last_message_role === 'function_call') {
        await RunFunction()
    }
}

//检查回答按钮什么时候可以点击
const canNotAnswered = computed(() => {
    return messages.value.length === 0 || messages.value[messages.value.length - 1].role === "gpt";
})

function AddToObservation() {
    if (function_results.value.length === 0) {
        ElNotification({
            title: '提示',
            message: '函数没有执行完成或者还没执行函数',
            type: 'warning',
        })
        return;
    }
    //把function_results的内容添加到messages中, 当前如果是修改的function，那么就修改下1个observation
    //新增observation的内容，首先把当前的内容添加到messages中
    if (currentQuestion.value.question_type === "function_call") {
        submitQuestion() //提交后，btnContent内容会改变，所以放在这个括号里面
    }
    for (let one_func_res of function_results.value) {
        let func_msg = one_func_res.msg
        const func_msg_type = getType(func_msg)
        if (func_msg_type === "array" || func_msg_type === "object") {
            func_msg = JSON.stringify(func_msg, null, 2)
        }
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: "observation",
            content: func_msg, //显示内容
            tool_call_id: one_func_res.id,  //工具id
            name: one_func_res.name, //工具的名称
            display_content: `${one_func_res.name}\n${one_func_res.id}\n${func_msg}`
        });
    }
    if (!need_summary.value) {
        // 如果不需要gpt进行summary的话，直接追加GPT的回答结果和函数的返回结果相同即可
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: "gpt",
            content: function_results.value,
        });
    };
    function_results.value = [];
    need_summary.value = true;
};

function AddToResponse(content) {
    //把llm的回答添加到messages中
    messages.value.push({
        id: messages.value[messages.value.length - 1].id + 1,
        role: "gpt",
        content: content,
    });
    display_answer_results.value = false; //显示答案结果
    multi_llm_results.value = [] //清空multi_llm_results
}

function AddToFunctionCall(callMsg) {
    //把函数调用的内容添加到messages中
    const callMsg_string = JSON.stringify(callMsg)
    messages.value.push({
        id: messages.value[messages.value.length - 1].id + 1,
        role: "function_call",
        content: callMsg_string,
    });
    display_answer_results.value = false; //显示答案结果
    multi_llm_results.value = [] //清空multi_llm_results
}

function GetSampleAndSelectedTools() {
    //实现根据sample到的样本，控制answer按钮的状态,selectedSample,tools_names,selectedTools
    if (tools_names.value.includes(selectedSample.value)) {
        selectedTools.value.push(selectedSample.value)
        show_answer_tools.value = true
    }
};

async function GetSample() {
    //获取的问题，根据sample_idx和questions, 如果sample_idx.value不是字符串，变成数字
    if (!questions.value) {
        ElNotification.info("你还没有在管理界面设置Sample问题类型，请先进行设置后，在使用sample按钮")
    }
    from_sample.value = true; //当前数据的问题来自采样
    if (sample_idx.value <= questions.value.length) {
        const question = questions.value[sample_idx.value]
        //获取样本的时候，就控制answer应该怎么回答，如果selectedSample在tools_names中，那么就默认选中
        GetSampleAndSelectedTools()
        if (messages.value.length === 0) {
            //当messages为空时，只有1个问题的时候，我们查询queryQuestionLabel，获取这个问题的已标注数据，方便再次就行标注和修改
            const query_result = await queryQuestionLabel({ "questions": [question] })
            console.log("query_result:", query_result)
            if (query_result.code === 0) {
                if (query_result.data[0].status !== "unlabeled") {
                    messages.value = query_result.data[0].messages
                } else {
                    messages.value.push({
                        id: 1,
                        role: "human",
                        content: question,
                    });
                }
            }
        } else if (messages.value[messages.value.length - 1].role === 'gpt') {
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "human",
                content: question,
            });
        } else {
            ElNotification.warning("上一条消息不是gpt，或者不是第一条信息，无法添加human的问题")
        }
    } else {
        ElNotification.warning("没有更多的的样本了,请在管理中设置样本数据集和样本的起始序号")
    }
};

async function SaveMessage() {
    //保存当前的对话到数据库
    const result = await saveChat({ messages: messages.value, prompt: currentPrompt.value, tools: message_tool_names.value })
    console.log("数据的保存结果:", result)
    const code = result.code
    if (code === 0) {
        ElNotification({
            message: `保存数据成功到后台`,
            type: 'info',
        });
        //清空当前的对话
        messages.value = []
        //清空当前问题记录
        currentQuestion.value.question = ''
        currentQuestion.value.question_id = -1
        currentQuestion.value.question_type = ''
        if (from_sample.value) {
            //记录下一个问题的样本, 只有当clear的时，下个sample_idx才加+1
            sample_idx.value += 1
        }
        from_sample.value = false; //重置是否来自采样的开关
        display_neo4j_meta.value = ""; //重置知识图谱的显示
        display_plot_meta.value = ""; //重置知识图谱的显示
        need_summary.value = true;
    }
    else {
        ElNotification({
            message: `保存数据失败，请检查后端日志`,
            type: 'error',
        });
    };
};

async function AnswerQuestion() {
    //对当前的问题进行回答, 最后的message的role应该是human或者gpt，那么才进行回答
    const last_message_role = messages.value[messages.value.length - 1].role
    if (last_message_role !== 'human' && last_message_role !== 'observation') {
        ElNotification({
            message: '最后一条消息不是用户或者observation，无法进行回答',
            type: 'warning',
        })
        return
    }
    loading.value = true
    //计算selectedTools
    const tools = selectedTools.value.length === 0 ? "empty" : selectedTools.value.join(",")
    if (selectedLLM.value.length === 1) {
        const response = await startLabelChat({ "prompt": currentPrompt.value, "messages": messages.value, "llm": selectedLLM.value, "tools": tools, "usecache": usecache.value })
        console.log("Chat response:", response)
        //用户选择1个答案时，直接添加答案到message
        const response_content = response.data[0].response.content
        let tool_calls = response.data[0].response.tool_calls
        activeBgcolorIndex.value = -1
        //添加到messages的中，追加到最后一条数据中
        if (tool_calls.length > 0) {
            const tool_calls_string = JSON.stringify(tool_calls)
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "function_call",
                content: tool_calls_string,
                display_content: JSON.stringify(JSON.parse(tool_calls_string), null, 2),
            });
        } else {
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "gpt",
                content: response_content,
            });
        }
        loading.value = false
    } else {
        //如果使用了多个模型，那么回答的答案是多个，逐个调用模型，然后让用户选择1个答案
        console.log("使用多个模型的回答");
        multi_llm_results.value = []; //清空multi_llm_results
        display_answer_results.value = true //显示答案结果
        //使用异步方式调用所有模型
        let promises = selectedLLM.value.map(llm =>
            startLabelChat({ "prompt": currentPrompt.value, "messages": messages.value, "llm": [llm], "tools": tools, "usecache": usecache.value })
                .then(response => {
                    console.log("llm:", llm, "response:", response);
                    //用户选择1个答案时，直接添加答案到message
                    multi_llm_results.value.push(response.data[0]);
                })
        );
        Promise.all(promises)
            .then(() => {
                console.log('All tasks have been done.');
                loading.value = false;
            })
            .catch(error => {
                console.log('An error has occurred: ', error);
                loading.value = false;
            });
    }
    show_answer_tools.value = false
};

function deleteMessage(msg_id) {
    //删除1条信信息
    if (msg_id !== -1) {
        console.log("要删除message:", msg_id)
        let updateList = messages.value.filter((el) => el.id !== msg_id);
        messages.value = updateList
        if (from_sample.value && messages.value.length === 0) {
            //当是只有一条数据，并且是样本数据时，删除，会增加一条索引，方便找下一条索引
            sample_idx.value += 1
        };
        from_sample.value = false; //重置是否来自采样的开关
    } else {
        ElNotification({
            message: '没有选中任何信息，请双击1条信息，然后按delete键删除',
            type: 'info',
        })
    }
};

// 双击的功能：把现在的input的type属性改成text，可以输入值
function changeContent(index) {
    //同时，改变消息的背景颜色，表示选中这条消息
    messages.value.forEach((msg, idx) => {
        //取消其它消息的背景色
        if (idx === index) {
            currentQuestion.value.question_type = msg.role
            activeBgcolorIndex.value = index
        }
    })
};

function submitQuestion() {
    // 当question_id为-1时，说明用户是直接输入的内容，没有对已有聊天进行修改
    if (currentQuestion.value.question_id === -1 && messages.value.length === 0) {
        // 当用户第1次输入内容时，可以作为用户数据添加
        messages.value.push({
            id: 1,
            role: "human",
            content: currentQuestion.value.question,
        });
    } else {
        if (!currentQuestion.value.question_type) {
            ElNotification({
                message: '还没有选择当前消息的类型，请右边点击按钮选择类型',
                type: 'info',
            })
            return
        }
        if (!currentQuestion.value.question) {
            ElNotification({
                message: '你好像还么有输入任何內',
                type: 'info',
            })
            return
        }
        const last_message_role = messages.value[messages.value.length - 1].role;
        if (currentQuestion.value.question_type === last_message_role) {
            ElNotification({
                message: '不能连续2条都是同1个角色的消息',
                type: 'info',
            })
            return
        }
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: currentQuestion.value.question_type,
            content: currentQuestion.value.question,
        });
    }
    //修改货新增完成后重置question和question_id
    currentQuestion.value.question = ''
    currentQuestion.value.question_id = -1
    currentQuestion.value.question_type = ''
};

onMounted(async () => {
    const result = await getPrompts()
    prompts.value = result.data
    console.log("prompts:", prompts.value);
    const tools = await getTools()
    // console.log(tools);
    tools_data.value = tools.data;
    console.log("tools_data:", tools_data.value);
    tools_names.value = Object.keys(tools_data.value)
    const allQuestions = await getAllQuestion({ "keyword": selectedSample.value });
    console.log(allQuestions)
    allQuestions.data.forEach(item => {
        if (item.prompt === selectedSample.value) {
            questions.value = item.questions
        };
    });
    //根据selectedSample筛选问题
    console.log(questions.value)
    //把sample_idx.value从字符串变成数字
    sample_idx.value = +sample_idx.value;
});
</script>

<style lang="scss" scoped></style>