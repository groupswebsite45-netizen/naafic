<script setup lang="ts">
defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary' | 'warning';
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();
</script>

<template>
  <div v-if="isOpen" class="dialog-backdrop" @click.self="emit('cancel')">
    <div class="dialog-card">
      <div class="dialog-header">
        <div class="dialog-icon-box" :class="variant || 'danger'">
          <svg v-if="variant === 'primary'" class="dialog-icon text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="dialog-icon text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="dialog-title-block">
          <h3 class="dialog-title">{{ title }}</h3>
          <p class="dialog-message">{{ message }}</p>
        </div>
      </div>

      <div class="dialog-footer">
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
          :class="variant || 'danger'"
          :disabled="isLoading"
          @click="emit('confirm')"
        >
          {{ isLoading ? 'Processing...' : (confirmText || 'Confirm') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(2px);
  z-index: 70;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  box-sizing: border-box;
}

.dialog-card {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: min(440px, calc(100vw - 20px));
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  border: 1px solid #e2e8f0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 1.125rem 1.25rem;
  display: flex;
  gap: 0.875rem;
  align-items: flex-start;
  box-sizing: border-box;
}

.dialog-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dialog-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.dialog-icon-box.danger { background: #fff1f2; }
.dialog-icon-box.primary { background: #eff6ff; }
.dialog-icon-box.warning { background: #fffbeb; }

.dialog-title-block {
  flex: 1;
  min-width: 0;
}

.dialog-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
}

.dialog-message {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.35rem 0 0;
  line-height: 1.45;
}

.dialog-footer {
  padding: 0.875rem 1.25rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  box-sizing: border-box;
}

.btn-cancel, .btn-confirm {
  height: 36px;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s ease;
  box-sizing: border-box;
}

.btn-cancel {
  padding: 0 0.875rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.btn-cancel:hover {
  background: #f1f5f9;
}

.btn-confirm.danger {
  padding: 0 1rem;
  background: #e11d48;
  border: none;
  color: #ffffff;
}

.btn-confirm.danger:hover:not(:disabled) {
  background: #be123c;
}

.btn-confirm.primary {
  padding: 0 1rem;
  background: #2563eb;
  border: none;
  color: #ffffff;
}

.btn-confirm.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .dialog-footer {
    flex-direction: column-reverse;
  }
  .btn-confirm, .btn-cancel {
    width: 100%;
    justify-content: center;
    display: flex;
    align-items: center;
  }
}
</style>

