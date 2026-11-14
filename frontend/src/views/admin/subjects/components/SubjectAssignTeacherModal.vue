<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Subject, SchoolClass, Teacher } from '../../../../types/school';
import { classService } from '../../../../services/classService';
import { teacherService } from '../../../../services/teacherService';

const props = defineProps<{
  isOpen: boolean;
  subject: Subject | null;
  isSubmitting: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'assign', payload: {
    teacher_id: number;
    class_id: number;
    academic_year: string;
    section?: string | null;
  }): void;
}>();

const availableClasses = ref<SchoolClass[]>([]);
const availableTeachers = ref<Teacher[]>([]);
const isLoadingOptions = ref(false);

const form = reactive({
  teacher_id: 0,
  class_id: 0,
  academic_year: '2026/2027',
  section: '',
});

const formErrors = reactive<Record<string, string>>({});

async function loadOptions() {
  isLoadingOptions.value = true;
  try {
    const [classesData, teachersData] = await Promise.all([
      classService.getClasses({ status: 'ACTIVE' }),
      teacherService.getTeachers({ status: 'ACTIVE' }),
    ]);
    availableClasses.value = classesData;
    availableTeachers.value = teachersData;
  } catch (err) {
    console.error('Failed to load teachers or classes:', err);
  } finally {
    isLoadingOptions.value = false;
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      form.teacher_id = 0;
      form.class_id = 0;
      form.academic_year = '2026/2027';
      form.section = '';
      loadOptions();
    }
  },
  { immediate: true }
);

function validateForm(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let isValid = true;

  if (!form.teacher_id || form.teacher_id === 0) {
    formErrors.teacher_id = 'Please select a faculty member / teacher.';
    isValid = false;
  }
  if (!form.class_id || form.class_id === 0) {
    formErrors.class_id = 'Please select an academic class.';
    isValid = false;
  }
  if (!form.academic_year.trim()) {
    formErrors.academic_year = 'Academic year is required.';
    isValid = false;
  }

  return isValid;
}

async function checkDuplicateAssignment(): Promise<boolean> {
  if (!props.subject?.id || !form.class_id || !form.academic_year) return true;

  // 1. Check in props.subject.teachers if available
  const subjectTeachers = (props.subject as any)?.teachers;
  if (Array.isArray(subjectTeachers)) {
    const normYear = (y?: string) => (y || '').replace('/', '-').trim();
    const targetNorm = normYear(form.academic_year);
    const existing = subjectTeachers.find(
      (t: any) => t.class_id === Number(form.class_id) && normYear(t.academic_year) === targetNorm
    );
    if (existing) {
      if (form.teacher_id && existing.teacher_id !== Number(form.teacher_id)) {
        formErrors.class_id = 'This subject is already assigned to another teacher in this class.';
        formErrors.general = 'This subject is already assigned to another teacher in this class.';
        return false;
      }
    }
  }

  // 2. Check via API check endpoint
  try {
    const res = await teacherService.checkAssignment({
      class_id: Number(form.class_id),
      subject_id: props.subject.id,
      academic_year: form.academic_year.trim(),
      teacher_id: form.teacher_id ? Number(form.teacher_id) : undefined,
    });
    if (!res.available) {
      formErrors.class_id = res.message || 'This subject is already assigned to another teacher in this class.';
      formErrors.general = res.message || 'This subject is already assigned to another teacher in this class.';
      return false;
    }
  } catch (err: any) {
    console.warn('Assignment check failed:', err);
  }
  return true;
}

watch(
  [() => form.class_id, () => form.teacher_id, () => form.academic_year],
  () => {
    if (form.class_id && form.academic_year) {
      checkDuplicateAssignment();
    }
  }
);

