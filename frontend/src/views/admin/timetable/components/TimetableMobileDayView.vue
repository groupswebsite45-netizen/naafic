<script setup lang="ts">
import { ref, computed } from 'vue';
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

const activeDay = ref(props.days[0] || 'Monday');

const daySlots = computed(() => {
  return props.entries
    .filter((e) => e.day_of_week.toLowerCase() === activeDay.value.toLowerCase())
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
});

function getDayCount(day: string) {
  return props.entries.filter((e) => e.day_of_week.toLowerCase() === day.toLowerCase()).length;
}
</script>

<template>
  <div class="mobile-day-view-card">
    <!-- Segmented Day Selector Bar -->
    <div class="day-segments-container">
      <div class="day-segments-scroll">
        <button
          v-for="day in days"
          :key="day"
          type="button"
          class="day-pill-btn"
          :class="{ active: activeDay === day }"
          @click="activeDay = day"
        >
          <span class="day-abbr">{{ day.slice(0, 3) }}</span>
          <span class="day-pill-count">{{ getDayCount(day) }}</span>
        </button>
      </div>
    </div>

    <!-- Active Day Header -->
    <div class="active-day-header">
      <div class="header-left">
        <h3 class="active-day-title">{{ activeDay }}</h3>
        <span class="active-day-subtitle">
          {{ daySlots.length }} {{ daySlots.length === 1 ? 'Period' : 'Periods' }} Scheduled
        </span>
      </div>

      <button
        type="button"
        class="add-slot-mobile-btn"
        @click="emit('addSlot', activeDay)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Add Period</span>
      </button>
    </div>

    <!-- Active Day Period List -->
    <div class="day-periods-stack">
      <div
        v-if="daySlots.length === 0"
        class="empty-mobile-day"
        @click="emit('addSlot', activeDay)"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        <p class="empty-day-msg">No classes scheduled on {{ activeDay }}</p>
        <span class="empty-action-hint">+ Tap here to add a class period</span>
      </div>

      <TimetableScheduleCard
        v-for="slot in daySlots"
        :key="slot.id"
        :entry="slot"
        @edit="emit('edit', slot)"
        @delete="emit('delete', slot)"
      />
    </div>
  </div>
</template>

<style scoped>
.mobile-day-view-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.day-segments-container {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
  padding-bottom: 0.5rem;
}

.day-segments-scroll {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  overflow-x: auto;
  max-width: 100%;
  width: 100%;
  -webkit-overflow-scrolling: touch;
  padding: 0.25rem 0.125rem;
  box-sizing: border-box;
}

.day-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 0.625rem;
  border-radius: 9999px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.day-pill-btn.active {
  background: var(--brand-primary, #1e40af);
  border-color: var(--brand-primary, #1e40af);
  color: #ffffff;
}

.day-pill-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  font-size: 0.625rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.08);
}

.day-pill-btn.active .day-pill-count {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.active-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.active-day-title {
  font-size: 1.125rem;
  font-weight: 800;
  color: var(--text-main, #0f172a);
  margin: 0;
}

.active-day-subtitle {
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
}

.add-slot-mobile-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
}

.add-slot-mobile-btn svg {
  width: 0.8125rem;
  height: 0.8125rem;
}

.day-periods-stack {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.empty-mobile-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  border: 1px dashed #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  text-align: center;
  color: #64748b;
  cursor: pointer;
  background: #f8fafc;
}

.empty-mobile-day svg {
  width: 2rem;
  height: 2rem;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}

.empty-day-msg {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin: 0 0 0.25rem 0;
}

.empty-action-hint {
  font-size: 0.75rem;
  color: var(--brand-primary, #1e40af);
  font-weight: 600;
}
</style>
