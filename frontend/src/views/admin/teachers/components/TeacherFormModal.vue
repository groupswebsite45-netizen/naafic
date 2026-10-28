<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Teacher } from '../../../../types/school';
import { useFormDraft } from '../../../../composables/useFormDraft';

const props = defineProps<{
  isOpen: boolean;
  isEditing: boolean;
  teacher: Teacher | null;
  isSubmitting: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: any): void;
}>();

const activeTab = ref<'personal' | 'professional' | 'portal'>('personal');

const form = reactive({
  teacher_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: 'Male',
  date_of_birth: '',
  phone: '',
  email: '',
  address: '',
  qualification: 'B.Sc. Education',
  hire_date: new Date().toISOString().split('T')[0],
  status: 'ACTIVE',
  create_portal_account: false,
  portal_username: '',
  portal_password: '',
});

const formErrors = reactive<Record<string, string>>({});

function resetCreateForm() {
  const randomHex = Math.floor(1000 + Math.random() * 9000);
  form.teacher_number = `TCH-${randomHex}`;
  form.first_name = '';
  form.middle_name = '';
  form.last_name = '';
  form.gender = 'Male';
  form.date_of_birth = '';
  form.phone = '';
  form.email = '';
  form.address = '';
  form.qualification = 'B.Sc. Education';
  form.hire_date = new Date().toISOString().split('T')[0];
  form.status = 'ACTIVE';
  form.create_portal_account = true;
  form.portal_username = `teacher_${randomHex}`;
  form.portal_password = 'Teacher@Hawlwadaag2026';
}

const {
  hasDraft,
  saveDraft,
  restoreDraft,
  clearDraft,
} = useFormDraft({
  storageKey: 'sms_draft_teacher_create',
  form,
  enabled: () => !props.isEditing,
  isDirty: (f) => !!(f.first_name?.trim() || f.last_name?.trim() || f.email?.trim() || f.phone?.trim() || f.address?.trim()),
  onRestore: (saved) => {
    Object.assign(form, saved);
    if ((saved as any)._tab) {
      activeTab.value = (saved as any)._tab;
    }
  },
});

function discardDraft() {
  clearDraft();
  resetCreateForm();
  activeTab.value = 'personal';
}

// Keep active tab in draft
watch(activeTab, (t) => {
  if (!props.isEditing && hasDraft.value) {
    (form as any)._tab = t;
    saveDraft();
  }
});

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);

      if (props.isEditing && props.teacher) {
        activeTab.value = 'personal';
        form.teacher_number = props.teacher.teacher_number || props.teacher.employee_id || '';
        form.first_name = props.teacher.first_name || '';
        form.middle_name = props.teacher.middle_name || '';
        form.last_name = props.teacher.last_name || '';
        form.gender = props.teacher.gender || 'Male';
        form.date_of_birth = props.teacher.date_of_birth || '';
        form.phone = props.teacher.phone || '';
        form.email = props.teacher.email || '';
        form.address = props.teacher.address || '';
        form.qualification = props.teacher.qualification || '';
        form.hire_date = props.teacher.hire_date || new Date().toISOString().split('T')[0];
        form.status = props.teacher.status || 'ACTIVE';
        form.create_portal_account = false;
        form.portal_username = '';
        form.portal_password = '';
      } else {
        // Create mode: Try restoring draft first
        const restored = restoreDraft();
        if (!restored) {
          activeTab.value = 'personal';
          resetCreateForm();
        }
      }
    }
  },
  { immediate: true }
);

function validate(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let valid = true;

  if (!form.first_name.trim()) {
    formErrors.first_name = 'First name is required.';
    valid = false;
  }
  if (!form.last_name.trim()) {
    formErrors.last_name = 'Last name is required.';
    valid = false;
  }
  if (!form.email.trim()) {
    formErrors.email = 'Email address is required.';
    valid = false;
  }
  if (!form.teacher_number.trim()) {
    formErrors.teacher_number = 'Teacher ID number is required.';
    valid = false;
  }

  if (!props.isEditing && form.create_portal_account) {
    if (!form.portal_username.trim()) {
      formErrors.portal_username = 'Portal username is required.';
      valid = false;
    }
    if (!form.portal_password.trim() || form.portal_password.length < 6) {
      formErrors.portal_password = 'Password must be at least 6 characters.';
      valid = false;
    }
  }

  return valid;
}

