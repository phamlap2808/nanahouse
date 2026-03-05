<template>
  <div>
    <!-- Node row -->
    <div
      class="tree-node"
      :style="{ paddingLeft: (depth * 24 + 16) + 'px' }"
    >
      <!-- Expand/collapse toggle -->
      <button
        v-if="node.children && node.children.length > 0"
        class="tree-toggle"
        @click="$emit('toggle', node.id)"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          :class="{ rotated: isExpanded }"
        >
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </button>
      <span v-else class="tree-toggle-spacer"/>

      <!-- Category icon -->
      <span class="tree-icon">
        <svg v-if="node.children && node.children.length > 0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
          <polyline points="13 2 13 9 20 9"/>
        </svg>
      </span>

      <!-- Image thumbnail -->
      <img
        v-if="node.image_url"
        :src="apiBase + node.image_url"
        class="tree-thumb"
        alt=""
      >

      <!-- Name -->
      <span class="tree-name" :class="{ inactive: !node.is_active }">
        {{ node.name }}
      </span>

      <!-- Description -->
      <span v-if="node.description" class="tree-desc">
        {{ node.description }}
      </span>

      <!-- Status badge -->
      <span
        class="badge"
        :class="node.is_active ? 'badge-active' : 'badge-inactive'"
        style="margin-left: auto; flex-shrink: 0;"
      >
        {{ node.is_active ? $t('common.active') : $t('common.inactive') }}
      </span>

      <!-- Actions (admin only) -->
      <div v-if="isAdmin" class="tree-actions">
        <button class="action-btn" :title="$t('categories.add_sub')" @click="$emit('add-child', node.id)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <button class="action-btn" :title="$t('common.edit')" @click="$emit('edit', node)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="action-btn danger" :title="$t('common.delete')" @click="$emit('delete', node)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Children (recursive) -->
    <template v-if="isExpanded && node.children && node.children.length > 0">
      <CategoryNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
        :is-admin="isAdmin"
        :expanded-ids="expandedIds"
        :api-base="apiBase"
        @toggle="$emit('toggle', $event)"
        @edit="$emit('edit', $event)"
        @add-child="$emit('add-child', $event)"
        @delete="$emit('delete', $event)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
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

const props = defineProps<{
  node: CategoryItem
  depth: number
  isAdmin: boolean
  expandedIds: Set<number>
  apiBase: string
}>()

defineEmits<{
  toggle: [id: number]
  edit: [cat: CategoryItem]
  'add-child': [parentId: number]
  delete: [cat: CategoryItem]
}>()

const isExpanded = computed(() => props.expandedIds.has(props.node.id))
</script>
