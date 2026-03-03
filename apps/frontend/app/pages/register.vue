<template>
  <NuxtLayout name="auth">
    <div class="auth-card glass-card">
      <div class="auth-header">
        <div class="auth-logo">
          <div class="auth-logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          NanaHouse
        </div>
        <h1 class="auth-title">Create your account</h1>
        <p class="auth-subtitle">Get started with NanaHouse today</p>
      </div>

      <!-- Error alert -->
      <div v-if="error" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="15" y1="9" x2="9" y2="15"/>
          <line x1="9" y1="9" x2="15" y2="15"/>
        </svg>
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="full_name" class="form-label">Full Name</label>
          <input
            id="full_name"
            v-model="form.full_name"
            type="text"
            class="form-input"
            placeholder="John Doe"
            required
            autocomplete="name"
          />
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="you@example.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-input"
            :class="{ error: passwordError }"
            placeholder="Min 6 characters"
            required
            autocomplete="new-password"
            minlength="6"
          />
          <p v-if="passwordError" class="form-error">{{ passwordError }}</p>
        </div>

        <div class="form-group">
          <label for="confirm_password" class="form-label">Confirm Password</label>
          <input
            id="confirm_password"
            v-model="form.confirm_password"
            type="password"
            class="form-input"
            :class="{ error: confirmError }"
            placeholder="Re-enter your password"
            required
            autocomplete="new-password"
          />
          <p v-if="confirmError" class="form-error">{{ confirmError }}</p>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <div class="auth-footer">
        Already have an account? <NuxtLink to="/login">Sign in</NuxtLink>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

useHead({
  title: 'Create Account - NanaHouse',
  meta: [{ name: 'description', content: 'Create your NanaHouse account' }],
})

const { register, loading, error, isAuthenticated, initAuth } = useAuth()

const form = reactive({
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
})

const passwordError = ref('')
const confirmError = ref('')

// Redirect if already authenticated
onMounted(() => {
  initAuth()
  if (isAuthenticated.value) {
    navigateTo('/dashboard')
  }
})

const validate = (): boolean => {
  passwordError.value = ''
  confirmError.value = ''

  if (form.password.length < 6) {
    passwordError.value = 'Password must be at least 6 characters'
    return false
  }

  if (form.password !== form.confirm_password) {
    confirmError.value = 'Passwords do not match'
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validate()) return

  const success = await register({
    full_name: form.full_name,
    email: form.email,
    password: form.password,
  })

  if (success) {
    navigateTo('/login?registered=true')
  }
}
</script>
