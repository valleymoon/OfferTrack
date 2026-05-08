<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  text: string | null | undefined
}>()

const URL_RE = /(https?:\/\/[^\s<]+[^\s<.,;:!?)\]}'"，。；：！？）】」』])/g

type Segment = { type: 'text' | 'link'; value: string }

const segments = computed<Segment[]>(() => {
  const raw = props.text ?? ''
  if (!raw) return []
  const out: Segment[] = []
  let lastIndex = 0
  for (const match of raw.matchAll(URL_RE)) {
    const start = match.index ?? 0
    if (start > lastIndex) {
      out.push({ type: 'text', value: raw.slice(lastIndex, start) })
    }
    out.push({ type: 'link', value: match[0] })
    lastIndex = start + match[0].length
  }
  if (lastIndex < raw.length) {
    out.push({ type: 'text', value: raw.slice(lastIndex) })
  }
  return out
})
</script>

<template>
  <span class="break-all whitespace-pre-wrap">
    <template v-for="(seg, i) in segments" :key="i">
      <a
        v-if="seg.type === 'link'"
        :href="seg.value"
        target="_blank"
        rel="noopener noreferrer"
        class="text-blue-600 hover:underline"
      >{{ seg.value }}</a>
      <template v-else>{{ seg.value }}</template>
    </template>
  </span>
</template>
