<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  totalStudents?: number;
  primaryCount?: number;
  secondaryCount?: number;
  othersCount?: number;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  totalStudents: 21,
  primaryCount: 21,
  secondaryCount: 0,
  othersCount: 0,
  loading: false,
});

const selectedPeriod = ref('This Year');
</script>

<template>
  <div class="analytics-card student-enrollment-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box blue-box">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 9.2h3V19H5zM10.6 5h2.8v14h-2.8zm5.6 8H19v6h-2.8z" />
          </svg>
        </div>
        <div class="header-text-group">
          <h3 class="card-title">Student Enrollment Overview</h3>
          <p class="card-sub">Enrollment by academic level</p>
        </div>
      </div>

      <!-- Filter Dropdown -->
      <div class="period-select-wrap">
        <select v-model="selectedPeriod" class="period-select">
          <option value="This Year">This Year</option>
          <option value="Last Year">Last Year</option>
          <option value="All Time">All Time</option>
        </select>
        <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Chart & Legend Container -->
    <div class="chart-content">
      <!-- SVG Donut Chart -->
      <div class="donut-chart-wrap">
        <svg class="donut-svg" viewBox="0 0 140 140">
          <!-- Background Circle -->
          <circle
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#E2E8F0"
            stroke-width="14"
          />
          <!-- Primary Level (100% Blue Arc) -->
          <circle
            cx="70"
            cy="70"
            r="54"
            fill="none"
            stroke="#2563EB"
            stroke-width="14"
            stroke-dasharray="339.29"
            stroke-dashoffset="0"
            stroke-linecap="round"
            transform="rotate(-90 70 70)"
          />
        </svg>

        <!-- Center Metric -->
        <div class="donut-center-text">
          <span class="center-value">{{ totalStudents }}</span>
          <span class="center-label">Total</span>
        </div>
      </div>

      <!-- Legend List -->
      <div class="legend-list">
        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet primary-bullet" />
            <span class="legend-name">Primary Level</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ primaryCount }}</span>
            <span class="val-pct">(100%)</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet secondary-bullet" />
            <span class="legend-name">Secondary Level</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ secondaryCount }}</span>
            <span class="val-pct">(0%)</span>
          </div>
        </div>

        <div class="legend-row">
          <div class="legend-indicator">
            <span class="legend-bullet others-bullet" />
            <span class="legend-name">Others</span>
          </div>
          <div class="legend-val">
            <span class="val-count">{{ othersCount }}</span>
            <span class="val-pct">(0%)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-card {
  background: linear-gradient(145deg, #F0F7FF 0%, #E6F1FE 100%);
  border: 1.5px solid #BFDBFE;
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 8px 24px -4px rgba(37, 99, 235, 0.1), inset 0 1px 0 #FFFFFF;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.analytics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px -4px rgba(37, 99, 235, 0.18);
  border-color: #93C5FD;
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
  transform: rotate(0deg);
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

.primary-bullet {
  background-color: #2563EB;
}

.secondary-bullet {
  background-color: #F97316;
}

.others-bullet {
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
</style>
