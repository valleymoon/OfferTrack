<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { applicationsApi, type Application } from '../api/applications'
import ApplicationFormModal from '../components/ApplicationFormModal.vue'
import LinkifiedText from '../components/LinkifiedText.vue'

const items = ref<Application[]>([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const modalOpen = ref(false)
const editing = ref<Application | null>(null)

const STATUS_OPTIONS = ['投递中', '面试中', '已 Offer', '已拒', '已结束']

const filtered = computed(() => {
  return items.value.filter(it => {
    const matchesSearch =
      !search.value ||
      it.company.includes(search.value) ||
      it.position.includes(search.value)
    const matchesStatus = !statusFilter.value || it.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

async function loadAll() {
  loading.value = true
  try {
    items.value = await applicationsApi.list()
  } finally {
    loading.value = false
  }
}

function openNew() {
  editing.value = null
  modalOpen.value = true
}

function openEdit(item: Application) {
  editing.value = item
  modalOpen.value = true
}

async function handleSubmit(data: {
  company: string
  position: string
  jd: string
  channel: string
  applied_at: string
  note: string
}) {
  const payload = { ...data }
  if (payload.applied_at && payload.applied_at.length === 16) {
    payload.applied_at += ':00'
  }
  if (editing.value) {
    await applicationsApi.update(editing.value.id, payload)
  } else {
    await applicationsApi.create(payload)
  }
  modalOpen.value = false
  await loadAll()
}

async function handleDelete(item: Application) {
  if (!confirm(`确认删除「${item.company} - ${item.position}」？`)) return
  await applicationsApi.delete(item.id)
  await loadAll()
}

function statusBadgeClass(status: string) {
  const map: Record<string, string> = {
    '投递中': 'bg-gray-100 text-gray-700',
    '面试中': 'bg-blue-100 text-blue-700',
    '已 Offer': 'bg-green-100 text-green-700',
    '已拒': 'bg-red-100 text-red-700',
    '已结束': 'bg-gray-100 text-gray-500',
  }
  return map[status] ?? 'bg-gray-100 text-gray-700'
}

function fmtDate(s: string) {
  return new Date(s).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' })
}

onMounted(loadAll)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold">投递记录</h2>
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        @click="openNew"
      >+ 新建投递</button>
    </div>

    <div class="bg-white rounded-lg shadow-sm border p-4 mb-4 flex gap-3">
      <input
        v-model="search"
        type="text"
        placeholder="搜索公司或岗位…"
        class="flex-1 px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select
        v-model="statusFilter"
        class="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">全部状态</option>
        <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div v-if="loading" class="text-center text-gray-500 py-12">加载中…</div>
    <div
      v-else-if="filtered.length === 0"
      class="text-center text-gray-500 py-12 bg-white rounded-lg border"
    >
      暂无投递记录，点击右上角「+ 新建投递」开始记录吧
    </div>
    <div v-else class="bg-white rounded-lg shadow-sm border overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50 border-b">
          <tr class="text-left text-sm">
            <th class="px-4 py-3 font-medium text-gray-700">公司 / 岗位</th>
            <th class="px-4 py-3 font-medium text-gray-700">渠道</th>
            <th class="px-4 py-3 font-medium text-gray-700">投递时间</th>
            <th class="px-4 py-3 font-medium text-gray-700">状态</th>
            <th class="px-4 py-3 font-medium text-gray-700 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="item in filtered" :key="item.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <RouterLink
                :to="`/applications/${item.id}`"
                class="font-medium text-gray-900 hover:text-blue-600"
              >{{ item.company }}</RouterLink>
              <div class="text-sm text-gray-500">{{ item.position }}</div>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600 max-w-xs">
              <LinkifiedText v-if="item.channel" :text="item.channel" />
              <span v-else>—</span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ fmtDate(item.applied_at) }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-block px-2 py-0.5 rounded text-xs"
                :class="statusBadgeClass(item.status)"
              >{{ item.status }}</span>
            </td>
            <td class="px-4 py-3 text-right text-sm whitespace-nowrap">
              <button class="text-blue-600 hover:underline mr-3" @click="openEdit(item)">编辑</button>
              <button class="text-red-600 hover:underline" @click="handleDelete(item)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ApplicationFormModal v-model="modalOpen" :initial="editing" @submit="handleSubmit" />
  </div>
</template>
