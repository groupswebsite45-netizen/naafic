<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { SchoolClass, Student } from '../../../../types/school';
import { studentService } from '../../../../services/studentService';

const props = defineProps<{
  isOpen: boolean;
  schoolClass: SchoolClass | null;
  isSubmitting: boolean;
  years: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'enroll', payload: { studentId: number; academicYear: string; enrollmentDate?: string }): void;
}>();

const searchQuery = ref('');
const students = ref<Student[]>([]);
const isLoadingStudents = ref(false);
const selectedStudent = ref<Student | null>(null);

const form = reactive({
  academic_year: '2025-2026',
  enrollment_date: new Date().toISOString().split('T')[0],
});

const formError = ref('');

async function searchStudents() {
  if (!searchQuery.value.trim()) {
    students.value = [];
    return;
  }
  isLoadingStudents.value = true;
  formError.value = '';
  try {
    const res = await studentService.getStudents({
      search: searchQuery.value.trim(),
      page: 1,
      page_size: 10,
    });
    students.value = Array.isArray(res) ? res : [];
  } catch (err: any) {
    console.error('Failed to search students:', err);
  } finally {
    isLoadingStudents.value = false;
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      searchQuery.value = '';
      students.value = [];
      selectedStudent.value = null;
      formError.value = '';
      form.academic_year = props.schoolClass?.academic_year || props.years[0] || '2025-2026';
      form.enrollment_date = new Date().toISOString().split('T')[0];
    }
  },
  { immediate: true }
);

function selectStudent(s: Student) {
  selectedStudent.value = s;
}

function handleEnroll() {
  if (!selectedStudent.value) {
    formError.value = 'Please select a student to enroll.';
    return;
  }
  emit('enroll', {
    studentId: selectedStudent.value.id,
    academicYear: form.academic_year,
    enrollmentDate: form.enrollment_date,
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
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M19 8v6m3-3h-6" />
            </svg>
          </div>
          <div>
            <h3 class="modal-title">Enroll Student into Class</h3>
            <p class="modal-subtitle">
              Target Class: <strong>{{ schoolClass?.name }}</strong> ({{ schoolClass?.code }})
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

      <!-- Body -->
      <div class="modal-body">
        <!-- Search Bar -->
        <div class="form-group">
          <label class="form-label">Search Student by Name or Admission #</label>
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              class="form-input"
              placeholder="Type student name or ADM-XXXX..."
              @input="searchStudents"
            />
            <button
              type="button"
              class="search-btn"
              :disabled="isLoadingStudents"
              @click="searchStudents"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Student Search Results List -->
        <div v-if="searchQuery && students.length > 0" class="results-list">
          <div
            v-for="s in students"
            :key="s.id"
            class="student-result-item"
            :class="{ 'is-selected': selectedStudent?.id === s.id }"
            @click="selectStudent(s)"
          >
            <div class="student-avatar">
              {{ (s.first_name[0] || '') + (s.last_name[0] || '') }}
            </div>
            <div class="student-info">
              <span class="student-name">{{ s.full_name || `${s.first_name} ${s.last_name}` }}</span>
              <span class="student-adm">Adm: {{ s.admission_number }} · {{ s.gender }}</span>
            </div>
            <div v-if="selectedStudent?.id === s.id" class="check-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>
        </div>
        <div v-else-if="searchQuery && !isLoadingStudents && students.length === 0" class="empty-search">
          No students found matching "{{ searchQuery }}".
        </div>

        <!-- Selected Student Preview -->
        <div v-if="selectedStudent" class="selected-card">
          <div class="selected-label">Selected Student:</div>
          <div class="selected-content">
            <strong>{{ selectedStudent.full_name || `${selectedStudent.first_name} ${selectedStudent.last_name}` }}</strong>
            <span>({{ selectedStudent.admission_number }})</span>
          </div>
        </div>

        <!-- Academic Settings -->
        <div class="settings-grid">
          <div class="form-group">
            <label class="form-label">Academic Year</label>
            <select v-model="form.academic_year" class="form-select">
              <option v-for="yr in years" :key="yr" :value="yr">
                {{ yr }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Enrollment Date</label>
            <input v-model="form.enrollment_date" type="date" class="form-input" />
          </div>
        </div>

        <div v-if="formError" class="error-banner">
          {{ formError }}
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-cancel" :disabled="isSubmitting" @click="emit('close')">
          Cancel
        </button>
        <button
          type="button"
          class="btn-submit"
          :disabled="!selectedStudent || isSubmitting"
          @click="handleEnroll"
        >
          <svg v-if="isSubmitting" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" />
          </svg>
          <span>Confirm Enrollment</span>
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
  max-width: min(32rem, calc(100vw - 20px));
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

.search-box {
  display: flex;
  gap: 0.5rem;
}

.form-input,
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

.form-input:focus,
.form-select:focus {
  background-color: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.search-btn {
  height: 40px;
  padding: 0 1rem;
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  color: #475569;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.search-btn svg {
  width: 1rem;
  height: 1rem;
}

.results-list {
  max-height: 10rem;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
}

.student-result-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.student-result-item:last-child {
  border-bottom: none;
}

.student-result-item:hover {
  background-color: #f8fafc;
}

.student-result-item.is-selected {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.student-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: #e0e7ff;
  color: #4338ca;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
}

.student-adm {
  font-size: 0.6875rem;
  color: #64748b;
}

.check-icon svg {
  width: 1rem;
  height: 1rem;
  color: #2563eb;
}

.empty-search {
  font-size: 0.8125rem;
  color: #64748b;
  text-align: center;
  padding: 0.75rem;
  background-color: #f8fafc;
  border-radius: 0.5rem;
}

.selected-card {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.5rem;
  padding: 0.625rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
}

.selected-label {
  font-weight: 600;
  color: #166534;
}

.selected-content {
  color: #14532d;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.error-banner {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
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

  .settings-grid {
    grid-template-columns: 1fr;
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
