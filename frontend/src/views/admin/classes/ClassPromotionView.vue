<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import {
  classPromotionService,
  SuggestedMappingsResponse,
  ClassPromotionMappingItem,
  ClassPromotionMappingSuggestion,
  TargetClassOption,
  BulkPromotionPreviewResponse,
  StudentPromotionPreviewItem,
  StudentPromotionOverrideItem,
  PromotionBatch,
  StudentSearchForPromotionItem,
  PromotionActionType,
} from '../../../services/classPromotionService';

const router = useRouter();

// Main Education Level Filter: 'PRIMARY' (Grade 1..8) | 'SECONDARY' (Form 1..4)
const educationLevel = ref<'PRIMARY' | 'SECONDARY'>('PRIMARY');

// Main Workflow Navigation: 'bulk' | 'single' | 'individual' | 'history'
const activeWorkflow = ref<'bulk' | 'single' | 'individual' | 'history'>('bulk');

// Global Notification Banners
const alertSuccess = ref('');
const executionError = ref('');

// Academic Years
const sourceAcademicYear = ref('2026/2027');
const targetAcademicYear = ref('2027/2028');
const availableYears = ref<string[]>(['2025-2026', '2026/2027', '2027/2028', '2028/2029']);

// -----------------------------------------------------------------------------
// WORKFLOW 1: BULK PROMOTION STATE
// -----------------------------------------------------------------------------
// Wizard Steps: 1 = Configuration & Mapping, 2 = Live Preview & Validation, 3 = Confirmation, 4 = Success Receipt
const wizardStep = ref<1 | 2 | 3 | 4>(1);
const isLoadingMappings = ref(false);
const classMappings = ref<ClassPromotionMappingSuggestion[]>([]);
const availableTargetClasses = ref<TargetClassOption[]>([]);
const bulkClassSearch = ref('');
const bulkPromotionReason = ref('Annual Academic Promotion');

// Overrides map for individual students inside preview
const studentOverrides = ref<Map<number, StudentPromotionOverrideItem>>(new Map());

// Preview State
const isLoadingPreview = ref(false);
const previewData = ref<BulkPromotionPreviewResponse | null>(null);
const previewSearch = ref('');
const previewClassFilter = ref<number | ''>('');
const previewStatusFilter = ref<string>('');
const previewActionFilter = ref<string>('');

// Bulk Execution
const isExecutingBulk = ref(false);
const successBatch = ref<PromotionBatch | null>(null);

// -----------------------------------------------------------------------------
// WORKFLOW 2: SINGLE CLASS PROMOTION STATE
// -----------------------------------------------------------------------------
const singleSourceClassId = ref<number | ''>('');
const singleTargetClassId = ref<number | ''>('');
const singleAction = ref<'PROMOTE' | 'GRADUATE'>('PROMOTE');
const singleReason = ref('Single Class Promotion');
const singlePreviewData = ref<BulkPromotionPreviewResponse | null>(null);
const singleIsLoadingPreview = ref(false);
const singleIsExecuting = ref(false);
const singleStep = ref<1 | 2>(1); // 1 = Configure, 2 = Preview & Confirm

// -----------------------------------------------------------------------------
// WORKFLOW 3: INDIVIDUAL STUDENT PROMOTION STATE
// -----------------------------------------------------------------------------
const indSearchQuery = ref('');
const indClassFilter = ref<number | ''>('');
const indSearchResults = ref<StudentSearchForPromotionItem[]>([]);
const indIsSearching = ref(false);
const selectedStudent = ref<StudentSearchForPromotionItem | null>(null);
const indAction = ref<PromotionActionType>('PROMOTE');
const indTargetClassId = ref<number | ''>('');
const indReason = ref('Individual Student Promotion');
const indIsExecuting = ref(false);
const indConfirmModalOpen = ref(false);

// -----------------------------------------------------------------------------
// WORKFLOW 4: PROMOTION HISTORY STATE
// -----------------------------------------------------------------------------
const isLoadingHistory = ref(false);
const promotionBatches = ref<PromotionBatch[]>([]);
const historyTypeFilter = ref<string>('');
const historyStatusFilter = ref<string>('');
const selectedBatchForDetails = ref<PromotionBatch | null>(null);
const isBatchDetailsModalOpen = ref(false);
const isLoadingBatchDetails = ref(false);

// Rollback State
const isRollbackModalOpen = ref(false);
const batchToRollback = ref<PromotionBatch | null>(null);
const isRollingBack = ref(false);
const rollbackError = ref('');

// -----------------------------------------------------------------------------
// COMPUTED PROPERTIES
// -----------------------------------------------------------------------------
// Filtered mappings by search query in Step 1
const filteredClassMappings = computed(() => {
  if (!bulkClassSearch.value.trim()) return classMappings.value;
  const q = bulkClassSearch.value.toLowerCase().trim();
  return classMappings.value.filter(m =>
    m.from_class_name.toLowerCase().includes(q) ||
    m.from_class_code.toLowerCase().includes(q) ||
    (m.section && m.section.toLowerCase().includes(q))
  );
});

// Eligible classes for single class promotion
const availableSourceClassesForSingle = computed(() => {
  return classMappings.value;
});

const selectedSingleSourceClass = computed(() => {
  if (!singleSourceClassId.value) return null;
  return classMappings.value.find(m => m.from_class_id === singleSourceClassId.value) || null;
});

// Filter target classes for single class promotion (cannot be the same class)
const availableTargetClassesForSingle = computed(() => {
  if (!singleSourceClassId.value) return availableTargetClasses.value;
  return availableTargetClasses.value.filter(c => c.id !== singleSourceClassId.value);
});

// Selected target class for single promotion
const selectedSingleTargetClass = computed(() => {
  if (!singleTargetClassId.value) return null;
  return availableTargetClasses.value.find(c => c.id === singleTargetClassId.value) || null;
});

// Missing destination count in current mappings
const currentMissingDestinationsCount = computed(() => {
  return classMappings.value.filter(m => m.action === 'PROMOTE' && !m.to_class_id).length;
});

// Filtered student previews in Step 2
const filteredPreviewStudents = computed(() => {
  if (!previewData.value) return [];
  return previewData.value.student_previews.filter(s => {
    const matchesSearch = !previewSearch.value ||
      s.student_name.toLowerCase().includes(previewSearch.value.toLowerCase()) ||
      s.admission_number.toLowerCase().includes(previewSearch.value.toLowerCase());
    const matchesClass = !previewClassFilter.value || s.current_class_id === previewClassFilter.value;
    const matchesStatus = !previewStatusFilter.value || s.status === previewStatusFilter.value;
    const matchesAction = !previewActionFilter.value || s.action === previewActionFilter.value;
    return matchesSearch && matchesClass && matchesStatus && matchesAction;
  });
});

// Filtered history batches
const filteredHistoryBatches = computed(() => {
  return promotionBatches.value.filter(b => {
    const matchesType = !historyTypeFilter.value || b.promotion_type === historyTypeFilter.value;
    const matchesStatus = !historyStatusFilter.value || b.status === historyStatusFilter.value;
    return matchesType && matchesStatus;
  });
});

// -----------------------------------------------------------------------------
// METHODS: BULK PROMOTION
// -----------------------------------------------------------------------------
async function loadSuggestedMappings() {
  isLoadingMappings.value = true;
  executionError.value = '';
  try {
    const data: SuggestedMappingsResponse = await classPromotionService.getSuggestedMappings(
      sourceAcademicYear.value,
      targetAcademicYear.value,
      educationLevel.value
    );
    sourceAcademicYear.value = data.source_academic_year;
    targetAcademicYear.value = data.target_academic_year;
    classMappings.value = data.mappings;
    availableTargetClasses.value = data.available_target_classes;

    if (data.academic_years && data.academic_years.length > 0) {
      const set = new Set([...availableYears.value, ...data.academic_years]);
      availableYears.value = Array.from(set);
    }
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Failed to load class mappings from database.';
  } finally {
    isLoadingMappings.value = false;
  }
}

async function handleGeneratePreview() {
  if (sourceAcademicYear.value === targetAcademicYear.value) {
    executionError.value = 'Source and Target academic years cannot be the same.';
    return;
  }

  isLoadingPreview.value = true;
  executionError.value = '';

  const payloadMappings: ClassPromotionMappingItem[] = classMappings.value.map(m => ({
    from_class_id: m.from_class_id,
    to_class_id: m.action === 'PROMOTE' ? (m.to_class_id || null) : null,
    action: m.action
  }));

  const overridesList = Array.from(studentOverrides.value.values());

  try {
    const res = await classPromotionService.previewBulkPromotion({
      source_academic_year: sourceAcademicYear.value,
      target_academic_year: targetAcademicYear.value,
      education_level: educationLevel.value,
      mappings: payloadMappings,
      student_overrides: overridesList.length > 0 ? overridesList : undefined
    });
    previewData.value = res;
    wizardStep.value = 2;
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Promotion preview evaluation failed.';
  } finally {
    isLoadingPreview.value = false;
  }
}

// Student action override in preview table
function updateStudentActionOverride(student: StudentPromotionPreviewItem, newAction: PromotionActionType, targetClassId?: number) {
  if (newAction === 'PROMOTE' && !targetClassId) {
    targetClassId = student.target_class_id || undefined;
  }
  studentOverrides.value.set(student.student_id, {
    student_id: student.student_id,
    action: newAction,
    target_class_id: targetClassId || null,
    reason: `Individual override: ${newAction}`
  });
  // Re-generate live preview to refresh validation & totals
  handleGeneratePreview();
}

