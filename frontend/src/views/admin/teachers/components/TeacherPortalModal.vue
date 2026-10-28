<script setup lang="ts">
import { reactive, watch } from 'vue';
import { Teacher } from '../../../../types/school';

const props = defineProps<{
  isOpen: boolean;
  teacher: Teacher | null;
  isSubmitting: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'createAccount', payload: { username: string; password?: string }): void;
}>();

const form = reactive({
  username: '',
  password: '',
});

const formError = reactive({
  username: '',
  password: '',
});

watch(
  () => props.isOpen,
  (open) => {
    if (open && props.teacher) {
      const defaultUsername = (props.teacher.teacher_number || props.teacher.employee_id || `teacher_${props.teacher.id}`).toLowerCase().replace(/[^a-z0-9_]/g, '_');
      form.username = props.teacher.portal_username || defaultUsername;
      form.password = 'Teacher@Hawlwadaag2026';
      formError.username = '';
      formError.password = '';
    }
  },
  { immediate: true }
);

function handleSubmit() {
  formError.username = '';
  formError.password = '';
  let valid = true;

  if (!form.username.trim()) {
    formError.username = 'Portal username is required.';
    valid = false;
  }
  if (!form.password.trim() || form.password.length < 6) {
    formError.password = 'Password must be at least 6 characters.';
    valid = false;
  }

  if (!valid) return;

  emit('createAccount', {
    username: form.username.toLowerCase().trim(),
    password: form.password,
  });
}
</script>

<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
      <div class="modal-dialog" @click.stop>
        <!-- Header -->
        <div class="modal-header">
          <div class="modal-title-box">
            <svg class="modal-title-icon text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <div>
              <h3 class="modal-title">Teacher Portal Authentication</h3>
              <p class="modal-subtitle">
                Configure portal credentials for <strong>{{ teacher?.full_name || teacher?.first_name }}</strong>.
              </p>
            </div>
          </div>
          <button type="button" class="btn-close" @click="emit('close')">&times;</button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <div v-if="teacher?.has_portal_access" class="portal-active-banner">
            <svg class="w-5 h-5 text-emerald-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <span class="font-semibold text-emerald-900 text-sm">Portal Account is Active</span>
              <p class="text-xs text-emerald-700 mt-0.5">
                Username: <code>{{ teacher.portal_username || teacher.email }}</code> (Role: TEACHER)
              </p>
            </div>
          </div>

          <div v-else class="portal-info-box">
            <p class="text-xs text-slate-600">
              Provisioning a portal account grants this faculty member direct access to the Education Management System Teacher Portal to record student attendance, enter exam marks, and view timetable schedules.
            </p>
          </div>

          <div class="form-grid mt-4">
            <div class="form-group">
              <label class="form-label">Portal Username <span class="required">*</span></label>
              <input
                v-model="form.username"
                type="text"
                class="form-input code-input"
                :class="{ error: formError.username }"
                placeholder="username"
              />
              <span v-if="formError.username" class="err-text">{{ formError.username }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Password <span class="required">*</span></label>
              <input
                v-model="form.password"
                type="text"
                class="form-input"
                :class="{ error: formError.password }"
                placeholder="Temporary password"
              />
              <span v-if="formError.password" class="err-text">{{ formError.password }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" class="btn-cancel" :disabled="isSubmitting" @click="emit('close')">
            Cancel
          </button>
          <button type="button" class="btn-submit" :disabled="isSubmitting" @click="handleSubmit">
            <span v-if="isSubmitting">Provisioning...</span>
            <span v-else>{{ teacher?.has_portal_access ? 'Update Credentials' : 'Provision Portal Account' }}</span>
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
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-dialog {
  width: 100%;
  max-width: min(480px, calc(100vw - 20px));
  max-height: calc(100vh - 24px);
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.modal-title-box {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  min-width: 0;
}

.modal-title-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  margin-top: 2px;
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

.btn-close {
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
  transition: all 0.12s ease;
  flex-shrink: 0;
}

.btn-close:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.portal-active-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  padding: 0.75rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 8px;
}

.portal-info-box {
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
}

.required {
  color: #e11d48;
}

.form-input {
  height: 40px;
  padding: 0 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
  width: 100%;
}

.form-input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.form-input.error {
  border-color: #e11d48;
}

.code-input {
  font-family: monospace;
  font-weight: 600;
}

.err-text {
  font-size: 0.6875rem;
  color: #e11d48;
  font-weight: 500;
}

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
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  height: 40px;
  padding: 0 1.25rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-submit:hover {
  background: #1d4ed8;
}

@media (max-width: 480px) {
  .modal-backdrop {
    padding: 8px;
  }

  .modal-dialog {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }
  .btn-cancel,
  .btn-submit {
    width: 100%;
    height: 44px;
  }
}
</style>
