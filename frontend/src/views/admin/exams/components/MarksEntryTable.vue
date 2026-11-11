<script setup lang="ts">
import { ref, computed } from 'vue';
import { ExamStudentSheetItem } from '../../../../types/school';
import GradeBadge from './GradeBadge.vue';

interface EditableStudentSheetItem extends ExamStudentSheetItem {
  draftMarks: string;
  draftRemarks: string;
  hasChanged?: boolean;
}

const props = defineProps<{
  items: ExamStudentSheetItem[];
  maxMarks: number;
  passMarks: number;
  isSaving?: boolean;
}>();

const emit = defineEmits<{
  (e: 'save-marks', payload: { student_id: number; marks_obtained: number; remarks: string }[]): void;
}>();

// Initialize editable local state
const editableRows = ref<EditableStudentSheetItem[]>(
  props.items.map((item) => ({
    ...item,
    draftMarks: item.marks_obtained !== null && item.marks_obtained !== undefined ? String(item.marks_obtained) : '',
    draftRemarks: item.remarks || '',
    hasChanged: false,
  }))
);

function calculateLiveGrade(marksStr: string, maxM: number): string {
  if (!marksStr || isNaN(Number(marksStr))) return '—';
  const val = Number(marksStr);
  if (val < 0 || val > maxM) return 'Invalid';
  const pct = (val / maxM) * 100;
  if (pct >= 90) return 'A+';
  if (pct >= 80) return 'A';
  if (pct >= 70) return 'B';
  if (pct >= 60) return 'C';
  if (pct >= 50) return 'D';
  return 'F';
}

function onMarkChange(row: EditableStudentSheetItem) {
  row.hasChanged = true;
}

function onRemarkChange(row: EditableStudentSheetItem) {
  row.hasChanged = true;
}

const changedCount = computed(() => {
  return editableRows.value.filter((r) => r.hasChanged).length;
});

const validationErrors = computed(() => {
  const errors: string[] = [];
  editableRows.value.forEach((r) => {
    if (r.draftMarks !== '') {
      const val = Number(r.draftMarks);
      if (isNaN(val)) {
        errors.push(`${r.student_name}: Marks must be a valid number.`);
      } else if (val < 0) {
        errors.push(`${r.student_name}: Marks cannot be negative.`);
      } else if (val > props.maxMarks) {
        errors.push(`${r.student_name}: Marks (${val}) cannot exceed maximum (${props.maxMarks}).`);
      }
    }
  });
  return errors;
});

function handleSaveAll() {
  if (validationErrors.value.length > 0) return;

  const toSave = editableRows.value
    .filter((r) => r.draftMarks !== '')
    .map((r) => ({
      student_id: r.student_id,
      marks_obtained: Number(r.draftMarks),
      remarks: r.draftRemarks || ''
    }));

  emit('save-marks', toSave);
}
</script>

