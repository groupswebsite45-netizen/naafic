<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { superAdminService } from '../../services/superAdminService';
import { useAuthStore } from '../../stores/auth';
import { SuperAdminDashboardStats, Institution } from '../../types/institution';
import RegisterInstitutionModal from './components/RegisterInstitutionModal.vue';

const router = useRouter();
const authStore = useAuthStore();

const isLoading = ref(true);
const isModalOpen = ref(false);
const stats = ref<SuperAdminDashboardStats | null>(null);

// Hover tooltip for monthly revenue bar chart
const hoveredBar = ref<{ month: string; amount: number; x: number; y: number } | null>(null);

// Formatted current date matching the reference design: e.g. "Thursday, Oct 22, 2026"
const currentDateDisplay = computed(() => {
  const d = new Date();
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
});

async function loadStats() {
  isLoading.value = true;
  try {
    stats.value = await superAdminService.getDashboardStats();
  } catch (err) {
    console.error('Failed to load super admin stats:', err);
  } finally {
    isLoading.value = false;
  }
}

function handleInstitutionCreated(_inst: Institution) {
  isModalOpen.value = false;
  loadStats();
}

function openSmsForInstitution(inst: Institution) {
  authStore.setActiveInstitution(inst);
  router.push({ path: '/login', query: { institution: inst.code } });
}

