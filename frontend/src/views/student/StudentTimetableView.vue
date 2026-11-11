<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { TimetableSlot } from '../../types/studentPortal';

const timetable = ref<TimetableSlot[]>([]);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const selectedDay = ref<string>('Monday');
const isLoading = ref(true);
const errorMessage = ref('');

const allDays = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

async function loadTimetable() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    timetable.value = await studentPortalService.getMyTimetable(selectedYear.value || undefined);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to retrieve weekly timetable.';
  } finally {
    isLoading.value = false;
  }
}

async function initPage() {
  try {
    academicYears.value = await studentPortalService.getAcademicYears();
    if (academicYears.value.length > 0) {
      selectedYear.value = academicYears.value[0];
    }
  } catch {
    academicYears.value = ['2025-2026'];
    selectedYear.value = '2025-2026';
  }

  // Set selectedDay to today if it's a weekday
  const todayName = new Date().toLocaleDateString('en-US', { weekday: 'long' });
  if (allDays.includes(todayName)) {
    selectedDay.value = todayName;
  }

  await loadTimetable();
}

const groupedByDay = computed(() => {
  const map: Record<string, TimetableSlot[]> = {};
  for (const day of allDays) {
    map[day] = timetable.value.filter((t) => t.day_of_week === day);
  }
  return map;
});

