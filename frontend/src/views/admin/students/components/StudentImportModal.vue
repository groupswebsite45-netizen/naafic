<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { SchoolClass } from '../../../../types/school';
import {
  studentService,
  StudentImportPreviewResponse,
  StudentImportSummaryResponse,
} from '../../../../services/studentService';

const props = defineProps<{
  isOpen: boolean;
  availableClasses: SchoolClass[];
  availableYears?: string[];
  initialAcademicYear?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'importComplete', classId: number, academicYear: string): void;
}>();

// Steps: 1 = Select Class, 2 = Upload File, 3 = Preview & Validate, 4 = Processing, 5 = Summary
const currentStep = ref<number>(1);

// Step 1 State
const educationLevel = ref<'PRIMARY' | 'SECONDARY'>('PRIMARY');
const selectedClassId = ref<number | null>(null);
const selectedAcademicYear = ref<string>(props.initialAcademicYear || '2026/2027');

// Step 2 State
const selectedFile = ref<File | null>(null);
const isDragging = ref(false);
const isDownloadingTemplate = ref(false);

// Step 3 Preview State
const isValidating = ref(false);
const previewData = ref<StudentImportPreviewResponse | null>(null);
const enrollExistingStudents = ref(false);

// Step 4 & 5 Import State
const isImporting = ref(false);
const importSummary = ref<StudentImportSummaryResponse | null>(null);
const importError = ref<string>('');

const stepNames = [
  'Select Class',
  'Upload Excel',
  'Preview & Validate',
  'Summary',
];

// Filter classes by education level
const filteredClasses = computed(() => {
  return props.availableClasses.filter((c) => {
    const isPrimary = c.division === 'PRIMARY' || c.name.toLowerCase().startsWith('grade') || (c.level && c.level.toLowerCase().startsWith('grade'));
    const isSecondary = c.division === 'SECONDARY' || c.name.toLowerCase().startsWith('form') || (c.level && c.level.toLowerCase().startsWith('form'));
    return educationLevel.value === 'PRIMARY' ? isPrimary : isSecondary;
  });
});

const selectedClass = computed(() => {
  return props.availableClasses.find((c) => c.id === selectedClassId.value) || null;
});

const validImportableCount = computed(() => {
  if (!previewData.value) return 0;
  return previewData.value.rows.filter((r) => {
    if (r.status === 'VALID') return true;
    if (r.status === 'WARNING' && enrollExistingStudents.value) return true;
    return false;
  }).length;
});

// Watch education level change to reset class selection if invalid
watch(educationLevel, () => {
  if (selectedClassId.value) {
    const exists = filteredClasses.value.some((c) => c.id === selectedClassId.value);
    if (!exists) {
      selectedClassId.value = filteredClasses.value.length > 0 ? filteredClasses.value[0].id : null;
    }
  } else if (filteredClasses.value.length > 0) {
    selectedClassId.value = filteredClasses.value[0].id;
  }
});

// Auto-select first class when opening
watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      resetModal();
      if (filteredClasses.value.length > 0 && !selectedClassId.value) {
        selectedClassId.value = filteredClasses.value[0].id;
      }
    }
  }
);

function resetModal() {
  currentStep.value = 1;
  selectedFile.value = null;
  previewData.value = null;
  importSummary.value = null;
  importError.value = '';
  enrollExistingStudents.value = false;
}

// Download template
async function handleDownloadTemplate() {
  isDownloadingTemplate.value = true;
  try {
    const blob = await studentService.downloadImportTemplate();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'Student_Import_Template.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err: any) {
    importError.value = 'Failed to download template. Please try again.';
  } finally {
    isDownloadingTemplate.value = false;
  }
}

// File Drag & Drop handlers
function onFileDrop(e: DragEvent) {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    processSelectedFile(files[0]);
  }
}

function onFileInputChange(e: Event) {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    processSelectedFile(target.files[0]);
  }
}

