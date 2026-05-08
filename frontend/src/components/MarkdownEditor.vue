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
    class="ot-md-editor"
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

<style scoped>
/* 让中文长文本（无空格）能在编辑器与预览区里正常换行，避免横向溢出被裁掉看起来像 "..." 折叠 */
.ot-md-editor :deep(.cm-line),
.ot-md-editor :deep(.cm-content),
.ot-md-editor :deep(textarea),
.ot-md-editor :deep(.md-editor-preview),
.ot-md-editor :deep(.md-editor-preview p),
.ot-md-editor :deep(.md-editor-preview pre),
.ot-md-editor :deep(.md-editor-preview code) {
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}
</style>
