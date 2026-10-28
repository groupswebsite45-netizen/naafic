<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue';
import { SchoolClass, Student } from '../../../../types/school';
import { useFormDraft } from '../../../../composables/useFormDraft';
import { classService } from '../../../../services/classService';

const props = defineProps<{
  isOpen: boolean;
  isEditing: boolean;
  student: Student | null;
  availableClasses: SchoolClass[];
  isSubmitting: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: any): void;
}>();

// Steps: 1 = Personal Details, 2 = Admission & Class, 3 = Guardian Contact, 4 = Portal Account
const currentStep = ref<number>(1);

const form = reactive({
  full_name: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: 'Male',
  date_of_birth: '',
  phone: '',
  address: '',
  admission_number: '',
  admission_date: new Date().toISOString().split('T')[0],
  academic_year: '2026/2027',
  initial_class_id: 0,
  status: 'ACTIVE',
  guardian_name: '',
  guardian_phone: '',
  guardian_email: '',
  guardian_relationship: 'Father',
  create_portal_account: false,
  portal_username: '',
  portal_password: '',
});

const formErrors = reactive<Record<string, string>>({});

const internalClasses = ref<SchoolClass[]>([]);

const displayClasses = computed(() => {
  const map = new Map<number, SchoolClass>();
  if (Array.isArray(props.availableClasses)) {
    props.availableClasses.forEach((c) => {
      if (c && c.id) map.set(c.id, c);
    });
  }
  if (Array.isArray(internalClasses.value)) {
    internalClasses.value.forEach((c) => {
      if (c && c.id) map.set(c.id, c);
    });
  }
  return Array.from(map.values());
});

async function loadModalClasses() {
  try {
    const res = await classService.getClasses({ page_size: 200 });
    const list = Array.isArray(res) ? res : (res as any)?.items || [];
    if (list.length > 0) {
      internalClasses.value = list;
    }
  } catch (err) {
    console.warn('Failed to load active classes for StudentFormModal', err);
  }
}

onMounted(() => {
  loadModalClasses();
});

watch(
  () => form.initial_class_id,
  (newId) => {
    if (newId) {
      const found = displayClasses.value.find((c) => c.id === Number(newId));
      if (found && found.academic_year) {
        form.academic_year = found.academic_year;
      }
    }
  }
);

function resetCreateForm() {
  const randomHex = Math.floor(100000 + Math.random() * 900000);
  form.first_name = '';
  form.middle_name = '';
  form.last_name = '';
  form.full_name = '';
  form.gender = 'Male';
  form.date_of_birth = '';
  form.phone = '';
  form.address = '';
  form.admission_number = `ADM-${randomHex}`;
  form.admission_date = new Date().toISOString().split('T')[0];
  form.academic_year = '2026/2027';
  form.initial_class_id = displayClasses.value.length > 0 ? displayClasses.value[0].id : 0;
  form.status = 'ACTIVE';
  form.guardian_name = '';
  form.guardian_phone = '';
  form.guardian_email = '';
  form.guardian_relationship = 'Father';
  form.create_portal_account = true;
  form.portal_username = `student_${randomHex}`;
  form.portal_password = 'Student@Hawlwadaag2026';
}

const {
  hasDraft,
  saveDraft,
  restoreDraft,
  clearDraft,
} = useFormDraft({
  storageKey: 'sms_draft_student_create',
  form,
  enabled: () => !props.isEditing,
  isDirty: (f) => !!(f.full_name?.trim() || f.first_name?.trim() || f.middle_name?.trim() || f.last_name?.trim() || f.phone?.trim() || f.address?.trim() || f.guardian_name?.trim() || f.guardian_phone?.trim()),
  onRestore: (saved) => {
    Object.assign(form, saved);
    if ((saved as any)._step) {
      currentStep.value = Number((saved as any)._step) || 1;
    }
  },
});

