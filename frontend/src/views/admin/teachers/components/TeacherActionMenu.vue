<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { Teacher } from '../../../../types/school';

const props = defineProps<{
  teacher: Teacher;
}>();

const emit = defineEmits<{
  (e: 'edit', teacher: Teacher): void;
  (e: 'assign', teacher: Teacher): void;
  (e: 'managePortal', teacher: Teacher): void;
  (e: 'toggleStatus', teacher: Teacher): void;
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
  router.push(`/admin/teachers/${props.teacher.id}`);
}

function handleEdit() {
  isOpen.value = false;
  emit('edit', props.teacher);
}

function handleAssign() {
  isOpen.value = false;
  emit('assign', props.teacher);
}

function handleManagePortal() {
  isOpen.value = false;
  emit('managePortal', props.teacher);
}

function handleToggleStatus() {
  isOpen.value = false;
  emit('toggleStatus', props.teacher);
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
      class="btn-trigger"
      :class="{ active: isOpen }"
      title="Teacher actions"
      @click.stop="toggleMenu"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
      </svg>
    </button>

    <transition name="pop">
      <div v-if="isOpen" class="menu-dropdown">
        <button class="menu-item" @click="handleView">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <span>View Profile</span>
        </button>

        <button class="menu-item" @click="handleEdit">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span>Edit Details</span>
        </button>

        <button class="menu-item" @click="handleAssign">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span>Assign Classes</span>
        </button>

        <button class="menu-item" @click="handleManagePortal">
          <svg class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
          <span>{{ teacher.has_portal_access ? 'Portal Account' : 'Enable Portal' }}</span>
        </button>

        <div class="menu-divider" />

        <button
          class="menu-item"
          :class="teacher.status === 'ACTIVE' ? 'danger' : 'success'"
          @click="handleToggleStatus"
        >
          <svg v-if="teacher.status === 'ACTIVE'" class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <svg v-else class="menu-item-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ teacher.status === 'ACTIVE' ? 'Deactivate Teacher' : 'Activate Teacher' }}</span>
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
