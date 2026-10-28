<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { Exam } from '../../../../types/school';

const props = defineProps<{
  exam: Exam;
}>();

const emit = defineEmits<{
  (e: 'view', exam: Exam): void;
  (e: 'edit', exam: Exam): void;
  (e: 'enter-marks', exam: Exam): void;
  (e: 'review-results', exam: Exam): void;
  (e: 'publish', exam: Exam): void;
  (e: 'unpublish', exam: Exam): void;
  (e: 'delete', exam: Exam): void;
}>();

const isOpen = ref(false);
const menuRef = ref<HTMLElement | null>(null);

function toggleMenu(event: MouseEvent) {
  event.stopPropagation();
  isOpen.value = !isOpen.value;
}

function closeMenu() {
  isOpen.value = false;
}

function handleAction(action: 'view' | 'edit' | 'enter-marks' | 'review-results' | 'publish' | 'unpublish' | 'delete') {
  closeMenu();
  switch (action) {
    case 'view': emit('view', props.exam); break;
    case 'edit': emit('edit', props.exam); break;
    case 'enter-marks': emit('enter-marks', props.exam); break;
    case 'review-results': emit('review-results', props.exam); break;
    case 'publish': emit('publish', props.exam); break;
    case 'unpublish': emit('unpublish', props.exam); break;
    case 'delete': emit('delete', props.exam); break;
  }
}

function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div ref="menuRef" class="action-menu-wrapper">
    <button
      type="button"
      class="action-trigger"
      title="Exam Actions"
      aria-label="Exam Actions Menu"
      @click="toggleMenu"
    >
      <svg class="dots-icon" viewBox="0 0 20 20" fill="currentColor">
        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
      </svg>
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <button type="button" class="menu-item" @click="handleAction('view')">
        <svg class="item-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>
        <span>View Exam Profile</span>
      </button>

      <button type="button" class="menu-item" @click="handleAction('review-results')">
        <svg class="item-icon text-indigo" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>Review in Results Center</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.action-menu-wrapper {
  position: relative;
  display: inline-block;
}

.action-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-trigger:hover {
  background-color: var(--bg-surface-secondary, #f1f5f9);
  color: var(--text-primary, #0f172a);
}

.dots-icon {
  width: 18px;
  height: 18px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 50;
  min-width: 180px;
  margin-top: 4px;
  padding: 0.35rem 0;
  background-color: #ffffff;
  border: 1px solid var(--border-medium, #cbd5e1);
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-primary, #1e293b);
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.15s ease;
  white-space: nowrap;
}

.menu-item:hover:not(:disabled) {
  background-color: #f8fafc;
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-icon {
  width: 16px;
  height: 16px;
  color: #64748b;
  flex-shrink: 0;
}

.menu-item:hover .item-icon {
  color: #1e293b;
}

.menu-item.danger {
  color: #dc2626;
}

.menu-item.danger .item-icon {
  color: #dc2626;
}

.menu-item.danger:hover:not(:disabled) {
  background-color: #fef2f2;
}

.menu-item.text-emerald {
  color: #059669;
}

.menu-item.text-emerald .item-icon {
  color: #059669;
}

.menu-item.text-amber {
  color: #d97706;
}

.menu-item.text-amber .item-icon {
  color: #d97706;
}

.menu-divider {
  height: 1px;
  margin: 0.35rem 0;
  background-color: #e2e8f0;
}
</style>
