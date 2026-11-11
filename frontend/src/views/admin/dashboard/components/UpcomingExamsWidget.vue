<script setup lang="ts">
import { computed } from 'vue';
import { Exam } from '../../../../types/school';

interface Props {
  exams?: Exam[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  exams: () => [],
  loading: false,
});

const displayedExams = computed(() => {
  return props.exams.slice(0, 4);
});

function formatExamDate(dateStr?: string | null) {
  if (!dateStr) return 'TBD';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  } catch {
    return dateStr;
  }
}
</script>

<template>
  <div class="dashboard-widget exams-widget">
    <div class="widget-header">
      <div class="widget-title-group">
        <div class="widget-icon-box orange">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
        </div>
        <div>
          <h3 class="widget-title">Upcoming Exams</h3>
          <p class="widget-sub">Scheduled institutional assessments</p>
        </div>
      </div>
      <router-link to="/admin/exams" class="widget-link">
        View All &rarr;
      </router-link>
    </div>

    <!-- Exam List -->
    <div v-if="displayedExams.length > 0" class="exams-list">
      <div
        v-for="exam in displayedExams"
        :key="exam.id"
        class="exam-row-item"
      >
        <div class="exam-main-info">
          <h4 class="exam-name">{{ exam.name }}</h4>
          <div class="exam-tags">
            <span class="exam-type-pill">{{ exam.exam_type }}</span>
            <span class="exam-year-tag">{{ exam.academic_year }}</span>
          </div>
        </div>

        <div class="exam-date-status">
          <span class="exam-date">{{ formatExamDate(exam.start_date) }}</span>
          <span
            class="exam-status-badge"
            :class="exam.status.toLowerCase()"
          >
            {{ exam.status }}
          </span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-exams-box">
      <div class="empty-calendar-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
      </div>
      <div class="empty-text-wrap">
        <h4 class="empty-heading">No upcoming exams scheduled</h4>
        <p class="empty-detail">
          New examination timetables will appear here once created.
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

.widget-icon-box.orange {
  background-color: #fff7ed;
  color: #ea580c;
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
  display: inline-flex;
  align-items: center;
  min-height: 28px;
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

/* Exams List */
.exams-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.exam-row-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  padding: 0.85rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  transition: background-color 0.15s ease;
}

.exam-row-item:hover {
  background-color: #f1f5f9;
}

.exam-main-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.exam-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.exam-tags {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.exam-type-pill {
  font-size: 0.7rem;
  font-weight: 600;
  color: #0369a1;
  background-color: #e0f2fe;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
}

.exam-year-tag {
  font-size: 0.725rem;
  color: #64748b;
}

.exam-date-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  flex-shrink: 0;
}

.exam-date {
  font-size: 0.775rem;
  font-weight: 600;
  color: #334155;
}

.exam-status-badge {
  font-size: 0.675rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
}

.exam-status-badge.scheduled {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.exam-status-badge.ongoing {
  background-color: #fefce8;
  color: #ca8a04;
  border: 1px solid #fef08a;
}

.exam-status-badge.completed {
  background-color: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}

/* Empty State */
.empty-exams-box {
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  padding: 1.15rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.empty-calendar-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #fff7ed;
  color: #ea580c;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.empty-calendar-icon svg {
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

@media (max-width: 480px) {
  .exam-name {
    white-space: normal;
    overflow: visible;
    text-overflow: unset;
    overflow-wrap: break-word;
    word-break: normal;
  }

  .exam-date-status {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    width: 100%;
  }

  .empty-exams-box {
    flex-wrap: wrap;
  }
}
</style>
