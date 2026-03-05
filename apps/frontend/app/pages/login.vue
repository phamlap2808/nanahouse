<template>
  <div>
    <div class="auth-card glass-card">
      <div class="auth-logo-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
      <h1 class="auth-title">NanaHouse</h1>
      <h2 class="auth-subtitle">{{ $t('auth.login_title') }}</h2>
      <p class="auth-description">{{ $t('auth.login_subtitle') }}</p>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>

      <!-- Success Message (from registration) -->
      <div v-if="successMessage" class="alert alert-success">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">{{ $t('auth.email') }}</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            :placeholder="$t('auth.enter_email')"
            required
          >
        </div>

        <div class="form-group">
          <label class="form-label">{{ $t('auth.password') }}</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            :placeholder="$t('auth.enter_password')"
            required
            minlength="6"
          >
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ $t('auth.login') }}
        </button>
      </form>

      <p class="auth-footer">
        {{ $t('auth.no_account') }}
        <NuxtLink to="/register">{{ $t('auth.register') }}</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

useHead({
  title: 'Login - NanaHouse',
})

const { login, loading, error, isAuthenticated, initAuth } = useAuth()
const route = useRoute()
const successMessage = ref('')

// Check for success from registration
if (route.query.registered === 'true') {
  const { t } = useI18n()
  successMessage.value = t('auth.register_success')
}

onMounted(() => {
  initAuth()
  if (isAuthenticated.value) {
    navigateTo('/admin/dashboard')
  }
})

const form = reactive({
  email: '',
  password: '',
})

const handleLogin = async () => {
  successMessage.value = ''
  const success = await login(form)
  if (success) {
    navigateTo('/admin/dashboard')
  }
}
</script>
