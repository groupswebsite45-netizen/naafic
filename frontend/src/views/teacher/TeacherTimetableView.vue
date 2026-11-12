<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { teacherPortalService } from '../../services/teacherPortalService';
import { TimetableEntry } from '../../types/school';

const timetable = ref<TimetableEntry[]>([]);
const isLoading = ref(true);
const daysOfWeek = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

// View mode: 'list' or 'week'
const viewMode = ref<'week' | 'list'>('week');

const todayName = computed(() => new Date().toLocaleDateString('en-US', { weekday: 'long' }));

const todayLessons = computed(() => {
  return timetable.value.filter((t) => t.day_of_week === todayName.value);
});

async function loadData() {
  isLoading.value = true;
  try {
    timetable.value = await teacherPortalService.getMyTimetable();
  } catch (err) {
    console.error('Failed to load timetable', err);
  } finally {
    isLoading.value = false;
  }
}

const groupedByDay = computed(() => {
  const map: Record<string, TimetableEntry[]> = {};
  for (const day of daysOfWeek) {
    map[day] = timetable.value.filter((t) => t.day_of_week === day);
  }
  return map;
});

const totalPeriods = computed(() => timetable.value.length);

onMounted(() => {
  // Automatically default to list view on mobile screens
  if (typeof window !== 'undefined' && window.innerWidth < 900) {
    viewMode.value = 'list';
  }
  loadData();
});
</script>

<template>
  <div class="portal-page">
    <!-- Today's Schedule Banner -->
    <div v-if="!isLoading" class="today-banner">
      <div class="today-banner-icon">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="today-banner-content">
        <div class="today-tag">CURRENT DAY SCHEDULE</div>
        <h3 class="today-banner-title">
          Today: {{ todayName }}
        </h3>
        <p v-if="todayLessons.length > 0" class="today-banner-desc">
          You have <strong>{{ todayLessons.length }} teaching session{{ todayLessons.length > 1 ? 's' : '' }}</strong> scheduled today.
        </p>
        <p v-else class="today-banner-desc free">
          ✨ You are free today! No lectures or class periods scheduled for {{ todayName }}.
        </p>
      </div>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="somroyal-tag">
          <svg class="crown-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5m14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
          <span>WEEKLY TIMETABLE &bull; LECTURE PERIODS</span>
        </div>
        <h1 class="page-title">My Timetable</h1>
        <p class="page-subtitle">Weekly master schedule of lectures, classroom locations, and teaching periods.</p>
      </div>

      <div class="header-right-actions">
        <!-- View Toggle -->
        <div class="view-toggle-bar">
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            <span>List View</span>
          </button>
          <button
            class="toggle-btn"
            :class="{ active: viewMode === 'week' }"
            @click="viewMode = 'week'"
          >
            <svg class="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            <span>Week Grid</span>
          </button>
        </div>

        <div class="header-count-pill">
          <span class="count-lbl">Total Periods:</span>
          <strong class="count-val">{{ totalPeriods }}</strong>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="state-card loading">
      <div class="spinner-ring" />
      <span class="loading-label">Loading your personal timetable...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="timetable.length === 0" class="state-card empty">
      <div class="empty-icon-circle">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <h3 class="state-title">No Timetable Periods Scheduled</h3>
      <p class="state-desc">You do not have any teaching sessions assigned to the weekly master schedule yet.</p>
    </div>

    <!-- Mode 1: Week Grid Layout -->
    <div v-else-if="viewMode === 'week'" class="weekly-schedule-grid">
      <div
        v-for="day in daysOfWeek"
        :key="day"
        class="day-card"
        :class="{ 'is-today': day === todayName }"
      >
        <div class="day-header">
          <div class="day-title-row">
            <h3 class="day-name">{{ day }}</h3>
            <span v-if="day === todayName" class="today-indicator">TODAY</span>
          </div>
          <span class="day-badge">{{ (groupedByDay[day] || []).length }} Periods</span>
        </div>

        <div v-if="!groupedByDay[day] || groupedByDay[day].length === 0" class="day-empty">
          <span>No teaching periods</span>
        </div>

        <div v-else class="slots-list">
          <div v-for="s in groupedByDay[day]" :key="s.id" class="slot-item">
            <div class="slot-time-row">
              <span class="slot-time">⏰ {{ s.start_time }} &ndash; {{ s.end_time }}</span>
            </div>
            <h4 class="slot-subject">{{ s.subject_name }}</h4>
            <div class="slot-details">
              <span class="class-text">{{ s.class_name }}</span>
              <span class="room-text">{{ s.room_number || 'Room TBD' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mode 2: Sequential List View (Optimized for Mobile/Tablets) -->
    <div v-else class="sequential-day-list">
      <div
        v-for="day in daysOfWeek"
        :key="day"
        class="day-section-card"
        :class="{ 'is-today': day === todayName }"
      >
        <div class="day-section-header">
          <div class="day-title-wrap">
            <h3 class="day-heading">{{ day.toUpperCase() }}</h3>
            <span v-if="day === todayName" class="today-indicator">TODAY</span>
          </div>
          <span class="period-count-tag">
            {{ (groupedByDay[day] || []).length }} Scheduled Period{{ (groupedByDay[day] || []).length === 1 ? '' : 's' }}
          </span>
        </div>

        <div v-if="!groupedByDay[day] || groupedByDay[day].length === 0" class="list-empty-inline">
          No lecture sessions scheduled for {{ day }}.
        </div>

        <div v-else class="list-slots-grid">
          <div v-for="s in groupedByDay[day]" :key="s.id" class="list-slot-card">
            <div class="list-slot-time">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
              </svg>
              <span>{{ s.start_time }} &ndash; {{ s.end_time }}</span>
            </div>
            <div class="list-slot-main">
              <h4 class="list-subject">{{ s.subject_name }}</h4>
              <div class="list-meta">
                <span class="class-tag">{{ s.class_name }}</span>
                <span class="bullet">&bull;</span>
                <span class="room-tag">{{ s.room_number || 'Room TBD' }}</span>
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
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
}

/* Today Banner */
.today-banner {
  background: linear-gradient(135deg, #0A192F 0%, #0F2A4A 60%, #081528 100%);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: 0 10px 25px -5px rgba(10, 25, 47, 0.25);
  position: relative;
  overflow: hidden;
}

.today-banner::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 280px;
  background: radial-gradient(circle at right, rgba(16, 185, 129, 0.18) 0%, transparent 70%);
  pointer-events: none;
}

.today-banner-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
  flex-shrink: 0;
}

