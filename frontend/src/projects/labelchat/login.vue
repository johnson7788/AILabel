<template>
    <!-- component -->
    <div v-show="error_message"
        class="font-regular block w-full rounded-lg bg-pink-500 p-4 text-base leading-5 text-white opacity-100 z-10 absolute top-0 left-0">
        {{ error_message }}
    </div>
    <div class="relative flex h-full w-full">
        <div class="h-screen w-1/2 bg-black">
            <div class="mx-auto flex h-full w-2/3 flex-col justify-center text-white xl:w-1/2">
                <div>
                    <p class="text-2xl">登录</p>
                </div>
                <div class="mt-10">
                    <form @submit.prevent="submitForm">
                        <div>
                            <label class="mb-2.5 block font-extrabold" for="user">用户名</label>
                            <input type="user" id="user" v-model="formData.username"
                                class="inline-block w-full rounded-full bg-white p-2.5 leading-none text-black placeholder-indigo-900 shadow placeholder:opacity-30"
                                placeholder="" />
                        </div>
                        <div class="mt-4">
                            <label class="mb-2.5 block font-extrabold" for="password">密码</label>
                            <input type="password" id="password" autocomplete="off" v-model="formData.password"
                                class="inline-block w-full rounded-full bg-white p-2.5 leading-none text-black placeholder-indigo-900 shadow" />
                        </div>
                        <div class="mt-4 flex w-full flex-col justify-between sm:flex-row">
                            <!-- Remember me -->
                            <div><input type="checkbox" id="remember" /><label for="remember"
                                    class="mx-2 text-sm">记住我</label></div>
                            <!-- Forgot password -->
                            <div>
                                <a href="#" class="text-sm hover:text-gray-200">忘记密码</a>
                            </div>
                        </div>
                        <div class="my-10">
                            <button class="w-full rounded-full bg-orange-600 p-5 hover:bg-orange-800">登录</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <div class="h-screen w-1/2 bg-blue-600">
            <img src="/src/assets/login_background.jpeg" class="h-full w-full" />
        </div>
    </div>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue';
import axios from 'axios';
import {useRouter } from "vue-router";
const router = useRouter();
const TOOL_API = import.meta.env.VITE_APP_TOOL_API;
const formData = reactive({
    username: '',
    password: '',
});
const error_message = ref("")

const submitForm = () => {
    if (formData.username === "") {
        console.log("用户名不能为空");
        error_message.value = "用户名不能为空"
    }
    if (formData.password === "") {
        console.log("密码不能为空");
        error_message.value = "密码不能为空"
    }
    // 发送登录请求
    if (formData.username !== "" && formData.password !== "") {
        axios.post(TOOL_API + '/login', {
            username: formData.username,
            password: formData.password,})
            .then(response => {
                // 保存JWT到浏览器的localStorage
                localStorage.setItem('access_token', response.data.access_token);

                // 可以根据需要跳转到其他页面
                router.push('/labelchat/home');
            })
            .catch(error => {
                console.error('Error:', error);
                // 处理错误
                error_message.value = "用户名或密码错误" + error
            });
    }
    // 3秒后自动隐藏错误提示信息
    setTimeout(() => {
        error_message.value = "";
    }, 3000);
};

</script>

<style lang="scss" scoped></style>