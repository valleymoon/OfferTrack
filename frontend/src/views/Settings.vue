<script setup lang="ts">
import { ref } from 'vue'
import { backupApi, type BackupPayload, type ImportResult } from '../api/backup'

const exporting = ref(false)
const importing = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const importResult = ref<ImportResult | null>(null)
const errorMsg = ref('')

async function handleExport() {
  exporting.value = true
  errorMsg.value = ''
  try {
    const data = await backupApi.export()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    a.download = `offertrack-backup-${today}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (err: any) {
    errorMsg.value = `导出失败：${err.message ?? err}`
  } finally {
    exporting.value = false
  }
}

function pickFile() {
  fileInput.value?.click()
}

async function handleFile(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  let payload: BackupPayload
  try {
    const text = await file.text()
    payload = JSON.parse(text)
  } catch {
    errorMsg.value = '文件不是合法的 JSON'
    target.value = ''
    return
  }

  if (typeof payload?.version !== 'number' || !Array.isArray(payload.applications)) {
    errorMsg.value = '文件不是 OfferTrack 备份格式'
    target.value = ''
    return
  }

  const summary = `备份包含：投递 ${payload.applications.length} 条 / 节点 ${payload.events.length} 条 / 题目 ${payload.questions.length} 条`
  const choice = window.prompt(
    `${summary}\n\n请选择导入方式：\n  输入 "overwrite" → 清空当前数据后导入\n  输入 "merge" → 合并到现有数据（追加，不冲突）\n  其他任意输入 → 取消`,
    'merge',
  )
  if (choice !== 'overwrite' && choice !== 'merge') {
    target.value = ''
    return
  }
  if (choice === 'overwrite') {
    if (!confirm('⚠️ 覆盖模式会清空当前所有数据再导入。确定继续？')) {
      target.value = ''
      return
    }
  }

  importing.value = true
  errorMsg.value = ''
  importResult.value = null
  try {
    importResult.value = await backupApi.import(choice, payload)
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    errorMsg.value = `导入失败：${detail ?? err.message ?? err}`
  } finally {
    importing.value = false
    target.value = ''
  }
}
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">设置</h2>

    <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <h3 class="text-lg font-bold mb-2">导出备份</h3>
      <p class="text-sm text-gray-600 mb-4">
        把所有投递、时间线节点、面试题打包成 JSON 文件，下载到本地。
        建议定期备份，或在换电脑时迁移用。
      </p>
      <button
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        :disabled="exporting"
        @click="handleExport"
      >{{ exporting ? '导出中…' : '⬇ 导出为 JSON' }}</button>
    </div>

    <div class="bg-white rounded-lg shadow-sm border p-6">
      <h3 class="text-lg font-bold mb-2">导入备份</h3>
      <p class="text-sm text-gray-600 mb-1">选择之前导出的 JSON 文件，支持两种模式：</p>
      <ul class="text-sm text-gray-600 mb-4 list-disc list-inside space-y-0.5">
        <li><strong>覆盖（overwrite）</strong>：清空当前所有数据再导入备份</li>
        <li><strong>合并（merge）</strong>：把备份的内容追加到现有数据（推荐，无冲突）</li>
      </ul>
      <button
        class="px-4 py-2 border rounded-md hover:bg-gray-50 disabled:opacity-50"
        :disabled="importing"
        @click="pickFile"
      >{{ importing ? '导入中…' : '⬆ 选择文件并导入' }}</button>
      <input
        ref="fileInput"
        type="file"
        accept="application/json,.json"
        class="hidden"
        @change="handleFile"
      />

      <div
        v-if="importResult"
        class="mt-4 px-3 py-2 bg-green-50 border border-green-200 rounded text-sm text-green-800"
      >
        ✓ 导入成功（{{ importResult.mode === 'overwrite' ? '覆盖' : '合并' }}模式）：
        投递 {{ importResult.applications_imported }} 条 /
        节点 {{ importResult.events_imported }} 条 /
        题目 {{ importResult.questions_imported }} 条
      </div>

      <div
        v-if="errorMsg"
        class="mt-4 px-3 py-2 bg-red-50 border border-red-200 rounded text-sm text-red-700"
      >{{ errorMsg }}</div>
    </div>
  </div>
</template>
