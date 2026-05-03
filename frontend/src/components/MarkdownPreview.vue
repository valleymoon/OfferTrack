<script setup lang="ts">
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

defineProps<{
  modelValue: string
  editorId?: string
}>()
</script>

<template>
  <MdPreview :model-value="modelValue" :editor-id="editorId" language="zh-CN" />
</template>
