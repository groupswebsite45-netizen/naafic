<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  isOpen: boolean;
  className: string;
  examName: string;
  academicYear: string;
  studentsCount: number;
  subjectsCount: number;
  expectedResults: number;
  approvedResults: number;
  pendingResults: number;
  isProcessing?: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', releaseType: 'FULL' | 'PARTIAL', notes?: string): void;
}>();

const releaseType = ref<'FULL' | 'PARTIAL'>('FULL');
const notes = ref('');

const isFullyApproved = computed(() => {
  return props.approvedResults >= props.expectedResults && props.expectedResults > 0;
});

function handleConfirm() {
  emit('confirm', releaseType.value, notes.value.trim() || undefined);
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-dialog" role="dialog" aria-modal="true">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-icon-wrap" :class="{ 'ready': isFullyApproved }">
          <svg class="header-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
        </div>
        <div>
          <h3 class="modal-title">Release Results for {{ className }}</h3>
          <p class="modal-subtitle">{{ examName }} ({{ academicYear }})</p>
        </div>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <!-- Readiness Banner -->
        <div v-if="isFullyApproved" class="status-banner ready">
          <svg class="banner-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <strong>Ready for Full Class Release:</strong>
            <p>All {{ expectedResults }} expected results across {{ subjectsCount }} subjects have been approved by Admin.</p>
          </div>
        </div>

        <div v-else class="status-banner warning">
          <svg class="banner-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <strong>Class is not ready for full result release:</strong>
            <p>
              {{ pendingResults }} results are still pending teacher completion or admin review. Full class release is blocked by school policy.
            </p>
          </div>
        </div>

        <!-- Summary Grid -->
        <div class="release-summary-grid">
          <div class="summary-box">
            <span class="box-label">Students</span>
            <span class="box-val">{{ studentsCount }}</span>
          </div>
          <div class="summary-box">
            <span class="box-label">Subjects</span>
            <span class="box-val">{{ subjectsCount }}</span>
          </div>
          <div class="summary-box">
            <span class="box-label">Expected</span>
            <span class="box-val">{{ expectedResults }}</span>
          </div>
          <div class="summary-box">
            <span class="box-label">Approved</span>
            <span class="box-val text-blue">{{ approvedResults }}</span>
          </div>
          <div class="summary-box">
            <span class="box-label">Pending</span>
            <span class="box-val" :class="{ 'text-red': pendingResults > 0 }">{{ pendingResults }}</span>
          </div>
        </div>

        <!-- Mode Selection if Incomplete -->
        <div v-if="!isFullyApproved && approvedResults > 0" class="mode-select-wrap">
          <label class="mode-option" :class="{ 'active': releaseType === 'PARTIAL' }">
            <input
              v-model="releaseType"
              type="radio"
              value="PARTIAL"
              name="releaseType"
            />
            <div class="option-details">
              <span class="option-title">Release Approved Results Only ({{ approvedResults }} Results)</span>
              <span class="option-desc">
                This will publish only the {{ approvedResults }} currently approved results. The remaining {{ pendingResults }} results will stay hidden until approved.
              </span>
            </div>
          </label>
        </div>

        <div class="notes-field">
          <label class="notes-label" for="releaseNotes">RELEASE NOTES (OPTIONAL)</label>
          <input
            id="releaseNotes"
            v-model="notes"
            type="text"
            class="notes-input"
            placeholder="e.g., Official release sanctioned by Academic Board."
            :disabled="isProcessing"
          />
        </div>

        <p class="audit-notice">
          <strong>Database Audit:</strong> A release batch record (e.g. <code>RB-{{ academicYear.split('-')[0] }}-0001</code>) will be created in PostgreSQL with your authenticated Admin ID and timestamp.
        </p>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button
          type="button"
          class="btn-cancel"
          :disabled="isProcessing"
          @click="emit('close')"
        >
          Cancel
        </button>

        <button
          v-if="isFullyApproved"
          type="button"
          class="btn-release"
          :disabled="isProcessing"
          @click="handleConfirm"
        >
          {{ isProcessing ? 'Releasing...' : `Release ${className} Results` }}
        </button>

        <button
          v-else-if="approvedResults > 0"
          type="button"
          class="btn-partial"
          :disabled="isProcessing || releaseType !== 'PARTIAL'"
          @click="handleConfirm"
        >
          {{ isProcessing ? 'Releasing...' : `Release ${approvedResults} Approved Results` }}
        </button>

        <button
          v-else
          type="button"
          class="btn-disabled"
          disabled
        >
          Full Release Blocked
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 70;
  padding: 1rem;
}

.modal-dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  width: 100%;
  max-width: 540px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
  padding: 1.25rem;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-wrap {
  width: 40px;
  height: 40px;
  background-color: rgba(245, 158, 11, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.header-icon-wrap.ready {
  background-color: rgba(16, 185, 129, 0.15);
}

.header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #f59e0b;
}

.header-icon-wrap.ready .header-icon {
  color: #10b981;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0.2rem 0 0 0;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-banner {
  border-radius: 8px;
  padding: 0.85rem 1rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  font-size: 0.8125rem;
}

.status-banner.ready {
  background-color: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #a7f3d0;
}

.status-banner.warning {
  background-color: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fde68a;
}

.banner-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.status-banner.ready .banner-icon { color: #10b981; }
.status-banner.warning .banner-icon { color: #f59e0b; }

.status-banner p {
  margin: 0.25rem 0 0 0;
  font-size: 0.75rem;
  line-height: 1.4;
}

.release-summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
}

.summary-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.box-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

.box-val {
  font-size: 1rem;
  font-weight: 800;
  color: #f8fafc;
}

.text-blue { color: #38bdf8; }
.text-red { color: #f87171; }

.mode-select-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mode-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.85rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.mode-option.active {
  border-color: #0284c7;
  background-color: rgba(2, 132, 199, 0.08);
}

.option-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.option-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffffff;
}

.option-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.35;
}

.notes-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.notes-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: #cbd5e1;
  letter-spacing: 0.06em;
}

.notes-input {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  color: #ffffff;
  font-size: 0.8125rem;
  outline: none;
}

.notes-input:focus {
  border-color: #0284c7;
}

.audit-notice {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.audit-notice code {
  color: #38bdf8;
  background-color: #0f172a;
  padding: 0.1rem 0.3rem;
  border-radius: 4px;
}

.modal-footer {
  padding: 1rem 1.25rem;
  background-color: #0f172a;
  border-top: 1px solid #334155;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  background-color: #334155;
  color: #f8fafc;
  border: none;
  padding: 0.55rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-release {
  background-color: #059669;
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-release:hover {
  background-color: #047857;
}

.btn-partial {
  background-color: #0284c7;
  color: #ffffff;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-partial:hover {
  background-color: #0369a1;
}

.btn-disabled {
  background-color: #334155;
  color: #64748b;
  border: none;
  padding: 0.55rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: not-allowed;
}
</style>
