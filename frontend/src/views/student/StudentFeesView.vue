<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { studentPortalService } from '../../services/studentPortalService';
import { StudentFeesData } from '../../types/studentPortal';
import StatusBadge from '../../components/common/StatusBadge.vue';

const feesData = ref<StudentFeesData | null>(null);
const academicYears = ref<string[]>([]);
const selectedYear = ref<string>('');
const isLoading = ref(true);
const errorMessage = ref('');

async function loadFees() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    feesData.value = await studentPortalService.getMyFees(selectedYear.value || undefined);
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load student fee ledger.';
  } finally {
    isLoading.value = false;
  }
}

async function initPage() {
  try {
    academicYears.value = await studentPortalService.getAcademicYears();
    if (academicYears.value.length > 0) {
      selectedYear.value = academicYears.value[0];
    }
  } catch {
    academicYears.value = ['2025-2026'];
    selectedYear.value = '2025-2026';
  }
  await loadFees();
}

function formatDate(dateStr?: string | null) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch {
    return dateStr;
  }
}

onMounted(() => {
  initPage();
});
</script>

<template>
  <div class="portal-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content-row">
        <div>
          <h1 class="page-title">My Fees & Financial Ledger</h1>
          <p class="page-subtitle">Your official tuition invoices, verified payment receipts, and outstanding institutional account balance.</p>
        </div>

        <!-- Academic Year Selector -->
        <div v-if="academicYears.length > 0" class="year-selector-wrap">
          <label for="fee-year-select" class="selector-lbl">Academic Year:</label>
          <select
            id="fee-year-select"
            v-model="selectedYear"
            class="year-select"
            @change="loadFees"
          >
            <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div v-if="feesData" class="summary-grid">
      <div class="summary-card card blue">
        <span class="sum-label">TOTAL INVOICED</span>
        <span class="sum-val">${{ Number(feesData.summary.total_billed).toFixed(2) }}</span>
        <span class="sum-sub">All Issued Tuition & Fees</span>
      </div>

      <div class="summary-card card green">
        <span class="sum-label">TOTAL PAID</span>
        <span class="sum-val text-emerald">${{ Number(feesData.summary.total_paid).toFixed(2) }}</span>
        <span class="sum-sub">Verified Payment Receipts</span>
      </div>

      <div class="summary-card card" :class="feesData.summary.total_outstanding > 0 ? 'red' : 'green'">
        <span class="sum-label">OUTSTANDING BALANCE</span>
        <div class="balance-display-row">
          <span class="sum-val" :class="feesData.summary.total_outstanding > 0 ? 'text-rose' : 'text-emerald'">
            ${{ Number(feesData.summary.total_outstanding).toFixed(2) }}
          </span>
        </div>
        <span class="sum-sub font-semibold" :class="feesData.summary.total_outstanding > 0 ? 'text-rose' : 'text-emerald'">
          {{ feesData.summary.total_outstanding > 0 ? 'Due to School Finance Office' : '✓ All fees are paid' }}
        </span>
      </div>
    </div>

    <!-- Clear / Zero Balance Banner if no fees are owed -->
    <div v-if="feesData && feesData.summary.is_cleared" class="card cleared-banner">
      <div class="cleared-icon-wrap">
        <svg class="cleared-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="cleared-text">
        <strong class="cleared-title">NO OUTSTANDING BALANCE &bull; ACCOUNT IN GOOD STANDING</strong>
        <p class="cleared-desc">
          All scheduled tuition fees and invoices for this period have been fully settled. Thank you for your prompt payments.
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card loading-card">
      <div class="spinner" />
      <span>Querying financial ledger from PostgreSQL...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="card error-card">
      <p class="error-title">Unable to Load Fee Records</p>
      <p class="error-desc">{{ errorMessage }}</p>
      <button class="retry-btn" @click="loadFees">Try Again</button>
    </div>

    <!-- Content Stack -->
    <div v-else-if="feesData" class="content-stack">
      <!-- Invoices Section -->
      <div class="section-container">
        <div class="section-title-row">
          <h3 class="section-title">Tuition Invoices</h3>
          <span class="badge-count">{{ feesData.fees.length }} Invoices</span>
        </div>

        <div v-if="feesData.fees.length === 0" class="card empty-card">
          <p class="empty-title">No Fee Invoices Recorded</p>
          <p class="empty-desc">You do not have any tuition invoices issued for academic year {{ selectedYear }}.</p>
        </div>

        <div v-else class="invoices-list">
          <div v-for="f in feesData.fees" :key="f.id" class="card invoice-card">
            <!-- Invoice Header -->
            <div class="invoice-header">
              <div class="invoice-main-info">
                <span class="inv-num">INVOICE #INV-{{ f.id.toString().padStart(5, '0') }}</span>
                <h4 class="fee-name">{{ f.fee_structure?.name || 'Tuition Fee' }}</h4>
                <div class="fee-meta">
                  <span>Due Date: <strong>{{ formatDate(f.due_date) }}</strong></span>
                  <span class="meta-sep">&bull;</span>
                  <span>Academic Year: {{ f.fee_structure?.academic_year || selectedYear }}</span>
                </div>
              </div>
              <div class="invoice-status">
                <StatusBadge
                  :status="f.status"
                  :variant="f.status === 'PAID' ? 'success' : f.status === 'PARTIALLY_PAID' ? 'warning' : 'danger'"
                />
              </div>
            </div>

            <!-- Financial Breakdown Grid -->
            <div class="breakdown-grid">
              <div class="b-item">
                <span class="b-lbl">AMOUNT DUE</span>
                <span class="b-val">${{ Number(f.amount_due).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">DISCOUNT</span>
                <span class="b-val text-muted">${{ Number(f.discount_amount).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">NET BILLED</span>
                <span class="b-val font-bold">${{ Number(f.net_amount).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">PAID TO DATE</span>
                <span class="b-val text-emerald font-bold">${{ Number(f.total_paid).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">BALANCE REMAINING</span>
                <span class="b-val font-bold" :class="f.balance_remaining > 0 ? 'text-rose' : 'text-emerald'">
                  ${{ Number(f.balance_remaining).toFixed(2) }}
                </span>
              </div>
            </div>

            <!-- Payment Receipts Nested -->
            <div v-if="f.payments && f.payments.length > 0" class="receipts-wrapper">
              <h5 class="receipts-heading">Verified Payment Transactions</h5>
              <div class="receipts-cards-grid">
                <div v-for="p in f.payments" :key="p.id" class="receipt-card">
                  <div class="r-top">
                    <span class="r-num">{{ p.receipt_number }}</span>
                    <strong class="r-amt text-emerald">+${{ Number(p.amount_paid).toFixed(2) }}</strong>
                  </div>
                  <div class="r-meta-row">
                    <span>Method: <strong>{{ p.payment_method }}</strong></span>
                    <span v-if="p.reference_number">&bull; Ref: {{ p.reference_number }}</span>
                  </div>
                  <div class="r-date">Recorded: {{ formatDate(p.payment_date) }}</div>
                </div>
              </div>
            </div>

            <div v-else class="no-payments-note">
              No payments recorded against this invoice yet.
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
}

.header-content-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
}

.selector-lbl {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
}

.year-select {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.summary-card {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  border-left: 4px solid var(--brand-primary);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left-width: 4px;
}

.summary-card.blue { border-left-color: #0284c7; }
.summary-card.green { border-left-color: #10b981; }
.summary-card.red { border-left-color: #ef4444; }

.sum-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.sum-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
}

.sum-sub {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.text-emerald { color: #10b981; }
.text-rose { color: #ef4444; }

/* Cleared Banner */
.cleared-banner {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(2, 132, 199, 0.05) 100%);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-left: 4px solid #10b981;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.cleared-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(16, 185, 129, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cleared-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #10b981;
}

.cleared-title {
  font-size: 0.85rem;
  color: #10b981;
  letter-spacing: 0.05em;
  display: block;
}

.cleared-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin: 0.2rem 0 0 0;
}

/* Invoices List */
.content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.section-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.badge-count {
  font-size: 0.75rem;
  font-weight: 700;
  background-color: var(--bg-surface-secondary);
  color: var(--text-muted);
  padding: 0.2rem 0.55rem;
  border-radius: 12px;
}

.invoices-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.invoice-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-top: 3px solid #10b981;
}

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.inv-num {
  font-size: 0.72rem;
  font-family: monospace;
  font-weight: 700;
  color: #10b981;
  letter-spacing: 0.05em;
  display: block;
}

.fee-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0.2rem 0;
}

.fee-meta {
  font-size: 0.82rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.fee-meta strong {
  color: var(--text-primary);
}

.meta-sep {
  color: var(--border-subtle);
}

/* Breakdown Grid */
.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
  background: var(--bg-surface-secondary);
  padding: 1rem;
  border-radius: 8px;
}

.b-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.b-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.b-val {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* Receipts */
.receipts-wrapper {
  border-top: 1px solid var(--border-subtle);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.receipts-heading {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.receipts-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.receipt-card {
  background: var(--bg-surface-secondary);
  border: 1px solid var(--border-subtle);
  border-left: 3px solid #10b981;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.r-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.r-num {
  font-size: 0.75rem;
  font-family: monospace;
  font-weight: 700;
  color: var(--text-primary);
}

.r-amt {
  font-size: 0.95rem;
  font-weight: 800;
}

.r-meta-row {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.r-date {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.no-payments-note {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-style: italic;
  padding: 0.5rem 0;
}

/* Common states */
.loading-card, .error-card, .empty-card {
  padding: 3.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-subtle);
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-title, .error-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.empty-desc, .error-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

.retry-btn {
  background-color: #0f172a;
  color: #fff;
  border: 1px solid #334155;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
  .breakdown-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .breakdown-grid {
    grid-template-columns: 1fr;
  }
}
</style>
