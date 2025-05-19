<template>
    <component :is="tag" @dblclick="startEditing" :class="['editable', customClass]">
        <textarea v-if="isEditing" v-model="editableContent" @blur="saveContent" @keydown.enter="saveContent"
            class="w-full p-2 border rounded" :rows="tag === 'td' ? 1 : 3" @click.stop></textarea>
        <template v-else>{{ modelValue }}</template>
    </component>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
//可以让内容可编辑
//可以在template被使用: <EditableContent tag="p" v-model="paragraph" custom-class="text-gray-600 mb-8 leading-relaxed" />
const props = defineProps<{
    tag: string;
    modelValue: string;
    customClass?: string;
}>();

const emit = defineEmits(['update:modelValue']);
const isEditing = ref(false);
const editableContent = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
    editableContent.value = newValue;
});

const startEditing = () => {
    isEditing.value = true;
    nextTick(() => {
        const textarea = document.querySelector('textarea');
        if (textarea) {
            textarea.focus();
        }
    });
};

const saveContent = () => {
    isEditing.value = false;
    emit('update:modelValue', editableContent.value);
};
</script>