async function handleExecuteBulkPromotion() {
  isExecutingBulk.value = true;
  executionError.value = '';

  const payloadMappings: ClassPromotionMappingItem[] = classMappings.value.map(m => ({
    from_class_id: m.from_class_id,
    to_class_id: m.action === 'PROMOTE' ? (m.to_class_id || null) : null,
    action: m.action
  }));

  const overridesList = Array.from(studentOverrides.value.values());

  try {
    const batch = await classPromotionService.executeBulkPromotion({
      source_academic_year: sourceAcademicYear.value,
      target_academic_year: targetAcademicYear.value,
      education_level: educationLevel.value,
      mappings: payloadMappings,
      student_overrides: overridesList.length > 0 ? overridesList : undefined,
      reason: bulkPromotionReason.value.trim() || undefined
    });

    successBatch.value = batch;
    wizardStep.value = 4;
    alertSuccess.value = `Bulk promotion executed successfully! Batch ${batch.batch_code} recorded.`;
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Bulk promotion transaction failed. No students were changed.';
  } finally {
    isExecutingBulk.value = false;
  }
}

function resetWizard() {
  wizardStep.value = 1;
  previewData.value = null;
  successBatch.value = null;
  executionError.value = '';
  studentOverrides.value.clear();
  loadSuggestedMappings();
}

// -----------------------------------------------------------------------------
// METHODS: SINGLE CLASS PROMOTION
// -----------------------------------------------------------------------------
watch(singleSourceClassId, (newCId) => {
  if (!newCId) {
    singleTargetClassId.value = '';
    return;
  }
  const found = classMappings.value.find(m => m.from_class_id === newCId);
  if (found) {
    if (found.is_terminal_class) {
      singleAction.value = 'GRADUATE';
      singleTargetClassId.value = '';
    } else {
      singleAction.value = 'PROMOTE';
      singleTargetClassId.value = found.to_class_id || '';
    }
  }
});

async function handleSingleClassPreview() {
  if (!singleSourceClassId.value) {
    executionError.value = 'Please select a source class.';
    return;
  }
  if (singleAction.value === 'PROMOTE' && !singleTargetClassId.value) {
    executionError.value = 'Please select a destination class for promotion.';
    return;
  }

  singleIsLoadingPreview.value = true;
  executionError.value = '';

  try {
    const res = await classPromotionService.previewBulkPromotion({
      source_academic_year: sourceAcademicYear.value,
      target_academic_year: targetAcademicYear.value,
      education_level: educationLevel.value,
      mappings: [
        {
          from_class_id: Number(singleSourceClassId.value),
          to_class_id: singleAction.value === 'PROMOTE' ? Number(singleTargetClassId.value) : null,
          action: singleAction.value
        }
      ]
    });
    singlePreviewData.value = res;
    singleStep.value = 2;
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Failed to preview single class promotion.';
  } finally {
    singleIsLoadingPreview.value = false;
  }
}

async function handleExecuteSingleClassPromotion() {
  if (!singleSourceClassId.value) return;

  singleIsExecuting.value = true;
  executionError.value = '';

  try {
    const batch = await classPromotionService.executeClassLevelPromotion({
      from_class_id: Number(singleSourceClassId.value),
      to_class_id: singleAction.value === 'PROMOTE' ? Number(singleTargetClassId.value) : undefined,
      source_academic_year: sourceAcademicYear.value,
      target_academic_year: targetAcademicYear.value,
      action: singleAction.value,
      reason: singleReason.value.trim() || undefined
    });

    alertSuccess.value = `Single class promotion completed! Batch ${batch.batch_code} created for ${batch.total_promoted} student(s).`;
    singleStep.value = 1;
    singleSourceClassId.value = '';
    singleTargetClassId.value = '';
    singlePreviewData.value = null;
    loadSuggestedMappings();
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Single class promotion failed.';
  } finally {
    singleIsExecuting.value = false;
  }
}

// -----------------------------------------------------------------------------
// METHODS: INDIVIDUAL STUDENT PROMOTION
// -----------------------------------------------------------------------------
async function handleSearchStudents() {
  indIsSearching.value = true;
  executionError.value = '';
  try {
    const res = await classPromotionService.searchStudentsForPromotion({
      q: indSearchQuery.value.trim() || undefined,
      class_id: indClassFilter.value ? Number(indClassFilter.value) : undefined,
      education_level: educationLevel.value,
      academic_year: sourceAcademicYear.value,
      limit: 40
    });
    indSearchResults.value = res;
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Student search failed.';
  } finally {
    indIsSearching.value = false;
  }
}

function handleSelectStudent(student: StudentSearchForPromotionItem) {
  selectedStudent.value = student;
  if (student.is_terminal) {
    indAction.value = 'GRADUATE';
    indTargetClassId.value = '';
  } else {
    indAction.value = 'PROMOTE';
    indTargetClassId.value = student.suggested_next_class_id || '';
  }
  indReason.value = `Promotion for ${student.student_name}`;
}

async function handleConfirmIndividualPromotion() {
  if (!selectedStudent.value) return;

  indIsExecuting.value = true;
  executionError.value = '';

  try {
    const batch = await classPromotionService.executeIndividualPromotion({
      student_id: selectedStudent.value.student_id,
      source_academic_year: sourceAcademicYear.value,
      target_academic_year: targetAcademicYear.value,
      action: indAction.value as any,
      target_class_id: indAction.value in ['PROMOTE', 'REPEAT', 'TRANSFER'] ? Number(indTargetClassId.value) : undefined,
      reason: indReason.value.trim() || undefined
    });

    alertSuccess.value = `Successfully processed promotion for ${selectedStudent.value.student_name}! Batch ${batch.batch_code} logged.`;
    indConfirmModalOpen.value = false;
    selectedStudent.value = null;
    handleSearchStudents();
    loadSuggestedMappings();
  } catch (err: any) {
    executionError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Individual promotion failed.';
  } finally {
    indIsExecuting.value = false;
  }
}

// -----------------------------------------------------------------------------
// METHODS: PROMOTION HISTORY & ROLLBACK
// -----------------------------------------------------------------------------
async function loadHistory() {
  isLoadingHistory.value = true;
  try {
    const batches = await classPromotionService.listHistory({ limit: 100 });
    promotionBatches.value = batches;
  } catch (err: any) {
    console.error('Failed to load promotion history', err);
  } finally {
    isLoadingHistory.value = false;
  }
}

async function openBatchDetails(batch: PromotionBatch) {
  selectedBatchForDetails.value = batch;
  isBatchDetailsModalOpen.value = true;
  isLoadingBatchDetails.value = true;
  try {
    const details = await classPromotionService.getBatchDetails(batch.id);
    selectedBatchForDetails.value = details;
  } catch (err: any) {
    console.error('Failed to load batch details', err);
  } finally {
    isLoadingBatchDetails.value = false;
  }
}

function openRollbackModal(batch: PromotionBatch) {
  batchToRollback.value = batch;
  rollbackError.value = '';
  isRollbackModalOpen.value = true;
}

async function handleConfirmRollback() {
  if (!batchToRollback.value) return;
  isRollingBack.value = true;
  rollbackError.value = '';
  try {
    const res = await classPromotionService.rollbackBatch(batchToRollback.value.id);
    alertSuccess.value = res.message;
    isRollbackModalOpen.value = false;
    loadHistory();
    loadSuggestedMappings();
    setTimeout(() => { alertSuccess.value = ''; }, 6000);
  } catch (err: any) {
    rollbackError.value =
      err.response?.data?.error?.message ||
      err.response?.data?.detail ||
      'Failed to rollback promotion batch.';
  } finally {
    isRollingBack.value = false;
  }
}

// Watchers
watch(educationLevel, () => {
  loadSuggestedMappings();
  if (activeWorkflow.value === 'individual') {
    handleSearchStudents();
  }
});

watch(activeWorkflow, (wf) => {
  if (wf === 'history') {
    loadHistory();
  } else if (wf === 'individual' && indSearchResults.value.length === 0) {
    handleSearchStudents();
  }
});

onMounted(() => {
  loadSuggestedMappings();
});
</script>

