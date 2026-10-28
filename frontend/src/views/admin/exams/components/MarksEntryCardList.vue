<script setup lang="ts">
import { ref } from 'vue';
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

function onInputChange(row: EditableStudentSheetItem) {
  row.hasChanged = true;
}

function handleSaveSingle(row: EditableStudentSheetItem) {
  if (row.draftMarks === '') return;
  const val = Number(row.draftMarks);
  if (isNaN(val) || val < 0 || val > props.maxMarks) return;

  emit('save-marks', [
    {
      student_id: row.student_id,
      marks_obtained: val,
      remarks: row.draftRemarks || ''
    }
  ]);
  row.hasChanged = false;
}
</script>

<template>
  <div class="mobile-marks-list">
    <div
      v-for="row in editableRows"
      :key="row.student_id"
      class="student-mark-card"
      :class="{ 'card-changed': row.hasChanged, 'card-invalid': Number(row.draftMarks) > maxMarks || Number(row.draftMarks) < 0 }"
    >
      <div class="card-top">
        <div>
          <span class="student-name">{{ row.student_name }}</span>
          <div class="student-meta">
            <span class="adm-badge">{{ row.admission_number }}</span>
            <span v-if="row.roll_number" class="roll-badge">Roll: {{ row.roll_number }}</span>
          </div>
        </div>
        <div class="grade-preview">
          <GradeBadge :grade="calculateLiveGrade(row.draftMarks, maxMarks)" />
        </div>
      </div>

      <!-- Mark Input Row -->
      <div class="input-row">
        <div class="field-group">
          <label class="field-label">Score (Max: {{ maxMarks }})</label>
          <div class="input-with-suffix">
            <input
              v-model="row.draftMarks"
              type="number"
              step="0.5"
              min="0"
              :max="maxMarks"
              placeholder="0"
              class="score-input"
              @input="onInputChange(row)"
            />
            <span class="suffix">/ {{ maxMarks }}</span>
          </div>
        </div>

        <div class="field-group flex-2">
          <label class="field-label">Remarks</label>
          <input
            v-model="row.draftRemarks"
            type="text"
            placeholder="Remarks"
            class="remark-input"
            @input="onInputChange(row)"
          />
        </div>
      </div>

      <div class="card-bottom">
        <span v-if="row.hasChanged" class="save-status unsaved">Unsaved changes</span>
        <span v-else-if="row.is_saved" class="save-status saved">Saved in PostgreSQL</span>
        <span v-else class="save-status pending">Pending score</span>

        <button
          type="button"
          class="single-save-btn"
          :disabled="isSaving || row.draftMarks === '' || Number(row.draftMarks) > maxMarks || Number(row.draftMarks) < 0"
          @click="handleSaveSingle(row)"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-marks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.student-mark-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.875rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.student-mark-card.card-changed {
  border-color: #fde68a;
  background-color: #fffdfa;
}

.student-mark-card.card-invalid {
  border-color: #fca5a5;
  background-color: #fef2f2;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.student-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
}

.student-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.2rem;
}

.adm-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #475569;
  background-color: #f1f5f9;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.roll-badge {
  font-size: 0.6875rem;
  color: #64748b;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.625rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.field-group.flex-2 {
  flex: 1.6;
}

.field-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.input-with-suffix {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.score-input {
  width: 60px;
  padding: 0.4rem 0.4rem;
  font-size: 0.875rem;
  font-weight: 700;
  text-align: right;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #0f172a;
}

.score-input:focus {
  border-color: #4f46e5;
  outline: none;
}

.suffix {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.remark-input {
  width: 100%;
  padding: 0.4rem 0.5rem;
  font-size: 0.8125rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #0f172a;
}

.remark-input:focus {
  border-color: #4f46e5;
  outline: none;
}

.card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.save-status {
  font-size: 0.6875rem;
  font-weight: 600;
}

.save-status.saved {
  color: #059669;
}

.save-status.unsaved {
  color: #d97706;
}

.save-status.pending {
  color: #94a3b8;
}

.single-save-btn {
  padding: 0.35rem 0.875rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  background-color: #4f46e5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.single-save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
