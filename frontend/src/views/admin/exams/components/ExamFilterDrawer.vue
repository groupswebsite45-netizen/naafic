<script setup lang="ts">
import { reactive, watch } from 'vue';
import { ExamFilterOptions } from '../../../../types/school';

interface FilterState {
  academic_year?: string;
  exam_type?: string;
  class_id?: number;
  subject_id?: number;
  status?: string;
}

const props = defineProps<{
  isOpen: boolean;
  filters: FilterState;
  options: ExamFilterOptions | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'apply', filters: FilterState): void;
  (e: 'reset'): void;
}>();

const localFilters = reactive<FilterState>({
  academic_year: '',
  exam_type: '',
  class_id: undefined,
  subject_id: undefined,
  status: '',
});

watch(
  () => props.filters,
  (newVal) => {
    localFilters.academic_year = newVal.academic_year || '';
    localFilters.exam_type = newVal.exam_type || '';
    localFilters.class_id = newVal.class_id;
    localFilters.subject_id = newVal.subject_id;
    localFilters.status = newVal.status || '';
  },
  { immediate: true, deep: true }
);

function handleApply() {
  emit('apply', { ...localFilters });
  emit('close');
}

function handleReset() {
  localFilters.academic_year = '';
  localFilters.exam_type = '';
  localFilters.class_id = undefined;
  localFilters.subject_id = undefined;
  localFilters.status = '';
  emit('reset');
  emit('close');
}
</script>

<template>
  <div v-if="isOpen" class="drawer-overlay" @click.self="emit('close')">
    <div class="drawer-panel" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
      <div class="drawer-header">
        <h2 id="drawer-title" class="drawer-title">Filter Examinations</h2>
        <button
          type="button"
          class="close-btn"
          aria-label="Close filters"
          @click="emit('close')"
        >
          &times;
        </button>
      </div>

      <div class="drawer-body">
        <!-- Academic Year -->
        <div class="form-group">
          <label class="form-label">Academic Year</label>
          <select v-model="localFilters.academic_year" class="form-select">
            <option value="">All Academic Years</option>
            <option v-for="y in options?.academic_years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>

        <!-- Exam Type -->
        <div class="form-group">
          <label class="form-label">Exam Type</label>
          <select v-model="localFilters.exam_type" class="form-select">
            <option value="">All Exam Types</option>
            <option v-for="t in options?.exam_types" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- Class -->
        <div class="form-group">
          <label class="form-label">Class</label>
          <select v-model="localFilters.class_id" class="form-select">
            <option :value="undefined">All Classes</option>
            <option v-for="c in options?.classes" :key="c.id" :value="c.id">{{ c.name }} ({{ c.code }})</option>
          </select>
        </div>

        <!-- Subject -->
        <div class="form-group">
          <label class="form-label">Subject</label>
          <select v-model="localFilters.subject_id" class="form-select">
            <option :value="undefined">All Subjects</option>
            <option v-for="s in options?.subjects" :key="s.id" :value="s.id">{{ s.name }} ({{ s.code }})</option>
          </select>
        </div>

        <!-- Status -->
        <div class="form-group">
          <label class="form-label">Status</label>
          <select v-model="localFilters.status" class="form-select">
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="SCHEDULED">Scheduled</option>
            <option value="ONGOING">Ongoing / In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="PUBLISHED">Published</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      <div class="drawer-footer">
        <button type="button" class="btn-reset" @click="handleReset">Reset Filters</button>
        <button type="button" class="btn-apply" @click="handleApply">Apply Filters</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 100%;
  max-width: 380px;
  height: 100%;
  background-color: #ffffff;
  box-shadow: -4px 0 25px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  animation: slideLeft 0.25s ease-out;
}

@keyframes slideLeft {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.drawer-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.close-btn {
  font-size: 1.5rem;
  line-height: 1;
  color: #64748b;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0.25rem;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.close-btn:hover {
  color: #0f172a;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-select {
  width: 100%;
  padding: 0.55rem 0.75rem;
  font-size: 0.875rem;
  color: #0f172a;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}

.form-select:focus {
  border-color: #4f46e5;
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
}

.btn-reset {
  flex: 1;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
}

.btn-reset:hover {
  background-color: #f1f5f9;
}

.btn-apply {
  flex: 1.5;
  padding: 0.6rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  border: 1px solid #4338ca;
  border-radius: 6px;
  cursor: pointer;
}

.btn-apply:hover {
  background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
}
</style>
