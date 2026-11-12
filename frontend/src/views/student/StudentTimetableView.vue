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
    academicYears.value = ['2026/2027'];
    selectedYear.value = '2026/2027';
  }

  // Default to today if it's a weekday, otherwise Monday
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
  <div class="portal-page student-timetable-view">
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
          <div class="select-container">
            <select
              id="timetable-year-select"
              v-model="selectedYear"
              class="year-select"
              @change="loadTimetable"
            >
              <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
            </select>
            <svg class="select-chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
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
      <div class="error-icon-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
          <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
      <div class="error-content">
        <p class="error-title">Unable to Load Timetable</p>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button type="button" class="retry-btn" @click="loadTimetable">Try Again</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="timetable.length === 0" class="card empty-card">
      <div class="empty-icon-wrap">
        <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 class="empty-title">No Timetable Periods Scheduled</h3>
      <p class="empty-desc">There are no active timetable schedule entries for your class in academic year {{ selectedYear }}.</p>
    </div>

    <!-- Timetable Content Area -->
    <div v-else class="timetable-content">
      <!-- Mobile Day Selector (Visible on <= 900px, hidden on desktop) -->
      <div class="mobile-day-selector card">
        <div class="selector-top">
          <span class="sel-label">Select Day:</span>
          <div class="select-container compact">
            <select v-model="selectedDay" class="mobile-select-dropdown">
              <option v-for="day in allDays" :key="day" :value="day">
                {{ day }} ({{ (groupedByDay[day] || []).length }} periods)
              </option>
            </select>
            <svg class="select-chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <!-- Horizontal Day Pills for Mobile Quick-Switching -->
        <div class="mobile-day-pills">
          <button
            v-for="day in allDays"
            :key="day"
            type="button"
            class="day-pill-btn"
            :class="{
              active: selectedDay === day,
              hasPeriods: (groupedByDay[day] || []).length > 0
            }"
            @click="selectedDay = day"
          >
            <span>{{ day.slice(0, 3) }}</span>
            <span v-if="(groupedByDay[day] || []).length > 0" class="pill-dot" />
          </button>
        </div>
      </div>

      <!-- Mobile Single-Day View (Visible on <= 900px) -->
      <div class="mobile-single-day-view">
        <div class="single-day-header">
          <h3 class="single-day-title">{{ selectedDay }}'s Schedule</h3>
          <span class="day-count-badge">{{ currentDaySlots.length }} Periods</span>
        </div>

        <div v-if="currentDaySlots.length === 0" class="card empty-day-card">
          <div class="empty-icon-mini">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" stroke-width="2" />
              <polyline points="12 6 12 12 16 14" stroke-width="2" />
            </svg>
          </div>
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
              <div class="time-badge">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ s.start_time.slice(0, 5) }} – {{ s.end_time.slice(0, 5) }}</span>
              </div>
              <span v-if="!s.is_break" class="room-pill">{{ s.room_number || s.room || 'Room TBD' }}</span>
              <span v-else class="break-pill">Break / Recess</span>
            </div>

            <h4 class="period-subject">
              {{ s.subject_name || s.subject?.name || (s.is_break ? 'Recess / Interval' : 'Class Subject') }}
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

      <!-- Desktop Weekly Grid (Visible on > 900px) -->
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
            <span>No periods scheduled</span>
          </div>

          <div v-else class="day-col-slots">
            <div
              v-for="s in groupedByDay[day]"
              :key="s.id"
              class="desktop-slot-item"
              :class="{ 'desktop-break-slot': s.is_break }"
            >
              <div class="slot-time-pill">
                {{ s.start_time.slice(0, 5) }} – {{ s.end_time.slice(0, 5) }}
              </div>

              <div class="slot-subject-title">
                {{ s.subject_name || s.subject?.name || (s.is_break ? 'Recess / Break' : 'Subject') }}
              </div>

              <div v-if="!s.is_break" class="slot-meta-row">
                <span class="slot-teacher-name" :title="s.teacher_name || s.teacher?.full_name">
                  {{ s.teacher_name || s.teacher?.full_name || 'Faculty' }}
                </span>
                <span class="slot-room-badge">{{ s.room_number || s.room || 'Room' }}</span>
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
  width: 100%;
}

.page-header {
  margin-bottom: 0.25rem;
}

.header-content-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
}

.page-subtitle {
  font-size: 0.85rem;
  color: #64748B;
  margin: 0.25rem 0 0 0;
}

/* Academic Year Selector */
.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.selector-lbl {
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
}

.select-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.year-select,
.mobile-select-dropdown {
  appearance: none;
  background-color: #FFFFFF;
  border: 1px solid #CBD5E1;
  border-radius: 10px;
  padding: 0.45rem 2.25rem 0.45rem 0.85rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: #1E293B;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
}

.year-select:focus,
.mobile-select-dropdown:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.select-chevron {
  position: absolute;
  right: 0.65rem;
  width: 16px;
  height: 16px;
  color: #64748B;
  pointer-events: none;
}

