<template>
  <div>
    <!-- :ellipsis="false"表示不折叠 -->
    <el-menu
    :ellipsis="false"
    class="el-menu-demo"
    mode="horizontal"
    :router="true"
    @select="handleSelect"
  >
  <el-menu-item
      v-for="route in routes"
      :key="route.path"
      :index="route.path"
    >{{ route.name }}</el-menu-item>
  </el-menu>
  </div>
</template>

<script setup>
import {useRouter} from "vue-router";
import { ref, onMounted } from "vue";
let routes = ref([]);

onMounted(() => {
  let router = useRouter();
  // 获取所有路由信息
  routes = router.getRoutes();
  //过滤掉name=menu的路由,  过滤出只包含menu的路由作为菜单
  routes = routes.filter(route => route.name !== 'menu' && route.path.includes('/menu'));
  // console.log(routes);
});

function handleSelect() {
  // console.log('handle select');
}
</script>
