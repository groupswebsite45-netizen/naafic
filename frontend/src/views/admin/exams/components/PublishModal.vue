<script setup lang="ts">
import { Exam } from '../../../../types/school';

defineProps<{
  isOpen: boolean;
  exam: Exam | null;
  isPublishing: boolean; // true = publish, false = unpublish
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'confirm', exam: Exam, publish: boolean): void;
  (e: 'cancel'): void;
}>();
</script>

<template>
  <div v-if="isOpen && exam" class="modal-overlay" @click.self="emit('cancel')">
    <div class="modal-card" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div class="icon-circle" :class="{ publish: isPublishing, unpublish: !isPublishing }">
          <svg v-if="isPublishing" class="header-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="header-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.477 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />
            <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
          </svg>
        </div>
        <div>
          <h2 class="modal-title">
            {{ isPublishing ? 'Publish Examination to Student Portal' : 'Unpublish Examination from Portal' }}
          </h2>
          <span class="exam-subtitle">{{ exam.name }} ({{ exam.academic_year }})</span>
        </div>
      </div>

      <div class="modal-body">
        <div v-if="isPublishing" class="notice-box success">
          <svg class="notice-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          <div class="notice-text">
            <strong>Immediate Visibility:</strong>
            Publishing this examination will immediately make its schedule, dates, subject, instructions, and announcement accessible to students enrolled in <strong>{{ exam.school_class?.name || exam.class_name }}</strong> on their Student Portal.
          </div>
        </div>

        <div v-else class="notice-box warning">
          <svg class="notice-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <div class="notice-text">
            <strong>Revoke Visibility:</strong>
            Unpublishing will revoke visibility of this examination and its schedule from the Student Portal. Students will no longer see this exam until republished.
          </div>
        </div>

        <div class="meta-list">
          <div class="meta-item">
            <span class="meta-k">Class:</span>
            <span class="meta-v">{{ exam.school_class?.name || exam.class_name }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-k">Subject:</span>
            <span class="meta-v">{{ exam.subject?.name || exam.subject_name }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-k">Graded Students:</span>
            <span class="meta-v">{{ exam.results_count ?? 0 }} / {{ exam.enrolled_students_count ?? 0 }}</span>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isLoading"
          @click="emit('cancel')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn-action"
          :class="{ publish: isPublishing, unpublish: !isPublishing }"
          :disabled="isLoading"
          @click="emit('confirm', exam, isPublishing)"
        >
          <span v-if="isLoading" class="spinner" />
          <span>{{ isPublishing ? 'Confirm & Publish to Portal' : 'Confirm & Unpublish' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 120;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-card {
  width: 100%;
  max-width: 480px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: modalIn 0.2s ease-out;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1.25rem 0.75rem 1.25rem;
}

.icon-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  flex-shrink: 0;
}

.icon-circle.publish {
  background-color: #ecfdf5;
  color: #059669;
}

.icon-circle.unpublish {
  background-color: #fffbeb;
  color: #d97706;
}

.header-icon {
  width: 24px;
  height: 24px;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.exam-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
}

.modal-body {
  padding: 0.75rem 1.25rem 1.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.notice-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  line-height: 1.45;
}

.notice-box.success {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.notice-box.warning {
  background-color: #fffbeb;
  border: 1px solid #fef08a;
  color: #854d0e;
}

.notice-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.meta-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-k {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
}

.meta-v {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1e293b;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  background-color: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel {
  padding: 0.55rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  color: #ffffff;
}

.btn-action.publish {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.btn-action.unpublish {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.btn-action:disabled, .btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
