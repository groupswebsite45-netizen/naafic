<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  isOpen: boolean;
  subjectName: string;
  className: string;
  isProcessing?: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', reason: string): void;
}>();

const reason = ref('');
const error = ref('');

function handleSubmit() {
  if (!reason.value.trim() || reason.value.trim().length < 3) {
    error.value = 'Please provide a descriptive reason for returning this submission.';
    return;
  }
  error.value = '';
  emit('confirm', reason.value.trim());
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-dialog" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg class="header-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div>
          <h3 class="modal-title">Return for Correction</h3>
          <p class="modal-subtitle">
            Returning <strong>{{ subjectName }}</strong> results for <strong>{{ className }}</strong> to teacher.
          </p>
        </div>
      </div>

      <div class="modal-body">
        <label class="form-label" for="returnReason">
          REASON FOR RETURN <span class="required">*</span>
        </label>
        <textarea
          id="returnReason"
          v-model="reason"
          class="form-textarea"
          rows="4"
          placeholder="e.g., Student STU-0021 mark appears incorrect. Please review attendance and assessment score."
          :disabled="isProcessing"
        />
        <span v-if="error" class="error-msg">{{ error }}</span>
        <p class="help-text">
          The teacher will be notified with this exact reason and granted edit access to correct and resubmit the marks sheet.
        </p>
      </div>

      <div class="modal-footer">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isProcessing"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn-return"
          :disabled="isProcessing"
          @click="handleSubmit"
        >
          {{ isProcessing ? 'Returning...' : 'Return Submission' }}
        </button>
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
  z-index: 70;
  padding: 1rem;
}

.modal-dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 1.25rem;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
}

.header-icon-wrap {
  width: 38px;
  height: 38px;
  background-color: rgba(239, 68, 68, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #ef4444;
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0.25rem 0 0 0;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #cbd5e1;
  letter-spacing: 0.06em;
}

.required {
  color: #ef4444;
}

.form-textarea {
  width: 100%;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.75rem;
  color: #ffffff;
  font-size: 0.875rem;
  font-family: inherit;
  resize: vertical;
  outline: none;
}

.form-textarea:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.error-msg {
  color: #f87171;
  font-size: 0.75rem;
  font-weight: 600;
}

.help-text {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
  line-height: 1.4;
}

.modal-footer {
  padding: 1rem 1.25rem;
  background-color: #0f172a;
  border-top: 1px solid #334155;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background-color: #334155;
  color: #f8fafc;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-return {
  background-color: #ef4444;
  color: #ffffff;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-return:hover {
  background-color: #dc2626;
}
</style>
