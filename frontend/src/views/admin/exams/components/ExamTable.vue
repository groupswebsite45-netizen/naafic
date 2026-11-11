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

function formatDateTime(dateStr?: string | null): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return dateStr;
  }
}
</script>

<template>
  <div class="table-responsive">
    <table class="exam-data-table">
      <thead>
        <tr>
          <th scope="col" class="th-exam">Exam Identity</th>
          <th scope="col" class="th-academic">Academic Year</th>
          <th scope="col" class="th-date">Schedule & Deadline</th>
          <th scope="col" class="th-class">Class</th>
          <th scope="col" class="th-subject">Subject</th>
          <th scope="col" class="th-status">Status</th>
          <th scope="col" class="th-results">Results Progress</th>
          <th scope="col" class="th-actions text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="exam in exams"
          :key="exam.id"
          class="table-row"
          @click="emit('view', exam)"
        >
          <!-- Exam Identity -->
          <td class="td-exam">
            <div class="exam-identity">
              <span class="exam-name">{{ exam.name }}</span>
              <div class="exam-meta">
                <span class="exam-type-pill">{{ exam.exam_type }}</span>
                <span class="marks-weight">Max: {{ exam.max_marks ?? 100 }} pts</span>
              </div>
            </div>
          </td>

          <!-- Academic Year -->
          <td class="td-academic">
            <span class="academic-year-text">{{ exam.academic_year }}</span>
          </td>

          <!-- Schedule Window & Result Deadline -->
          <td class="td-date">
            <div class="date-cell">
              <svg class="calendar-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
              </svg>
              <span>{{ formatDateRange(exam.start_date || exam.exam_date, exam.end_date) }}</span>
            </div>
            <div v-if="exam.result_submission_deadline" class="deadline-subtext">
              <span class="dl-tag">Deadline:</span>
              <span>{{ formatDateTime(exam.result_submission_deadline) }}</span>
            </div>
          </td>

          <!-- Class -->
          <td class="td-class">
            <div class="class-badge">
              <span>{{ exam.school_class?.name || exam.class_name || `Class #${exam.class_id}` }}</span>
              <span v-if="exam.school_class?.section" class="section-tag">Sec {{ exam.school_class.section }}</span>
            </div>
          </td>

          <!-- Subject -->
          <td class="td-subject">
            <span class="subject-text">
              {{ exam.subject?.name || exam.subject_name || `Subject #${exam.subject_id}` }}
            </span>
          </td>

          <!-- Status -->
          <td class="td-status">
            <ExamStatusBadge :status="exam.status" />
          </td>

          <!-- Results Progress -->
          <td class="td-results" @click.stop>
            <ResultProgressBar
              :entered="exam.results_count ?? 0"
              :total="exam.enrolled_students_count ?? 0"
              :percentage="exam.completion_percentage"
            />
          </td>

          <!-- Actions -->
          <td class="td-actions text-right" @click.stop>
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
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-responsive {
  width: 100%;
  overflow-x: auto;
  border-radius: 10px;
  background-color: #ffffff;
  border: 1px solid var(--border-subtle, #e2e8f0);
}

.exam-data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead {
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.text-right {
  text-align: right;
}

.table-row {
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.table-row:hover {
  background-color: #f8fafc;
}

.table-row:last-child {
  border-bottom: none;
}

td {
  padding: 0.875rem 1rem;
  font-size: 0.875rem;
  color: var(--text-primary, #0f172a);
  vertical-align: middle;
}

/* Exam Identity */
.exam-identity {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.exam-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}

.exam-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.exam-type-pill {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 600;
  padding: 0.1rem 0.45rem;
  background-color: #eff6ff;
  color: #2563eb;
  border-radius: 4px;
}

.marks-weight {
  font-size: 0.6875rem;
  color: #64748b;
}

.academic-year-text {
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
}

.date-cell {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #475569;
  font-size: 0.8125rem;
  white-space: nowrap;
}

.calendar-icon {
  width: 15px;
  height: 15px;
  color: #94a3b8;
  flex-shrink: 0;
}

.deadline-subtext {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.2rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.dl-tag {
  font-weight: 700;
  color: #0369a1;
}

.class-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  color: #1e293b;
}

.section-tag {
  font-size: 0.6875rem;
  font-weight: 500;
  color: #64748b;
  background-color: #f1f5f9;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
}

.subject-text {
  font-weight: 600;
  color: #0f172a;
}

.th-results, .td-results {
  min-width: 140px;
}

.th-actions, .td-actions {
  width: 48px;
}
</style>
