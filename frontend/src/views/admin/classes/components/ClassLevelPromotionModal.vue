<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { SchoolClass } from '../../../../types/school';
import { classPromotionService, StudentPromotionPreviewItem } from '../../../../services/classPromotionService';

const props = defineProps<{
  isOpen: boolean;
  sourceClass: SchoolClass | null;
  availableClasses: SchoolClass[];
  years: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'success', data: any): void;
}>();

const currentStep = ref<1 | 2>(1); // 1 = Configure, 2 = Preview & Confirm
const isLoadingPreview = ref(false);
const isExecuting = ref(false);
const errorMessage = ref('');

const form = reactive({
  target_class_id: 0,
  source_academic_year: '2026/2027',
  target_academic_year: '2027/2028',
  reason: 'Annual Class-Level Promotion',
});

const previewStudents = ref<StudentPromotionPreviewItem[]>([]);
const totalAffected = ref(0);

const targetClasses = computed(() => {
  if (!props.sourceClass) return props.availableClasses;
  return props.availableClasses.filter(c => c.id !== props.sourceClass?.id && c.status === 'ACTIVE');
});

const selectedTargetClass = computed(() => {
  return props.availableClasses.find(c => c.id === Number(form.target_class_id)) || null;
});

watch(
  () => props.isOpen,
  (open) => {
    if (open && props.sourceClass) {
      currentStep.value = 1;
      errorMessage.value = '';
      previewStudents.value = [];
      totalAffected.value = 0;

      form.source_academic_year = props.sourceClass.academic_year || '2026/2027';
      // Calculate next academic year
      const parts = form.source_academic_year.split(/[/ -]/);
      if (parts.length >= 2 && !isNaN(Number(parts[0])) && !isNaN(Number(parts[1]))) {
        const sep = form.source_academic_year.includes('/') ? '/' : '-';
        form.target_academic_year = `${Number(parts[0]) + 1}${sep}${Number(parts[1]) + 1}`;
      } else {
        form.target_academic_year = '2027/2028';
      }

      // Auto-suggest next class by level
      const match = props.sourceClass.name.match(/(\d+)/);
      if (match) {
        const nextNum = parseInt(match[1]) + 1;
        const autoNext = props.availableClasses.find(c => c.name.includes(String(nextNum)) && c.id !== props.sourceClass?.id);
        form.target_class_id = autoNext ? autoNext.id : (targetClasses.value[0]?.id || 0);
      } else {
        form.target_class_id = targetClasses.value[0]?.id || 0;
      }
    }
  }
);

