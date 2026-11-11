<script setup lang="ts">
import { ref, onMounted } from 'vue';
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

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="sas-page">
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

    <!-- Overview Stats -->
    <div class="sas-stats-grid">
      <div class="sas-stat-card">
        <span class="sas-stat-label">Active Subscriptions</span>
        <span class="sas-stat-val text-emerald-600">
          {{ subscriptions.filter(s => s.status.toLowerCase() === 'active').length }}
        </span>
      </div>
      <div class="sas-stat-card">
        <span class="sas-stat-label">Expiring Soon (< 30 days)</span>
        <span class="sas-stat-val text-amber-500">2</span>
      </div>
      <div class="sas-stat-card">
        <span class="sas-stat-label">Suspended / Expired</span>
        <span class="sas-stat-val text-rose-500">
          {{ subscriptions.filter(s => s.status.toLowerCase() !== 'active').length }}
        </span>
      </div>
    </div>

    <!-- Table Card -->
    <div class="sas-card">
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
                <div class="text-xs text-slate-400">{{ sub.institution_code }}</div>
              </td>
              <td>
                <span class="font-semibold text-blue-900">{{ sub.plan_name }}</span>
              </td>
              <td>{{ sub.billing_cycle }}</td>
              <td class="font-bold text-slate-800">${{ sub.price }}</td>
              <td>{{ formatDate(sub.start_date) }}</td>
              <td>{{ formatDate(sub.end_date) }}</td>
              <td>
                <span
                  class="sas-pill"
                  :class="sub.status.toLowerCase() === 'active' ? 'pill-active' : 'pill-expired'"
                >
                  {{ sub.status }}
                </span>
              </td>
              <td>
                <span v-if="sub.auto_renew" class="text-emerald-600 font-semibold text-xs">Enabled</span>
                <span v-else class="text-slate-400 text-xs">Manual</span>
              </td>
            </tr>

            <tr v-if="!subscriptions.length && !isLoading">
              <td colspan="8" class="text-center py-10 text-slate-400">
                No subscription records found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Renew Modal -->
    <div v-if="renewModalOpen" class="sas-modal-backdrop" @click.self="renewModalOpen = false">
      <div class="sas-modal">
        <div class="sas-modal-header">
          <h3 class="sas-modal-title">Assign or Renew Subscription</h3>
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
            {{ isRenewing ? 'Processing...' : 'Confirm Renewal' }}
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
}

.sas-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sas-btn-renew {
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

.sas-btn-renew:hover {
  background: #e55a00;
}

.sas-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.sas-stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sas-stat-label {
  font-size: 0.82rem;
  color: #64748b;
  font-weight: 600;
}

.sas-stat-val {
  font-size: 1.85rem;
  font-weight: 800;
}

.sas-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: hidden;
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
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.sas-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sas-pill {
  padding: 0.2rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.pill-active {
  background: #ecfdf5;
  color: #059669;
}

.pill-expired {
  background: #fef2f2;
  color: #dc2626;
}

/* Modal */
.sas-modal-backdrop {
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

.sas-modal {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: 520px;
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

.sas-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sas-modal-close {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
}

.sas-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  padding: 0.55rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
}

.sas-modal-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sas-btn-cancel {
  padding: 0.55rem 1rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.sas-btn-submit {
  padding: 0.55rem 1.25rem;
  border: none;
  background: #ff6500;
  color: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.sas-btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .sas-stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
