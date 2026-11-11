<script setup lang="ts">
import { ReportCardData } from '../../../../types/school';
import GradeBadge from './GradeBadge.vue';

defineProps<{
  reportCard: ReportCardData | null;
}>();

function printReportCard() {
  window.print();
}
</script>

<template>
  <div v-if="reportCard" class="report-card-wrapper">
    <!-- Top Action Bar (hidden in print) -->
    <div class="report-card-toolbar no-print">
      <div class="report-status-notice">
        <span class="status-indicator-dot" />
        <span>Official Student Performance Assessment Sheet</span>
      </div>
      <button type="button" class="print-btn" @click="printReportCard">
        <svg class="print-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z" clip-rule="evenodd" />
        </svg>
        <span>Print Report Card</span>
      </button>
    </div>

    <!-- Official Report Card Sheet -->
    <div class="official-sheet">
      <!-- School Crest & Header -->
      <div class="school-header">
        <div class="school-emblem">
          <svg class="crest-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 14l9-5-9-5-9 5 9 5z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
          </svg>
        </div>
        <h1 class="school-title">{{ reportCard.school_name }}</h1>
        <p class="school-motto">{{ reportCard.school_motto }}</p>
        <div class="sheet-badge">OFFICIAL EXAMINATION REPORT CARD</div>
      </div>

      <!-- Student Metadata Card -->
      <div class="meta-section">
        <div class="meta-grid">
          <div class="meta-box">
            <span class="m-label">Student Full Name</span>
            <span class="m-value bold">{{ reportCard.student.full_name }}</span>
          </div>
          <div class="meta-box">
            <span class="m-label">Admission Number</span>
            <span class="m-value"><code>{{ reportCard.student.admission_number }}</code></span>
          </div>
          <div class="meta-box">
            <span class="m-label">Class / Grade</span>
            <span class="m-value">{{ reportCard.student.class_name }} {{ reportCard.student.class_section ? `(${reportCard.student.class_section})` : '' }}</span>
          </div>
          <div class="meta-box">
            <span class="m-label">Examination</span>
            <span class="m-value bold">{{ reportCard.exam_name }}</span>
          </div>
          <div class="meta-box">
            <span class="m-label">Academic Year</span>
            <span class="m-value">{{ reportCard.academic_year }}</span>
          </div>
          <div class="meta-box">
            <span class="m-label">Publication Status</span>
            <span class="m-value">{{ reportCard.summary.publication_status }}</span>
          </div>
        </div>
      </div>

      <!-- Subjects Table -->
      <div class="table-container" tabindex="0" role="region" aria-label="Subject grades report table">
        <table class="report-table">
          <thead>
            <tr>
              <th scope="col" class="th-num">#</th>
              <th scope="col" class="th-subj">Subject</th>
              <th scope="col" class="th-stat">Max</th>
              <th scope="col" class="th-stat">Score</th>
              <th scope="col" class="th-stat">Percentage</th>
              <th scope="col" class="th-stat">Grade</th>
              <th scope="col" class="th-rem">Teacher Evaluation Remarks</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(subj, index) in reportCard.subjects" :key="subj.subject_id">
              <td class="td-num">{{ index + 1 }}</td>
              <td class="td-subj">
                <span class="subj-name">{{ subj.subject_name }}</span>
                <span v-if="subj.subject_code" class="subj-code">({{ subj.subject_code }})</span>
              </td>
              <td class="td-stat">{{ subj.max_marks }}</td>
              <td class="td-stat bold">{{ subj.marks_obtained }}</td>
              <td class="td-stat">{{ subj.percentage }}%</td>
              <td class="td-stat">
                <GradeBadge :grade="subj.grade" />
              </td>
              <td class="td-rem">{{ subj.remarks || 'Satisfactory academic progress' }}</td>
            </tr>
          </tbody>
          <!-- Totals Footer -->
          <tfoot>
            <tr class="totals-row">
              <td colspan="2" class="total-label">OVERALL TOTALS & PERFORMANCE</td>
              <td class="td-stat bold">{{ reportCard.summary.total_possible_marks }}</td>
              <td class="td-stat bold text-indigo">{{ reportCard.summary.total_marks_obtained }}</td>
              <td class="td-stat bold">{{ reportCard.summary.overall_percentage }}%</td>
              <td class="td-stat">
                <GradeBadge :grade="reportCard.summary.overall_grade" />
              </td>
              <td class="td-rem bold">{{ reportCard.summary.overall_remark }}</td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Performance Summary Metric Boxes -->
      <div class="summary-cards-row">
        <div class="summary-box">
          <span class="sb-label">Total Points</span>
          <span class="sb-val">{{ reportCard.summary.total_marks_obtained }} / {{ reportCard.summary.total_possible_marks }}</span>
        </div>
        <div class="summary-box">
          <span class="sb-label">Average Score</span>
          <span class="sb-val">{{ reportCard.summary.overall_percentage }}%</span>
        </div>
        <div class="summary-box highlight">
          <span class="sb-label">Final Evaluation Grade</span>
          <span class="sb-val lg">{{ reportCard.summary.overall_grade }}</span>
        </div>
      </div>

      <!-- Official Signatures Block -->
      <div class="signatures-section">
        <div class="sig-block">
          <div class="sig-line" />
          <span class="sig-title">Class Teacher Signature</span>
          <span class="sig-date">Date: ________________</span>
        </div>
        <div class="stamp-box">
          <span class="stamp-label">Official Education Management System Seal</span>
        </div>
        <div class="sig-block">
          <div class="sig-line" />
          <span class="sig-title">Head of School / Principal</span>
          <span class="sig-date">Date: ________________</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-card-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.report-card-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.report-status-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.status-indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #10b981;
}

