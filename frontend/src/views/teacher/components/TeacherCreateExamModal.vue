<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { teacherPortalService } from '../../../services/teacherPortalService';
import { useFormDraft } from '../../../composables/useFormDraft';

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'created', exam: any): void;
}>();

// Options from /exam-options endpoint — backend enforces: only classes with active students
const examOptions = ref<{
  academic_years: string[];
  subjects: Array<{ id: number; name: string; code: string; division: string }>;
  classes: Array<{ id: number; name: string; code: string; division: string; level: string; section: string; academic_year: string; student_count: number }>;
  teacher_id: number;
  teacher_name: string;
} | null>(null);
const isLoadingAssignments = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref('');
const refreshSuccess = ref(false);

const form = reactive({
  academic_year: '',
  class_id: null as number | null,
  subject_id: null as number | null,
  exam_type: 'QUIZ',
  name: '',
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
  max_marks: 100,
  pass_marks: 50,
  instructions: '',
});

function resetCreateForm() {
  form.academic_year = '';
  form.class_id = null;
  form.subject_id = null;
  form.exam_type = 'QUIZ';
  form.name = '';
  form.start_date = new Date().toISOString().split('T')[0];
  form.end_date = '';
  form.max_marks = 100;
  form.pass_marks = 50;
  form.instructions = '';
}

const {
  hasDraft,
  restoreDraft,
  clearDraft,
} = useFormDraft({
  storageKey: 'sms_draft_teacher_quiz_create',
  form,
  enabled: () => true,
  isDirty: (f) => !!(f.name?.trim() || f.instructions?.trim() || f.class_id || f.subject_id),
});

function discardDraft() {
  clearDraft();
  resetCreateForm();
  loadAssignments(true);
}

