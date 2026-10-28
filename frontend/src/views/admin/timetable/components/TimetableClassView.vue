<script setup lang="ts">
import { computed } from 'vue';
import { TimetableEntry, SchoolClass } from '../../../../types/school';
import TimetableScheduleCard from './TimetableScheduleCard.vue';

const props = defineProps<{
  entries: TimetableEntry[];
  classes: SchoolClass[];
  selectedClassId?: number;
  days: string[];
}>();

const emit = defineEmits<{
  (e: 'update:selectedClassId', id?: number): void;
  (e: 'edit', entry: TimetableEntry): void;
  (e: 'delete', entry: TimetableEntry): void;
  (e: 'addSlotForClass', payload: { classId: number; day?: string }): void;
}>();

const filteredClasses = computed(() => {
  if (props.selectedClassId) {
    return props.classes.filter((c) => c.id === props.selectedClassId);
  }
  return props.classes;
});

function getSlotsForClassAndDay(classId: number, day: string) {
  return props.entries
    .filter((e) => e.class_id === classId && e.day_of_week.toLowerCase() === day.toLowerCase())
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
}

function getClassTotalSlots(classId: number) {
  return props.entries.filter((e) => e.class_id === classId).length;
}
</script>

<template>
  <div class="class-view-container">
    <!-- Class Selector Bar -->
    <div class="class-selector-bar">
      <div class="selector-left">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="class-icon">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M6 6h10" />
          <path d="M6 10h10" />
        </svg>
        <span class="selector-label">Focus Class:</span>
        <select
          class="class-select"
          :value="selectedClassId || ''"
          @change="emit('update:selectedClassId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined)"
        >
          <option value="">All Academic Classes</option>
          <option v-for="c in classes" :key="c.id" :value="c.id">
            {{ c.name }} ({{ c.code }})
          </option>
        </select>
      </div>

      <button
        v-if="selectedClassId"
        type="button"
        class="add-class-slot-btn"
        @click="emit('addSlotForClass', { classId: selectedClassId })"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Add Slot for this Class</span>
      </button>
    </div>

    <!-- Classes Schedule Panels -->
    <div class="classes-list-stack">
      <div
        v-for="c in filteredClasses"
        :key="c.id"
        class="class-schedule-panel"
      >
        <!-- Panel Header -->
        <div class="panel-header">
          <div class="panel-title-group">
            <h3 class="panel-class-name">{{ c.name }}</h3>
            <span class="class-code-badge">{{ c.code }}</span>
            <span class="slot-count-badge">
              {{ getClassTotalSlots(c.id) }} Weekly Periods
            </span>
          </div>

          <button
            type="button"
            class="btn-add-slot-sm"
            @click="emit('addSlotForClass', { classId: c.id })"
          >
            + Add Period
          </button>
        </div>

        <!-- Days Grid for this Class -->
        <div class="class-days-grid">
          <div
            v-for="day in days"
            :key="day"
            class="class-day-card"
          >
            <div class="day-card-header">
              <span class="day-label">{{ day }}</span>
              <span class="day-slot-count">
                {{ getSlotsForClassAndDay(c.id, day).length }}
              </span>
            </div>

            <div class="day-card-body">
              <div
                v-if="getSlotsForClassAndDay(c.id, day).length === 0"
                class="empty-class-day"
                @click="emit('addSlotForClass', { classId: c.id, day })"
              >
                <span>No periods</span>
              </div>
              <div v-else class="slots-stack">
                <TimetableScheduleCard
                  v-for="slot in getSlotsForClassAndDay(c.id, day)"
                  :key="slot.id"
                  :entry="slot"
                  :compact="true"
                  @edit="emit('edit', slot)"
                  @delete="emit('delete', slot)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.class-view-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  box-sizing: border-box;
}

.class-selector-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1rem;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  flex-wrap: wrap;
}

.selector-left {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex: 1;
  min-width: 240px;
}

.class-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--brand-primary, #1e40af);
}

.selector-label {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  white-space: nowrap;
}

.class-select {
  height: 2.25rem;
  padding: 0 2rem 0 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  background-color: #f8fafc;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2364748b' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 0.8125rem;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  outline: none;
  appearance: none;
  cursor: pointer;
}

.add-class-slot-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.25rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-class-slot-btn:hover {
  background: #1d4ed8;
}

.add-class-slot-btn svg {
  width: 0.875rem;
  height: 0.875rem;
}

.classes-list-stack {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.class-schedule-panel {
  background: #ffffff;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1.25rem;
  background: #f8fafc;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.panel-title-group {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.panel-class-name {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.class-code-badge {
  font-family: monospace;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  color: #334155;
}

.slot-count-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: #ffffff;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid #e2e8f0;
}

.btn-add-slot-sm {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--brand-primary, #1e40af);
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.35rem 0.625rem;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-add-slot-sm:hover {
  background: #dbeafe;
}

.class-days-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
  background: #fbfcfe;
}

.class-day-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md, 0.5rem);
  display: flex;
  flex-direction: column;
  min-height: 180px;
}

.day-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.day-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #334155;
}

.day-slot-count {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #64748b;
}

.day-card-body {
  padding: 0.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-class-day {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #f1f5f9;
  border-radius: 0.375rem;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 1rem 0.5rem;
}

.empty-class-day:hover {
  background: #eff6ff;
  color: #1e40af;
  border-color: #bfdbfe;
}

.slots-stack {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
</style>