function discardDraft() {
  clearDraft();
  resetCreateForm();
  currentStep.value = 1;
}

// Keep step in draft as well
watch(currentStep, (s) => {
  if (!props.isEditing && hasDraft.value) {
    (form as any)._step = s;
    saveDraft();
  }
});

// Smart synchronization between single Full Name field and first/middle/last name
function syncNamesFromFullName(val: string) {
  const parts = val.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) {
    form.first_name = '';
    form.middle_name = '';
    form.last_name = '';
  } else if (parts.length === 1) {
    form.first_name = parts[0];
    form.middle_name = '';
    form.last_name = parts[0]; // fallback so last_name is satisfied
  } else if (parts.length === 2) {
    form.first_name = parts[0];
    form.middle_name = '';
    form.last_name = parts[1];
  } else {
    form.first_name = parts[0];
    form.middle_name = parts.slice(1, -1).join(' ');
    form.last_name = parts[parts.length - 1];
  }
}

function syncFullNameFromParts() {
  const parts = [form.first_name, form.middle_name, form.last_name].filter(Boolean);
  form.full_name = parts.join(' ');
}

watch(
  () => props.isOpen,
  async (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      await loadModalClasses();

      if (props.isEditing && props.student) {
        currentStep.value = 1;
        form.first_name = props.student.first_name || '';
        form.middle_name = props.student.middle_name || '';
        form.last_name = props.student.last_name || '';
        form.full_name = props.student.full_name || [props.student.first_name, props.student.middle_name, props.student.last_name].filter(Boolean).join(' ');
        form.gender = props.student.gender || 'Male';
        form.date_of_birth = props.student.date_of_birth || '';
        form.phone = props.student.phone || '';
        form.address = props.student.address || '';
        form.admission_number = props.student.admission_number || '';
        form.admission_date = props.student.admission_date || new Date().toISOString().split('T')[0];
        form.status = props.student.status || 'ACTIVE';
        form.guardian_name = props.student.guardian_name || '';
        form.guardian_phone = props.student.guardian_phone || '';
        form.guardian_email = props.student.guardian_email || '';
        form.guardian_relationship = props.student.guardian_relationship || 'Father';
        form.create_portal_account = false;
        form.portal_username = '';
        form.portal_password = '';

        if (props.student.current_class) {
          form.initial_class_id = props.student.current_class.id;
          form.academic_year = props.student.current_class.academic_year || '2026/2027';
        } else if (props.student.enrollments && props.student.enrollments.length > 0) {
          form.initial_class_id = props.student.enrollments[0].class_id;
          form.academic_year = props.student.enrollments[0].academic_year || '2026/2027';
        } else {
          form.initial_class_id = displayClasses.value.length > 0 ? displayClasses.value[0].id : 0;
          form.academic_year = '2026/2027';
        }
      } else {
        // Create mode: Try to restore draft first
        const restored = restoreDraft();
        if (!restored) {
          currentStep.value = 1;
          resetCreateForm();
        } else if ((!form.initial_class_id || form.initial_class_id === 0) && displayClasses.value.length > 0) {
          // If draft had 0 for class (e.g. classes were empty when drafted), default to first available
          form.initial_class_id = displayClasses.value[0].id;
        }
      }
    }
  },
  { immediate: true }
);

// Auto-sync academic year when user selects a class
watch(
  () => form.initial_class_id,
  (newClassId) => {
    if (newClassId && Number(newClassId) > 0) {
      const cls = displayClasses.value.find((c) => c.id === Number(newClassId));
      if (cls && cls.academic_year) {
        form.academic_year = cls.academic_year;
      }
    }
  }
);

const stepTitles = [
  'Personal Details',
  'Admission & Class',
  'Guardian Contact',
  'Portal Account',
];

const totalSteps = computed(() => (props.isEditing ? 3 : 4));

