<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Application } from '../api/applications'

const props = defineProps<{
  modelValue: boolean
  initial?: Application | null
}>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
  submit: [data: {
    company: string
    position: string
    jd: string
    channel: string
    applied_at: string
    note: string
  }]
}>()

const form = ref({
  company: '',
  position: '',
  jd: '',
  channel: '',
  applied_at: '',
  note: '',
})

watch(() => [props.modelValue, props.initial] as const, ([open, initial]) => {
  if (!open) return
  if (initial) {
    form.value = {
      company: initial.company,
      position: initial.position,
      jd: initial.jd,
      channel: initial.channel,
      applied_at: initial.applied_at.slice(0, 16),
      note: initial.note,
    }
  } else {
    const now = new Date()
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
    form.value = {
      company: '',
      position: '',
      jd: '',
      channel: '',
      applied_at: now.toISOString().slice(0, 16),
      note: '',
    }
  }
})

function close() {
  emit('update:modelValue', false)
}

function submit() {
  if (!form.value.company || !form.value.position || !form.value.applied_at) return
  emit('submit', { ...form.value })
}
</script>

<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
      <div class="px-6 py-4 border-b flex items-center justify-between">
        <h3 class="text-lg font-bold">{{ initial ? '编辑投递' : '新建投递' }}</h3>
        <button class="text-gray-400 hover:text-gray-600 text-xl leading-none" @click="close">✕</button>
      </div>
      <form class="px-6 py-4 space-y-4" @submit.prevent="submit">
        <div>
          <label class="block text-sm font-medium mb-1">
            公司名 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.company"
            type="text"
            required
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">
            岗位名 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.position"
            type="text"
            required
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">
            投递时间 <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.applied_at"
            type="datetime-local"
            required
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">投递渠道</label>
          <input
            v-model="form.channel"
            type="text"
            placeholder="BOSS / 内推 / 官网…"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">JD（职位描述，支持 Markdown）</label>
          <textarea
            v-model="form.jd"
            rows="5"
            class="w-full px-3 py-2 border rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">备注</label>
          <textarea
            v-model="form.note"
            rows="2"
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
