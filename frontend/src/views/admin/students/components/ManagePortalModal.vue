<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { Student } from '../../../../types/school';
import { studentService } from '../../../../services/studentService';

const props = defineProps<{
  isOpen: boolean;
  student: Student | null;
  isSubmitting?: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'updated'): void;
}>();

// Tabs for already active accounts
type ActiveTab = 'overview' | 'reset-password' | 'change-username';
const activeTab = ref<ActiveTab>('overview');

// Activation Form
const activateForm = reactive({
  username: '',
  password: 'Student@Hawlwadaag2026',
});

// Reset Password Form
const resetForm = reactive({
  password: 'Student@Hawlwadaag2026',
});

// Change Username Form
const usernameForm = reactive({
  username: '',
});

// Loading & error states
const isActionLoading = ref(false);
const isSuggesting = ref(false);
const formError = ref('');
const formSuccess = ref('');

const studentDisplayName = computed(() => {
  if (!props.student) return '';
  return props.student.full_name || `${props.student.first_name || ''} ${props.student.last_name || ''}`.trim();
});

const studentAdmissionFormatted = computed(() => {
  if (!props.student) return '';
  const adm = props.student.admission_number || '';
  return adm.startsWith('ADM-') ? adm : `ADM-${adm}`;
});

const studentIdFormatted = computed(() => {
  if (!props.student) return '';
  return `STU-${String(props.student.id).padStart(4, '0')}`;
});

const isPortalActive = computed(() => {
  if (!props.student?.has_portal_access) return false;
  return props.student.portal_is_active !== false;
});

// Watch when modal opens
watch(
  () => props.isOpen,
  async (open) => {
    if (open && props.student) {
      formError.value = '';
      formSuccess.value = '';
      activeTab.value = 'overview';
      resetForm.password = 'Student@Hawlwadaag2026';
      usernameForm.username = props.student.portal_username || '';

      if (!props.student.has_portal_access) {
        // Auto-fetch suggested username from backend
        isSuggesting.value = true;
        activateForm.username = '';
        activateForm.password = 'Student@Hawlwadaag2026';
        try {
          const res = await studentService.suggestPortalUsername(props.student.id);
          activateForm.username = res.suggested_username;
        } catch {
          // Fallback client-side generation if network fails
          const fn = (props.student.first_name || 'student').toLowerCase().replace(/[^a-z0-9]/g, '');
          const adm = (props.student.admission_number || '').replace(/[^a-z0-9]/gi, '').toLowerCase();
          activateForm.username = `${fn}${adm}` || `student${props.student.id}`;
        } finally {
          isSuggesting.value = false;
        }
      }
    }
  }
);

function validateUsername(uname: string): string | null {
  const trimmed = uname.trim();
  if (!trimmed) return 'Username is required.';
  if (trimmed.length < 3) return 'Username must be at least 3 characters.';
  if (trimmed.length > 50) return 'Username cannot exceed 50 characters.';
  if (/\s/.test(trimmed)) return 'Username cannot contain spaces.';
  if (!/^[a-zA-Z0-9._-]+$/.test(trimmed)) {
    return 'Username can only contain letters, numbers, underscores, dots, and hyphens.';
  }
  return null;
}

function validatePassword(pwd: string): string | null {
  if (!pwd || pwd.length < 6) {
    return 'Password must be at least 6 characters.';
  }
  return null;
}

// 1. Activate Account
async function handleActivate() {
  if (!props.student) return;
  formError.value = '';
  formSuccess.value = '';

  const uErr = validateUsername(activateForm.username);
  if (uErr) {
    formError.value = uErr;
    return;
  }
  const pErr = validatePassword(activateForm.password);
  if (pErr) {
    formError.value = pErr;
    return;
  }

  isActionLoading.value = true;
  try {
    const res = await studentService.createPortalAccount(props.student.id, {
      username: activateForm.username.trim().toLowerCase(),
      password: activateForm.password,
    });
    formSuccess.value = res.message || 'Portal account activated successfully!';
    setTimeout(() => {
      emit('updated');
      emit('close');
    }, 1200);
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'Failed to activate portal account.';
  } finally {
    isActionLoading.value = false;
  }
}