function validateStep(step: number): boolean {
  let valid = true;

  if (step === 1) {
    delete formErrors.first_name;
    delete formErrors.last_name;
    delete formErrors.full_name;

    // Ensure full_name and parts are in sync
    if (form.full_name.trim() && (!form.first_name || !form.last_name)) {
      syncNamesFromFullName(form.full_name);
    } else if (form.first_name && !form.full_name) {
      syncFullNameFromParts();
    }

    if (!form.first_name.trim() && !form.full_name.trim()) {
      formErrors.first_name = 'Student name is required.';
      valid = false;
    }
    if (!form.last_name.trim()) {
      // If single name was provided, duplicate first_name to satisfy database constraint
      if (form.first_name.trim()) {
        form.last_name = form.first_name.trim();
      } else {
        formErrors.last_name = 'Last / family name is required.';
        valid = false;
      }
    }
  }

  if (step === 2) {
    delete formErrors.admission_number;
    if (!form.admission_number.trim()) {
      formErrors.admission_number = 'Admission number is required.';
      valid = false;
    }
  }

  if (step === 4 && !props.isEditing && form.create_portal_account) {
    delete formErrors.portal_username;
    delete formErrors.portal_password;

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

function nextStep() {
  if (validateStep(currentStep.value)) {
    if (currentStep.value < totalSteps.value) {
      currentStep.value++;
    }
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
}

function handleSave() {
  // Validate all steps
  for (let s = 1; s <= totalSteps.value; s++) {
    if (!validateStep(s)) {
      currentStep.value = s;
      return;
    }
  }

  const payload: any = {
    first_name: form.first_name.trim(),
    middle_name: form.middle_name.trim() || null,
    last_name: form.last_name.trim(),
    gender: form.gender,
    date_of_birth: form.date_of_birth || null,
    phone: form.phone.trim() || null,
    address: form.address.trim() || null,
    admission_number: form.admission_number.trim().toUpperCase(),
    admission_date: form.admission_date || null,
    academic_year: form.academic_year,
    status: form.status,
    guardian_name: form.guardian_name.trim() || null,
    guardian_phone: form.guardian_phone.trim() || null,
    guardian_email: form.guardian_email.trim() || null,
    guardian_relationship: form.guardian_relationship || null,
  };

  if (!props.isEditing) {
    payload.initial_class_id = form.initial_class_id ? Number(form.initial_class_id) : null;
    payload.create_portal_account = form.create_portal_account;
    if (form.create_portal_account) {
      payload.portal_username = form.portal_username.trim().toLowerCase();
      payload.portal_password = form.portal_password;
    }
  }

  emit('save', payload);
}
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card" role="dialog" aria-modal="true">
      <!-- Fixed Modal Header -->
      <div class="modal-header">
        <div class="header-text-wrap">
          <h3 class="modal-title">
            {{ isEditing ? 'Edit Student Profile' : 'Register New Student' }}
          </h3>
          <p class="modal-subtitle">
            {{ isEditing ? 'Update student personal, enrollment, and contact records.' : 'Admit a new student into Education Management System database.' }}
          </p>
        </div>
        <button
          type="button"
          class="modal-close"
          aria-label="Close dialog"
          @click="emit('close')"
        >
          &times;
        </button>
      </div>

      <!-- Draft Restored Banner -->
      <div v-if="!isEditing && hasDraft" class="draft-notice-banner">
        <div class="draft-notice-text">
          <svg class="draft-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v4.59L7.3 9.24a.75.75 0 00-1.1 1.02l3.25 3.5a.75.75 0 001.1 0l3.25-3.5a.75.75 0 10-1.1-1.02l-1.95 2.1V6.75z" clip-rule="evenodd" />
          </svg>
          <span><strong>Draft Restored:</strong> Your previously entered student details have been saved and restored.</span>
        </div>
        <button type="button" class="btn-discard-draft" @click="discardDraft">
          Reset / Discard
        </button>
      </div>

      <!-- Desktop Stepper (>=768px) -->
      <div class="modal-stepper-desktop hide-mobile">
        <button
          v-for="idx in totalSteps"
          :key="idx"
          type="button"
          class="step-tab-btn"
          :class="{
            active: currentStep === idx,
            completed: currentStep > idx,
            error: (idx === 1 && (formErrors.first_name || formErrors.last_name)) || (idx === 2 && formErrors.admission_number) || (idx === 4 && (formErrors.portal_username || formErrors.portal_password)),
          }"
          @click="validateStep(currentStep) && (currentStep = idx)"
        >
          <span class="step-badge">{{ currentStep > idx ? '✓' : idx }}</span>
          <span class="step-text">{{ stepTitles[idx - 1] }}</span>
        </button>
      </div>

      <!-- Mobile Stepper (<768px) -->
      <div class="modal-stepper-mobile hide-desktop">
        <div class="mobile-step-header">
          <span class="step-counter">STEP {{ currentStep }} OF {{ totalSteps }}</span>
          <span class="step-current-name">{{ stepTitles[currentStep - 1] }}</span>
        </div>
        <div class="step-progress-track">
          <div
            class="step-progress-bar"
            :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
          />
        </div>
      </div>

      <!-- Scrollable Modal Body -->
      <div class="modal-body">
        <!-- STEP 1: Personal Details -->
        <div v-if="currentStep === 1" class="tab-pane">
          <div class="form-grid">
            <!-- Full Name (Unified Helper) -->
            <div class="form-group col-span-2">
              <label class="form-label required">Student Full Name</label>
              <input
                v-model="form.full_name"
                type="text"
                placeholder="e.g. Mohamed Ali Mire"
                class="form-control"
                @input="syncNamesFromFullName(($event.target as HTMLInputElement).value)"
              />
              <span v-if="formErrors.first_name || formErrors.full_name" class="form-error">
                {{ formErrors.first_name || formErrors.full_name }}
              </span>
            </div>

            <div class="form-group">
              <label class="form-label required">First Name</label>
              <input
                v-model="form.first_name"
                type="text"
                placeholder="e.g. Mohamed"
                class="form-control"
                @input="syncFullNameFromParts"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Middle Name</label>
              <input
                v-model="form.middle_name"
                type="text"
                placeholder="e.g. Ali"
                class="form-control"
                @input="syncFullNameFromParts"
              />
            </div>

            <div class="form-group">
              <label class="form-label required">Last / Family Name</label>
              <input
                v-model="form.last_name"
                type="text"
                placeholder="e.g. Mire"
                class="form-control"
                @input="syncFullNameFromParts"
              />
              <span v-if="formErrors.last_name" class="form-error">{{ formErrors.last_name }}</span>
            </div>

            <div class="form-group">
              <label class="form-label required">Gender</label>
              <select v-model="form.gender" class="form-control">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Date of Birth</label>
              <input v-model="form.date_of_birth" type="date" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label">Student Phone</label>
              <input v-model="form.phone" type="tel" placeholder="+252 61 0000000" class="form-control" />
            </div>

            <div class="form-group col-span-2">
              <label class="form-label">Residential Address</label>
              <input v-model="form.address" type="text" placeholder="e.g. Hawlwadaag District, Mogadishu" class="form-control" />
            </div>
          </div>
        </div>

        <!-- STEP 2: Admission & Class -->
        <div v-if="currentStep === 2" class="tab-pane">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label required">Admission Number</label>
              <input
                v-model="form.admission_number"
                type="text"
                placeholder="ADM-XXXXXX"
                class="form-control uppercase"
              />
              <span v-if="formErrors.admission_number" class="form-error">{{ formErrors.admission_number }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Admission Date</label>
              <input v-model="form.admission_date" type="date" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label required">Enrolled Class</label>
              <select v-model="form.initial_class_id" class="form-control">
                <option :value="0">Select Class...</option>
                <option v-for="c in displayClasses" :key="c.id" :value="c.id">
                  {{ c.name }} ({{ c.code }}) — {{ c.academic_year }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label required">Academic Year</label>
              <select v-model="form.academic_year" class="form-control">
                <option value="2026/2027">2026/2027 (Active)</option>
                <option value="2026-2027">2026-2027</option>
                <option value="2025/2026">2025/2026</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2027/2028">2027/2028</option>
              </select>
            </div>

            <div class="form-group col-span-2">
              <label class="form-label required">Student Status</label>
              <select v-model="form.status" class="form-control">
                <option value="ACTIVE">Active (Enrolled)</option>
                <option value="INACTIVE">Inactive</option>
                <option value="SUSPENDED">Suspended</option>
                <option value="GRADUATED">Graduated</option>
              </select>
            </div>
          </div>
        </div>

        <!-- STEP 3: Guardian Contact -->
        <div v-if="currentStep === 3" class="tab-pane">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Guardian / Parent Name</label>
              <input v-model="form.guardian_name" type="text" placeholder="e.g. Farah Jama" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label">Relationship</label>
              <select v-model="form.guardian_relationship" class="form-control">
                <option value="Father">Father</option>
                <option value="Mother">Mother</option>
                <option value="Uncle">Uncle</option>
                <option value="Aunt">Aunt</option>
                <option value="Guardian">Guardian</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Guardian Phone</label>
              <input v-model="form.guardian_phone" type="tel" placeholder="+252 61 0000000" class="form-control" />
            </div>

            <div class="form-group">
              <label class="form-label">Guardian Email</label>
              <input v-model="form.guardian_email" type="email" placeholder="guardian@email.com" class="form-control" />
            </div>
          </div>
        </div>

        <!-- STEP 4: Portal Account (Create mode only) -->
        <div v-if="currentStep === 4 && !isEditing" class="tab-pane">
          <div class="portal-toggle-box">
            <label class="switch-label">
              <input v-model="form.create_portal_account" type="checkbox" />
              <span class="switch-text">Create Student Portal Login Account</span>
            </label>
            <p class="portal-desc">
              Allows student to sign in at <code>/login</code> with role <strong>STUDENT</strong> to view timetable, exam results, and fee invoices.
            </p>
          </div>

          <div v-if="form.create_portal_account" class="form-grid mt-4">
            <div class="form-group">
              <label class="form-label required">Portal Username</label>
              <input v-model="form.portal_username" type="text" placeholder="username" class="form-control" />
              <span v-if="formErrors.portal_username" class="form-error">{{ formErrors.portal_username }}</span>
            </div>

            <div class="form-group">
              <label class="form-label required">Initial Password</label>
              <input v-model="form.portal_password" type="text" class="form-control font-mono" />
              <span v-if="formErrors.portal_password" class="form-error">{{ formErrors.portal_password }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fixed Modal Footer -->
      <div class="modal-footer">
        <div class="footer-left">
          <button
            v-if="currentStep > 1"
            type="button"
            class="btn-footer-back"
            @click="prevStep"
          >
            &larr; Back
          </button>
          <button
            type="button"
            class="btn-footer-cancel"
            @click="emit('close')"
          >
            Cancel
          </button>
        </div>

        <div class="footer-right">
          <button
            v-if="currentStep < totalSteps"
            type="button"
            class="btn-footer-next"
            @click="nextStep"
          >
            <span>Next Step</span>
            <span>&rarr;</span>
          </button>

          <button
            v-else
            type="button"
            class="btn-footer-save"
            :disabled="isSubmitting"
            @click="handleSave"
          >
            <span v-if="isSubmitting">Saving...</span>
            <span v-else>{{ isEditing ? 'Save Changes' : 'Save & Register Student' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-card {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: min(820px, calc(100vw - 24px));
  max-height: calc(100vh - 32px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  box-sizing: border-box;
}

/* Header */
.modal-header {
  padding: 1.125rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
}

.header-text-wrap {
  flex: 1;
  min-width: 0;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.25;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0;
  line-height: 1.4;
}

.modal-close {
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 1.625rem;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.modal-close:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

/* Stepper Desktop */
.modal-stepper-desktop {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.step-tab-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 0.5rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 44px;
}

.step-tab-btn:hover {
  background: #f1f5f9;
}

.step-tab-btn.active {
  background: #ffffff;
  border-bottom-color: #2563eb;
}

.step-badge {
  width: 22px;
  height: 22px;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.6875rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-tab-btn.active .step-badge {
  background: #2563eb;
  color: #ffffff;
}

.step-tab-btn.completed .step-badge {
  background: #10b981;
  color: #ffffff;
}

.step-text {
  font-size: 0.78125rem;
  font-weight: 600;
  color: #64748b;
  white-space: nowrap;
}

.step-tab-btn.active .step-text {
  color: #1e3a8a;
  font-weight: 700;
}

/* Stepper Mobile */
.modal-stepper-mobile {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.mobile-step-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.step-counter {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.05em;
}

.step-current-name {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0f172a;
}

.step-progress-track {
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.step-progress-bar {
  height: 100%;
  background: #2563eb;
  transition: width 0.25s ease;
}

/* Body */
.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  flex: 1 1 auto;
  box-sizing: border-box;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.col-span-2 {
  grid-column: span 2;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
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
  padding: 0 0.875rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.84375rem;
  color: #0f172a;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  box-sizing: border-box;
}

.form-control:focus {
  background: #ffffff;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.form-control.uppercase {
  text-transform: uppercase;
}

.form-error {
  font-size: 0.75rem;
  color: #e11d48;
  font-weight: 500;
}

.portal-toggle-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  box-sizing: border-box;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  cursor: pointer;
}

.switch-label input {
  width: 18px;
  height: 18px;
  accent-color: #2563eb;
  cursor: pointer;
}

.switch-text {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}

.portal-desc {
  font-size: 0.78125rem;
  color: #64748b;
  margin: 0.35rem 0 0 1.75rem;
  line-height: 1.4;
}

.mt-4 { margin-top: 1rem; }

/* Footer */
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #f8fafc;
  flex-shrink: 0;
  box-sizing: border-box;
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-footer-back,
.btn-footer-cancel,
.btn-footer-next,
.btn-footer-save {
  height: 40px;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  box-sizing: border-box;
  white-space: nowrap;
}

.btn-footer-back,
.btn-footer-cancel {
  padding: 0 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.btn-footer-back:hover,
.btn-footer-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-footer-next {
  padding: 0 1.25rem;
  background: #2563eb;
  border: none;
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
}

.btn-footer-next:hover {
  background: #1d4ed8;
}

.btn-footer-save {
  padding: 0 1.25rem;
  background: #16a34a;
  border: none;
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(22, 163, 74, 0.2);
}

.btn-footer-save:hover:not(:disabled) {
  background: #15803d;
}

.btn-footer-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Responsive queries */
@media (min-width: 768px) {
  .hide-desktop { display: none !important; }
}

@media (max-width: 767px) {
  .hide-mobile { display: none !important; }

  .modal-card {
    max-width: calc(100vw - 24px);
    max-height: calc(100vh - 24px);
  }

  .modal-header {
    padding: 0.875rem 1rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .col-span-2 {
    grid-column: span 1;
  }

  .modal-footer {
    padding: 0.75rem 1rem;
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .footer-left,
  .footer-right {
    width: 100%;
  }

  .footer-left {
    display: flex;
    justify-content: space-between;
  }

  .btn-footer-back,
  .btn-footer-cancel {
    flex: 1 1 0%;
  }

  .btn-footer-next,
  .btn-footer-save {
    width: 100%;
  }
}
</style>