/* Card Base */
.card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* Loading & Error */
.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3.5rem 1.5rem;
  color: #64748B;
  font-size: 0.88rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #1E3A8A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background-color: #FEF2F2;
  border-color: #FECACA;
  color: #991B1B;
}

.error-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #FEE2E2;
  color: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-icon-box svg {
  width: 22px;
  height: 22px;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}

.error-desc {
  font-size: 0.82rem;
  margin: 0.2rem 0 0 0;
  color: #B91C1C;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background-color: #DC2626;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

/* Empty Card */
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3.5rem 1.5rem;
  text-align: center;
}

.empty-icon-wrap {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #F1F5F9;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.85rem;
}

.empty-icon {
  width: 28px;
  height: 28px;
}

.empty-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 0.35rem 0;
}

.empty-desc {
  font-size: 0.82rem;
  color: #64748B;
  max-width: 420px;
  margin: 0;
}

/* Timetable Layouts */
.timetable-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Mobile Day Selector */
.mobile-day-selector {
  display: none;
  padding: 1.15rem;
  flex-direction: column;
  gap: 0.85rem;
}

.selector-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sel-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: #334155;
}

.mobile-day-pills {
  display: flex;
  gap: 0.45rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.day-pill-btn {
  flex: 1;
  min-width: 44px;
  padding: 0.55rem 0.4rem;
  border-radius: 10px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  color: #475569;
  font-size: 0.78rem;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.day-pill-btn:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
}

.day-pill-btn.active {
  background: #0A192F;
  border-color: #0A192F;
  color: #FFFFFF;
  box-shadow: 0 4px 10px rgba(10, 25, 47, 0.25);
}

.pill-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: #10B981;
}

.day-pill-btn.active .pill-dot {
  background-color: #34D399;
}

/* Mobile Single Day View */
.mobile-single-day-view {
  display: none;
  flex-direction: column;
  gap: 0.85rem;
}

.single-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.single-day-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
}

.day-count-badge {
  background: #ECFDF5;
  color: #065F46;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid #A7F3D0;
}

.empty-day-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748B;
}

.empty-icon-mini {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F1F5F9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.empty-icon-mini svg {
  width: 18px;
  height: 18px;
}

.empty-msg {
  font-size: 0.84rem;
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
  border-left: 4px solid #2563EB;
}

.mobile-period-card.break-slot {
  border-left-color: #F59E0B;
  background: #FFFBEB;
}

.period-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.time-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #ECFDF5;
  color: #065F46;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  border: 1px solid #A7F3D0;
}

.room-pill {
  background: #F1F5F9;
  border: 1px solid #E2E8F0;
  color: #334155;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.break-pill {
  background: #FEF3C7;
  color: #B45309;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.period-subject {
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.period-faculty {
  font-size: 0.8rem;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.teacher-name {
  color: #1E293B;
}

/* Desktop Weekly Grid (7 Columns) */
.desktop-weekly-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.85rem;
  align-items: start;
}

.desktop-day-column {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 280px;
}

.day-col-header {
  padding: 0.75rem 0.85rem;
  background-color: #F8FAFC;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.day-col-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.day-col-badge {
  font-size: 0.68rem;
  font-weight: 700;
  background: #E2E8F0;
  color: #475569;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.desktop-day-column.hasSlots .day-col-header {
  background-color: #0A192F;
}

.desktop-day-column.hasSlots .day-col-title {
  color: #FFFFFF;
}

.desktop-day-column.hasSlots .day-col-badge {
  background: #2563EB;
  color: #FFFFFF;
}

.day-col-empty {
  padding: 2.5rem 0.75rem;
  text-align: center;
  color: #94A3B8;
  font-size: 0.74rem;
  font-style: italic;
}

.day-col-slots {
  padding: 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.desktop-slot-item {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-left: 3px solid #2563EB;
  border-radius: 8px;
  padding: 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  transition: all 0.15s ease;
}

.desktop-slot-item:hover {
  background: #FFFFFF;
  border-color: #CBD5E1;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.desktop-break-slot {
  background: #FFFBEB;
  border-color: #FDE68A;
  border-left-color: #F59E0B;
}

.slot-time-pill {
  font-size: 0.68rem;
  font-weight: 700;
  color: #2563EB;
  line-height: 1.1;
}

.slot-subject-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #0F172A;
  line-height: 1.25;
}

.slot-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
  font-size: 0.68rem;
}

.slot-teacher-name {
  color: #64748B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 85px;
}

.slot-room-badge {
  background: #FFFFFF;
  border: 1px solid #CBD5E1;
  color: #334155;
  font-weight: 600;
  padding: 0.05rem 0.3rem;
  border-radius: 4px;
}

/* Responsive Media Queries */
@media (max-width: 900px) {
  .desktop-weekly-grid {
    display: none;
  }
  .mobile-day-selector,
  .mobile-single-day-view {
    display: flex;
  }
}

@media (max-width: 640px) {
  .header-content-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .year-selector-wrap {
    width: 100%;
    justify-content: space-between;
  }
  .select-container {
    flex: 1;
  }
  .year-select {
    width: 100%;
  }
}
</style>