async function handleGeneratePreview() {
  errorMessage.value = '';
  if (!props.sourceClass || !form.target_class_id) {
    errorMessage.value = 'Please select a destination class.';
    return;
  }
  if (form.source_academic_year === form.target_academic_year) {
    errorMessage.value = 'Source and Target academic years cannot be identical.';
    return;
  }

  isLoadingPreview.value = true;
  try {
    const preview = await classPromotionService.previewBulkPromotion({
      source_academic_year: form.source_academic_year,
      target_academic_year: form.target_academic_year,
      mappings: [
        {
          from_class_id: props.sourceClass.id,
          to_class_id: Number(form.target_class_id),
          action: 'PROMOTE'
        }
      ]
    });

    previewStudents.value = preview.student_previews;
    totalAffected.value = preview.total_students_affected;

    if (preview.validation_errors.length > 0) {
      errorMessage.value = preview.validation_errors.join(' | ');
    } else {
      currentStep.value = 2;
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to generate preview.';
  } finally {
    isLoadingPreview.value = false;
  }
}

async function handleConfirmPromotion() {
  if (!props.sourceClass || !form.target_class_id) return;
  isExecuting.value = true;
  errorMessage.value = '';
  try {
    const result = await classPromotionService.executeClassLevelPromotion({
      from_class_id: props.sourceClass.id,
      to_class_id: Number(form.target_class_id),
      source_academic_year: form.source_academic_year,
      target_academic_year: form.target_academic_year,
      reason: form.reason.trim() || undefined
    });

    emit('success', result);
    emit('close');
  } catch (err: any) {
    errorMessage.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Promotion execution failed.';
  } finally {
    isExecuting.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen && sourceClass" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-icon-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 0 1 4-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 0 1-4 4H3" />
          </svg>
        </div>
        <div class="header-text-wrap">
          <h3 class="modal-title">
            {{ currentStep === 1 ? 'Class-Level Promotion' : 'Class Promotion Preview' }}
          </h3>
          <p class="modal-subtitle">
            Promote students from <strong>{{ sourceClass.name }}</strong> to a destination class.
          </p>
        </div>
        <button class="modal-close" aria-label="Close" @click="emit('close')">&times;</button>
      </div>

      <!-- Alert -->
      <div v-if="errorMessage" class="modal-alert-danger">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- STEP 1: CONFIGURE -->
      <div v-if="currentStep === 1" class="modal-body">
        <div class="flow-preview-box">
          <div class="flow-pill source-pill">
            <span class="pill-label">Current Class</span>
            <strong class="pill-name">{{ sourceClass.name }}</strong>
            <span class="pill-code">{{ sourceClass.code }}</span>
          </div>
          <div class="flow-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>
          <div class="flow-pill target-pill">
            <span class="pill-label">Promote To</span>
            <strong class="pill-name">{{ selectedTargetClass?.name || 'Select Below' }}</strong>
            <span class="pill-code">{{ selectedTargetClass?.code || '—' }}</span>
          </div>
        </div>

        <div class="form-group mt-4">
          <label class="form-label required">Promote To (Destination Class)</label>
          <select v-model="form.target_class_id" class="form-control">
            <option :value="0" disabled>Select Destination Class...</option>
            <option v-for="c in targetClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }}) {{ c.section ? `• ${c.section}` : '' }}
            </option>
          </select>
        </div>

        <div class="grid-2-cols mt-3">
          <div class="form-group">
            <label class="form-label required">From Academic Year</label>
            <input v-model="form.source_academic_year" type="text" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label required">To Academic Year</label>
            <input v-model="form.target_academic_year" type="text" class="form-control" />
          </div>
        </div>

        <div class="form-group mt-3">
          <label class="form-label">Promotion Reason / Notes</label>
          <input
            v-model="form.reason"
            type="text"
            placeholder="e.g. Annual Academic Progression 2026-2027"
            class="form-control"
          />
        </div>

        <div class="safety-tip mt-3">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          <span>All students currently in {{ sourceClass.name }} will be previewed before applying changes.</span>
        </div>
      </div>

      <!-- STEP 2: PREVIEW TABLE & CONFIRM -->
      <div v-else class="modal-body">
        <div class="preview-metrics-bar">
          <div class="metric-item">
            <span class="metric-lbl">Source Class:</span>
            <strong class="metric-val">{{ sourceClass.name }}</strong>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Target Class:</span>
            <strong class="metric-val text-brand">{{ selectedTargetClass?.name }}</strong>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Academic Year:</span>
            <strong class="metric-val text-year">{{ form.source_academic_year }} → {{ form.target_academic_year }}</strong>
          </div>
          <div class="metric-item">
            <span class="metric-lbl">Students Affected:</span>
            <span class="count-badge">{{ totalAffected }}</span>
          </div>
        </div>

        <div class="preview-table-container" tabindex="0" role="region" aria-label="Promotion preview students table">
          <table class="preview-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Admission #</th>
                <th>Current</th>
                <th>New Class</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in previewStudents" :key="s.student_id">
                <td>
                  <span class="student-name-cell">{{ s.student_name }}</span>
                </td>
                <td>
                  <span class="adm-cell">{{ s.admission_number }}</span>
                </td>
                <td>
                  <span class="class-pill from-pill">{{ s.current_class_name }}</span>
                </td>
                <td>
                  <span class="class-pill to-pill">{{ s.target_class_name }}</span>
                </td>
                <td>
                  <span class="status-chip" :class="s.status.toLowerCase()">{{ s.status }}</span>
                </td>
              </tr>
              <tr v-if="previewStudents.length === 0">
                <td colspan="5" class="empty-cell">No active students found in {{ sourceClass.name }}.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="transaction-notice">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Executed in a single database transaction. Historical records remain fully preserved.</span>
        </div>
      </div>

      <!-- Footer -->
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
          :disabled="isLoadingPreview"
          @click="handleGeneratePreview"
        >
          <span v-if="isLoadingPreview">Checking Students...</span>
          <span v-else>Preview Promotion</span>
          <svg v-if="!isLoadingPreview" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>

        <button
          v-if="currentStep === 2"
          type="button"
          class="btn-cancel"
          :disabled="isExecuting"
          @click="currentStep = 1"
        >
          Back
        </button>
        <button
          v-if="currentStep === 2"
          type="button"
          class="btn-confirm"
          :disabled="isExecuting || totalAffected === 0"
          @click="handleConfirmPromotion"
        >
          <span v-if="isExecuting">Executing Promotion...</span>
          <span v-else>Confirm Promotion ({{ totalAffected }} Students)</span>
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
  backdrop-filter: blur(4px);
  z-index: 1000;
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
  max-width: min(640px, calc(100vw - 20px));
  max-height: calc(100vh - 24px);
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  position: relative;
  animation: modalPop 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.header-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #f0fdf4;
  color: #16a34a;
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
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.15rem 0 0;
  line-height: 1.35;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
  transition: all 0.12s ease;
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
  -webkit-overflow-scrolling: touch;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.flow-preview-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  box-sizing: border-box;
}

.flow-pill {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0.75rem 0.875rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  min-width: 0;
  box-sizing: border-box;
}

.source-pill { border-left: 4px solid #64748b; }
.target-pill { border-left: 4px solid #16a34a; }

.pill-label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
}

.pill-name {
  font-size: 1rem;
  color: #0f172a;
  margin: 0.2rem 0;
}

.pill-code {
  font-size: 0.75rem;
  color: #94a3b8;
  font-family: monospace;
}

.flow-arrow {
  color: #16a34a;
  flex-shrink: 0;
}

.flow-arrow svg {
  width: 24px;
  height: 24px;
}

.grid-2-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  width: 100%;
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

.form-label.required::after {
  content: ' *';
  color: #e11d48;
}

.form-control {
  width: 100%;
  height: 40px;
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

.safety-tip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #166534;
}

.safety-tip svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

/* Step 2 Preview */
.preview-metrics-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.65rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.875rem;
  box-sizing: border-box;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.metric-lbl {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 600;
}

.metric-val {
  font-size: 0.875rem;
  color: #0f172a;
}

.text-brand { color: #2563eb; font-weight: 700; }
.text-year { color: #059669; font-weight: 700; }

.count-badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 700;
  width: fit-content;
}

.preview-table-container {
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
}

.preview-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.preview-table th {
  background: #f8fafc;
  padding: 0.55rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 2;
}

.preview-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.student-name-cell {
  font-weight: 600;
  color: #0f172a;
}

.adm-cell {
  font-family: monospace;
  font-size: 0.75rem;
  color: #64748b;
}

.class-pill {
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.from-pill { background: #f1f5f9; color: #475569; }
.to-pill { background: #eff6ff; color: #1d4ed8; }

.status-chip {
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.status-chip.ready { background: #ecfdf5; color: #065f46; }
.status-chip.validation_error { background: #fef2f2; color: #991b1b; }
.status-chip.already_enrolled { background: #fffbeb; color: #92400e; }

.empty-cell {
  text-align: center;
  padding: 2rem !important;
  color: #94a3b8;
}

.transaction-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.875rem;
  font-size: 0.75rem;
  color: #475569;
}

.transaction-notice svg {
  width: 16px;
  height: 16px;
  color: #16a34a;
  flex-shrink: 0;
}

/* Footer */
.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.625rem;
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
}

.btn-cancel {
  height: 40px;
  padding: 0 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-proceed, .btn-confirm {
  height: 40px;
  padding: 0 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  box-sizing: border-box;
}

.btn-proceed { background: #2563eb; }
.btn-proceed:hover { background: #1d4ed8; }
.btn-proceed svg { width: 14px; height: 14px; }

.btn-confirm { background: #16a34a; }
.btn-confirm:hover:not(:disabled) { background: #15803d; }
.btn-confirm:disabled, .btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 580px) {
  .modal-backdrop {
    padding: 8px;
  }

  .modal-card {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .flow-preview-box {
    flex-direction: column;
    align-items: stretch;
  }

  .flow-arrow {
    align-self: center;
    transform: rotate(90deg);
  }

  .grid-2-cols {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .btn-cancel,
  .btn-proceed,
  .btn-confirm {
    width: 100%;
    height: 44px;
    justify-content: center;
  }
}
</style>
