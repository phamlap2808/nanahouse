<template>
  <div>
    <div class="page-header" style="display: flex; align-items: flex-start; justify-content: space-between;">
      <div>
        <h1 class="page-title">Products</h1>
        <p class="page-subtitle">Manage products and variants</p>
      </div>
      <button v-if="isAdmin" class="btn btn-primary btn-sm" @click="openCreateModal">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Add Product
      </button>
    </div>

    <!-- Messages -->
    <div v-if="successMsg" class="alert alert-success">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-error">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      {{ errorMsg }}
    </div>

    <!-- Filter bar -->
    <div class="glass-card" style="padding: 12px 16px; margin-bottom: 16px;">
      <div style="display: flex; gap: 12px; flex-wrap: wrap; align-items: center;">
        <input v-model="filters.search" type="text" class="form-input" placeholder="Search products..." style="flex: 1; min-width: 180px;" @input="debouncedFetch">
        <select v-model="filters.category_id" class="form-input" style="width: 180px;" @change="fetchProducts">
          <option :value="null">All Categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filters.is_active" class="form-input" style="width: 130px;" @change="fetchProducts">
          <option :value="null">All Status</option>
          <option :value="true">Active</option>
          <option :value="false">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Product Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container glass-card" style="max-width: 600px; max-height: 90vh; overflow-y: auto;">
          <div class="modal-header">
            <h2 class="modal-title">{{ editingId ? 'Edit Product' : 'New Product' }}</h2>
            <button class="action-btn" @click="closeModal">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <form @submit.prevent="handleSubmit">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
              <div class="form-group" style="grid-column: 1 / -1;">
                <label class="form-label">Name *</label>
                <input v-model="form.name" type="text" class="form-input" required>
              </div>
              <div class="form-group">
                <label class="form-label">SKU</label>
                <input v-model="form.sku" type="text" class="form-input" placeholder="e.g. CF-SUA-DA">
              </div>
              <div class="form-group">
                <label class="form-label">Category</label>
                <select v-model="form.category_id" class="form-input">
                  <option :value="null">— No category —</option>
                  <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Price *</label>
                <input v-model.number="form.price" type="number" class="form-input" min="0" step="1000" required>
              </div>
              <div class="form-group">
                <label class="form-label">Compare Price</label>
                <input v-model.number="form.compare_price" type="number" class="form-input" min="0" step="1000">
              </div>
              <div class="form-group">
                <label class="form-label">Stock</label>
                <input v-model.number="form.stock_quantity" type="number" class="form-input" min="0">
              </div>
              <div class="form-group">
                <label class="form-label">Sort Order</label>
                <input v-model.number="form.sort_order" type="number" class="form-input" min="0">
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label class="form-label">Description</label>
                <textarea v-model="form.description" class="form-input" rows="2" placeholder="Optional description" />
              </div>

              <!-- Image Upload -->
              <div class="form-group" style="grid-column: 1 / -1;">
                <label class="form-label">Product Image</label>
                <div class="image-upload-area">
                  <div v-if="imagePreviewUrl" class="image-preview">
                    <img :src="imagePreviewUrl" alt="Preview">
                    <button type="button" class="image-remove-btn" @click="removeImage">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                  </div>
                  <label v-else class="image-upload-trigger">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                    <span>Click to upload image</span>
                    <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/gif,image/webp" style="display:none;" @change="onFileSelected">
                  </label>
                </div>
              </div>
            </div>

            <!-- Variants Section -->
            <div style="margin-top: 16px; border-top: 1px solid var(--glass-border); padding-top: 16px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <label class="form-label" style="margin-bottom: 0; font-size: 0.95rem;">Variants</label>
                <button type="button" class="btn btn-ghost btn-sm" style="font-size: 0.8rem;" @click="addVariant">+ Add Variant</button>
              </div>
              <div v-if="form.variants.length === 0" style="color: var(--text-secondary); font-size: 0.85rem; text-align: center; padding: 12px;">
                No variants — product uses base price
              </div>
              <div v-for="(v, i) in form.variants" :key="i" style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px; padding: 8px; border-radius: 8px; background: var(--glass-bg);">
                <input v-model="v.name" type="text" class="form-input" placeholder="Name" style="flex: 2; font-size: 0.85rem;" required>
                <input v-model="v.sku" type="text" class="form-input" placeholder="SKU" style="flex: 1; font-size: 0.85rem;">
                <input v-model.number="v.price" type="number" class="form-input" placeholder="Price" min="0" step="1000" style="flex: 1; font-size: 0.85rem;" required>
                <input v-model.number="v.stock_quantity" type="number" class="form-input" placeholder="Stock" min="0" style="width: 70px; font-size: 0.85rem;">
                <button type="button" class="action-btn danger" style="flex-shrink:0;" @click="form.variants.splice(i, 1)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>
            </div>

            <div v-if="modalError" class="alert alert-error" style="margin-top: 12px;">{{ modalError }}</div>

            <div class="form-actions" style="margin-top: 20px; justify-content: flex-end;">
              <button type="button" class="btn btn-ghost btn-sm" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm" :disabled="saving">
                <span v-if="saving" class="spinner"/>
                {{ editingId ? 'Save Changes' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Product Table -->
    <div class="glass-card" style="padding: 0; overflow-x: auto;">
      <div v-if="loading" class="empty-state">
        <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;"/>
      </div>

      <div v-else-if="products.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
        <p>No products yet</p>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="width: 50px;"></th>
            <th>Name</th>
            <th class="hide-mobile">SKU</th>
            <th>Price</th>
            <th class="hide-mobile">Category</th>
            <th class="hide-mobile">Stock</th>
            <th class="hide-mobile">Variants</th>
            <th>Status</th>
            <th v-if="isAdmin" style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>
              <div class="product-thumb">
                <img v-if="p.image_url" :src="`${apiBase}${p.image_url}`" :alt="p.name">
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              </div>
            </td>
            <td><strong>{{ p.name }}</strong></td>
            <td class="hide-mobile" style="color: var(--text-secondary); font-size: 0.85rem;">{{ p.sku || '—' }}</td>
            <td style="font-weight: 600;">{{ formatPrice(p.price) }}</td>
            <td class="hide-mobile">
              <span v-if="p.category" class="badge">{{ p.category.name }}</span>
              <span v-else style="color: var(--text-secondary);">—</span>
            </td>
            <td class="hide-mobile">{{ p.stock_quantity }}</td>
            <td class="hide-mobile">
              <span v-if="p.variants.length" class="badge badge-info">{{ p.variants.length }}</span>
              <span v-else style="color: var(--text-secondary);">—</span>
            </td>
            <td>
              <span :class="['status-dot', p.is_active ? 'active' : 'inactive']">
                {{ p.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td v-if="isAdmin">
              <div style="display: flex; gap: 4px;">
                <button class="action-btn" title="Edit" @click="openEditModal(p)">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <button class="action-btn danger" title="Delete" @click="handleDelete(p)">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination-bar">
      <button class="btn btn-ghost btn-sm" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">← Prev</button>
      <span class="pagination-info">Page {{ currentPage }} / {{ totalPages }} ({{ totalItems }} items)</span>
      <button class="btn btn-ghost btn-sm" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">Next →</button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
useHead({ title: 'Products - NanaHouse' })

interface VariantItem {
  id?: number
  name: string
  sku: string | null
  price: number
  compare_price: number | null
  stock_quantity: number
  is_active?: boolean
  sort_order: number
}

interface CategoryItem { id: number; name: string }

interface ProductItem {
  id: number
  name: string
  slug: string
  sku: string | null
  description: string | null
  price: number
  compare_price: number | null
  image_url: string | null
  category_id: number | null
  category: CategoryItem | null
  is_active: boolean
  stock_quantity: number
  sort_order: number
  variants: VariantItem[]
  created_at: string
  updated_at: string | null
}

interface ProductListData {
  items: ProductItem[]
  total: number
  page: number
  size: number
  pages: number
}

const { token, isAdmin } = useAuth()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

const products = ref<ProductItem[]>([])
const categories = ref<CategoryItem[]>([])
const loading = ref(true)
const successMsg = ref('')
const errorMsg = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const filters = reactive({
  search: '',
  category_id: null as number | null,
  is_active: null as boolean | null,
})

// Modal
const showModal = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const modalError = ref('')
const imageFile = ref<File | null>(null)
const existingImageUrl = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const form = reactive({
  name: '',
  sku: '',
  description: '',
  price: 0,
  compare_price: null as number | null,
  category_id: null as number | null,
  stock_quantity: 0,
  sort_order: 0,
  variants: [] as VariantItem[],
})

const imagePreviewUrl = computed(() => {
  if (imageFile.value) return URL.createObjectURL(imageFile.value)
  if (existingImageUrl.value) return `${apiBase}${existingImageUrl.value}`
  return null
})

const onFileSelected = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    imageFile.value = input.files[0]
  }
}

const removeImage = () => {
  imageFile.value = null
  existingImageUrl.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
}

const authHeaders = () => ({ Authorization: `Bearer ${token.value}` })

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(price)
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
const debouncedFetch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { currentPage.value = 1; fetchProducts() }, 300)
}

onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories()])
})

const fetchCategories = async () => {
  try {
    const data = await $fetch<CategoryItem[]>(`${apiBase}/api/v1/categories/`, {
      headers: authHeaders(),
    })
    categories.value = data
  } catch { /* ignore */ }
}

const fetchProducts = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const params = new URLSearchParams()
    params.set('page', String(currentPage.value))
    params.set('size', '20')
    if (filters.search) params.set('search', filters.search)
    if (filters.category_id !== null) params.set('category_id', String(filters.category_id))
    if (filters.is_active !== null) params.set('is_active', String(filters.is_active))

    const data = await $fetch<ProductListData>(`${apiBase}/api/v1/products/?${params}`, {
      headers: authHeaders(),
    })
    products.value = data.items
    totalPages.value = data.pages
    totalItems.value = data.total
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || 'Failed to load products'
  } finally {
    loading.value = false
  }
}

const goToPage = (page: number) => {
  currentPage.value = page
  fetchProducts()
}

const addVariant = () => {
  form.variants.push({ name: '', sku: null, price: 0, compare_price: null, stock_quantity: 0, sort_order: form.variants.length })
}

const openCreateModal = () => {
  editingId.value = null
  form.name = ''
  form.sku = ''
  form.description = ''
  form.price = 0
  form.compare_price = null
  form.category_id = null
  form.stock_quantity = 0
  form.sort_order = 0
  form.variants = []
  imageFile.value = null
  existingImageUrl.value = null
  modalError.value = ''
  showModal.value = true
}

