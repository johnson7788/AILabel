<template>
    <navHeader></navHeader>
    <main class="w-screen flex mx-auto my-0 p-2">
        <div class="left h-screen w-1/2 rounded">
            <div class="w-full h-full overflow-auto border-r-2 border-gray-300 rounded-sm">
                <div class="leading-6 flex justify-between content-center relative grow"
                    v-for="(msg, index) in messages" :key="msg.id">
                    <!-- 显示在左侧还是在右侧 -->
                    <div class="w-full flex justify-between my-1 py-1 rounded-sm"
                        :class="msg.role === 'user' ? 'flex-row bg-green-200' : 'flex-row-reverse bg-blue-200'">
                        <div class="font-medium flex-grow" :class="{ 'bg-red-200': activeBgcolorIndex === index }">
                            <!-- getBackgroundClass设置不同的用户不同的颜色 -->
                            <div class="mx-2 whitespace-pre-wrap" :class="msg.role === 'user' ? '' : 'mr-8'"
                                :msgId="msg.id" @dblclick="changeContent(index)" v-if="activeBgcolorIndex !== index"
                                v-html="msg.display_content ? msg.display_content : msg.content">
                            </div>
                            <textarea v-else v-model="msg.content" @blur="activeBgcolorIndex = -1" class="w-full"
                                v-autogrow />
                        </div>
                        <div class="relative w-24 shrink-0 flex items-center box-border"
                            :class="msg.role === 'user' ? 'flex-row-reverse mr-8' : 'flex-row'">
                            <div v-if="msg.role === 'user'" class="w-6 h-6 mt-1">
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
                <el-input v-model="currentQuestion.question" autosize type="textarea" ref="InputBox"
                    :placeholder="placeholder_value" @keyup.shift.enter="submitQuestion" />
                <el-button type="success" @click="submitQuestion" title="shift+enter提交">新增</el-button>
            </div>
        </div>
        <div class="right bg-white w-1/2">
            <div class="text-center mb-2">三种标注模式 </div>
            <div class="flex justify-between items-center flex-wrap w-4/5">
                <div>
                    <span>prompt:</span>
                    <el-select v-model="currentPrompt" placeholder="Select" style="width: 100px">
                        <el-option v-for="(prompt, index) in prompts" :key="prompt.name" :label="prompt.name"
                            :value="prompt.name" />
                    </el-select>
                </div>
                <el-row class="w-full">
                    <el-button :type="currentQuestion.question_type === 'auto' ? 'primary' : 'success'" round
                        @click="Auto">Auto</el-button>
                    <el-button :type="currentQuestion.question_type === 'user' ? 'primary' : 'success'" round
                        @click="AddQuestion">Question</el-button>
                    <el-button :type="currentQuestion.question_type === 'SOP' ? 'primary' : 'success'" round
                        @click="AddQuestionSOP">Question+SOP</el-button>
                    <!-- 选择使用哪个prompt -->
                </el-row>
                <el-row>
                    <el-button type="danger" round @click="GetSample">Sample</el-button>
                    <el-button type="warning" round @click="ClearMessage">Clear</el-button>
                    <el-button type="danger" round @click="SaveMessage">Save&Correct</el-button>
                    <el-button type="danger" round @click="WrongMessage">Wrong</el-button>
                </el-row>
                <el-row class="w-full">
                    <button class="btn" @click="AnswerQuestion" :disabled="canNotAnswered">
                        <span class="loading loading-spinner" v-if="loading"></span>
                        answer
                    </button>
                </el-row>
            </div>
            <div v-if="currentQuestion.question_type === 'SOP'">
                <el-divider />
                <textarea placeholder="输入标准工作流计划和关键点，格式是,Workflow:  Key points:"
                    class="textarea textarea-bordered textarea-lg w-full" v-model="workflow"></textarea>
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
            <plotEcharts></plotEcharts>
        </div>
    </main>
</template>

<script lang="ts" setup>
import axios from 'axios';
import navHeader from './navHeader.vue';
import IconOpenAI from './IconOpenAI.vue';
import IconPerson from './IconPerson.vue';
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
const InputBox = ref(null);
const prompts = ref();
const tools_names = ref();
const selectedTools = ref([]); //注意bool类型和数组类型，导致选中的状态不一样
const questions = ref(); //所有的问题
const display_answer_results = ref(false) //当使用多个模型时，答案有多个，那么就显示多个答案结果，供用户选择
const loading = ref(false);
const from_sample = ref(false); //当前数据的问题是否来自采样
const GEN_API = import.meta.env.VITE_APP_GEN_QA_AGENT_API;
const placeholder_value = ref("请输入或双击对话修改,Shift+enter提交")
const workflow = ref("") //默认workflow的内容

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

function AddQuestion() {
    // 点击按钮，生成一条人类消息
    currentQuestion.value.question_type = 'user'
    placeholder_value.value = `User: 请输入问题`
    InputBox.value.focus()  //切换聚焦位置
}

