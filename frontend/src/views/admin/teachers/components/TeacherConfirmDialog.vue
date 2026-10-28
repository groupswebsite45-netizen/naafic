<script setup lang="ts">
defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'primary';
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();
</script>

<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-backdrop" @click="emit('cancel')">
      <div class="modal-dialog" @click.stop>
        <div class="dialog-body">
          <div class="dialog-icon-box" :class="variant || 'danger'">
            <svg class="dialog-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="dialog-content">
            <h3 class="dialog-title">{{ title }}</h3>
            <p class="dialog-message">{{ message }}</p>
          </div>
        </div>

        <div class="dialog-footer">
          <button type="button" class="btn-cancel" :disabled="isLoading" @click="emit('cancel')">
            {{ cancelText || 'Cancel' }}
          </button>
          <button
            type="button"
            class="btn-confirm"
            :class="variant || 'danger'"
            :disabled="isLoading"
            @click="emit('confirm')"
          >
            <span v-if="isLoading">Processing...</span>
            <span v-else>{{ confirmText || 'Confirm' }}</span>
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-dialog {
  width: 100%;
  max-width: min(440px, calc(100vw - 20px));
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  box-sizing: border-box;
}

.dialog-body {
  padding: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  box-sizing: border-box;
}

.dialog-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dialog-icon-box.danger { background: #fee2e2; color: #dc2626; }
.dialog-icon-box.warning { background: #fef3c7; color: #d97706; }
.dialog-icon-box.primary { background: #eff6ff; color: #2563eb; }

.dialog-icon {
  width: 20px;
  height: 20px;
}

.dialog-content {
  display: flex;
  flex-direction: column;
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
  line-height: 1.4;
}

.dialog-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn-cancel {
  height: 34px;
  padding: 0 0.875rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-confirm {
  height: 34px;
  padding: 0 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
}

.btn-confirm.danger {
  background: #e11d48;
  border: 1px solid #e11d48;
}

.btn-confirm.danger:hover {
  background: #be123c;
}

.btn-confirm.warning {
  background: #d97706;
  border: 1px solid #d97706;
}

.btn-confirm.primary {
  background: #2563eb;
  border: 1px solid #2563eb;
}

@media (max-width: 480px) {
  .dialog-footer {
    flex-direction: column-reverse;
  }
  .btn-cancel,
  .btn-confirm {
    width: 100%;
  }
}
</style>