function processSelectedFile(file: File) {
  importError.value = '';
  if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
    importError.value = 'Invalid file format. Please upload an Excel file (.xlsx or .xls).';
    selectedFile.value = null;
    return;
  }
  selectedFile.value = file;
}

function parseApiErrorMessage(err: any, fallbackMessage: string): string {
  if (!err) return fallbackMessage;
  const status = err.response?.status;

  if (status === 404) {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim() && !detail.toLowerCase().includes('not found')) {
      return detail;
    }
    return 'Import preview service was not found. Please check network connection.';
  }
  if (status === 401) {
    return 'Your Admin session has expired. Please log in again.';
  }
  if (status === 403) {
    return 'You do not have permission to import students.';
  }
  if (status === 422) {
    const detail = err.response?.data?.detail;
    if (Array.isArray(detail)) {
      return detail.map((d: any) => `${d.loc?.slice(1)?.join('.') || 'field'}: ${d.msg}`).join(', ');
    }
    return typeof detail === 'string' ? detail : 'Invalid Excel file format or parameters.';
  }
  if (status >= 500) {
    return 'Server error while reading the Excel file. Please check file formatting.';
  }
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  return err.message || fallbackMessage;
}

// Validate & Preview Step
async function handleValidateAndPreview() {
  if (!selectedFile.value || !selectedClassId.value) return;

  isValidating.value = true;
  importError.value = '';
  try {
    const res = await studentService.previewImportExcel(
      selectedFile.value,
      selectedClassId.value,
      selectedAcademicYear.value
    );
    previewData.value = res;
    currentStep.value = 3;
  } catch (err: any) {
    importError.value = parseApiErrorMessage(err, 'Failed to parse and validate Excel file.');
  } finally {
    isValidating.value = false;
  }
}

// Execute Import Step
async function handleExecuteImport() {
  if (!previewData.value || !selectedClassId.value) return;

  isImporting.value = true;
  currentStep.value = 4;
  importError.value = '';

  try {
    const res = await studentService.executeImport({
      class_id: selectedClassId.value,
      academic_year: selectedAcademicYear.value,
      file_name: selectedFile.value?.name || 'students.xlsx',
      rows: previewData.value.rows,
      enroll_existing_students: enrollExistingStudents.value,
    });
    importSummary.value = res;
    currentStep.value = 5;
  } catch (err: any) {
    importError.value = parseApiErrorMessage(err, 'Import transaction failed.');
    currentStep.value = 3;
  } finally {
    isImporting.value = false;
  }
}

