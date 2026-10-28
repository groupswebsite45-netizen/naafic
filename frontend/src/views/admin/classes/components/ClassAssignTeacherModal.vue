<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { SchoolClass, Teacher, Subject } from '../../../../types/school';
import { teacherService } from '../../../../services/teacherService';
import { subjectService } from '../../../../services/subjectService';

const props = defineProps<{
  isOpen: boolean;
  schoolClass: SchoolClass | null;
  isSubmitting: boolean;
  years: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'assign', payload: { teacher_id: number; subject_id: number; academic_year: string }): void;
}>();

const teachers = ref<Teacher[]>([]);
const subjects = ref<Subject[]>([]);
const isLoadingOptions = ref(false);

const form = reactive({
  teacher_id: '',
  subject_id: '',
  academic_year: '2025-2026',
});

const formErrors = reactive<Record<string, string>>({});

async function loadOptions() {
  isLoadingOptions.value = true;
  try {
    const classId = props.schoolClass?.id;
    const division = props.schoolClass?.division;
    const [tRes, sRes] = await Promise.all([
      teacherService.getTeachers({ status: 'ACTIVE', page: 1, page_size: 100 }),
      subjectService.getSubjects({
        status: 'ACTIVE',
        class_id: classId,
        division: division || undefined,
        page: 1,
        page_size: 100
      }),
    ]);
    teachers.value = Array.isArray(tRes) ? tRes : [];
    subjects.value = Array.isArray(sRes) ? sRes : [];
  } catch (err) {
    console.error('Failed to load teachers or subjects:', err);
  } finally {
    isLoadingOptions.value = false;
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      form.teacher_id = '';
      form.subject_id = '';
      form.academic_year = props.schoolClass?.academic_year || props.years[0] || '2025-2026';
      loadOptions();
    }
  },
  { immediate: true }
);

function validateForm(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let isValid = true;

  if (!form.teacher_id) {
    formErrors.teacher_id = 'Please select a teacher.';
    isValid = false;
  }
  if (!form.subject_id) {
    formErrors.subject_id = 'Please select a subject.';
    isValid = false;
  }
  if (!form.academic_year) {
    formErrors.academic_year = 'Academic year is required.';
    isValid = false;
  }
  return isValid;
}

function handleAssign() {
  if (!validateForm()) return;
  emit('assign', {
    teacher_id: Number(form.teacher_id),
    subject_id: Number(form.subject_id),
    academic_year: form.academic_year,
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel">
      <!-- Header -->
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M12 6v6m3-3H9" />
            </svg>
          </div>
          <div>
            <h3 class="modal-title">Assign Teacher & Subject</h3>
            <p class="modal-subtitle">
              Class: <strong>{{ schoolClass?.name }}</strong> ({{ schoolClass?.code }})
            </p>
          </div>
        </div>
        <button type="button" class="modal-close-btn" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Form Body -->
      <form class="modal-body" @submit.prevent="handleAssign">
        <div v-if="isLoadingOptions" class="loading-state">
          <span>Loading teachers and subjects...</span>
        </div>
        <template v-else>
          <!-- Teacher Select -->
          <div class="form-group">
            <label class="form-label required">Select Teacher</label>
            <select
              v-model="form.teacher_id"
              class="form-select"
              :class="{ 'has-error': formErrors.teacher_id }"
            >
              <option value="">-- Choose Teacher --</option>
              <option v-for="t in teachers" :key="t.id" :value="t.id">
                {{ t.full_name || `${t.first_name} ${t.last_name}` }} ({{ t.teacher_number || t.employee_id }})
              </option>
            </select>
            <span v-if="formErrors.teacher_id" class="error-text">{{ formErrors.teacher_id }}</span>
          </div>

          <!-- Subject Select -->
          <div class="form-group">
            <label class="form-label required">Select Subject</label>
            <select
              v-model="form.subject_id"
              class="form-select"
              :class="{ 'has-error': formErrors.subject_id }"
            >
              <option value="">-- Choose Subject --</option>
              <option v-for="s in subjects" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.code }})
              </option>
            </select>
            <span v-if="formErrors.subject_id" class="error-text">{{ formErrors.subject_id }}</span>
          </div>

          <!-- Academic Year -->
          <div class="form-group">
            <label class="form-label required">Academic Year</label>
            <select
              v-model="form.academic_year"
              class="form-select"
              :class="{ 'has-error': formErrors.academic_year }"
            >
              <option v-for="yr in years" :key="yr" :value="yr">
                {{ yr }}
              </option>
            </select>
            <span v-if="formErrors.academic_year" class="error-text">{{ formErrors.academic_year }}</span>
          </div>
        </template>
      </form>

      <!-- Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-cancel" :disabled="isSubmitting" @click="emit('close')">
          Cancel
        </button>
        <button
          type="button"
          class="btn-submit"
          :disabled="isSubmitting || isLoadingOptions"
          @click="handleAssign"
        >
          <svg v-if="isSubmitting" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" />
          </svg>
          <span>Assign Teacher</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
  animation: fadeIn 0.15s ease-out;
}

.modal-panel {
  width: 100%;
  max-width: min(30rem, calc(100vw - 20px));
  background-color: #ffffff;
  border-radius: 0.875rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 24px);
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
  animation: scaleUp 0.18s ease-out;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.modal-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background-color: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.15rem 0 0 0;
  line-height: 1.35;
}

.modal-close-btn {
  background: transparent;
  border: none;
  min-width: 44px;
  min-height: 44px;
  color: #64748b;
  cursor: pointer;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.12s ease;
}

.modal-close-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.modal-close-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.loading-state {
  font-size: 0.8125rem;
  color: #64748b;
  text-align: center;
  padding: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-select {
  width: 100%;
  height: 40px;
  padding: 0 0.75rem;
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.form-select:focus {
  background-color: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.form-select.has-error {
  border-color: #ef4444;
  background-color: #fffbfb;
}

.error-text {
  font-size: 0.75rem;
  color: #ef4444;
  font-weight: 500;
}

.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
}

.btn-cancel {
  height: 40px;
  padding: 0 1.25rem;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  height: 40px;
  padding: 0 1.25rem;
  background-color: #2563eb;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  box-sizing: border-box;
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 0.875rem;
  height: 0.875rem;
  animation: spin 1s linear infinite;
}

.spinner circle {
  stroke-dasharray: 40;
  stroke-dashoffset: 10;
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
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 540px) {
  .modal-overlay {
    padding: 8px;
  }

  .modal-panel {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
    height: 44px;
    justify-content: center;
  }
}
</style>
