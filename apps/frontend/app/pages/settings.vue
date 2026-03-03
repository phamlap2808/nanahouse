<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
      <p class="page-subtitle">Manage your account preferences</p>
    </div>

    <!-- Success / Error Messages -->
    <div v-if="successMsg" class="alert alert-success">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      {{ successMsg }}
    </div>

    <div v-if="error" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {{ error }}
    </div>

    <!-- Single unified settings card -->
    <div class="settings-card glass-card">
      <!-- Avatar Section -->
      <section class="settings-section">
        <h3 class="settings-section-title">Avatar</h3>
        <div class="avatar-upload-area">
          <div class="avatar-preview" @click="triggerFileInput">
            <img v-if="avatarSrc" :src="avatarSrc" alt="User avatar" class="avatar-preview-img">
            <div v-else class="avatar-preview-initials">{{ userInitials }}</div>
            <div class="avatar-overlay">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </div>
          </div>
          <div class="avatar-upload-info">
            <button type="button" class="btn btn-ghost btn-sm" @click="triggerFileInput">
              Change photo
            </button>
            <p class="avatar-upload-hint">JPG, PNG, GIF or WebP. Max 2MB.</p>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            style="display: none;"
            @change="handleFileChange"
          >
        </div>
      </section>

      <div class="settings-divider"></div>

      <!-- Profile Section -->
      <section class="settings-section">
        <h3 class="settings-section-title">Profile</h3>
        <form @submit.prevent="handleUpdateProfile">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input
              v-model="profileForm.fullName"
              type="text"
              class="form-input"
              placeholder="Your full name"
              required
            >
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              :value="user?.email"
              type="email"
              class="form-input"
              disabled
              style="opacity: 0.6; cursor: not-allowed;"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              Save Changes
            </button>
          </div>
        </form>
      </section>

      <div class="settings-divider"></div>

      <!-- Password Section -->
      <section class="settings-section" style="margin-bottom: 0;">
        <h3 class="settings-section-title">Change Password</h3>
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label class="form-label">Current Password</label>
            <input
              v-model="passwordForm.currentPassword"
              type="password"
              class="form-input"
              placeholder="Enter current password"
              required
            >
          </div>
          <div class="form-group">
            <label class="form-label">New Password</label>
            <input
              v-model="passwordForm.newPassword"
              type="password"
              class="form-input"
              placeholder="Enter new password (min 6 chars)"
              required
              minlength="6"
            >
          </div>
          <div class="form-group">
            <label class="form-label">Confirm New Password</label>
            <input
              v-model="passwordForm.confirmPassword"
              type="password"
              class="form-input"
              placeholder="Confirm new password"
              required
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              Update Password
            </button>
          </div>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

useHead({
  title: 'Settings - NanaHouse',
})

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { user, loading, error, updateProfile, changePassword, uploadAvatar } = useAuth()

const successMsg = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)

const userInitials = computed(() => {
  const name = user.value?.full_name || 'U'
  return name.split(' ').map((w: string) => w[0]).join('').toUpperCase().slice(0, 2)
})

const avatarSrc = computed(() => {
  if (!user.value?.avatar_url) return null
  return `${apiBase}${user.value.avatar_url}`
})

const profileForm = reactive({
  fullName: user.value?.full_name || '',
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

watch(() => user.value?.full_name, (val) => {
  if (val) profileForm.fullName = val
})

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  successMsg.value = ''
  error.value = null

  if (file.size > 2 * 1024 * 1024) {
    error.value = 'File size must be less than 2MB'
    return
  }

  const ok = await uploadAvatar(file)
  if (ok) {
    successMsg.value = 'Avatar updated successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  }

  // Reset input so same file can be re-selected
  input.value = ''
}

const handleUpdateProfile = async () => {
  successMsg.value = ''
  error.value = null
  const ok = await updateProfile(profileForm.fullName)
  if (ok) {
    successMsg.value = 'Profile updated successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  }
}

const handleChangePassword = async () => {
  successMsg.value = ''
  error.value = null

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    error.value = 'New passwords do not match'
    return
  }

  if (passwordForm.newPassword.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  const ok = await changePassword(passwordForm.currentPassword, passwordForm.newPassword)
  if (ok) {
    successMsg.value = 'Password changed successfully!'
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    setTimeout(() => { successMsg.value = '' }, 3000)
  }
}
</script>