function handleViewClassStudents() {
  if (selectedClassId.value) {
    emit('importComplete', selectedClassId.value, selectedAcademicYear.value);
  }
  emit('close');
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-container" role="dialog" aria-modal="true">
      <!-- Fixed Modal Header -->
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon-wrap" aria-hidden="true">
            <svg class="header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <div class="header-title-block">
            <h2 class="modal-title">Import Students from Excel</h2>
            <p class="modal-subtitle">Enroll multiple students into a designated class with authoritative validation.</p>
          </div>
        </div>
        <button
          type="button"
          class="close-btn"
          title="Close dialog"
          aria-label="Close dialog"
          @click="emit('close')"
        >
          &times;
        </button>
      </div>

      <!-- Desktop Stepper (>=768px) -->
      <div class="stepper-bar hide-mobile">
        <div class="step-item" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
          <span class="step-num">{{ currentStep > 1 ? '✓' : '1' }}</span>
          <span class="step-label">Select Class</span>
        </div>
        <div class="step-divider" />
        <div class="step-item" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
          <span class="step-num">{{ currentStep > 2 ? '✓' : '2' }}</span>
          <span class="step-label">Upload Excel</span>
        </div>
        <div class="step-divider" />
        <div class="step-item" :class="{ active: currentStep === 3, completed: currentStep > 3 }">
          <span class="step-num">{{ currentStep > 3 ? '✓' : '3' }}</span>
          <span class="step-label">Preview & Validate</span>
        </div>
        <div class="step-divider" />
        <div class="step-item" :class="{ active: currentStep >= 4, completed: currentStep === 5 }">
          <span class="step-num">{{ currentStep === 5 ? '✓' : '4' }}</span>
          <span class="step-label">Summary</span>
        </div>
      </div>

      <!-- Mobile Stepper (<768px) -->
      <div class="mobile-stepper hide-desktop">
        <div class="mobile-step-header">
          <span class="mobile-step-count">STEP {{ Math.min(currentStep, 4) }} OF 4</span>
          <span class="mobile-step-title">{{ stepNames[Math.min(currentStep, 4) - 1] }}</span>
        </div>
        <div class="step-progress-track">
          <div
            class="step-progress-fill"
            :style="{ width: `${(Math.min(currentStep, 4) / 4) * 100}%` }"
          />
        </div>
      </div>

      <!-- Global Error Banner -->
      <div v-if="importError" class="alert-banner danger">
        <svg class="alert-icon flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ importError }}</span>
      </div>

      <!-- Scrollable Modal Body -->
      <div class="modal-body">
        <!-- ================================================================= -->
        <!-- STEP 1: SELECT CLASS & ACADEMIC YEAR                              -->
        <!-- ================================================================= -->
        <div v-if="currentStep === 1" class="step-pane">
          <div class="guide-box">
            <h4 class="guide-title">Class Roster Allocation</h4>
            <p class="guide-desc">
              All students imported in this batch will be directly enrolled into the selected class for the designated academic year.
            </p>
          </div>

          <div class="form-grid">
            <!-- Education Level -->
            <div class="form-group">
              <label class="form-label">Education Level *</label>
              <div class="segmented-control">
                <button
                  type="button"
                  class="seg-btn"
                  :class="{ active: educationLevel === 'PRIMARY' }"
                  @click="educationLevel = 'PRIMARY'"
                >
                  Primary (Grade 1 - 8)
                </button>
                <button
                  type="button"
                  class="seg-btn"
                  :class="{ active: educationLevel === 'SECONDARY' }"
                  @click="educationLevel = 'SECONDARY'"
                >
                  Secondary (Form 1 - 4)
                </button>
              </div>
            </div>

            <!-- Destination Class -->
            <div class="form-group">
              <label class="form-label" for="dest-class-select">Destination Class *</label>
              <select
                id="dest-class-select"
                v-model="selectedClassId"
                class="form-select"
                required
              >
                <option :value="null" disabled>Select Destination Class</option>
                <option v-for="c in filteredClasses" :key="c.id" :value="c.id">
                  {{ c.name }} ({{ c.code }}) — {{ c.students_count || 0 }} enrolled
                </option>
              </select>
              <span v-if="filteredClasses.length === 0" class="field-hint text-amber-600">
                No active {{ educationLevel.toLowerCase() }} classes found.
              </span>
            </div>

            <!-- Academic Year -->
            <div class="form-group">
              <label class="form-label" for="dest-year-select">Academic Year *</label>
              <select
                id="dest-year-select"
                v-model="selectedAcademicYear"
                class="form-select"
              >
                <option value="2026/2027">2026/2027 (Active School Year)</option>
                <option value="2025/2026">2025/2026</option>
                <option value="2027/2028">2027/2028</option>
              </select>
            </div>
          </div>
        </div>

        <!-- ================================================================= -->
        <!-- STEP 2: UPLOAD EXCEL FILE                                         -->
        <!-- ================================================================= -->
        <div v-else-if="currentStep === 2" class="step-pane">
          <!-- Class Context Badge -->
          <div class="context-pill">
            <span class="pill-label">Destination:</span>
            <span class="pill-val">{{ selectedClass?.name }} ({{ selectedAcademicYear }})</span>
            <button type="button" class="pill-change" @click="currentStep = 1">Change</button>
          </div>

          <!-- Template Download Card -->
          <div class="template-card">
            <div class="template-info">
              <svg class="template-svg flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="template-text">
                <h4 class="template-heading">Official Excel Template</h4>
                <p class="template-sub">Download formatted template with columns for Student Name, Gender, Date of Birth, Guardian details.</p>
              </div>
            </div>
            <button
              type="button"
              class="btn-template"
              :disabled="isDownloadingTemplate"
              @click="handleDownloadTemplate"
            >
              <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>{{ isDownloadingTemplate ? 'Downloading...' : 'Download Template' }}</span>
            </button>
          </div>

          <!-- Dropzone -->
          <div
            class="dropzone"
            :class="{ dragging: isDragging, 'has-file': !!selectedFile }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onFileDrop"
          >
            <input
              id="file-upload-input"
              type="file"
              accept=".xlsx, .xls"
              class="hidden-file-input"
              @change="onFileInputChange"
            />

            <div v-if="!selectedFile" class="dropzone-content">
              <svg class="drop-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="drop-main-text">Drag & drop your <strong>.xlsx</strong> file here</p>
              <p class="drop-sub-text">or click to choose from your device</p>
              <label for="file-upload-input" class="btn-browse">Choose Excel File</label>
            </div>

            <div v-else class="file-preview-card">
              <div class="file-icon-box">
                <svg class="w-7 h-7 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="file-meta">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
              </div>
              <label for="file-upload-input" class="file-replace-btn">Change File</label>
            </div>
          </div>
        </div>

        <!-- ================================================================= -->
        <!-- STEP 3: PREVIEW & VALIDATE                                        -->
        <!-- ================================================================= -->
        <div v-else-if="currentStep === 3 && previewData" class="step-pane preview-pane">
          <!-- Summary Metrics Header -->
          <div class="preview-metrics-row">
            <div class="metric-card">
              <span class="metric-label">Total Rows</span>
              <span class="metric-val">{{ previewData.total_rows }}</span>
            </div>
            <div class="metric-card valid">
              <span class="metric-label">Valid to Import</span>
              <span class="metric-val text-emerald-600">{{ previewData.valid_rows }}</span>
            </div>
            <div v-if="previewData.warning_rows > 0" class="metric-card warning">
              <span class="metric-label">Existing Records</span>
              <span class="metric-val text-amber-600">{{ previewData.warning_rows }}</span>
            </div>
            <div v-if="previewData.already_exists_rows > 0" class="metric-card exists">
              <span class="metric-label">Already Enrolled</span>
              <span class="metric-val text-purple-600">{{ previewData.already_exists_rows }}</span>
            </div>
            <div v-if="previewData.error_rows > 0" class="metric-card error">
              <span class="metric-label">Errors</span>
              <span class="metric-val text-rose-600">{{ previewData.error_rows }}</span>
            </div>
          </div>

          <!-- Existing Students Option -->
          <div v-if="previewData.warning_rows > 0" class="enroll-option-banner">
            <label class="checkbox-label">
              <input v-model="enrollExistingStudents" type="checkbox" class="checkbox-input" />
              <span>Enroll <strong>{{ previewData.warning_rows }}</strong> existing student(s) into <strong>{{ selectedClass?.name }}</strong></span>
            </label>
          </div>

          <!-- Bounded Horizontally-Scrollable Table Container -->
          <div class="preview-table-wrapper">
            <div class="preview-table-scroller" tabindex="0" role="region" aria-label="Excel parsed student preview table">
              <table class="preview-table" aria-label="Excel parsed student preview table">
                <thead>
                  <tr>
                    <th style="width: 45px;">#</th>
                    <th>Student ID</th>
                    <th>Student Name</th>
                    <th>Gender</th>
                    <th>Date of Birth</th>
                    <th>Guardian Name</th>
                    <th>Guardian Phone</th>
                    <th>Validation Status</th>
                    <th>Notes / Details</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in previewData.rows"
                    :key="row.row_number"
                    :class="{
                      'row-error': row.status === 'ERROR',
                      'row-warning': row.status === 'WARNING',
                      'row-exists': row.status === 'ALREADY_EXISTS',
                    }"
                  >
                    <td class="text-center font-mono text-xs text-slate-400">{{ row.row_number }}</td>
                    <td class="font-mono text-xs text-slate-500">
                      {{ row.admission_number || '(Auto)' }}
                    </td>
                    <td class="font-medium text-slate-900">
                      {{ row.student_name || row.full_name || [row.first_name, row.middle_name, row.last_name].filter(Boolean).join(' ') }}
                    </td>
                    <td>
                      <span class="gender-tag" :class="row.gender?.toLowerCase()">
                        {{ row.gender || '—' }}
                      </span>
                    </td>
                    <td class="font-mono text-xs text-slate-600">
                      {{ row.date_of_birth || '—' }}
                    </td>
                    <td>{{ row.guardian_name || '—' }}</td>
                    <td class="font-mono text-xs">{{ row.guardian_phone || '—' }}</td>
                    <td>
                      <span
                        class="status-chip"
                        :class="{
                          valid: row.status === 'VALID',
                          error: row.status === 'ERROR',
                          warning: row.status === 'WARNING',
                          exists: row.status === 'ALREADY_EXISTS',
                        }"
                      >
                        {{ row.status === 'ALREADY_EXISTS' ? 'ALREADY ENROLLED' : row.status }}
                      </span>
                    </td>
                    <td class="text-xs text-slate-500 max-w-xs truncate" :title="row.error_reason || ''">
                      {{ row.error_reason || '—' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ================================================================= -->
        <!-- STEP 4: PROCESSING TRANSACTION                                    -->
        <!-- ================================================================= -->
        <div v-else-if="currentStep === 4" class="step-pane loading-pane">
          <div class="spinner-large" />
          <h3 class="font-bold text-slate-800 text-lg mt-4">Processing Import</h3>
          <p class="text-sm text-slate-500 mt-1">Committing student records and class enrollments to PostgreSQL...</p>
        </div>

        <!-- ================================================================= -->
        <!-- STEP 5: IMPORT SUMMARY                                            -->
        <!-- ================================================================= -->
        <div v-else-if="currentStep === 5 && importSummary" class="step-pane summary-pane">
          <div class="success-icon-wrap" aria-hidden="true">
            <svg class="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h3 class="summary-title">Import Completed Successfully</h3>
          <p class="summary-subtitle">{{ importSummary.message }}</p>

          <div class="summary-stats-grid">
            <div class="stat-card">
              <span class="stat-num text-emerald-600">{{ importSummary.imported_count }}</span>
              <span class="stat-label">Enrolled Students</span>
            </div>
            <div class="stat-card">
              <span class="stat-num text-purple-600">{{ importSummary.already_enrolled_count }}</span>
              <span class="stat-label">Already Enrolled</span>
            </div>
            <div class="stat-card">
              <span class="stat-num text-slate-500">{{ importSummary.skipped_count }}</span>
              <span class="stat-label">Skipped</span>
            </div>
            <div class="stat-card">
              <span class="stat-num text-rose-600">{{ importSummary.failed_count }}</span>
              <span class="stat-label">Failed</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fixed Modal Footer -->
      <div class="modal-footer">
        <template v-if="currentStep === 1">
          <button type="button" class="btn-secondary" @click="emit('close')">Cancel</button>
          <button
            type="button"
            class="btn-primary"
            :disabled="!selectedClassId"
            @click="currentStep = 2"
          >
            <span>Continue to Upload</span>
            <span>&rarr;</span>
          </button>
        </template>

        <template v-else-if="currentStep === 2">
          <button type="button" class="btn-secondary" @click="currentStep = 1">&larr; Back</button>
          <button
            type="button"
            class="btn-primary"
            :disabled="!selectedFile || isValidating"
            @click="handleValidateAndPreview"
          >
            <span v-if="isValidating">Validating Excel...</span>
            <span v-else>Validate & Preview &rarr;</span>
          </button>
        </template>

        <template v-else-if="currentStep === 3">
          <button type="button" class="btn-secondary" @click="currentStep = 2">&larr; Back to Upload</button>
          <button
            type="button"
            class="btn-primary"
            :disabled="validImportableCount === 0 || isImporting"
            @click="handleExecuteImport"
          >
            <span>Import {{ validImportableCount }} Student(s)</span>
          </button>
        </template>

        <template v-else-if="currentStep === 5">
          <button type="button" class="btn-secondary" @click="resetModal">Import Another File</button>
          <button type="button" class="btn-primary" @click="handleViewClassStudents">
            View {{ selectedClass?.name }} Students &rarr;
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 60;
  box-sizing: border-box;
}

.modal-container {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: min(900px, calc(100vw - 20px));
  max-height: calc(100vh - 28px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  overflow: hidden;
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.125rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  gap: 0.75rem;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-width: 0;
  flex: 1;
}

.header-icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2563eb;
  flex-shrink: 0;
}

.header-icon {
  width: 22px;
  height: 22px;
}

.header-title-block {
  min-width: 0;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  line-height: 1.3;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.2rem 0 0;
  line-height: 1.4;
}

.close-btn {
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  background: none;
  border: none;
  border-radius: 8px;
  font-size: 1.625rem;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

/* Stepper Desktop */
.stepper-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
}

.step-item.active .step-num {
  background: #2563eb;
  color: #ffffff;
}

.step-item.active .step-label {
  color: #1e3a8a;
}

.step-item.completed .step-num {
  background: #10b981;
  color: #ffffff;
}

.step-item.completed .step-label {
  color: #047857;
}

.step-divider {
  flex: 1;
  height: 1px;
  background: #e2e8f0;
  margin: 0 0.75rem;
}

/* Mobile Stepper */
.mobile-stepper {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.mobile-step-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.mobile-step-count {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.05em;
}

.mobile-step-title {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0f172a;
}

.step-progress-track {
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.step-progress-fill {
  height: 100%;
  background: #2563eb;
  transition: width 0.25s ease;
}

/* Modal Body */
.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  flex: 1 1 auto;
  box-sizing: border-box;
}

.alert-banner {
  margin: 0.875rem 1.5rem 0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-banner.danger {
  background: #fff1f2;
  color: #e11d48;
  border: 1px solid #fecdd3;
}

.alert-icon {
  width: 1.125rem;
  height: 1.125rem;
}

/* Step 1 */
.guide-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.875rem 1rem;
  margin-bottom: 1.25rem;
}

.guide-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e3a8a;
  margin: 0 0 0.25rem 0;
}

.guide-desc {
  font-size: 0.8125rem;
  color: #475569;
  margin: 0;
  line-height: 1.4;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.segmented-control {
  display: flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 8px;
  gap: 0.25rem;
  width: 100%;
  box-sizing: border-box;
}

.seg-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  background: transparent;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  min-height: 38px;
}

.seg-btn.active {
  background: #ffffff;
  color: #1e3a8a;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.form-select {
  height: 42px;
  padding: 0 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #ffffff;
  box-sizing: border-box;
}

.form-select:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

/* Step 2 */
.context-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 9999px;
  font-size: 0.75rem;
  margin-bottom: 1rem;
}

