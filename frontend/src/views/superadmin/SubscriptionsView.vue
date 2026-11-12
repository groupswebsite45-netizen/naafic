<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { superAdminService } from '../../services/superAdminService';
import { Subscription, Institution } from '../../types/institution';

const subscriptions = ref<Subscription[]>([]);
const institutions = ref<Institution[]>([]);
const isLoading = ref(true);
const statusFilter = ref('');

// Renew Modal
const renewModalOpen = ref(false);
const selectedInstId = ref<number | null>(null);
const renewPlan = ref('Professional School');
const renewMonths = ref(12);
const renewPrice = ref(350);
const isRenewing = ref(false);

async function loadData() {
  isLoading.value = true;
  try {
    const [subs, insts] = await Promise.all([
      superAdminService.getSubscriptions({ status: statusFilter.value || undefined }),
      superAdminService.getInstitutions(),
    ]);
    subscriptions.value = subs;
    institutions.value = insts;
  } catch (err) {
    console.error('Failed to load subscriptions:', err);
  } finally {
    isLoading.value = false;
  }
}

async function handleRenew() {
  if (!selectedInstId.value) return;
  isRenewing.value = true;
  try {
    const startDate = new Date();
    const endDate = new Date();
    endDate.setMonth(endDate.getMonth() + renewMonths.value);

    await superAdminService.createSubscription({
      institution_id: selectedInstId.value,
      plan_name: renewPlan.value,
      billing_cycle: renewMonths.value === 12 ? 'Annual' : 'Monthly',
      price: renewPrice.value,
      setup_fee: 0,
      status: 'Active',
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      auto_renew: true,
      notes: `Subscription renewed via Super Admin panel on ${new Date().toISOString().split('T')[0]}.`,
    });

    renewModalOpen.value = false;
    await loadData();
    alert('Subscription successfully renewed!');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to renew subscription.');
  } finally {
    isRenewing.value = false;
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
const activeCount = computed(() => subscriptions.value.filter(s => s.status.toLowerCase() === 'active').length);
const suspendedCount = computed(() => subscriptions.value.filter(s => s.status.toLowerCase() !== 'active').length);

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="sas-page">
    <!-- Header -->
    <div class="sas-header">
      <div>
        <h1 class="sas-title">Subscription Management</h1>
        <p class="sas-sub">Oversee and configure institutional licensing, renewals, and tier assignments.</p>
      </div>

      <button class="sas-btn-renew" @click="renewModalOpen = true">
        <svg class="w-5 h-5 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
        </svg>
        <span>Assign / Renew Subscription</span>
      </button>
    </div>

    <!-- Overview Stats Grid -->
    <div class="sas-stats-grid">
      <div class="sas-stat-card">
        <div class="sas-stat-icon bg-emerald-50 text-emerald-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </div>
        <div>
          <span class="sas-stat-label">Active Subscriptions</span>
          <span class="sas-stat-val text-emerald-600">{{ activeCount }}</span>
        </div>
      </div>

      <div class="sas-stat-card">
        <div class="sas-stat-icon bg-amber-50 text-amber-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        </div>
        <div>
          <span class="sas-stat-label">Expiring Soon (&lt; 30 days)</span>
          <span class="sas-stat-val text-amber-500">2</span>
        </div>
      </div>

      <div class="sas-stat-card">
        <div class="sas-stat-icon bg-rose-50 text-rose-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <div>
          <span class="sas-stat-label">Suspended / Expired</span>
          <span class="sas-stat-val text-rose-500">{{ suspendedCount }}</span>
        </div>
      </div>
    </div>

    <!-- Desktop Table Card -->
    <div class="sas-card sas-desktop-only">
      <div class="sas-table-wrap">
        <table class="sas-table">
          <thead>
            <tr>
              <th>Institution</th>
              <th>Licensing Plan</th>
              <th>Billing Cycle</th>
              <th>Price</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Auto Renew</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in subscriptions" :key="sub.id">
              <td>
                <div class="font-bold text-slate-900">{{ sub.institution_name }}</div>
                <div class="text-xs text-slate-400 font-mono">{{ sub.institution_code }}</div>
              </td>
              <td>
                <span class="sas-plan-tag">{{ sub.plan_name }}</span>
              </td>
              <td>
                <span class="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-1 rounded">
                  {{ sub.billing_cycle }}
                </span>
              </td>
              <td class="font-extrabold text-slate-900 text-sm">${{ sub.price }}</td>
              <td class="text-xs text-slate-600">{{ formatDate(sub.start_date) }}</td>
              <td class="text-xs text-slate-600">{{ formatDate(sub.end_date) }}</td>
              <td>
                <span
                  class="sas-pill"
                  :class="sub.status.toLowerCase() === 'active' ? 'pill-active' : 'pill-expired'"
                >
                  {{ sub.status }}
                </span>
              </td>
              <td>
                <span v-if="sub.auto_renew" class="text-emerald-600 font-bold text-xs bg-emerald-50 px-2 py-0.5 rounded">Enabled</span>
                <span v-else class="text-slate-400 text-xs bg-slate-100 px-2 py-0.5 rounded">Manual</span>
              </td>
            </tr>

            <tr v-if="!subscriptions.length && !isLoading">
              <td colspan="8" class="text-center py-12 text-slate-400">
                No subscription records found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards View (<768px) -->
    <div class="sas-mobile-cards sas-mobile-only">
      <div
        v-for="sub in subscriptions"
        :key="`ms-${sub.id}`"
        class="sas-mobile-card"
      >
        <div class="sas-mcard-header">
          <div>
            <div class="font-bold text-slate-900 text-sm">{{ sub.institution_name }}</div>
            <div class="text-xs text-slate-400 font-mono">{{ sub.institution_code }}</div>
          </div>
          <span
            class="sas-pill"
            :class="sub.status.toLowerCase() === 'active' ? 'pill-active' : 'pill-expired'"
          >
            {{ sub.status }}
          </span>
        </div>

        <div class="sas-mcard-body">
          <div class="sas-mcard-row">
            <span class="text-xs text-slate-500">Plan:</span>
            <span class="sas-plan-tag">{{ sub.plan_name }}</span>
          </div>
          <div class="sas-mcard-row">
            <span class="text-xs text-slate-500">Cycle / Price:</span>
            <span class="font-bold text-slate-900 text-sm">${{ sub.price }} / {{ sub.billing_cycle }}</span>
          </div>
          <div class="sas-mcard-row">
            <span class="text-xs text-slate-500">Expires:</span>
            <span class="text-xs font-semibold text-slate-700">{{ formatDate(sub.end_date) }}</span>
          </div>
        </div>
      </div>

      <div v-if="!subscriptions.length && !isLoading" class="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
        No subscription records found.
      </div>
    </div>

    <!-- Renew Modal -->
    <div v-if="renewModalOpen" class="sas-modal-backdrop" @click.self="renewModalOpen = false">
      <div class="sas-modal">
        <div class="sas-modal-header">
          <div class="flex items-center gap-2.5">
            <div class="sas-modal-icon-badge">
              <svg class="w-5 h-5 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
              </svg>
            </div>
            <div>
              <h3 class="sas-modal-title">Assign or Renew Subscription</h3>
              <p class="text-xs text-slate-500">Grant institutional access and extend licensing period.</p>
            </div>
          </div>
          <button class="sas-modal-close" @click="renewModalOpen = false">✕</button>
        </div>

        <div class="sas-modal-body">
          <div class="sas-modal-field">
            <label class="sas-modal-label">Select Institution</label>
            <select v-model="selectedInstId" class="sas-modal-input">
              <option :value="null">-- Choose Institution --</option>
              <option v-for="inst in institutions" :key="inst.id" :value="inst.id">
                {{ inst.name }} ({{ inst.code }})
              </option>
            </select>
          </div>

          <div class="sas-modal-field">
            <label class="sas-modal-label">Licensing Plan</label>
            <select v-model="renewPlan" class="sas-modal-input">
              <option value="Starter Academy">Starter Academy ($250/yr)</option>
              <option value="Professional School">Professional School ($350/yr)</option>
              <option value="Enterprise Institution">Enterprise Institution ($600/yr)</option>
            </select>
          </div>

          <div class="sas-modal-grid">
            <div class="sas-modal-field">
              <label class="sas-modal-label">Duration (Months)</label>
              <input v-model.number="renewMonths" type="number" class="sas-modal-input" min="1" max="60" />
            </div>
            <div class="sas-modal-field">
              <label class="sas-modal-label">Total Fee ($ USD)</label>
              <input v-model.number="renewPrice" type="number" class="sas-modal-input" />
            </div>
          </div>
        </div>

        <div class="sas-modal-footer">
          <button class="sas-btn-cancel" @click="renewModalOpen = false">Cancel</button>
          <button class="sas-btn-submit" :disabled="!selectedInstId || isRenewing" @click="handleRenew">
            <span v-if="isRenewing">Processing...</span>
            <span v-else>Confirm Renewal</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sas-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sas-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.sas-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sas-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sas-btn-renew {
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

.sas-btn-renew:hover {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(255, 101, 0, 0.45);
}

/* Stats */
.sas-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.sas-stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sas-stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sas-stat-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.sas-stat-val {
  font-size: 1.65rem;
  font-weight: 800;
  line-height: 1.2;
}

/* Table Card */
.sas-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sas-table-wrap {
  overflow-x: auto;
}

.sas-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sas-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.04em;
}

.sas-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sas-table tr:hover td {
  background: #fbfcfe;
}

.sas-plan-tag {
  font-size: 0.78rem;
  font-weight: 700;
  color: #1e3a8a;
  background: #eff6ff;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.sas-pill {
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.pill-active {
  background: #ecfdf5;
  color: #047857;
}

.pill-expired {
  background: #fef2f2;
  color: #b91c1c;
}

/* Visibility */
.sas-desktop-only {
  display: block;
}

.sas-mobile-only {
  display: none;
}

/* Mobile Cards */
.sas-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.sas-mobile-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sas-mcard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sas-mcard-body {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.sas-mcard-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Modal */
.sas-modal-backdrop {
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

.sas-modal {
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

.sas-modal-header {
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sas-modal-icon-badge {
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

.sas-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sas-modal-close {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.sas-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  overflow-y: auto;
}

.sas-modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.sas-modal-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sas-modal-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.sas-modal-input {
  padding: 0.6rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  background: #ffffff;
  transition: all 0.15s ease;
}

.sas-modal-input:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sas-modal-footer {
  padding: 1.15rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sas-btn-cancel {
  padding: 0.6rem 1.25rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
  cursor: pointer;
}

.sas-btn-submit {
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

.sas-btn-submit:hover:not(:disabled) {
  background: #ea580c;
  transform: translateY(-1px);
}

.sas-btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 900px) {
  .sas-stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sas-desktop-only {
    display: none;
  }

  .sas-mobile-only {
    display: flex;
  }

  .sas-modal-grid {
    grid-template-columns: 1fr;
  }

  .sas-btn-renew {
    width: 100%;
    justify-content: center;
  }
}
</style>
