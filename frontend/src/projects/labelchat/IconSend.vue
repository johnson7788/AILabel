<script setup>
//父组件可以给这里传颜色
defineProps({
    color: {
        type: String,
        default: '#00DC82',
    },
    width: {
        type: String,
        default: '40',
    },
    height: {
        type: String,
        default: '40',
    }
})
</script>

<template>
    <svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" fill="red"
        aria-hidden="true" focusable="false" class="" :width="width" :height="height">
        <defs>
            <symbol id="mshd-send" viewBox="0 0 1024 1024">
                <path
                    d="M525.952 537.514667l-313.557333 31.274666-82.474667 272.256a43.093333 43.093333 0 0 0 12.288 44.714667 39.936 39.936 0 0 0 44.672 5.973333l687.146667-343.338666a40.490667 40.490667 0 0 0 21.973333-36.266667c0-15.402667-8.533333-29.482667-21.973333-36.266667L187.349333 132.266667a39.893333 39.893333 0 0 0-44.672 5.973333c-12.373333 11.008-17.237333 28.586667-12.330666 44.672l82.517333 272.256 312.96 31.317333c12.629333 1.28 22.272 12.288 22.272 25.386667a25.258667 25.258667 0 0 1-22.272 25.386667l0.128 0.256z">
                </path>
            </symbol>
        </defs>
        <use xlink:href="#mshd-send" fill-opacity="1" :fill="color"></use>
    </svg>
</template>