<script setup lang="ts">
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

const props = defineProps<{
  modelValue: string
  height?: string
  placeholder?: string
  editorId?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [v: string]
}>()

function onChange(v: string) {
  emit('update:modelValue', v)
}
</script>

<template>
  <MdEditor
    :model-value="modelValue"
    :editor-id="editorId"
    :placeholder="placeholder"
    language="zh-CN"
    :preview="false"
    :toolbars-exclude="['github', 'save', 'pageFullscreen']"
    :style="{ height: height ?? '260px' }"
    @on-change="onChange"
  />
</template>
