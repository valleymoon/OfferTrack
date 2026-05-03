<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-6xl mx-auto px-6 py-3 flex items-center gap-6">
        <h1 class="text-xl font-bold text-blue-600">📋 OfferTrack</h1>
        <RouterLink
          to="/dashboard"
          class="text-gray-600 hover:text-blue-600"
          active-class="!text-blue-600 font-medium"
        >仪表盘</RouterLink>
        <RouterLink
          to="/applications"
          class="text-gray-600 hover:text-blue-600"
          active-class="!text-blue-600 font-medium"
        >投递记录</RouterLink>
        <div class="flex-1"></div>
        <RouterLink
          to="/settings"
          class="text-gray-600 hover:text-blue-600 text-sm"
          active-class="!text-blue-600 font-medium"
        >⚙ 设置</RouterLink>
      </div>
    </nav>
    <main class="max-w-6xl mx-auto px-6 py-6">
      <RouterView />
    </main>
  </div>
</template>
