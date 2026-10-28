<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  isOpen: boolean;
  departments: string[];
  initialDepartment: string;
  initialStatus: string;
  initialSection: string;
  initialAssignmentState: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (
    e: 'apply',
    filters: {
      department: string;
      status: string;
      section: string;
      assignmentState: string;
    }
  ): void;
  (e: 'reset'): void;
}>();

const localDepartment = ref(props.initialDepartment);
const localStatus = ref(props.initialStatus);
const localSection = ref(props.initialSection);
const localAssignmentState = ref(props.initialAssignmentState);

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      localDepartment.value = props.initialDepartment;
      localStatus.value = props.initialStatus;
      localSection.value = props.initialSection;
      localAssignmentState.value = props.initialAssignmentState;
    }
  }
);

function handleApply() {
  emit('apply', {
    department: localDepartment.value,
    status: localStatus.value,
    section: localSection.value,
    assignmentState: localAssignmentState.value,
  });
  emit('close');
}

function handleReset() {
  localDepartment.value = '';
  localStatus.value = '';
  localSection.value = '';
  localAssignmentState.value = '';
  emit('reset');
  emit('close');
}
</script>

<template>
  <div v-if="isOpen" class="drawer-overlay" @click.self="emit('close')">
    <div class="drawer-panel" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <!-- Header -->
      <div class="drawer-header">
        <div class="header-title-group">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="header-icon">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          <h2 id="drawer-title" class="drawer-title">Filter Subjects</h2>
        </div>
        <button
          type="button"
          class="close-drawer-btn"
          title="Close filter drawer"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="drawer-body">
        <!-- Department Filter -->
        <div class="filter-group">
          <label class="filter-label">Academic Department</label>
          <select v-model="localDepartment" class="filter-select">
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept" :value="dept">
              {{ dept }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div class="filter-group">
          <label class="filter-label">Status</label>
          <select v-model="localStatus" class="filter-select">
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>

        <!-- School Section Filter -->
        <div class="filter-group">
          <label class="filter-label">School Section / Level</label>
          <select v-model="localSection" class="filter-select">
            <option value="">All Sections</option>
            <option value="PRIMARY">Primary Section</option>
            <option value="SECONDARY">Secondary Section</option>
            <option value="BOTH">Both Primary & Secondary</option>
          </select>
        </div>

        <!-- Class Allocation State -->
        <div class="filter-group">
          <label class="filter-label">Class Allocation State</label>
          <select v-model="localAssignmentState" class="filter-select">
            <option value="">All Allocation States</option>
            <option value="ASSIGNED">Assigned to Classes</option>
            <option value="UNASSIGNED">Unassigned (0 Classes)</option>
          </select>
        </div>
      </div>

      <!-- Footer -->
      <div class="drawer-footer">
        <button
          type="button"
          class="btn-reset"
          @click="handleReset"
        >
          Reset All
        </button>
        <div class="footer-actions-right">
          <button
            type="button"
            class="btn-cancel"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn-apply"
            @click="handleApply"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease-out;
}

.drawer-panel {
  width: 100%;
  max-width: 380px;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  animation: slideLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--brand-primary, #1e40af);
}

.drawer-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0;
}

.close-drawer-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md, 0.5rem);
  background: none;
  border: 1px solid transparent;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-drawer-btn:hover {
  background: #f1f5f9;
  color: var(--text-main, #0f172a);
}

.close-drawer-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-main, #1e293b);
}

.filter-select {
  height: 2.5rem;
  padding: 0 2rem 0 0.75rem;
  font-size: 0.875rem;
  color: var(--text-main, #0f172a);
  background-color: #f8fafc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.filter-select:focus {
  background-color: #ffffff;
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  background: #f8fafc;
  gap: 0.75rem;
}

.btn-reset {
  background: none;
  border: none;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.btn-reset:hover {
  color: #ef4444;
  background: #fee2e2;
}

.footer-actions-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-cancel {
  height: 2.25rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-apply {
  height: 2.25rem;
  padding: 0 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-apply:hover {
  background: #1d4ed8;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideLeft {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
