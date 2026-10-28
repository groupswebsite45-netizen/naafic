<script setup lang="ts">
import { ClassSubjectMatrixItem } from '../../types/resultWorkflow';
import ResultStatusBadge from './ResultStatusBadge.vue';

interface Props {
  subjects: ClassSubjectMatrixItem[];
  isLoading?: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'review', subject: ClassSubjectMatrixItem): void;
}>();
</script>

<template>
  <div class="matrix-container">
    <!-- Desktop & Tablet Matrix Table -->
    <div class="table-wrapper desktop-only">
      <table class="matrix-table" aria-label="Class Subject Results Matrix">
        <thead>
          <tr>
            <th scope="col">SUBJECT</th>
            <th scope="col">TEACHER</th>
            <th scope="col" class="text-center">STUDENTS</th>
            <th scope="col" class="text-center">ATTENDED</th>
            <th scope="col" class="text-center">ENTERED</th>
            <th scope="col" class="text-center">SUBMITTED</th>
            <th scope="col" class="text-center">APPROVED</th>
            <th scope="col" class="text-center">RELEASED</th>
            <th scope="col" class="text-center">PENDING</th>
            <th scope="col" class="text-center">ABSENT</th>
            <th scope="col" class="text-center">STATUS</th>
            <th scope="col" class="text-right">ACTION</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="12" class="loading-cell">
              <div class="table-skeleton-row" />
              <div class="table-skeleton-row" />
              <div class="table-skeleton-row" />
            </td>
          </tr>
          <tr v-else-if="subjects.length === 0">
            <td colspan="12" class="empty-cell">
              No subjects scheduled for this examination in this class.
            </td>
          </tr>
          <tr v-for="subj in subjects" :key="subj.subject_id" class="matrix-row">
            <td class="subject-cell">
              <div class="subject-name">{{ subj.subject_name }}</div>
              <div class="subject-code">{{ subj.subject_code }}</div>
            </td>
            <td class="teacher-cell">
              <div class="teacher-name">{{ subj.teacher_name }}</div>
              <div v-if="subj.teacher_email" class="teacher-sub">{{ subj.teacher_email }}</div>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val">{{ subj.expected_students }}</span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val">{{ subj.attended_students }}</span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val" :class="{ 'highlight-amber': subj.marks_entered < subj.expected_students }">
                {{ subj.marks_entered }}
              </span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val">{{ subj.marks_submitted }}</span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val" :class="{ 'highlight-blue': subj.marks_approved > 0 }">
                {{ subj.marks_approved }}
              </span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val" :class="{ 'highlight-emerald': subj.marks_released > 0 }">
                {{ subj.marks_released }}
              </span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val" :class="{ 'highlight-red': subj.pending_students > 0 }">
                {{ subj.pending_students }}
              </span>
            </td>
            <td class="text-center metric-cell">
              <span class="metric-val" :class="{ 'text-muted': subj.absent_students === 0 }">
                {{ subj.absent_students }}
              </span>
            </td>
            <td class="text-center">
              <ResultStatusBadge :status="subj.status" size="sm" />
            </td>
            <td class="text-right">
              <button
                v-if="subj.submission_id"
                type="button"
                class="action-btn"
                @click="emit('review', subj)"
              >
                Inspect
              </button>
              <span v-else class="action-none">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Responsive Cards (under 640px) -->
    <div class="mobile-only mobile-card-list">
      <div v-if="isLoading" class="mobile-skeleton-wrap">
        <div class="mobile-skeleton" />
        <div class="mobile-skeleton" />
      </div>
      <div v-else-if="subjects.length === 0" class="empty-cell">
        No subjects scheduled for this examination in this class.
      </div>
      <div
        v-for="subj in subjects"
        :key="`mob-${subj.subject_id}`"
        class="mobile-subject-card"
      >
        <div class="mobile-card-top">
          <div>
            <h4 class="mobile-subj-title">{{ subj.subject_name }}</h4>
            <span class="mobile-subj-teacher">{{ subj.teacher_name }}</span>
          </div>
          <ResultStatusBadge :status="subj.status" size="sm" />
        </div>

        <div class="mobile-metrics-grid">
          <div class="metric-box">
            <span class="metric-box-label">Students</span>
            <span class="metric-box-val">{{ subj.expected_students }}</span>
          </div>
          <div class="metric-box">
            <span class="metric-box-label">Entered</span>
            <span class="metric-box-val">{{ subj.marks_entered }} / {{ subj.expected_students }}</span>
          </div>
          <div class="metric-box">
            <span class="metric-box-label">Approved</span>
            <span class="metric-box-val">{{ subj.marks_approved }}</span>
          </div>
          <div class="metric-box">
            <span class="metric-box-label">Pending</span>
            <span class="metric-box-val" :class="{ 'highlight-red': subj.pending_students > 0 }">
              {{ subj.pending_students }}
            </span>
          </div>
        </div>

        <div v-if="subj.submission_id" class="mobile-card-actions">
          <button
            type="button"
            class="action-btn mobile-full-btn"
            @click="emit('review', subj)"
          >
            Review Submission
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.matrix-container {
  width: 100%;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.8125rem;
}

.matrix-table th {
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.matrix-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #334155;
  color: #f1f5f9;
  vertical-align: middle;
}

.matrix-row:hover {
  background-color: rgba(51, 65, 85, 0.4);
}

.subject-cell {
  min-width: 160px;
}

.subject-name {
  font-weight: 700;
  color: #ffffff;
}

.subject-code {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.teacher-cell {
  min-width: 150px;
}

.teacher-name {
  font-weight: 600;
  color: #cbd5e1;
}

.teacher-sub {
  font-size: 0.6875rem;
  color: #64748b;
}

.metric-cell {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.metric-val {
  color: #e2e8f0;
}

.highlight-blue { color: #60a5fa; }
.highlight-emerald { color: #34d399; }
.highlight-amber { color: #fbbf24; }
.highlight-red { color: #f87171; font-weight: 700; }
.text-muted { color: #64748b; }

.text-center { text-align: center; }
.text-right { text-align: right; }

.action-btn {
  background-color: #0284c7;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background-color: #0369a1;
}

.action-none {
  color: #64748b;
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 2.5rem 1rem;
  color: #94a3b8;
}

.table-skeleton-row {
  height: 1.5rem;
  background: linear-gradient(90deg, #334155 25%, #475569 50%, #334155 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Mobile Cards */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

@media (max-width: 820px) {
  .desktop-only {
    display: none;
  }
  .mobile-only {
    display: block;
  }

  .mobile-card-list {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .mobile-subject-card {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mobile-card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .mobile-subj-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
  }

  .mobile-subj-teacher {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  .mobile-metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
    background-color: #1e293b;
    border-radius: 8px;
    padding: 0.65rem;
  }

  .metric-box {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .metric-box-label {
    font-size: 0.625rem;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
  }

  .metric-box-val {
    font-size: 0.875rem;
    font-weight: 700;
    color: #f1f5f9;
  }

  .mobile-card-actions {
    display: flex;
  }

  .mobile-full-btn {
    width: 100%;
    padding: 0.5rem;
    text-align: center;
  }
}
</style>
