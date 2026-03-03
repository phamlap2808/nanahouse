<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <ClientOnly>
        <p class="page-subtitle">Welcome back, {{ user?.full_name || 'User' }}</p>
        <template #fallback>
          <p class="page-subtitle">Welcome back</p>
        </template>
      </ClientOnly>
    </div>

    <div class="dashboard-welcome-card glass-card">
      <div class="dashboard-welcome-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      </div>
      <h1 class="dashboard-welcome-title">
        All systems operational
      </h1>
      <p class="dashboard-welcome-text">
        Your NanaHouse dashboard is ready. Use the sidebar to navigate between sections.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

useHead({
  title: 'Dashboard - NanaHouse',
})

const { user } = useAuth()
</script>
