<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import {
  TimetableEntry,
  SchoolClass,
  Teacher,
  Subject,
  TimetableConflictDetail
} from '../../../../types/school';
import { timetableService, CreateTimetablePayload } from '../../../../services/timetableService';

const props = defineProps<{
  isOpen: boolean;
  isEditing: boolean;
  slot: TimetableEntry | null;
  defaultDay?: string;
  defaultClassId?: number;
  defaultTeacherId?: number;
  academicYear: string;
  classes: SchoolClass[];
  teachers: Teacher[];
  subjects: Subject[];
  days: string[];
  rooms: string[];
  isSubmitting: boolean;
  submitError?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', payload: CreateTimetablePayload): void;
}>();

const form = reactive({
  class_id: 0,
  subject_id: 0,
  teacher_id: 0,
  academic_year: '2026/2027',
  day_of_week: 'Monday',
  start_time: '08:00',
  end_time: '09:00',
  room: '',
  status: 'ACTIVE',
});

const formErrors = reactive<Record<string, string>>({});
const detectedConflicts = ref<TimetableConflictDetail[]>([]);
const isCheckingConflict = ref(false);

function onClassChange() {
  const chosen = props.classes.find((c) => c.id === Number(form.class_id));
  if (chosen && chosen.academic_year) {
    form.academic_year = chosen.academic_year;
  }
  runConflictCheck();
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      Object.keys(formErrors).forEach((k) => delete formErrors[k]);
      detectedConflicts.value = [];

      if (props.isEditing && props.slot) {
        form.class_id = props.slot.class_id;
        form.subject_id = props.slot.subject_id;
        form.teacher_id = props.slot.teacher_id || 0;
        form.academic_year = props.slot.academic_year || props.academicYear;
        form.day_of_week = props.slot.day_of_week || 'Monday';
        form.start_time = props.slot.start_time.slice(0, 5);
        form.end_time = props.slot.end_time.slice(0, 5);
        form.room = props.slot.room || props.slot.room_number || '';
        form.status = props.slot.status || 'ACTIVE';
      } else {
        const initialClassId = props.defaultClassId || (props.classes[0]?.id ?? 0);
        form.class_id = initialClassId;
        const initialClass = props.classes.find((c) => c.id === initialClassId);
        form.subject_id = props.subjects[0]?.id ?? 0;
        form.teacher_id = props.defaultTeacherId || 0;
        form.academic_year = initialClass?.academic_year || props.academicYear || '2026/2027';
        form.day_of_week = props.defaultDay || props.days[0] || 'Monday';
        form.start_time = '08:00';
        form.end_time = '09:00';
        form.room = 'Room 101';
        form.status = 'ACTIVE';
      }
      runConflictCheck();
    }
  },
  { immediate: true }
);

async function runConflictCheck() {
  if (!form.class_id || !form.start_time || !form.end_time || form.start_time >= form.end_time) {
    detectedConflicts.value = [];
    return;
  }

  isCheckingConflict.value = true;
  try {
    const res = await timetableService.checkConflict({
      class_id: Number(form.class_id),
      subject_id: Number(form.subject_id),
      teacher_id: form.teacher_id ? Number(form.teacher_id) : null,
      academic_year: form.academic_year,
      day_of_week: form.day_of_week,
      start_time: `${form.start_time}:00`,
      end_time: `${form.end_time}:00`,
      room: form.room || null,
      exclude_id: props.isEditing && props.slot ? props.slot.id : null,
    });
    detectedConflicts.value = res.conflicts || [];
  } catch (err) {
    console.error('Error running conflict check:', err);
  } finally {
    isCheckingConflict.value = false;
  }
}

function validateForm(): boolean {
  Object.keys(formErrors).forEach((k) => delete formErrors[k]);
  let isValid = true;

  if (!form.class_id || form.class_id === 0) {
    formErrors.class_id = 'Please select a class.';
    isValid = false;
  }
  if (!form.subject_id || form.subject_id === 0) {
    formErrors.subject_id = 'Please select a subject.';
    isValid = false;
  }
  if (!form.academic_year.trim()) {
    formErrors.academic_year = 'Academic year is required.';
    isValid = false;
  }
  if (!form.day_of_week.trim()) {
    formErrors.day_of_week = 'Day of week is required.';
    isValid = false;
  }
  if (!form.start_time || !form.end_time) {
    formErrors.times = 'Both start and end times are required.';
    isValid = false;
  } else if (form.start_time >= form.end_time) {
    formErrors.times = 'End time must be after start time.';
    isValid = false;
  }

  return isValid;
}

