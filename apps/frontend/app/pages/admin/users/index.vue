<template>
  <div>
    <div class="page-header" style="display: flex; align-items: flex-start; justify-content: space-between;">
      <div>
        <h1 class="page-title">{{ $t('users.title') }}</h1>
        <p class="page-subtitle">{{ $t('users.subtitle') }}</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openCreateModal">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ $t('users.add') }}
      </button>
    </div>

    <!-- Error / Success Messages -->
    <div v-if="successMsg" class="alert alert-success">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {{ errorMsg }}
    </div>

    <!-- Create User Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
        <div class="modal-container glass-card">
          <div class="modal-header">
            <h2 class="modal-title">{{ $t('users.create_new') }}</h2>
            <button class="action-btn" @click="closeCreateModal">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleCreateUser">
            <div class="form-group">
              <label class="form-label">{{ $t('auth.full_name') }}</label>
              <input
                v-model="createForm.full_name"
                type="text"
                class="form-input"
                :placeholder="$t('users.enter_name')"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('auth.email') }}</label>
              <input
                v-model="createForm.email"
                type="email"
                class="form-input"
                :placeholder="$t('users.enter_email')"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('auth.password') }}</label>
              <input
                v-model="createForm.password"
                type="password"
                class="form-input"
                :placeholder="$t('auth.min_password')"
                required
                minlength="6"
              />
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('users.role') }}</label>
              <select v-model="createForm.role" class="form-input">
                <option value="staff">{{ $t('users.role_staff') }}</option>
                <option value="admin">{{ $t('users.role_admin') }}</option>
                <option value="viewer">{{ $t('users.role_viewer') }}</option>
              </select>
            </div>

            <div v-if="createError" class="alert alert-error" style="margin-top: 12px;">
              {{ createError }}
            </div>

            <div class="form-actions" style="margin-top: 20px; justify-content: flex-end;">
              <button type="button" class="btn btn-ghost btn-sm" @click="closeCreateModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn btn-primary btn-sm" :disabled="creating">
                <span v-if="creating" class="spinner" />
                {{ $t('common.create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Users Table -->
    <div class="glass-card" style="overflow: hidden;">
      <table v-if="users.length > 0" class="data-table">
        <thead>
          <tr>
            <th>{{ $t('users.user') }}</th>
            <th>{{ $t('auth.email') }}</th>
            <th>{{ $t('users.role') }}</th>
            <th>{{ $t('common.status') }}</th>
            <th>{{ $t('users.joined') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>
              <div class="user-cell">
                <div class="user-cell-avatar">{{ getInitials(u.full_name) }}</div>
                <span>{{ u.full_name }}</span>
              </div>
            </td>
            <td>{{ u.email }}</td>
            <td>
              <select
                :value="u.role"
                class="form-input"
                style="padding: 4px 8px; font-size: 12px; width: auto; min-width: 90px;"
                :disabled="u.id === currentUser?.id"
                @change="handleRoleChange(u.id, ($event.target as HTMLSelectElement).value)"
              >
                <option value="admin">{{ $t('users.role_admin') }}</option>
                <option value="staff">{{ $t('users.role_staff') }}</option>
                <option value="viewer">{{ $t('users.role_viewer') }}</option>
              </select>
            </td>
            <td>
              <span class="badge" :class="u.is_active ? 'badge-active' : 'badge-inactive'">
                {{ u.is_active ? $t('common.active') : $t('common.inactive') }}
              </span>
            </td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <div style="display: flex; gap: 4px;">
                <button
                  v-if="u.id !== currentUser?.id"
                  class="action-btn"
                  :title="u.is_active ? $t('users.deactivate') : $t('users.activate')"
                  @click="handleToggleStatus(u)"
                >
                  <svg v-if="u.is_active" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                    <line x1="12" y1="2" x2="12" y2="12"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                </button>
                <button
                  v-if="u.id !== currentUser?.id"
                  class="action-btn danger"
                  :title="$t('users.delete_user')"
                  @click="handleDelete(u)"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else-if="!loadingUsers" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
        </svg>
        <p>{{ $t('users.no_users') }}</p>
      </div>

      <div v-else class="empty-state">
        <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
})

useHead({
  title: 'Users - NanaHouse',
})

interface UserItem {
  id: number
  email: string
  full_name: string
  role: string
  avatar_url: string | null
  is_active: boolean
  created_at: string
}

const { user: currentUser, token, isAdmin } = useAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { t } = useI18n()

const users = ref<UserItem[]>([])
const loadingUsers = ref(true)
const successMsg = ref('')
const errorMsg = ref('')

// Create modal state
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const createForm = reactive({
  full_name: '',
  email: '',
  password: '',
  role: 'staff',
})

const authHeaders = () => ({
  Authorization: `Bearer ${token.value}`,
})

onMounted(async () => {
  if (!isAdmin.value) {
    navigateTo('/admin/dashboard')
    return
  }
  await fetchUsers()
})

const openCreateModal = () => {
  createForm.full_name = ''
  createForm.email = ''
  createForm.password = ''
  createForm.role = 'staff'
  createError.value = ''
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

const handleCreateUser = async () => {
  creating.value = true
  createError.value = ''
  try {
    await $fetch(`${apiBase}/api/v1/users/`, {
      method: 'POST',
      headers: authHeaders(),
      body: {
        email: createForm.email,
        password: createForm.password,
        full_name: createForm.full_name,
        role: createForm.role,
      },
    })
    closeCreateModal()
    successMsg.value = t('users.created_success', { name: createForm.full_name })
    await fetchUsers()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    createError.value = e?.data?.detail || t('users.failed_create')
  } finally {
    creating.value = false
  }
}

const fetchUsers = async () => {
  loadingUsers.value = true
  errorMsg.value = ''
  try {
    const data = await $fetch<UserItem[]>(`${apiBase}/api/v1/users/`, {
      headers: authHeaders(),
    })
    users.value = data
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('users.failed_load')
  } finally {
    loadingUsers.value = false
  }
}

const handleRoleChange = async (userId: number, newRole: string) => {
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await $fetch(`${apiBase}/api/v1/users/${userId}/role`, {
      method: 'PUT',
      headers: authHeaders(),
      body: { role: newRole },
    })
    successMsg.value = t('users.role_updated')
    await fetchUsers()
    setTimeout(() => { successMsg.value = '' }, 2000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('users.failed_role')
  }
}

const handleToggleStatus = async (u: UserItem) => {
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await $fetch(`${apiBase}/api/v1/users/${u.id}/status`, {
      method: 'PUT',
      headers: authHeaders(),
      body: { is_active: !u.is_active },
    })
    successMsg.value = u.is_active ? t('users.status_deactivated') : t('users.status_activated')
    await fetchUsers()
    setTimeout(() => { successMsg.value = '' }, 2000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('users.failed_status')
  }
}

const handleDelete = async (u: UserItem) => {
  if (!confirm(t('users.delete_confirm', { name: u.full_name }))) {
    return
  }
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await $fetch(`${apiBase}/api/v1/users/${u.id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    successMsg.value = t('users.deleted_success')
    await fetchUsers()
    setTimeout(() => { successMsg.value = '' }, 2000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('users.failed_delete')
  }
}

const getInitials = (name: string) => {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>