function AddQuestionSOP() {
    //添加1个问题和计划
    currentQuestion.value.question_type = 'SOP'
    placeholder_value.value = `User: 请输入问题,输入完问题，旁边框输入SOP`
    InputBox.value.focus()  //切换聚焦位置
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
async function Auto() {
    //自动生成问答对
    loading.value = true;
    const res = await axios.post(
        `${GEN_API}/api/generate_qa`,
        { "workflow": true, "fake": true },
    )
    console.log(res)
    const data = res.data
    const msg = data.msg
    if (data.code == 0) {
        const data_result = data.data
        const question = data_result.question
        const answer = data_result.answer
        const workflow_output = data_result.workflow_output
        const intermidiates = data_result.intermidiates
        messages.value.push({
            id: 1,
            role: "user",
            content: question,
        });
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: "SOP",
            content: workflow_output,
        });
        //遍历intermidiates
        intermidiates.forEach((intermediate) => {
            const agent_status = intermediate["status"]
            if (agent_status === "AgentAction") {
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "thought",
                    content: intermediate["thought"],
                });
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "observation",
                    content: intermediate["observation"],
                });
            } else {
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "thought",
                    content: intermediate["thought"],
                });
            }
        });
        //将当前的问题记录下来
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: "assistant",
            content: answer,
            meta: data_result
        });
    } else {
        ElNotification({
            title: '错误',
            message: '生成问答对失败:' + msg,
            type: 'warning',
        })
    }
    loading.value = false;
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


async function GetSample() {
    //获取的问题，根据sample_idx和questions, 如果sample_idx.value不是字符串，变成数字
    if (!questions.value) {
        ElNotification.info("你还没有在管理界面设置Sample问题类型，请先进行设置后，在使用sample按钮")
    }
    from_sample.value = true; //当前数据的问题来自采样
    if (sample_idx.value <= questions.value.length) {
        const question = questions.value[sample_idx.value]
        //获取样本的时候，就控制answer应该怎么回答，如果selectedSample在tools_names中，那么就默认选中
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
                        role: "user",
                        content: question,
                    });
                }
            }
        } else if (messages.value[messages.value.length - 1].role === 'gpt') {
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "user",
                content: question,
            });
        } else {
            ElNotification.warning("上一条消息不是assistant，或者不是第一条信息，无法添加user的问题")
        }
    } else {
        ElNotification.warning("没有更多的的样本了,请在管理中设置样本数据集和样本的起始序号")
    }
};

async function WrongMessage() {
    //当点击错误的时候，也需要保存起来，方便进行对比学习
    const result = await saveChat({ messages: messages.value, prompt: currentPrompt.value, tools: message_tool_names.value, collection: "wronglabel" })
    console.log("数据的保存结果:", result)
    const code = result.code
    if (code === 0) {
        ElNotification({
            message: `保存错误回答数据成功到后台，请对当前数据继续进行修改`,
            type: 'info',
        });
    }
    else {
        ElNotification({
            message: `保存数据失败，请检查后端日志`,
            type: 'error',
        });
    };
}

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
    //对当前的问题进行回答, 最后的message的role应该是user那么才进行回答
    const last_message_role = messages.value[messages.value.length - 1].role
    if (last_message_role !== 'user' && last_message_role !== 'SOP') {
        ElNotification({
            message: '最后一条消息不是用户或者SOP，无法进行回答',
            type: 'warning',
        })
        return
    }
    loading.value = true
    let workflow = true;
    // 如果已经存在SOP了，那么没必要在进行生成了
    if (last_message_role === 'SOP') {
        workflow = false;
    }
    const res = await axios.post(
        `${GEN_API}/api/answer_messages`,
        { "messages": messages.value, "workflow": workflow },
    )
    console.log("Chat response:", res)
    const data = res.data
    const msg = data.msg
    if (data.code == 0) {
        const data_result = data.data
        const answer = data_result.output
        const workflow_output = data_result.workflow_output
        const intermidiates = data_result.intermidiates
        if (workflow_output) {
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "SOP",
                content: workflow_output,
            });
        }
        //遍历intermidiates
        intermidiates.forEach((intermediate) => {
            const agent_status = intermediate["status"]
            if (agent_status === "AgentAction") {
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "thought",
                    content: intermediate["thought"],
                });
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "observation",
                    content: intermediate["observation"],
                });
            } else {
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "thought",
                    content: intermediate["thought"],
                });
            }
        });
        //将当前的问题记录下来
        messages.value.push({
            id: messages.value[messages.value.length - 1].id + 1,
            role: "assistant",
            content: answer,
            meta: data_result
        });
    } else {
        ElNotification({
            title: '错误',
            message: '生成问答对失败:' + msg,
            type: 'warning',
        })
    }
    loading.value = false
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
            role: "user",
            content: currentQuestion.value.question,
        });
        if (workflow.value) {
            messages.value.push({
                id: messages.value[messages.value.length - 1].id + 1,
                role: "SOP",
                content: workflow.value,
            });
            workflow.value = "";
        }
    } else {
        if (!currentQuestion.value.question_type) {
            ElNotification({
                message: '还没有选择当前消息的类型，请右边点击按钮选择类型',
                type: 'info',
            })
            return
        }
        if (!currentQuestion.value.question) {
            if (workflow.value) {
                messages.value.push({
                    id: messages.value[messages.value.length - 1].id + 1,
                    role: "SOP",
                    content: workflow.value,
                });
                workflow.value = "";
            } else {
                ElNotification({
                    message: '你好像还么有输入任何內',
                    type: 'info',
                })
            }
            return
        }
        const last_message_role = messages.value[messages.value.length - 1].role;
        if (currentQuestion.value.question_type === last_message_role) {
            ElNotification({
                message: '注意:连续2条都是同1个角色的消息',
                type: 'warning',
            })
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