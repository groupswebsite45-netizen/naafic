<script setup lang="ts">
import { reactive, watch } from 'vue';
import { Subject } from '../../../../types/school';
import { useFormDraft } from '../../../../composables/useFormDraft';

const props = defineProps<{
  isOpen: boolean;
  isEditing: boolean;
  subject: Subject | null;
  isSubmitting: boolean;
  departments: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: Partial<Subject>): void;
}>();

const form = reactive({
  name: '',
  code: '',
  department: '',
  description: '',
  status: 'ACTIVE',
});

const formErrors = reactive<Record<string, string>>({});

function resetCreateForm() {
  form.name = '';
  form.code = '';
  form.department = props.departments[0] || '';
  form.description = '';
  form.status = 'ACTIVE';
}

const {
  hasDraft,
  restoreDraft,
  clearDraft,
} = useFormDraft({
  storageKey: 'sms_draft_subject_create',
  form,
  enabled: () => !props.isEditing,
  isDirty: (f) => !!(f.name?.trim() || f.code?.trim() || f.description?.trim()),
});

function discardDraft() {
  clearDraft();
  resetCreateForm();
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      if (props.isEditing && props.subject) {
        form.name = props.subject.name || '';
        form.code = props.subject.code || '';
        form.department = props.subject.department || '';
        form.description = props.subject.description || '';
        form.status = props.subject.status || 'ACTIVE';
      } else {
        const restored = restoreDraft();
        if (!restored) {
          resetCreateForm();
        }
      }
    }
  },
  { immediate: true }
);

function autoGenerateCode() {
  if (!props.isEditing && form.name) {
    const cleanName = form.name.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
    if (!form.code || form.code.length <= 4) {
      form.code = `${cleanName.slice(0, 3)}-101`;
    }
  }
}

