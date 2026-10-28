<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { SchoolClass } from '../../../../types/school';

const props = defineProps<{
  schoolClass: SchoolClass;
}>();

const emit = defineEmits<{
  (e: 'edit', schoolClass: SchoolClass): void;
  (e: 'manageStudents', schoolClass: SchoolClass): void;
  (e: 'assignTeacher', schoolClass: SchoolClass): void;
  (e: 'promoteClass', schoolClass: SchoolClass): void;
  (e: 'toggleStatus', schoolClass: SchoolClass): void;
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
  router.push(`/admin/classes/${props.schoolClass.id}`);
}

function handleEdit() {
  closeMenu();
  emit('edit', props.schoolClass);
}

function handleManageStudents() {
  closeMenu();
  emit('manageStudents', props.schoolClass);
}

function handleAssignTeacher() {
  closeMenu();
  emit('assignTeacher', props.schoolClass);
}

function handlePromoteClass() {
  closeMenu();
  emit('promoteClass', props.schoolClass);
}

function handleToggleStatus() {
  closeMenu();
  emit('toggleStatus', props.schoolClass);
}
</script>

<template>
  <div ref="menuRef" class="action-menu-container">
    <button
      type="button"
      class="action-trigger-btn"
      title="Actions"
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
        <span>View Class Profile</span>
      </button>

      <button type="button" class="menu-item" @click="handleEdit">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
          <path d="m15 5 4 4" />
        </svg>
        <span>Edit Class</span>
      </button>

      <button type="button" class="menu-item" @click="handleManageStudents">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M19 8v6m3-3h-6" />
        </svg>
        <span>Enroll Student</span>
      </button>

      <button type="button" class="menu-item" @click="handleAssignTeacher">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M12 6v6m3-3H9" />
        </svg>
        <span>Assign Teacher & Subject</span>
      </button>

      <button type="button" class="menu-item menu-item-promote" @click="handlePromoteClass">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="17 1 21 5 17 9" />
          <path d="M3 11V9a4 4 0 0 1 4-4h14" />
          <polyline points="7 23 3 19 7 15" />
          <path d="M21 13v2a4 4 0 0 1-4 4H3" />
        </svg>
        <span>Promote Class</span>
      </button>

      <div class="menu-divider"></div>

      <button
        type="button"
        class="menu-item"
        :class="schoolClass.status === 'ACTIVE' ? 'menu-item-danger' : 'menu-item-success'"
        @click="handleToggleStatus"
      >
        <template v-if="schoolClass.status === 'ACTIVE'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="m15 9-6 6m0-6 6 6" />
          </svg>
          <span>Deactivate Class</span>
        </template>
        <template v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="m9 12 2 2 4-4" />
          </svg>
          <span>Activate Class</span>
        </template>
      </button>
    </div>
  </div>
</template>

<style scoped>
.action-menu-container {
  position: relative;
  display: inline-flex;
}

.action-trigger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  min-width: 36px;
  min-height: 36px;
  border-radius: 10px;
  background: transparent;
  border: 1px solid transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

.action-trigger-btn:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: scale(1.05);
}

.action-trigger-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 0.35rem);
  width: 15.5rem;
  max-width: calc(100vw - 32px);
  background-color: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.12), 0 6px 12px -2px rgba(15, 23, 42, 0.06);
  padding: 0.45rem;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  box-sizing: border-box;
  animation: scaleIn 0.15s ease-out;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  min-height: 38px;
  padding: 0.5rem 0.65rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.menu-item:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.menu-item svg {
  width: 0.95rem;
  height: 0.95rem;
  color: #64748b;
  flex-shrink: 0;
}

.menu-divider {
  height: 1px;
  background-color: #e2e8f0;
  margin: 0.25rem 0;
}

.menu-item-danger {
  color: #dc2626;
}

.menu-item-danger:hover {
  background-color: #fef2f2;
  color: #b91c1c;
}

.menu-item-danger svg {
  color: #dc2626;
}

.menu-item-success {
  color: #16a34a;
}

.menu-item-success:hover {
  background-color: #f0fdf4;
  color: #15803d;
}

.menu-item-success svg {
  color: #16a34a;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
