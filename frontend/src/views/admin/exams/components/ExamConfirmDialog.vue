<script setup lang="ts">
defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDangerous?: boolean;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('cancel')">
    <div class="modal-card" role="alertdialog" aria-modal="true">
      <div class="modal-header">
        <div class="icon-circle" :class="{ danger: isDangerous, primary: !isDangerous }">
          <svg v-if="isDangerous" class="header-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="header-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>
        <h2 class="modal-title">{{ title }}</h2>
      </div>

      <div class="modal-body">
        <p class="modal-message">{{ message }}</p>
      </div>

      <div class="modal-footer">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isLoading"
          @click="emit('cancel')"
        >
          {{ cancelText || 'Cancel' }}
        </button>
        <button
          type="button"
          class="btn-confirm"
          :class="{ danger: isDangerous, primary: !isDangerous }"
          :disabled="isLoading"
          @click="emit('confirm')"
        >
          <span v-if="isLoading" class="spinner" />
          <span>{{ confirmText || 'Confirm' }}</span>
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
  max-width: 440px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  animation: modalIn 0.2s ease-out;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.25rem 0.5rem 1.25rem;
}

.icon-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.icon-circle.danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.icon-circle.primary {
  background-color: #e0e7ff;
  color: #4f46e5;
}

.header-icon {
  width: 22px;
  height: 22px;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-body {
  padding: 0.75rem 1.25rem 1.25rem 1.25rem;
}

.modal-message {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
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

.btn-cancel:hover:not(:disabled) {
  background-color: #f1f5f9;
}

.btn-confirm {
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

.btn-confirm.danger {
  background-color: #dc2626;
}

.btn-confirm.danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-confirm.primary {
  background-color: #4f46e5;
}

.btn-confirm.primary:hover:not(:disabled) {
  background-color: #4338ca;
}

.btn-confirm:disabled, .btn-cancel:disabled {
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
