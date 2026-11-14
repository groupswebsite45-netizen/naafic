<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { SchoolClass, Student } from '../../../../types/school';
import { classPromotionService } from '../../../../services/classPromotionService';

const props = defineProps<{
  isOpen: boolean;
  student: Student | null;
  availableClasses: SchoolClass[];
  isSubmitting?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'success', data: any): void;
}>();

// Steps: 1 = Form Selection, 2 = Confirmation Step
const currentStep = ref<1 | 2>(1);
const isSubmittingLocal = ref(false);
const localError = ref('');

const form = reactive({
  new_class_id: 0,
  academic_year: '2026/2027',
  reason: '',
  is_promotion: false,
});

const currentClassName = computed(() => {
  if (!props.student) return '—';
  if (props.student.current_class) return props.student.current_class.name;
  if (props.student.enrollments && props.student.enrollments.length > 0) {
    return props.student.enrollments[0].school_class?.name || 'Enrolled Class';
  }
  return 'Unassigned';
});

const selectedNewClass = computed(() => {
  return props.availableClasses.find(c => c.id === Number(form.new_class_id)) || null;
});

const studentDisplayName = computed(() => {
  if (!props.student) return '';
  return props.student.full_name || `${props.student.first_name} ${props.student.last_name}`;
});

// Watch modal opening to reset form
watch(
  () => props.isOpen,
  (open) => {
    if (open && props.student) {
      currentStep.value = 1;
      localError.value = '';
      form.reason = '';
      form.is_promotion = false;

      const currentYear = props.student.current_enrollment?.academic_year || '2026/2027';
      form.academic_year = currentYear;

      // Default selected class to next available or first
      const currentCId = props.student.current_class?.id;
      const otherClasses = props.availableClasses.filter(c => c.id !== currentCId);
      form.new_class_id = otherClasses.length > 0 ? otherClasses[0].id : 0;
    }
  }
);

function handleProceedToConfirmation() {
  localError.value = '';
  if (!form.new_class_id) {
    localError.value = 'Please select a destination class.';
    return;
  }
  if (!form.academic_year.trim()) {
    localError.value = 'Please specify the academic year.';
    return;
  }
  if (props.student?.current_class && props.student.current_class.id === Number(form.new_class_id)) {
    localError.value = 'Destination class must be different from current class.';
    return;
  }
  currentStep.value = 2;
}

function handleBackToForm() {
  currentStep.value = 1;
}

