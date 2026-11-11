<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { examService, CreateExamPayload, BatchCreateExamPayload } from '../../../services/examService';
import { ExamFilterOptions, ConflictCheckItem } from '../../../types/school';

const router = useRouter();

const isLoadingOptions = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref('');
const filterOptions = ref<ExamFilterOptions | null>(null);

// Mode: 'single' | 'batch'
const schedulingMode = ref<'single' | 'batch'>('single');

// Single Form State
const form = reactive({
  name: '',
  exam_type: 'FINAL',
  academic_year: '2025/2026',
  class_id: undefined as number | undefined,
  subject_id: undefined as number | undefined,
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
  start_time: '08:30 AM',
  end_time: '11:30 AM',
  result_submission_deadline: '',
  instructions: 'Please grade and enter verified student marks on or before the result submission deadline. Ensure absence reasons are recorded appropriately.',
  max_marks: 100,
  pass_marks: 50,
  status: 'SCHEDULED',
});

// Batch Form State (Multiple classes & subjects)
const selectedBatchClasses = ref<number[]>([]);
const selectedBatchSubjects = ref<number[]>([]);

// Conflict warning state
const isCheckingConflict = ref(false);
const conflictsFound = ref<ConflictCheckItem[]>([]);

// Quick deadline presets helper
function applyDeadlinePreset(daysFromStart: number) {
  const base = form.start_date ? new Date(form.start_date) : new Date();
  base.setDate(base.getDate() + daysFromStart);
  base.setHours(23, 59, 0, 0);

  const yyyy = base.getFullYear();
  const mm = String(base.getMonth() + 1).padStart(2, '0');
  const dd = String(base.getDate()).padStart(2, '0');
  const hh = String(base.getHours()).padStart(2, '0');
  const min = String(base.getMinutes()).padStart(2, '0');
  form.result_submission_deadline = `${yyyy}-${mm}-${dd}T${hh}:${min}`;
}

// Deadline countdown preview
const deadlineCountdownPreview = computed(() => {
  if (!form.result_submission_deadline) return null;
  const target = new Date(form.result_submission_deadline);
  const now = new Date();
  const diffMs = target.getTime() - now.getTime();
  if (diffMs < 0) {
    return { text: 'Deadline is in the past', isPast: true, days: 0 };
  }
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  return {
    text: `${days} day${days !== 1 ? 's' : ''} ${hours} hr${hours !== 1 ? 's' : ''} from now`,
    isPast: false,
    days
  };
});

// Form validation
const dateError = computed(() => {
  if (form.end_date && form.start_date && form.end_date < form.start_date) {
    return 'End date cannot be earlier than start date.';
  }
  return '';
});

const marksError = computed(() => {
  if (form.max_marks <= 0) return 'Maximum marks must be greater than zero.';
  if (form.pass_marks < 0) return 'Passing marks cannot be negative.';
  if (form.pass_marks > form.max_marks) return 'Passing marks cannot exceed maximum marks.';
  return '';
});

const deadlineError = computed(() => {
  if (form.result_submission_deadline && form.start_date) {
    const startObj = new Date(form.start_date);
    const deadlineObj = new Date(form.result_submission_deadline);
    if (deadlineObj < startObj) {
      return 'Result submission deadline cannot be earlier than the examination start date.';
    }
  }
  return '';
});

const isFormValid = computed(() => {
  if (!form.name.trim() || !form.exam_type || !form.academic_year || !form.start_date) return false;
  if (dateError.value || marksError.value || deadlineError.value) return false;

  if (schedulingMode.value === 'single') {
    return Boolean(form.class_id && form.subject_id);
  } else {
    return selectedBatchClasses.value.length > 0 && selectedBatchSubjects.value.length > 0;
  }
});

// Check conflicts on class/date change
async function checkScheduleConflicts() {
  if (!form.class_id || !form.start_date) {
    conflictsFound.value = [];
    return;
  }
  isCheckingConflict.value = true;
  try {
    const res = await examService.checkConflict({
      class_id: form.class_id,
      start_date: form.start_date,
      end_date: form.end_date || null
    });
    conflictsFound.value = res.conflicts || [];
  } catch (err) {
    console.error('Failed to check conflicts', err);
  } finally {
    isCheckingConflict.value = false;
  }
}

