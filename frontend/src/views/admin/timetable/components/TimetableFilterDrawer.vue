<script setup lang="ts">
import { ref, watch } from 'vue';
import { SchoolClass, Teacher, Subject } from '../../../../types/school';

const props = defineProps<{
  isOpen: boolean;
  academicYear: string;
  initialClassId?: number;
  initialTeacherId?: number;
  initialSubjectId?: number;
  initialDay?: string;
  initialRoom?: string;
  initialStatus?: string;
  classes: SchoolClass[];
  teachers: Teacher[];
  subjects: Subject[];
  days: string[];
  rooms: string[];
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (
    e: 'apply',
    filters: {
      classId?: number;
      teacherId?: number;
      subjectId?: number;
      day?: string;
      room?: string;
      status?: string;
    }
  ): void;
  (e: 'reset'): void;
}>();

const localClassId = ref<number | undefined>(props.initialClassId);
const localTeacherId = ref<number | undefined>(props.initialTeacherId);
const localSubjectId = ref<number | undefined>(props.initialSubjectId);
const localDay = ref<string | undefined>(props.initialDay);
const localRoom = ref<string | undefined>(props.initialRoom);
const localStatus = ref<string | undefined>(props.initialStatus);

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      localClassId.value = props.initialClassId;
      localTeacherId.value = props.initialTeacherId;
      localSubjectId.value = props.initialSubjectId;
      localDay.value = props.initialDay;
      localRoom.value = props.initialRoom;
      localStatus.value = props.initialStatus;
    }
  }
);

function handleApply() {
  emit('apply', {
    classId: localClassId.value,
    teacherId: localTeacherId.value,
    subjectId: localSubjectId.value,
    day: localDay.value,
    room: localRoom.value,
    status: localStatus.value,
  });
  emit('close');
}

function handleReset() {
  localClassId.value = undefined;
  localTeacherId.value = undefined;
  localSubjectId.value = undefined;
  localDay.value = undefined;
  localRoom.value = undefined;
  localStatus.value = undefined;
  emit('reset');
  emit('close');
}
</script>

<template>
  <div v-if="isOpen" class="drawer-overlay" @click.self="emit('close')">
    <div class="drawer-panel" role="dialog" aria-modal="true" aria-labelledby="timetable-drawer-title">
      <!-- Header -->
      <div class="drawer-header">
        <div class="header-title-group">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="header-icon">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          <h2 id="timetable-drawer-title" class="drawer-title">Filter Timetable</h2>
        </div>
        <button
          type="button"
          class="close-drawer-btn"
          title="Close filter drawer"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="drawer-body">
        <!-- Class Filter -->
        <div class="filter-group">
          <label class="filter-label">Academic Class</label>
          <select
            class="filter-select"
            :value="localClassId || ''"
            @change="localClassId = ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined"
          >
            <option value="">All Classes</option>
            <option v-for="c in classes" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.code }})
            </option>
          </select>
        </div>

        <!-- Teacher Filter -->
        <div class="filter-group">
          <label class="filter-label">Faculty Teacher</label>
          <select
            class="filter-select"
            :value="localTeacherId || ''"
            @change="localTeacherId = ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined"
          >
            <option value="">All Teachers</option>
            <option v-for="t in teachers" :key="t.id" :value="t.id">
              {{ t.first_name }} {{ t.last_name }}
            </option>
          </select>
        </div>

        <!-- Subject Filter -->
        <div class="filter-group">
          <label class="filter-label">Curriculum Subject</label>
          <select
            class="filter-select"
            :value="localSubjectId || ''"
            @change="localSubjectId = ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined"
          >
            <option value="">All Subjects</option>
            <option v-for="s in subjects" :key="s.id" :value="s.id">
              {{ s.name }} ({{ s.code }})
            </option>
          </select>
        </div>

        <!-- Day of Week Filter -->
        <div class="filter-group">
          <label class="filter-label">Day of Week</label>
          <select
            class="filter-select"
            :value="localDay || ''"
            @change="localDay = ($event.target as HTMLSelectElement).value || undefined"
          >
            <option value="">All Operating Days</option>
            <option v-for="d in days" :key="d" :value="d">
              {{ d }}
            </option>
          </select>
        </div>

        <!-- Room Filter -->
        <div class="filter-group">
          <label class="filter-label">Classroom / Facility</label>
          <select
            class="filter-select"
            :value="localRoom || ''"
            @change="localRoom = ($event.target as HTMLSelectElement).value || undefined"
          >
            <option value="">All Rooms & Labs</option>
            <option v-for="r in rooms" :key="r" :value="r">
              {{ r }}
            </option>
          </select>
        </div>
      </div>

      <!-- Footer -->
      <div class="drawer-footer">
        <button
          type="button"
          class="btn-reset"
          @click="handleReset"
        >
          Reset All
        </button>
        <div class="footer-actions-right">
          <button
            type="button"
            class="btn-cancel"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn-apply"
            @click="handleApply"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(3px);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease-out;
}

.drawer-panel {
  width: 100%;
  max-width: 380px;
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
  animation: slideLeft 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.125rem 1.25rem;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--brand-primary, #1e40af);
}

.drawer-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0;
}

.close-drawer-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: var(--radius-md, 0.5rem);
  background: none;
  border: 1px solid transparent;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.15s ease;
}

.close-drawer-btn:hover {
  background: #f1f5f9;
  color: var(--text-main, #0f172a);
}

.close-drawer-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-main, #1e293b);
}

.filter-select {
  height: 2.5rem;
  padding: 0 2rem 0 0.75rem;
  font-size: 0.875rem;
  color: var(--text-main, #0f172a);
  background-color: #f8fafc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.filter-select:focus {
  background-color: #ffffff;
  border-color: var(--brand-primary, #1e40af);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color, #e2e8f0);
  background: #f8fafc;
  gap: 0.75rem;
}

.btn-reset {
  background: none;
  border: none;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.15s ease;
}

.btn-reset:hover {
  color: #ef4444;
  background: #fee2e2;
}

.footer-actions-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-cancel {
  height: 2.25rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-apply {
  height: 2.25rem;
  padding: 0 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-apply:hover {
  background: #1d4ed8;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideLeft {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
