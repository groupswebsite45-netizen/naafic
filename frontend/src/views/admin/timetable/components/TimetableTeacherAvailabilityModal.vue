<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Teacher, TeacherAvailability } from '../../../../types/school';
import { timetableService } from '../../../../services/timetableService';

const props = defineProps<{
  isOpen: boolean;
  teachers: Teacher[];
  academicYear: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'saved'): void;
}>();

const selectedTeacherId = ref<number | undefined>(undefined);
const isLoading = ref(false);
const isSaving = ref(false);
const successMessage = ref('');
const errorMessage = ref('');

const allDays = [
  'Saturday',
  'Sunday',
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday'
];

interface DayConfig {
  day_of_week: string;
  is_available: boolean;
  start_time: string;
  end_time: string;
  max_periods_per_day: number;
  notes: string;
}

const dayConfigs = reactive<Record<string, DayConfig>>({});

function initDays() {
  for (const day of allDays) {
    dayConfigs[day] = {
      day_of_week: day,
      is_available: day !== 'Friday', // Friday weekend default
      start_time: '07:30',
      end_time: '13:30',
      max_periods_per_day: 5,
      notes: ''
    };
  }
}
initDays();

watch(
  () => [props.isOpen, props.teachers],
  ([isOpen]) => {
    if (isOpen) {
      successMessage.value = '';
      errorMessage.value = '';
      if (!selectedTeacherId.value && props.teachers.length > 0) {
        selectedTeacherId.value = props.teachers[0].id;
      }
      if (selectedTeacherId.value) {
        loadAvailability(selectedTeacherId.value);
      }
    }
  },
  { immediate: true }
);

watch(
  () => selectedTeacherId.value,
  (newId) => {
    if (newId) {
      loadAvailability(newId);
    }
  }
);

async function loadAvailability(teacherId: number) {
  isLoading.value = true;
  errorMessage.value = '';
  initDays();
  try {
    const list: TeacherAvailability[] = await timetableService.getTeacherAvailability(
      teacherId,
      props.academicYear
    );
    for (const item of list) {
      if (dayConfigs[item.day_of_week]) {
        dayConfigs[item.day_of_week].is_available = item.is_available;
        if (item.start_time) dayConfigs[item.day_of_week].start_time = item.start_time.slice(0, 5);
        if (item.end_time) dayConfigs[item.day_of_week].end_time = item.end_time.slice(0, 5);
        if (item.max_periods_per_day) {
          dayConfigs[item.day_of_week].max_periods_per_day = item.max_periods_per_day;
        }
        if (item.notes) dayConfigs[item.day_of_week].notes = item.notes;
      }
    }
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load teacher availability.';
  } finally {
    isLoading.value = false;
  }
}

