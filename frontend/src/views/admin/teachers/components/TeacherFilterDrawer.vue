<script setup lang="ts">
import { reactive, watch } from 'vue';
import { SchoolClass, Subject, TeacherFilterParams } from '../../../../types/school';

const props = defineProps<{
  isOpen: boolean;
  filters: TeacherFilterParams;
  availableClasses: SchoolClass[];
  availableSubjects: Subject[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'apply', filters: TeacherFilterParams): void;
  (e: 'reset'): void;
}>();

const draft = reactive<TeacherFilterParams>({
  class_id: undefined,
  subject_id: undefined,
  status: '',
  has_portal: undefined,
  academic_year: '',
});

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      draft.class_id = props.filters.class_id;
      draft.subject_id = props.filters.subject_id;
      draft.status = props.filters.status || '';
      draft.has_portal = props.filters.has_portal;
      draft.academic_year = props.filters.academic_year || '';
    }
  },
  { immediate: true }
);

function handleApply() {
  emit('apply', { ...draft });
  emit('close');
}

function handleReset() {
  draft.class_id = undefined;
  draft.subject_id = undefined;
  draft.status = '';
  draft.has_portal = undefined;
  draft.academic_year = '';
  emit('reset');
  emit('close');
}
</script>

<template>
  <transition name="drawer-fade">
    <div v-if="isOpen" class="drawer-backdrop" @click="emit('close')">
      <div class="drawer-panel" @click.stop>
        <!-- Drawer Header -->
        <div class="drawer-header">
          <div class="drawer-title-box">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            <h3 class="drawer-title">Filter Faculty</h3>
          </div>
          <button type="button" class="btn-close" @click="emit('close')">&times;</button>
        </div>

        <!-- Drawer Body -->
        <div class="drawer-body">
          <!-- Class Filter -->
          <div class="form-group">
            <label class="form-label">Assigned Class</label>
            <select
              v-model="draft.class_id"
              class="form-select"
            >
              <option :value="undefined">All Classes</option>
              <option v-for="c in availableClasses" :key="c.id" :value="c.id">
                {{ c.name }} ({{ c.code }})
              </option>
            </select>
          </div>

          <!-- Subject Filter -->
          <div class="form-group">
            <label class="form-label">Teaching Subject</label>
            <select
              v-model="draft.subject_id"
              class="form-select"
            >
              <option :value="undefined">All Subjects</option>
              <option v-for="s in availableSubjects" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.code }})
              </option>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="form-group">
            <label class="form-label">Employment Status</label>
            <div class="pill-options-grid">
              <button
                type="button"
                class="pill-btn"
                :class="{ active: !draft.status }"
                @click="draft.status = ''"
              >
                All Statuses
              </button>
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.status === 'ACTIVE' }"
                @click="draft.status = 'ACTIVE'"
              >
                Active
              </button>
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.status === 'INACTIVE' }"
                @click="draft.status = 'INACTIVE'"
              >
                Inactive
              </button>
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.status === 'ON_LEAVE' }"
                @click="draft.status = 'ON_LEAVE'"
              >
                On Leave
              </button>
            </div>
          </div>

          <!-- Portal Account Filter -->
          <div class="form-group">
            <label class="form-label">Portal Login Account</label>
            <div class="pill-options-grid">
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.has_portal === undefined }"
                @click="draft.has_portal = undefined"
              >
                All
              </button>
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.has_portal === true }"
                @click="draft.has_portal = true"
              >
                Portal Enabled
              </button>
              <button
                type="button"
                class="pill-btn"
                :class="{ active: draft.has_portal === false }"
                @click="draft.has_portal = false"
              >
                No Portal Account
              </button>
            </div>
          </div>

          <!-- Academic Year -->
          <div class="form-group">
            <label class="form-label">Academic Year</label>
            <select v-model="draft.academic_year" class="form-select">
              <option value="">All Academic Years</option>
              <option value="2025-2026">2025-2026 (Current)</option>
              <option value="2024-2025">2024-2025</option>
            </select>
          </div>
        </div>

        <!-- Drawer Footer -->
        <div class="drawer-footer">
          <button type="button" class="btn-reset" @click="handleReset">
            Reset Filters
          </button>
          <button type="button" class="btn-apply" @click="handleApply">
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(2px);
  z-index: 50;
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 100%;
  max-width: 360px;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.12);
  box-sizing: border-box;
}

.drawer-header {
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}

.drawer-title-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.drawer-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  line-height: 1;
  padding: 0.25rem;
}

.btn-close:hover {
  color: #0f172a;
}

.drawer-body {
  padding: 1.25rem;
  flex: 1 1 0%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.form-select {
  height: 38px;
  padding: 0 0.75rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
}

.form-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.pill-options-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pill-btn {
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.12s ease;
  flex: 1 1 calc(50% - 0.35rem);
  text-align: center;
  box-sizing: border-box;
}

.pill-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.pill-btn.active {
  background: #eff6ff;
  border-color: #2563eb;
  color: #2563eb;
}

.drawer-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f8fafc;
}

.btn-reset {
  flex: 1;
  height: 38px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  box-sizing: border-box;
}

.btn-reset:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-apply {
  flex: 1.5;
  height: 38px;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  box-sizing: border-box;
}

.btn-apply:hover {
  background: #1d4ed8;
}

/* Animations */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-active .drawer-panel,
.drawer-fade-leave-active .drawer-panel {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-fade-enter-from .drawer-panel,
.drawer-fade-leave-to .drawer-panel {
  transform: translateX(100%);
}
</style>