.print-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  background-color: #1e293b;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.print-btn:hover {
  background-color: #0f172a;
}

.print-icon {
  width: 16px;
  height: 16px;
}

/* Official Sheet */
.official-sheet {
  background-color: #ffffff;
  border: 2px solid #cbd5e1;
  border-radius: 12px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.school-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border-bottom: 2px double #cbd5e1;
  padding-bottom: 1.25rem;
}

.school-emblem {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
  color: #ffffff;
  margin-bottom: 0.75rem;
}

.crest-svg {
  width: 30px;
  height: 30px;
}

.school-title {
  font-size: 1.375rem;
  font-weight: 800;
  color: #0f172a;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0;
}

.school-motto {
  font-size: 0.875rem;
  color: #64748b;
  font-style: italic;
  margin: 0.25rem 0 0.75rem 0;
}

.sheet-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1e3a8a;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.2rem 0.875rem;
  border-radius: 9999px;
  letter-spacing: 0.05em;
}

.meta-section {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.875rem;
}

.meta-box {
  display: flex;
  flex-direction: column;
}

.m-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.m-value {
  font-size: 0.875rem;
  color: #0f172a;
}

.m-value.bold {
  font-weight: 700;
}

.table-container {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  min-width: 580px;
  border-collapse: collapse;
}

.report-table th {
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.625rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
  text-transform: uppercase;
  text-align: left;
}

.report-table td {
  border: 1px solid #e2e8f0;
  padding: 0.625rem 0.75rem;
  font-size: 0.8125rem;
  color: #0f172a;
}

.td-num { width: 40px; text-align: center; }
.th-num { width: 40px; text-align: center; }
.td-stat, .th-stat { text-align: center; }
.bold { font-weight: 700; }
.text-indigo { color: #4338ca; }

.totals-row td {
  background-color: #f8fafc;
  font-weight: 700;
  border-top: 2px solid #cbd5e1;
}

.total-label {
  text-align: right;
  letter-spacing: 0.03em;
}

.summary-cards-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.summary-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.875rem;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.summary-box.highlight {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.sb-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.sb-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin-top: 0.25rem;
}

.sb-val.lg {
  font-size: 1.5rem;
  color: #1e3a8a;
}

.signatures-section {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-top: 2rem;
  margin-top: 1rem;
}

.sig-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 200px;
}

.sig-line {
  width: 100%;
  border-bottom: 1px dashed #94a3b8;
  margin-bottom: 0.5rem;
}

.sig-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #334155;
}

.sig-date {
  font-size: 0.6875rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.stamp-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 80px;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  text-align: center;
  padding: 0.5rem;
}

.stamp-label {
  font-size: 0.625rem;
  color: #94a3b8;
  text-transform: uppercase;
}

@media print {
  .no-print {
    display: none !important;
  }
  .official-sheet {
    border: none;
    box-shadow: none;
    padding: 0;
  }
}

@media (max-width: 768px) {
  .meta-grid {
    grid-template-columns: 1fr 1fr;
  }
  .official-sheet {
    padding: 1rem;
  }
  .signatures-section {
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  .summary-cards-row {
    grid-template-columns: 1fr;
  }
}
</style>
