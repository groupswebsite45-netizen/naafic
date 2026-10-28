<script setup lang="ts">
defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmVariant?: 'danger' | 'primary' | 'warning';
  isSubmitting?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm'): void;
}>();
</script>

<template>
  <div v-if="isOpen" class="dialog-overlay" @click.self="emit('close')">
    <div class="dialog-panel">
      <div class="dialog-icon-wrap" :class="`variant-${confirmVariant || 'primary'}`">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>

      <div class="dialog-content">
        <h3 class="dialog-title">{{ title }}</h3>
        <p class="dialog-message">{{ message }}</p>
      </div>

      <div class="dialog-actions">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isSubmitting"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn-confirm"
          :class="`btn-${confirmVariant || 'primary'}`"
          :disabled="isSubmitting"
          @click="emit('confirm')"
        >
          <svg v-if="isSubmitting" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" />
          </svg>
          <span>{{ confirmLabel || 'Confirm' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(2px);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: fadeIn 0.15s ease-out;
}

.dialog-panel {
  width: 100%;
  max-width: 24rem;
  background-color: #ffffff;
  border-radius: 0.875rem;
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  animation: scaleUp 0.18s ease-out;
  box-sizing: border-box;
}

.dialog-icon-wrap {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.dialog-icon-wrap svg {
  width: 1.5rem;
  height: 1.5rem;
}

.variant-primary {
  background-color: #eff6ff;
  color: #1e40af;
}

.variant-warning {
  background-color: #fffbeb;
  color: #d97706;
}

.variant-danger {
  background-color: #fef2f2;
  color: #dc2626;
}

.dialog-content {
  margin-bottom: 1.5rem;
}

.dialog-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.35rem 0;
}

.dialog-message {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}

.btn-cancel {
  flex: 1;
  height: 2.375rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-confirm {
  flex: 1;
  height: 2.375rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  transition: all 0.15s ease;
}

.btn-primary {
  background-color: #1e40af;
}
.btn-primary:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-warning {
  background-color: #d97706;
}
.btn-warning:hover:not(:disabled) {
  background-color: #b45309;
}

.btn-danger {
  background-color: #dc2626;
}
.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-confirm:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 0.875rem;
  height: 0.875rem;
  animation: spin 0.8s linear infinite;
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
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
