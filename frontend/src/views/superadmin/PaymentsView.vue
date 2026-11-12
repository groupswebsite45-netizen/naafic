<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { superAdminService } from '../../services/superAdminService';
import { InstitutionPayment, Institution } from '../../types/institution';

const payments = ref<InstitutionPayment[]>([]);
const institutions = ref<Institution[]>([]);
const isLoading = ref(true);

// New Payment Modal
const paymentModalOpen = ref(false);
const payInstId = ref<number | null>(null);
const payAmount = ref<number>(350);
const payMethod = ref<string>('EVC Plus');
const payNotes = ref<string>('');
const isSaving = ref(false);

async function loadData() {
  isLoading.value = true;
  try {
    const [pList, iList] = await Promise.all([
      superAdminService.getPayments(),
      superAdminService.getInstitutions(),
    ]);
    payments.value = pList;
    institutions.value = iList;
  } catch (err) {
    console.error('Failed to load payments:', err);
  } finally {
    isLoading.value = false;
  }
}

async function handleRecordPayment() {
  if (!payInstId.value) return;
  isSaving.value = true;
  try {
    await superAdminService.recordPayment({
      institution_id: payInstId.value,
      amount: payAmount.value,
      payment_method: payMethod.value,
      notes: payNotes.value,
      status: 'Completed',
    });
    paymentModalOpen.value = false;
    await loadData();
    alert('Payment successfully recorded!');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to record payment.');
  } finally {
    isSaving.value = false;
  }
}