function handleSave() {
  if (!validate()) {
    if (formErrors.first_name || formErrors.last_name || formErrors.email) {
      activeTab.value = 'personal';
    } else if (formErrors.teacher_number) {
      activeTab.value = 'professional';
    } else if (formErrors.portal_username || formErrors.portal_password) {
      activeTab.value = 'portal';
    }
    return;
  }

  const payload: any = {
    teacher_number: form.teacher_number.toUpperCase().trim(),
    first_name: form.first_name.trim(),
    middle_name: form.middle_name.trim() || null,
    last_name: form.last_name.trim(),
    gender: form.gender,
    date_of_birth: form.date_of_birth || null,
    phone: form.phone.trim() || null,
    email: form.email.toLowerCase().trim(),
    address: form.address.trim() || null,
    qualification: form.qualification.trim() || null,
    hire_date: form.hire_date || null,
    status: form.status,
  };

  if (!props.isEditing) {
    payload.create_portal_account = form.create_portal_account;
    if (form.create_portal_account) {
      payload.portal_username = form.portal_username.toLowerCase().trim();
      payload.portal_password = form.portal_password;
    }
  }

  emit('save', payload);
}
</script>

<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
      <div class="modal-dialog" @click.stop>
        <!-- Modal Header -->
        <div class="modal-header">
          <div class="modal-title-box">
            <svg class="modal-title-icon text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <div>
              <h3 class="modal-title">{{ isEditing ? 'Edit Faculty Profile' : 'Register New Faculty Member' }}</h3>
              <p class="modal-subtitle">
                {{ isEditing ? 'Update teacher contact, qualification and employment records.' : 'Admit a new teacher and provision optional portal login credentials.' }}
              </p>
            </div>
          </div>
          <button type="button" class="btn-close" @click="emit('close')">&times;</button>
        </div>

        <!-- Draft Restored Banner -->
        <div v-if="!isEditing && hasDraft" class="draft-notice-banner">
          <div class="draft-notice-text">
            <svg class="draft-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v4.59L7.3 9.24a.75.75 0 00-1.1 1.02l3.25 3.5a.75.75 0 001.1 0l3.25-3.5a.75.75 0 10-1.1-1.02l-1.95 2.1V6.75z" clip-rule="evenodd" />
            </svg>
            <span><strong>Draft Restored:</strong> Your previously entered faculty details have been saved and restored.</span>
          </div>
          <button type="button" class="btn-discard-draft" @click="discardDraft">
            Reset / Discard
          </button>
        </div>

        <!-- Navigation Tab Strip -->
        <div class="modal-tabs">
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'personal', has_error: formErrors.first_name || formErrors.last_name || formErrors.email }"
            @click="activeTab = 'personal'"
          >
            <span>1. Personal & Contact</span>
          </button>
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'professional', has_error: formErrors.teacher_number }"
            @click="activeTab = 'professional'"
          >
            <span>2. Professional Profile</span>
          </button>
          <button
            v-if="!isEditing"
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'portal', has_error: formErrors.portal_username || formErrors.portal_password }"
            @click="activeTab = 'portal'"
          >
            <span>3. Portal Account</span>
          </button>
        </div>

        <!-- Modal Body Content -->
        <div class="modal-body">
          <!-- TAB 1: Personal & Contact -->
          <div v-show="activeTab === 'personal'" class="form-grid">
            <div class="form-group">
              <label class="form-label">First Name <span class="required">*</span></label>
              <input
                v-model="form.first_name"
                type="text"
                class="form-input"
                :class="{ error: formErrors.first_name }"
                placeholder="e.g. Ahmed"
              />
              <span v-if="formErrors.first_name" class="err-text">{{ formErrors.first_name }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Middle Name</label>
              <input
                v-model="form.middle_name"
                type="text"
                class="form-input"
                placeholder="e.g. Nur"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Last / Family Name <span class="required">*</span></label>
              <input
                v-model="form.last_name"
                type="text"
                class="form-input"
                :class="{ error: formErrors.last_name }"
                placeholder="e.g. Farah"
              />
              <span v-if="formErrors.last_name" class="err-text">{{ formErrors.last_name }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Gender <span class="required">*</span></label>
              <select v-model="form.gender" class="form-select">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Email Address <span class="required">*</span></label>
              <input
                v-model="form.email"
                type="email"
                class="form-input"
                :class="{ error: formErrors.email }"
                placeholder="e.g. ahmed.farah@hawlwadaag.edu.so"
              />
              <span v-if="formErrors.email" class="err-text">{{ formErrors.email }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input
                v-model="form.phone"
                type="text"
                class="form-input"
                placeholder="e.g. +252 61 5000000"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Date of Birth</label>
              <input
                v-model="form.date_of_birth"
                type="date"
                class="form-input"
              />
            </div>

            <div class="form-group col-span-full">
              <label class="form-label">Residential Address</label>
              <input
                v-model="form.address"
                type="text"
                class="form-input"
                placeholder="District, Street address..."
              />
            </div>
          </div>

          <!-- TAB 2: Professional Profile -->
          <div v-show="activeTab === 'professional'" class="form-grid">
            <div class="form-group">
              <label class="form-label">Teacher ID Number <span class="required">*</span></label>
              <input
                v-model="form.teacher_number"
                type="text"
                class="form-input code-input"
                :class="{ error: formErrors.teacher_number }"
                :disabled="isEditing"
                placeholder="TCH-XXXX"
              />
              <span v-if="formErrors.teacher_number" class="err-text">{{ formErrors.teacher_number }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Status <span class="required">*</span></label>
              <select v-model="form.status" class="form-select">
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
                <option value="ON_LEAVE">On Leave</option>
                <option value="SUSPENDED">Suspended</option>
              </select>
            </div>

            <div class="form-group col-span-full">
              <label class="form-label">Qualification & Specialization</label>
              <input
                v-model="form.qualification"
                type="text"
                class="form-input"
                placeholder="e.g. B.Sc. Mathematics & Physics, Master of Education"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Hire Date</label>
              <input
                v-model="form.hire_date"
                type="date"
                class="form-input"
              />
            </div>
          </div>

          <!-- TAB 3: Portal Account (Register mode only) -->
          <div v-if="!isEditing" v-show="activeTab === 'portal'" class="portal-pane">
            <div class="portal-toggle-row">
              <label class="switch-label">
                <input v-model="form.create_portal_account" type="checkbox" class="switch-input" />
                <span class="switch-slider" />
              </label>
              <div>
                <span class="font-semibold text-slate-800 text-sm">Provision Teacher Portal Account</span>
                <p class="text-xs text-slate-500">Allow this faculty member to access the Teacher Portal for class attendance, grading, and timetable.</p>
              </div>
            </div>

            <div v-if="form.create_portal_account" class="portal-subform form-grid mt-4">
              <div class="form-group">
                <label class="form-label">Portal Username <span class="required">*</span></label>
                <input
                  v-model="form.portal_username"
                  type="text"
                  class="form-input code-input"
                  :class="{ error: formErrors.portal_username }"
                  placeholder="username"
                />
                <span v-if="formErrors.portal_username" class="err-text">{{ formErrors.portal_username }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Temporary Password <span class="required">*</span></label>
                <input
                  v-model="form.portal_password"
                  type="text"
                  class="form-input"
                  :class="{ error: formErrors.portal_password }"
                  placeholder="Min 6 characters"
                />
                <span v-if="formErrors.portal_password" class="err-text">{{ formErrors.portal_password }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button type="button" class="btn-cancel" :disabled="isSubmitting" @click="emit('close')">
            Cancel
          </button>
          <button type="button" class="btn-submit" :disabled="isSubmitting" @click="handleSave">
            <span v-if="isSubmitting">Saving...</span>
            <span v-else>{{ isEditing ? 'Save Changes' : 'Register Faculty Member' }}</span>
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
  max-width: min(680px, calc(100vw - 20px));
  max-height: calc(100vh - 24px);
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
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
  line-height: 1.25;
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

.modal-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  flex-wrap: nowrap;
  flex-shrink: 0;
  scrollbar-width: thin;
}

.tab-btn {
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.12s ease;
  flex-shrink: 0;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tab-btn:hover {
  color: #0f172a;
}

.tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  background: #ffffff;
}

.tab-btn.has_error {
  color: #e11d48;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.875rem;
  width: 100%;
  box-sizing: border-box;
}

.col-span-full {
  grid-column: 1 / -1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.required {
  color: #e11d48;
}

.form-input,
.form-select {
  height: 40px;
  padding: 0 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
  transition: border-color 0.12s ease, box-shadow 0.12s ease;
  box-sizing: border-box;
  width: 100%;
}

.form-input:focus,
.form-select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

.form-input.error,
.form-select.error {
  border-color: #e11d48;
}

.code-input {
  font-family: monospace;
  font-weight: 600;
  text-transform: uppercase;
}

.err-text {
  font-size: 0.6875rem;
  color: #e11d48;
  font-weight: 500;
}

.portal-pane {
  display: flex;
  flex-direction: column;
}

.portal-toggle-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.switch-label {
  position: relative;
  display: inline-block;
  width: 42px;
  height: 24px;
  flex-shrink: 0;
  cursor: pointer;
}

.switch-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: #cbd5e1;
  transition: 0.2s;
  border-radius: 24px;
}

.switch-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.2s;
  border-radius: 50%;
}

.switch-input:checked + .switch-slider {
  background-color: #2563eb;
}

.switch-input:checked + .switch-slider:before {
  transform: translateX(18px);
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
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-submit:hover {
  background: #1d4ed8;
}

/* Draft Notice Banner */
.draft-notice-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.625rem 1.25rem;
  background: #eff6ff;
  border-bottom: 1px solid #bfdbfe;
  color: #1e40af;
  font-size: 0.8125rem;
  flex-shrink: 0;
}

.draft-notice-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.draft-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
  color: #2563eb;
}

.btn-discard-draft {
  background: white;
  border: 1px solid #93c5fd;
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-discard-draft:hover {
  background: #dbeafe;
  color: #1e3a8a;
  border-color: #60a5fa;
}

@media (max-width: 600px) {
  .modal-backdrop {
    padding: 8px;
  }

  .modal-dialog {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .form-grid {
    grid-template-columns: 1fr;
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