async function loadAssignments(isUserRefresh = false) {
  isLoadingAssignments.value = true;
  errorMessage.value = '';
  refreshSuccess.value = false;
  try {
    // 1. Fetch available options scoped to authenticated teacher
    const opts = await teacherPortalService.getExamOptions({
      academic_year: form.academic_year || undefined
    });
    examOptions.value = opts;

    // 2. Select teacher's active academic year
    if (opts.academic_years && opts.academic_years.length > 0) {
      if (!form.academic_year || !opts.academic_years.includes(form.academic_year)) {
        form.academic_year = (opts as any).selected_academic_year || opts.academic_years[0];
      }
    } else {
      form.academic_year = '';
    }

    // 3. Load cascading assigned subjects
    if (opts.subjects && opts.subjects.length > 0) {
      if (!form.subject_id || !opts.subjects.some((s) => s.id === form.subject_id)) {
        form.subject_id = opts.subjects[0].id;
      }
      // 4. Load cascading classes for this subject and year
      const classOpts = await teacherPortalService.getExamOptions({
        academic_year: form.academic_year,
        subject_id: form.subject_id
      });
      if (examOptions.value) {
        examOptions.value.classes = classOpts.classes;
      }
      if (classOpts.classes && classOpts.classes.length > 0) {
        if (!form.class_id || !classOpts.classes.some((c) => c.id === form.class_id)) {
          form.class_id = classOpts.classes[0].id;
        }
      } else {
        form.class_id = null;
      }
    } else {
      form.subject_id = null;
      form.class_id = null;
    }

    generateTitle();

    if (isUserRefresh) {
      refreshSuccess.value = true;
      setTimeout(() => { refreshSuccess.value = false; }, 3500);
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load your assigned classes and subjects.';
  } finally {
    isLoadingAssignments.value = false;
  }
}

const availableYears = computed(() => {
  return examOptions.value?.academic_years || [];
});

// Use examOptions for actual dropdown data
const assignedSubjectsForYear = computed(() => {
  return (examOptions.value?.subjects || []).map(s => ({
    subject_id: s.id,
    subject_name: s.name,
    subject_code: s.code,
  }));
});

const assignedClassesForSubject = computed(() => {
  return (examOptions.value?.classes || []).map(c => ({
    class_id: c.id,
    class_name: c.name,
    section: c.section,
    student_count: c.student_count,
  }));
});


// When subject changes, reload classes from backend (cascading dropdown)
watch(
  () => form.subject_id,
  async (newSubId) => {
    if (!newSubId) {
      form.class_id = null;
      generateTitle();
      return;
    }
    try {
      const classOpts = await teacherPortalService.getExamOptions({
        academic_year: form.academic_year,
        subject_id: newSubId
      });
      if (examOptions.value) {
        examOptions.value.classes = classOpts.classes;
      }
      const validClasses = classOpts.classes;
      if (validClasses.length > 0) {
        if (!form.class_id || !validClasses.some((c) => c.id === form.class_id)) {
          form.class_id = validClasses[0].id;
        }
      } else {
        form.class_id = null;
      }
    } catch {
      form.class_id = null;
    }
    generateTitle();
  }
);


// When academic year changes, reload all options from backend
watch(
  () => form.academic_year,
  async (newYear) => {
    try {
      const opts = await teacherPortalService.getExamOptions({ academic_year: newYear });
      examOptions.value = opts;
      if (opts.subjects.length > 0) {
        if (!form.subject_id || !opts.subjects.some((s) => s.id === form.subject_id)) {
          form.subject_id = opts.subjects[0].id;
        }
        const classOpts = await teacherPortalService.getExamOptions({
          academic_year: newYear,
          subject_id: form.subject_id!
        });
        examOptions.value.classes = classOpts.classes;
        form.class_id = classOpts.classes.length > 0 ? classOpts.classes[0].id : null;
      } else {
        form.subject_id = null;
        form.class_id = null;
      }
    } catch { /* keep existing values */ }
  }
);


watch(
  () => [form.exam_type, form.subject_id, form.class_id],
  () => {
    generateTitle();
  }
);

function generateTitle() {
  const subj = assignedSubjectsForYear.value.find((s) => s.subject_id === form.subject_id);
  const cls = assignedClassesForSubject.value.find((c) => c.class_id === form.class_id);
  const subjName = subj ? subj.subject_name : '';
  const clsName = cls ? cls.class_name : '';

  if (subjName && clsName) {
    form.name = `Quiz: ${subjName} (${clsName})`.trim();
  } else if (subjName) {
    form.name = `Quiz: ${subjName}`.trim();
  } else {
    form.name = `Class Quiz`.trim();
  }
}

watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      const restored = restoreDraft();
      loadAssignments(!restored);
    }
  }
);

onMounted(() => {
  if (props.isOpen) {
    const restored = restoreDraft();
    loadAssignments(!restored);
  }
});

