<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Subject } from '../../../../types/school';

const props = defineProps<{
  subject: Subject;
}>();

const emit = defineEmits<{
  (e: 'edit', subject: Subject): void;
  (e: 'assignClass', subject: Subject): void;
  (e: 'assignTeacher', subject: Subject): void;
  (e: 'toggleStatus', subject: Subject): void;
  (e: 'delete', subject: Subject): void;
}>();

const router = useRouter();
const isOpen = ref(false);
const menuRef = ref<HTMLElement | null>(null);

function toggleMenu() {
  isOpen.value = !isOpen.value;
}

function closeMenu() {
  isOpen.value = false;
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

function handleViewProfile() {
  closeMenu();
  router.push(`/admin/subjects/${props.subject.id}`);
}

function handleEdit() {
  closeMenu();
  emit('edit', props.subject);
}

function handleAssignClass() {
  closeMenu();
  emit('assignClass', props.subject);
}

function handleAssignTeacher() {
  closeMenu();
  emit('assignTeacher', props.subject);
}

function handleToggleStatus() {
  closeMenu();
  emit('toggleStatus', props.subject);
}

function handleDelete() {
  closeMenu();
  emit('delete', props.subject);
}
</script>

<template>
  <div ref="menuRef" class="action-menu-container">
    <button
      type="button"
      class="action-trigger-btn"
      title="Subject Actions"
      @click.stop="toggleMenu"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="1" />
        <circle cx="12" cy="5" r="1" />
        <circle cx="12" cy="19" r="1" />
      </svg>
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <button type="button" class="menu-item" @click="handleViewProfile">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
        <span>View Subject Profile</span>
      </button>

      <button type="button" class="menu-item" @click="handleEdit">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
          <path d="m15 5 4 4" />
        </svg>
        <span>Edit Subject</span>
      </button>

      <div class="menu-divider"></div>

      <button type="button" class="menu-item" @click="handleAssignClass">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M6 6h10" />
          <path d="M6 10h10" />
        </svg>
        <span>Assign to Classes</span>
      </button>

      <button type="button" class="menu-item" @click="handleAssignTeacher">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M19 8v6m3-3h-6" />
        </svg>
        <span>Assign Teacher</span>
      </button>

      <div class="menu-divider"></div>

      <button
        type="button"
        class="menu-item"
        :class="subject.status === 'ACTIVE' ? 'warning' : 'success'"
        @click="handleToggleStatus"
      >
        <svg v-if="subject.status === 'ACTIVE'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="10" y1="15" x2="10" y2="9" />
          <line x1="14" y1="15" x2="14" y2="9" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <polygon points="10 8 16 12 10 16 10 8" />
        </svg>
        <span>{{ subject.status === 'ACTIVE' ? 'Deactivate Subject' : 'Activate Subject' }}</span>
      </button>

      <button
        type="button"
        class="menu-item danger"
        @click="handleDelete"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18" />
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
        </svg>
        <span>Delete Subject</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.action-menu-container {
  position: relative;
  display: inline-flex;
  justify-content: center;
}

.action-trigger-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md, 0.5rem);
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-trigger-btn:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
  color: var(--text-main, #0f172a);
}

.action-trigger-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  width: 200px;
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  padding: 0.375rem;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  animation: dropDownIn 0.15s ease-out;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #334155;
  background: none;
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  text-align: left;
  transition: all 0.12s ease;
  box-sizing: border-box;
}

.menu-item svg {
  width: 0.9375rem;
  height: 0.9375rem;
  color: #64748b;
  flex-shrink: 0;
}

.menu-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.menu-item:hover svg {
  color: var(--brand-primary, #1e40af);
}

.menu-item.warning:hover {
  background: #fffbeb;
  color: #b45309;
}

.menu-item.warning:hover svg {
  color: #b45309;
}

.menu-item.success:hover {
  background: #f0fdf4;
  color: #15803d;
}

.menu-item.success:hover svg {
  color: #15803d;
}

.menu-item.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.menu-item.danger:hover svg {
  color: #dc2626;
}

.menu-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 0.25rem 0;
}

@keyframes dropDownIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