async function handleConfirmClassChange() {
  if (!props.student || !form.new_class_id) return;
  isSubmittingLocal.value = true;
  localError.value = '';
  try {
    const result = await classPromotionService.changeStudentClass(props.student.id, {
      new_class_id: Number(form.new_class_id),
      academic_year: form.academic_year.trim(),
      reason: form.reason.trim() || undefined,
      is_promotion: form.is_promotion,
      preserve_history: true
    });
    emit('success', result);
    emit('close');
  } catch (err: any) {
    localError.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to apply class change.';
  } finally {
    isSubmittingLocal.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen && student" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <polyline points="16 11 18 13 22 9" />
          </svg>
        </div>
        <div class="header-text-wrap">
          <h3 class="modal-title">
            {{ currentStep === 1 ? 'Change Student Class' : 'Confirm Class Change' }}
          </h3>
          <p class="modal-subtitle">
            Student: <strong>{{ studentDisplayName }}</strong> ({{ student.admission_number }})
          </p>
        </div>
        <button class="modal-close" aria-label="Close" @click="emit('close')">&times;</button>
      </div>

      <!-- Error Alert -->
      <div v-if="localError" class="modal-alert-danger">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>{{ localError }}</span>
      </div>

      <!-- STEP 1: FORM SELECTION -->
      <div v-if="currentStep === 1" class="modal-body">
        <div class="current-status-banner">
          <div class="status-col">
            <span class="col-label">Current Class</span>
            <span class="col-value current-highlight">{{ currentClassName }}</span>
          </div>
          <div class="status-divider">→</div>
          <div class="status-col">
            <span class="col-label">Current Status</span>
            <span class="col-value status-active">{{ student.status }}</span>
          </div>
        </div>

        <div class="form-group mt-4">
          <label class="form-label required">Target Class</label>
          <select v-model="form.new_class_id" class="form-control">
            <option :value="0" disabled>Select Destination Class...</option>
            <option
              v-for="c in availableClasses"
              :key="c.id"
              :value="c.id"
              :disabled="student.current_class?.id === c.id"
            >
              {{ c.name }} ({{ c.code }}) {{ c.section ? `• ${c.section}` : '' }}
            </option>
          </select>
        </div>

        <div class="form-group mt-3">
          <label class="form-label required">Academic Year</label>
          <input
            v-model="form.academic_year"
            type="text"
            placeholder="2026/2027"
            class="form-control"
          />
          <span class="form-hint">Specifying a new academic year preserves previous historical enrollment.</span>
        </div>

        <div class="form-group mt-3">
          <label class="form-label">Reason / Justification (Optional)</label>
          <input
            v-model="form.reason"
            type="text"
            placeholder="e.g. Annual Promotion, Stream Reassignment, Mid-term Transfer"
            class="form-control"
          />
        </div>

        <div class="checkbox-row mt-3">
          <label class="checkbox-label">
            <input v-model="form.is_promotion" type="checkbox" class="checkbox-input" />
            <span>Mark as Annual Promotion record</span>
          </label>
        </div>
      </div>

      <!-- STEP 2: CONFIRMATION STEP -->
      <div v-else class="modal-body">
        <div class="confirmation-box">
          <div class="confirmation-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
          </div>
          <h4 class="confirmation-prompt">
            Are you sure you want to move <strong>{{ studentDisplayName }}</strong> from <strong>{{ currentClassName }}</strong> to <strong>{{ selectedNewClass?.name || 'selected class' }}</strong>?
          </h4>
        </div>

        <div class="details-summary-card">
          <div class="summary-row">
            <span class="summary-key">Student:</span>
            <span class="summary-val">{{ studentDisplayName }} ({{ student.admission_number }})</span>
          </div>
          <div class="summary-row">
            <span class="summary-key">Current Class:</span>
            <span class="summary-val text-muted-class">{{ currentClassName }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-key">New Class:</span>
            <span class="summary-val text-brand-class">{{ selectedNewClass?.name }} ({{ selectedNewClass?.code }})</span>
          </div>
          <div class="summary-row">
            <span class="summary-key">Academic Year:</span>
            <span class="summary-val text-year">{{ form.academic_year }}</span>
          </div>
          <div v-if="form.reason" class="summary-row">
            <span class="summary-key">Reason:</span>
            <span class="summary-val">{{ form.reason }}</span>
          </div>
        </div>

        <div class="history-notice">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Historical academic-year records, exam grades, and attendance remain preserved in PostgreSQL.</span>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button
          v-if="currentStep === 1"
          type="button"
          class="btn-cancel"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          v-if="currentStep === 1"
          type="button"
          class="btn-proceed"
          @click="handleProceedToConfirmation"
        >
          <span>Change Class</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>

        <button
          v-if="currentStep === 2"
          type="button"
          class="btn-cancel"
          :disabled="isSubmittingLocal"
          @click="handleBackToForm"
        >
          Cancel
        </button>
        <button
          v-if="currentStep === 2"
          type="button"
          class="btn-confirm"
          :disabled="isSubmittingLocal"
          @click="handleConfirmClassChange"
        >
          <span v-if="isSubmittingLocal">Applying Transaction...</span>
          <span v-else>Confirm Change</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(3px);
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-card {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: min(500px, calc(100vw - 24px));
  max-height: calc(100vh - 32px);
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: modalPop 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon-badge svg {
  width: 20px;
  height: 20px;
}

.header-text-wrap {
  flex: 1;
  min-width: 0;
}

.modal-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.01em;
}

.modal-subtitle {
  font-size: 0.78125rem;
  color: #64748b;
  margin: 0.2rem 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0.25rem;
  border-radius: 6px;
}

.modal-close:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.modal-alert-danger {
  margin: 0.875rem 1.25rem 0;
  padding: 0.65rem 0.875rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.8125rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-alert-danger svg {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
}

.current-status-banner {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-col {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.col-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.04em;
}

.col-value {
  font-size: 0.9375rem;
  font-weight: 700;
}

.current-highlight {
  color: #0f172a;
}

.status-active {
  color: #059669;
}

.status-divider {
  font-size: 1.125rem;
  color: #94a3b8;
  font-weight: 700;
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

.form-label.required::after {
  content: ' *';
  color: #e11d48;
}

.form-control {
  width: 100%;
  height: 38px;
  padding: 0 0.75rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
}

.form-control:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.form-hint {
  font-size: 0.71875rem;
  color: #64748b;
}

.checkbox-row {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #334155;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: #2563eb;
  cursor: pointer;
}

.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

/* Confirmation Step Styles */
.confirmation-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.confirmation-icon {
  color: #2563eb;
  flex-shrink: 0;
}

.confirmation-icon svg {
  width: 22px;
  height: 22px;
}

.confirmation-prompt {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #1e3a8a;
  margin: 0;
  line-height: 1.4;
}

.confirmation-prompt strong {
  font-weight: 700;
  color: #0f172a;
}

.details-summary-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px dashed #f1f5f9;
}

.summary-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.summary-key {
  color: #64748b;
  font-weight: 500;
}

.summary-val {
  font-weight: 600;
  color: #0f172a;
}

.text-muted-class {
  color: #64748b;
}

.text-brand-class {
  color: #2563eb;
  font-weight: 700;
}

.text-year {
  color: #059669;
  font-weight: 700;
}

.history-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.65rem 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #475569;
  line-height: 1.35;
}

.history-notice svg {
  width: 16px;
  height: 16px;
  color: #059669;
  flex-shrink: 0;
}

/* Modal Footer */
.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.625rem;
}

.btn-cancel {
  height: 36px;
  padding: 0 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-cancel:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-proceed {
  height: 36px;
  padding: 0 1.125rem;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-proceed:hover {
  background: #1d4ed8;
}

.btn-proceed svg {
  width: 14px;
  height: 14px;
}

.btn-confirm {
  height: 36px;
  padding: 0 1.25rem;
  background: #16a34a;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(22, 163, 74, 0.2);
}

.btn-confirm:hover:not(:disabled) {
  background: #15803d;
}

.btn-confirm:disabled, .btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}
</style>