const openEditModal = (p: ProductItem) => {
  editingId.value = p.id
  form.name = p.name
  form.sku = p.sku || ''
  form.description = p.description || ''
  form.price = p.price
  form.compare_price = p.compare_price
  form.category_id = p.category_id
  form.stock_quantity = p.stock_quantity
  form.sort_order = p.sort_order
  form.variants = p.variants.map(v => ({ ...v }))
  imageFile.value = null
  existingImageUrl.value = p.image_url
  modalError.value = ''
  showModal.value = true
}

const closeModal = () => { showModal.value = false }

const handleSubmit = async () => {
  saving.value = true
  modalError.value = ''
  try {
    const body: Record<string, unknown> = {
      name: form.name,
      sku: form.sku || null,
      description: form.description || null,
      price: form.price,
      compare_price: form.compare_price,
      category_id: form.category_id,
      stock_quantity: form.stock_quantity,
      sort_order: form.sort_order,
    }

    if (editingId.value) {
      // Update product
      await $fetch(`${apiBase}/api/v1/products/${editingId.value}`, {
        method: 'PUT', headers: authHeaders(), body,
      })

      // Upload image if a new file was selected
      if (imageFile.value) {
        const fd = new FormData()
        fd.append('file', imageFile.value)
        await $fetch(`${apiBase}/api/v1/products/${editingId.value}/image`, {
          method: 'PUT', headers: { Authorization: `Bearer ${token.value}` }, body: fd,
        })
      }

      // Sync variants: for simplicity, delete all existing, re-create
      const existing = products.value.find(p => p.id === editingId.value)
      if (existing) {
        for (const v of existing.variants) {
          await $fetch(`${apiBase}/api/v1/products/${editingId.value}/variants/${v.id}`, {
            method: 'DELETE', headers: authHeaders(),
          })
        }
      }
      for (const v of form.variants) {
        await $fetch(`${apiBase}/api/v1/products/${editingId.value}/variants`, {
          method: 'POST', headers: authHeaders(),
          body: { name: v.name, sku: v.sku || null, price: v.price, compare_price: v.compare_price, stock_quantity: v.stock_quantity, sort_order: v.sort_order },
        })
      }
      successMsg.value = 'Product updated successfully'
    } else {
      // Create with variants
      body.variants = form.variants.map(v => ({
        name: v.name, sku: v.sku || null, price: v.price, compare_price: v.compare_price,
        stock_quantity: v.stock_quantity, sort_order: v.sort_order,
      }))
      const created = await $fetch<ProductItem>(`${apiBase}/api/v1/products/`, {
        method: 'POST', headers: authHeaders(), body,
      })
      // Upload image if selected
      if (imageFile.value && created.id) {
        const fd = new FormData()
        fd.append('file', imageFile.value)
        await $fetch(`${apiBase}/api/v1/products/${created.id}/image`, {
          method: 'PUT', headers: { Authorization: `Bearer ${token.value}` }, body: fd,
        })
      }
      successMsg.value = 'Product created successfully'
    }
    closeModal()
    await fetchProducts()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    modalError.value = e?.data?.detail || 'Operation failed'
  } finally {
    saving.value = false
  }
}