<template>
  <div class="promotion-module-root">
    <!-- HERO HEADER -->
    <header class="module-header-card">
      <div class="header-left-cluster">
        <div class="brand-crest-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 0 1 4-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 0 1-4 4H3" />
          </svg>
        </div>
        <div class="title-meta-box">
          <h1 class="module-main-title">Class Promotion & Progression</h1>
          <p class="module-sub-desc">
            Somroyal Educational Management System • Precision Academic Transition & History Preservation
          </p>
        </div>
      </div>

      <div class="header-right-actions">
        <button
          type="button"
          class="btn-outline-action"
          @click="router.push('/admin/classes')"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <span>Class Directory</span>
        </button>
      </div>
    </header>

    <!-- ALERT BANNERS -->
    <div v-if="alertSuccess" class="notice-banner success-notice">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <span class="notice-text">{{ alertSuccess }}</span>
      <button class="notice-dismiss" @click="alertSuccess = ''">&times;</button>
    </div>

    <div v-if="executionError" class="notice-banner error-notice">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span class="notice-text">{{ executionError }}</span>
      <button class="notice-dismiss" @click="executionError = ''">&times;</button>
    </div>

    <!-- 1. EDUCATION LEVEL SEGMENTED SWITCH (Requirement 1: Separate Primary & Secondary) -->
    <section class="education-level-control-bar">
      <div class="level-segment-wrap">
        <button
          type="button"
          class="level-segment-btn"
          :class="{ active: educationLevel === 'PRIMARY' }"
          @click="educationLevel = 'PRIMARY'"
        >
          <span class="segment-icon">🏫</span>
          <span class="segment-title">Primary Promotion</span>
          <span class="segment-sub">Grade 1 through Grade 8</span>
        </button>

        <button
          type="button"
          class="level-segment-btn"
          :class="{ active: educationLevel === 'SECONDARY' }"
          @click="educationLevel = 'SECONDARY'"
        >
          <span class="segment-icon">🎓</span>
          <span class="segment-title">Secondary Promotion</span>
          <span class="segment-sub">Form 1 through Form 4</span>
        </button>
      </div>

      <div class="active-level-indicator-pill">
        <span class="indicator-dot"></span>
        <span>Managing <strong>{{ educationLevel === 'PRIMARY' ? 'Primary (Grades 1–8)' : 'Secondary (Forms 1–4)' }}</strong></span>
      </div>
    </section>

    <!-- 2. WORKFLOW NAVIGATION TABS (Bulk, Single Class, Individual, History) -->
    <nav class="workflows-nav-bar">
      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeWorkflow === 'bulk' }"
        @click="activeWorkflow = 'bulk'"
      >
        <span class="wf-tab-icon">⚡</span>
        <span class="wf-tab-title">Bulk Promotion</span>
        <span class="wf-badge">{{ classMappings.length }} Classes</span>
      </button>

      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeWorkflow === 'single' }"
        @click="activeWorkflow = 'single'"
      >
        <span class="wf-tab-icon">🎯</span>
        <span class="wf-tab-title">Promote a Single Class</span>
      </button>

      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeWorkflow === 'individual' }"
        @click="activeWorkflow = 'individual'"
      >
        <span class="wf-tab-icon">👤</span>
        <span class="wf-tab-title">Individual Student Promotion</span>
      </button>

      <button
        type="button"
        class="workflow-tab-btn"
        :class="{ active: activeWorkflow === 'history' }"
        @click="activeWorkflow = 'history'"
      >
        <span class="wf-tab-icon">◷</span>
        <span class="wf-tab-title">Promotion History & Audit</span>
      </button>
    </nav>

    <!-- ===================================================================== -->
    <!-- WORKFLOW 1: BULK PROMOTION                                            -->
    <!-- ===================================================================== -->
    <div v-if="activeWorkflow === 'bulk'" class="workflow-pane bulk-pane">
      <!-- Wizard Progress Stepper -->
      <div class="wizard-stepper-box">
        <div class="stepper-step" :class="{ active: wizardStep === 1, done: wizardStep > 1 }">
          <div class="step-num-circle">1</div>
          <span class="step-label">1. Class Mappings & Sections</span>
        </div>
        <div class="stepper-bar" :class="{ done: wizardStep > 1 }"></div>
        <div class="stepper-step" :class="{ active: wizardStep === 2, done: wizardStep > 2 }">
          <div class="step-num-circle">2</div>
          <span class="step-label">2. Live Preview & Validation</span>
        </div>
        <div class="stepper-bar" :class="{ done: wizardStep > 2 }"></div>
        <div class="stepper-step" :class="{ active: wizardStep === 3, done: wizardStep > 3 }">
          <div class="step-num-circle">3</div>
          <span class="step-label">3. Transaction Confirmation</span>
        </div>
        <div class="stepper-bar" :class="{ done: wizardStep > 3 }"></div>
        <div class="stepper-step" :class="{ active: wizardStep === 4 }">
          <div class="step-num-circle">4</div>
          <span class="step-label">4. Promotion Receipt</span>
        </div>
      </div>

      <!-- STEP 1: CONFIGURE YEARS & MAP CLASSES -->
      <div v-if="wizardStep === 1" class="workflow-card">
        <div class="card-section-head">
          <h2 class="card-title">Configure Academic Years & Progression Mappings</h2>
          <p class="card-desc">
            The system automatically pairs classes with their corresponding next grade preserving sections
            (e.g., Grade 4A → Grade 5A, Grade 4B → Grade 5B, Form 1B → Form 2B).
            Terminal classes (Grade 8 / Form 4) are safely set to graduate.
          </p>
        </div>

        <!-- Academic Year Selectors -->
        <div class="academic-year-bridge-grid">
          <div class="year-input-card">
            <label class="year-label">Current Academic Year (Source)</label>
            <input
              v-model="sourceAcademicYear"
              type="text"
              class="year-field"
              placeholder="e.g. 2026/2027"
              @change="loadSuggestedMappings"
            />
            <span class="year-hint">Currently active enrollments will be transitioned.</span>
          </div>

          <div class="year-progression-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </div>

          <div class="year-input-card">
            <label class="year-label">Next Academic Year (Destination)</label>
            <input
              v-model="targetAcademicYear"
              type="text"
              class="year-field"
              placeholder="e.g. 2027/2028"
              @change="loadSuggestedMappings"
            />
            <span class="year-hint">New class assignments will be enrolled for this year.</span>
          </div>
        </div>

        <!-- Class Filter & Search Bar -->
        <div class="table-actions-toolbar">
          <div class="search-box-pill">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="bulkClassSearch"
              type="text"
              placeholder="Filter classes by name, grade, or section..."
              class="search-inner-input"
            />
          </div>

          <div class="toolbar-right">
            <span v-if="currentMissingDestinationsCount > 0" class="missing-warn-pill">
              ⚠️ {{ currentMissingDestinationsCount }} missing destination class(es)
            </span>
            <button
              type="button"
              class="btn-secondary-sm"
              :disabled="isLoadingMappings"
              @click="loadSuggestedMappings"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              <span>Regenerate Mappings</span>
            </button>
          </div>
        </div>

        <!-- Mappings Table -->
        <div class="table-container-wrap" tabindex="0" role="region" aria-label="Class progression mappings table">
          <table class="progression-table">
            <thead>
              <tr>
                <th>Current Class</th>
                <th>Education Level</th>
                <th>Section</th>
                <th>Eligible Students</th>
                <th>Promote To (Destination Class)</th>
                <th>Action Policy</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in filteredClassMappings" :key="m.from_class_id">
                <td class="class-col-cell">
                  <div class="class-name-row">
                    <strong class="class-name">{{ m.from_class_name }}</strong>
                    <span class="code-badge">{{ m.from_class_code }}</span>
                  </div>
                </td>
                <td>
                  <span class="level-tag" :class="m.education_level?.toLowerCase()">
                    {{ m.education_level }}
                  </span>
                </td>
                <td>
                  <span class="section-tag">{{ m.section || 'General' }}</span>
                </td>
                <td>
                  <span class="count-pill">{{ m.student_count }} Students</span>
                </td>
                <td class="dest-select-col">
                  <!-- Destination Dropdown if PROMOTE -->
                  <div v-if="m.action === 'PROMOTE'">
                    <div class="select-container" :class="{ 'has-warning': m.missing_destination_warning }">
                      <select v-model="m.to_class_id" class="destination-select">
                        <option :value="null">-- Select Destination Class --</option>
                        <option
                          v-for="tc in availableTargetClasses"
                          :key="tc.id"
                          :value="tc.id"
                          :disabled="tc.id === m.from_class_id"
                        >
                          {{ tc.name }} ({{ tc.code }}) {{ tc.section ? `• Section ${tc.section}` : '' }}
                        </option>
                      </select>
                    </div>
                    <div v-if="m.missing_destination_warning && !m.to_class_id" class="warning-alert-mini">
                      <span>⚠️ Destination class/section missing. Please select destination above.</span>
                    </div>
                  </div>

                  <!-- Graduation Tag if GRADUATE -->
                  <div v-else-if="m.action === 'GRADUATE'" class="graduation-indicator-box">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                      <path d="M6 12v5c0 2 3 3 6 3s6-1 6-3v-5" />
                    </svg>
                    <span>Final Grade: Student Completion / Graduation</span>
                  </div>

                  <div v-else class="skip-indicator-box">
                    <span>No Automatic Promotion (Skipped)</span>
                  </div>
                </td>
                <td>
                  <select v-model="m.action" class="policy-select" :class="m.action.toLowerCase()">
                    <option value="PROMOTE">Promote to Class</option>
                    <option value="GRADUATE">Graduate / Complete</option>
                    <option value="NO_CHANGE">No Action (Skip)</option>
                  </select>
                </td>
              </tr>
              <tr v-if="filteredClassMappings.length === 0">
                <td colspan="6" class="empty-table-cell">
                  {{ isLoadingMappings ? 'Analyzing school class progression...' : 'No active classes found for this education level.' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card-footer-controls">
          <button
            type="button"
            class="btn-primary-action"
            :disabled="isLoadingPreview || classMappings.length === 0"
            @click="handleGeneratePreview"
          >
            <span v-if="isLoadingPreview">Evaluating Eligibility & Conflicts...</span>
            <span v-else>Proceed to Live Preview & Verification</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </div>

      <!-- STEP 2: LIVE PREVIEW & VALIDATION TABLE (Requirement 8) -->
      <div v-if="wizardStep === 2 && previewData" class="workflow-card">
        <div class="card-section-head split-head">
          <div>
            <h2 class="card-title">Live Promotion Review & Validation</h2>
            <p class="card-desc">
              Review destination of every affected student from <strong>{{ previewData.source_academic_year }}</strong> to <strong>{{ previewData.target_academic_year }}</strong>.
              You can override individual student outcomes (Repeat, Transfer, Graduate, Exclude) directly below.
            </p>
          </div>
          <button type="button" class="btn-ghost-back" @click="wizardStep = 1">
            ← Modify Class Mappings
          </button>
        </div>

        <!-- Summary Statistics Cards -->
        <div class="metrics-dashboard-grid">
          <div class="stat-metric-card">
            <span class="stat-lbl">Total Affected</span>
            <span class="stat-num text-brand">{{ previewData.total_students_affected }}</span>
            <span class="stat-sub">Active Students</span>
          </div>
          <div class="stat-metric-card">
            <span class="stat-lbl">Promoting</span>
            <span class="stat-num text-success">{{ previewData.total_to_promote }}</span>
            <span class="stat-sub">To Next Grade/Form</span>
          </div>
          <div class="stat-metric-card">
            <span class="stat-lbl">Repeating</span>
            <span class="stat-num text-orange">{{ previewData.total_to_repeat }}</span>
            <span class="stat-sub">Repeat Academic Year</span>
          </div>
          <div class="stat-metric-card">
            <span class="stat-lbl">Graduating</span>
            <span class="stat-num text-purple">{{ previewData.total_to_graduate }}</span>
            <span class="stat-sub">Final Grade Complete</span>
          </div>
          <div class="stat-metric-card">
            <span class="stat-lbl">Excluded</span>
            <span class="stat-num text-gray">{{ previewData.total_excluded }}</span>
            <span class="stat-sub">Skipped With Reason</span>
          </div>
          <div class="stat-metric-card" :class="{ 'stat-danger': previewData.total_validation_errors > 0 || previewData.missing_destination_classes_count > 0 }">
            <span class="stat-lbl">Validation Conflicts</span>
            <span class="stat-num" :class="previewData.total_validation_errors > 0 ? 'text-danger' : 'text-success'">
              {{ previewData.total_validation_errors }}
            </span>
            <span class="stat-sub">{{ previewData.total_validation_errors === 0 ? 'All students ready' : 'Conflicts detected' }}</span>
          </div>
        </div>

        <!-- Search & Filter Bar for Student Previews -->
        <div class="preview-filters-box">
          <div class="search-box-pill flex-1">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="previewSearch"
              type="text"
              placeholder="Search by student name or admission number..."
              class="search-inner-input"
            />
          </div>

          <div class="filter-dropdowns-group">
            <select v-model="previewClassFilter" class="filter-control">
              <option :value="''">All Source Classes</option>
              <option v-for="c in previewData.class_summaries" :key="c.from_class_id" :value="c.from_class_id">
                {{ c.from_class_name }} ({{ c.students_count }})
              </option>
            </select>

            <select v-model="previewStatusFilter" class="filter-control">
              <option value="">All Validation Statuses</option>
              <option value="READY">READY</option>
              <option value="GRADUATING">GRADUATING</option>
              <option value="REPEATING">REPEATING</option>
              <option value="ALREADY_ENROLLED">ALREADY_ENROLLED</option>
              <option value="VALIDATION_ERROR">VALIDATION_ERROR</option>
            </select>

            <select v-model="previewActionFilter" class="filter-control">
              <option value="">All Actions</option>
              <option value="PROMOTE">PROMOTE</option>
              <option value="REPEAT">REPEAT</option>
              <option value="TRANSFER">TRANSFER</option>
              <option value="GRADUATE">GRADUATE</option>
              <option value="EXCLUDE">EXCLUDE</option>
            </select>
          </div>
        </div>

        <!-- Review & Verification Table (Requirement 8) -->
        <div class="table-container-wrap" tabindex="0" role="region" aria-label="Bulk promotion verification table">
          <table class="verification-table">
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Student Name</th>
                <th>Education Level</th>
                <th>Current Class & Section</th>
                <th>Destination Class & Section</th>
                <th>Source Year</th>
                <th>Target Year</th>
                <th>Promotion Action</th>
                <th>Validation Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="s in filteredPreviewStudents"
                :key="s.student_id"
                :class="{ 'row-conflict': !s.is_valid }"
              >
                <td>
                  <span class="adm-pill-text">{{ s.admission_number }}</span>
                </td>
                <td class="name-cell">
                  <strong class="student-name">{{ s.student_name }}</strong>
                </td>
                <td>
                  <span class="level-tag" :class="s.education_level?.toLowerCase()">
                    {{ s.education_level }}
                  </span>
                </td>
                <td>
                  <span class="class-chip from-chip">
                    {{ s.current_class_name }} {{ s.current_section ? `(${s.current_section})` : '' }}
                  </span>
                </td>
                <td>
                  <span v-if="s.target_class_name" class="class-chip to-chip">
                    {{ s.target_class_name }} {{ s.target_section ? `(${s.target_section})` : '' }}
                  </span>
                  <span v-else-if="s.action === 'GRADUATE'" class="text-purple-bold">
                    🎓 Graduation
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span class="year-subtext">{{ s.source_academic_year }}</span>
                </td>
                <td>
                  <span class="year-subtext highlight">{{ s.target_academic_year }}</span>
                </td>
                <td>
                  <!-- Interactive Action Override -->
                  <select
                    :value="s.action"
                    class="action-override-select"
                    :class="s.action.toLowerCase()"
                    @change="(e: any) => updateStudentActionOverride(s, e.target.value)"
                  >
                    <option value="PROMOTE">Promote</option>
                    <option value="REPEAT">Repeat Class</option>
                    <option value="TRANSFER">Transfer Class</option>
                    <option value="GRADUATE">Graduate</option>
                    <option value="EXCLUDE">Exclude</option>
                  </select>
                </td>
                <td>
                  <div class="validation-status-cell">
                    <span class="status-chip" :class="s.status.toLowerCase()">{{ s.status }}</span>
                    <span v-if="s.validation_message" class="val-err-text">{{ s.validation_message }}</span>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredPreviewStudents.length === 0">
                <td colspan="9" class="empty-table-cell">No students matching the filter criteria.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card-footer-controls split">
          <button type="button" class="btn-secondary-action" @click="wizardStep = 1">
            Back to Mappings
          </button>
          <button
            type="button"
            class="btn-primary-action"
            :disabled="!previewData.can_execute"
            @click="wizardStep = 3"
          >
            <span>Proceed to Confirmation</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </div>

      <!-- STEP 3: TRANSACTION CONFIRMATION -->
      <div v-if="wizardStep === 3 && previewData" class="workflow-card">
        <div class="confirmation-hero-box">
          <div class="confirm-shield-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>

          <h2 class="confirm-title">Confirm {{ educationLevel === 'PRIMARY' ? 'Primary' : 'Secondary' }} Bulk Promotion</h2>
          <p class="confirm-subtitle">
            You are about to commit promotion for <strong>{{ previewData.total_students_affected }} students</strong>.
            This operation runs in a single atomic database transaction.
          </p>

          <div class="summary-breakdown-card">
            <div class="breakdown-row">
              <span class="b-lbl">Education Level:</span>
              <strong class="b-val">{{ educationLevel === 'PRIMARY' ? 'Primary Education (Grades 1–8)' : 'Secondary Education (Forms 1–4)' }}</strong>
            </div>
            <div class="breakdown-row">
              <span class="b-lbl">Source Academic Year:</span>
              <span class="b-val">{{ previewData.source_academic_year }}</span>
            </div>
            <div class="breakdown-row">
              <span class="b-lbl">Destination Academic Year:</span>
              <strong class="b-val text-brand">{{ previewData.target_academic_year }}</strong>
            </div>
            <div class="breakdown-row">
              <span class="b-lbl">Promoting to Next Grade:</span>
              <span class="b-val text-success">{{ previewData.total_to_promote }} Students</span>
            </div>
            <div v-if="previewData.total_to_repeat > 0" class="breakdown-row">
              <span class="b-lbl">Repeating Current Class:</span>
              <span class="b-val text-orange">{{ previewData.total_to_repeat }} Students</span>
            </div>
            <div class="breakdown-row">
              <span class="b-lbl">Graduating / Completing:</span>
              <span class="b-val text-purple">{{ previewData.total_to_graduate }} Students</span>
            </div>
            <div class="breakdown-row">
              <span class="b-lbl">Promotion Reason / Audit Note:</span>
              <input v-model="bulkPromotionReason" type="text" class="audit-note-input" />
            </div>
          </div>

          <div class="safety-reassurance-box">
            <div class="reassurance-icon">🛡️</div>
            <div class="reassurance-text">
              <strong>Transactional Safety:</strong> Historical academic grades, previous enrollments, and attendance records remain preserved.
              If any unexpected error occurs, no students will be changed and the transaction will automatically abort.
            </div>
          </div>

          <div class="confirm-action-buttons">
            <button
              type="button"
              class="btn-secondary-action"
              :disabled="isExecutingBulk"
              @click="wizardStep = 2"
            >
              Cancel & Review
            </button>
            <button
              type="button"
              class="btn-success-commit"
              :disabled="isExecutingBulk"
              @click="handleExecuteBulkPromotion"
            >
              <span v-if="isExecutingBulk">Committing Atomic Transaction...</span>
              <span v-else>Confirm & Execute Bulk Promotion</span>
            </button>
          </div>
        </div>
      </div>

      <!-- STEP 4: SUCCESS RECEIPT (Requirement 4) -->
      <div v-if="wizardStep === 4 && successBatch" class="workflow-card">
        <div class="success-receipt-card">
          <div class="receipt-checkmark">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>

          <h2 class="receipt-heading">Class Promotion Completed Successfully!</h2>
          <p class="receipt-lead">
            Students have progressed to academic year <strong>{{ successBatch.target_academic_year }}</strong>.
            All historical enrollments and records are preserved.
          </p>

          <div class="receipt-batch-pill">
            <span class="badge-title">Audit Batch Code:</span>
            <strong class="badge-code">{{ successBatch.batch_code }}</strong>
          </div>

          <div class="receipt-numbers-grid">
            <div class="receipt-stat-box">
              <span class="r-number">{{ successBatch.total_promoted }}</span>
              <span class="r-label">Promoted / Enrolled</span>
            </div>
            <div class="receipt-stat-box">
              <span class="r-number text-purple">{{ successBatch.total_graduated }}</span>
              <span class="r-label">Graduated</span>
            </div>
            <div class="receipt-stat-box">
              <span class="r-number text-gray">{{ successBatch.total_skipped }}</span>
              <span class="r-label">Excluded / Skipped</span>
            </div>
            <div class="receipt-stat-box">
              <span class="r-number text-brand">{{ successBatch.target_academic_year }}</span>
              <span class="r-label">Target Year</span>
            </div>
          </div>

          <div class="receipt-cta-buttons">
            <button
              type="button"
              class="btn-view-audit"
              @click="activeWorkflow = 'history'"
            >
              View Promotion Audit History
            </button>
            <button
              type="button"
              class="btn-restart-wizard"
              @click="resetWizard"
            >
              Perform Another Promotion
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- WORKFLOW 2: PROMOTE A SINGLE CLASS (Requirement 5)                    -->
    <!-- ===================================================================== -->
    <div v-if="activeWorkflow === 'single'" class="workflow-pane single-pane">
      <div class="workflow-card">
        <div class="card-section-head">
          <h2 class="card-title">Promote an Entire Single Class</h2>
          <p class="card-desc">
            Promote all eligible students in one specific class (e.g. <strong>Grade 4A → Grade 5A</strong>) without promoting the whole school.
            Other classes (such as Grade 4B or Grade 4C) will remain completely untouched.
          </p>
        </div>

        <!-- Single Class Step 1: Selection -->
        <div v-if="singleStep === 1" class="single-class-config-grid">
          <div class="form-box">
            <label class="input-lbl required">Select Source Class</label>
            <select v-model="singleSourceClassId" class="select-field">
              <option :value="''">-- Choose Source Class --</option>
              <option
                v-for="c in availableSourceClassesForSingle"
                :key="c.from_class_id"
                :value="c.from_class_id"
              >
                {{ c.from_class_name }} ({{ c.from_class_code }}) • {{ c.student_count }} Students
              </option>
            </select>
          </div>

          <div class="form-box">
            <label class="input-lbl required">Promotion Action</label>
            <select v-model="singleAction" class="select-field">
              <option value="PROMOTE">Promote to Destination Class</option>
              <option value="GRADUATE">Graduate / Complete Cycle</option>
            </select>
          </div>

          <div v-if="singleAction === 'PROMOTE'" class="form-box">
            <label class="input-lbl required">Destination Class (Section Preserving)</label>
            <select v-model="singleTargetClassId" class="select-field">
              <option :value="''">-- Select Destination Class --</option>
              <option
                v-for="tc in availableTargetClassesForSingle"
                :key="tc.id"
                :value="tc.id"
              >
                {{ tc.name }} ({{ tc.code }}) {{ tc.section ? `• Section ${tc.section}` : '' }}
              </option>
            </select>
          </div>

          <div class="form-box">
            <label class="input-lbl required">Academic Years</label>
            <div class="years-pair-row">
              <input v-model="sourceAcademicYear" type="text" class="mini-field" placeholder="From Year" />
              <span class="pair-arrow">→</span>
              <input v-model="targetAcademicYear" type="text" class="mini-field" placeholder="To Year" />
            </div>
          </div>

          <div class="form-box full-span">
            <label class="input-lbl">Promotion Reason / Notes</label>
            <input
              v-model="singleReason"
              type="text"
              class="select-field"
              placeholder="e.g. Annual Class Progression Grade 4A -> 5A"
            />
          </div>

          <div v-if="selectedSingleSourceClass" class="source-class-summary-pill full-span">
            <span>Selected Class: <strong>{{ selectedSingleSourceClass.from_class_name }}</strong></span>
            <span>Section: <strong>{{ selectedSingleSourceClass.section || 'General' }}</strong></span>
            <span>Enrolled Students: <strong>{{ selectedSingleSourceClass.student_count }}</strong></span>
            <span v-if="selectedSingleTargetClass">Destination: <strong>{{ selectedSingleTargetClass.name }}</strong></span>
          </div>

          <div class="card-footer-controls full-span">
            <button
              type="button"
              class="btn-primary-action"
              :disabled="!singleSourceClassId || (singleAction === 'PROMOTE' && !singleTargetClassId) || singleIsLoadingPreview"
              @click="handleSingleClassPreview"
            >
              <span v-if="singleIsLoadingPreview">Loading Students...</span>
              <span v-else>Preview Class Students & Verification</span>
            </button>
          </div>
        </div>

        <!-- Single Class Step 2: Preview & Confirm -->
        <div v-else class="single-class-preview-view">
          <div class="preview-metrics-banner">
            <div>
              <span class="m-lbl">Source Class:</span>
              <strong class="m-val">{{ selectedSingleSourceClass?.from_class_name }}</strong>
            </div>
            <div>
              <span class="m-lbl">Destination:</span>
              <strong class="m-val text-brand">{{ singleAction === 'GRADUATE' ? '🎓 Graduation' : selectedSingleTargetClass?.name }}</strong>
            </div>
            <div>
              <span class="m-lbl">Academic Year:</span>
              <strong class="m-val text-success">{{ sourceAcademicYear }} → {{ targetAcademicYear }}</strong>
            </div>
            <div>
              <span class="m-lbl">Total Students:</span>
              <span class="count-badge-lg">{{ singlePreviewData?.total_students_affected || 0 }}</span>
            </div>
          </div>

          <div class="table-container-wrap" tabindex="0" role="region" aria-label="Class promotion preview table">
            <table class="verification-table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Student Name</th>
                  <th>Current Class</th>
                  <th>Destination</th>
                  <th>Action</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in singlePreviewData?.student_previews || []" :key="s.student_id">
                  <td><span class="adm-pill-text">{{ s.admission_number }}</span></td>
                  <td><strong class="student-name">{{ s.student_name }}</strong></td>
                  <td><span class="class-chip from-chip">{{ s.current_class_name }}</span></td>
                  <td>
                    <span v-if="s.target_class_name" class="class-chip to-chip">{{ s.target_class_name }}</span>
                    <span v-else-if="s.action === 'GRADUATE'" class="text-purple-bold">Graduation</span>
                    <span v-else>—</span>
                  </td>
                  <td><span class="action-tag" :class="s.action.toLowerCase()">{{ s.action }}</span></td>
                  <td><span class="status-chip" :class="s.status.toLowerCase()">{{ s.status }}</span></td>
                </tr>
                <tr v-if="(singlePreviewData?.student_previews || []).length === 0">
                  <td colspan="6" class="empty-table-cell">No active students found in this class.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card-footer-controls split">
            <button type="button" class="btn-secondary-action" @click="singleStep = 1">
              Back to Configuration
            </button>
            <button
              type="button"
              class="btn-success-commit"
              :disabled="singleIsExecuting || !singlePreviewData?.can_execute"
              @click="handleExecuteSingleClassPromotion"
            >
              <span v-if="singleIsExecuting">Executing Single Class Promotion...</span>
              <span v-else>Confirm Promotion for {{ selectedSingleSourceClass?.from_class_name }} ({{ singlePreviewData?.total_students_affected }} Students)</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- WORKFLOW 3: INDIVIDUAL STUDENT PROMOTION (Requirement 6 & 7)          -->
    <!-- ===================================================================== -->
    <div v-if="activeWorkflow === 'individual'" class="workflow-pane individual-pane">
      <div class="workflow-card">
        <div class="card-section-head">
          <h2 class="card-title">Individual Student Promotion & Progression</h2>
          <p class="card-desc">
            Search for an individual student to promote, repeat, transfer, or graduate.
            Individual promotion affects ONLY the selected student and never impacts classmates.
          </p>
        </div>

        <!-- Search Bar -->
        <div class="student-search-control-grid">
          <div class="search-input-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="indSearchQuery"
              type="text"
              placeholder="Search by student name or admission number..."
              class="search-text-field"
              @keyup.enter="handleSearchStudents"
            />
          </div>

          <div class="class-filter-wrap">
            <select v-model="indClassFilter" class="select-field" @change="handleSearchStudents">
              <option :value="''">All Classes</option>
              <option v-for="c in classMappings" :key="c.from_class_id" :value="c.from_class_id">
                {{ c.from_class_name }}
              </option>
            </select>
          </div>

          <button type="button" class="btn-primary-action btn-search" :disabled="indIsSearching" @click="handleSearchStudents">
            <span v-if="indIsSearching">Searching...</span>
            <span v-else>Search Students</span>
          </button>
        </div>

        <!-- Search Results Table -->
        <div class="table-container-wrap mt-4" tabindex="0" role="region" aria-label="Individual student promotion search table">
          <table class="students-search-table">
            <thead>
              <tr>
                <th>Admission #</th>
                <th>Student Full Name</th>
                <th>Education Level</th>
                <th>Current Class & Section</th>
                <th>Suggested Next Class</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in indSearchResults" :key="s.student_id">
                <td><span class="adm-pill-text">{{ s.admission_number }}</span></td>
                <td><strong class="student-name">{{ s.student_name }}</strong></td>
                <td><span class="level-tag" :class="s.current_division?.toLowerCase()">{{ s.current_division }}</span></td>
                <td>
                  <span class="class-chip from-chip">
                    {{ s.current_class_name }} {{ s.current_section ? `(${s.current_section})` : '' }}
                  </span>
                </td>
                <td>
                  <span v-if="s.suggested_next_class_name" class="class-chip to-chip">
                    {{ s.suggested_next_class_name }}
                  </span>
                  <span v-else-if="s.is_terminal" class="text-purple-bold">
                    🎓 Graduation Grade
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <button
                    type="button"
                    class="btn-select-student"
                    @click="handleSelectStudent(s)"
                  >
                    Select for Promotion →
                  </button>
                </td>
              </tr>
              <tr v-if="indSearchResults.length === 0">
                <td colspan="6" class="empty-table-cell">
                  {{ indIsSearching ? 'Searching active students...' : 'Search for a student above to manage promotion.' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Selected Student Promotion Form Card -->
        <div v-if="selectedStudent" class="student-action-config-card">
          <div class="student-profile-header">
            <div class="avatar-circle">👤</div>
            <div class="profile-meta">
              <h3 class="profile-name">{{ selectedStudent.student_name }}</h3>
              <p class="profile-sub">
                Admission: <strong>{{ selectedStudent.admission_number }}</strong> •
                Current Class: <strong>{{ selectedStudent.current_class_name }}</strong> •
                Academic Year: <strong>{{ selectedStudent.current_academic_year || sourceAcademicYear }}</strong>
              </p>
            </div>
            <button class="btn-close-selection" @click="selectedStudent = null">&times;</button>
          </div>

          <div class="promotion-action-form-grid">
            <div class="form-box">
              <label class="input-lbl required">Progression Action (Requirement 7)</label>
              <select v-model="indAction" class="select-field">
                <option value="PROMOTE">Promote to Next Class</option>
                <option value="REPEAT">Repeat Current Class in Next Academic Year</option>
                <option value="TRANSFER">Transfer to Another Class / Section</option>
                <option value="GRADUATE">Mark as Graduated / Completed</option>
                <option value="EXCLUDE">Exclude from Promotion</option>
              </select>
            </div>

            <div v-if="indAction in ['PROMOTE', 'REPEAT', 'TRANSFER']" class="form-box">
              <label class="input-lbl required">Destination Class (Section Preserving)</label>
              <select v-model="indTargetClassId" class="select-field">
                <option :value="''">-- Select Destination Class --</option>
                <option
                  v-for="tc in availableTargetClasses"
                  :key="tc.id"
                  :value="tc.id"
                >
                  {{ tc.name }} ({{ tc.code }}) {{ tc.section ? `• Section ${tc.section}` : '' }}
                </option>
              </select>
            </div>

            <div class="form-box">
              <label class="input-lbl required">Destination Academic Year</label>
              <input v-model="targetAcademicYear" type="text" class="select-field" />
            </div>

            <div class="form-box full-span">
              <label class="input-lbl">Reason / Administrative Justification</label>
              <input v-model="indReason" type="text" class="select-field" placeholder="e.g. End of year academic progression" />
            </div>

            <div class="card-footer-controls full-span">
              <button
                type="button"
                class="btn-success-commit"
                :disabled="(indAction in ['PROMOTE', 'REPEAT', 'TRANSFER'] && !indTargetClassId) || indIsExecuting"
                @click="indConfirmModalOpen = true"
              >
                Proceed to Confirm Individual Promotion
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Individual Confirmation Modal -->
      <div v-if="indConfirmModalOpen && selectedStudent" class="modal-backdrop" @click.self="indConfirmModalOpen = false">
        <div class="modal-dialog-standard">
          <div class="modal-header-standard">
            <h3 class="modal-title">Confirm Individual Student Promotion</h3>
            <button class="modal-close" @click="indConfirmModalOpen = false">&times;</button>
          </div>

          <div class="modal-body-standard">
            <p class="modal-lead-text">
              Are you sure you want to apply <strong>{{ indAction }}</strong> to <strong>{{ selectedStudent.student_name }}</strong>?
            </p>

            <div class="details-list-box">
              <div class="d-row">
                <span class="d-lbl">Student:</span>
                <span class="d-val">{{ selectedStudent.student_name }} ({{ selectedStudent.admission_number }})</span>
              </div>
              <div class="d-row">
                <span class="d-lbl">Current Class:</span>
                <span class="d-val">{{ selectedStudent.current_class_name }}</span>
              </div>
              <div class="d-row">
                <span class="d-lbl">Action:</span>
                <span class="action-tag" :class="indAction.toLowerCase()">{{ indAction }}</span>
              </div>
              <div v-if="indTargetClassId" class="d-row">
                <span class="d-lbl">Destination Class:</span>
                <strong class="d-val text-brand">{{ availableTargetClasses.find(c => c.id === Number(indTargetClassId))?.name }}</strong>
              </div>
              <div class="d-row">
                <span class="d-lbl">Academic Year:</span>
                <strong class="d-val text-success">{{ sourceAcademicYear }} → {{ targetAcademicYear }}</strong>
              </div>
            </div>

            <div class="safe-note-box">
              <span>🛡️ Classmates will NOT be affected. Historical academic records remain intact.</span>
            </div>
          </div>

          <div class="modal-footer-standard">
            <button type="button" class="btn-secondary-action" :disabled="indIsExecuting" @click="indConfirmModalOpen = false">
              Cancel
            </button>
            <button type="button" class="btn-success-commit" :disabled="indIsExecuting" @click="handleConfirmIndividualPromotion">
              <span v-if="indIsExecuting">Applying Promotion...</span>
              <span v-else>Confirm & Save Promotion</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- WORKFLOW 4: PROMOTION HISTORY & AUDIT TRAIL                           -->
    <!-- ===================================================================== -->
    <div v-if="activeWorkflow === 'history'" class="workflow-pane history-pane">
      <div class="workflow-card">
        <div class="card-section-head split-head">
          <div>
            <h2 class="card-title">Promotion History & Audit Trail</h2>
            <p class="card-desc">
              Immutable audit log of all batch promotions, single-class promotions, and individual transitions.
              Safe rollback restores previous student enrollment records.
            </p>
          </div>
          <button type="button" class="btn-secondary-sm" :disabled="isLoadingHistory" @click="loadHistory">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            <span>Refresh Audit Log</span>
          </button>
        </div>

        <!-- History Filter Controls -->
        <div class="preview-filters-box">
          <div class="filter-dropdowns-group">
            <select v-model="historyTypeFilter" class="filter-control">
              <option value="">All Promotion Types</option>
              <option value="BULK_PROMOTION">Bulk Promotion</option>
              <option value="CLASS_LEVEL">Class-Level Promotion</option>
              <option value="INDIVIDUAL_PROMOTION">Individual Promotion</option>
              <option value="INDIVIDUAL_CHANGE">Individual Class Change</option>
            </select>

            <select v-model="historyStatusFilter" class="filter-control">
              <option value="">All Statuses</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="ROLLED_BACK">ROLLED_BACK</option>
            </select>
          </div>
        </div>

        <!-- History Table -->
        <div class="table-container-wrap" tabindex="0" role="region" aria-label="Promotion batch history audit table">
          <table class="history-audit-table">
            <thead>
              <tr>
                <th>Date & Time</th>
                <th>Batch Code</th>
                <th>Type</th>
                <th>Academic Year Range</th>
                <th>Promoted</th>
                <th>Graduated</th>
                <th>Admin User</th>
                <th>Status</th>
                <th>Audit Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in filteredHistoryBatches" :key="b.id">
                <td>
                  <span class="date-text">{{ new Date(b.created_at).toLocaleString() }}</span>
                </td>
                <td>
                  <span class="batch-code-pill">{{ b.batch_code }}</span>
                </td>
                <td>
                  <span class="type-pill">{{ b.promotion_type }}</span>
                </td>
                <td>
                  <span class="year-span">{{ b.source_academic_year }} → {{ b.target_academic_year }}</span>
                </td>
                <td>
                  <strong class="text-success">{{ b.total_promoted }}</strong>
                </td>
                <td>
                  <strong class="text-purple">{{ b.total_graduated }}</strong>
                </td>
                <td>
                  <span class="admin-text">{{ b.created_by_name || 'System Admin' }}</span>
                </td>
                <td>
                  <span class="status-pill" :class="b.status.toLowerCase()">{{ b.status }}</span>
                </td>
                <td>
                  <div class="history-actions-row">
                    <button type="button" class="btn-view-details" @click="openBatchDetails(b)">
                      View Records ({{ b.records_count }})
                    </button>
                    <button
                      v-if="b.status === 'COMPLETED'"
                      type="button"
                      class="btn-rollback-action"
                      @click="openRollbackModal(b)"
                    >
                      Rollback
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredHistoryBatches.length === 0">
                <td colspan="9" class="empty-table-cell">
                  {{ isLoadingHistory ? 'Loading audit records...' : 'No promotion records matching filter.' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- BATCH DETAILS MODAL -->
      <div v-if="isBatchDetailsModalOpen && selectedBatchForDetails" class="modal-backdrop" @click.self="isBatchDetailsModalOpen = false">
        <div class="modal-dialog-large">
          <div class="modal-header-standard">
            <div>
              <h3 class="modal-title">Promotion Batch Details: {{ selectedBatchForDetails.batch_code }}</h3>
              <p class="modal-sub">
                {{ selectedBatchForDetails.source_academic_year }} → {{ selectedBatchForDetails.target_academic_year }} •
                Executed by {{ selectedBatchForDetails.created_by_name || 'Admin' }}
              </p>
            </div>
            <button class="modal-close" @click="isBatchDetailsModalOpen = false">&times;</button>
          </div>

          <div class="modal-body-standard">
            <div v-if="isLoadingBatchDetails" class="modal-loading-box">
              Loading student promotion records...
            </div>
            <div v-else class="table-container-wrap" tabindex="0" role="region" aria-label="Batch student promotion records table">
              <table class="batch-records-table">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Admission #</th>
                    <th>Source Class</th>
                    <th>Target Class</th>
                    <th>Action</th>
                    <th>Status</th>
                    <th>Reason / Justification</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in selectedBatchForDetails.records || []" :key="r.id">
                    <td><strong class="student-name">{{ r.student_name }}</strong></td>
                    <td><span class="adm-pill-text">{{ r.admission_number }}</span></td>
                    <td><span class="class-chip from-chip">{{ r.from_class_name }}</span></td>
                    <td><span class="class-chip to-chip">{{ r.to_class_name || '—' }}</span></td>
                    <td><span class="action-tag" :class="r.action.toLowerCase()">{{ r.action }}</span></td>
                    <td><span class="status-chip" :class="r.status.toLowerCase()">{{ r.status }}</span></td>
                    <td class="text-muted">{{ r.reason || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="modal-footer-standard">
            <button type="button" class="btn-secondary-action" @click="isBatchDetailsModalOpen = false">Close</button>
          </div>
        </div>
      </div>

      <!-- ROLLBACK MODAL -->
      <div v-if="isRollbackModalOpen && batchToRollback" class="modal-backdrop" @click.self="isRollbackModalOpen = false">
        <div class="modal-dialog-danger">
          <div class="modal-header-danger">
            <div class="danger-crest">⚠️</div>
            <div>
              <h3 class="modal-title text-danger">Rollback Promotion Batch</h3>
              <p class="modal-sub">Batch: <strong>{{ batchToRollback.batch_code }}</strong></p>
            </div>
            <button class="modal-close" @click="isRollbackModalOpen = false">&times;</button>
          </div>

          <div v-if="rollbackError" class="notice-banner error-notice mt-2">
            <span>{{ rollbackError }}</span>
          </div>

          <div class="modal-body-standard">
            <p class="rollback-warning-lead">
              Are you sure you want to rollback batch <strong>{{ batchToRollback.batch_code }}</strong>?
            </p>
            <ul class="rollback-points-list">
              <li>Target enrollments created for <strong>{{ batchToRollback.target_academic_year }}</strong> will be safely removed.</li>
              <li>Source enrollments in <strong>{{ batchToRollback.source_academic_year }}</strong> will be restored to ACTIVE.</li>
              <li>Any graduated students will be reactivated.</li>
              <li>Only the records generated by this exact batch are modified.</li>
            </ul>
          </div>

          <div class="modal-footer-standard">
            <button type="button" class="btn-secondary-action" :disabled="isRollingBack" @click="isRollbackModalOpen = false">
              Cancel
            </button>
            <button type="button" class="btn-danger-commit" :disabled="isRollingBack" @click="handleConfirmRollback">
              <span v-if="isRollingBack">Reversing Batch...</span>
              <span v-else>Confirm Rollback</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.promotion-module-root {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Header */
.module-header-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.header-left-cluster {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
  flex: 1 1 240px;
}

.brand-crest-badge {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1e3a8a, #0284c7);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
}

.brand-crest-badge svg {
  width: 24px;
  height: 24px;
}

.title-meta-box {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.module-main-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.02em;
}

.module-sub-desc {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
}

.btn-outline-action {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  height: 38px;
  padding: 0 1rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}

.btn-outline-action:hover {
  background: #f8fafc;
  color: #0f172a;
}

.btn-outline-action svg {
  width: 16px;
  height: 16px;
}

/* Notice Banners */
.notice-banner {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.success-notice { background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }
.error-notice { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
.notice-banner svg { width: 18px; height: 18px; flex-shrink: 0; }
.notice-dismiss { margin-left: auto; background: none; border: none; font-size: 1.25rem; cursor: pointer; color: currentColor; }

/* 1. Education Level Control Bar */
.education-level-control-bar {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.level-segment-wrap {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.65rem;
  width: 100%;
}

.level-segment-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 1.25rem;
  border-radius: 10px;
  border: 2px solid #e2e8f0;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.16s ease;
  text-align: left;
  flex: 1 1 190px;
  min-width: 0;
}

.level-segment-btn:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.level-segment-btn.active {
  background: #eff6ff;
  border-color: #2563eb;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.15);
}

.segment-icon {
  font-size: 1.25rem;
}

.segment-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  display: block;
}

.level-segment-btn.active .segment-title {
  color: #1d4ed8;
}

.segment-sub {
  font-size: 0.6875rem;
  color: #64748b;
  display: block;
}

.active-level-indicator-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  background: #f1f5f9;
  font-size: 0.75rem;
  color: #475569;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
}

/* 2. Workflows Nav Bar */
.workflows-nav-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
  overflow-x: auto;
}

.workflow-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.25rem;
  border: none;
  background: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.workflow-tab-btn:hover {
  color: #0f172a;
}

.workflow-tab-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  background-color: rgba(37, 99, 235, 0.04);
}

.wf-badge {
  font-size: 0.6875rem;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #475569;
  font-weight: 700;
}

.workflow-tab-btn.active .wf-badge {
  background: #dbeafe;
  color: #1d4ed8;
}

/* Stepper Box */
.wizard-stepper-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.65rem 0.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.stepper-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #94a3b8;
  min-width: 0;
}

.step-num-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.stepper-step.active .step-num-circle {
  background: #2563eb;
  color: #ffffff;
}

.stepper-step.active {
  color: #2563eb;
}

.stepper-step.done .step-num-circle {
  background: #10b981;
  color: #ffffff;
}

.stepper-step.done {
  color: #0f172a;
}

.stepper-bar {
  flex: 1;
  height: 2px;
  background: #e2e8f0;
  margin: 0 1rem;
}

.stepper-bar.done {
  background: #10b981;
}

/* Workflow Card */
.workflow-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.card-section-head {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.card-section-head.split-head {
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.card-desc {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
  line-height: 1.45;
}

/* Academic Year Grid */
.academic-year-bridge-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}

.year-input-card {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.year-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #475569;
  letter-spacing: 0.03em;
}

.year-field {
  height: 40px;
  padding: 0 0.85rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
  outline: none;
}

.year-field:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.year-hint {
  font-size: 0.6875rem;
  color: #64748b;
}

.year-progression-arrow {
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.year-progression-arrow svg {
  width: 24px;
  height: 24px;
}

/* Toolbar */
.table-actions-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 38px;
  padding: 0 0.85rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  flex: 1 1 220px;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}

.search-box-pill svg {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
}

.search-inner-input {
  border: none;
  background: none;
  outline: none;
  font-size: 0.8125rem;
  width: 100%;
  height: 100%;
  min-width: 0;
  color: #0f172a;
}

.toolbar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.missing-warn-pill {
  font-size: 0.75rem;
  font-weight: 700;
  color: #b45309;
  background: #fef3c7;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid #fde68a;
}

.btn-secondary-sm {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  height: 36px;
  padding: 0 0.85rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-secondary-sm svg {
  width: 14px;
  height: 14px;
}

/* Tables */
.table-container-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #ffffff;
}

.progression-table,
.verification-table,
.students-search-table,
.history-audit-table,
.batch-records-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

th {
  background: #f8fafc;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 700;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

tr:hover td {
  background: #fcfdfe;
}

.class-col-cell {
  min-width: 180px;
}

.class-name-row {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.class-name {
  font-size: 0.875rem;
  color: #0f172a;
}

.code-badge, .adm-pill-text {
  font-family: monospace;
  font-size: 0.6875rem;
  background: #f1f5f9;
  color: #64748b;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  width: fit-content;
}

.level-tag {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.level-tag.primary { background: #eff6ff; color: #1d4ed8; }
.level-tag.secondary { background: #fdf4ff; color: #86198f; }

.section-tag {
  font-weight: 700;
  color: #334155;
  background: #f8fafc;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.count-pill {
  font-size: 0.75rem;
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
}

.select-container {
  min-width: 170px;
  max-width: 100%;
}

.destination-select, .policy-select, .select-field {
  width: 100%;
  height: 36px;
  padding: 0 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
}

.select-container.has-warning .destination-select {
  border-color: #f59e0b;
  background-color: #fffbeb;
}

.warning-alert-mini {
  font-size: 0.6875rem;
  color: #b45309;
  margin-top: 0.25rem;
  font-weight: 600;
}

.graduation-indicator-box {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #7e22ce;
  background: #faf5ff;
  border: 1px solid #f3e8ff;
  padding: 0.4rem 0.65rem;
  border-radius: 8px;
}

.graduation-indicator-box svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.skip-indicator-box {
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.policy-select.promote { font-weight: 700; color: #1d4ed8; }
.policy-select.graduate { font-weight: 700; color: #7e22ce; }
.policy-select.no_change { color: #64748b; }

.empty-table-cell {
  text-align: center;
  padding: 2.5rem !important;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Card Footer Controls */
.card-footer-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.card-footer-controls.split {
  justify-content: space-between;
}

.btn-primary-action, .btn-success-commit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: 42px;
  padding: 0 1.5rem;
  border-radius: 8px;
  border: none;
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.btn-primary-action { background: #2563eb; }
.btn-primary-action:hover:not(:disabled) { background: #1d4ed8; }

.btn-success-commit { background: #16a34a; }
.btn-success-commit:hover:not(:disabled) { background: #15803d; }

.btn-primary-action:disabled, .btn-success-commit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-secondary-action {
  height: 42px;
  padding: 0 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-ghost-back {
  background: none;
  border: none;
  color: #2563eb;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

/* Metrics Dashboard Grid */
.metrics-dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.85rem;
}

.stat-metric-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.stat-metric-card.stat-danger {
  background: #fef2f2;
  border-color: #fecaca;
}

.stat-lbl {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
}

.stat-num {
  font-size: 1.35rem;
  font-weight: 800;
}

.stat-sub {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.text-brand { color: #2563eb; }
.text-success { color: #16a34a; }
.text-orange { color: #ea580c; }
.text-purple { color: #9333ea; }
.text-gray { color: #64748b; }
.text-danger { color: #dc2626; }

/* Filter Box */
.preview-filters-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-dropdowns-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-control {
  height: 38px;
  padding: 0 0.75rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
}

/* Verification Table specifics */
.class-chip {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.from-chip { background: #f1f5f9; color: #334155; }
.to-chip { background: #eff6ff; color: #1d4ed8; font-weight: 700; }

.action-tag, .action-override-select {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.action-tag.promote, .action-tag.promoted, .action-override-select.promote { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.action-tag.repeat, .action-tag.repeated, .action-override-select.repeat { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.action-tag.transfer, .action-tag.transferred, .action-override-select.transfer { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.action-tag.graduate, .action-tag.graduated, .action-override-select.graduate { background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }
.action-tag.exclude, .action-tag.excluded, .action-override-select.exclude { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

.status-chip {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
}

.status-chip.ready { background: #ecfdf5; color: #065f46; }
.status-chip.graduating { background: #faf5ff; color: #7e22ce; }
.status-chip.repeating { background: #fff7ed; color: #c2410c; }
.status-chip.already_enrolled { background: #fffbeb; color: #b45309; }
.status-chip.validation_error { background: #fef2f2; color: #991b1b; }
.status-chip.completed { background: #ecfdf5; color: #065f46; }
.status-chip.rolled_back { background: #fef2f2; color: #991b1b; }

.val-err-text {
  font-size: 0.6875rem;
  color: #dc2626;
  display: block;
  margin-top: 0.15rem;
  font-weight: 500;
}

.year-subtext {
  font-size: 0.75rem;
  color: #64748b;
}

.year-subtext.highlight {
  font-weight: 700;
  color: #059669;
}

.row-conflict td {
  background: #fffafa !important;
}

/* Confirmation Hero Box */
.confirmation-hero-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 680px;
  margin: 0 auto;
  gap: 1.25rem;
  padding: 1.5rem 0;
}

.confirm-shield-icon {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-shield-icon svg {
  width: 30px;
  height: 30px;
}

.confirm-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.confirm-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.summary-breakdown-card {
  width: 100%;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  text-align: left;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px dashed #e2e8f0;
}

.breakdown-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.b-lbl { color: #64748b; }
.b-val { color: #0f172a; font-weight: 600; }

.audit-note-input {
  width: 50%;
  height: 32px;
  padding: 0 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
}

.safety-reassurance-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  color: #166534;
}

.confirm-action-buttons {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  justify-content: center;
}

/* Success Receipt Card */
.success-receipt-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 640px;
  margin: 0 auto;
  gap: 1.25rem;
  padding: 2rem 0;
}

.receipt-checkmark {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #16a34a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}

.receipt-checkmark svg {
  width: 32px;
  height: 32px;
}

.receipt-heading {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.receipt-lead {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.receipt-batch-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.4rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
}

.badge-code {
  font-family: monospace;
  color: #1d4ed8;
  font-size: 1rem;
}

.receipt-numbers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  width: 100%;
}

.receipt-stat-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.r-number {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
}

.r-label {
  font-size: 0.6875rem;
  color: #64748b;
}

.receipt-cta-buttons {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-view-audit {
  height: 42px;
  padding: 0 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}

.btn-restart-wizard {
  height: 42px;
  padding: 0 1.5rem;
  background: #2563eb;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
}

/* Single Class Grid */
.single-class-config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-box {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-box.full-span {
  grid-column: span 2;
}

.input-lbl {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
}

.input-lbl.required::after {
  content: ' *';
  color: #dc2626;
}

.years-pair-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mini-field {
  flex: 1;
  height: 36px;
  padding: 0 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #0f172a;
}

.source-class-summary-pill {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-size: 0.8125rem;
  color: #1e3a8a;
}

.preview-metrics-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.m-lbl { font-size: 0.6875rem; color: #64748b; text-transform: uppercase; margin-right: 0.35rem; }
.m-val { font-size: 0.875rem; }
.count-badge-lg { background: #eff6ff; color: #2563eb; font-weight: 800; padding: 0.2rem 0.65rem; border-radius: 9999px; }

/* Individual Student Search */
.student-search-control-grid {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input-wrap {
  flex: 2 1 220px;
  min-width: 0;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 40px;
  padding: 0 0.85rem;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  box-sizing: border-box;
}

.search-input-wrap svg { width: 16px; height: 16px; color: #94a3b8; flex-shrink: 0; }
.search-text-field { border: none; background: none; outline: none; width: 100%; min-width: 0; font-size: 0.875rem; color: #0f172a; }

.class-filter-wrap {
  flex: 1 1 180px;
  min-width: 0;
  width: 100%;
}

.btn-select-student {
  height: 32px;
  padding: 0 0.85rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1d4ed8;
  cursor: pointer;
}

.btn-select-student:hover {
  background: #2563eb;
  color: #ffffff;
}

/* Selected Student Action Config Card */
.student-action-config-card {
  margin-top: 1.5rem;
  border: 2px solid #2563eb;
  border-radius: 12px;
  padding: 1.25rem;
  background: #fafcff;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.student-profile-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  border-bottom: 1px solid #dbeafe;
  padding-bottom: 0.85rem;
}

.avatar-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #dbeafe;
  color: #1d4ed8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.profile-meta {
  flex: 1;
}

.profile-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
}

.profile-sub {
  font-size: 0.75rem;
  color: #475569;
  margin: 0.2rem 0 0;
}

.btn-close-selection {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #94a3b8;
}

.promotion-action-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* History table specifics */
.date-text, .admin-text { font-size: 0.75rem; color: #475569; }
.batch-code-pill { font-family: monospace; font-size: 0.75rem; font-weight: 700; background: #eff6ff; color: #1d4ed8; padding: 0.2rem 0.5rem; border-radius: 4px; }
.type-pill { font-size: 0.6875rem; font-weight: 700; background: #f1f5f9; color: #475569; padding: 0.15rem 0.45rem; border-radius: 4px; }
.year-span { font-size: 0.75rem; font-weight: 600; color: #059669; }

.history-actions-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-view-details {
  height: 30px;
  padding: 0 0.65rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}

.btn-rollback-action {
  height: 30px;
  padding: 0 0.65rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 0.6875rem;
  font-weight: 700;
  color: #dc2626;
  cursor: pointer;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-dialog-standard, .modal-dialog-large, .modal-dialog-danger {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-height: calc(100dvh - 24px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  box-sizing: border-box;
}

.modal-dialog-standard { max-width: min(560px, 100%); }
.modal-dialog-large { max-width: min(900px, 100%); }
.modal-dialog-danger { max-width: min(500px, 100%); }

.modal-header-standard, .modal-header-danger {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header-danger {
  background: #fff5f5;
  border-bottom-color: #fed7d7;
}

.danger-crest {
  font-size: 1.5rem;
  margin-right: 0.5rem;
}

.modal-title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0; }
.modal-sub { font-size: 0.75rem; color: #64748b; margin: 0.15rem 0 0; }
.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.modal-body-standard {
  padding: 1.25rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.details-list-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.d-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8125rem;
}

.d-lbl { color: #64748b; }
.d-val { font-weight: 600; color: #0f172a; }

.safe-note-box {
  font-size: 0.75rem;
  color: #166534;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 0.65rem 0.75rem;
  border-radius: 6px;
}

.modal-footer-standard {
  padding: 0.85rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
}

.btn-danger-commit {
  height: 40px;
  padding: 0 1.25rem;
  background: #dc2626;
  border: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
}

.btn-danger-commit:hover { background: #b91c1c; }

.rollback-warning-lead {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.rollback-points-list {
  font-size: 0.8125rem;
  color: #475569;
  padding-left: 1.25rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

@media (max-width: 768px) {
  .academic-year-bridge-grid {
    grid-template-columns: 1fr;
  }
  .year-progression-arrow {
    transform: rotate(90deg);
  }
  .single-class-config-grid, .promotion-action-form-grid {
    grid-template-columns: 1fr;
  }
  .form-box.full-span {
    grid-column: span 1;
  }
  .stepper-bar {
    display: none;
  }
  .wizard-stepper-box {
    justify-content: flex-start;
    gap: 0.65rem 1rem;
  }
}

@media (max-width: 640px) {
  .module-header-card {
    padding: 1rem;
  }
  .header-right-actions,
  .btn-outline-action {
    width: 100%;
    justify-content: center;
  }
  .modal-backdrop {
    padding: 0.5rem;
  }
  .modal-footer-standard {
    flex-wrap: wrap;
  }
  .d-row {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  .confirm-action-buttons {
    flex-wrap: wrap;
  }
  .receipt-numbers-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