watch([() => form.class_id, () => form.start_date, () => form.end_date], () => {
  checkScheduleConflicts();
});

// Load options from backend
async function loadFilterOptions() {
  isLoadingOptions.value = true;
  try {
    const data = await examService.getFilterOptions();
    filterOptions.value = data;
    if (data.academic_years && data.academic_years.length > 0) {
      form.academic_year = data.academic_years[0];
    }
    if (data.classes.length > 0 && !form.class_id) {
      form.class_id = data.classes[0].id;
    }
    if (data.subjects.length > 0 && !form.subject_id) {
      form.subject_id = data.subjects[0].id;
    }
  } catch (err: any) {
    errorMessage.value = 'Failed to load class and subject directories from database.';
  } finally {
    isLoadingOptions.value = false;
  }
}

async function handleSubmit() {
  if (!isFormValid.value) return;
  isSubmitting.value = true;
  errorMessage.value = '';

  try {
    const deadlineVal = form.result_submission_deadline ? new Date(form.result_submission_deadline).toISOString() : null;

    if (schedulingMode.value === 'single') {
      const payload: CreateExamPayload = {
        name: form.name.trim(),
        exam_type: form.exam_type.trim(),
        academic_year: form.academic_year.trim(),
        class_id: form.class_id!,
        subject_id: form.subject_id!,
        start_date: form.start_date,
        end_date: form.end_date || null,
        start_time: form.start_time || null,
        end_time: form.end_time || null,
        result_submission_deadline: deadlineVal,
        instructions: form.instructions.trim() || null,
        max_marks: Number(form.max_marks),
        pass_marks: Number(form.pass_marks),
        status: form.status,
      };
      const created = await examService.createExam(payload);
      router.push(`/admin/exams/${created.id}`);
    } else {
      const batchPayload: BatchCreateExamPayload = {
        name: form.name.trim(),
        exam_type: form.exam_type.trim(),
        academic_year: form.academic_year.trim(),
        class_ids: selectedBatchClasses.value,
        subject_ids: selectedBatchSubjects.value,
        start_date: form.start_date,
        end_date: form.end_date || null,
        start_time: form.start_time || null,
        end_time: form.end_time || null,
        result_submission_deadline: deadlineVal,
        instructions: form.instructions.trim() || null,
        max_marks: Number(form.max_marks),
        pass_marks: Number(form.pass_marks),
        status: form.status,
      };
      await examService.createBatchExams(batchPayload);
      router.push('/admin/exams');
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to schedule examination in database.';
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(() => {
  loadFilterOptions();
  // Default to 1-Month (30 days) submission deadline preset as required
  applyDeadlinePreset(30);
});
</script>

<template>
  <div class="exam-create-page">
    <!-- Top Navigation -->
    <div class="top-nav">
      <button type="button" class="back-link" @click="router.push('/admin/exams')">
        <svg class="back-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        <span>Back to Exams Directory</span>
      </button>
    </div>

    <!-- Header -->
    <div class="page-title-row">
      <div>
        <h1 class="page-title">Advanced Examination Scheduling</h1>
        <p class="page-subtitle">Configure official examinations, schedule windows, teacher result submission deadlines, and grading criteria.</p>
      </div>

      <!-- Mode Selector -->
      <div class="mode-tabs">
        <button
          type="button"
          class="mode-btn"
          :class="{ active: schedulingMode === 'single' }"
          @click="schedulingMode = 'single'"
        >
          Single Exam
        </button>
        <button
          type="button"
          class="mode-btn"
          :class="{ active: schedulingMode === 'batch' }"
          @click="schedulingMode = 'batch'"
        >
          Multi-Class Batch
        </button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="error-banner">
      <svg class="err-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Main Form Card -->
    <form class="form-card" @submit.prevent="handleSubmit">
      <!-- SECTION 1: Examination Identity & Official Type -->
      <div class="form-section">
        <div class="section-header">
          <span class="step-num">1</span>
          <div>
            <h2 class="section-title">Examination Identity & Type</h2>
            <p class="section-desc">Official school examinations are administered exclusively by authorized administrators.</p>
          </div>
        </div>

        <div class="form-grid-3">
          <div class="field-item">
            <label class="field-label">Examination Title <span class="req">*</span></label>
            <input
              v-model="form.name"
              type="text"
              placeholder="e.g. Term 1 Final Examination 2026"
              class="form-input"
              required
            />
          </div>

          <div class="field-item">
            <label class="field-label">Examination Type <span class="req">*</span></label>
            <select v-model="form.exam_type" class="form-select" required>
              <option value="FINAL">Final Examination</option>
              <option value="MID_TERM">Midterm Examination</option>
              <option value="MONTHLY">Monthly Examination</option>
            </select>
            <span class="field-hint">Teachers cannot schedule official Final, Midterm, or Monthly exams.</span>
          </div>

          <div class="field-item">
            <label class="field-label">Academic Year <span class="req">*</span></label>
            <select v-model="form.academic_year" class="form-select" required>
              <option
                v-for="y in filterOptions?.academic_years || ['2025/2026', '2026/2027']"
                :key="y"
                :value="y"
              >
                {{ y }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- SECTION 2: Class & Subject Assignment -->
      <div class="form-section">
        <div class="section-header">
          <span class="step-num">2</span>
          <div>
            <h2 class="section-title">Class & Subject Assignment</h2>
            <p class="section-desc">Assign specific class sections and curriculum subjects. Submissions will automatically route to assigned teachers.</p>
          </div>
        </div>

        <!-- Single Mode Selection -->
        <div v-if="schedulingMode === 'single'" class="form-grid-2">
          <div class="field-item">
            <label class="field-label">Select Class & Section <span class="req">*</span></label>
            <select v-model="form.class_id" class="form-select" required>
              <option :value="undefined" disabled>Select class...</option>
              <option v-for="c in filterOptions?.classes" :key="c.id" :value="c.id">
                {{ c.name }} ({{ c.code }})
              </option>
            </select>
          </div>

          <div class="field-item">
            <label class="field-label">Select Subject <span class="req">*</span></label>
            <select v-model="form.subject_id" class="form-select" required>
              <option :value="undefined" disabled>Select subject...</option>
              <option v-for="s in filterOptions?.subjects" :key="s.id" :value="s.id">
                {{ s.name }} ({{ s.code }})
              </option>
            </select>
          </div>
        </div>

        <!-- Batch Mode Selection -->
        <div v-else class="batch-selection-container">
          <div class="batch-col">
            <label class="field-label">Target Classes ({{ selectedBatchClasses.length }} selected) <span class="req">*</span></label>
            <div class="multi-select-box">
              <label
                v-for="c in filterOptions?.classes"
                :key="c.id"
                class="checkbox-item"
              >
                <input
                  type="checkbox"
                  :value="c.id"
                  v-model="selectedBatchClasses"
                />
                <span>{{ c.name }} ({{ c.code }})</span>
              </label>
            </div>
          </div>

          <div class="batch-col">
            <label class="field-label">Target Subjects ({{ selectedBatchSubjects.length }} selected) <span class="req">*</span></label>
            <div class="multi-select-box">
              <label
                v-for="s in filterOptions?.subjects"
                :key="s.id"
                class="checkbox-item"
              >
                <input
                  type="checkbox"
                  :value="s.id"
                  v-model="selectedBatchSubjects"
                />
                <span>{{ s.name }} ({{ s.code }})</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Conflict Alert Banner -->
        <div v-if="conflictsFound.length > 0" class="conflict-alert-box">
          <svg class="conflict-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <div>
            <strong>Potential Schedule Conflict:</strong>
            <ul class="conflict-list">
              <li v-for="(c, idx) in conflictsFound" :key="idx">{{ c.message }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- SECTION 3: Schedule Window, Timing & Marks Scale -->
      <div class="form-section">
        <div class="section-header">
          <span class="step-num">3</span>
          <div>
            <h2 class="section-title">Examination Window, Timing & Marks Scale</h2>
            <p class="section-desc">Keep examination calendar dates and result deadlines distinct.</p>
          </div>
        </div>

        <div class="form-grid-4">
          <div class="field-item">
            <label class="field-label">Start Date <span class="req">*</span></label>
            <input
              v-model="form.start_date"
              type="date"
              class="form-input"
              required
            />
          </div>

          <div class="field-item">
            <label class="field-label">End Date</label>
            <input
              v-model="form.end_date"
              type="date"
              class="form-input"
            />
            <span v-if="dateError" class="field-err">{{ dateError }}</span>
          </div>

          <div class="field-item">
            <label class="field-label">Start Time</label>
            <input
              v-model="form.start_time"
              type="text"
              placeholder="08:30 AM"
              class="form-input"
            />
          </div>

          <div class="field-item">
            <label class="field-label">End Time</label>
            <input
              v-model="form.end_time"
              type="text"
              placeholder="11:30 AM"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-grid-2" style="margin-top: 0.5rem;">
          <div class="field-item">
            <label class="field-label">Maximum Total Marks <span class="req">*</span></label>
            <input
              v-model="form.max_marks"
              type="number"
              min="1"
              max="1000"
              class="form-input"
              required
            />
          </div>

          <div class="field-item">
            <label class="field-label">Passing Mark <span class="req">*</span></label>
            <input
              v-model="form.pass_marks"
              type="number"
              min="0"
              :max="form.max_marks"
              class="form-input"
              required
            />
            <span v-if="marksError" class="field-err">{{ marksError }}</span>
          </div>
        </div>
      </div>

      <!-- SECTION 4: Result Submission Deadline & Teacher Instructions -->
      <div class="form-section">
        <div class="section-header">
          <span class="step-num">4</span>
          <div>
            <h2 class="section-title">Result Submission Deadline & Teacher Guidance</h2>
            <p class="section-desc">Define how long teachers have to grade and submit results. Submissions become overdue once this passes.</p>
          </div>
        </div>

        <div class="deadline-control-box">
          <div class="preset-buttons-row">
            <span class="preset-label">Quick Deadline Presets:</span>
            <button
              type="button"
              class="preset-btn recommended"
              @click="applyDeadlinePreset(30)"
            >
              +1 Month (+30 Days)
            </button>
            <button
              type="button"
              class="preset-btn"
              @click="applyDeadlinePreset(14)"
            >
              +2 Weeks (+14 Days)
            </button>
            <button
              type="button"
              class="preset-btn"
              @click="applyDeadlinePreset(45)"
            >
              +45 Days (End of Term)
            </button>
          </div>

          <div class="form-grid-2" style="margin-top: 0.75rem;">
            <div class="field-item">
              <label class="field-label">Submission Deadline Date & Time <span class="req">*</span></label>
              <input
                v-model="form.result_submission_deadline"
                type="datetime-local"
                class="form-input"
                required
              />
              <span v-if="deadlineError" class="field-err">{{ deadlineError }}</span>
            </div>

            <div class="field-item">
              <label class="field-label">Remaining Time Telemetry</label>
              <div v-if="deadlineCountdownPreview" class="deadline-badge-box" :class="{ 'overdue-badge': deadlineCountdownPreview.isPast }">
                <svg class="clock-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                <span>{{ deadlineCountdownPreview.text }}</span>
              </div>
              <div v-else class="deadline-badge-box muted">
                <span>Select a submission deadline to preview countdown</span>
              </div>
            </div>
          </div>

          <div class="field-item" style="margin-top: 0.75rem;">
            <label class="field-label">Instructions for Teachers</label>
            <textarea
              v-model="form.instructions"
              rows="3"
              placeholder="e.g. Please verify absent students and ensure all section papers match curriculum rubric before final submission to Administration."
              class="form-textarea"
            ></textarea>
            <span class="field-hint">These instructions will be displayed prominently in the Teacher Portal examination workspace.</span>
          </div>
        </div>
      </div>

      <!-- SECTION 5: Lifecycle Status -->
      <div class="form-section">
        <div class="section-header">
          <span class="step-num">5</span>
          <div>
            <h2 class="section-title">Examination Status</h2>
            <p class="section-desc">Choose initial lifecycle state for this examination schedule.</p>
          </div>
        </div>

        <div class="status-options-row">
          <label class="status-radio-card" :class="{ selected: form.status === 'SCHEDULED' }">
            <input
              v-model="form.status"
              type="radio"
              value="SCHEDULED"
            />
            <div class="radio-content">
              <span class="radio-title">Scheduled</span>
              <span class="radio-desc">Official examination scheduled on academic calendar for upcoming dates.</span>
            </div>
          </label>

          <label class="status-radio-card" :class="{ selected: form.status === 'OPEN_FOR_RESULTS' }">
            <input
              v-model="form.status"
              type="radio"
              value="OPEN_FOR_RESULTS"
            />
            <div class="radio-content">
              <span class="radio-title">Open for Results</span>
              <span class="radio-desc">Teachers can immediately enter, save drafts, and submit results.</span>
            </div>
          </label>

          <label class="status-radio-card" :class="{ selected: form.status === 'DRAFT' }">
            <input
              v-model="form.status"
              type="radio"
              value="DRAFT"
            />
            <div class="radio-content">
              <span class="radio-title">Draft</span>
              <span class="radio-desc">Preliminary schedule draft without locking teacher workflows.</span>
            </div>
          </label>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="form-actions-footer">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isSubmitting"
          @click="router.push('/admin/exams')"
        >
          Cancel
        </button>

        <button
          type="submit"
          class="btn-save"
          :disabled="isSubmitting || !isFormValid"
        >
          <span v-if="isSubmitting" class="spinner" />
          <span>{{ isSubmitting ? 'Scheduling Examination...' : 'Schedule Official Examination' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.exam-create-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1040px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  box-sizing: border-box;
}

.top-nav {
  margin-bottom: 0.75rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #4f46e5;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0;
}

.back-link:hover {
  text-decoration: underline;
}

.back-icon {
  width: 16px;
  height: 16px;
}

.page-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.625rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

.mode-tabs {
  display: flex;
  background-color: #f1f5f9;
  border-radius: 8px;
  padding: 0.25rem;
}

.mode-btn {
  padding: 0.45rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-btn.active {
  background-color: #ffffff;
  color: #4f46e5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.err-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Form Card */
.form-card {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 1.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #e0e7ff;
  color: #4338ca;
  font-size: 0.8125rem;
  font-weight: 700;
  flex-shrink: 0;
}

.section-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.section-desc {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.15rem 0 0 0;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.form-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.form-grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

@media (max-width: 768px) {
  .form-grid-2,
  .form-grid-3,
  .form-grid-4 {
    grid-template-columns: 1fr;
  }
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.req {
  color: #dc2626;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.55rem 0.75rem;
  font-size: 0.875rem;
  color: #0f172a;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.15s ease;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.field-err {
  font-size: 0.75rem;
  color: #dc2626;
  font-weight: 500;
}

.field-hint {
  font-size: 0.75rem;
  color: #64748b;
}

/* Batch container */
.batch-selection-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 640px) {
  .batch-selection-container {
    grid-template-columns: 1fr;
  }
}

.multi-select-box {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.5rem;
  background-color: #f8fafc;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #334155;
  cursor: pointer;
  padding: 0.25rem 0.4rem;
  border-radius: 4px;
}

.checkbox-item:hover {
  background-color: #e2e8f0;
}

/* Deadline controls */
.deadline-control-box {
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem;
}

.preset-buttons-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
}

.preset-btn {
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  border-color: #6366f1;
  color: #4f46e5;
  background-color: #eef2ff;
}

.preset-btn.recommended {
  border-color: #a5b4fc;
  background-color: #e0e7ff;
  color: #3730a3;
}

.deadline-badge-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  background-color: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 6px;
  color: #065f46;
  font-size: 0.8125rem;
  font-weight: 600;
}

.deadline-badge-box.overdue-badge {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.deadline-badge-box.muted {
  background-color: #f1f5f9;
  border-color: #e2e8f0;
  color: #64748b;
  font-weight: 500;
}

.clock-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* Status Radio Cards */
.status-options-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 768px) {
  .status-options-row {
    grid-template-columns: 1fr;
  }
}

.status-radio-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.status-radio-card.selected {
  border-color: #4f46e5;
  background-color: #f5f3ff;
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.radio-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
}

.radio-desc {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.3;
}

/* Conflict Alert */
.conflict-alert-box {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  background-color: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  color: #92400e;
  font-size: 0.8125rem;
}

.conflict-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}

.conflict-list {
  margin: 0.25rem 0 0 1rem;
  padding: 0;
}

/* Form Actions */
.form-actions-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
}

.btn-cancel {
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background-color: #f1f5f9;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  background-color: #4f46e5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-save:hover:not(:disabled) {
  background-color: #4338ca;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
