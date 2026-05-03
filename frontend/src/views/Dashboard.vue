<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import {
  dashboardApi,
  TIME_WINDOW_PRESETS,
  type DashboardData,
} from '../api/dashboard'

const STORAGE_KEY = 'offertrack_dashboard_settings'

const data = ref<DashboardData | null>(null)
const loading = ref(false)
const presetIndex = ref(1)
const staleDays = ref(14)

const currentPreset = computed(() => TIME_WINDOW_PRESETS[presetIndex.value])

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const s = JSON.parse(raw)
    if (typeof s.presetIndex === 'number' && TIME_WINDOW_PRESETS[s.presetIndex]) {
      presetIndex.value = s.presetIndex
    }
    if (typeof s.staleDays === 'number' && s.staleDays >= 1 && s.staleDays <= 365) {
      staleDays.value = s.staleDays
    }
  } catch {
    // ignore parse errors
  }
}

function saveSettings() {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ presetIndex: presetIndex.value, staleDays: staleDays.value }),
  )
}

async function load() {
  loading.value = true
  try {
    data.value = await dashboardApi.get({
      past_days: currentPreset.value.past,
      future_days: currentPreset.value.future,
      stale_days: staleDays.value,
    })
  } finally {
    loading.value = false
  }
}

watch([presetIndex, staleDays], () => {
  saveSettings()
  load()
})

onMounted(() => {
  loadSettings()
  load()
})

function fmtDate(s: string) {
  return new Date(s).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function fmtRelative(s: string): string {
  const target = new Date(s)
  const now = new Date()
  const startOfTarget = new Date(target.getFullYear(), target.getMonth(), target.getDate())
  const startOfNow = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diffDays = Math.round(
    (startOfTarget.getTime() - startOfNow.getTime()) / (1000 * 60 * 60 * 24),
  )
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '明天'
  if (diffDays === -1) return '昨天'
  if (diffDays > 1) return `${diffDays} 天后`
  return `${-diffDays} 天前`
}

function relativeColor(s: string): string {
  const target = new Date(s).getTime()
  const diffDays = Math.round((target - Date.now()) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 'text-gray-500'
  if (diffDays <= 1) return 'text-red-600 font-medium'
  if (diffDays <= 3) return 'text-orange-600 font-medium'
  return 'text-green-700'
}

function stageColorClass(stage: string) {
  if (stage === 'Offer 沟通' || stage === '入职') return 'bg-green-100 text-green-700'
  if (stage === '笔试/测评') return 'bg-purple-100 text-purple-700'
  if (['一面', '二面', '三面', '终面', 'HR 面'].includes(stage)) return 'bg-blue-100 text-blue-700'
  return 'bg-yellow-100 text-yellow-700'
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">仪表盘</h2>

    <!-- 4 个数字卡片 -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="text-sm text-gray-500 mb-1">总投递</div>
        <div class="text-3xl font-bold text-gray-800">{{ data?.stats.total ?? '—' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="text-sm text-blue-600 mb-1">面试中</div>
        <div class="text-3xl font-bold text-blue-700">{{ data?.stats.interviewing ?? '—' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="text-sm text-green-600 mb-1">已 Offer</div>
        <div class="text-3xl font-bold text-green-700">{{ data?.stats.offered ?? '—' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="text-sm text-gray-500 mb-1">已结束 / 已拒</div>
        <div class="text-3xl font-bold text-gray-700">{{ data?.stats.ended ?? '—' }}</div>
      </div>
    </div>

    <!-- 近期面试 -->
    <div class="bg-white rounded-lg shadow-sm border p-5 mb-6">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h3 class="text-lg font-bold">近期面试</h3>
        <div class="flex gap-1 bg-gray-100 rounded-md p-1">
          <button
            v-for="(p, i) in TIME_WINDOW_PRESETS"
            :key="p.label"
            class="px-3 py-1 rounded text-sm transition"
            :class="i === presetIndex ? 'bg-white shadow-sm font-medium text-blue-600' : 'text-gray-600 hover:text-gray-800'"
            @click="presetIndex = i"
          >{{ p.label }}</button>
        </div>
      </div>

      <div v-if="loading && !data" class="text-center text-gray-400 py-6 text-sm">加载中…</div>
      <div
        v-else-if="!data || data.upcoming_interviews.length === 0"
        class="text-center text-gray-400 py-6 text-sm"
      >该时间窗口内没有面试节点</div>
      <ul v-else class="space-y-2">
        <li
          v-for="evt in data.upcoming_interviews"
          :key="evt.event_id"
          class="border rounded-md p-3 hover:bg-gray-50"
        >
          <RouterLink :to="`/applications/${evt.application.id}`" class="block">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 min-w-0">
                <span
                  class="inline-block px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap"
                  :class="stageColorClass(evt.stage)"
                >{{ evt.stage }}</span>
                <span class="font-medium text-gray-800 truncate">{{ evt.application.company }}</span>
                <span class="text-sm text-gray-500 truncate">{{ evt.application.position }}</span>
              </div>
              <div class="text-right whitespace-nowrap">
                <div :class="relativeColor(evt.happened_at)" class="text-sm">
                  {{ fmtRelative(evt.happened_at) }}
                </div>
                <div class="text-xs text-gray-400">{{ fmtDate(evt.happened_at) }}</div>
              </div>
            </div>
          </RouterLink>
        </li>
      </ul>
    </div>

    <!-- 疑似挂掉 -->
    <div class="bg-white rounded-lg shadow-sm border p-5">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h3 class="text-lg font-bold">疑似挂掉
          <span class="text-sm font-normal text-gray-500">（投递后无任何节点）</span>
        </h3>
        <div class="flex items-center gap-2 text-sm">
          <span class="text-gray-600">超过</span>
          <input
            v-model.number="staleDays"
            type="number"
            min="1"
            max="365"
            class="w-16 px-2 py-1 border rounded-md text-center focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span class="text-gray-600">天未响应</span>
        </div>
      </div>

      <div
        v-if="!data || data.stale_applications.length === 0"
        class="text-center text-gray-400 py-6 text-sm"
      >没有超过 {{ staleDays }} 天未响应的投递 🎉</div>
      <ul v-else class="space-y-2">
        <li
          v-for="app in data.stale_applications"
          :key="app.id"
          class="border rounded-md p-3 hover:bg-gray-50 bg-yellow-50/40"
        >
          <RouterLink :to="`/applications/${app.id}`" class="block">
            <div class="flex items-center justify-between gap-3">
              <div class="min-w-0">
                <div class="font-medium text-gray-800 truncate">{{ app.company }}</div>
                <div class="text-sm text-gray-500 truncate">{{ app.position }}</div>
              </div>
              <div class="text-right whitespace-nowrap">
                <div class="text-sm text-orange-600 font-medium">{{ app.days_since_applied }} 天前投递</div>
                <div class="text-xs text-gray-400">{{ fmtDate(app.applied_at) }}</div>
              </div>
            </div>
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>
