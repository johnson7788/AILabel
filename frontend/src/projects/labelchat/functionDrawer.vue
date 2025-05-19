<template>
    <div class="function">
        <!-- 获取所有函数名称并添加点击事件 ,<span class="loading loading-spinner" v-if="loading"></span>-->
        <button class="btn btn-outline btn-success" v-for="(value, name) of tools_data" :key="name" @click="displayOptions(name)" text bg>
        <span class="loading loading-spinner" v-if="loading === name"></span>
        {{name}}
        </button>
        <div v-for="(value, name) of tools_data" :key="name">
            <div v-if="tools_display.get(name)">
                <el-drawer v-model="drawerOpening" :title="value.description" :with-header="true">
                    <div class="params" v-for="param of value.params" :key="param.name">
                        <el-form label-width="120px">
                            <el-form-item :label="param.name">
                                <div>{{ param.type }}: {{ param.description }}</div>
                                <el-input v-model="param.value" :placeholder="param.required ? '必填' : '可选'" />
                            </el-form-item>
                        </el-form>
                    </div>
                    <el-button type="success" @click="submitParams(name)">确认</el-button>
                </el-drawer>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, toRefs } from 'vue';
import { getTools } from './api.ts'
import { ElNotification } from 'element-plus'
import { useMessageStore } from './store.ts'
import {RunFunction} from './utils.ts'
import internal from 'stream';
import { Integer } from 'neo4j-driver';
const { currentQuestion, tools_data } = toRefs(useMessageStore())
const tools_display = ref(new Map()); //保存显示哪个drawer，抽屉
const drawerOpening = ref(false);
const loading = ref("");

function getRandomToolCallId() {
    var chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    var id = 'call_';
    for (var i = 0; i < 24; i++) {
        id += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return id;
}


async function submitParams(name) {
    // 点击确认按钮，提交参数
    const params = tools_data.value[name].params
    console.log("提交参数:", params)
    //检查提交是否符合要求，如果符合，提示成功
    let verify = true
    params.forEach((param) => {
        if (param.required && !param.value) {
            ElNotification({
                message: `参数${param.name}为必填项，请检查`,
                type: 'warning',
            })
            verify = false;
        }
    });
    if (verify) {
        // 处理数据，生成function组成的消息, 修改currentQuestion中的message值
        let args = params.reduce((obj, item) => {
            obj[item.name] = item.value;
            return obj;
        }, {});
        const id = getRandomToolCallId(); //为每个函数调用生成唯一id
        let message = [{
            "name": name,
            "id": id,
            "arguments": args
        }]
        //导出messages为JSON字符串
        const question = JSON.stringify(message)
        currentQuestion.value.question = question
        ElNotification({
            message: '参数提交成功',
            type: 'info',
        })
        // 关闭抽屉
        drawerOpening.value = false;
        // 开始运行函数
        loading.value = name
        await RunFunction()
        loading.value = ""
    }
}

function displayOptions(name: string) {
    //先设置所有都为false
    Object.keys(tools_data.value).map((key) => {
        tools_display.value.set(key, false)
    });
    //控制显示哪个drawer
    tools_display.value.set(name, !tools_display.value.get(name))
    console.log("显示drawer:", name, tools_display.value)
    drawerOpening.value = true
}

onMounted(async () => {
    console.log("tools_data",tools_data.value)
    if (tools_data.value) {
        //遍历object tools_data.value, 得到每个函数的名称，默认都不显示drawer抽屉
        Object.keys(tools_data.value).map((key) => {
            tools_display.value.set(key, false)
            const params = tools_data.value[key].params
            //同时设置每个函数都添加1个空的value
            for (let i = 0; i < params.length; i++) {
                tools_data.value[key].params[i].value = ''
            }
        });
    }
})
</script>

<style lang="scss" scoped></style>