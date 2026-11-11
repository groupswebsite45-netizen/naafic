<script setup lang="ts">
import { ref, onMounted } from 'vue';
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

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="sap-page">
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

    <!-- Payments Table Card -->
    <div class="sap-card">
      <div class="sap-table-wrap sap-desktop-table" tabindex="0" role="region" aria-label="Payments table">
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
              <td class="whitespace-nowrap">
                <span class="font-extrabold text-emerald-600">${{ pay.amount.toFixed(2) }}</span>
              </td>
              <td>
                <span class="sap-method-badge">{{ pay.payment_method }}</span>
              </td>
              <td class="text-slate-600 whitespace-nowrap">{{ formatDate(pay.payment_date) }}</td>
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
              <td colspan="7" class="text-center py-10 text-slate-400">
                No financial transactions found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Payments Cards (<= 768px) -->
      <div class="sap-mobile-cards">
        <div v-if="!payments.length && !isLoading" class="sap-mobile-empty">
          No financial transactions found.
        </div>
        <article v-for="pay in payments" :key="'m-pay-' + pay.id" class="sap-mobile-card">
          <div class="sap-mobile-head">
            <div>
              <div class="sap-mobile-ref">{{ pay.reference }}</div>
              <div class="sap-mobile-inv">{{ pay.invoice_number || 'INV-Auto' }}</div>
            </div>
            <span
              class="sap-status-pill"
              :class="pay.status.toLowerCase() === 'completed' ? 'status-completed' : 'status-pending'"
            >
              {{ pay.status }}
            </span>
          </div>
          <div class="sap-mobile-inst">{{ pay.institution_name }}</div>
          <div class="sap-mobile-kv-grid">
            <div class="sap-mobile-kv">
              <span class="sap-kv-label">Amount</span>
              <span class="sap-kv-val sap-kv-money">${{ pay.amount.toFixed(2) }}</span>
            </div>
            <div class="sap-mobile-kv">
              <span class="sap-kv-label">Method</span>
              <span class="sap-method-badge">{{ pay.payment_method }}</span>
            </div>
            <div class="sap-mobile-kv">
              <span class="sap-kv-label">Date</span>
              <span class="sap-kv-val">{{ formatDate(pay.payment_date) }}</span>
            </div>
          </div>
          <div v-if="pay.notes" class="sap-mobile-notes">{{ pay.notes }}</div>
        </article>
      </div>
    </div>

    <!-- Modal Record Payment -->
    <div v-if="paymentModalOpen" class="sap-modal-backdrop" @click.self="paymentModalOpen = false">
      <div class="sap-modal">
        <div class="sap-modal-header">
          <h3 class="sap-modal-title">Record Institution Payment</h3>
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
              <label class="sap-modal-label">Method</label>
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
            <textarea v-model="payNotes" class="sap-modal-input" rows="2" placeholder="e.g. Received via EVC Plus TxID 129384723"></textarea>
          </div>
        </div>
        <div class="sap-modal-footer">
          <button class="sap-btn-cancel" @click="paymentModalOpen = false">Cancel</button>
          <button class="sap-btn-submit" :disabled="!payInstId || isSaving" @click="handleRecordPayment">
            {{ isSaving ? 'Saving...' : 'Save Payment' }}
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
}

.sap-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sap-btn-record {
  display: flex;
  align-items: center;
  background: #ff6500;
  color: #ffffff;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.7rem 1.25rem;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.3);
  transition: all 0.2s;
}

.sap-btn-record:hover {
  background: #e55a00;
}

.sap-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: clip;
  min-width: 0;
}

.sap-table-wrap {
  overflow-x: auto;
}

.sap-table {
  width: 100%;
  min-width: 780px;
  border-collapse: collapse;
  text-align: left;
}

.sap-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.sap-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.875rem;
}

.sap-mobile-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: #94a3b8;
  font-size: 0.85rem;
}

.sap-mobile-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.sap-mobile-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.sap-mobile-ref {
  font-family: monospace;
  font-size: 0.78rem;
  font-weight: 700;
  color: #1e293b;
}

.sap-mobile-inv {
  font-size: 0.72rem;
  color: #64748b;
}

.sap-mobile-inst {
  font-size: 0.95rem;
  font-weight: 700;
  color: #061737;
}

.sap-mobile-kv-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem 0.75rem;
  padding-top: 0.45rem;
  border-top: 1px dashed #e2e8f0;
}

.sap-mobile-kv {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
}

.sap-kv-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
}

.sap-kv-val {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
}

.sap-kv-money {
  font-size: 0.98rem;
  font-weight: 800;
  color: #059669;
}

.sap-mobile-notes {
  font-size: 0.78rem;
  color: #475569;
  padding-top: 0.25rem;
}

.sap-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sap-method-badge {
  background: #f1f5f9;
  color: #061737;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.sap-status-pill {
  padding: 0.2rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-completed {
  background: #ecfdf5;
  color: #059669;
}

.status-pending {
  background: #fffbeb;
  color: #d97706;
}

/* Modal */
.sap-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 23, 55, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

.sap-modal {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: 520px;
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

.sap-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sap-modal-close {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.sap-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sap-modal-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.sap-modal-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.sap-modal-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.sap-modal-input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 0.55rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
}

.sap-modal-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.sap-btn-cancel {
  padding: 0.55rem 1rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.sap-btn-submit {
  padding: 0.55rem 1.25rem;
  border: none;
  background: #ff6500;
  color: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .sap-desktop-table {
    display: none;
  }

  .sap-mobile-cards {
    display: flex;
  }
}

@media (max-width: 640px) {
  .sap-title {
    font-size: 1.4rem;
  }

  .sap-btn-record {
    width: 100%;
    justify-content: center;
  }

  .sap-modal-backdrop {
    padding: 0.5rem;
  }

  .sap-modal-grid {
    grid-template-columns: 1fr;
  }

  .sap-modal-header,
  .sap-modal-body,
  .sap-modal-footer {
    padding: 1rem;
  }

  .sap-table th,
  .sap-table td {
    padding: 0.75rem 0.85rem;
  }
}
</style>
