<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { PRESET_STAGES, type TimelineEvent } from '../api/events'

const props = defineProps<{
  modelValue: boolean
  initial?: TimelineEvent | null
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  submit: [data: { stage: string; happened_at: string; note: string }]
}>()

const stageSelect = ref<string>('一面')
const customStage = ref('')
const happenedAt = ref('')
const note = ref('')

const isCustom = computed(() => stageSelect.value === '__custom__')

function nowLocalForInput(): string {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
}

watch(() => [props.modelValue, props.initial] as const, ([open, initial]) => {
  if (!open) return
  if (initial) {
    if ((PRESET_STAGES as readonly string[]).includes(initial.stage)) {
      stageSelect.value = initial.stage
      customStage.value = ''
    } else {
      stageSelect.value = '__custom__'
      customStage.value = initial.stage
    }
    happenedAt.value = initial.happened_at.slice(0, 16)
    note.value = initial.note
  } else {
    stageSelect.value = '一面'
    customStage.value = ''
    happenedAt.value = nowLocalForInput()
    note.value = ''
  }
})

function close() {
  emit('update:modelValue', false)
}

function submit() {
  const stage = isCustom.value ? customStage.value.trim() : stageSelect.value
  if (!stage || !happenedAt.value) return
  let happened = happenedAt.value
  if (happened.length === 16) happened += ':00'
  emit('submit', { stage, happened_at: happened, note: note.value })
}
</script>

<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <h3 class="text-lg font-bold">{{ initial ? '编辑节点' : '添加时间线节点' }}</h3>
        <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="close">✕</button>
      </div>
      <form class="px-6 py-4 space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm font-medium mb-1">
            阶段 <span class="text-red-500">*</span>
          </label>
          <select
            v-model="stageSelect"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="s in PRESET_STAGES" :key="s" :value="s">{{ s }}</option>
            <option value="__custom__">自定义…</option>
          </select>
          <input
            v-if="isCustom"
            v-model="customStage"
            type="text"
            placeholder="输入自定义阶段名"
            required
            class="w-full mt-2 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">
            时间 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="happenedAt"
            type="datetime-local"
            required
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">备注</label>
          <textarea
            v-model="note"
            rows="3"
            placeholder="面试官姓名、面试形式、感受……"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            class="px-4 py-2 border rounded-md hover:bg-gray-50"
            @click="close"
          >取消</button>
          <button
            type="submit"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >保存</button>
        </div>
      </form>
    </div>
  </div>
</template>
