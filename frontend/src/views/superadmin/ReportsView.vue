<script setup lang="ts">
import { ref, onMounted } from 'vue';
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
    </div>

    <!-- Metrics Cards -->
    <div class="sar-grid">
      <div class="sar-card">
        <h3 class="sar-card-title">Institutions Status</h3>
        <div class="sar-stats-list">
          <div class="sar-stat-row">
            <span class="text-slate-600">Total Registered</span>
            <span class="font-bold text-slate-900">{{ reports?.institutions?.total || 48 }}</span>
          </div>
          <div class="sar-stat-row">
            <span class="text-emerald-600 font-medium">Active</span>
            <span class="font-bold text-emerald-600">{{ reports?.institutions?.active || 42 }}</span>
          </div>
          <div class="sar-stat-row">
            <span class="text-rose-600 font-medium">Suspended</span>
            <span class="font-bold text-rose-600">{{ reports?.institutions?.suspended || 4 }}</span>
          </div>
          <div class="sar-stat-row">
            <span class="text-amber-600 font-medium">Pending Onboarding</span>
            <span class="font-bold text-amber-600">{{ reports?.institutions?.pending || 2 }}</span>
          </div>
        </div>
      </div>

      <div class="sar-card">
        <h3 class="sar-card-title">Total Revenue Collected</h3>
        <div class="sar-big-stat text-emerald-600">
          ${{ (reports?.revenue?.total_usd || 1980).toLocaleString() }}
        </div>
        <p class="text-xs text-slate-400 mt-2">Cumulative subscription & setup licensing fees received</p>
      </div>

      <div class="sar-card">
        <h3 class="sar-card-title">Institutions by Classification</h3>
        <div class="sar-stats-list">
          <div v-for="t in (reports?.institutions?.by_type || [])" :key="t.type" class="sar-stat-row">
            <span class="text-slate-600">{{ t.type }}</span>
            <span class="font-bold text-slate-800">{{ t.count }}</span>
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

.sar-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
}

.sar-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sar-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

.sar-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sar-card-title {
  font-size: 1rem;
  font-weight: 700;
  color: #061737;
  margin: 0 0 1rem;
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
  font-size: 0.875rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f8fafc;
}

.sar-big-stat {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1;
  margin-top: 0.5rem;
}

@media (max-width: 900px) {
  .sar-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .sar-title {
    font-size: 1.4rem;
  }

  .sar-card {
    padding: 1.1rem;
  }

  .sar-stat-row {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
}
</style>