function handleSubmit() {
  if (!validateForm()) return;

  emit('save', {
    class_id: Number(form.class_id),
    subject_id: Number(form.subject_id),
    teacher_id: form.teacher_id ? Number(form.teacher_id) : null,
    academic_year: form.academic_year.trim(),
    day_of_week: form.day_of_week.trim(),
    start_time: form.start_time.length === 5 ? `${form.start_time}:00` : form.start_time,
    end_time: form.end_time.length === 5 ? `${form.end_time}:00` : form.end_time,
    room: form.room.trim() || null,
    status: form.status,
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="slot-modal-title">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="header-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </div>
        <div class="header-titles">
          <h2 id="slot-modal-title" class="modal-title">
            {{ isEditing ? 'Edit Schedule Slot' : 'Add Timetable Schedule Slot' }}
          </h2>
          <p class="modal-subtitle">
            Configure academic class, subject, assigned teacher, timings, and classroom.
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

      <!-- Submit Error Alert in Modal -->
      <div v-if="submitError" class="modal-conflict-warning" style="background: #fef2f2; border-color: #fca5a5; color: #991b1b;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="warning-icon" style="color: #ef4444;">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <div class="warning-texts">
          <span class="warning-heading">Error Saving Slot:</span>
          <p class="warning-detail" style="color: #b91c1c;">{{ submitError }}</p>
        </div>
      </div>

      <!-- Live Conflict Alert in Modal -->
      <div v-if="detectedConflicts.length > 0" class="modal-conflict-warning">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="warning-icon">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <div class="warning-texts">
          <span class="warning-heading">Conflict Detected:</span>
          <p class="warning-detail">{{ detectedConflicts[0].message }}</p>
        </div>
      </div>

      <!-- Form Body -->
      <form class="modal-form" @submit.prevent="handleSubmit">
        <div class="form-sections">
          <!-- SECTION 1: ACADEMIC TIMING -->
          <div class="form-section">
            <h4 class="section-title">Academic Schedule & Timing</h4>
            <div class="form-grid">
              <!-- Academic Year -->
              <div class="form-group">
                <label class="form-label" for="slot-year">
                  Academic Year <span class="required">*</span>
                </label>
                <input
                  id="slot-year"
                  v-model="form.academic_year"
                  type="text"
                  class="form-input"
                  :class="{ 'has-error': formErrors.academic_year }"
                  placeholder="2026/2027"
                  @blur="runConflictCheck"
                />
              </div>

              <!-- Day of Week -->
              <div class="form-group">
                <label class="form-label" for="slot-day">
                  Day of Week <span class="required">*</span>
                </label>
                <select
                  id="slot-day"
                  v-model="form.day_of_week"
                  class="form-select"
                  @change="runConflictCheck"
                >
                  <option v-for="d in days" :key="d" :value="d">
                    {{ d }}
                  </option>
                </select>
              </div>

              <!-- Start Time -->
              <div class="form-group">
                <label class="form-label" for="slot-start">
                  Start Time <span class="required">*</span>
                </label>
                <input
                  id="slot-start"
                  v-model="form.start_time"
                  type="time"
                  class="form-input"
                  :class="{ 'has-error': formErrors.times }"
                  @change="runConflictCheck"
                />
              </div>

              <!-- End Time -->
              <div class="form-group">
                <label class="form-label" for="slot-end">
                  End Time <span class="required">*</span>
                </label>
                <input
                  id="slot-end"
                  v-model="form.end_time"
                  type="time"
                  class="form-input"
                  :class="{ 'has-error': formErrors.times }"
                  @change="runConflictCheck"
                />
              </div>

              <div v-if="formErrors.times" class="error-banner full-width">
                {{ formErrors.times }}
              </div>
            </div>
          </div>

          <!-- SECTION 2: CLASS, SUBJECT & TEACHER ASSIGNMENT -->
          <div class="form-section">
            <h4 class="section-title">Class & Faculty Allocation</h4>
            <div class="form-grid">
              <!-- Class Select -->
              <div class="form-group full-width">
                <label class="form-label" for="slot-class">
                  Academic Class <span class="required">*</span>
                </label>
                <select
                  id="slot-class"
                  v-model="form.class_id"
                  class="form-select"
                  :class="{ 'has-error': formErrors.class_id }"
                  @change="onClassChange"
                >
                  <option :value="0" disabled>Select class...</option>
                  <option v-for="c in classes" :key="c.id" :value="c.id">
                    {{ c.name }} ({{ c.code }}) - {{ c.academic_year }}
                  </option>
                </select>
                <span v-if="formErrors.class_id" class="error-msg">{{ formErrors.class_id }}</span>
              </div>

              <!-- Subject Select -->
              <div class="form-group full-width">
                <label class="form-label" for="slot-subject">
                  Curriculum Subject <span class="required">*</span>
                </label>
                <select
                  id="slot-subject"
                  v-model="form.subject_id"
                  class="form-select"
                  :class="{ 'has-error': formErrors.subject_id }"
                  @change="runConflictCheck"
                >
                  <option :value="0" disabled>Select subject...</option>
                  <option v-for="s in subjects" :key="s.id" :value="s.id">
                    {{ s.name }} ({{ s.code }})
                  </option>
                </select>
                <span v-if="formErrors.subject_id" class="error-msg">{{ formErrors.subject_id }}</span>
              </div>

              <!-- Faculty Teacher Select -->
              <div class="form-group full-width">
                <label class="form-label" for="slot-teacher">
                  Assigned Teacher / Faculty
                </label>
                <select
                  id="slot-teacher"
                  v-model="form.teacher_id"
                  class="form-select"
                  @change="runConflictCheck"
                >
                  <option :value="0">-- No Teacher Assigned Yet --</option>
                  <option v-for="t in teachers" :key="t.id" :value="t.id">
                    {{ t.first_name }} {{ t.last_name }} ({{ t.teacher_number || 'Staff' }})
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- SECTION 3: ROOM & STATUS -->
          <div class="form-section">
            <h4 class="section-title">Facility & Status</h4>
            <div class="form-grid">
              <!-- Room -->
              <div class="form-group">
                <label class="form-label" for="slot-room">
                  Classroom / Laboratory
                </label>
                <input
                  id="slot-room"
                  v-model="form.room"
                  type="text"
                  list="rooms-datalist"
                  class="form-input"
                  placeholder="e.g. Room 101, Science Lab A"
                  @blur="runConflictCheck"
                />
                <datalist id="rooms-datalist">
                  <option v-for="r in rooms" :key="r" :value="r" />
                </datalist>
              </div>

              <!-- Status -->
              <div class="form-group">
                <label class="form-label" for="slot-status">
                  Slot Status
                </label>
                <select
                  id="slot-status"
                  v-model="form.status"
                  class="form-select"
                >
                  <option value="ACTIVE">Active</option>
                  <option value="INACTIVE">Inactive</option>
                </select>
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
            <span>{{ isSubmitting ? 'Saving...' : isEditing ? 'Update Schedule Slot' : 'Save Schedule' }}</span>
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
  max-width: 540px;
  max-height: 90vh;
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

.modal-conflict-warning {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: #fffbeb;
  border-bottom: 1px solid #fde68a;
}

.warning-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: #d97706;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.warning-texts {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.warning-heading {
  font-size: 0.75rem;
  font-weight: 700;
  color: #92400e;
}

.warning-detail {
  font-size: 0.75rem;
  color: #b45309;
  margin: 0;
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
.form-select {
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

.form-input:focus,
.form-select:focus {
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

.error-msg {
  font-size: 0.6875rem;
  color: var(--danger, #ef4444);
  font-weight: 500;
}

.error-banner {
  grid-column: 1 / -1;
  font-size: 0.75rem;
  color: var(--danger, #ef4444);
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
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

@media (max-width: 520px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
