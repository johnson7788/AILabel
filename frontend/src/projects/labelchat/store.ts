import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'

export const useMessageStore = defineStore('message', () => {
    const currentQuestion = ref({
        question: '',
        question_id: -1,
        question_type: '',
    })
    // const messages = ref([
    //     {
    //         id: 1,
    //         role: "human",
    //         content: "你好",
    //     },
    //     {
    //         id: 2,
    //         role: "gpt",
    //         content: "hi,我有什么可以帮助您的？",
    //     },
    //     {
    //         id: 3,
    //         role: "function_call",
    //         content: '{"name": "query_neo4j", "arguments": {"cql": "MATCH p=()-[r:BRAND_IS]->(n:Brand {name:\\"汤姆·福特\\"}) return p limit 30"}}',
    //     },
    //     {
    //         id: 4,
    //         role: "observation",
    //         content: "xxxxxx",
    //     },
    //     {
    //         id: 5,
    //         role: "gpt",
    //         content: "好的，30个搜索到的产品分别是：xxx,xxx",
    //     }
    // ])
    const messages = ref([]);
    const message_tool_names = computed(() => {
        //根据messages，获取所有使用到的工具的名称
        const names = []
        messages.value.forEach(message => {
            if (message.role === "function_call") {
                const json = JSON.parse(message.content)
                names.push(json.name)
            }
        });
        return names
    });
    //函数调用结果
    const function_results = ref([])
    function AddHumanMsg() {
        // 点击按钮，生成一条人类消息
        currentQuestion.value.question_id = messages.value.length + 1
        currentQuestion.value.question_type = 'human'
    }
    function AddGptMsg() {
        // 点击按钮，生成一条gpt消息
        currentQuestion.value.question_id = messages.value.length + 1
        currentQuestion.value.question_type = 'gpt'
    }

    function AddFunctionMsg() {
        // 点击按钮，生成一条function_call消息
        currentQuestion.value.question_id = messages.value.length + 1
        currentQuestion.value.question_type = 'function_call'
    }

    function AddObservationMsg() {
        // 点击按钮，生成一条observation消息
        currentQuestion.value.question_id = messages.value.length + 1
        currentQuestion.value.question_type = 'observation'
    }
    const tools_data = ref();
    const multi_llm_results = ref([]); //多个模型的回答结果
    const display_neo4j_meta = ref(); //neo4j查询结果的元数据
    const display_plot_meta = ref(); //普通绘图的元数据
    const need_summary = ref(true); //对于工具运行后的结果，是否需要LLM再次进行summary汇总，默认是需要的
    const select_nodes = ref([]); //用户选择的知识图谱的节点id
    return { select_nodes, need_summary, display_neo4j_meta, display_plot_meta, multi_llm_results, tools_data, message_tool_names, currentQuestion, messages, function_results, AddHumanMsg, AddGptMsg, AddFunctionMsg, AddObservationMsg }
})

export const useSettings = defineStore(
    'settings',
    () => {
        const selectedLLM = ref(['chatgpt']);
        const usecache = ref(true);  //llm模型是否使用缓存
        const norepeat = ref(true);  //是否采样数据去重
        const selectedSample = ref(''); //选中的采样的问题
        const sample_idx = ref(0); //采样的索引
        const currentPrompt = ref("default");
        const defaultLabel = ref("default")
        const label2page = ref({
            "default": {
                "label": "/labelchat/label",
                "prelabel": "/labelchat/prelabel",
                "insgenerate": "/labelchat/instruction_generation", //指令生成
            },
            "other": {
                "label": "/labelchat/label",
                "prelabel": "/labelchat/prelabel",
                "insgenerate": "/labelchat/instruction_generation", //指令生成
            },
            "agent": {
                "label": "/labelchat/labelAgent",
                "prelabel": "/labelchat/prelabelAgent",
                "insgenerate": "/labelchat/instruction_generation_agent", //指令生成
            },
            "beauty_agent": {
                "label": "/labelchat/labelBeautyAgent",
                "prelabel": "/labelchat/prelabelBeautyAgent",
                "insgenerate": "/labelchat/instruction_generation_Beautyagent", //指令生成
            },
        })
        return {
            norepeat,
            defaultLabel,
            label2page,
            currentPrompt,
            usecache,
            selectedLLM,
            selectedSample,
            sample_idx,
        };
    },
    {
        persist: {
            storage: localStorage,
        },
    }
);