const currentDaySlots = computed(() => {
  return groupedByDay.value[selectedDay.value] || [];
});

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content-row">
        <div>
          <h1 class="page-title">My Weekly Timetable</h1>
          <p class="page-subtitle">Scheduled lecture periods, subject teachers, and classroom locations for your class.</p>
        </div>

        <!-- Academic Year Selector -->
        <div v-if="academicYears.length > 0" class="year-selector-wrap">
          <label for="timetable-year-select" class="selector-lbl">Academic Year:</label>
          <select
            id="timetable-year-select"
            v-model="selectedYear"
            class="year-select"
            @change="loadTimetable"
          >
            <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Loading class schedule from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Timetable</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadTimetable">Try Again</button>
    </div>

    <div v-else-if="timetable.length === 0" class="card empty-card">
      <div class="empty-icon-wrap">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 class="empty-title">No Timetable Periods Scheduled</h3>
      <p class="empty-desc">There are no active timetable schedule entries for your class in academic year {{ selectedYear }}.</p>
    </div>

    <div v-else class="timetable-content">
      <!-- Mobile Day Selector (Visible on <= 820px, hidden on desktop) -->
      <div class="mobile-day-selector card">
        <div class="selector-top">
          <span class="sel-label">Select Day:</span>
          <select v-model="selectedDay" class="mobile-select-dropdown">
            <option v-for="day in allDays" :key="day" :value="day">
              {{ day }} ({{ (groupedByDay[day] || []).length }} periods)
            </option>
          </select>
        </div>

        <!-- Horizontal Day Pills for Mobile Quick-Switching -->
        <div class="mobile-day-pills">
          <button
            v-for="day in allDays"
            :key="day"
            class="day-pill-btn"
            :class="{
              active: selectedDay === day,
              hasPeriods: (groupedByDay[day] || []).length > 0
            }"
            @click="selectedDay = day"
          >
            {{ day.slice(0, 3) }}
            <span v-if="(groupedByDay[day] || []).length > 0" class="pill-dot" />
          </button>
        </div>
      </div>

      <!-- Mobile Single-Day View -->
      <div class="mobile-single-day-view">
        <div class="single-day-header">
          <h3 class="single-day-title">{{ selectedDay }}</h3>
          <span class="day-count-badge">{{ currentDaySlots.length }} Periods</span>
        </div>

        <div v-if="currentDaySlots.length === 0" class="card empty-day-card">
          <p class="empty-msg">No classes scheduled on {{ selectedDay }}.</p>
        </div>

        <div v-else class="mobile-slots-stack">
          <div
            v-for="s in currentDaySlots"
            :key="s.id"
            class="card mobile-period-card"
            :class="{ 'break-slot': s.is_break }"
          >
            <div class="period-top-row">
              <span class="period-time">{{ s.start_time.slice(0, 5) }} – {{ s.end_time.slice(0, 5) }}</span>
              <span v-if="!s.is_break" class="room-pill">{{ s.room_number || s.room || 'Room TBD' }}</span>
              <span v-else class="break-pill">Break</span>
            </div>
            <h4 class="period-subject">
              {{ s.subject_name || s.subject?.name || (s.is_break ? 'Recess / Break' : 'Class Subject') }}
            </h4>
            <div v-if="!s.is_break" class="period-faculty">
              <span class="teacher-lbl">Teacher:</span>
              <strong class="teacher-name">
                {{ s.teacher_name || s.teacher?.full_name || (s.teacher ? `${s.teacher.first_name} ${s.teacher.last_name}` : 'Assigned Faculty') }}
              </strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop Weekly Grid (Visible on > 820px) -->
      <div class="desktop-weekly-grid">
        <div
          v-for="day in allDays"
          :key="day"
          class="card desktop-day-column"
          :class="{ hasSlots: (groupedByDay[day] || []).length > 0 }"
        >
          <div class="day-col-header">
            <h4 class="day-col-title">{{ day }}</h4>
            <span class="day-col-badge">{{ (groupedByDay[day] || []).length }}</span>
          </div>

          <div v-if="!groupedByDay[day] || groupedByDay[day].length === 0" class="day-col-empty">
            <span>No periods</span>
          </div>

          <div v-else class="day-col-slots">
            <div
              v-for="s in groupedByDay[day]"
              :key="s.id"
              class="desktop-slot-item"
              :class="{ 'desktop-break-slot': s.is_break }"
            >
              <div class="slot-time">{{ s.start_time.slice(0, 5) }} – {{ s.end_time.slice(0, 5) }}</div>
              <div class="slot-subject">
                {{ s.subject_name || s.subject?.name || (s.is_break ? 'Recess / Break' : 'Subject') }}
              </div>
              <div v-if="!s.is_break" class="slot-footer">
                <span class="slot-teacher">
                  {{ s.teacher_name || s.teacher?.full_name || (s.teacher ? `${s.teacher.first_name} ${s.teacher.last_name}` : 'Faculty') }}
                </span>
                <span class="slot-room">{{ s.room_number || s.room || 'Room' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portal-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.header-content-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
}

.selector-lbl {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.year-select {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.timetable-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Mobile Day Selector */
.mobile-day-selector {
  display: none;
  padding: 1rem;
  flex-direction: column;
  gap: 0.75rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.selector-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.sel-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
}

.mobile-select-dropdown {
  padding: 0.4rem 0.75rem;
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
}

.mobile-day-pills {
  display: flex;
  gap: 0.35rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.day-pill-btn {
  flex: 1;
  min-width: 44px;
  padding: 0.45rem 0.25rem;
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  transition: all 0.15s ease;
}

.day-pill-btn.active {
  background: #10b981;
  color: #fff;
  border-color: #10b981;
}

.pill-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #0284c7;
}

.day-pill-btn.active .pill-dot {
  background: #fff;
}

/* Mobile Single Day View */
.mobile-single-day-view {
  display: none;
  flex-direction: column;
  gap: 0.85rem;
}

.single-day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.single-day-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.day-count-badge {
  font-size: 0.75rem;
  font-weight: 700;
  background-color: var(--bg-surface-secondary);
  color: var(--text-muted);
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
}

.empty-day-card {
  padding: 2.5rem 1rem;
  text-align: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
}

.empty-msg {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-style: italic;
  margin: 0;
}

.mobile-slots-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-period-card {
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left: 4px solid #10b981;
}

.period-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.period-time {
  font-size: 0.82rem;
  font-weight: 800;
  color: #10b981;
}

.room-pill {
  background-color: var(--bg-surface-secondary);
  color: var(--text-secondary);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.72rem;
}

.period-subject {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.period-faculty {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
}

.teacher-lbl {
  color: var(--text-muted);
}

.teacher-name {
  color: var(--text-primary);
}

/* Desktop Weekly Grid */
.desktop-weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.75rem;
}

.desktop-day-column {
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  min-height: 380px;
}

.day-col-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 0.5rem;
}

.day-col-title {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.day-col-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
}

.day-col-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  font-style: italic;
}

.day-col-slots {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.desktop-slot-item {
  background: var(--bg-surface-secondary);
  border-left: 3px solid #10b981;
  padding: 0.6rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  transition: transform 0.15s ease;
}

.desktop-slot-item:hover {
  transform: translateY(-1px);
}

.slot-time {
  font-size: 0.72rem;
  font-weight: 800;
  color: #10b981;
}

.slot-subject {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.25;
}

.slot-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.slot-teacher {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 85px;
}

.slot-room {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  font-size: 0.68rem;
}

/* Common states */
.loading-card, .error-card, .empty-card {
  padding: 3.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle);
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-icon-wrap {
  width: 52px;
  height: 52px;
  background-color: var(--bg-surface-secondary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--text-muted);
}

.empty-title, .error-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.empty-desc, .error-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

.retry-btn {
  background-color: #0f172a;
  color: #fff;
  border: 1px solid #334155;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

/* Responsive threshold for Mobile Timetable */
@media (max-width: 900px) {
  .desktop-weekly-grid {
    display: none;
  }
  .mobile-day-selector {
    display: flex;
  }
  .mobile-single-day-view {
    display: flex;
  }
}
</style>