.today-banner-icon svg {
  width: 26px;
  height: 26px;
}

.today-tag {
  font-size: 0.68rem;
  font-weight: 800;
  color: #38BDF8;
  letter-spacing: 0.08em;
  margin-bottom: 0.25rem;
}

.today-banner-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0;
}

.today-banner-desc {
  font-size: 0.86rem;
  color: #94A3B8;
  margin-top: 0.25rem;
}

.today-banner-desc strong {
  color: #FFFFFF;
}

.today-banner-desc.free {
  color: #FDE68A;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.somroyal-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #38BDF8;
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}

.crown-icon {
  width: 14px;
  height: 14px;
  color: #F59E0B;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin-top: 0.25rem;
  line-height: 1.5;
}

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.view-toggle-bar {
  display: flex;
  gap: 0.25rem;
  background: #E2E8F0;
  padding: 0.25rem;
  border-radius: 12px;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: transparent;
  border: none;
  padding: 0.45rem 0.85rem;
  border-radius: 9px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #64748B;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: #FFFFFF;
  color: #0A192F;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.08);
}

.icon-sm {
  width: 15px;
  height: 15px;
}

.header-count-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.count-lbl {
  font-size: 0.78rem;
  color: #64748B;
  font-weight: 700;
}

.count-val {
  font-size: 1.15rem;
  color: #0A192F;
  font-weight: 900;
}

/* Week Grid */
.weekly-schedule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  align-items: start;
}

.day-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
  display: flex;
  flex-direction: column;
}

.day-card.is-today {
  border: 2px solid #2563EB;
}

.day-header {
  background: #0A192F;
  color: #FFFFFF;
  padding: 0.85rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.day-title-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.day-name {
  font-size: 0.95rem;
  font-weight: 800;
  margin: 0;
  color: #FFFFFF;
}

.today-indicator {
  font-size: 0.65rem;
  font-weight: 900;
  background: #2563EB;
  color: #FFFFFF;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.day-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: #94A3B8;
}

.day-empty {
  padding: 2.5rem 1rem;
  text-align: center;
  font-size: 0.78rem;
  color: #94A3B8;
  font-style: italic;
}

.slots-list {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.slot-item {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-left: 3px solid #2563EB;
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.slot-time {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748B;
}

.slot-subject {
  font-size: 0.88rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.slot-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.72rem;
  color: #475569;
}

.class-text {
  font-weight: 700;
  color: #2563EB;
}

.room-text {
  background: #E2E8F0;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

/* Sequential List Mode */
.sequential-day-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.day-section-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(10, 25, 47, 0.03);
}

.day-section-card.is-today {
  border-left: 4px solid #2563EB;
}

.day-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #F1F5F9;
}

.day-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.day-heading {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
  letter-spacing: 0.02em;
}

.period-count-tag {
  font-size: 0.76rem;
  font-weight: 700;
  color: #64748B;
  background: #F1F5F9;
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
}

.list-empty-inline {
  padding: 1.5rem 1rem;
  text-align: center;
  font-size: 0.84rem;
  color: #94A3B8;
  font-style: italic;
}

.list-slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.list-slot-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-left: 3px solid #2563EB;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-slot-time {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.76rem;
  font-weight: 700;
  color: #2563EB;
}

.list-slot-time svg {
  width: 14px;
  height: 14px;
}

.list-subject {
  font-size: 1rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.list-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #64748B;
}

.class-tag {
  font-weight: 700;
  color: #2563EB;
}

.room-tag {
  font-weight: 600;
  color: #475569;
}

.bullet { color: #CBD5E1; }

/* States */
.state-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  padding: 4rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
}

.spinner-ring {
  width: 36px;
  height: 36px;
  border: 3px solid #E2E8F0;
  border-top-color: #1E3A8A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-label {
  font-size: 0.88rem;
  color: #64748B;
  font-weight: 600;
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  background: #F1F5F9;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94A3B8;
}

.empty-icon-circle svg { width: 28px; height: 28px; }

.state-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0A192F;
  margin: 0;
}

.state-desc {
  font-size: 0.86rem;
  color: #64748B;
  max-width: 500px;
  line-height: 1.5;
  margin: 0;
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-right-actions {
    justify-content: space-between;
  }
}

@media (max-width: 640px) {
  .today-banner {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.25rem;
  }
  .view-toggle-bar {
    width: 100%;
  }
  .toggle-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
