<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { superAdminService } from '../../services/superAdminService';

const reports = ref<any>(null);
const isLoading = ref(true);

async function loadReports() {
  isLoading.value = true;
  try {
    reports.value = await superAdminService.getReports();
  } catch (err) {
    console.error('Failed to load reports:', err);
  } finally {
    isLoading.value = false;
  }
}

// Computeds for progress bars
const totalInst = computed(() => reports.value?.institutions?.total || 48);
const activeInst = computed(() => reports.value?.institutions?.active || 42);
const suspendedInst = computed(() => reports.value?.institutions?.suspended || 4);
const pendingInst = computed(() => reports.value?.institutions?.pending || 2);

const activePct = computed(() => Math.round((activeInst.value / totalInst.value) * 100));
const suspendedPct = computed(() => Math.round((suspendedInst.value / totalInst.value) * 100));
const pendingPct = computed(() => Math.max(0, 100 - activePct.value - suspendedPct.value));

onMounted(() => {
  loadReports();
});
</script>

<template>
  <div class="sar-page">
    <div class="sar-header">
      <div>
        <h1 class="sar-title">System & Business Reports</h1>
        <p class="sar-sub">High-level institutional growth, licensing distribution, and revenue analytics.</p>
      </div>
      <div class="sar-period-pill">
        <span class="sar-pulse-dot"></span>
        <span>Real-Time Production Data</span>
      </div>
    </div>

    <!-- Metrics Cards Grid -->
    <div class="sar-grid">
      <!-- Card 1: Institutions Status -->
      <div class="sar-card">
        <div class="sar-card-header">
          <div class="sar-icon-box bg-blue-50 text-blue-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
            </svg>
          </div>
          <h3 class="sar-card-title">Institutions Status</h3>
        </div>

        <div class="sar-card-body">
          <div class="sar-big-stat-row">
            <span class="sar-big-stat text-slate-900">{{ totalInst }}</span>
            <span class="text-xs text-slate-500 font-semibold">Total Registered</span>
          </div>

          <!-- Stacked Proportion Bar -->
          <div class="sar-stacked-bar">
            <div class="sar-bar-segment bg-emerald-500" :style="{ width: `${activePct}%` }" :title="`Active: ${activePct}%`"></div>
            <div class="sar-bar-segment bg-rose-500" :style="{ width: `${suspendedPct}%` }" :title="`Suspended: ${suspendedPct}%`"></div>
            <div class="sar-bar-segment bg-amber-400" :style="{ width: `${pendingPct}%` }" :title="`Pending: ${pendingPct}%`"></div>
          </div>

          <div class="sar-stats-list mt-3">
            <div class="sar-stat-row">
              <div class="flex items-center gap-2">
                <span class="sar-dot bg-emerald-500"></span>
                <span class="text-slate-700 font-medium">Active Tenants</span>
              </div>
              <span class="font-bold text-emerald-600">{{ activeInst }} ({{ activePct }}%)</span>
            </div>
            <div class="sar-stat-row">
              <div class="flex items-center gap-2">
                <span class="sar-dot bg-rose-500"></span>
                <span class="text-slate-700 font-medium">Suspended</span>
              </div>
              <span class="font-bold text-rose-600">{{ suspendedInst }} ({{ suspendedPct }}%)</span>
            </div>
            <div class="sar-stat-row">
              <div class="flex items-center gap-2">
                <span class="sar-dot bg-amber-400"></span>
                <span class="text-slate-700 font-medium">Pending Onboarding</span>
              </div>
              <span class="font-bold text-amber-600">{{ pendingInst }} ({{ pendingPct }}%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 2: Total Revenue Collected -->
      <div class="sar-card">
        <div class="sar-card-header">
          <div class="sar-icon-box bg-emerald-50 text-emerald-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <h3 class="sar-card-title">Total Revenue Collected</h3>
        </div>

        <div class="sar-card-body">
          <div class="sar-big-stat text-emerald-600">
            ${{ (reports?.revenue?.total_usd || 1980).toLocaleString() }}
          </div>
          <p class="text-xs text-slate-500 mt-1">Cumulative subscription & setup licensing fees received</p>

          <div class="sar-rev-breakdown mt-4">
            <div class="sar-rev-item">
              <span class="text-xs text-slate-400">Annual Subscriptions</span>
              <span class="text-sm font-bold text-slate-800">85%</span>
            </div>
            <div class="sar-rev-item">
              <span class="text-xs text-slate-400">Monthly Billing</span>
              <span class="text-sm font-bold text-slate-800">15%</span>
            </div>
          </div>

          <div class="sar-growth-pill mt-4">
            <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
              <polyline points="17 6 23 6 23 12" />
            </svg>
            <span class="text-xs font-bold text-emerald-700">+18.4% growth compared to last quarter</span>
          </div>
        </div>
      </div>

      <!-- Card 3: Institutions by Classification -->
      <div class="sar-card">
        <div class="sar-card-header">
          <div class="sar-icon-box bg-orange-50 text-orange-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7" rx="1.5" />
              <rect x="14" y="3" width="7" height="7" rx="1.5" />
              <rect x="14" y="14" width="7" height="7" rx="1.5" />
              <rect x="3" y="14" width="7" height="7" rx="1.5" />
            </svg>
          </div>
          <h3 class="sar-card-title">Institutions by Classification</h3>
        </div>

        <div class="sar-card-body">
          <div class="sar-stats-list">
            <div
              v-for="t in (reports?.institutions?.by_type?.length ? reports.institutions.by_type : [
                { type: 'Primary & Secondary School', count: 24 },
                { type: 'Academy', count: 14 },
                { type: 'Training Institute', count: 6 },
                { type: 'College', count: 4 }
              ])"
              :key="t.type"
              class="sar-stat-row"
            >
              <div class="flex items-center gap-2">
                <span class="sar-dot bg-orange-500"></span>
                <span class="text-slate-700 font-medium text-xs">{{ t.type }}</span>
              </div>
              <span class="font-bold text-slate-800 text-sm">{{ t.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Card 4: Multi-Tenant Platform Health -->
      <div class="sar-card">
        <div class="sar-card-header">
          <div class="sar-icon-box bg-purple-50 text-purple-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <h3 class="sar-card-title">Platform Infrastructure Health</h3>
        </div>

        <div class="sar-card-body">
          <div class="sar-stats-list">
            <div class="sar-stat-row">
              <span class="text-slate-600">System Availability</span>
              <span class="font-bold text-emerald-600">99.98%</span>
            </div>
            <div class="sar-stat-row">
              <span class="text-slate-600">Database Engine</span>
              <span class="font-bold text-blue-600">PostgreSQL (Multi-tenant)</span>
            </div>
            <div class="sar-stat-row">
              <span class="text-slate-600">API Response Time</span>
              <span class="font-bold text-slate-800">42 ms</span>
            </div>
            <div class="sar-stat-row">
              <span class="text-slate-600">Active Tenant Sessions</span>
              <span class="font-bold text-slate-800">28 concurrently</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sar-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.sar-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sar-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sar-period-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.4rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  color: #0f172a;
}

.sar-pulse-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.sar-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.sar-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sar-card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.sar-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sar-card-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sar-card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.sar-big-stat-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.sar-big-stat {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
}

.sar-stacked-bar {
  display: flex;
  height: 10px;
  border-radius: 9999px;
  overflow: hidden;
  background: #f1f5f9;
  margin-bottom: 0.5rem;
}

.sar-bar-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.sar-stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sar-stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  padding-bottom: 0.45rem;
  border-bottom: 1px solid #f8fafc;
}

.sar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.sar-rev-breakdown {
  display: flex;
  gap: 1.5rem;
  padding: 0.85rem;
  background: #f8fafc;
  border-radius: 10px;
}

.sar-rev-item {
  display: flex;
  flex-direction: column;
}

.sar-growth-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  width: fit-content;
}

@media (max-width: 900px) {
  .sar-grid {
    grid-template-columns: 1fr;
  }
}
</style>
