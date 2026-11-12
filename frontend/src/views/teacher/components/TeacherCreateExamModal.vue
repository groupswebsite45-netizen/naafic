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
    const opts = await teacherPortalService.getExamOptions({
      academic_year: form.academic_year || undefined
    });
    examOptions.value = opts;

    if (opts.academic_years && opts.academic_years.length > 0) {
      if (!form.academic_year || !opts.academic_years.includes(form.academic_year)) {
        form.academic_year = (opts as any).selected_academic_year || opts.academic_years[0];
      }
    } else {
      form.academic_year = '';
    }

    if (opts.subjects && opts.subjects.length > 0) {
      if (!form.subject_id || !opts.subjects.some((s) => s.id === form.subject_id)) {
        form.subject_id = opts.subjects[0].id;
      }
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

// Cascading subject change
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

// Cascading academic year change
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
    <div class="modal-card" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-left">
          <div class="header-icon-wrap">
            <svg class="header-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Create Class Quiz</h2>
            <p class="modal-subtitle">Schedule a quiz assessment for your assigned class and subject</p>
          </div>
        </div>

        <div class="header-right-actions">
          <button
            type="button"
            class="btn-refresh-assignments"
            :disabled="isLoadingAssignments"
            title="Reload active assignments from Administration"
            @click="loadAssignments(true)"
          >
            <svg class="refresh-icon" :class="{ spinning: isLoadingAssignments }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
            </svg>
            <span>Sync Assignments</span>
          </button>
          <button type="button" class="close-btn" aria-label="Close modal" @click="emit('close')">
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
          <span><strong>Draft Restored:</strong> Your previously entered quiz details have been restored.</span>
        </div>
        <button type="button" class="btn-discard-draft" @click="discardDraft">
          Discard Draft
        </button>
      </div>

      <!-- Modal Body -->
      <form class="modal-body" @submit.prevent="handleSubmit">
        <!-- Examination Policy Notice -->
        <div class="admin-notice-banner">
          <svg class="notice-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
          <div class="notice-text">
            <strong>Institutional Policy:</strong> Official examinations (<em>Midterm, Final, Monthly</em>) are scheduled exclusively by School Administration. Teachers can create quizzes for their assigned classes.
          </div>
        </div>

        <!-- Success Refresh Banner -->
        <div v-if="refreshSuccess" class="refresh-success-banner">
          <svg class="success-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
          <span>Active teaching assignments refreshed successfully!</span>
        </div>

        <!-- Error Banner -->
        <div v-if="errorMessage" class="error-banner">
          <svg class="err-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <div v-if="isLoadingAssignments" class="loading-state">
          <div class="spinner-ring" />
          <p>Loading your assigned classes and subjects...</p>
        </div>

        <div v-else class="form-content">
          <!-- Academic Year & Subject Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                Academic Year <span class="required">*</span>
              </label>
              <select v-model="form.academic_year" class="form-select" required>
                <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
                <option v-if="availableYears.length === 0" value="2026/2027">2026/2027</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">
                Assigned Subject <span class="required">*</span>
              </label>
              <select v-model="form.subject_id" class="form-select" required>
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
              <select v-model="form.class_id" class="form-select" required :disabled="!form.subject_id">
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
                <span class="quiz-badge-label">Quiz Assessment</span>
              </div>
            </div>
          </div>

          <!-- Exam Title -->
          <div class="form-group">
            <label class="form-label">
              Quiz Title <span class="required">*</span>
            </label>
            <input
              v-model="form.name"
              type="text"
              class="form-input title-input"
              placeholder="e.g. Quiz: Mathematics (Grade 9-A)"
              required
            />
          </div>

          <!-- Date & Marks Row -->
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                Quiz Date <span class="required">*</span>
              </label>
              <input v-model="form.start_date" type="date" class="form-input" required />
            </div>

            <div class="form-group">
              <label class="form-label">End Date (Optional)</label>
              <input v-model="form.end_date" type="date" class="form-input" :min="form.start_date" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                Max Marks <span class="required">*</span>
              </label>
              <input v-model.number="form.max_marks" type="number" min="1" max="1000" class="form-input" required />
            </div>

            <div class="form-group">
              <label class="form-label">
                Passing Marks <span class="required">*</span>
              </label>
              <input v-model.number="form.pass_marks" type="number" min="1" :max="form.max_marks" class="form-input" required />
            </div>
          </div>

          <!-- Instructions -->
          <div class="form-group">
            <label class="form-label">Instructions / Exam Notes</label>
            <textarea
              v-model="form.instructions"
              class="form-textarea"
              rows="3"
              placeholder="Add instructions for students or personal notes for this assessment..."
            />
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="emit('close')">
            Cancel
          </button>
          <button type="submit" class="btn-create" :disabled="isSubmitting || isLoadingAssignments">
            <svg v-if="!isSubmitting" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            <span>{{ isSubmitting ? 'Creating Quiz...' : 'Create Quiz & Open Roster' }}</span>
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
  background: rgba(10, 25, 47, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 1rem;
}

.modal-card {
  background: #FFFFFF;
  border-radius: 20px;
  width: 100%;
  max-width: 680px;
  max-height: 92vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 1.75rem;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  background: #F8FAFC;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #ECFDF5;
  color: #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon {
  width: 22px;
  height: 22px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8rem;
  color: #64748B;
  margin-top: 0.2rem;
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-refresh-assignments {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.35rem 0.65rem;
  border-radius: 8px;
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-refresh-assignments:hover {
  background: #F1F5F9;
}

.refresh-icon {
  width: 14px;
  height: 14px;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.close-btn {
  background: none;
  border: none;
  font-size: 1.75rem;
  color: #94A3B8;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover { color: #0A192F; }

.draft-notice-banner {
  background: #EFF6FF;
  border-bottom: 1px solid #BFDBFE;
  padding: 0.75rem 1.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.draft-notice-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #1E40AF;
}

.draft-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.btn-discard-draft {
  background: none;
  border: none;
  color: #DC2626;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
}

.modal-body {
  padding: 1.5rem 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.admin-notice-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-left: 3px solid #2563EB;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #475569;
  line-height: 1.45;
}

.notice-icon {
  width: 18px;
  height: 18px;
  color: #2563EB;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.refresh-success-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}

.success-icon {
  width: 16px;
  height: 16px;
  color: #10B981;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  color: #991B1B;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
}

.err-icon {
  width: 16px;
  height: 16px;
  color: #EF4444;
}

.loading-state {
  padding: 3rem 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  color: #64748B;
  font-size: 0.86rem;
}

.spinner-ring {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #10B981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.74rem;
  font-weight: 700;
  color: #0A192F;
}

.required { color: #DC2626; }

.badge-teacher-only {
  font-size: 0.65rem;
  font-weight: 700;
  background: #ECFDF5;
  color: #059669;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.35rem;
}

.form-select, .form-input, .form-textarea {
  background: #F8FAFC;
  border: 1px solid #CBD5E1;
  color: #0A192F;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  font-size: 0.86rem;
  font-weight: 600;
  outline: none;
}

.form-textarea {
  resize: vertical;
  font-weight: 500;
}

.title-input {
  font-weight: 700;
}

.hint-text {
  font-size: 0.72rem;
  margin-top: 0.2rem;
}

.text-amber { color: #D97706; }

.single-quiz-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  padding: 0.55rem 0.85rem;
  border-radius: 8px;
  color: #065F46;
  font-size: 0.84rem;
  font-weight: 700;
}

.quiz-check-icon {
  width: 16px;
  height: 16px;
  color: #10B981;
}

.modal-footer {
  padding-top: 1rem;
  border-top: 1px solid #F1F5F9;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #475569;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #10B981;
  border: none;
  color: #FFFFFF;
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-create:hover:not(:disabled) {
  background: #059669;
}

.btn-create svg { width: 16px; height: 16px; }

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .modal-header {
    flex-direction: column;
  }
  .header-right-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
