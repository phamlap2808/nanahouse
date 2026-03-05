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
      <h2 class="auth-subtitle">{{ $t('auth.register_title') }}</h2>
      <p class="auth-description">{{ $t('auth.register_subtitle') }}</p>

      <!-- Error Message -->
      <div v-if="error" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">{{ $t('auth.full_name') }}</label>
          <input
            v-model="form.full_name"
            type="text"
            class="form-input"
            :placeholder="$t('auth.enter_name')"
            required
          >
        </div>

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
            :placeholder="$t('auth.min_password')"
            required
            minlength="6"
          >
        </div>

        <div class="form-group">
          <label class="form-label">{{ $t('auth.confirm_password') }}</label>
          <input
            v-model="form.confirmPassword"
            type="password"
            class="form-input"
            :placeholder="$t('auth.confirm_your_password')"
            required
          >
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ $t('auth.register') }}
        </button>
      </form>

      <p class="auth-footer">
        {{ $t('auth.has_account') }}
        <NuxtLink to="/login">{{ $t('auth.login') }}</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

useHead({
  title: 'Register - NanaHouse',
})

const { register, loading, error, isAuthenticated, initAuth } = useAuth()
const { t } = useI18n()

onMounted(() => {
  initAuth()
  if (isAuthenticated.value) {
    navigateTo('/admin/dashboard')
  }
})

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    error.value = t('auth.password_mismatch')
    return
  }

  const success = await register({
    email: form.email,
    password: form.password,
    full_name: form.full_name,
  })
  if (success) {
    navigateTo('/login?registered=true')
  }
}
</script>