function formatDate(dStr?: string) {
  if (!dStr) return '-';
  try {
    return new Date(dStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dStr;
  }
}

// Stats
const totalRevenue = computed(() => {
  return payments.value.reduce((acc, p) => acc + (p.amount || 0), 0);
});
const completedCount = computed(() => {
  return payments.value.filter(p => (p.status || '').toLowerCase() === 'completed').length;
});

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="sap-page">
    <!-- Header -->
    <div class="sap-header">
      <div>
        <h1 class="sap-title">Institutional Payments & Billing</h1>
        <p class="sap-sub">Track real-time SaaS subscription transactions, setup fees, and invoices.</p>
      </div>

      <button class="sap-btn-record" @click="paymentModalOpen = true">
        <svg class="w-5 h-5 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Record Offline Payment</span>
      </button>
    </div>

    <!-- Overview Stats Grid -->
    <div class="sap-stats-grid">
      <div class="sap-stat-card">
        <div class="sap-stat-icon bg-emerald-50 text-emerald-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="1" x2="12" y2="23" />
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </div>
        <div>
          <span class="sap-stat-label">Total Volume Collected</span>
          <span class="sap-stat-val text-emerald-600">${{ totalRevenue.toLocaleString() }}</span>
        </div>
      </div>

      <div class="sap-stat-card">
        <div class="sap-stat-icon bg-blue-50 text-blue-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </div>
        <div>
          <span class="sap-stat-label">Settled Transactions</span>
          <span class="sap-stat-val text-slate-800">{{ completedCount }}</span>
        </div>
      </div>

      <div class="sap-stat-card">
        <div class="sap-stat-icon bg-purple-50 text-purple-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="5" width="20" height="14" rx="2" />
            <line x1="2" y1="10" x2="22" y2="10" />
          </svg>
        </div>
        <div>
          <span class="sap-stat-label">Primary Gateway</span>
          <span class="sap-stat-val text-purple-600 text-lg">EVC Plus & Bank</span>
        </div>
      </div>
    </div>

    <!-- Desktop Payments Table Card -->
    <div class="sap-card sap-desktop-only">
      <div class="sap-table-wrap">
        <table class="sap-table">
          <thead>
            <tr>
              <th>Reference & Invoice</th>
              <th>Institution</th>
              <th>Amount (USD)</th>
              <th>Payment Method</th>
              <th>Payment Date</th>
              <th>Status</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pay in payments" :key="pay.id">
              <td>
                <div class="font-mono font-bold text-slate-800 text-xs">{{ pay.reference }}</div>
                <div class="text-xs text-slate-400 mt-0.5">{{ pay.invoice_number || 'INV-Auto' }}</div>
              </td>
              <td>
                <div class="font-bold text-slate-900">{{ pay.institution_name }}</div>
              </td>
              <td>
                <span class="font-extrabold text-emerald-600 text-base">${{ pay.amount.toFixed(2) }}</span>
              </td>
              <td>
                <span class="sap-method-badge">{{ pay.payment_method }}</span>
              </td>
              <td class="text-slate-600 text-xs">{{ formatDate(pay.payment_date) }}</td>
              <td>
                <span
                  class="sap-status-pill"
                  :class="pay.status.toLowerCase() === 'completed' ? 'status-completed' : 'status-pending'"
                >
                  {{ pay.status }}
                </span>
              </td>
              <td class="text-xs text-slate-500 max-w-xs truncate">{{ pay.notes || '-' }}</td>
            </tr>

            <tr v-if="!payments.length && !isLoading">
              <td colspan="7" class="text-center py-12 text-slate-400">
                No financial transactions found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards View (<768px) -->
    <div class="sap-mobile-cards sap-mobile-only">
      <div
        v-for="pay in payments"
        :key="`mp-${pay.id}`"
        class="sap-mobile-card"
      >
        <div class="sap-mcard-top">
          <div>
            <div class="font-bold text-slate-900 text-sm">{{ pay.institution_name }}</div>
            <div class="text-xs text-slate-400 font-mono">{{ pay.reference }}</div>
          </div>
          <span class="font-extrabold text-emerald-600 text-base">${{ pay.amount.toFixed(2) }}</span>
        </div>

        <div class="sap-mcard-body">
          <div class="sap-mcard-row">
            <span class="sap-method-badge">{{ pay.payment_method }}</span>
            <span
              class="sap-status-pill"
              :class="pay.status.toLowerCase() === 'completed' ? 'status-completed' : 'status-pending'"
            >
              {{ pay.status }}
            </span>
          </div>
          <div class="sap-mcard-row text-xs text-slate-500">
            <span>Date: {{ formatDate(pay.payment_date) }}</span>
            <span>{{ pay.invoice_number || 'INV-Auto' }}</span>
          </div>
          <p v-if="pay.notes" class="text-xs text-slate-400 mt-1 italic">{{ pay.notes }}</p>
        </div>
      </div>

      <div v-if="!payments.length && !isLoading" class="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
        No payment records found.
      </div>
    </div>

    <!-- Modal Record Payment -->
    <div v-if="paymentModalOpen" class="sap-modal-backdrop" @click.self="paymentModalOpen = false">
      <div class="sap-modal">
        <div class="sap-modal-header">
          <div class="flex items-center gap-2.5">
            <div class="sap-modal-icon-badge">
              <svg class="w-5 h-5 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="5" width="20" height="14" rx="2" />
                <line x1="2" y1="10" x2="22" y2="10" />
              </svg>
            </div>
            <div>
              <h3 class="sap-modal-title">Record Institution Payment</h3>
              <p class="text-xs text-slate-500">Log an incoming offline subscription or setup payment.</p>
            </div>
          </div>
          <button class="sap-modal-close" @click="paymentModalOpen = false">✕</button>
        </div>

        <div class="sap-modal-body">
          <div class="sap-modal-field">
            <label class="sap-modal-label">Institution</label>
            <select v-model="payInstId" class="sap-modal-input">
              <option :value="null">-- Select Institution --</option>
              <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
                {{ inst.name }} ({{ inst.code }})
              </option>
            </select>
          </div>

          <div class="sap-modal-grid">
            <div class="sap-modal-field">
              <label class="sap-modal-label">Amount ($ USD)</label>
              <input v-model.number="payAmount" type="number" class="sap-modal-input" />
            </div>
            <div class="sap-modal-field">
              <label class="sap-modal-label">Payment Method</label>
              <select v-model="payMethod" class="sap-modal-input">
                <option value="EVC Plus">EVC Plus (Hormuud)</option>
                <option value="Zaad">Zaad (Telesom)</option>
                <option value="Sahal">Sahal (Golis)</option>
                <option value="Bank Transfer">Bank Transfer (Premier / Dahabshiil)</option>
                <option value="Cash / Cheque">Cash / Cheque</option>
              </select>
            </div>
          </div>

          <div class="sap-modal-field">
            <label class="sap-modal-label">Reference / Transaction Notes</label>
            <textarea
              v-model="payNotes"
              class="sap-modal-input"
              rows="2"
              placeholder="e.g. Received via EVC Plus TxID 129384723"
            ></textarea>
          </div>
        </div>

        <div class="sap-modal-footer">
          <button class="sap-btn-cancel" @click="paymentModalOpen = false">Cancel</button>
          <button class="sap-btn-submit" :disabled="!payInstId || isSaving" @click="handleRecordPayment">
            <span v-if="isSaving">Saving...</span>
            <span v-else>Confirm & Save Payment</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sap-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.sap-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sap-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sap-btn-record {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  border: none;
  font-size: 0.88rem;
  font-weight: 700;
  height: 44px;
  padding: 0 1.35rem;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(255, 101, 0, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.sap-btn-record:hover {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(255, 101, 0, 0.45);
}

/* Stats */
.sap-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.sap-stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sap-stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sap-stat-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.sap-stat-val {
  font-size: 1.65rem;
  font-weight: 800;
  line-height: 1.2;
}

/* Table Card */
.sap-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sap-table-wrap {
  overflow-x: auto;
}

.sap-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sap-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.04em;
}

.sap-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sap-table tr:hover td {
  background: #fbfcfe;
}

.sap-method-badge {
  background: #f1f5f9;
  color: #334155;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.sap-status-pill {
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-completed {
  background: #ecfdf5;
  color: #047857;
}

.status-pending {
  background: #fffbeb;
  color: #b45309;
}

/* Visibility */
.sap-desktop-only {
  display: block;
}

.sap-mobile-only {
  display: none;
}

/* Mobile Cards */
.sap-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.sap-mobile-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sap-mcard-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sap-mcard-body {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.sap-mcard-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Modal */
.sap-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 23, 55, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
  overflow-y: auto;
}

.sap-modal {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.sap-modal-header {
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sap-modal-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sap-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sap-modal-close {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.sap-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  overflow-y: auto;
}

.sap-modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.sap-modal-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sap-modal-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.sap-modal-input {
  padding: 0.6rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  background: #ffffff;
  transition: all 0.15s ease;
}

.sap-modal-input:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sap-modal-footer {
  padding: 1.15rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sap-btn-cancel {
  padding: 0.6rem 1.25rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
  cursor: pointer;
}

.sap-btn-submit {
  padding: 0.6rem 1.5rem;
  border: none;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(255, 101, 0, 0.35);
  transition: all 0.15s;
}

.sap-btn-submit:hover:not(:disabled) {
  background: #ea580c;
  transform: translateY(-1px);
}

.sap-btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 900px) {
  .sap-stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sap-desktop-only {
    display: none;
  }

  .sap-mobile-only {
    display: flex;
  }

  .sap-modal-grid {
    grid-template-columns: 1fr;
  }

  .sap-btn-record {
    width: 100%;
    justify-content: center;
  }
}
</style>