const handleDelete = async (p: ProductItem) => {
  if (!confirm(`Delete "${p.name}"? This will also delete all variants.`)) return
  try {
    await $fetch(`${apiBase}/api/v1/products/${p.id}`, {
      method: 'DELETE', headers: authHeaders(),
    })
    successMsg.value = 'Product deleted successfully'
    await fetchProducts()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err: unknown) {
    const e = err as { data?: { detail?: string } }
    errorMsg.value = e?.data?.detail || 'Failed to delete product'
  }
}
</script>

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
  white-space: nowrap;
}
.data-table th {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
.data-table tbody tr:hover {
  background: var(--glass-hover);
}
.product-thumb {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--glass-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}
.product-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.product-thumb svg {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--accent-bg);
  color: var(--accent-color);
}
.badge-info {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}
.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
}
.status-dot::before {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.status-dot.active::before { background: #22c55e; }
.status-dot.inactive::before { background: #ef4444; }
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 0;
}
.pagination-info {
  font-size: 0.85rem;
  color: var(--text-secondary);
}
/* Image Upload */
.image-upload-area {
  border: 2px dashed var(--glass-border);
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;
}
.image-upload-area:hover {
  border-color: var(--accent-color);
}
.image-upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}
.image-upload-trigger:hover {
  color: var(--accent-color);
}
.image-upload-trigger span {
  font-size: 0.85rem;
}
.image-preview {
  position: relative;
  width: 100%;
  max-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
}
.image-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 10px;
}
.image-remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s;
}
.image-remove-btn:hover {
  transform: scale(1.15);
}
@media (max-width: 768px) {
  .hide-mobile { display: none; }
}
</style>
