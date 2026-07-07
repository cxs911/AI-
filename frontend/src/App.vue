<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/store'

const appStore = useAppStore()

onMounted(() => {
  appStore.loadSystemInfo()
  appStore.loadOllamaConfig()
})
</script>
