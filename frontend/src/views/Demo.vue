<script setup>
import Menu from './Menu.vue';
</script>

<template>
  <div class="container">
    <div class="menu">
      <el-row>
        <el-col :span="24">
          <Menu></Menu>
        </el-col>
      </el-row>
    </div>
    <router-view></router-view>
  </div>
</template>

<style>
.container {
  display: flex;
  flex-direction: column;
  height: 200vh;
}

.menu {
  width: 100%;
  height: 50px;
  background-color: #ccc;
}

.content {
  margin-top: 40px;
  width: 100%;
  height: calc(100vh - 50px);
  background-color: #fff;
}
</style>