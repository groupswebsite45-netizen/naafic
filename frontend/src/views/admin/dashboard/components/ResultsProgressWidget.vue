<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  resultsData?: any;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  resultsData: null,
  loading: false,
});

const selectedPeriod = ref('This Year');

const passedCount = computed(() => Number(props.resultsData?.passed_count ?? 0));
const failedCount = computed(() => Number(props.resultsData?.failed_count ?? 0));
const notTakenCount = computed(() => Number(props.resultsData?.not_taken_count ?? 0));
const totalResults = computed(() => passedCount.value + failedCount.value + notTakenCount.value);

const passedPct = computed(() => totalResults.value > 0 ? Math.round((passedCount.value / totalResults.value) * 100) : 0);
const failedPct = computed(() => totalResults.value > 0 ? Math.round((failedCount.value / totalResults.value) * 100) : 0);
const notTakenPct = computed(() => totalResults.value > 0 ? Math.round((notTakenCount.value / totalResults.value) * 100) : 0);

const passedDash = computed(() => `${(passedPct.value / 100) * 339.29} 339.29`);
const failedDash = computed(() => `${(failedPct.value / 100) * 339.29} 339.29`);
const failedOffset = computed(() => -((passedPct.value / 100) * 339.29));
</script>

<template>
  <div class="analytics-card academic-performance-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box blue-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
        </div>
        <div class="header-text-group">
          <h3 class="card-title">Academic Performance</h3>
          <p class="card-sub">Class results overview</p>
        </div>
      </div>

      <!-- Filter Dropdown -->
      <div class="period-select-wrap">
        <select v-model="selectedPeriod" class="period-select">
          <option value="This Year">This Year</option>
          <option value="Last Term">Last Term</option>
        </select>
        <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Chart & Legend Container -->
    <div class="chart-content">
      <!-- SVG Radial Gauge Donut Chart -->
      <div class="donut-chart-wrap">
        <svg class="donut-svg" viewBox="0 0 140 140">
          <!-- Background Track -->
          <circle
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#E2E8F0"
            stroke-width="14"
          />
          <!-- Passed Segment -->
          <circle
            v-if="passedPct > 0"
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#10B981"
            stroke-width="14"
            :stroke-dasharray="passedDash"
            stroke-dashoffset="0"
            stroke-linecap="round"
            transform="rotate(-90 70 70)"
          />
          <!-- Failed Segment -->
          <circle
            v-if="failedPct > 0"
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#EF4444"
            stroke-width="14"
            :stroke-dasharray="failedDash"
            :stroke-dashoffset="failedOffset"
            stroke-linecap="round"
            transform="rotate(-90 70 70)"
          />
        </svg>

        <!-- Center Metric -->
        <div class="donut-center-text">
          <span class="center-value">{{ totalResults > 0 ? `${passedPct}%` : '0%' }}</span>
          <span class="center-label">{{ totalResults > 0 ? 'Average' : 'No Data' }}</span>
        </div>
      </div>

      <!-- Legend List -->
      <div class="legend-list">
        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet passed-bullet" />
            <span class="legend-name">Passed</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ passedCount }}</span>
            <span class="val-pct">({{ passedPct }}%)</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet failed-bullet" />
            <span class="legend-name">Failed</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ failedCount }}</span>
            <span class="val-pct">({{ failedPct }}%)</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet not-taken-bullet" />
            <span class="legend-name">Not Taken</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ notTakenCount }}</span>
            <span class="val-pct">({{ notTakenPct }}%)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-card {
  background: linear-gradient(145deg, #F6F4FF 0%, #EBE6FE 100%);
  border: 1.5px solid #DDD6FE;
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 8px 24px -4px rgba(139, 92, 246, 0.1), inset 0 1px 0 #FFFFFF;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.analytics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px -4px rgba(139, 92, 246, 0.18);
  border-color: #A78BFA;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.blue-box {
  background-color: #EFF6FF;
  color: #2563EB;
}

.header-icon-box svg {
  width: 20px;
  height: 20px;
}

.header-text-group {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
  line-height: 1.25;
}

.card-sub {
  font-size: 0.75rem;
  color: #64748B;
  margin: 0.15rem 0 0 0;
}

/* Period Filter Dropdown */
.period-select-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.period-select {
  appearance: none;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  padding: 0.3rem 1.6rem 0.3rem 0.65rem;
  font-size: 0.76rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  outline: none;
}

.select-arrow {
  position: absolute;
  right: 0.45rem;
  width: 14px;
  height: 14px;
  color: #64748B;
  pointer-events: none;
}

/* Chart and Legend */
.chart-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 0.5rem 0;
}

.donut-chart-wrap {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.donut-svg {
  width: 100%;
  height: 100%;
}

.donut-center-text {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.center-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1;
}

.center-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748B;
  margin-top: 0.15rem;
}

/* Legend */
.legend-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  flex: 1;
}

.legend-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8rem;
}

.legend-indicator {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.legend-bullet {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.passed-bullet {
  background-color: #10B981;
}

.failed-bullet {
  background-color: #EF4444;
}

.not-taken-bullet {
  background-color: #CBD5E1;
}

.legend-name {
  color: #334155;
  font-weight: 500;
}

.legend-val {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 700;
}

.val-count {
  color: #0F172A;
}

.val-pct {
  color: #64748B;
  font-weight: 500;
}

@media (max-width: 480px) {
  .analytics-card {
    padding: 1rem 0.75rem;
    gap: 0.85rem;
  }
  .card-header {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .chart-content {
    flex-direction: column;
    align-items: center;
    gap: 0.85rem;
  }
  .legend-list {
    width: 100%;
  }
}
</style>
