<template>
  <div></div>
</template>

<script setup lang="ts">
const { isAuthenticated, initAuth } = useAuth()

onMounted(() => {
  initAuth()
  if (isAuthenticated.value) {
    navigateTo('/admin/dashboard')
  } else {
    navigateTo('/login')
  }
})
</script>
