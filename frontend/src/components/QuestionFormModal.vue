<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import MarkdownEditor from './MarkdownEditor.vue'
import type { InterviewQuestion } from '../api/questions'

const props = defineProps<{
  modelValue: boolean
  initial?: InterviewQuestion | null
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  submit: [data: { question: string; my_answer: string; reflection: string; tags: string }]
}>()

const question = ref('')
const myAnswer = ref('')
const reflection = ref('')
const tags = ref('')

// 每次打开弹窗刷新会话 ID，避免 md-editor-v3 跨 mount 复用同一 editorId 时残留 DOM
const sessionId = ref(Date.now())
const editorIds = computed(() => ({
  question: `md-question-${sessionId.value}`,
  answer: `md-answer-${sessionId.value}`,
  reflection: `md-reflection-${sessionId.value}`,
}))

watch(() => [props.modelValue, props.initial] as const, ([open, initial]) => {
  if (!open) return
  sessionId.value = Date.now()
  if (initial) {
    question.value = initial.question
    myAnswer.value = initial.my_answer
    reflection.value = initial.reflection
    tags.value = initial.tags
  } else {
    question.value = ''
    myAnswer.value = ''
    reflection.value = ''
    tags.value = ''
  }
})

function close() {
  emit('update:modelValue', false)
}

function submit() {
  if (!question.value.trim()) return
  emit('submit', {
    question: question.value,
    my_answer: myAnswer.value,
    reflection: reflection.value,
    tags: tags.value,
  })
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 bg-white flex flex-col">
    <header class="flex items-center justify-between px-6 py-3 border-b bg-white sticky top-0 z-10">
      <h3 class="text-lg font-bold">{{ initial ? '编辑面试题' : '添加面试题' }}</h3>
      <div class="flex items-center gap-2">
        <button class="px-4 py-1.5 border rounded-md hover:bg-gray-50" @click="close">取消</button>
        <button
          class="px-4 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          @click="submit"
        >保存</button>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto px-6 py-4 max-w-5xl mx-auto w-full space-y-5">
      <div>
        <label class="block text-sm font-medium mb-1">
          标签（逗号分隔，如「算法,二叉树,中等」）
        </label>
        <input
          v-model="tags"
          type="text"
          placeholder="算法, 二叉树, 中等"
          class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">
          题目 <span class="text-red-500">*</span>
        </label>
        <MarkdownEditor
          v-model="question"
          :editor-id="editorIds.question"
          placeholder="题目内容，支持 Markdown 与代码块"
          height="280px"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">我的回答</label>
        <MarkdownEditor
          v-model="myAnswer"
          :editor-id="editorIds.answer"
          placeholder="当时的作答（可贴代码）"
          height="280px"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">复盘</label>
        <MarkdownEditor
          v-model="reflection"
          :editor-id="editorIds.reflection"
          placeholder="事后的最优解、踩过的坑、需要复习的知识点"
          height="280px"
        />
      </div>
    </div>
  </div>
</template>
