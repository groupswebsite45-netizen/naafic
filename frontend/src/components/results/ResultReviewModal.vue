<script setup lang="ts">
import { SubmissionReviewDetail } from '../../types/resultWorkflow';
import ResultStatusBadge from './ResultStatusBadge.vue';

interface Props {
  isOpen: boolean;
  submission: SubmissionReviewDetail | null;
  isLoading?: boolean;
  isProcessing?: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'approve'): void;
  (e: 'return'): void;
}>();
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-dialog" role="dialog" aria-modal="true">
      <!-- Modal Header -->
      <div class="modal-header">
        <div>
          <div class="modal-pre-title">ADMIN RESULT VERIFICATION</div>
          <h3 class="modal-title">
            {{ submission?.subject_name }} &bull; {{ submission?.class_name }}
          </h3>
          <div class="modal-meta">
            <span>Teacher: <strong>{{ submission?.teacher_name }}</strong></span>
            <span>&bull;</span>
            <span>Exam: {{ submission?.exam_name }} ({{ submission?.academic_year }})</span>
          </div>
        </div>
        <div class="header-right">
          <ResultStatusBadge v-if="submission" :status="submission.status" />
          <button type="button" class="close-btn" aria-label="Close modal" @click="emit('close')">
            &times;
          </button>
        </div>
      </div>

      <!-- Modal Body: Student Marks Sheet -->
      <div class="modal-body">
        <div v-if="submission?.return_reason" class="return-banner">
          <svg class="alert-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <strong>Previously Returned for Correction:</strong>
            <p>{{ submission.return_reason }}</p>
          </div>
        </div>

        <div class="sheet-summary-bar">
          <span>Expected Students: <strong>{{ submission?.expected_students }}</strong></span>
          <span>Submitted: <strong>{{ submission?.completed_students }}</strong></span>
          <span>Pending: <strong>{{ submission?.pending_students }}</strong></span>
        </div>

        <div tabindex="0" role="region" aria-label="Submission marks review table" class="table-container">
          <table class="review-table">
            <thead>
              <tr>
                <th>#</th>
                <th>STUDENT</th>
                <th>ADMISSION NO</th>
                <th class="text-center">ATTENDANCE</th>
                <th class="text-center">MARKS</th>
                <th class="text-center">GRADE</th>
                <th>REMARKS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(std, idx) in submission?.students" :key="std.student_id">
                <td class="idx-col">{{ idx + 1 }}</td>
                <td class="name-col">
                  <strong>{{ std.student_name }}</strong>
                </td>
                <td class="adm-col">{{ std.admission_number }}</td>
                <td class="text-center">
                  <span
                    class="att-tag"
                    :class="std.attendance_status.toLowerCase()"
                  >
                    {{ std.attendance_status }}
                  </span>
                </td>
                <td class="text-center marks-col">
                  <span v-if="std.attendance_status === 'PRESENT' && std.marks_obtained !== null">
                    <strong>{{ std.marks_obtained }}</strong> / {{ std.max_marks }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="text-center">
                  <span v-if="std.grade" class="grade-badge">{{ std.grade }}</span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td class="remarks-col">{{ std.remarks || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal Footer with Actions -->
      <div class="modal-footer">
        <div class="footer-left">
          <button
            type="button"
            class="btn-secondary"
            :disabled="isProcessing"
            @click="emit('close')"
          >
            Close
          </button>
        </div>
        <div class="footer-right">
          <button
            v-if="submission?.status === 'SUBMITTED' || submission?.status === 'UNDER_REVIEW'"
            type="button"
            class="btn-danger"
            :disabled="isProcessing"
            @click="emit('return')"
          >
            Return for Correction
          </button>
          <button
            v-if="submission?.status === 'SUBMITTED' || submission?.status === 'UNDER_REVIEW'"
            type="button"
            class="btn-success"
            :disabled="isProcessing"
            @click="emit('approve')"
          >
            Approve Submission
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 1rem;
}

.modal-dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 14px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.modal-pre-title {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #38bdf8;
  letter-spacing: 0.08em;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0.15rem 0 0.25rem 0;
}

.modal-meta {
  font-size: 0.75rem;
  color: #94a3b8;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.25rem;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  flex-shrink: 0;
}

.close-btn:hover {
  color: #ffffff;
}

.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.return-banner {
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  color: #fca5a5;
  font-size: 0.8125rem;
}

.alert-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: #ef4444;
}

.sheet-summary-bar {
  display: flex;
  gap: 1.5rem;
  font-size: 0.8125rem;
  color: #cbd5e1;
  background-color: #0f172a;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 1px solid #334155;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #334155;
  border-radius: 8px;
}

.review-table {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
}

.review-table th {
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.review-table td {
  padding: 0.65rem 0.85rem;
  border-bottom: 1px solid #334155;
  color: #f8fafc;
}

.idx-col { color: #64748b; font-size: 0.75rem; width: 40px; }
.adm-col { color: #94a3b8; font-variant-numeric: tabular-nums; }
.marks-col { font-variant-numeric: tabular-nums; }
.remarks-col { color: #94a3b8; font-size: 0.75rem; }

.att-tag {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.att-tag.present { background-color: rgba(16, 185, 129, 0.15); color: #34d399; }
.att-tag.absent { background-color: rgba(239, 68, 68, 0.15); color: #f87171; }
.att-tag.excused { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.grade-badge {
  background-color: #334155;
  color: #38bdf8;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
}

.text-center { text-align: center; }
.text-muted { color: #64748b; }

.modal-footer {
  padding: 1rem 1.5rem;
  background-color: #0f172a;
  border-top: 1px solid #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
}

.footer-right {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn-secondary {
  background-color: #334155;
  color: #f8fafc;
  border: none;
  padding: 0.55rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:hover { background-color: #475569; }

.btn-danger {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
  padding: 0.55rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-danger:hover { background-color: #ef4444; color: #ffffff; }

.btn-success {
  background-color: #059669;
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
}

.btn-success:hover { background-color: #047857; }
</style>
