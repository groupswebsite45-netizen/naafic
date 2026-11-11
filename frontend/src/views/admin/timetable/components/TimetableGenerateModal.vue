<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import {
  SchoolClass,
  ClassTimetableOverview,
  TimetableGenerateResponse
} from '../../../../types/school';
import { timetableService } from '../../../../services/timetableService';

const props = defineProps<{
  isOpen: boolean;
  selectedClass: SchoolClass | null;
  academicYear: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'generated', result: TimetableGenerateResponse): void;
}>();

// Loading & overview state
const isLoadingOverview = ref(false);
const isGenerating = ref(false);
const overview = ref<ClassTimetableOverview | null>(null);
const generationResult = ref<TimetableGenerateResponse | null>(null);
const errorMessage = ref('');

// Config Form
const allWeekDays = [
  'Saturday',
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday'
];

const form = reactive({
  school_days: ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'],
  start_time: '07:30',
  end_time: '13:00',
  period_duration_minutes: 45,
  break_duration_minutes: 20,
  lunch_duration_minutes: 30,
  periods_per_day: 6,
  respect_teacher_availability: true,
  overwrite_existing: true,
  distribution: {} as Record<string, number>,
});

// Watch modal opening and selected class
watch(
  () => [props.isOpen, props.selectedClass?.id],
  async ([isOpen, classId]) => {
    if (isOpen && classId) {
      generationResult.value = null;
      errorMessage.value = '';
      await fetchClassOverview(Number(classId));
    }
  },
  { immediate: true }
);

