<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicationsApi, type Application } from '../api/applications'
import { eventsApi, type TimelineEvent } from '../api/events'
import ApplicationFormModal from '../components/ApplicationFormModal.vue'
import TimelineEventModal from '../components/TimelineEventModal.vue'
import QuestionsSection from '../components/QuestionsSection.vue'
import LinkifiedText from '../components/LinkifiedText.vue'
import { isInterviewLikeStage } from '../api/questions'

const route = useRoute()
const router = useRouter()

const appId = computed(() => Number(route.params.id))
const application = ref<Application | null>(null)
const events = ref<TimelineEvent[]>([])
const loading = ref(false)

const appModalOpen = ref(false)
const eventModalOpen = ref(false)
const editingEvent = ref<TimelineEvent | null>(null)

async function loadAll() {
  loading.value = true
  try {
    const [app, evts] = await Promise.all([
      applicationsApi.get(appId.value),
      eventsApi.list(appId.value),
    ])
    application.value = app
    events.value = evts
  } finally {
    loading.value = false
  }
}

async function handleAppSubmit(data: {
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
  await applicationsApi.update(appId.value, payload)
  appModalOpen.value = false
  await loadAll()
}

async function handleAppDelete() {
  if (!application.value) return
  if (!confirm(`删除整条投递「${application.value.company} - ${application.value.position}」？所有时间线节点也会一起删除。`)) return
  await applicationsApi.delete(appId.value)
  router.push('/applications')
}

function openNewEvent() {
  editingEvent.value = null
  eventModalOpen.value = true
}

function openEditEvent(evt: TimelineEvent) {
  editingEvent.value = evt
  eventModalOpen.value = true
}

async function handleEventSubmit(data: {
  stage: string
  happened_at: string
  note: string
}) {
  if (editingEvent.value) {
    await eventsApi.update(editingEvent.value.id, data)
  } else {
    await eventsApi.create({ application_id: appId.value, ...data })
  }
  eventModalOpen.value = false
  await loadAll()
}

async function handleEventDelete(evt: TimelineEvent) {
  if (!confirm(`删除节点「${evt.stage}」？`)) return
  await eventsApi.delete(evt.id)
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

function stageColorClass(stage: string) {
  if (stage === 'Offer 沟通' || stage === '入职') return 'bg-green-100 text-green-700'
  if (stage === '被拒') return 'bg-red-100 text-red-700'
  if (stage === '主动放弃' || stage === '泡池子') return 'bg-gray-200 text-gray-600'
  if (stage === '笔试/测评') return 'bg-purple-100 text-purple-700'
  if (['一面', '二面', '三面', '终面', 'HR 面'].includes(stage)) return 'bg-blue-100 text-blue-700'
  return 'bg-yellow-100 text-yellow-700'
}

function fmtDateTime(s: string) {
  return new Date(s).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadAll)
</script>

<template>
  <div>
    <RouterLink to="/applications" class="text-blue-600 hover:underline mb-4 inline-block">
      ← 返回列表
    </RouterLink>

    <div v-if="loading && !application" class="text-center text-gray-500 py-12">加载中…</div>

    <template v-else-if="application">
      <!-- 投递基本信息 -->
      <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-2xl font-bold">{{ application.company }}</h2>
            <p class="text-gray-600 mt-1">{{ application.position }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span
              class="inline-block px-3 py-1 rounded text-sm"
              :class="statusBadgeClass(application.status)"
            >{{ application.status }}</span>
            <button
              class="px-3 py-1 border rounded text-sm hover:bg-gray-50"
              @click="appModalOpen = true"
            >编辑</button>
            <button
              class="px-3 py-1 border border-red-300 text-red-600 rounded text-sm hover:bg-red-50"
              @click="handleAppDelete"
            >删除</button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm mb-4">
          <div>
            <span class="text-gray-500">投递时间：</span>
            <span>{{ fmtDateTime(application.applied_at) }}</span>
          </div>
          <div class="min-w-0">
            <span class="text-gray-500">投递渠道：</span>
            <LinkifiedText v-if="application.channel" :text="application.channel" />
            <span v-else>—</span>
          </div>
        </div>

        <div v-if="application.note" class="text-sm bg-yellow-50 border border-yellow-200 rounded px-3 py-2 mb-4">
          <span class="text-gray-500">备注：</span>{{ application.note }}
        </div>

        <details v-if="application.jd" class="text-sm">
          <summary class="cursor-pointer text-gray-700 hover:text-gray-900 font-medium">
            JD（点击展开）
          </summary>
          <div class="mt-2 p-3 bg-gray-50 border rounded font-mono text-xs">
            <LinkifiedText :text="application.jd" />
          </div>
        </details>
      </div>

      <!-- 时间线 -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold">时间线</h3>
          <button
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
            @click="openNewEvent"
          >+ 添加节点</button>
        </div>

        <div v-if="events.length === 0" class="text-center text-gray-500 py-8">
          暂无节点。每次面试后点「+ 添加节点」记录一笔吧
        </div>

        <ol v-else class="relative border-l-2 border-gray-200 ml-3 space-y-6">
          <li v-for="evt in events" :key="evt.id" class="pl-6 relative">
            <span class="absolute -left-[7px] top-2 w-3 h-3 rounded-full bg-blue-500 border-2 border-white"></span>
            <div class="flex items-start justify-between gap-3">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span
                    class="inline-block px-2 py-0.5 rounded text-xs font-medium"
                    :class="stageColorClass(evt.stage)"
                  >{{ evt.stage }}</span>
                  <span class="text-xs text-gray-500">{{ fmtDateTime(evt.happened_at) }}</span>
                </div>
                <p v-if="evt.note" class="text-sm text-gray-700 whitespace-pre-wrap">{{ evt.note }}</p>
              </div>
              <div class="flex gap-2 text-sm whitespace-nowrap">
                <button class="text-blue-600 hover:underline" @click="openEditEvent(evt)">编辑</button>
                <button class="text-red-600 hover:underline" @click="handleEventDelete(evt)">删除</button>
              </div>
            </div>
            <QuestionsSection v-if="isInterviewLikeStage(evt.stage)" :event-id="evt.id" />
          </li>
        </ol>
      </div>

      <ApplicationFormModal
        v-model="appModalOpen"
        :initial="application"
        @submit="handleAppSubmit"
      />
      <TimelineEventModal
        v-model="eventModalOpen"
        :initial="editingEvent"
        @submit="handleEventSubmit"
      />
    </template>
  </div>
</template>