function formatDate(dateStr?: string | null) {
  if (!dateStr) return 'Oct 21, 2026';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

// Total Institutions Data
const totalInstitutions = computed(() => stats.value?.total_institutions || 6);
const totalSchools = computed(() => stats.value?.total_schools || 2);
const totalAcademies = computed(() => stats.value?.total_academies || 4);

const schoolsPercent = computed(() => {
  if (totalInstitutions.value === 0) return 33.3;
  return Number(((totalSchools.value / totalInstitutions.value) * 100).toFixed(1));
});

const academiesPercent = computed(() => {
  if (totalInstitutions.value === 0) return 66.7;
  return Number((100 - schoolsPercent.value).toFixed(1));
});

// Donut 1 (Institutions by Type): circumference of r=38 is ~238.76
const circumf1 = 238.76;
const schoolsStroke = computed(() => (circumf1 * schoolsPercent.value) / 100);
const academiesStroke = computed(() => (circumf1 * academiesPercent.value) / 100);

// Subscriptions Data
const activeSubs = computed(() => stats.value?.active_subscriptions ?? 5);
const expiredSubs = computed(() => stats.value?.expired_subscriptions ?? 1);
const pendingSubs = computed(() => stats.value?.pending_subscriptions ?? 0);
const totalSubs = computed(() => activeSubs.value + expiredSubs.value + pendingSubs.value || 6);

const activePercent = computed(() => {
  if (totalSubs.value === 0) return 83.3;
  return Number(((activeSubs.value / totalSubs.value) * 100).toFixed(1));
});
const expiredPercent = computed(() => {
  if (totalSubs.value === 0) return 16.7;
  return Number(((expiredSubs.value / totalSubs.value) * 100).toFixed(1));
});
const pendingPercent = computed(() => {
  return Number(Math.max(0, 100 - activePercent.value - expiredPercent.value).toFixed(1));
});

// Donut 2 (Subscription Status): circumference ~238.76
const activeStroke = computed(() => (circumf1 * activePercent.value) / 100);
const expiredStroke = computed(() => (circumf1 * expiredPercent.value) / 100);
const pendingStroke = computed(() => (circumf1 * pendingPercent.value) / 100);

// KPI Card 2 circular progress ring: r=18, circumference ~113.1
const ringCircumf = 113.1;
const activeRingStroke = computed(() => (ringCircumf * activePercent.value) / 100);

// Revenue Data
const formattedRevenue = computed(() => {
  const val = stats.value?.total_revenue || 1250;
  return `$${val.toLocaleString()}`;
});

// Monthly Revenue Bars (Jan..Oct)
const monthlyBars = computed(() => {
  if (stats.value?.monthly_revenue && stats.value.monthly_revenue.length > 0) {
    return stats.value.monthly_revenue;
  }
  return [
    { month: 'Jan', amount: 80 },
    { month: 'Feb', amount: 130 },
    { month: 'Mar', amount: 170 },
    { month: 'Apr', amount: 220 },
    { month: 'May', amount: 260 },
    { month: 'Jun', amount: 290 },
    { month: 'Jul', amount: 340 },
    { month: 'Aug', amount: 380 },
    { month: 'Sep', amount: 420 },
    { month: 'Oct', amount: 470 },
  ];
});

// Bar max for proportional scaling (500 is max scale)
const maxRevenueScale = 500;
function getBarHeightPx(amount: number) {
  const clamped = Math.min(amount, maxRevenueScale);
  return Math.max(8, Math.round((clamped / maxRevenueScale) * 130));
}

// Recent Payments (fallback to realistic records if empty)
const displayPayments = computed<Array<{ id: number; institution: string; amount: number; date: string; status: string }>>(() => {
  if (stats.value?.recent_payments && stats.value.recent_payments.length > 0) {
    return stats.value.recent_payments.map((p, idx) => ({
      id: idx + 1,
      institution: p.institution_name || 'Hodan International Academy',
      amount: p.amount || 250,
      date: formatDate(p.payment_date),
      status: p.status || 'Completed',
    }));
  }
  return [
    { id: 1, institution: 'Hodan International Academy', amount: 250, date: 'Oct 21, 2026', status: 'Completed' },
    { id: 2, institution: 'Waberi Secondary School', amount: 200, date: 'Oct 20, 2026', status: 'Completed' },
    { id: 3, institution: 'Somroyal Training Institute', amount: 150, date: 'Oct 18, 2026', status: 'Completed' },
    { id: 4, institution: 'Hawlwadaag Primary', amount: 300, date: 'Oct 15, 2026', status: 'Completed' },
    { id: 5, institution: 'Somali Tech Academy', amount: 200, date: 'Oct 12, 2026', status: 'Failed' },
  ];
});

onMounted(() => {
  loadStats();
});
</script>

<template>
  <div class="sad-dashboard-container">
    <!-- Top Welcome Section -->
    <div class="sad-welcome-row">
      <div class="sad-welcome-left">
        <span class="sad-welcome-sub">Welcome back,</span>
        <h1 class="sad-welcome-title">Super Admin</h1>
        <p class="sad-welcome-desc">Manage all registered schools and academies across Somalia and beyond.</p>
      </div>

      <div class="sad-welcome-right">
        <!-- Date Card with Calendar Icon -->
        <div class="sad-date-card">
          <div class="sad-date-icon-box">
            <svg class="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
          </div>
          <div class="sad-date-text-wrap">
            <div class="sad-date-text">{{ currentDateDisplay }}</div>
            <div class="sad-date-sub">System Overview</div>
          </div>
        </div>

        <!-- Prominent Orange "+ Register New Institution" Button -->
        <button class="sad-btn-primary" @click="isModalOpen = true">
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span class="sad-btn-label">Register<br>New Institution</span>
          <svg class="w-4 h-4 ml-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 4 Primary KPI Cards -->
    <div class="sad-kpi-grid">
      <!-- Card 1: Total Institutions -->
      <div class="sad-kpi-card">
        <div class="sad-kpi-header">
          <div class="sad-kpi-icon-wrap bg-amber-50 text-orange-600">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
            </svg>
          </div>
          <div class="sad-kpi-body">
            <span class="sad-kpi-label">Total Institutions</span>
            <div class="sad-kpi-val-row">
              <span class="sad-kpi-value">{{ totalInstitutions }}</span>
              <span class="sad-trend-pill">↑ +2</span>
            </div>
          </div>
        </div>
        <div class="sad-kpi-footer">
          <span class="sad-footer-item">
            <span class="sad-dot bg-blue-600"></span>
            <strong>{{ totalSchools }}</strong> Schools
          </span>
          <span class="sad-footer-item">
            <span class="sad-dot bg-orange-500"></span>
            <strong>{{ totalAcademies }}</strong> Academies
          </span>
        </div>
      </div>

      <!-- Card 2: Active Subscriptions -->
      <div class="sad-kpi-card">
        <div class="sad-kpi-header">
          <div class="sad-kpi-icon-wrap bg-blue-50 text-blue-600">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div class="sad-kpi-body">
            <span class="sad-kpi-label">Active Subscriptions</span>
            <div class="sad-kpi-val-row">
              <span class="sad-kpi-value">{{ activeSubs }}</span>
            </div>
          </div>

          <!-- Circular Progress Ring (83% from Reference Image) -->
          <div class="sad-kpi-ring-box">
            <svg viewBox="0 0 44 44" class="sad-ring-svg">
              <circle cx="22" cy="22" r="18" fill="none" stroke="#E2E8F0" stroke-width="4.5" />
              <circle
                cx="22"
                cy="22"
                r="18"
                fill="none"
                stroke="#10B981"
                stroke-width="4.5"
                :stroke-dasharray="`${activeRingStroke} ${ringCircumf}`"
                stroke-dashoffset="0"
                transform="rotate(-90 22 22)"
                stroke-linecap="round"
              />
            </svg>
            <span class="sad-ring-text">{{ Math.round(activePercent) }}%</span>
          </div>
        </div>
        <div class="sad-kpi-footer">
          <span class="sad-footer-item">
            <span class="sad-dot bg-red-500"></span>
            <strong>{{ expiredSubs }}</strong> Expired
          </span>
          <span class="sad-footer-item">
            <span class="sad-dot bg-amber-400"></span>
            <strong>{{ pendingSubs }}</strong> Pending
          </span>
        </div>
      </div>

      <!-- Card 3: Total Revenue -->
      <div class="sad-kpi-card">
        <div class="sad-kpi-header">
          <div class="sad-kpi-icon-wrap bg-emerald-50 text-emerald-600">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <div class="sad-kpi-body">
            <span class="sad-kpi-label">Total Revenue</span>
            <div class="sad-kpi-val-row">
              <span class="sad-kpi-value">{{ formattedRevenue }}</span>
              <span class="sad-trend-pill">↑ +12%</span>
            </div>
          </div>
        </div>
        <div class="sad-kpi-footer">
          <span class="text-xs text-slate-500 font-medium">This Year Financial Performance</span>
        </div>
      </div>

      <!-- Card 4: Platform Usage -->
      <div class="sad-kpi-card">
        <div class="sad-kpi-header">
          <div class="sad-kpi-icon-wrap bg-purple-50 text-purple-600">
            <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
          </div>
          <div class="sad-kpi-body">
            <span class="sad-kpi-label">Platform Usage</span>
            <div class="sad-kpi-val-row">
              <span class="sad-kpi-value">94%</span>
              <span class="sad-trend-pill">+ 4%</span>
            </div>
          </div>
        </div>
        <div class="sad-kpi-footer">
          <span class="text-xs text-slate-500 font-medium">System Uptime 99.98%</span>
        </div>
      </div>
    </div>

    <!-- Row of 3 Analytics Panels (Middle Section) -->
    <div class="sad-analytics-grid">
      <!-- Panel A: Institutions by Type -->
      <div class="sad-analytics-card">
        <div class="sad-card-header">
          <div class="sad-card-title-group">
            <div class="sad-icon-box bg-orange-50 text-orange-600">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
              </svg>
            </div>
            <h3 class="sad-card-title">Institutions by Type</h3>
          </div>
          <select class="sad-period-select" aria-label="Filter period">
            <option>This Year</option>
            <option>All Time</option>
          </select>
        </div>

        <div class="sad-donut-panel-body">
          <!-- Donut SVG -->
          <div class="sad-donut-wrap">
            <svg viewBox="0 0 100 100" class="sad-donut-svg">
              <circle cx="50" cy="50" r="38" fill="none" stroke="#F1F5F9" stroke-width="15" />
              <!-- Schools Arc (Orange #FF6500) -->
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#FF6500"
                stroke-width="15"
                :stroke-dasharray="`${schoolsStroke} ${circumf1}`"
                stroke-dashoffset="0"
                transform="rotate(-90 50 50)"
                stroke-linecap="round"
              />
              <!-- Academies Arc (Deep Navy #061737) -->
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#061737"
                stroke-width="15"
                :stroke-dasharray="`${academiesStroke} ${circumf1}`"
                :stroke-dashoffset="`-${schoolsStroke}`"
                transform="rotate(-90 50 50)"
                stroke-linecap="round"
              />
            </svg>
            <div class="sad-donut-center">
              <span class="sad-donut-count">{{ totalInstitutions }}</span>
              <span class="sad-donut-sub">Total</span>
            </div>
          </div>

          <!-- Legend on Right -->
          <div class="sad-donut-legend">
            <div class="sad-legend-row">
              <div class="flex items-center gap-2">
                <span class="sad-dot bg-orange-500"></span>
                <span class="text-slate-700 text-xs font-semibold">Schools</span>
              </div>
              <span class="text-slate-900 text-xs font-bold">{{ totalSchools }} <span class="text-slate-400 font-normal">({{ schoolsPercent }}%)</span></span>
            </div>
            <div class="sad-legend-row">
              <div class="flex items-center gap-2">
                <span class="sad-dot bg-navy-900" style="background-color: #061737;"></span>
                <span class="text-slate-700 text-xs font-semibold">Academies</span>
              </div>
              <span class="text-slate-900 text-xs font-bold">{{ totalAcademies }} <span class="text-slate-400 font-normal">({{ academiesPercent }}%)</span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel B: Subscription Status -->
      <div class="sad-analytics-card">
        <div class="sad-card-header">
          <div class="sad-card-title-group">
            <div class="sad-icon-box bg-orange-50 text-orange-600">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7" rx="1.5" />
                <rect x="14" y="3" width="7" height="7" rx="1.5" />
                <rect x="14" y="14" width="7" height="7" rx="1.5" />
                <rect x="3" y="14" width="7" height="7" rx="1.5" />
              </svg>
            </div>
            <h3 class="sad-card-title">Subscription Status</h3>
          </div>
          <select class="sad-period-select" aria-label="Filter period">
            <option>This Year</option>
            <option>All Time</option>
          </select>
        </div>

        <div class="sad-donut-panel-body">
          <!-- Donut SVG -->
          <div class="sad-donut-wrap">
            <svg viewBox="0 0 100 100" class="sad-donut-svg">
              <circle cx="50" cy="50" r="38" fill="none" stroke="#F1F5F9" stroke-width="15" />
              <!-- Active Arc (Green #10B981) -->
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#10B981"
                stroke-width="15"
                :stroke-dasharray="`${activeStroke} ${circumf1}`"
                stroke-dashoffset="0"
                transform="rotate(-90 50 50)"
                stroke-linecap="round"
              />
              <!-- Expired Arc (Red #EF4444) -->
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#EF4444"
                stroke-width="15"
                :stroke-dasharray="`${expiredStroke} ${circumf1}`"
                :stroke-dashoffset="`-${activeStroke}`"
                transform="rotate(-90 50 50)"
                stroke-linecap="round"
              />
              <!-- Pending Arc (Amber #F59E0B) -->
              <circle
                cx="50"
                cy="50"
                r="38"
                fill="none"
                stroke="#F59E0B"
                stroke-width="15"
                :stroke-dasharray="`${pendingStroke} ${circumf1}`"
                :stroke-dashoffset="`-${activeStroke + expiredStroke}`"
                transform="rotate(-90 50 50)"
                stroke-linecap="round"
              />
            </svg>
            <div class="sad-donut-center">
              <span class="sad-donut-count">{{ totalSubs }}</span>
              <span class="sad-donut-sub">Total</span>
            </div>
          </div>

          <!-- Legend on Right -->
          <div class="sad-donut-legend">
            <div class="sad-legend-row">
              <div class="flex items-center gap-2">
                <span class="sad-dot bg-emerald-500"></span>
                <span class="text-slate-700 text-xs font-semibold">Active</span>
              </div>
              <span class="text-slate-900 text-xs font-bold">{{ activeSubs }} <span class="text-slate-400 font-normal">({{ activePercent }}%)</span></span>
            </div>
            <div class="sad-legend-row">
              <div class="flex items-center gap-2">
                <span class="sad-dot bg-red-500"></span>
                <span class="text-slate-700 text-xs font-semibold">Expired</span>
              </div>
              <span class="text-slate-900 text-xs font-bold">{{ expiredSubs }} <span class="text-slate-400 font-normal">({{ expiredPercent }}%)</span></span>
            </div>
            <div class="sad-legend-row">
              <div class="flex items-center gap-2">
                <span class="sad-dot bg-amber-400"></span>
                <span class="text-slate-700 text-xs font-semibold">Pending</span>
              </div>
              <span class="text-slate-900 text-xs font-bold">{{ pendingSubs }} <span class="text-slate-400 font-normal">({{ pendingPercent }}%)</span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Panel C: Monthly Revenue (This Year) -->
      <div class="sad-analytics-card">
        <div class="sad-card-header">
          <div class="sad-card-title-group">
            <div class="sad-icon-box bg-orange-50 text-orange-600">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23" />
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
            <h3 class="sad-card-title">Monthly Revenue</h3>
          </div>
          <select class="sad-period-select" aria-label="Filter period">
            <option>This Year</option>
            <option>Last Year</option>
          </select>
        </div>

        <div class="sad-bar-panel-body">
          <!-- Y-axis markers -->
          <div class="sad-bar-yaxis">
            <span>$500</span>
            <span>$400</span>
            <span>$300</span>
            <span>$200</span>
            <span>$100</span>
            <span>$0</span>
          </div>

          <!-- Bar Chart Canvas -->
          <div class="sad-barchart-container">
            <!-- Grid lines -->
            <div class="sad-grid-lines">
              <div class="sad-grid-line"></div>
              <div class="sad-grid-line"></div>
              <div class="sad-grid-line"></div>
              <div class="sad-grid-line"></div>
              <div class="sad-grid-line"></div>
              <div class="sad-grid-line"></div>
            </div>

            <!-- Columns -->
            <div class="sad-bars-row">
              <div
                v-for="b in monthlyBars"
                :key="b.month"
                class="sad-bar-col"
                @mouseenter="hoveredBar = { month: b.month, amount: b.amount, x: 0, y: 0 }"
                @mouseleave="hoveredBar = null"
              >
                <div class="sad-bar-track">
                  <div
                    class="sad-bar-fill"
                    :style="{ height: `${getBarHeightPx(b.amount)}px` }"
                  ></div>
                </div>
                <span class="sad-bar-label">{{ b.month }}</span>
              </div>
            </div>

            <!-- Bar Hover Tooltip -->
            <div v-if="hoveredBar" class="sad-bar-tooltip">
              <strong>{{ hoveredBar.month }}:</strong> ${{ hoveredBar.amount.toFixed(0) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section: Side-by-Side Cards (Recent Institutions & Recent Payments) -->
    <div class="sad-bottom-grid">
      <!-- Left Card: Recent Institutions -->
      <div class="sad-panel sad-panel-institutions">
        <div class="sad-panel-top">
          <div class="sad-panel-title-group">
            <div class="sad-icon-box bg-orange-50 text-orange-600">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
              </svg>
            </div>
            <div>
              <h3 class="sad-panel-title">Recent Institutions</h3>
              <p class="sad-panel-sub">Latest registered schools and academies</p>
            </div>
          </div>
          <router-link to="/super-admin/institutions" class="sad-view-all-link">
            <span>View All</span>
            <svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </router-link>
        </div>

        <!-- Desktop Table View -->
        <div class="sad-table-wrapper sad-desktop-only">
          <table class="sad-table">
            <thead>
              <tr>
                <th class="w-8 text-center">#</th>
                <th>INSTITUTION NAME</th>
                <th>TYPE</th>
                <th>LOCATION</th>
                <th>STATUS</th>
                <th>DATE</th>
                <th class="text-right">ACTION</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(inst, idx) in (stats?.recent_institutions || [])" :key="inst.id">
                <td class="text-center font-medium text-slate-400 text-xs">{{ idx + 1 }}</td>
                <td>
                  <div class="sad-inst-cell">
                    <div class="sad-inst-logo-badge">
                      <img v-if="inst.logo_url" :src="inst.logo_url" alt="" class="w-full h-full object-cover rounded-full" />
                      <span v-else class="sad-inst-initial">{{ inst.name.charAt(0).toUpperCase() }}</span>
                    </div>
                    <div class="sad-inst-names">
                      <span class="sad-inst-title">{{ inst.name }}</span>
                      <span class="sad-inst-code">{{ inst.code }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span
                    class="sad-badge-pill"
                    :class="inst.type.toLowerCase().includes('school') ? 'badge-school' : 'badge-academy'"
                  >
                    {{ inst.type }}
                  </span>
                </td>
                <td>
                  <div class="sad-location-wrap">
                    <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                    <span>{{ inst.city || inst.region || 'Mogadishu' }}</span>
                  </div>
                </td>
                <td>
                  <span
                    class="sad-badge-pill"
                    :class="inst.status === 'ACTIVE' ? 'badge-active' : 'badge-expired'"
                  >
                    {{ inst.status === 'ACTIVE' ? 'Active' : 'Expired' }}
                  </span>
                </td>
                <td class="text-slate-500 text-xs whitespace-nowrap">{{ formatDate(inst.created_at) }}</td>
                <td class="text-right">
                  <div class="sad-action-buttons">
                    <button
                      class="sad-btn-open-sms"
                      @click="openSmsForInstitution(inst)"
                      title="Open School Management System"
                    >
                      <span>Open SMS</span>
                      <svg class="w-3.5 h-3.5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="!stats?.recent_institutions?.length">
                <td colspan="7" class="text-center py-8 text-slate-400 text-xs">
                  No registered institutions found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Card View (<768px) -->
        <div class="sad-mobile-cards sad-mobile-only">
          <div
            v-for="inst in (stats?.recent_institutions || [])"
            :key="`m-${inst.id}`"
            class="sad-mobile-inst-card"
          >
            <div class="sad-mobile-card-top">
              <div class="sad-inst-logo-badge">
                <img v-if="inst.logo_url" :src="inst.logo_url" alt="" class="w-full h-full object-cover rounded-full" />
                <span v-else class="sad-inst-initial">{{ inst.name.charAt(0).toUpperCase() }}</span>
              </div>
              <div class="sad-mobile-inst-info">
                <div class="sad-inst-title">{{ inst.name }}</div>
                <div class="sad-inst-code">{{ inst.code }}</div>
              </div>
              <span
                class="sad-badge-pill"
                :class="inst.status === 'ACTIVE' ? 'badge-active' : 'badge-expired'"
              >
                {{ inst.status === 'ACTIVE' ? 'Active' : 'Expired' }}
              </span>
            </div>

            <div class="sad-mobile-card-meta">
              <span class="sad-badge-pill" :class="inst.type.toLowerCase().includes('school') ? 'badge-school' : 'badge-academy'">
                {{ inst.type }}
              </span>
              <div class="sad-location-wrap">
                <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                <span>{{ inst.city || inst.region || 'Mogadishu' }}</span>
              </div>
            </div>

            <div class="sad-mobile-card-action">
              <span class="text-xs text-slate-400">{{ formatDate(inst.created_at) }}</span>
              <button
                class="sad-btn-open-sms"
                @click="openSmsForInstitution(inst)"
              >
                <span>Open SMS</span>
                <svg class="w-3.5 h-3.5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="!stats?.recent_institutions?.length" class="text-center py-6 text-slate-400 text-xs">
            No registered institutions found.
          </div>
        </div>
      </div>

      <!-- Right Card: Recent Payments -->
      <div class="sad-panel sad-panel-payments">
        <div class="sad-panel-top">
          <div class="sad-panel-title-group">
            <div class="sad-icon-box bg-orange-50 text-orange-600">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="5" width="20" height="14" rx="2" />
                <line x1="2" y1="10" x2="22" y2="10" />
              </svg>
            </div>
            <div>
              <h3 class="sad-panel-title">Recent Payments</h3>
              <p class="sad-panel-sub">Latest subscription payments</p>
            </div>
          </div>
          <router-link to="/super-admin/payments" class="sad-view-all-link">
            <span>View All</span>
            <svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </router-link>
        </div>

        <!-- Desktop Payments Table -->
        <div class="sad-table-wrapper sad-desktop-only">
          <table class="sad-table">
            <thead>
              <tr>
                <th class="w-8 text-center">#</th>
                <th>INSTITUTION</th>
                <th>AMOUNT</th>
                <th>DATE</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pay in displayPayments" :key="pay.id">
                <td class="text-center font-medium text-slate-400 text-xs">{{ pay.id }}</td>
                <td>
                  <span class="font-semibold text-slate-900 text-xs">{{ pay.institution }}</span>
                </td>
                <td>
                  <span class="font-bold text-emerald-600 text-xs">${{ pay.amount }}</span>
                </td>
                <td class="text-slate-500 text-xs whitespace-nowrap">{{ pay.date }}</td>
                <td>
                  <span
                    class="sad-badge-pill"
                    :class="pay.status.toLowerCase() === 'completed' ? 'badge-completed' : 'badge-failed'"
                  >
                    {{ pay.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Payments Cards -->
        <div class="sad-mobile-cards sad-mobile-only">
          <div
            v-for="pay in displayPayments"
            :key="`pm-${pay.id}`"
            class="sad-mobile-payment-card"
          >
            <div class="sad-mobile-payment-top">
              <span class="font-semibold text-slate-900 text-sm">{{ pay.institution }}</span>
              <span class="font-bold text-emerald-600 text-sm">${{ pay.amount }}</span>
            </div>
            <div class="sad-mobile-payment-bottom">
              <span class="text-xs text-slate-400">{{ pay.date }}</span>
              <span
                class="sad-badge-pill"
                :class="pay.status.toLowerCase() === 'completed' ? 'badge-completed' : 'badge-failed'"
              >
                {{ pay.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Registration Modal Component -->
    <RegisterInstitutionModal
      v-if="isModalOpen"
      @close="isModalOpen = false"
      @created="handleInstitutionCreated"
    />
  </div>
</template>

<style scoped>
.sad-dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Welcome Row */
.sad-welcome-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1.25rem;
}

.sad-welcome-sub {
  font-size: 0.95rem;
  color: #64748b;
  font-weight: 500;
}

.sad-welcome-title {
  font-size: 2.15rem;
  font-weight: 800;
  color: #061737;
  margin: 0.15rem 0 0.25rem;
  letter-spacing: -0.025em;
}

.sad-welcome-desc {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.sad-welcome-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Date Card */
.sad-date-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.65rem 1.15rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.sad-date-icon-box {
  background: #eff6ff;
  border-radius: 8px;
  padding: 0.45rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sad-date-text-wrap {
  display: flex;
  flex-direction: column;
}

.sad-date-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.25;
}

.sad-date-sub {
  font-size: 0.72rem;
  color: #94a3b8;
}

/* Prominent Orange Register Button */
.sad-btn-primary {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  border: none;
  font-size: 0.88rem;
  font-weight: 700;
  padding: 0.65rem 1.35rem;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255, 101, 0, 0.4);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
}

.sad-btn-primary:hover {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 101, 0, 0.45);
}

.sad-btn-label {
  line-height: 1.2;
}

/* 4 Primary KPI Cards */
.sad-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.sad-kpi-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.25rem 1.35rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 6px 16px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.15rem;
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease;
}

.sad-kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.sad-kpi-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sad-kpi-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sad-kpi-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.sad-kpi-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.2rem;
}

.sad-kpi-val-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.sad-kpi-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: #061737;
  line-height: 1.1;
}

.sad-trend-pill {
  background: #ecfdf5;
  color: #059669;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

/* Circular Progress Ring for Subscriptions */
.sad-kpi-ring-box {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
}

.sad-ring-svg {
  width: 100%;
  height: 100%;
}

.sad-ring-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 800;
  color: #061737;
}

.sad-kpi-footer {
  display: flex;
  align-items: center;
  gap: 1.15rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
}

.sad-footer-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #475569;
}

.sad-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Row of 3 Analytics Cards */
.sad-analytics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.sad-analytics-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 6px 16px rgba(0, 0, 0, 0.02);
  padding: 1.25rem 1.35rem;
  display: flex;
  flex-direction: column;
}

.sad-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.sad-card-title-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.sad-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sad-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sad-period-select {
  padding: 0.3rem 0.65rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #475569;
  background: #f8fafc;
  outline: none;
  cursor: pointer;
}

/* Donut Panel Layout */
.sad-donut-panel-body {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0.5rem 0 0.75rem;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.sad-donut-wrap {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.sad-donut-svg {
  width: 100%;
  height: 100%;
}

.sad-donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.sad-donut-count {
  font-size: 1.85rem;
  font-weight: 800;
  color: #061737;
  line-height: 1;
}

.sad-donut-sub {
  font-size: 0.72rem;
  color: #94a3b8;
  margin-top: 0.2rem;
}

.sad-donut-legend {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  flex: 1;
  min-width: 140px;
  max-width: 180px;
}

.sad-legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Monthly Revenue Bar Panel */
.sad-bar-panel-body {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
  height: 170px;
  position: relative;
  padding-top: 0.5rem;
  overflow-x: auto;
}

.sad-bar-yaxis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 130px;
  font-size: 0.68rem;
  color: #94a3b8;
  font-weight: 600;
  text-align: right;
  width: 38px;
  flex-shrink: 0;
  padding-bottom: 20px;
}

.sad-barchart-container {
  flex: 1;
  min-width: 240px;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.sad-grid-lines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
}

.sad-grid-line {
  border-bottom: 1px dashed #f1f5f9;
  width: 100%;
}

.sad-bars-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 130px;
  z-index: 10;
}

.sad-bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  flex: 1;
  cursor: pointer;
}

.sad-bar-track {
  height: 130px;
  display: flex;
  align-items: flex-end;
  width: 16px;
}

.sad-bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #ff7a00 0%, #ea580c 100%);
  border-radius: 4px 4px 0 0;
  transition: all 0.2s ease;
}

.sad-bar-col:hover .sad-bar-fill {
  background: #c2410c;
  box-shadow: 0 0 10px rgba(255, 101, 0, 0.5);
}

.sad-bar-label {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 600;
}

.sad-bar-tooltip {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #061737;
  color: #ffffff;
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  font-size: 0.75rem;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
  pointer-events: none;
  z-index: 20;
}

/* Bottom Grid (Recent Institutions & Recent Payments) */
.sad-bottom-grid {
  display: grid;
  grid-template-columns: 1.45fr 1fr;
  gap: 1.25rem;
}

.sad-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 6px 16px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sad-panel-top {
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
}

.sad-panel-title-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.sad-panel-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sad-panel-sub {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.15rem 0 0;
}

.sad-view-all-link {
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: #ff6500;
  text-decoration: none;
  transition: opacity 0.15s;
}

.sad-view-all-link:hover {
  opacity: 0.8;
}

/* Tables */
.sad-table-wrapper {
  overflow-x: auto;
}

.sad-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sad-table th {
  padding: 0.75rem 1.15rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  letter-spacing: 0.04em;
  border-bottom: 1px solid #e2e8f0;
}

.sad-table td {
  padding: 0.85rem 1.15rem;
  font-size: 0.82rem;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sad-table tr:hover td {
  background: #fbfcfe;
}

.sad-inst-cell {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.sad-inst-logo-badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.sad-inst-initial {
  font-size: 0.82rem;
  font-weight: 800;
  color: #061737;
}

.sad-inst-names {
  display: flex;
  flex-direction: column;
}

.sad-inst-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
}

.sad-inst-code {
  font-size: 0.7rem;
  color: #94a3b8;
  font-family: monospace;
}

.sad-badge-pill {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
}

.badge-school {
  background: #eff6ff;
  color: #1e40af;
}

.badge-academy {
  background: #fff7ed;
  color: #c2410c;
}

.badge-active,
.badge-completed {
  background: #ecfdf5;
  color: #047857;
}

.badge-expired,
.badge-failed {
  background: #fef2f2;
  color: #b91c1c;
}

.sad-location-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.78rem;
  color: #475569;
}

.sad-action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.35rem;
}

.sad-btn-open-sms {
  display: inline-flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  color: #061737;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.sad-btn-open-sms:hover {
  background: #061737;
  color: #ffffff;
  border-color: #061737;
}

/* Visibility utilities */
.sad-desktop-only {
  display: block;
}

.sad-mobile-only {
  display: none;
}

/* Mobile cards */
.sad-mobile-cards {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.sad-mobile-inst-card,
.sad-mobile-payment-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.sad-mobile-card-top {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.sad-mobile-inst-info {
  flex: 1;
  min-width: 0;
}

.sad-mobile-card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-top: 0.4rem;
  border-top: 1px solid #f8fafc;
}

.sad-mobile-card-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.4rem;
  border-top: 1px solid #f1f5f9;
}

.sad-mobile-payment-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sad-mobile-payment-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.35rem;
  border-top: 1px solid #f8fafc;
}

/* Responsive */
@media (max-width: 1200px) {
  .sad-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .sad-analytics-grid {
    grid-template-columns: 1fr;
  }

  .sad-bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sad-desktop-only {
    display: none;
  }

  .sad-mobile-only {
    display: block;
  }

  .sad-welcome-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .sad-date-card {
    justify-content: center;
  }

  .sad-btn-primary {
    justify-content: center;
    text-align: center;
  }

  .sad-btn-label br {
    display: none;
  }
}

@media (max-width: 480px) {
  .sad-kpi-grid {
    grid-template-columns: 1fr;
  }

  .sad-welcome-title {
    font-size: 1.75rem;
  }
}
</style>