async function handleSave() {
  if (!selectedTeacherId.value) return;
  isSaving.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    const payloadList = Object.values(dayConfigs).map((c) => ({
      day_of_week: c.day_of_week,
      is_available: c.is_available,
      start_time: c.start_time,
      end_time: c.end_time,
      max_periods_per_day: c.max_periods_per_day,
      notes: c.notes || undefined
    }));

    await timetableService.setTeacherAvailability({
      teacher_id: selectedTeacherId.value,
      academic_year: props.academicYear,
      availabilities: payloadList
    });

    successMessage.value = 'Teacher availability updated and saved successfully.';
    emit('saved');
    setTimeout(() => {
      if (successMessage.value) successMessage.value = '';
    }, 3000);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save availability settings.';
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
    <div class="modal-dialog availability-modal" @click.stop>
      <!-- Header -->
      <div class="modal-header">
        <div class="header-title-wrap">
          <div class="header-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <polyline points="16 11 18 13 22 9" />
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Teacher Availability & Working Windows</h2>
            <p class="modal-subtitle">
              Configure available days, daily max lessons, and hours for automated scheduling.
            </p>
          </div>
        </div>
        <button type="button" class="btn-close" @click="emit('close')">&times;</button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- Teacher Selector Bar -->
        <div class="teacher-select-bar">
          <label class="bar-label">Select Teacher:</label>
          <select v-model="selectedTeacherId" class="teacher-select">
            <option v-for="t in teachers" :key="t.id" :value="t.id">
              {{ t.first_name }} {{ t.last_name }} ({{ t.employee_id || t.email || 'Teacher' }})
            </option>
          </select>
          <span class="year-pill">{{ academicYear }}</span>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="alert-box alert-success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="alert-box alert-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Loading spinner -->
        <div v-if="isLoading" class="loading-state">
          <div class="spinner" />
          <span>Loading teacher schedule availability...</span>
        </div>

        <!-- Availability Table -->
        <div v-else tabindex="0" role="region" aria-label="Teacher weekly availability matrix" class="availability-table-wrap">
          <table class="availability-table">
            <thead>
              <tr>
                <th style="width: 130px;">Day</th>
                <th style="width: 110px;">Status</th>
                <th>Working Hours</th>
                <th style="width: 140px;">Max Lessons / Day</th>
                <th>Notes / Exceptions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="day in allDays"
                :key="day"
                :class="{ 'day-unavailable-row': !dayConfigs[day]?.is_available }"
              >
                <td>
                  <strong>{{ day }}</strong>
                </td>
                <td>
                  <label class="toggle-switch">
                    <input v-model="dayConfigs[day].is_available" type="checkbox" />
                    <span class="toggle-slider" />
                    <span class="toggle-text">
                      {{ dayConfigs[day]?.is_available ? 'Available' : 'Unavailable' }}
                    </span>
                  </label>
                </td>
                <td>
                  <div class="time-range-group" :class="{ disabled: !dayConfigs[day]?.is_available }">
                    <input
                      v-model="dayConfigs[day].start_time"
                      type="time"
                      class="table-input"
                      :disabled="!dayConfigs[day]?.is_available"
                    />
                    <span>to</span>
                    <input
                      v-model="dayConfigs[day].end_time"
                      type="time"
                      class="table-input"
                      :disabled="!dayConfigs[day]?.is_available"
                    />
                  </div>
                </td>
                <td>
                  <input
                    v-model.number="dayConfigs[day].max_periods_per_day"
                    type="number"
                    min="1"
                    max="10"
                    class="table-input-number"
                    :disabled="!dayConfigs[day]?.is_available"
                  />
                </td>
                <td>
                  <input
                    v-model="dayConfigs[day].notes"
                    type="text"
                    placeholder="e.g. Leave early on Thursdays"
                    class="table-input-text"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button type="button" class="btn-secondary" @click="emit('close')">
          Close
        </button>
        <button
          type="button"
          class="btn-primary"
          :disabled="isSaving || !selectedTeacherId"
          @click="handleSave"
        >
          <div v-if="isSaving" class="spinner-sm" />
          <span v-else>Save Teacher Availability</span>
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

.modal-dialog.availability-modal {
  background: #ffffff;
  border-radius: var(--radius-xl, 1rem);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 880px;
  max-height: calc(100dvh - 1.5rem);
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
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.teacher-select-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  background: #f8fafc;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}

.bar-label {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
}

.teacher-select {
  flex: 1 1 200px;
  min-width: 0;
  width: 100%;
  padding: 0.45rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: #ffffff;
}

.year-pill {
  padding: 0.25rem 0.5rem;
  background: #e2e8f0;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
}

.alert-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
}

.alert-box svg {
  width: 1.125rem;
  height: 1.125rem;
}

.alert-box.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.alert-box.alert-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.availability-table-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.availability-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.availability-table th {
  background: #f8fafc;
  padding: 0.625rem 0.75rem;
  text-align: left;
  font-weight: 700;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.availability-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.day-unavailable-row {
  background: #f8fafc;
  color: #94a3b8;
}

.toggle-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
}

.toggle-text {
  font-size: 0.75rem;
  font-weight: 600;
}

.time-range-group {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
}

.time-range-group.disabled {
  opacity: 0.4;
}

.table-input {
  padding: 0.25rem 0.375rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.table-input-number {
  width: 4rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  text-align: center;
}

.table-input-text {
  width: 100%;
  padding: 0.25rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
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
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #cbd5e1;
  border-top-color: var(--brand-primary, #1e40af);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-sm {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
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
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
}
</style>