async function handleSubmit() {
  if (!validateForm()) return;
  const isAvailable = await checkDuplicateAssignment();
  if (!isAvailable) return;

  emit('assign', {
    teacher_id: Number(form.teacher_id),
    class_id: Number(form.class_id),
    academic_year: form.academic_year.trim(),
    section: form.section.trim() || null,
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="assign-teacher-title">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M19 8v6m3-3h-6" />
          </svg>
        </div>
        <div class="header-titles">
          <h2 id="assign-teacher-title" class="modal-title">
            Assign Teacher to Subject
          </h2>
          <p class="modal-subtitle">
            Allocate a faculty teacher to teach <strong v-if="subject">{{ subject.name }}</strong> for a class.
          </p>
        </div>
        <button
          type="button"
          class="close-btn"
          title="Close modal"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body Form -->
      <form class="modal-form" @submit.prevent="handleSubmit">
        <div class="form-body">
          <div v-if="isLoadingOptions" class="loading-state">
            <div class="spinner"></div>
            <span>Loading active faculty and classes...</span>
          </div>

          <div v-else class="form-grid">
            <!-- General Duplicate Error Banner -->
            <div v-if="formErrors.general" class="form-group full-width alert-box-error p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              <span>{{ formErrors.general }}</span>
            </div>

            <!-- Faculty / Teacher Selection -->
            <div class="form-group full-width">
              <label class="form-label" for="teacher-select">
                Teacher / Faculty Member <span class="required">*</span>
              </label>
              <select
                id="teacher-select"
                v-model="form.teacher_id"
                class="form-select"
                :class="{ 'has-error': formErrors.teacher_id }"
              >
                <option :value="0" disabled>Select a teacher...</option>
                <option v-for="t in availableTeachers" :key="t.id" :value="t.id">
                  {{ t.first_name }} {{ t.last_name }} ({{ t.teacher_number || t.employee_id || 'Staff' }})
                </option>
              </select>
              <span v-if="formErrors.teacher_id" class="error-msg">{{ formErrors.teacher_id }}</span>
            </div>

            <!-- Class Selection -->
            <div class="form-group full-width">
              <label class="form-label" for="teacher-class-select">
                Target Academic Class <span class="required">*</span>
              </label>
              <select
                id="teacher-class-select"
                v-model="form.class_id"
                class="form-select"
                :class="{ 'has-error': formErrors.class_id }"
              >
                <option :value="0" disabled>Select class...</option>
                <option v-for="c in availableClasses" :key="c.id" :value="c.id">
                  {{ c.name }} ({{ c.code }}) - {{ c.academic_year }}
                </option>
              </select>
              <span v-if="formErrors.class_id" class="error-msg">{{ formErrors.class_id }}</span>
            </div>

            <!-- Academic Year -->
            <div class="form-group">
              <label class="form-label" for="teacher-assign-year">
                Academic Year <span class="required">*</span>
              </label>
              <input
                id="teacher-assign-year"
                v-model="form.academic_year"
                type="text"
                class="form-input"
                :class="{ 'has-error': formErrors.academic_year }"
                placeholder="2026/2027"
              />
              <span v-if="formErrors.academic_year" class="error-msg">{{ formErrors.academic_year }}</span>
            </div>

            <!-- Section (Optional) -->
            <div class="form-group">
              <label class="form-label" for="teacher-assign-section">
                Section (Optional)
              </label>
              <input
                id="teacher-assign-section"
                v-model="form.section"
                type="text"
                class="form-input"
                placeholder="e.g. A, B, Science"
              />
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button
            type="button"
            class="btn-cancel"
            :disabled="isSubmitting"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="isSubmitting || isLoadingOptions"
          >
            <svg
              v-if="isSubmitting"
              class="spinner"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
              <path d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            <span>{{ isSubmitting ? 'Assigning...' : 'Assign Teacher' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
  animation: fadeIn 0.15s ease-out;
}

.modal-panel {
  background: #ffffff;
  border-radius: var(--radius-lg, 0.75rem);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  animation: scaleUp 0.15s ease-out;
  overflow: hidden;
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.header-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md, 0.5rem);
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  flex-shrink: 0;
}

.header-icon-wrap svg {
  width: 1.125rem;
  height: 1.125rem;
}

.header-titles {
  flex: 1;
  min-width: 0;
}

.modal-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
  margin: 0.125rem 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: var(--radius-md, 0.5rem);
  background: none;
  border: none;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: #f1f5f9;
  color: var(--text-main, #0f172a);
}

.close-btn svg {
  width: 1rem;
  height: 1rem;
}

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
}

.form-body {
  padding: 1.25rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem 1rem;
  color: #64748b;
  font-size: 0.875rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.875rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-main, #1e293b);
}

.required {
  color: var(--danger, #ef4444);
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: var(--text-main, #0f172a);
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus {
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.form-input.has-error,
.form-select.has-error {
  border-color: var(--danger, #ef4444);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.875rem;
  padding-right: 2rem;
  cursor: pointer;
}

.error-msg {
  font-size: 0.6875rem;
  color: var(--danger, #ef4444);
  font-weight: 500;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  background: #f8fafc;
}

.btn-cancel {
  height: 2.375rem;
  padding: 0 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-submit:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid #e2e8f0;
  border-top-color: var(--brand-primary, #1e40af);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { transform: scale(0.96); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@media (max-width: 520px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
