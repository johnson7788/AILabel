<script setup lang="ts">
import SemanticZoom from './c.vue';

const data = {
    "children": [
        {
            "children": [
                {
                    "id": "103171681b8853e9",
                    "topic": "生成数十个不同的创意"
                },
                {
                    "id": "103173e9e0da3b05",
                    "topic": "https://seenapse.ai/"
                }
            ],
            "id": "1031515bc584ffdb",
            "topic": "Seenapse"
        },
        {
            "children": [
                {
                    "children": [
                        {
                            "id": "288bf473d3dab9bf",
                            "topic": "CosyVoice：基于监督语义令牌的可扩展多语言零样本文本转语音合成器"
                        },
                        {
                            "id": "288bf7048cf4f43a",
                            "topic": "https://arxiv.org/abs/2407.05407"
                        }
                    ],
                    "id": "115f5108e5635e42",
                    "topic": "论文标题"
                }
            ],
            "id": "papers",
            "topic": "论文"
        },
        {
            "children": [
                {
                    "id": "191037c4kcfffaad",
                    "topic": "创建产品概念（也是 Photoshop 插件）"
                },
                {
                    "id": "191037c4fcxffwad",
                    "topic": "https://stablediffusionweb.com/"
                }
            ],
            "id": "191037c4fcf30936",
            "topic": "Stable Diffusion"
        },
        {
            "children": [
                {
                    "id": "191037d4fcfffavd",
                    "topic": "让你的绘图秒变成现实"
                },
                {
                    "id": "191037cqfcfffaxd",
                    "topic": "https://vizcom.co/"
                }
            ],
            "id": "191037c4fcf8ba85",
            "topic": "Vizcom"
        }
    ],
    "id": "root",
    "topic": "AI工具大全"
};
</script>

<template>
    <div class="min-h-screen bg-gray-900 flex items-center justify-center">
        <SemanticZoom :data="data" />
    </div>
</template>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;
</style>