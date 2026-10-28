<script setup lang="ts">
import { Exam } from '../../../../types/school';
import ExamStatusBadge from './ExamStatusBadge.vue';
import ResultProgressBar from './ResultProgressBar.vue';
import ExamActionMenu from './ExamActionMenu.vue';

defineProps<{
  exams: Exam[];
}>();

const emit = defineEmits<{
  (e: 'view', exam: Exam): void;
  (e: 'edit', exam: Exam): void;
  (e: 'enter-marks', exam: Exam): void;
  (e: 'review-results', exam: Exam): void;
  (e: 'publish', exam: Exam): void;
  (e: 'unpublish', exam: Exam): void;
  (e: 'delete', exam: Exam): void;
}>();

function formatDateRange(startDate?: string | null, endDate?: string | null): string {
  if (!startDate) return '—';
  try {
    const s = new Date(startDate);
    const startStr = s.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    if (!endDate || endDate === startDate) return startStr;
    const e = new Date(endDate);
    const endStr = e.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    return `${startStr} – ${endStr}`;
  } catch {
    return startDate;
  }
}
</script>

<template>
  <div class="exam-card-list">
    <div
      v-for="exam in exams"
      :key="exam.id"
      class="exam-mobile-card"
    >
      <!-- Card Top: Title, Meta, and Action Menu -->
      <div class="card-header">
        <div class="header-left">
          <div class="title-meta">
            <span class="exam-type-tag">{{ exam.exam_type }}</span>
            <span class="exam-year-tag">{{ exam.academic_year }}</span>
          </div>
          <h2 class="exam-card-title">{{ exam.name }}</h2>
        </div>
        <div class="header-right" @click.stop>
          <ExamActionMenu
            :exam="exam"
            @view="emit('view', exam)"
            @edit="emit('edit', exam)"
            @enter-marks="emit('enter-marks', exam)"
            @review-results="emit('review-results', exam)"
            @publish="emit('publish', exam)"
            @unpublish="emit('unpublish', exam)"
            @delete="emit('delete', exam)"
          />
        </div>
      </div>

      <!-- Date Section -->
      <div class="card-section">
        <span class="section-label">Date Window</span>
        <div class="date-row">
          <svg class="calendar-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
          </svg>
          <span class="date-text">{{ formatDateRange(exam.start_date || exam.exam_date, exam.end_date) }}</span>
        </div>
      </div>

      <!-- Class & Subject Grid -->
      <div class="card-grid">
        <div class="grid-item">
          <span class="section-label">Class</span>
          <span class="grid-val">{{ exam.school_class?.name || exam.class_name || `Class #${exam.class_id}` }}</span>
        </div>
        <div class="grid-item">
          <span class="section-label">Subject</span>
          <span class="grid-val">{{ exam.subject?.name || exam.subject_name || `Subject #${exam.subject_id}` }}</span>
        </div>
      </div>

      <!-- Results & Status Section -->
      <div class="results-section">
        <div class="results-header">
          <span class="section-label">Results Progress</span>
          <ExamStatusBadge :status="exam.status" />
        </div>
        <ResultProgressBar
          :entered="exam.results_count ?? 0"
          :total="exam.enrolled_students_count ?? 0"
          :percentage="exam.completion_percentage"
        />
      </div>

      <!-- Card Footer Action -->
      <div class="card-footer">
        <button
          type="button"
          class="view-exam-btn"
          @click="emit('view', exam)"
        >
          <span>View Exam Profile</span>
          <svg class="arrow-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.exam-card-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  width: 100%;
}

.exam-mobile-card {
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border: 1px solid var(--border-subtle, #e2e8f0);
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  width: 100%;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.header-left {
  flex: 1;
  min-width: 0;
}

.title-meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.35rem;
  flex-wrap: wrap;
}

.exam-type-tag {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  background-color: #eff6ff;
  color: #2563eb;
  border-radius: 4px;
}

.exam-year-tag {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
}

.exam-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
  word-break: break-word;
}

.header-right {
  flex-shrink: 0;
}

.card-section {
  padding: 0.625rem 0;
  border-bottom: 1px solid #f8fafc;
}

.section-label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.2rem;
}

.date-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.calendar-icon {
  width: 15px;
  height: 15px;
  color: #94a3b8;
  flex-shrink: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid #f8fafc;
}

.grid-item {
  min-width: 0;
}

.grid-val {
  display: block;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.results-section {
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-footer {
  padding-top: 0.625rem;
}

.view-exam-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  width: 100%;
  padding: 0.55rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #4f46e5;
  background-color: #f5f3ff;
  border: 1px solid #ddd6fe;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.view-exam-btn:hover {
  background-color: #ede9fe;
}

.arrow-icon {
  width: 14px;
  height: 14px;
}
</style>
