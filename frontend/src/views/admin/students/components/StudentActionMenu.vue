<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Student } from '../../../../types/school';

const props = defineProps<{
  student: Student;
}>();

const emit = defineEmits<{
  (e: 'edit', student: Student): void;
  (e: 'changeClass', student: Student): void;
  (e: 'managePortal', student: Student): void;
  (e: 'togglePortal', student: Student): void;
  (e: 'loginPortal', student: Student): void;
  (e: 'toggleStatus', student: Student): void;
}>();

const router = useRouter();
const isOpen = ref(false);
const menuRef = ref<HTMLElement | null>(null);

function toggleMenu() {
  isOpen.value = !isOpen.value;
}

function closeMenu(e?: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(e?.target as Node)) {
    isOpen.value = false;
  }
}

function handleView() {
  isOpen.value = false;
  router.push(`/admin/students/${props.student.id}`);
}

function handleEdit() {
  isOpen.value = false;
  emit('edit', props.student);
}

function handleChangeClass() {
  isOpen.value = false;
  emit('changeClass', props.student);
}

function handleManagePortal() {
  isOpen.value = false;
  emit('managePortal', props.student);
}

function handleTogglePortal() {
  isOpen.value = false;
  emit('togglePortal', props.student);
}

function handleLoginPortal() {
  isOpen.value = false;
  emit('loginPortal', props.student);
}

function handleToggleStatus() {
  isOpen.value = false;
  emit('toggleStatus', props.student);
}

onMounted(() => {
  document.addEventListener('click', closeMenu);
});

onUnmounted(() => {
  document.removeEventListener('click', closeMenu);
});
</script>

<template>
  <div ref="menuRef" class="action-menu-container">
    <button
      type="button"
      class="btn-trigger"
      :class="{ active: isOpen }"
      :aria-expanded="isOpen"
      aria-haspopup="true"
      :title="`Actions for ${student.full_name || student.first_name}`"
      :aria-label="`Actions for ${student.full_name || student.first_name}`"
      @click.stop="toggleMenu"
    >
      <svg class="trigger-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
      </svg>
    </button>

    <transition name="pop">
      <div v-if="isOpen" class="menu-dropdown" role="menu">
        <button type="button" class="menu-item" role="menuitem" @click="handleView">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <span>View Profile</span>
        </button>

        <button type="button" class="menu-item" role="menuitem" @click="handleEdit">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span>Edit Details</span>
        </button>

        <button type="button" class="menu-item" role="menuitem" @click="handleChangeClass">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          <span>Change Class</span>
        </button>

        <button type="button" class="menu-item" role="menuitem" @click="handleTogglePortal">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
          </svg>
          <span>{{ student.has_portal_access ? 'Disable Portal Access' : 'Quick Enable Portal' }}</span>
        </button>

        <button type="button" class="menu-item text-emerald-700" role="menuitem" @click="handleLoginPortal">
          <svg class="menu-item-icon text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
          </svg>
          <span style="font-weight: 600; color: #047857;">Log in as Student</span>
        </button>

        <button type="button" class="menu-item" role="menuitem" @click="handleManagePortal">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          <span>Advanced Portal Settings</span>
        </button>

        <div class="menu-divider" />

        <button
          type="button"
          class="menu-item"
          :class="student.status === 'ACTIVE' ? 'danger' : 'success'"
          role="menuitem"
          @click="handleToggleStatus"
        >
          <svg v-if="student.status === 'ACTIVE'" class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <svg v-else class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ student.status === 'ACTIVE' ? 'Deactivate Student' : 'Activate Student' }}</span>
        </button>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.action-menu-container {
  position: relative;
  display: inline-block;
}

.btn-trigger {
  width: 36px;
  height: 36px;
  min-width: 36px;
  min-height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1.5px solid transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

.btn-trigger:hover,
.btn-trigger.active {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #0f172a;
  transform: scale(1.05);
}

.trigger-icon {
  width: 20px;
  height: 20px;
}

.menu-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  width: 205px;
  max-width: calc(100vw - 32px);
  background: #ffffff;
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.16), 0 6px 12px -2px rgba(15, 23, 42, 0.06);
  padding: 0.45rem;
  z-index: 50;
  box-sizing: border-box;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #334155;
  font-size: 0.83rem;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
  white-space: nowrap;
}

.menu-item:hover {
  background: #f8fafc;
  color: #0f172a;
  transform: translateX(2px);
}

.menu-item-icon {
  width: 17px;
  height: 17px;
  color: #64748b;
  flex-shrink: 0;
  transition: color 0.15s ease;
}

.menu-item:hover .menu-item-icon {
  color: #2563eb;
}

.menu-item.danger {
  color: #e11d48;
}

.menu-item.danger:hover {
  background: #fff1f2;
  color: #be123c;
}

.menu-item.danger .menu-item-icon {
  color: #e11d48;
}

.menu-item.success {
  color: #16a34a;
}

.menu-item.success:hover {
  background: #f0fdf4;
  color: #15803d;
}

.menu-item.success .menu-item-icon {
  color: #16a34a;
}

.menu-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.35rem 0;
}

.pop-enter-active,
.pop-leave-active {
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>
