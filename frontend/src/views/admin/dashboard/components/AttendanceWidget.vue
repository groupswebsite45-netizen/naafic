<script setup lang="ts">
interface AttendanceStats {
  presentCount: number;
  absentCount: number;
  totalMarked: number;
}

interface Props {
  attendanceData?: AttendanceStats | null;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  attendanceData: null,
  loading: false,
});
</script>

<template>
  <div class="dashboard-widget attendance-widget">
    <div class="widget-header">
      <div class="widget-title-group">
        <div class="widget-icon-box cyan">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            <polyline points="9 14 11 16 15 11"></polyline>
          </svg>
        </div>
        <div>
          <h3 class="widget-title">Today's Attendance</h3>
          <p class="widget-sub">Daily student presence tracking</p>
        </div>
      </div>
      <router-link to="/admin/teachers" class="widget-link">
        Faculty Portal &rarr;
      </router-link>
    </div>

    <!-- State when real attendance is recorded -->
    <div v-if="attendanceData && attendanceData.totalMarked > 0" class="attendance-stats-grid">
      <div class="stat-pill present">
        <span class="pill-label">Present</span>
        <span class="pill-count">{{ attendanceData.presentCount }}</span>
      </div>
      <div class="stat-pill absent">
        <span class="pill-label">Absent</span>
        <span class="pill-count">{{ attendanceData.absentCount }}</span>
      </div>
      <div class="stat-pill total">
        <span class="pill-label">Total Marked</span>
        <span class="pill-count">{{ attendanceData.totalMarked }}</span>
      </div>
    </div>

    <!-- Clean operational empty state when no attendance is marked yet -->
    <div v-else class="empty-attendance-box">
      <div class="empty-icon-circle" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <div class="empty-text-wrap">
        <h4 class="empty-heading">No attendance recorded yet today</h4>
        <p class="empty-detail">
          Teachers take session attendance from the Faculty Portal upon class commencement.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-widget {
  background-color: #ffffff;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.widget-title-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.widget-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.widget-icon-box.cyan {
  background-color: #ecfeff;
  color: #0891b2;
}

.widget-icon-box svg {
  width: 20px;
  height: 20px;
}

.widget-title {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.25;
}

.widget-sub {
  font-size: 0.775rem;
  color: #64748b;
  margin: 0;
}

.widget-link {
  font-size: 0.825rem;
  font-weight: 600;
  color: #0284c7;
  text-decoration: none;
  white-space: nowrap;
  transition: color 0.15s ease;
}

.widget-link:hover {
  color: #0369a1;
  text-decoration: underline;
}

/* Attendance Stats Grid */
.attendance-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.stat-pill {
  padding: 0.85rem 0.75rem;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.stat-pill.present {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #16a34a;
}

.stat-pill.absent {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.stat-pill.total {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}

.pill-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
}

.pill-count {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 1.35rem;
  font-weight: 700;
}

/* Empty State */
.empty-attendance-box {
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  padding: 1.15rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.empty-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #eff6ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.empty-icon-circle svg {
  width: 20px;
  height: 20px;
}

.empty-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.empty-heading {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.empty-detail {
  font-size: 0.775rem;
  color: #64748b;
  margin: 0;
  line-height: 1.35;
}
</style>
