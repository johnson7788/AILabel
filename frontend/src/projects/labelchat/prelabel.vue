<template>
    <navHeader></navHeader>
    <section>
        <div class="mt-2 p-2  md:flex justify-around">
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">数据预标注
                        </span>
                        <span class="text-sm">已知一些问题，首先使用模型对这些问题进行预标注
                        </span>
                        <span class="text-sm">主要针对回答问题较慢的情况
                        </span>
                        <span class="text-sm">当用户使用sample按钮时，自动获取问题和缓存的结果
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script lang="ts" setup>
import navHeader from './navHeader.vue';

</script>

<style lang="scss" scoped></style>