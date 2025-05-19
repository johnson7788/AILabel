<template>
    <navHeader></navHeader>
    <!-- 搜索框 -->
    <div class="bar flex items-center justify-between flex-row h-16">
        <button class="btn btn-outline btn-info btn-sm" @click="showSidenav = true; isAddPrompt = true">添加</button>
        <div class="relative flex items-center md:mt-0 ml-auto w-1/4">
            <span class="absolute">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                    stroke="currentColor" class="w-5 h-5 mx-3 text-gray-400 dark:text-gray-600">
                    <path stroke-linecap="round" stroke-linejoin="round"
                        d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                </svg>
            </span>
            <input type="text" placeholder="Search"
                class="block w-full py-1.5 pr-5 text-gray-700 bg-white border border-gray-200 rounded-lg md:w-80 placeholder-gray-400/70 pl-11 rtl:pr-11 rtl:pl-5 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-300 focus:ring-blue-300 focus:outline-none focus:ring focus:ring-opacity-40">
        </div>
    </div>
    <table class="border-collapse w-full">
        <thead>
            <tr>
                <th
                    class="p-3 font-bold uppercase bg-gray-200 text-gray-600 border border-gray-300 hidden lg:table-cell">
                    Name</th>
                <th
                    class="p-3 font-bold uppercase bg-gray-200 text-gray-600 border border-gray-300 hidden lg:table-cell">
                    Prompt</th>
                <th
                    class="p-3 font-bold uppercase bg-gray-200 text-gray-600 border border-gray-300 hidden lg:table-cell">
                    Usage</th>
                    <th
                class="p-3 font-bold uppercase bg-gray-200 text-gray-600 border border-gray-300 hidden lg:table-cell">
                    KB</th>
                <th
                    class="p-3 font-bold uppercase w-40 bg-gray-200 text-gray-600 border border-gray-300 hidden lg:table-cell">
                    Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="prompt in prompts" :key="prompt.id"
                class="bg-white lg:hover:bg-gray-100 flex lg:table-row flex-row lg:flex-row flex-wrap lg:flex-no-wrap mb-10 lg:mb-0">
                <td
                    class="w-full lg:w-auto p-3 text-gray-800 text-center border border-b block lg:table-cell relative lg:static">
                    <span class="lg:hidden absolute top-0 left-0 bg-blue-200 px-2 py-1 text-xs font-bold uppercase">Name
                    </span>
                    {{ prompt.name }}
                </td>
                <td
                    class="w-full lg:w-auto p-3 text-gray-800 text-center border border-b text-center block lg:table-cell relative lg:static">
                    <span
                        class="lg:hidden absolute top-0 left-0 bg-blue-200 px-2 py-1 text-xs font-bold uppercase">Prompt</span>
                    {{ prompt.prompt }}
                </td>
                <td
                    class="w-full lg:w-auto p-3 text-gray-800 text-center border border-b text-center block lg:table-cell relative lg:static">
                    <span
                        class="lg:hidden absolute top-0 left-0 bg-blue-200 px-2 py-1 text-xs font-bold uppercase">Usage</span>
                    <span class="rounded bg-green-400 py-1 px-3 text-xs font-bold">{{ prompt.usage }}</span>
                </td>
                <td
                    class="w-full lg:w-auto p-3 text-gray-800 text-center border border-b text-center block lg:table-cell relative lg:static">
                    <span
                        class="lg:hidden absolute top-0 left-0 bg-blue-200 px-2 py-1 text-xs font-bold uppercase">Usage</span>
                    <span class="rounded bg-red-200 py-1 px-3 text-xs font-bold">{{ prompt.knowledge_base }}</span>
                </td>
                <td
                    class="w-full lg:w-auto p-3 text-gray-800 text-center border border-b text-center block lg:table-cell relative lg:static">
                    <span
                        class="lg:hidden absolute top-0 left-0 bg-blue-200 px-2 py-1 text-xs font-bold uppercase">Actions</span>
                    <a href="#" class="text-blue-400 hover:text-blue-600 underline"
                        @click="showSidenav = true; modifiedPrompt = prompt">修改</a>
                    <a href="#" class="text-blue-400 hover:text-blue-600 underline pl-6"
                        @click="deleteOnePrompt(prompt.name)">删除</a>
                </td>
            </tr>
        </tbody>
    </table>
    <!-- drawer 侧边栏 -->
    <nav class="fixed z-20 h-screen w-1/4 bg-green-200 p-8 right-0 top-0" v-show="showSidenav"
        x-transition:enter="transition ease-out duration-300" x-transition:enter-start="-translate-x-72"
        x-transition:enter-end="translate-x-0" x-transition:leave="transition ease-in duration-300 "
        x-transition:leave-start="translate-x-0" x-transition:leave-end="-translate-x-72" x-cloak>
        <button @click="showSidenav = false">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="black"
                class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
        </button>
        <label class="form-control w-full max-w-xs mb-6">
            <div class="label">
                <span class="label-text">Prompt 名称</span>
            </div>
            <input type="text" v-model="modifiedPrompt.name" placeholder="Type here"
                class="input input-bordered w-full max-w-xs" />
        </label>
        <label class="form-control w-full max-w-xs mb-6">
            <div class="label">
                <span class="label-text">Prompt 内容</span>
            </div>
            <textarea type="text" v-model="modifiedPrompt.prompt" placeholder="Type here"
                class="input input-bordered w-full max-w-xs" />
        </label>
        <label class="form-control w-full max-w-xs mb-6">
            <div class="label">
                <span class="label-text">Prompt 用途</span>
            </div>
            <input type="text" v-model="modifiedPrompt.usage" placeholder="Type here"
                class="input input-bordered w-full max-w-xs" />
        </label>
        <label class="form-control w-full max-w-xs mb-6">
            <div class="label">
                <span class="label-text">如果写知识库，那么answer将从知识库中获取上下文</span>
            </div>
            <input type="text" v-model="modifiedPrompt.knowledge_base" placeholder="Type here"
                class="input input-bordered w-full max-w-xs" />
        </label>
        <div class="flex justify-center">
            <button class="btn btn-outline btn-info mt-6" @click="updateOrAddOnePrompt()">确认</button>
        </div>
    </nav>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import navHeader from './navHeader.vue';
