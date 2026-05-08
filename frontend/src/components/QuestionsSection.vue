<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { questionsApi, type InterviewQuestion } from '../api/questions'
import MarkdownPreview from './MarkdownPreview.vue'
import QuestionFormModal from './QuestionFormModal.vue'

const props = defineProps<{
  eventId: number
}>()

const items = ref<InterviewQuestion[]>([])
const loading = ref(false)
const expanded = ref<Set<number>>(new Set())
const modalOpen = ref(false)
const editing = ref<InterviewQuestion | null>(null)

async function load() {
  loading.value = true
  try {
    items.value = await questionsApi.list(props.eventId)
  } finally {
    loading.value = false
  }
}

function toggle(id: number) {
  const next = new Set(expanded.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  expanded.value = next
}

function openNew() {
  editing.value = null
  modalOpen.value = true
}

function openEdit(q: InterviewQuestion) {
  editing.value = q
  modalOpen.value = true
}

async function handleSubmit(data: {
  question: string
  reflection: string
  tags: string
}) {
  const payload = { ...data, my_answer: '' }
  if (editing.value) {
    await questionsApi.update(editing.value.id, payload)
  } else {
    await questionsApi.create({ event_id: props.eventId, ...payload })
  }
  modalOpen.value = false
  await load()
}

async function handleDelete(q: InterviewQuestion) {
  if (!confirm('确认删除这道面试题？')) return
  await questionsApi.delete(q.id)
  await load()
}

function firstLine(text: string): string {
  const line = text.split('\n').find(l => l.trim().length > 0) ?? ''
  return line.replace(/^#+\s*/, '')
}

const tagList = computed(() => (q: InterviewQuestion) =>
  q.tags
    .split(/[,，]/)
    .map(t => t.trim())
    .filter(Boolean),
)

onMounted(load)
</script>

<template>
  <div class="mt-3 ml-2 pl-3 border-l-2 border-dashed border-gray-200">
    <div class="flex items-center justify-between mb-2">
      <h4 class="text-sm font-medium text-gray-700">
        面试题 <span v-if="items.length" class="text-gray-400">({{ items.length }})</span>
      </h4>
      <button
        class="text-xs text-blue-600 hover:underline"
        @click="openNew"
      >+ 添加面试题</button>
    </div>

    <div v-if="loading" class="text-xs text-gray-400 py-2">加载中…</div>
    <div v-else-if="items.length === 0" class="text-xs text-gray-400 py-1">
      暂无题目
    </div>
    <ul v-else class="space-y-2">
      <li
        v-for="q in items"
        :key="q.id"
        class="bg-gray-50 border rounded-md overflow-hidden"
      >
        <div
          class="px-3 py-2 flex items-start gap-3 cursor-pointer hover:bg-gray-100"
          @click="toggle(q.id)"
        >
          <span class="text-gray-400 mt-0.5 select-none text-xs">
            {{ expanded.has(q.id) ? '▼' : '▶' }}
          </span>
          <div class="flex-1 min-w-0">
            <div class="text-sm text-gray-800 break-words whitespace-pre-wrap">{{ firstLine(q.question) || '（空题目）' }}</div>
            <div v-if="tagList(q).length" class="mt-1 flex flex-wrap gap-1">
              <span
                v-for="tag in tagList(q)"
                :key="tag"
                class="text-[10px] px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded"
              >{{ tag }}</span>
            </div>
          </div>
          <div class="flex gap-2 text-xs whitespace-nowrap" @click.stop>
            <button class="text-blue-600 hover:underline" @click="openEdit(q)">编辑</button>
            <button class="text-red-600 hover:underline" @click="handleDelete(q)">删除</button>
          </div>
        </div>

        <div v-if="expanded.has(q.id)" class="border-t bg-white px-4 py-3 space-y-4">
          <section>
            <h5 class="text-xs font-semibold text-gray-500 mb-1">题目</h5>
            <MarkdownPreview :model-value="q.question" :editor-id="`q-${q.id}-question`" />
          </section>
          <section v-if="q.reflection">
            <h5 class="text-xs font-semibold text-gray-500 mb-1">复盘</h5>
            <MarkdownPreview :model-value="q.reflection" :editor-id="`q-${q.id}-reflection`" />
          </section>
        </div>
      </li>
    </ul>

    <QuestionFormModal v-model="modalOpen" :initial="editing" @submit="handleSubmit" />
  </div>
</template>
