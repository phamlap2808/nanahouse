<template>
  <div>
    <div class="page-header" style="display: flex; align-items: flex-start; justify-content: space-between;">
      <div>
        <h1 class="page-title">{{ $t('categories.title') }}</h1>
        <p class="page-subtitle">{{ $t('categories.subtitle') }}</p>
      </div>
      <button v-if="isAdmin" class="btn btn-primary btn-sm" @click="openCreateModal(null)">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ $t('categories.add') }}
      </button>
    </div>

    <!-- Messages -->
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

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container glass-card">
          <div class="modal-header">
            <h2 class="modal-title">{{ editingId ? $t('categories.edit') : $t('categories.new') }}</h2>
            <button class="action-btn" @click="closeModal">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">{{ $t('common.name') }}</label>
              <input v-model="form.name" type="text" class="form-input" :placeholder="$t('common.name')" required>
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('common.description') }}</label>
              <input v-model="form.description" type="text" class="form-input" :placeholder="$t('common.optional')">
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('categories.parent') }}</label>
              <select v-model="form.parent_id" class="form-input">
                <option :value="null">{{ $t('categories.root') }}</option>
                <option
                  v-for="opt in parentOptions"
                  :key="opt.id"
                  :value="opt.id"
                  :disabled="opt.id === editingId"
                >
                  {{ opt.prefix }}{{ opt.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">{{ $t('categories.sort_order') }}</label>
              <input v-model.number="form.sort_order" type="number" class="form-input" min="0">
            </div>

            <div v-if="modalError" class="alert alert-error" style="margin-top: 12px;">
              {{ modalError }}
            </div>

            <div class="form-actions" style="margin-top: 20px; justify-content: flex-end;">
              <button type="button" class="btn btn-ghost btn-sm" @click="closeModal">{{ $t('common.cancel') }}</button>
              <button type="submit" class="btn btn-primary btn-sm" :disabled="saving">
                <span v-if="saving" class="spinner"/>
                {{ editingId ? $t('common.save_changes') : $t('common.create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Category Tree -->
    <div class="glass-card" style="padding: 0;">
      <div v-if="loading" class="empty-state">
        <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;"/>
      </div>

      <div v-else-if="tree.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <p>{{ $t('categories.no_categories') }}</p>
      </div>

      <div v-else class="tree-container">
        <template v-for="node in tree" :key="node.id">
          <CategoryNode
            :node="node"
            :depth="0"
            :is-admin="isAdmin"
            :expanded-ids="expandedIds"
            :api-base="apiBase"
            @toggle="toggleExpand"
            @edit="openEditModal"
            @add-child="openCreateModal"
            @delete="handleDelete"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import CategoryNode from '~/components/CategoryNode.vue'

definePageMeta({
  middleware: 'auth',
})

useHead({
  title: 'Categories - NanaHouse',
})

interface CategoryItem {
  id: number
  name: string
  slug: string
  description: string | null
  image_url: string | null
  parent_id: number | null
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string | null
  children: CategoryItem[]
}

const { token, isAdmin } = useAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { t } = useI18n()

const tree = ref<CategoryItem[]>([])

const loading = ref(true)
const successMsg = ref('')
const errorMsg = ref('')
const expandedIds = ref<Set<number>>(new Set())

// Modal state
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const modalError = ref('')
const form = reactive({
  name: '',
  description: '',
  parent_id: null as number | null,
  sort_order: 0,
})

const authHeaders = () => ({
  Authorization: `Bearer ${token.value}`,
})

// Flat options for parent selector (with indent prefix)
const parentOptions = computed(() => {
  const opts: { id: number; name: string; prefix: string }[] = []
  const walk = (nodes: CategoryItem[], depth: number) => {
    for (const n of nodes) {
      opts.push({ id: n.id, name: n.name, prefix: '— '.repeat(depth) })
      if (n.children?.length) walk(n.children, depth + 1)
    }
  }
  walk(tree.value, 0)
  return opts
})

onMounted(async () => {
  await fetchCategories()
})

const fetchCategories = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await $fetch<CategoryItem[]>(`${apiBase}/api/v1/categories/?tree=true`, {
      headers: authHeaders(),
    })
    tree.value = data
    // Also expand all by default on first load
    const allIds = new Set<number>()
    const collectIds = (nodes: CategoryItem[]) => {
      for (const n of nodes) {
        if (n.children?.length) {
          allIds.add(n.id)
          collectIds(n.children)
        }
      }
    }
    collectIds(data)
    expandedIds.value = allIds
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('categories.failed_load')
  } finally {
    loading.value = false
  }
}

const toggleExpand = (id: number) => {
  const s = new Set(expandedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  expandedIds.value = s
}

const openCreateModal = (parentId: number | null) => {
  editingId.value = null
  form.name = ''
  form.description = ''
  form.parent_id = parentId
  form.sort_order = 0
  modalError.value = ''
  showModal.value = true
}

const openEditModal = (cat: CategoryItem) => {
  editingId.value = cat.id
  form.name = cat.name
  form.description = cat.description || ''
  form.parent_id = cat.parent_id
  form.sort_order = cat.sort_order
  modalError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const handleSubmit = async () => {
  saving.value = true
  modalError.value = ''
  try {
    if (editingId.value) {
      await $fetch(`${apiBase}/api/v1/categories/${editingId.value}`, {
        method: 'PUT',
        headers: authHeaders(),
        body: {
          name: form.name,
          description: form.description || null,
          parent_id: form.parent_id,
          sort_order: form.sort_order,
        },
      })
      successMsg.value = t('categories.updated_success')
    } else {
      await $fetch(`${apiBase}/api/v1/categories/`, {
        method: 'POST',
        headers: authHeaders(),
        body: {
          name: form.name,
          description: form.description || null,
          parent_id: form.parent_id,
          sort_order: form.sort_order,
        },
      })
      successMsg.value = t('categories.created_success')
    }
    closeModal()
    await fetchCategories()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    modalError.value = e?.data?.detail || t('categories.operation_failed')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (cat: CategoryItem) => {
  if (!confirm(t('categories.delete_confirm', { name: cat.name }))) return
  successMsg.value = ''
  errorMsg.value = ''
  try {
    await $fetch(`${apiBase}/api/v1/categories/${cat.id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    successMsg.value = t('categories.deleted_success')
    await fetchCategories()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || t('categories.failed_delete')
  }
}
</script>