async function fetchClassOverview(classId: number) {
  isLoadingOverview.value = true;
  errorMessage.value = '';
  try {
    const data = await timetableService.getClassOverview(classId, props.academicYear);
    overview.value = data;

    // Initialize subject lessons distribution default (3 or 4 per subject)
    const dist: Record<string, number> = {};
    for (const s of data.assigned_subjects) {
      dist[s.subject_name] = s.weekly_lessons || 3;
    }
    form.distribution = dist;

    // Load active settings if available
    try {
      const settings = await timetableService.getSettings(props.academicYear);
      if (settings) {
        if (settings.school_days?.length) form.school_days = [...settings.school_days];
        if (settings.start_time) form.start_time = settings.start_time.slice(0, 5);
        if (settings.end_time) form.end_time = settings.end_time.slice(0, 5);
        if (settings.period_duration_minutes) form.period_duration_minutes = settings.period_duration_minutes;
        if (settings.break_duration_minutes) form.break_duration_minutes = settings.break_duration_minutes;
        if (settings.lunch_duration_minutes) form.lunch_duration_minutes = settings.lunch_duration_minutes;
        if (settings.periods_per_day) form.periods_per_day = settings.periods_per_day;
      }
    } catch {
      // Fallback to default form values
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to retrieve class subject assignments.';
  } finally {
    isLoadingOverview.value = false;
  }
}

function toggleDay(day: string) {
  const idx = form.school_days.indexOf(day);
  if (idx > -1) {
    if (form.school_days.length > 1) {
      form.school_days.splice(idx, 1);
    }
  } else {
    form.school_days.push(day);
  }
}

const totalAssignedLessons = computed(() => {
  return Object.values(form.distribution).reduce((acc, val) => acc + (Number(val) || 0), 0);
});

const totalSlotsAvailable = computed(() => {
  return form.school_days.length * form.periods_per_day;
});

const hasAssignments = computed(() => {
  return Boolean(overview.value && overview.value.assigned_subjects.length > 0);
});

async function handleGenerate() {
  if (!props.selectedClass) return;
  isGenerating.value = true;
  errorMessage.value = '';
  generationResult.value = null;

  try {
    const res = await timetableService.generateTimetable({
      class_id: props.selectedClass.id,
      academic_year: props.academicYear,
      school_days: form.school_days,
      start_time: form.start_time,
      end_time: form.end_time,
      period_duration_minutes: form.period_duration_minutes,
      break_duration_minutes: form.break_duration_minutes,
      lunch_duration_minutes: form.lunch_duration_minutes,
      periods_per_day: form.periods_per_day,
      subject_lessons_distribution: form.distribution,
      respect_teacher_availability: form.respect_teacher_availability,
      overwrite_existing: form.overwrite_existing,
    });

    generationResult.value = res;
    emit('generated', res);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to generate timetable.';
  } finally {
    isGenerating.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
    <div class="modal-dialog generate-modal" @click.stop>
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-title-wrap">
          <div class="header-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Automatic Timetable Generator</h2>
            <p class="modal-subtitle">
              Intelligent constraint-based schedule generator for 
              <strong>{{ selectedClass?.name || 'Selected Class' }}</strong> 
              ({{ academicYear }})
            </p>
          </div>
        </div>
        <button type="button" class="btn-close" @click="emit('close')">&times;</button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        <!-- Error Alert -->
        <div v-if="errorMessage" class="alert-box alert-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>{{ errorMessage }}</div>
        </div>

        <!-- Generation Result Success Banner -->
        <div v-if="generationResult" class="generation-result-card" :class="{ 'has-warnings': generationResult.unplaced_subjects?.length }">
          <div class="result-header">
            <div class="result-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
            <div>
              <h4 class="result-title">{{ generationResult.message }}</h4>
              <p class="result-subtitle">
                Generated {{ generationResult.total_slots_generated }} timetable slots for {{ generationResult.class_name }}.
              </p>
            </div>
          </div>

          <!-- Unplaced constraints notice if any -->
          <div v-if="generationResult.unplaced_subjects && generationResult.unplaced_subjects.length > 0" class="unplaced-list">
            <div class="unplaced-title">⚠️ Scheduling Constraint Notes:</div>
            <div v-for="u in generationResult.unplaced_subjects" :key="u.subject_name" class="unplaced-item">
              <strong>{{ u.subject_name }}:</strong> {{ u.reason }} (Placed {{ u.placed }}/{{ u.requested }})
            </div>
          </div>

          <button type="button" class="btn-view-grid" @click="emit('close')">
            Review Generated Timetable in Grid &rarr;
          </button>
        </div>

        <!-- Class Overview & Retrieval State -->
        <div v-if="isLoadingOverview" class="loading-state">
          <div class="spinner" />
          <span>Retrieving assigned subjects and authorized teachers...</span>
        </div>

        <!-- No Assignments Warning -->
        <div v-else-if="!hasAssignments" class="empty-assignments-notice">
          <div class="notice-icon">⚠️</div>
          <div class="notice-content">
            <h3>No Subjects or Teachers Assigned</h3>
            <p>
              This class has no subjects or teacher assignments configured for academic year {{ academicYear }}.
              The automated generator requires at least one assigned subject with an authorized teacher.
            </p>
            <p class="notice-hint">
              Go to <strong>Academics &rarr; Classes & Teachers</strong> to assign subjects and teachers to {{ selectedClass?.name }}.
            </p>
          </div>
        </div>

        <!-- Form content if assignments exist -->
        <div v-else class="config-sections">
          <!-- Step 1: Assigned Subjects & Weekly Lesson Load -->
          <div class="section-card">
            <div class="section-header">
              <div class="badge-number">1</div>
              <div>
                <h3 class="section-title">Class Subjects & Required Lessons</h3>
                <p class="section-desc">
                  Retrieved {{ overview?.assigned_subjects.length }} subjects and authorized teachers for {{ selectedClass?.name }}.
                </p>
              </div>
            </div>

            <div class="subjects-table-wrap">
              <table class="subjects-table">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Authorized Teacher</th>
                    <th style="width: 140px; text-align: center;">Lessons / Week</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in overview?.assigned_subjects" :key="s.subject_id">
                    <td>
                      <div class="subject-cell">
                        <span class="subject-name">{{ s.subject_name }}</span>
                        <span v-if="s.subject_code" class="subject-code">{{ s.subject_code }}</span>
                      </div>
                    </td>
                    <td>
                      <div class="teacher-cell">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                          <circle cx="9" cy="7" r="4" />
                        </svg>
                        <span :class="{ 'unassigned-text': !s.teacher_name }">
                          {{ s.teacher_name || 'No Teacher Assigned' }}
                        </span>
                      </div>
                    </td>
                    <td style="text-align: center;">
                      <div class="lesson-input-wrap">
                        <input
                          v-model.number="form.distribution[s.subject_name]"
                          type="number"
                          min="1"
                          max="15"
                          class="lesson-input"
                        />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="lessons-summary-bar">
              <div>
                Total Weekly Lessons: <strong>{{ totalAssignedLessons }}</strong>
                <span class="capacity-hint">
                  (Available Period Slots: <strong>{{ totalSlotsAvailable }}</strong>)
                </span>
              </div>
              <div v-if="totalAssignedLessons > totalSlotsAvailable" class="overflow-warning">
                ⚠️ Lessons exceed available slots. Please add days or periods.
              </div>
            </div>
          </div>

          <!-- Step 2: Scheduling Constraints & School Hours -->
          <div class="section-card">
            <div class="section-header">
              <div class="badge-number">2</div>
              <div>
                <h3 class="section-title">Schedule Hours & Structure</h3>
                <p class="section-desc">Configure school days, periods, duration, and breaks.</p>
              </div>
            </div>

            <!-- School Days Selector -->
            <div class="form-group">
              <label class="form-label">School Days</label>
              <div class="days-pills">
                <button
                  v-for="d in allWeekDays"
                  :key="d"
                  type="button"
                  class="day-pill"
                  :class="{ active: form.school_days.includes(d) }"
                  @click="toggleDay(d)"
                >
                  {{ d.slice(0, 3) }}
                </button>
              </div>
            </div>

            <!-- Timings Grid -->
            <div class="form-grid-3">
              <div class="form-group">
                <label class="form-label">School Start Time</label>
                <input v-model="form.start_time" type="time" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">School End Time</label>
                <input v-model="form.end_time" type="time" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Periods Per Day</label>
                <input v-model.number="form.periods_per_day" type="number" min="3" max="10" class="form-input" />
              </div>
            </div>

            <div class="form-grid-3">
              <div class="form-group">
                <label class="form-label">Lesson Duration (mins)</label>
                <input v-model.number="form.period_duration_minutes" type="number" min="30" max="90" step="5" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Recess / Break (mins)</label>
                <input v-model.number="form.break_duration_minutes" type="number" min="10" max="60" step="5" class="form-input" />
              </div>
              <div class="form-group">
                <label class="form-label">Lunch Duration (mins)</label>
                <input v-model.number="form.lunch_duration_minutes" type="number" min="15" max="90" step="5" class="form-input" />
              </div>
            </div>

            <!-- Checkbox Constraints -->
            <div class="checkboxes-row">
              <label class="checkbox-label">
                <input v-model="form.respect_teacher_availability" type="checkbox" />
                <span>Respect Teacher Availability Constraints & Existing Schedules</span>
              </label>
              <label class="checkbox-label">
                <input v-model="form.overwrite_existing" type="checkbox" />
                <span>Replace existing draft timetable slots for this class</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-secondary" @click="emit('close')">
          Cancel
        </button>
        <button
          v-if="hasAssignments"
          type="button"
          class="btn-primary"
          :disabled="isGenerating || totalAssignedLessons === 0"
          @click="handleGenerate"
        >
          <div v-if="isGenerating" class="spinner-sm" />
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
          </svg>
          <span>{{ isGenerating ? 'Generating Schedule...' : 'Generate Timetable Automatically' }}</span>
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
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-dialog.generate-modal {
  background: #ffffff;
  border-radius: var(--radius-xl, 1rem);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 820px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalEnter 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.header-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.header-icon-box {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon-box svg {
  width: 1.5rem;
  height: 1.5rem;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 0.25rem;
}

.btn-close:hover {
  color: #0f172a;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.alert-box.alert-error {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.875rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.generation-result-card {
  padding: 1rem 1.25rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.generation-result-card.has-warnings {
  background: #fffbeb;
  border-color: #fde68a;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.result-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #dcfce7;
  color: #15803d;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.result-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #166534;
  margin: 0;
}

.result-subtitle {
  font-size: 0.8125rem;
  color: #15803d;
  margin-top: 0.15rem;
}

.unplaced-list {
  background: #ffffff;
  padding: 0.625rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid #fef3c7;
  font-size: 0.8125rem;
  color: #92400e;
}

.unplaced-title {
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.btn-view-grid {
  align-self: flex-start;
  padding: 0.5rem 1rem;
  background: #15803d;
  color: #ffffff;
  font-weight: 600;
  font-size: 0.8125rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.btn-view-grid:hover {
  background: #166534;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: #64748b;
  font-size: 0.875rem;
}

.empty-assignments-notice {
  display: flex;
  gap: 1rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.notice-icon {
  font-size: 2rem;
  line-height: 1;
}

.notice-content h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #92400e;
  margin: 0 0 0.35rem 0;
}

.notice-content p {
  font-size: 0.8125rem;
  color: #78350f;
  margin: 0 0 0.35rem 0;
  line-height: 1.4;
}

.notice-hint {
  font-weight: 600;
}

.config-sections {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.125rem;
  background: #ffffff;
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.badge-number {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: var(--brand-primary, #1e40af);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.8125rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.section-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.subjects-table-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow: hidden;
  max-height: 240px;
  overflow-y: auto;
}

.subjects-table {
  width: 100%;
  min-width: 520px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.subjects-table th {
  background: #f8fafc;
  padding: 0.625rem 0.75rem;
  text-align: left;
  font-weight: 700;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.subjects-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.subject-cell {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.subject-name {
  font-weight: 600;
  color: #0f172a;
}

.subject-code {
  font-size: 0.6875rem;
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.05rem 0.35rem;
  border-radius: 0.25rem;
  color: #475569;
}

.teacher-cell {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #334155;
}

.teacher-cell svg {
  width: 0.875rem;
  height: 0.875rem;
  color: #64748b;
}

.unassigned-text {
  color: #dc2626;
  font-style: italic;
}

.lesson-input-wrap {
  display: flex;
  justify-content: center;
}

.lesson-input {
  width: 4.5rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  text-align: center;
  font-weight: 700;
  font-size: 0.875rem;
}

.lessons-summary-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
  font-size: 0.8125rem;
  color: #334155;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.capacity-hint {
  color: #64748b;
  margin-left: 0.5rem;
}

.overflow-warning {
  color: #b45309;
  font-weight: 600;
  font-size: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 0.875rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
}

.days-pills {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.day-pill {
  padding: 0.35rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.12s ease;
}

.day-pill.active {
  background: var(--brand-primary, #1e40af);
  color: #ffffff;
  border-color: var(--brand-primary, #1e40af);
}

.form-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.875rem;
}

.form-input {
  padding: 0.45rem 0.625rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  color: #0f172a;
}

.checkboxes-row {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #334155;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.125rem;
  background: var(--brand-primary, #1e40af);
  color: #ffffff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s ease;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary svg {
  width: 1rem;
  height: 1rem;
}

.spinner-sm {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #cbd5e1;
  border-top-color: var(--brand-primary, #1e40af);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes modalEnter {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 640px) {
  .form-grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>
