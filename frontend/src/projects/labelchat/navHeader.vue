<template>
  <div class="main">
    <header class="header">
      <div class="flex justify-end">
        <!-- 菜单代码 -->
        <div class="navbar bg-base-100">
          <div class="flex-1 w-full" v-show="showMenu">
            <nav class="nav w-full">
              <el-menu :default-active="activeIndex" :router="true" class="el-menu-demo" mode="horizontal"
                @select="handleSelect">
                <el-menu-item index="/labelchat/home">主页</el-menu-item>
                <el-sub-menu index="1">
                  <template #title>数据</template>
                  <el-menu-item :index="label2page[defaultLabel]['label']">标注</el-menu-item>
                  <el-menu-item :index="label2page[defaultLabel]['prelabel']">预标注</el-menu-item>
                  <el-menu-item index="/labelchat/review">查看</el-menu-item>
                  <el-menu-item index="/labelchat/stats">统计</el-menu-item>
                </el-sub-menu>
                <el-sub-menu index="2">
                  <template #title>指令</template>
                  <el-menu-item index="/labelchat/sample">采样</el-menu-item>
                  <el-menu-item :index="label2page[defaultLabel]['insgenerate']">指令生成</el-menu-item>
                  <el-menu-item index="/labelchat/instruction_filter">指令过滤</el-menu-item>
                </el-sub-menu>
                <el-sub-menu index="3">
                  <template #title>工具</template>
                  <el-menu-item index="/labelchat/tools_manage">工具管理</el-menu-item>
                  <el-menu-item index="/labelchat/tools_generation">工具生成</el-menu-item>
                </el-sub-menu>
                <el-menu-item index="/labelchat/prompt">提示</el-menu-item>
                <el-menu-item index="/labelchat/manage">管理</el-menu-item>
                <el-menu-item index="/labelchat/test">测试</el-menu-item>
                <el-menu-item index="/labelchat/verify">验证</el-menu-item>
                <el-menu-item index="/labelchat/document">文档</el-menu-item>
              </el-menu>
            </nav>
          </div>
        </div>
        <!-- 用户设置代码 -->
        <div class="flex-none gap-2 my-2">
          <div class="dropdown dropdown-end">
            <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
              <div class="w-6 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                  stroke="#f90926" stroke-width="2" stroke-linecap="square" stroke-linejoin="bevel">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            </div>
            <ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-24">
              <li><a>联系我</a></li>
              <li><a @click="hiddenShowMenu">{{ MenuContent }}</a></li>
              <li><a @click="logout">退出</a></li>
            </ul>
          </div>
        </div>
      </div>
    </header>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRouter } from "vue-router";
import { useSettings } from './store.ts';
const { logoutClear,label2page,defaultLabel } = useSettings();
const router = useRouter();
const showMenu = ref(true);
const MenuContent = ref("隐藏菜单");

function hiddenShowMenu() {
  showMenu.value = !showMenu.value;
  if (showMenu.value) {
    MenuContent.value = "隐藏菜单";
  } else {
    MenuContent.value = "显示菜单";
  }
};

const activeIndex = ref('1')
const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

function logout() {
  localStorage.removeItem("settings"); //移出所有配置信息
  localStorage.removeItem("access_token");
  router.push('/labelchat/login');
};

//检查是否登录
onMounted(() => {
  const token = localStorage.getItem("access_token");
  // if (!token) {
  // 不验证token了，因为白名单的话，没有token
  //   router.push('/labelchat/login');
  // }
});

</script>

<style lang="scss" scoped></style>