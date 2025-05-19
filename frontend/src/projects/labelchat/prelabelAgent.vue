<template>
    <navHeader></navHeader>
    <section>
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
        <div class="flex float-end">
            <button class="btn btn-info mr-4" @click="inverseSelect">反选</button>
            <button class="btn btn-success mr-4" :disabled="generating" @click="generateAnswer">生成</button>
        </div>
        <el-table :data="tableData" style="width: 100%" class="mt-10">
            <el-table-column prop="id" label="id" width="200" />
            <el-table-column prop="question" label="question" width="600" />
            <!-- status表示是否已经缓存了问答结果 -->
            <el-table-column prop="status" label="status" width="200" />
            <el-table-column fixed="right" label="Operations" width="400">
                <template #default="scope">
                    <el-checkbox v-model="tableData[scope.$index].checked">勾选</el-checkbox>
                </template>
            </el-table-column>
        </el-table>
    </section>
</template>

<script lang="ts" setup>
import { ref, onMounted, toRefs, watch } from 'vue';
import axios from 'axios';
import { ElNotification } from 'element-plus';
import navHeader from './navHeader.vue';
import { getPromptsQuestions, queryQuestionLabel, saveChat } from './api.ts';
const prompts_questions = ref();
const selectedPrompt = ref();
const total_question_num = ref(0);
const tableData = ref([]);
const GEN_API = import.meta.env.VITE_APP_GEN_QA_AGENT_API;
const generating = ref(false);

watch(selectedPrompt, async (newVal, oldVal) => {
    //更细total_question_num, 根据all_questions中prompt等于newVal的中的内容来筛选
    total_question_num.value = prompts_questions.value.filter(item => item.name === newVal)[0].number;
    console.log("total_question_num", total_question_num.value);
    const questions = prompts_questions.value.filter(item => item.name === newVal)[0].questions;
    await updateTableData(questions);
});

async function generateAnswer() {
    //对tableData中选中的数据进行回答，回答之后保存起来
    const checked_questions = tableData.value.filter(item => item.checked);
    console.log("开始对这些questions进行回答:", checked_questions)
    // 遍历checked_questions
    checked_questions.forEach(async (item,index) => {
        generating.value = true
        const question_id = item.id
        let messages = [{
            "id": 1,
            "role": "user",
            "content": item.question
        }]
        const res = await axios.post(
            `${GEN_API}/api/answer_messages`,
            { "workflow": true, "messages": messages },
        )
        console.log(res)
        // 解析数据，生成messages
        const data = res.data
        const msg = data.msg
        if (data.code == 0) {
            const data_result = data.data
            const answer = data_result.output
            const workflow_output = data_result.workflow_output
            const intermidiates = data_result.intermidiates
            messages.push({
                id: messages[messages.length - 1].id + 1,
                role: "SOP",
                content: workflow_output,
            });
            //遍历intermidiates
            intermidiates.forEach((intermediate) => {
                const agent_status = intermediate["status"]
                if (agent_status === "AgentAction") {
                    messages.push({
                        id: messages[messages.length - 1].id + 1,
                        role: "thought",
                        content: intermediate["thought"],
                    });
                    messages.push({
                        id: messages[messages.length - 1].id + 1,
                        role: "observation",
                        content: intermediate["observation"],
                    });
                } else {
                    messages.push({
                        id: messages[messages.length - 1].id + 1,
                        role: "thought",
                        content: intermediate["thought"],
                    });
                }
            });
            //将当前的问题记录下来
            messages.push({
                id: messages[messages.length - 1].id + 1,
                role: "assistant",
                content: answer,
                meta: data_result
            });
            //保存到llmlabel中
            const save_res = await saveChat({
                "id": question_id,
                "prompt": selectedPrompt.value,
                "messages": messages,
                "collection": "llmlabel",
            })
            console.log("save_res", save_res)
            if (save_res.code === 0) {
                ElNotification({
                    title: '成功',
                    message: `第${index+1}个问题生成回答成功`,
                    type: 'success',
                })
            } else {
                ElNotification({
                    title: '错误',
                    message: `第${index+1}个问题保存回答失败:` + msg,
                    type: 'warning',
                })
            }
        } else {
            ElNotification({
                title: '错误',
                message: `第${index+1}个问题生成回答失败:` + msg,
                type: 'warning',
            })
        }
        generating.value = false
    });
}

function inverseSelect() {
    //对tableData中的数据进行反选
    tableData.value.forEach(item => {
        item.checked = !item.checked
    })
}


async function updateTableData(questions) {
    //更新表格数据, 根据问题获取问题的标注状态
    const result = await queryQuestionLabel({ questions: questions })
    console.log("query_questions result", result)
    const result_data = result.data
    //默认让tableData.value中status是unlabled的都选中
    tableData.value = result_data.map(item => {
        if (item.status === "unlabeled") {
            item.checked = true;
        }
        return item;
    })
};

onMounted(async () => {
    const result = await getPromptsQuestions()
    console.log(result.data)
    prompts_questions.value = result.data
});

</script>

<style lang="scss" scoped></style>