function validateForm(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let isValid = true;

  if (!form.name.trim()) {
    formErrors.name = 'Subject name is required (e.g. Mathematics, Biology).';
    isValid = false;
  }
  if (!form.code.trim()) {
    formErrors.code = 'Subject code is required (e.g. MAT-101, ENG-201).';
    isValid = false;
  } else if (!/^[A-Z0-9\-_]{2,20}$/i.test(form.code.trim())) {
    formErrors.code = 'Code must be 2-20 characters using letters, numbers, or dashes.';
    isValid = false;
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) return;

  emit('save', {
    name: form.name.trim(),
    code: form.code.toUpperCase().trim(),
    department: form.department.trim() || null,
    description: form.description.trim() || null,
    status: form.status,
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
            <path d="M6 6h10" />
            <path d="M6 10h10" />
          </svg>
        </div>
        <div class="header-titles">
          <h2 id="modal-title" class="modal-title">
            {{ isEditing ? 'Edit Subject' : 'Add New Subject' }}
          </h2>
          <p class="modal-subtitle">
            {{ isEditing ? 'Update curriculum subject metadata and details.' : 'Register a new subject to the school curriculum.' }}
          </p>
        </div>
        <button
          type="button"
          class="close-btn"
          title="Close modal"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Draft Restored Banner -->
      <div v-if="!isEditing && hasDraft" class="draft-notice-banner">
        <div class="draft-notice-text">
          <svg class="draft-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v4.59L7.3 9.24a.75.75 0 00-1.1 1.02l3.25 3.5a.75.75 0 001.1 0l3.25-3.5a.75.75 0 10-1.1-1.02l-1.95 2.1V6.75z" clip-rule="evenodd" />
          </svg>
          <span><strong>Draft Restored:</strong> Your previously entered subject details have been saved and restored.</span>
        </div>
        <button type="button" class="btn-discard-draft" @click="discardDraft">
          Reset / Discard
        </button>
      </div>

      <!-- Modal Body Form -->
      <form class="modal-form" @submit.prevent="handleSubmit">
        <div class="form-sections">
          <!-- SECTION 1: Subject Identity -->
          <div class="form-section">
            <h4 class="section-title">Subject Identity</h4>

            <div class="form-grid">
              <!-- Subject Name -->
              <div class="form-group full-width">
                <label class="form-label" for="subject-name">
                  Subject Name <span class="required">*</span>
                </label>
                <input
                  id="subject-name"
                  v-model="form.name"
                  type="text"
                  class="form-input"
                  :class="{ 'has-error': formErrors.name }"
                  placeholder="e.g. Mathematics, English Language, Physics"
                  @blur="autoGenerateCode"
                />
                <span v-if="formErrors.name" class="error-msg">{{ formErrors.name }}</span>
              </div>

              <!-- Subject Code -->
              <div class="form-group">
                <label class="form-label" for="subject-code">
                  Subject Code <span class="required">*</span>
                </label>
                <input
                  id="subject-code"
                  v-model="form.code"
                  type="text"
                  class="form-input code-input"
                  :class="{ 'has-error': formErrors.code }"
                  placeholder="e.g. MAT-101"
                />
                <span v-if="formErrors.code" class="error-msg">{{ formErrors.code }}</span>
                <span v-else class="help-text">Unique code identifier</span>
              </div>

              <!-- Department -->
              <div class="form-group">
                <label class="form-label" for="subject-dept">
                  Department
                </label>
                <input
                  id="subject-dept"
                  v-model="form.department"
                  type="text"
                  list="departments-list"
                  class="form-input"
                  placeholder="e.g. Sciences, Languages, Humanities"
                />
                <datalist id="departments-list">
                  <option v-for="dept in departments" :key="dept" :value="dept" />
                </datalist>
                <span class="help-text">Select or type a department</span>
              </div>

              <!-- Status -->
              <div class="form-group">
                <label class="form-label" for="subject-status">
                  Status
                </label>
                <select
                  id="subject-status"
                  v-model="form.status"
                  class="form-select"
                >
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                  <option value="ARCHIVED">Archived</option>
                </select>
              </div>

              <!-- Description / Notes -->
              <div class="form-group full-width">
                <label class="form-label" for="subject-desc">
                  Curriculum Description & Learning Objectives
                </label>
                <textarea
                  id="subject-desc"
                  v-model="form.description"
                  class="form-textarea"
                  rows="3"
                  placeholder="Provide an overview of the curriculum, key learning outcomes, syllabus topics..."
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button
            type="button"
            class="btn-cancel"
            :disabled="isSubmitting"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="isSubmitting"
          >
            <svg
              v-if="isSubmitting"
              class="spinner"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
              <path d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            <span>{{ isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Subject' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
  animation: fadeIn 0.15s ease-out;
}

.modal-panel {
  background: #ffffff;
  border-radius: var(--radius-lg, 0.75rem);
  width: 100%;
  max-width: min(540px, calc(100vw - 1.5rem));
  max-height: calc(100dvh - 1.5rem);
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  animation: scaleUp 0.15s ease-out;
  overflow: hidden;
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.header-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md, 0.5rem);
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  flex-shrink: 0;
}

.header-icon-wrap svg {
  width: 1.125rem;
  height: 1.125rem;
}

.header-titles {
  flex: 1;
  min-width: 0;
}

.modal-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
  margin: 0.125rem 0 0 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: var(--radius-md, 0.5rem);
  background: none;
  border: none;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: #f1f5f9;
  color: var(--text-main, #0f172a);
}

.close-btn svg {
  width: 1rem;
  height: 1rem;
}

.modal-form {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-y: auto;
}

.form-sections {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--brand-primary, #1e40af);
  margin: 0 0 0.75rem 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.875rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-main, #1e293b);
}

.required {
  color: var(--danger, #ef4444);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: var(--text-main, #0f172a);
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.code-input {
  text-transform: uppercase;
  font-family: monospace;
  font-weight: 600;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.form-input.has-error,
.form-select.has-error {
  border-color: var(--danger, #ef4444);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.875rem;
  padding-right: 2rem;
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
  min-height: 70px;
}

.help-text {
  font-size: 0.6875rem;
  color: var(--text-muted, #64748b);
}

.error-msg {
  font-size: 0.6875rem;
  color: var(--danger, #ef4444);
  font-weight: 500;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  background: #f8fafc;
}

.btn-cancel {
  height: 2.375rem;
  padding: 0 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.375rem;
  padding: 0 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
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

.btn-submit:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
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
  from { transform: scale(0.96); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
