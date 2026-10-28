<script setup lang="ts">
import { reactive, watch, computed } from 'vue';
import { SchoolClass } from '../../../../types/school';
import { useFormDraft } from '../../../../composables/useFormDraft';

const props = defineProps<{
  isOpen: boolean;
  isEditing: boolean;
  schoolClass: SchoolClass | null;
  isSubmitting: boolean;
  years: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: Partial<SchoolClass>): void;
}>();

const primaryLevels = [
  'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4',
  'Grade 5', 'Grade 6', 'Grade 7', 'Grade 8'
];

const secondaryLevels = [
  'Form 1', 'Form 2', 'Form 3', 'Form 4'
];

const standardSections = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

const form = reactive({
  division: 'PRIMARY' as 'PRIMARY' | 'SECONDARY',
  level: 'Grade 1',
  section: 'A',
  customSection: '',
  academic_year: '2026/2027',
  capacity: 40,
  description: '',
  status: 'ACTIVE',
});

const formErrors = reactive<Record<string, string>>({});

function resetCreateForm() {
  form.division = 'PRIMARY';
  form.level = 'Grade 7';
  form.section = 'A';
  form.customSection = '';
  form.academic_year = props.years[0] || '2026/2027';
  form.capacity = 40;
  form.description = '';
  form.status = 'ACTIVE';
}

const {
  hasDraft,
  restoreDraft,
  clearDraft,
} = useFormDraft({
  storageKey: 'sms_draft_class_create',
  form,
  enabled: () => !props.isEditing,
  isDirty: (f) => !!(f.customSection?.trim() || f.description?.trim() || (f.level && f.level !== 'Grade 7') || (f.section && f.section !== 'A')),
});

function discardDraft() {
  clearDraft();
  resetCreateForm();
}

// Dynamic available levels based on division
const availableLevels = computed(() => {
  return form.division === 'PRIMARY' ? primaryLevels : secondaryLevels;
});

// Effective section
const effectiveSection = computed(() => {
  if (form.section === 'CUSTOM') {
    return form.customSection.trim().toUpperCase();
  }
  return form.section.trim().toUpperCase();
});

// Live Class Name Preview
const classNamePreview = computed(() => {
  const lvl = form.level || '';
  const sec = effectiveSection.value;
  if (!lvl) return '—';
  return sec ? `${lvl} - ${sec}` : lvl;
});

// Auto-generated Code Preview
const classCodePreview = computed(() => {
  const lvl = form.level || '';
  const prefix = lvl.replace('Grade ', 'G').replace('Form ', 'F').replace(/\s+/g, '');
  const sec = effectiveSection.value || 'GEN';
  const yr = (form.academic_year || '2026').split('/')[0].split('-')[0];
  return `${prefix}-${sec}-${yr}`;
});

