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
  if (typeof window !== 'undefined' && window.innerWidth < 768) {
    viewMode.value = 'list';
  }
  loadData();
});
</script>

<template>
  <div class="portal-page">
    <!-- Today's Schedule Banner -->
    <div v-if="!isLoading" class="today-banner card">
      <div class="today-banner-icon">
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="today-banner-content">
        <h3 class="today-banner-title">
          Today: {{ todayName }}
        </h3>
        <p v-if="todayLessons.length > 0" class="today-banner-desc">
          You have <strong>{{ todayLessons.length }} lesson{{ todayLessons.length > 1 ? 's' : '' }}</strong> scheduled today.
        </p>
        <p v-else class="today-banner-desc text-free">
          🎉 You are free today! No lessons scheduled for {{ todayName }}.
        </p>
      </div>
    </div>
    <div class="page-header">
      <div>
        <h1 class="page-title">My Weekly Teaching Schedule</h1>
        <p class="page-subtitle">Your weekly schedule of lectures and classes across assigned grade levels.</p>
      </div>

      <div class="header-right-actions">
        <!-- View Toggle -->
        <div class="view-toggle-wrap">
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

        <div class="header-count-badge">
          Total Periods: <strong>{{ totalPeriods }}</strong>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-box card">
      <div class="spinner" />
      <span>Loading your personal timetable...</span>
    </div>

    <div v-else-if="timetable.length === 0" class="card empty-box">
      <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="empty-title">No Timetable Periods Scheduled</p>
      <p class="empty-desc">You do not have any timetable periods assigned yet.</p>
    </div>

    <!-- Mode 1: Week Grid Layout -->
    <div v-else-if="viewMode === 'week'" class="weekly-schedule-grid">
      <div v-for="day in daysOfWeek" :key="day" class="day-card card">
        <div class="day-header">
          <h3 class="day-name">{{ day }}</h3>
          <span class="day-badge">{{ (groupedByDay[day] || []).length }} Periods</span>
        </div>

        <div v-if="!groupedByDay[day] || groupedByDay[day].length === 0" class="day-empty">
          No periods
        </div>

        <div v-else class="slots-list">
          <div v-for="s in groupedByDay[day]" :key="s.id" class="slot-item">
            <div class="slot-time">{{ s.start_time }} - {{ s.end_time }}</div>
            <div class="slot-subject">{{ s.subject_name }}</div>
            <div class="slot-details">
              <span class="class-text">{{ s.class_name }}</span>
              <span class="room-text">{{ s.room_number || 'Room TBD' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mode 2: Sequential List View (Mobile optimized) -->
    <div v-else class="sequential-day-list">
      <div v-for="day in daysOfWeek" :key="day" class="day-section-card card">
        <div class="day-section-header">
          <div class="day-title-wrap">
            <h3 class="day-heading">{{ day.toUpperCase() }}</h3>
            <span class="period-count-pill">{{ (groupedByDay[day] || []).length }} scheduled</span>
          </div>
        </div>

        <div v-if="!groupedByDay[day] || groupedByDay[day].length === 0" class="empty-day-inline">
          No scheduled periods for {{ day }}
        </div>

        <div v-else class="day-period-cards">
          <div v-for="s in groupedByDay[day]" :key="s.id" class="period-entry-card">
            <div class="period-time-badge">
              <svg class="clock-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ s.start_time }} - {{ s.end_time }}</span>
            </div>

            <div class="period-main-info">
              <h4 class="period-subject">{{ s.subject_name }}</h4>
              <div class="period-tags">
                <span class="class-badge">{{ s.class_name }}</span>
                <span class="room-badge">📍 {{ s.room_number || 'Room TBD' }}</span>
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
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-title { font-size: 1.5rem; font-weight: 800; color: var(--text-primary, #0f172a); margin: 0; word-break: break-word; }
.page-subtitle { font-size: 0.85rem; color: var(--text-muted, #64748b); margin-top: 0.2rem; }

.header-right-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.view-toggle-wrap {
  display: flex;
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.25rem;
  border-radius: 8px;
  gap: 0.25rem;
}
.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.75rem;
  font-size: 0.82rem;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  background: none;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  min-height: 38px;
  transition: all 0.2s;
}
.toggle-btn.active {
  background: #ffffff;
  color: #0284c7;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.icon-sm { width: 1.1rem; height: 1.1rem; }

.header-count-badge {
  background: #f1f5f9;
  color: #334155;
  padding: 0.4rem 0.85rem;
  border-radius: 20px;
  font-size: 0.85rem;
  white-space: nowrap;
}

/* Week Grid */
.weekly-schedule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
  width: 100%;
}
.day-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background: var(--bg-surface, #ffffff);
  border-top: 4px solid #0284c7;
  box-sizing: border-box;
}
.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  padding-bottom: 0.5rem;
}
.day-name { font-size: 1.05rem; font-weight: 700; margin: 0; color: var(--text-primary, #0f172a); }
.day-badge { font-size: 0.75rem; color: var(--text-muted, #64748b); font-weight: 600; }
.day-empty { font-size: 0.82rem; color: var(--text-muted, #64748b); font-style: italic; padding: 1.5rem 0; text-align: center; }

.slots-list { display: flex; flex-direction: column; gap: 0.65rem; }
.slot-item {
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #0284c7;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.slot-time { font-size: 0.78rem; font-weight: 700; color: #0284c7; }
.slot-subject { font-size: 0.9rem; font-weight: 700; color: var(--text-primary, #0f172a); word-break: break-word; }
.slot-details { display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-secondary, #475569); }
.class-text { font-weight: 600; }
.room-text { background: #f1f5f9; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.72rem; }

/* List View */
.sequential-day-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
}
.day-section-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
}
.day-section-header {
  border-bottom: 2px solid var(--border-subtle, #e2e8f0);
  padding-bottom: 0.6rem;
}
.day-title-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.day-heading {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 0;
  color: var(--brand-primary, #0284c7);
  letter-spacing: 0.04em;
}
.period-count-pill {
  font-size: 0.75rem;
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-weight: 700;
}
.empty-day-inline {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
  font-style: italic;
  padding: 0.75rem 0;
}
.day-period-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.period-entry-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-surface-secondary, #f8fafc);
  padding: 0.85rem 1rem;
  border-radius: 8px;
  border-left: 4px solid #0284c7;
  gap: 1rem;
  flex-wrap: wrap;
}
.period-time-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: #0284c7;
  min-width: 140px;
}
.clock-icon { width: 1.1rem; height: 1.1rem; flex-shrink: 0; }
.period-main-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  flex: 1;
  justify-content: space-between;
}
.period-subject {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #0f172a);
}
.period-tags {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}
.class-badge {
  background: #e0f2fe;
  color: #0369a1;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
}
.room-badge {
  background: #f1f5f9;
  color: #334155;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
}

.loading-box, .empty-box {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-muted, #64748b);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.empty-icon { width: 48px; height: 48px; color: #94a3b8; }
.empty-title { font-size: 1.1rem; font-weight: 700; margin: 0; color: var(--text-primary, #0f172a); }
.empty-desc { font-size: 0.85rem; margin: 0; }
.spinner { width: 32px; height: 32px; border: 3px solid var(--border-subtle, #e2e8f0); border-top-color: #0284c7; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .period-entry-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .period-main-info {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

.today-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: #ffffff;
  border-left: 4px solid var(--brand-primary, #0284c7);
  border-radius: 8px;
}

.today-banner-icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.5rem;
  background: #f0f9ff;
  color: #0284c7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.today-banner-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.today-banner-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.today-banner-desc {
  margin: 0.2rem 0 0 0;
  font-size: 0.85rem;
  color: #475569;
}

.text-free {
  color: #16a34a;
  font-weight: 600;
}
</style>
