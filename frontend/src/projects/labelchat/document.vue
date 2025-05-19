<template>
    <navHeader></navHeader>
    <section>
        <div class="mt-2 p-2  md:flex justify-around">
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">标签页有4种角色，Human,gpt, function_call,observation
                        </span>
                        <span class="text-sm">新增对话时，需要选择1种角色
                        </span>
                        <span class="text-sm">function_call可以手动选择1种工具进行运行
                        </span>
                        <span class="text-sm">observation可以自动运行function_call中的参数
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">Sample按钮
                        </span>
                        <span class="text-sm">Sample按钮是根据管理里面设置的Sample数据自动按顺序抽取的
                        </span>
                        <span class="text-sm">管理里面可以设置Sample的语句
                        </span>
                        <span class="text-sm">管理里面可以设置Sample从哪个样本开始
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">Answer按钮
                        </span>
                        <span class="text-sm">当对话框中的内容不是轮到Human说话的时候都可以点击
                        </span>
                        <span class="text-sm">当使用Sample的时候，自动关联可能用到的工具
                        </span>
                        <span class="text-sm">save按钮会保存当前对话到数据库，并清空当前对话
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-2 p-2  md:flex justify-around">
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">prompt
                        </span>
                        <span class="text-sm">可以添加，修改，删除不同的prompt，用于不同的用途,默认prompt作为system角色加入对话的开头
                        </span>
                        <span class="text-sm">prompt可以和知识库进行关联，当prompt中包括context关键字时，必须提供知识库名称，会自动进行检索
                        </span>
                        <span class="text-sm">prompt中不包含context，但是包含question时，原始对话的每个问题都会带入prompt中进行回答
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">auto按钮
                        </span>
                        <span class="text-sm">自动获取sample数据，自动标注
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">快捷键
                        </span>
                        <span class="text-sm">shift+enter 表示把输入框中数据提交
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-2 p-2  md:flex justify-around">
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">测试
                        </span>
                        <span class="text-sm">可以对训练好的模型使用新标注的测试集数据进行测试
                        </span>
                        <span class="text-sm">可以对测试结果进行统计和绘图
                        </span>
                        <span class="text-sm">可以查看测试集中的错误样本，对比正确和错误的样本
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">验证
                        </span>
                        <span class="text-sm">对标注后的数据集进行重新验证，对有歧义的数据集进行重新标注
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">支持在管理页面配置不同的标注形式
                        </span>
                        <span class="text-sm">不同的标注类型可以支持不同的url，进行不同的标注
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">实体标注支持划线标注
                        </span>
                        <span class="text-sm">支持快捷键1，2，或者q的快速添加
                        </span>
                    </div>
                </div>
            </div>
            <div
                class="mt-16 flex justify-between py-6 px-4 bg-white/30 rounded-lg shadow-lg shadow-indigo-500/40 hover:shadow-xl hover:shadow-blue-500/40">
                <div class="flex items-center space-x-4 px-12">
                    <div class="flex flex-col my-16 space-y-1">
                        <span class="font-bold">LLM辅助标注预先标注
                        </span>
                        <span class="text-sm">对于Agent的标注，由于Agent需要多次调用LLM，所以预先根据问题进行LLM标注后，人工进行校验，这样速度会比较快
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