watch(
  () => form.division,
  (newDiv) => {
    if (newDiv === 'PRIMARY') {
      if (!primaryLevels.includes(form.level)) {
        form.level = primaryLevels[0];
      }
    } else {
      if (!secondaryLevels.includes(form.level)) {
        form.level = secondaryLevels[0];
      }
    }
  }
);

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      if (props.isEditing && props.schoolClass) {
        const c = props.schoolClass;
        form.division = (c.division?.toUpperCase() === 'SECONDARY' ? 'SECONDARY' : 'PRIMARY');
        form.level = c.level || c.name || (form.division === 'PRIMARY' ? 'Grade 1' : 'Form 1');
        
        const sec = (c.section || '').trim().toUpperCase();
        if (standardSections.includes(sec) || sec === '') {
          form.section = sec || '';
          form.customSection = '';
        } else {
          form.section = 'CUSTOM';
          form.customSection = sec;
        }

        form.academic_year = c.academic_year || '2026/2027';
        form.capacity = c.capacity || 40;
        form.description = c.description || '';
        form.status = c.status || 'ACTIVE';
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

function validateForm(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let isValid = true;

  if (!form.division) {
    formErrors.division = 'Academic division is required.';
    isValid = false;
  }
  if (!form.level) {
    formErrors.level = 'Academic level is required.';
    isValid = false;
  }
  if (form.section === 'CUSTOM' && !form.customSection.trim()) {
    formErrors.section = 'Please enter a custom section name (e.g. E, F, North).';
    isValid = false;
  }
  if (!form.academic_year.trim()) {
    formErrors.academic_year = 'Academic year is required.';
    isValid = false;
  }
  if (!form.capacity || form.capacity < 1) {
    formErrors.capacity = 'Capacity must be at least 1.';
    isValid = false;
  } else if (form.capacity > 200) {
    formErrors.capacity = 'Capacity cannot exceed 200.';
    isValid = false;
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) return;

  const sec = effectiveSection.value || null;
  const canonicalName = classNamePreview.value;
  const code = classCodePreview.value;

  emit('save', {
    name: canonicalName,
    code: code,
    division: form.division,
    level: form.level,
    section: sec,
    academic_year: form.academic_year.trim(),
    capacity: Number(form.capacity),
    description: form.description.trim() || null,
    status: form.status,
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel">
      <!-- Header -->
      <div class="modal-header">
        <div class="modal-title-group">
          <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h10" />
            </svg>
          </div>
          <div>
            <h3 class="modal-title">{{ isEditing ? 'Edit Class' : 'Create Academic Class' }}</h3>
            <p class="modal-subtitle">Configure Division, Level, Section, and Academic Year.</p>
          </div>
        </div>
        <button type="button" class="modal-close-btn" @click="emit('close')">
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
          <span><strong>Draft Restored:</strong> Your previously entered class details have been saved and restored.</span>
        </div>
        <button type="button" class="btn-discard-draft" @click="discardDraft">
          Reset / Discard
        </button>
      </div>

      <!-- Form Body -->
      <form class="modal-body" @submit.prevent="handleSubmit">
        <!-- Live Class Name & Code Preview Card -->
        <div class="preview-banner">
          <div class="preview-meta">
            <span class="preview-tag" :class="form.division === 'PRIMARY' ? 'tag-primary' : 'tag-secondary'">
              {{ form.division }}
            </span>
            <span class="preview-year">{{ form.academic_year }}</span>
          </div>
          <div class="preview-name-group">
            <span class="preview-label">Generated Class Identity:</span>
            <span class="preview-name">{{ classNamePreview }}</span>
          </div>
          <div class="preview-code-badge">
            Code: <strong>{{ classCodePreview }}</strong>
          </div>
        </div>

        <!-- Section 1: Academic Division & Level -->
        <div class="form-section">
          <h4 class="section-title">Academic Division & Level</h4>
          <div class="form-grid">
            <!-- Academic Division Switcher -->
            <div class="form-group col-span-2">
              <label class="form-label required">Academic Division</label>
              <div class="division-selector">
                <button
                  type="button"
                  class="division-btn"
                  :class="{ active: form.division === 'PRIMARY' }"
                  @click="form.division = 'PRIMARY'"
                >
                  <span class="div-icon">🏫</span>
                  <div class="div-text">
                    <span class="div-name">Primary Division</span>
                    <span class="div-sub">Grades 1 through 8</span>
                  </div>
                </button>
                <button
                  type="button"
                  class="division-btn"
                  :class="{ active: form.division === 'SECONDARY' }"
                  @click="form.division = 'SECONDARY'"
                >
                  <span class="div-icon">🎓</span>
                  <div class="div-text">
                    <span class="div-name">Secondary Division</span>
                    <span class="div-sub">Forms 1 through 4</span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Grade / Form Selection -->
            <div class="form-group">
              <label class="form-label required">
                {{ form.division === 'PRIMARY' ? 'Primary Grade Level' : 'Secondary Form Level' }}
              </label>
              <select
                v-model="form.level"
                class="form-select"
                :class="{ 'has-error': formErrors.level }"
              >
                <option v-for="lvl in availableLevels" :key="lvl" :value="lvl">
                  {{ lvl }}
                </option>
              </select>
              <span v-if="formErrors.level" class="error-text">{{ formErrors.level }}</span>
            </div>

            <!-- Section Selection (A, B, C, D, E, F... or Custom) -->
            <div class="form-group">
              <label class="form-label">Section / Stream</label>
              <select v-model="form.section" class="form-select">
                <option value="">No Section (General Level)</option>
                <option v-for="s in standardSections" :key="s" :value="s">
                  Section {{ s }}
                </option>
                <option value="CUSTOM">+ Custom Section (e.g. E, F, Stream...)</option>
              </select>
            </div>

            <!-- Custom Section Input if CUSTOM chosen -->
            <div v-if="form.section === 'CUSTOM'" class="form-group col-span-2">
              <label class="form-label required">Custom Section Identifier</label>
              <input
                v-model="form.customSection"
                type="text"
                class="form-input"
                :class="{ 'has-error': formErrors.section }"
                placeholder="Enter section name/letter (e.g. E, Stream North, Gold)"
              />
              <span v-if="formErrors.section" class="error-text">{{ formErrors.section }}</span>
            </div>
          </div>
        </div>

        <!-- Section 2: Academic Year & Capacity -->
        <div class="form-section">
          <h4 class="section-title">Academic Year & Capacity Settings</h4>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label required">Academic Year</label>
              <select
                v-model="form.academic_year"
                class="form-select"
                :class="{ 'has-error': formErrors.academic_year }"
              >
                <option v-for="yr in years" :key="yr" :value="yr">
                  {{ yr }}
                </option>
              </select>
              <span v-if="formErrors.academic_year" class="error-text">{{ formErrors.academic_year }}</span>
            </div>

            <div class="form-group">
              <label class="form-label required">Max Capacity</label>
              <input
                v-model.number="form.capacity"
                type="number"
                min="1"
                max="200"
                class="form-input"
                :class="{ 'has-error': formErrors.capacity }"
              />
              <span v-if="formErrors.capacity" class="error-text">{{ formErrors.capacity }}</span>
            </div>

            <div class="form-group col-span-2">
              <label class="form-label required">Status</label>
              <select v-model="form.status" class="form-select">
                <option value="ACTIVE">Active (Enrollments & Scheduling Open)</option>
                <option value="INACTIVE">Inactive (Temporarily Suspended)</option>
                <option value="ARCHIVED">Archived (Historical Record)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section 3: Notes -->
        <div class="form-section">
          <h4 class="section-title">Additional Notes (Optional)</h4>
          <div class="form-group">
            <textarea
              v-model="form.description"
              class="form-textarea"
              rows="2"
              placeholder="Add optional notes regarding room location, class teacher or curriculum focus..."
            ></textarea>
          </div>
        </div>
      </form>

      <!-- Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-cancel" :disabled="isSubmitting" @click="emit('close')">
          Cancel
        </button>
        <button type="button" class="btn-submit" :disabled="isSubmitting" @click="handleSubmit">
          <svg v-if="isSubmitting" class="spinner" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="3" />
          </svg>
          <span>{{ isEditing ? 'Save Changes' : 'Create Class' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-banner {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
  border: 1px solid #bfdbfe;
  border-radius: 0.625rem;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-tag {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.5rem;
  border-radius: 0.375rem;
}

.tag-primary {
  background-color: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}

.tag-secondary {
  background-color: #ede9fe;
  color: #6d28d9;
  border: 1px solid #ddd6fe;
}

.preview-year {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.preview-name-group {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.preview-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.preview-name {
  font-size: 1.125rem;
  font-weight: 800;
  color: #0f172a;
}

.preview-code-badge {
  font-size: 0.75rem;
  color: #475569;
}

.preview-code-badge strong {
  font-family: monospace;
  color: #1e293b;
  background-color: #e2e8f0;
  padding: 0.1rem 0.35rem;
  border-radius: 0.25rem;
}

.division-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.625rem;
}

.division-btn {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  background-color: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 0.5rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.division-btn:hover {
  border-color: #cbd5e1;
  background-color: #f1f5f9;
}

.division-btn.active {
  border-color: #2563eb;
  background-color: #eff6ff;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.div-icon {
  font-size: 1.25rem;
}

.div-text {
  display: flex;
  flex-direction: column;
}

.div-name {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0f172a;
}

.div-sub {
  font-size: 0.6875rem;
  color: #64748b;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
  animation: fadeIn 0.15s ease-out;
}

.modal-panel {
  width: 100%;
  max-width: min(36rem, calc(100vw - 20px));
  background-color: #ffffff;
  border-radius: 0.875rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 24px);
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
  animation: scaleUp 0.18s ease-out;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  background-color: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.modal-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background-color: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-icon svg {
  width: 1.25rem;
  height: 1.25rem;
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
  margin: 0.15rem 0 0 0;
  line-height: 1.35;
}

.modal-close-btn {
  background: transparent;
  border: none;
  min-width: 44px;
  min-height: 44px;
  color: #64748b;
  cursor: pointer;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.12s ease;
}

.modal-close-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.modal-close-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
  margin: 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.875rem;
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
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  height: 40px;
  padding: 0 0.75rem;
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.form-textarea {
  height: auto;
  padding: 0.5rem 0.75rem;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  background-color: #ffffff;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.form-input.has-error,
.form-select.has-error {
  border-color: #ef4444;
  background-color: #fffbfb;
}

.error-text {
  font-size: 0.75rem;
  color: #ef4444;
  font-weight: 500;
}

.modal-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background-color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
}

.btn-cancel {
  height: 40px;
  padding: 0 1.25rem;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  height: 40px;
  padding: 0 1.25rem;
  background-color: #2563eb;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.btn-submit:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-submit:disabled,
.btn-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 0.875rem;
  height: 0.875rem;
  animation: spin 1s linear infinite;
}

.spinner circle {
  stroke-dasharray: 40;
  stroke-dashoffset: 10;
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
  from {
    opacity: 0;
    transform: scale(0.97);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
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

@media (max-width: 640px) {
  .modal-overlay {
    padding: 8px;
  }

  .modal-panel {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .col-span-2 {
    grid-column: span 1;
  }

  .division-selector {
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
    justify-content: center;
  }
}
</style>