.pill-label { color: #64748b; font-weight: 500; }
.pill-val { color: #1e3a8a; font-weight: 700; }
.pill-change {
  background: none;
  border: none;
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  padding-left: 0.25rem;
}

.template-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  margin-bottom: 1.25rem;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.template-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  flex: 1;
}

.template-svg {
  width: 32px;
  height: 32px;
  color: #059669;
}

.template-heading {
  font-weight: 700;
  color: #065f46;
  font-size: 0.875rem;
  margin: 0;
}

.template-sub {
  font-size: 0.75rem;
  color: #047857;
  margin: 0.15rem 0 0;
  line-height: 1.35;
}

.btn-template {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: #10b981;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  height: 38px;
}

.btn-template:hover { background: #059669; }

.dropzone {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 2.25rem 1.25rem;
  text-align: center;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.dropzone.dragging {
  border-color: #2563eb;
  background: #eff6ff;
}

.dropzone.has-file {
  border-style: solid;
  border-color: #bbf7d0;
  background: #f0fdf4;
  padding: 1.25rem;
}

.hidden-file-input { display: none; }

.drop-icon {
  width: 42px;
  height: 42px;
  color: #94a3b8;
  margin: 0 auto 0.625rem auto;
}

.drop-main-text {
  font-size: 0.9375rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.drop-sub-text {
  font-size: 0.8125rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.btn-browse {
  display: inline-block;
  padding: 0.55rem 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-browse:hover { background: #f1f5f9; }

.file-preview-card {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  text-align: left;
}

.file-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.file-name {
  font-weight: 600;
  color: #0f172a;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 0.75rem;
  color: #64748b;
}

.file-replace-btn {
  padding: 0.45rem 0.875rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  white-space: nowrap;
}

/* Step 3 Preview */
.preview-metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.625rem;
  margin-bottom: 1rem;
}

.metric-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.625rem 0.75rem;
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 0.125rem;
}

.metric-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.enroll-option-banner {
  background: #fefce8;
  border: 1px solid #fef08a;
  border-radius: 8px;
  padding: 0.625rem 0.875rem;
  margin-bottom: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #854d0e;
  cursor: pointer;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  accent-color: #ca8a04;
}

/* Bounded Horizontally-Scrollable Table Container */
.preview-table-wrapper {
  max-height: 360px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #ffffff;
}

.preview-table-scroller {
  max-height: 360px;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
  width: 100%;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
  min-width: 650px;
}

.preview-table th {
  position: sticky;
  top: 0;
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
  font-size: 0.71875rem;
  text-transform: uppercase;
}

.preview-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  white-space: nowrap;
}

.preview-table tr.row-error { background: #fff1f2; }
.preview-table tr.row-warning { background: #fffbeb; }
.preview-table tr.row-exists { background: #faf5ff; }

.status-chip {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-chip.valid { background: #dcfce7; color: #15803d; }
.status-chip.error { background: #fee2e2; color: #b91c1c; }
.status-chip.warning { background: #fef3c7; color: #b45309; }
.status-chip.exists { background: #f3e8ff; color: #7e22ce; }

.gender-tag {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
}

.gender-tag.male { color: #2563eb; }
.gender-tag.female { color: #db2777; }

/* Step 4 Loading */
.loading-pane {
  padding: 3rem 1rem;
  text-align: center;
}

.spinner-large {
  width: 44px;
  height: 44px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Step 5 Summary */
.summary-pane {
  padding: 1.5rem 1rem;
  text-align: center;
}

.success-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.summary-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.summary-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.35rem 0 1.5rem 0;
}

.summary-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
  max-width: 580px;
  margin: 0 auto;
}

.stat-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 0.5rem;
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 1.5rem;
  font-weight: 800;
}

.stat-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-top: 0.25rem;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
  box-sizing: border-box;
}

.btn-secondary {
  height: 40px;
  padding: 0 1.125rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.btn-secondary:hover { background: #f1f5f9; color: #0f172a; }

.btn-primary {
  height: 40px;
  padding: 0 1.25rem;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  transition: all 0.15s ease;
  box-sizing: border-box;
}

.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Responsive adjustments */
@media (min-width: 768px) {
  .hide-desktop { display: none !important; }
}

@media (max-width: 767px) {
  .hide-mobile { display: none !important; }

  .modal-container {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .modal-header {
    padding: 0.875rem 1rem;
  }

  .modal-body {
    padding: 1rem;
  }

  .summary-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .preview-metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .template-card {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-template {
    width: 100%;
    justify-content: center;
  }

  .modal-footer {
    padding: 0.75rem 1rem;
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}
</style>
