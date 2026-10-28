<script setup lang="ts">
import { computed } from 'vue';
import { TimetableEntry } from '../../../../types/school';
import TimetableScheduleCard from './TimetableScheduleCard.vue';

const props = defineProps<{
  entries: TimetableEntry[];
  days: string[];
}>();

const emit = defineEmits<{
  (e: 'edit', entry: TimetableEntry): void;
  (e: 'delete', entry: TimetableEntry): void;
  (e: 'addSlot', day: string): void;
}>();

// Group entries by day of week, sorted by start_time
const groupedEntries = computed(() => {
  const map: Record<string, TimetableEntry[]> = {};
  for (const day of props.days) {
    map[day] = props.entries
      .filter((e) => e.day_of_week.toLowerCase() === day.toLowerCase())
      .sort((a, b) => a.start_time.localeCompare(b.start_time));
  }
  return map;
});
</script>

<template>
  <div class="weekly-grid-container">
    <div class="grid-table-wrap">
      <div class="weekly-days-grid" :style="{ '--col-count': days.length }">
        <!-- Day Columns -->
        <div
          v-for="day in days"
          :key="day"
          class="day-column"
        >
          <!-- Day Header -->
          <div class="day-column-header">
            <div class="day-title-wrap">
              <span class="day-name">{{ day }}</span>
              <span class="day-count-badge">
                {{ groupedEntries[day]?.length || 0 }}
              </span>
            </div>
            <button
              type="button"
              class="quick-add-day-btn"
              :title="`Add timetable slot for ${day}`"
              @click="emit('addSlot', day)"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </button>
          </div>

          <!-- Day Slots Body -->
          <div class="day-column-body">
            <!-- Empty state for day -->
            <div
              v-if="!groupedEntries[day] || groupedEntries[day].length === 0"
              class="empty-day-cell"
              @click="emit('addSlot', day)"
            >
              <span class="empty-plus">+</span>
              <span class="empty-text">No classes scheduled</span>
            </div>

            <!-- List of schedule cards for this day -->
            <div v-else class="cards-stack">
              <TimetableScheduleCard
                v-for="slot in groupedEntries[day]"
                :key="slot.id"
                :entry="slot"
                @edit="emit('edit', slot)"
                @delete="emit('delete', slot)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weekly-grid-container {
  width: 100%;
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  box-sizing: border-box;
}

.grid-table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.weekly-days-grid {
  display: grid;
  grid-template-columns: repeat(var(--col-count, 6), minmax(180px, 1fr));
  min-width: 100%;
  box-sizing: border-box;
}

.day-column {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color, #e2e8f0);
  background: #ffffff;
  min-height: 480px;
}

.day-column:last-child {
  border-right: none;
}

.day-column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.875rem;
  background: #f8fafc;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  position: sticky;
  top: 0;
  z-index: 10;
}

.day-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.day-name {
  font-size: 0.8125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #0f172a;
}

.day-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.05rem 0.375rem;
  font-size: 0.6875rem;
  font-weight: 700;
  background: #e2e8f0;
  color: #334155;
  border-radius: 9999px;
}

.quick-add-day-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.375rem;
  height: 1.375rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.12s ease;
}

.quick-add-day-btn:hover {
  background: var(--brand-primary, #1e40af);
  border-color: var(--brand-primary, #1e40af);
  color: #ffffff;
}

.quick-add-day-btn svg {
  width: 0.75rem;
  height: 0.75rem;
}

.day-column-body {
  padding: 0.625rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fbfcfe;
}

.empty-day-cell {
  flex: 1;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  border: 1px dashed #e2e8f0;
  border-radius: var(--radius-md, 0.5rem);
  padding: 1rem 0.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s ease;
  background: #ffffff;
}

.empty-day-cell:hover {
  border-color: #93c5fd;
  background: #eff6ff;
  color: #1e40af;
}

.empty-plus {
  font-size: 1.25rem;
  line-height: 1;
  font-weight: 600;
}

.empty-text {
  font-size: 0.6875rem;
  text-align: center;
}

.cards-stack {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