<template>
  <div class="marks-table-wrapper">
    <!-- Marks Header Controls -->
    <div class="marks-controls-bar">
      <div class="marks-info">
        <span class="info-item">
          <strong>Scale:</strong> 0 – {{ maxMarks }} points
        </span>
        <span class="info-item">
          <strong>Passing Mark:</strong> {{ passMarks }} points
        </span>
        <span v-if="changedCount > 0" class="unsaved-badge">
          {{ changedCount }} unsaved change(s)
        </span>
      </div>

      <div class="marks-actions">
        <button
          type="button"
          class="save-all-btn"
          :disabled="isSaving || validationErrors.length > 0 || changedCount === 0"
          @click="handleSaveAll"
        >
          <span v-if="isSaving" class="spinner" />
          <svg v-else class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span>{{ isSaving ? 'Saving Marks...' : 'Save All Marks' }}</span>
        </button>
      </div>
    </div>

    <!-- Error Alert if validation fails -->
    <div v-if="validationErrors.length > 0" class="validation-error-banner">
      <div class="error-title">Please fix the following validation errors:</div>
      <ul class="error-list">
        <li v-for="(err, idx) in validationErrors.slice(0, 3)" :key="idx">{{ err }}</li>
        <li v-if="validationErrors.length > 3">...and {{ validationErrors.length - 3 }} more</li>
      </ul>
    </div>

    <!-- Data Table -->
    <div tabindex="0" role="region" aria-label="Marks entry table" class="table-responsive">
      <table class="marks-entry-table">
        <thead>
          <tr>
            <th scope="col" class="th-student">Student Name</th>
            <th scope="col" class="th-adm">Admission #</th>
            <th scope="col" class="th-roll">Roll #</th>
            <th scope="col" class="th-marks">Marks (/ {{ maxMarks }})</th>
            <th scope="col" class="th-grade">Grade</th>
            <th scope="col" class="th-remarks">Remarks</th>
            <th scope="col" class="th-status text-center">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in editableRows"
            :key="row.student_id"
            :class="{ 'row-changed': row.hasChanged, 'row-error': Number(row.draftMarks) > maxMarks || Number(row.draftMarks) < 0 }"
          >
            <!-- Student Name -->
            <td class="td-student">
              <div class="student-cell">
                <span class="student-name">{{ row.student_name }}</span>
                <span v-if="row.gender" class="student-gender">({{ row.gender }})</span>
              </div>
            </td>

            <!-- Admission Number -->
            <td class="td-adm">
              <code class="adm-code">{{ row.admission_number }}</code>
            </td>

            <!-- Roll Number -->
            <td class="td-roll">
              <span>{{ row.roll_number || '—' }}</span>
            </td>

            <!-- Marks Input -->
            <td class="td-marks">
              <div class="input-container">
                <input
                  v-model="row.draftMarks"
                  type="number"
                  step="0.5"
                  min="0"
                  :max="maxMarks"
                  placeholder="0"
                  class="mark-input"
                  :class="{ 'input-invalid': Number(row.draftMarks) > maxMarks || Number(row.draftMarks) < 0 }"
                  @input="onMarkChange(row)"
                />
                <span class="max-suffix">/ {{ maxMarks }}</span>
              </div>
            </td>

            <!-- Grade Preview -->
            <td class="td-grade">
              <GradeBadge :grade="calculateLiveGrade(row.draftMarks, maxMarks)" />
            </td>

            <!-- Remarks Input -->
            <td class="td-remarks">
              <input
                v-model="row.draftRemarks"
                type="text"
                placeholder="Optional teacher remark"
                class="remark-input"
                @input="onRemarkChange(row)"
              />
            </td>

            <!-- Status Indicator -->
            <td class="td-status text-center">
              <span v-if="row.hasChanged" class="status-pill unsaved">Unsaved</span>
              <span v-else-if="row.is_saved" class="status-pill saved">Saved</span>
              <span v-else class="status-pill pending">Pending</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.marks-table-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  width: 100%;
}

.marks-controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.marks-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8125rem;
  color: #475569;
}

.unsaved-badge {
  padding: 0.2rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background-color: #fef3c7;
  color: #b45309;
  border-radius: 9999px;
  border: 1px solid #fde68a;
}

.save-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border: 1px solid #047857;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(5, 150, 105, 0.2);
  transition: all 0.2s;
}

.save-all-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
}

.save-all-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.validation-error-banner {
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #b91c1c;
  font-size: 0.8125rem;
}

.error-title {
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.error-list {
  margin: 0;
  padding-left: 1.25rem;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background-color: #ffffff;
}

.marks-entry-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead {
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

td {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

tr:last-child td {
  border-bottom: none;
}

tr.row-changed {
  background-color: #fffdf5;
}

tr.row-error {
  background-color: #fff5f5;
}

.student-cell {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.student-name {
  font-weight: 600;
  color: #0f172a;
}

.student-gender {
  font-size: 0.75rem;
  color: #64748b;
}

.adm-code {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  background-color: #f1f5f9;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.mark-input {
  width: 72px;
  padding: 0.4rem 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-align: right;
  color: #0f172a;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
}

.mark-input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15);
}

.mark-input.input-invalid {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.max-suffix {
  font-size: 0.75rem;
  color: #94a3b8;
}

.remark-input {
  width: 100%;
  max-width: 260px;
  padding: 0.4rem 0.6rem;
  font-size: 0.8125rem;
  color: #334155;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
}

.remark-input:focus {
  border-color: #4f46e5;
}

.status-pill {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  border-radius: 9999px;
  text-transform: uppercase;
}

.status-pill.saved {
  background-color: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.status-pill.unsaved {
  background-color: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.status-pill.pending {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.text-center {
  text-align: center;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