async function handleSubmit() {
  if (!form.class_id) {
    errorMessage.value = 'Please select an assigned class.';
    return;
  }
  if (!form.subject_id) {
    errorMessage.value = 'Please select an assigned subject.';
    return;
  }
  if (!form.name.trim()) {
    errorMessage.value = 'Please enter an exam title.';
    return;
  }
  if (form.pass_marks > form.max_marks) {
    errorMessage.value = 'Pass marks cannot exceed maximum marks.';
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const payload = {
      name: form.name.trim(),
      exam_type: form.exam_type,
      academic_year: form.academic_year.trim(),
      class_id: form.class_id,
      subject_id: form.subject_id,
      start_date: form.start_date,
      end_date: form.end_date ? form.end_date : null,
      max_marks: Number(form.max_marks),
      pass_marks: Number(form.pass_marks),
      instructions: form.instructions ? form.instructions.trim() : null,
    };

    const created = await teacherPortalService.createExam(payload);
    clearDraft();
    emit('created', created);
    emit('close');
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to create examination. Please verify assignment details.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </div>
        <div class="header-text">
          <h2 class="modal-title">Create Class Quiz</h2>
          <p class="modal-subtitle">Schedule a quiz for your assigned class and subject</p>
        </div>
        <div class="header-right-actions">
          <button
            type="button"
            class="refresh-assignments-btn"
            :disabled="isLoadingAssignments"
            @click="loadAssignments(true)"
            title="Reload active assignments from Administration"
            id="btn-refresh-assignments"
          >
            <svg class="refresh-icon" :class="{ spinning: isLoadingAssignments }" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Assignments
          </button>
          <button type="button" class="close-btn" @click="emit('close')" aria-label="Close modal">
            &times;
          </button>
        </div>
      </div>

      <!-- Draft Restored Banner -->
      <div v-if="hasDraft" class="draft-notice-banner">
        <div class="draft-notice-text">
          <svg class="draft-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v4.59L7.3 9.24a.75.75 0 00-1.1 1.02l3.25 3.5a.75.75 0 001.1 0l3.25-3.5a.75.75 0 10-1.1-1.02l-1.95 2.1V6.75z" clip-rule="evenodd" />
          </svg>
          <span><strong>Draft Restored:</strong> Your previously entered quiz details have been saved and restored.</span>
        </div>
        <button type="button" class="btn-discard-draft" @click="discardDraft">
          Reset / Discard
        </button>
      </div>

      <!-- Modal Body -->
      <form @submit.prevent="handleSubmit" class="modal-body">
        <!-- Admin Examination Policy Notice -->
        <div class="admin-notice-banner">
          <div class="notice-icon">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="notice-text">
            <strong>Examination Policy:</strong> Official examinations (<em>Final, Midterm, Monthly</em>) are scheduled exclusively by School Administration. Teachers can create quizzes for their assigned classes and subjects.
          </div>
        </div>

        <!-- Success Refresh Banner -->
        <div v-if="refreshSuccess" class="refresh-success-banner" id="banner-refresh-success">
          <svg class="success-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span>Active assignments refreshed successfully!</span>
        </div>

        <!-- Error Banner -->
        <div v-if="errorMessage" class="error-banner">
          <svg class="err-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <div v-if="isLoadingAssignments" class="loading-state">
          <div class="spinner"></div>
          <p>Loading your assigned classes and subjects...</p>
        </div>

        <div v-else class="form-content">
          <!-- Academic Year & Subject Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                Academic Year <span class="required">*</span>
              </label>
              <select v-model="form.academic_year" class="form-select" required id="select-exam-academic-year">
                <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
                <option v-if="availableYears.length === 0" value="2026/2027">2026/2027</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">
                Assigned Subject <span class="required">*</span>
              </label>
              <select v-model="form.subject_id" class="form-select" required id="select-exam-subject">
                <option :value="null" disabled>Select your assigned subject</option>
                <option v-for="s in assignedSubjectsForYear" :key="s.subject_id" :value="s.subject_id">
                  {{ s.subject_name }} {{ s.subject_code ? `(${s.subject_code})` : '' }}
                </option>
              </select>
              <span v-if="assignedSubjectsForYear.length === 0" class="hint-text text-amber">
                No subjects assigned to you for this academic year.
              </span>
            </div>
          </div>

          <!-- Assigned Class & Exam Type Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                Assigned Class <span class="required">*</span>
              </label>
              <select v-model="form.class_id" class="form-select" required :disabled="!form.subject_id" id="select-exam-class">
                <option :value="null" disabled>
                  {{ form.subject_id ? 'Select assigned class' : 'Select a subject first' }}
                </option>
                <option v-for="c in assignedClassesForSubject" :key="c.class_id" :value="c.class_id">
                  {{ c.class_name }} {{ c.section ? `(Sec ${c.section})` : '' }}
                </option>
              </select>
              <span v-if="form.subject_id && assignedClassesForSubject.length === 0" class="hint-text text-amber">
                No classes assigned to you for this subject.
              </span>
            </div>

            <div class="form-group">
              <label class="form-label">
                Exam Type <span class="badge-teacher-only">Teacher Created</span>
              </label>
              <div class="single-quiz-badge">
                <svg class="quiz-check-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span class="quiz-badge-label">Quiz Examination</span>
              </div>
            </div>
          </div>

          <!-- Exam Title -->
          <div class="form-group">
            <label class="form-label">
              Exam Title <span class="required">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              class="form-input title-input"
              placeholder="e.g. Mid-Term Mathematics Examination"
              required
            />
          </div>

          <!-- Date & Marks Row -->
          <div class="form-row-3">
            <div class="form-group">
              <label class="form-label">
                Exam Date <span class="required">*</span>
              </label>
              <input
                v-model="form.start_date"
                type="date"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                Maximum Marks <span class="required">*</span>
              </label>
              <input
                v-model.number="form.max_marks"
                type="number"
                min="1"
                max="1000"
                class="form-input"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                Pass Marks <span class="required">*</span>
              </label>
              <input
                v-model.number="form.pass_marks"
                type="number"
                min="0"
                :max="form.max_marks"
                class="form-input"
                required
              />
            </div>
          </div>

          <!-- Instructions -->
          <div class="form-group">
            <label class="form-label">
              Instructions / Notes <span class="optional">(Optional)</span>
            </label>
            <textarea
              v-model="form.instructions"
              rows="2"
              class="form-textarea"
              placeholder="Add optional exam guidelines or teacher notes..."
            ></textarea>
          </div>

          <!-- Summary Identity Card -->
          <div class="identity-card">
            <div class="identity-badge">EXAM IDENTITY PREVIEW</div>
            <div class="identity-row">
              <span class="id-item"><strong>Year:</strong> {{ form.academic_year }}</span>
              <span class="id-item"><strong>Type:</strong> {{ form.exam_type }}</span>
              <span class="id-item"><strong>Max Marks:</strong> {{ form.max_marks }} (Pass: {{ form.pass_marks }})</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="emit('close')">
            Cancel
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="isSubmitting || isLoadingAssignments || !form.class_id || !form.subject_id"
          >
            <svg v-if="isSubmitting" class="spinner-svg" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <span>{{ isSubmitting ? 'Creating Exam...' : 'Create Exam' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-card {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #e2e8f0;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  position: relative;
}

.header-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.header-icon {
  width: 22px;
  height: 22px;
}

.header-text {
  flex: 1;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.refresh-assignments-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #4338ca;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.refresh-assignments-btn:hover:not(:disabled) {
  background: #e0e7ff;
  border-color: #a5b4fc;
}

.refresh-assignments-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  width: 14px;
  height: 14px;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

.close-btn {
  font-size: 1.5rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  line-height: 1;
}

.close-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.refresh-success-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.success-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.modal-body {
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
}

.err-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  color: #64748b;
  gap: 0.75rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.875rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.required {
  color: #ef4444;
}

.optional {
  color: #94a3b8;
  font-weight: 400;
}

.form-select,
.form-input,
.form-textarea {
  padding: 0.55rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.admin-notice-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  line-height: 1.45;
}

.notice-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 1px;
}

.notice-text em {
  font-style: normal;
  font-weight: 600;
  color: #1d4ed8;
}

.badge-teacher-only {
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.15rem 0.45rem;
  background: #f1f5f9;
  color: #475569;
  border-radius: 4px;
  margin-left: 0.35rem;
}

.single-quiz-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.85rem;
  background: #eef2ff;
  border: 1.5px solid #6366f1;
  color: #4338ca;
  font-size: 0.875rem;
  font-weight: 700;
  border-radius: 8px;
  width: fit-content;
}

.quiz-check-icon {
  width: 16px;
  height: 16px;
  color: #4f46e5;
}

.custom-type-input {
  margin-top: 0.35rem;
}

.title-input {
  font-weight: 600;
}

.hint-text {
  font-size: 0.75rem;
  margin-top: 0.2rem;
}

.text-amber {
  color: #d97706;
}

.identity-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.identity-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #6366f1;
  margin-bottom: 0.35rem;
}

.identity-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.8125rem;
  color: #475569;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.btn-cancel {
  padding: 0.55rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
}

.btn-cancel:hover {
  background: #f8fafc;
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  border: 1px solid #4338ca;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.25);
  transition: all 0.2s ease;
}

.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-svg {
  width: 16px;
  height: 16px;
  animation: spin 0.8s linear infinite;
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
  .form-row,
  .form-row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
