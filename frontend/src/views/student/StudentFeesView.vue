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
    academicYears.value = ['2026/2027'];
    selectedYear.value = '2026/2027';
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
  <div class="portal-page student-fees-view">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content-row">
        <div>
          <h1 class="page-title">My Fees & Financial Ledger</h1>
          <p class="page-subtitle">Your official tuition invoices, verified payment receipts, and institutional account balance.</p>
        </div>

        <!-- Academic Year Selector -->
        <div v-if="academicYears.length > 0" class="year-selector-wrap">
          <label for="fee-year-select" class="selector-lbl">Academic Year:</label>
          <div class="select-container">
            <select
              id="fee-year-select"
              v-model="selectedYear"
              class="year-select"
              @change="loadFees"
            >
              <option v-for="y in academicYears" :key="y" :value="y">{{ y }}</option>
            </select>
            <svg class="select-chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <section v-if="feesData" class="summary-grid" aria-label="Fees Overview Metrics">
      <!-- Total Invoiced -->
      <div class="card summary-card variant-blue">
        <div class="sum-top">
          <span class="sum-label">TOTAL INVOICED</span>
          <div class="sum-icon-box bg-blue-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>
        <span class="sum-val">${{ Number(feesData.summary.total_billed).toFixed(2) }}</span>
        <span class="sum-sub">All Issued Tuition & Invoices</span>
      </div>

      <!-- Total Paid -->
      <div class="card summary-card variant-emerald">
        <div class="sum-top">
          <span class="sum-label">TOTAL PAID TO DATE</span>
          <div class="sum-icon-box bg-emerald-tint">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <span class="sum-val text-emerald-600">${{ Number(feesData.summary.total_paid).toFixed(2) }}</span>
        <span class="sum-sub">Verified Payment Receipts</span>
      </div>

      <!-- Outstanding Balance -->
      <div class="card summary-card" :class="feesData.summary.total_outstanding > 0 ? 'variant-rose' : 'variant-emerald'">
        <div class="sum-top">
          <span class="sum-label">OUTSTANDING BALANCE</span>
          <div class="sum-icon-box" :class="feesData.summary.total_outstanding > 0 ? 'bg-rose-tint' : 'bg-emerald-tint'">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <span class="sum-val" :class="feesData.summary.total_outstanding > 0 ? 'text-rose-600' : 'text-emerald-600'">
          ${{ Number(feesData.summary.total_outstanding).toFixed(2) }}
        </span>
        <span class="sum-sub font-semibold" :class="feesData.summary.total_outstanding > 0 ? 'text-rose-600' : 'text-emerald-600'">
          {{ feesData.summary.total_outstanding > 0 ? 'Due to School Bursar Office' : '✓ Account is fully paid' }}
        </span>
      </div>
    </section>

    <!-- Cleared Account Banner -->
    <div v-if="feesData && feesData.summary.is_cleared" class="card cleared-banner">
      <div class="cleared-icon-wrap">
        <svg class="cleared-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="cleared-text">
        <strong class="cleared-title">FINANCIAL ACCOUNT IN GOOD STANDING</strong>
        <p class="cleared-desc">
          All scheduled tuition fees and invoices for this academic session have been fully settled. Thank you for your prompt payments.
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
      <div class="error-icon-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <line x1="12" y1="8" x2="12" y2="12" stroke-width="2" stroke-linecap="round" />
          <line x1="12" y1="16" x2="12.01" y2="16" stroke-width="2" stroke-linecap="round" />
        </svg>
      </div>
      <div class="error-content">
        <p class="error-title">Unable to Load Fee Records</p>
        <p class="error-desc">{{ errorMessage }}</p>
      </div>
      <button type="button" class="retry-btn" @click="loadFees">Try Again</button>
    </div>

    <!-- Content Stack -->
    <div v-else-if="feesData" class="content-stack">
      <!-- Invoices Section -->
      <section class="section-container" aria-label="Tuition Invoices">
        <div class="section-title-row">
          <div>
            <h3 class="section-title">Tuition Invoices & Billing Breakdown</h3>
            <p class="section-sub">Detailed fee structures, applied discounts, and payment history.</p>
          </div>
          <span class="badge-count">{{ feesData.fees.length }} Invoices</span>
        </div>

        <div v-if="feesData.fees.length === 0" class="card empty-card">
          <div class="empty-icon-wrap">
            <svg class="empty-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h4 class="empty-title">No Fee Invoices Recorded</h4>
          <p class="empty-desc">You do not have any tuition invoices issued for academic year {{ selectedYear }}.</p>
        </div>

        <div v-else class="invoices-list">
          <div v-for="f in feesData.fees" :key="f.id" class="card invoice-card">
            <!-- Invoice Header -->
            <div class="invoice-header">
              <div class="invoice-main-info">
                <div class="inv-num-pill">INVOICE #INV-{{ f.id.toString().padStart(5, '0') }}</div>
                <h4 class="fee-name">{{ f.fee_structure?.name || 'Tuition Fee' }}</h4>
                <div class="fee-meta">
                  <span class="meta-tag">Due Date: <strong>{{ formatDate(f.due_date) }}</strong></span>
                  <span class="meta-sep">&bull;</span>
                  <span class="meta-tag">Session: {{ f.fee_structure?.academic_year || selectedYear }}</span>
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
                <span class="b-lbl">GROSS AMOUNT</span>
                <span class="b-val font-semibold">${{ Number(f.amount_due).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">DISCOUNT / WAIVER</span>
                <span class="b-val text-slate-500">${{ Number(f.discount_amount).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">NET BILLED</span>
                <span class="b-val font-bold text-slate-900">${{ Number(f.net_amount).toFixed(2) }}</span>
              </div>
              <div class="b-item">
                <span class="b-lbl">PAID TO DATE</span>
                <span class="b-val font-bold text-emerald-600">${{ Number(f.total_paid).toFixed(2) }}</span>
              </div>
              <div class="b-item highlight-box" :class="f.balance_remaining > 0 ? 'box-due' : 'box-cleared'">
                <span class="b-lbl">BALANCE REMAINING</span>
                <span class="b-val font-bold" :class="f.balance_remaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                  ${{ Number(f.balance_remaining).toFixed(2) }}
                </span>
              </div>
            </div>

            <!-- Payment Receipts Nested -->
            <div v-if="f.payments && f.payments.length > 0" class="receipts-wrapper">
              <div class="receipts-header-row">
                <svg class="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <h5 class="receipts-heading">Verified Payment Transactions ({{ f.payments.length }})</h5>
              </div>

              <div class="receipts-cards-grid">
                <div v-for="p in f.payments" :key="p.id" class="receipt-card">
                  <div class="r-top">
                    <span class="r-num">{{ p.receipt_number }}</span>
                    <strong class="r-amt text-emerald-600">+${{ Number(p.amount_paid).toFixed(2) }}</strong>
                  </div>
                  <div class="r-meta-row">
                    <span>Method: <strong>{{ p.payment_method }}</strong></span>
                    <span v-if="p.reference_number" class="r-ref">&bull; Ref: {{ p.reference_number }}</span>
                  </div>
                  <div class="r-date">Recorded: {{ formatDate(p.payment_date) }}</div>
                </div>
              </div>
            </div>

            <div v-else class="no-payments-note">
              <svg class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>No payments recorded against this invoice yet.</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.portal-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.page-header {
  margin-bottom: 0.25rem;
}

.header-content-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
}

.page-subtitle {
  font-size: 0.85rem;
  color: #64748B;
  margin: 0.25rem 0 0 0;
}

/* Academic Year Selector */
.year-selector-wrap {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.selector-lbl {
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
}

.select-container {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.year-select {
  appearance: none;
  background-color: #FFFFFF;
  border: 1px solid #CBD5E1;
  border-radius: 10px;
  padding: 0.45rem 2.25rem 0.45rem 0.85rem;
  font-size: 0.84rem;
  font-weight: 600;
  color: #1E293B;
  cursor: pointer;
  outline: none;
  transition: all 0.15s ease;
}

.year-select:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.select-chevron {
  position: absolute;
  right: 0.65rem;
  width: 16px;
  height: 16px;
  color: #64748B;
  pointer-events: none;
}

/* Base Card Style */
.card {
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

/* Summary Grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.summary-card {
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.sum-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.sum-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #64748B;
}

.sum-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sum-icon-box svg {
  width: 18px;
  height: 18px;
}

.bg-blue-tint { background: #EFF6FF; color: #2563EB; }
.bg-emerald-tint { background: #ECFDF5; color: #059669; }
.bg-rose-tint { background: #FEF2F2; color: #DC2626; }

.sum-val {
  font-size: 1.65rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.15;
  margin-bottom: 0.35rem;
}

.sum-sub {
  font-size: 0.74rem;
  color: #64748B;
}

/* Cleared Banner */
.cleared-banner {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  border-left: 4px solid #10B981;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.cleared-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #D1FAE5;
  color: #059669;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cleared-icon {
  width: 20px;
  height: 20px;
}

.cleared-title {
  font-size: 0.78rem;
  font-weight: 800;
  color: #065F46;
  letter-spacing: 0.03em;
  display: block;
}

.cleared-desc {
  font-size: 0.78rem;
  color: #047857;
  margin: 0.2rem 0 0 0;
}

/* Invoices Section */
.content-stack {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.section-sub {
  font-size: 0.78rem;
  color: #64748B;
  margin: 0.2rem 0 0 0;
}

.badge-count {
  font-size: 0.75rem;
  font-weight: 700;
  background: #F1F5F9;
  color: #475569;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  border: 1px solid #E2E8F0;
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
}

.invoice-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #F1F5F9;
  flex-wrap: wrap;
}

.inv-num-pill {
  font-size: 0.7rem;
  font-weight: 800;
  color: #2563EB;
  background: #EFF6FF;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 0.35rem;
}

.fee-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0 0 0.25rem 0;
}

.fee-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  color: #64748B;
}

.meta-tag strong {
  color: #1E293B;
}

.meta-sep {
  color: #CBD5E1;
}

/* Financial Breakdown Grid (5 columns) */
.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.85rem;
  background: #F8FAFC;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
}

.b-item {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.b-lbl {
  font-size: 0.66rem;
  font-weight: 700;
  color: #64748B;
  letter-spacing: 0.04em;
  margin-bottom: 0.25rem;
}

.b-val {
  font-size: 1.05rem;
  color: #1E293B;
}

.highlight-box {
  padding: 0.4rem 0.65rem;
  border-radius: 8px;
}

.box-due {
  background: #FEF2F2;
  border: 1px solid #FECACA;
}

.box-cleared {
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
}

/* Payment Receipts */
.receipts-wrapper {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 1rem;
}

.receipts-header-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.75rem;
}

.receipts-heading {
  font-size: 0.82rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.receipts-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.receipt-card {
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.r-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.r-num {
  font-size: 0.74rem;
  font-weight: 700;
  color: #0F172A;
  font-family: monospace;
}

.r-amt {
  font-size: 0.86rem;
  font-weight: 800;
}

.r-meta-row {
  font-size: 0.72rem;
  color: #475569;
}

.r-ref {
  color: #64748B;
}

.r-date {
  font-size: 0.68rem;
  color: #94A3B8;
  margin-top: 0.15rem;
}

.no-payments-note {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.78rem;
  color: #64748B;
  font-style: italic;
  padding: 0.35rem 0;
}

/* Loading, Error, Empty */
.loading-card,
.empty-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748B;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E2E8F0;
  border-top-color: #1E3A8A;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.65rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background-color: #FEF2F2;
  border-color: #FECACA;
  color: #991B1B;
}

.error-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #FEE2E2;
  color: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-icon-box svg {
  width: 22px;
  height: 22px;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}

.error-desc {
  font-size: 0.82rem;
  margin: 0.2rem 0 0 0;
  color: #B91C1C;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background-color: #DC2626;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.empty-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #F1F5F9;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.empty-icon {
  width: 26px;
  height: 26px;
}

.empty-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.82rem;
  color: #64748B;
  max-width: 420px;
  margin: 0;
}

/* Responsive Media Queries */
@media (max-width: 1024px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .breakdown-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
    gap: 0.85rem;
  }
  .breakdown-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .invoice-card {
    padding: 1.15rem;
  }
}

@media (max-width: 480px) {
  .breakdown-grid {
    grid-template-columns: 1fr;
    gap: 0.65rem;
  }
}
</style>