// 2. Toggle Status (Disable / Enable)
async function handleToggleStatus() {
  if (!props.student) return;
  formError.value = '';
  formSuccess.value = '';

  const nextState = !isPortalActive.value;
  isActionLoading.value = true;
  try {
    const res = await studentService.togglePortalAccess(props.student.id, nextState);
    formSuccess.value = res.message || `Portal ${nextState ? 'enabled' : 'disabled'} successfully.`;
    setTimeout(() => {
      emit('updated');
    }, 1000);
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'Failed to update portal status.';
  } finally {
    isActionLoading.value = false;
  }
}

// 3. Reset Password
async function handleResetPassword() {
  if (!props.student) return;
  formError.value = '';
  formSuccess.value = '';

  const pErr = validatePassword(resetForm.password);
  if (pErr) {
    formError.value = pErr;
    return;
  }

  isActionLoading.value = true;
  try {
    const res = await studentService.resetPortalPassword(props.student.id, resetForm.password);
    formSuccess.value = res.message || 'Password reset successfully.';
    setTimeout(() => {
      activeTab.value = 'overview';
      emit('updated');
    }, 1200);
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'Failed to reset password.';
  } finally {
    isActionLoading.value = false;
  }
}

// 4. Change Username
async function handleChangeUsername() {
  if (!props.student) return;
  formError.value = '';
  formSuccess.value = '';

  const uErr = validateUsername(usernameForm.username);
  if (uErr) {
    formError.value = uErr;
    return;
  }

  isActionLoading.value = true;
  try {
    const res = await studentService.changePortalUsername(props.student.id, usernameForm.username.trim().toLowerCase());
    formSuccess.value = res.message || 'Username updated successfully.';
    setTimeout(() => {
      activeTab.value = 'overview';
      emit('updated');
    }, 1200);
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'Failed to change username.';
  } finally {
    isActionLoading.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen && student" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        </div>
        <div class="header-title-block">
          <h3 class="modal-title">Student Portal Access</h3>
          <p class="modal-subtitle">Configure authentication & portal credentials</p>
        </div>
        <button class="modal-close" @click="emit('close')">&times;</button>
      </div>

      <!-- Student Summary Identity Banner -->
      <div class="student-identity-banner">
        <div class="identity-field">
          <span class="id-label">Student:</span>
          <span class="id-val font-bold">{{ studentDisplayName }}</span>
        </div>
        <div class="identity-meta-row">
          <div class="identity-field">
            <span class="id-label">Admission:</span>
            <span class="id-val font-mono">{{ studentAdmissionFormatted }}</span>
          </div>
          <div class="identity-field">
            <span class="id-label">Student ID:</span>
            <span class="id-val font-mono">{{ studentIdFormatted }}</span>
          </div>
          <div class="identity-field">
            <span class="id-label">Status:</span>
            <span
              class="status-chip"
              :class="{
                'chip-green': student.has_portal_access && isPortalActive,
                'chip-amber': student.has_portal_access && !isPortalActive,
                'chip-gray': !student.has_portal_access
              }"
            >
              {{ !student.has_portal_access ? 'Portal Not Activated' : isPortalActive ? 'Portal Enabled' : 'Portal Disabled' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="formError" class="modal-alert error">
        <svg class="alert-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ formError }}</span>
      </div>
      <div v-if="formSuccess" class="modal-alert success">
        <svg class="alert-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ formSuccess }}</span>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- CASE 1: PORTAL NOT ACTIVATED YET -->
        <div v-if="!student.has_portal_access" class="portal-setup-form">
          <p class="setup-intro">
            Activate this student's dedicated portal account. The username is auto-suggested based on student details and must contain at least 3 characters.
          </p>

          <div class="form-group">
            <div class="label-row">
              <label class="form-label required">Portal Username</label>
              <span v-if="isSuggesting" class="suggest-loading">Generating suggestion...</span>
            </div>
            <input
              v-model="activateForm.username"
              type="text"
              class="form-control"
              placeholder="e.g. suleiman19"
              minlength="3"
              maxlength="50"
              :disabled="isActionLoading || isSuggesting"
            />
            <span class="field-hint">Min 3 chars. Letters, numbers, underscore, dot, or hyphen. No spaces.</span>
          </div>

          <div class="form-group mt-3">
            <label class="form-label required">Initial Temporary Password</label>
            <input
              v-model="activateForm.password"
              type="text"
              class="form-control font-mono"
              placeholder="Min 6 characters"
              :disabled="isActionLoading"
            />
            <span class="field-hint">Secure password hash will be stored. Plaintext password is never saved.</span>
          </div>
        </div>

        <!-- CASE 2: PORTAL ALREADY ACTIVATED -->
        <div v-else class="portal-manage-container">
          <!-- Management Sub-Tabs -->
          <div class="manage-nav-tabs">
            <button
              type="button"
              class="nav-tab-btn"
              :class="{ active: activeTab === 'overview' }"
              @click="activeTab = 'overview'"
            >
              Account Status
            </button>
            <button
              type="button"
              class="nav-tab-btn"
              :class="{ active: activeTab === 'reset-password' }"
              @click="activeTab = 'reset-password'"
            >
              Reset Password
            </button>
            <button
              type="button"
              class="nav-tab-btn"
              :class="{ active: activeTab === 'change-username' }"
              @click="activeTab = 'change-username'"
            >
              Change Username
            </button>
          </div>

          <!-- TAB: Overview & Status Actions -->
          <div v-if="activeTab === 'overview'" class="tab-pane">
            <div class="account-card" :class="isPortalActive ? 'active-card' : 'disabled-card'">
              <div class="account-row">
                <span class="acc-label">Portal Username:</span>
                <span class="acc-val font-mono font-bold">{{ student.portal_username || 'N/A' }}</span>
              </div>
              <div class="account-row">
                <span class="acc-label">Portal Access:</span>
                <span class="acc-status-tag" :class="isPortalActive ? 'tag-enabled' : 'tag-disabled'">
                  {{ isPortalActive ? 'Active & Enabled' : 'Disabled / Suspended' }}
                </span>
              </div>
              <div class="account-row">
                <span class="acc-label">Assigned Role:</span>
                <span class="acc-val font-semibold text-slate-800">STUDENT</span>
              </div>
            </div>

            <div class="quick-action-strip">
              <button
                type="button"
                class="btn-toggle-status"
                :class="isPortalActive ? 'btn-warn' : 'btn-enable'"
                :disabled="isActionLoading"
                @click="handleToggleStatus"
              >
                {{ isPortalActive ? 'Disable Portal Access' : 'Enable Portal Access' }}
              </button>
            </div>
          </div>

          <!-- TAB: Reset Password -->
          <div v-if="activeTab === 'reset-password'" class="tab-pane">
            <p class="tab-desc">
              Set a new temporary password for <strong>{{ student.portal_username }}</strong>. The student can use this password to sign in immediately.
            </p>
            <div class="form-group">
              <label class="form-label required">New Temporary Password</label>
              <input
                v-model="resetForm.password"
                type="text"
                class="form-control font-mono"
                placeholder="Min 6 characters"
                :disabled="isActionLoading"
              />
              <span class="field-hint">Minimum 6 characters. Must satisfy authentication security rules.</span>
            </div>
            <div class="tab-actions mt-3">
              <button
                type="button"
                class="btn-save"
                :disabled="isActionLoading"
                @click="handleResetPassword"
              >
                {{ isActionLoading ? 'Updating Password...' : 'Save New Password' }}
              </button>
            </div>
          </div>

          <!-- TAB: Change Username -->
          <div v-if="activeTab === 'change-username'" class="tab-pane">
            <p class="tab-desc">
              Update the portal login username. Minimum 3 characters. Must be unique across the system.
            </p>
            <div class="form-group">
              <label class="form-label required">New Portal Username</label>
              <input
                v-model="usernameForm.username"
                type="text"
                class="form-control"
                placeholder="e.g. suleiman19"
                minlength="3"
                maxlength="50"
                :disabled="isActionLoading"
              />
              <span class="field-hint">Min 3 chars. Letters, numbers, underscore, dot, hyphen.</span>
            </div>
            <div class="tab-actions mt-3">
              <button
                type="button"
                class="btn-save"
                :disabled="isActionLoading"
                @click="handleChangeUsername"
              >
                {{ isActionLoading ? 'Saving Username...' : 'Update Username' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-cancel" :disabled="isActionLoading" @click="emit('close')">
          {{ student.has_portal_access ? 'Close' : 'Cancel' }}
        </button>
        <button
          v-if="!student.has_portal_access"
          type="button"
          class="btn-save"
          :disabled="isActionLoading || isSuggesting"
          @click="handleActivate"
        >
          <span v-if="isActionLoading">Activating Account...</span>
          <span v-else>Activate Portal Account</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(3px);
  z-index: 70;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  box-sizing: border-box;
}

.modal-card {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: min(520px, calc(100vw - 24px));
  max-height: calc(100vh - 32px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  box-sizing: border-box;
}

.header-icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-title-block {
  flex: 1;
  min-width: 0;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.2rem 0 0;
  line-height: 1.4;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0.125rem;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}
.modal-close:hover {
  color: #0f172a;
}

.student-identity-banner {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.75rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.identity-meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.identity-field {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
}

.id-label {
  color: #64748b;
  font-weight: 500;
}

.id-val {
  color: #1e293b;
}

.status-chip {
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.725rem;
  font-weight: 600;
}

.chip-green {
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.chip-amber {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
}

.chip-gray {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.modal-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.75rem 1.25rem 0;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8125rem;
}

.modal-alert.error {
  background: #fff1f2;
  color: #be123c;
  border: 1px solid #fecdd3;
}

.modal-alert.success {
  background: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.alert-svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  box-sizing: border-box;
}

.setup-intro, .tab-desc {
  font-size: 0.8125rem;
  color: #475569;
  margin: 0 0 1rem;
  line-height: 1.45;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggest-loading {
  font-size: 0.725rem;
  color: #2563eb;
  font-weight: 500;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.form-label.required::after {
  content: ' *';
  color: #e11d48;
}

.form-control {
  width: 100%;
  height: 40px;
  padding: 0 0.85rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
  transition: all 0.15s ease;
}

.form-control:focus {
  background: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.field-hint {
  font-size: 0.735rem;
  color: #64748b;
  line-height: 1.3;
}

.manage-nav-tabs {
  display: flex;
  gap: 0.35rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1rem;
  padding-bottom: 0.25rem;
}

.nav-tab-btn {
  background: none;
  border: none;
  padding: 0.45rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.nav-tab-btn.active {
  background: #eff6ff;
  color: #1d4ed8;
}

.account-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.account-card.active-card {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.account-card.disabled-card {
  border-color: #fde68a;
  background: #fffbeb;
}

.account-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
}

.acc-label {
  color: #64748b;
}

.acc-status-tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.tag-enabled {
  background: #dcfce7;
  color: #166534;
}

.tag-disabled {
  background: #fef3c7;
  color: #92400e;
}

.quick-action-strip {
  display: flex;
  justify-content: flex-end;
}

.btn-toggle-status {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.15s;
}

.btn-warn {
  background: #fff1f2;
  color: #be123c;
  border-color: #fecdd3;
}
.btn-warn:hover {
  background: #ffe4e6;
}

.btn-enable {
  background: #f0fdf4;
  color: #15803d;
  border-color: #bbf7d0;
}
.btn-enable:hover {
  background: #dcfce7;
}

.mt-3 {
  margin-top: 0.85rem;
}

.tab-actions {
  display: flex;
  justify-content: flex-end;
}

.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.625rem;
  background: #f8fafc;
  box-sizing: border-box;
}

.btn-cancel, .btn-save {
  height: 38px;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-cancel {
  padding: 0 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.btn-cancel:hover:not(:disabled) {
  background: #f1f5f9;
}

.btn-save {
  padding: 0 1.25rem;
  background: #2563eb;
  border: none;
  color: #ffffff;
}

.btn-save:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-save:disabled, .btn-cancel:disabled, .btn-toggle-status:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .modal-footer {
    flex-direction: column-reverse;
  }
  .btn-save, .btn-cancel {
    width: 100%;
  }
  .identity-meta-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.35rem;
  }
}
</style>
