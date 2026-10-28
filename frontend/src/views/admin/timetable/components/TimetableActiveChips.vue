<script setup lang="ts">
import { SchoolClass, Teacher, Subject } from '../../../../types/school';

const props = defineProps<{
  academicYear: string;
  selectedClassId?: number;
  selectedTeacherId?: number;
  selectedSubjectId?: number;
  selectedDay?: string;
  selectedRoom?: string;
  classes: SchoolClass[];
  teachers: Teacher[];
  subjects: Subject[];
}>();

const emit = defineEmits<{
  (e: 'removeClass'): void;
  (e: 'removeTeacher'): void;
  (e: 'removeSubject'): void;
  (e: 'removeDay'): void;
  (e: 'removeRoom'): void;
  (e: 'clearAll'): void;
}>();

function getClassName(id?: number) {
  if (!id) return '';
  const c = props.classes.find((x) => x.id === id);
  return c ? c.name : `Class ${id}`;
}

function getTeacherName(id?: number) {
  if (!id) return '';
  const t = props.teachers.find((x) => x.id === id);
  return t ? `${t.first_name} ${t.last_name}` : `Teacher ${id}`;
}

function getSubjectName(id?: number) {
  if (!id) return '';
  const s = props.subjects.find((x) => x.id === id);
  return s ? s.name : `Subject ${id}`;
}
</script>

<template>
  <div
    v-if="selectedClassId || selectedTeacherId || selectedSubjectId || selectedDay || selectedRoom"
    class="active-chips-bar"
  >
    <span class="chips-label">Active Filters:</span>

    <div class="chips-list">
      <!-- Class Chip -->
      <div v-if="selectedClassId" class="filter-chip">
        <span class="chip-key">Class:</span>
        <span class="chip-val">{{ getClassName(selectedClassId) }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove class filter"
          @click="emit('removeClass')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Teacher Chip -->
      <div v-if="selectedTeacherId" class="filter-chip">
        <span class="chip-key">Teacher:</span>
        <span class="chip-val">{{ getTeacherName(selectedTeacherId) }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove teacher filter"
          @click="emit('removeTeacher')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Subject Chip -->
      <div v-if="selectedSubjectId" class="filter-chip">
        <span class="chip-key">Subject:</span>
        <span class="chip-val">{{ getSubjectName(selectedSubjectId) }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove subject filter"
          @click="emit('removeSubject')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Day Chip -->
      <div v-if="selectedDay" class="filter-chip">
        <span class="chip-key">Day:</span>
        <span class="chip-val">{{ selectedDay }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove day filter"
          @click="emit('removeDay')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Room Chip -->
      <div v-if="selectedRoom" class="filter-chip">
        <span class="chip-key">Room:</span>
        <span class="chip-val">{{ selectedRoom }}</span>
        <button
          type="button"
          class="remove-chip-btn"
          title="Remove room filter"
          @click="emit('removeRoom')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      </div>

      <!-- Clear All Button -->
      <button
        type="button"
        class="clear-all-chips-btn"
        @click="emit('clearAll')"
      >
        Clear all
      </button>
    </div>
  </div>
</template>

<style scoped>
.active-chips-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.25rem 0.25rem;
  width: 100%;
  box-sizing: border-box;
}

.chips-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
  flex-shrink: 0;
}

.chips-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  height: 1.625rem;
  padding: 0 0.5rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #1e293b;
  box-sizing: border-box;
}

.chip-key {
  color: #64748b;
  font-weight: 500;
}

.chip-val {
  font-weight: 600;
}

.remove-chip-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  padding: 0;
  margin-left: 0.125rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  border-radius: 9999px;
  transition: all 0.15s ease;
}

.remove-chip-btn:hover {
  background: #cbd5e1;
  color: #0f172a;
}

.remove-chip-btn svg {
  width: 0.75rem;
  height: 0.75rem;
}

.clear-all-chips-btn {
  background: none;
  border: none;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s ease;
}

.clear-all-chips-btn:hover {
  color: #1d4ed8;
}
</style>