import { getPrompts, deletePrompt, modifyPrompt,addPrompt } from './api.ts';
import { ElNotification } from 'element-plus';
const prompts = ref();
const showSidenav = ref(false);
const modifiedPrompt = ref({
    "name": "",
    "prompt": "",
    "usage": "",
    "knowledge_base": ""
});
const isAddPrompt = ref(false); //控制是否是更新还是添加prompt

async function updateOrAddOnePrompt() {
    //添加新prompt
    if (isAddPrompt.value) {
        const result = await addPrompt(modifiedPrompt.value);
        if (result.code === 0) {
            ElNotification({
                message: `添加数据成功`,
                type: 'info',
            });
            showSidenav.value = false;
            await updatePrompts();
            isAddPrompt.value = false;
            modifiedPrompt.value = {"name": "","prompt": "","usage": "","knowledge_base":""}
        }
        else {
            ElNotification({
                message: `添加数据失败，${result.msg}，请检查接口`,
                type: 'info',
            });
        };
    } else {
        const result = await modifyPrompt(modifiedPrompt.value);
        if (result.code === 0) {
            ElNotification({
                message: `更新数据成功`,
                type: 'info',
            });
            showSidenav.value = false;
            await updatePrompts();
            modifiedPrompt.value = {"name": "","prompt": "","usage": "","knowledge_base":""}
        }
        else {
            ElNotification({
                message: `更新数据失败，${result.msg}，请检查接口`,
                type: 'info',
            });
        };
    }
}

async function deleteOnePrompt(name: string) {
    const result = await deletePrompt({ "name": name });
    if (result.code === 0) {
        ElNotification({
            message: `删除数据成功`,
            type: 'info',
        });
    }
    else {
        ElNotification({
            message: `删除数据失败，${result.msg}`,
            type: 'error',
        });
    };
    await updatePrompts();
}

async function updatePrompts() {
    const result = await getPrompts()
    prompts.value = result.data
}

onMounted(async () => {
    const result = await getPrompts()
    prompts.value = result.data
    console.log(prompts.value)
});

</script>

<style lang="scss" scoped></style>