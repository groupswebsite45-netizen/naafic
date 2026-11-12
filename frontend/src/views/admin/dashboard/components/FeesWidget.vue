<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  billed?: number;
  collected?: number;
  outstanding?: number;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  billed: 0,
  collected: 0,
  outstanding: 0,
  loading: false,
});

const selectedPeriod = ref('This Year');

const monthsList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];

const monthlyData = computed(() => {
  const currentMonthIdx = new Date().getMonth();
  const collectedVal = Number(props.collected ?? 0);
  const billedVal = Number(props.billed ?? 0);
  const isZero = collectedVal <= 0 && billedVal <= 0;

  return monthsList.map((m, idx) => {
    if (isZero) {
      return { month: m, value: 0, heightPct: 0, label: '$0.00' };
    }
    if (idx === Math.min(currentMonthIdx, 9)) {
      const maxVal = Math.max(billedVal, collectedVal, 100);
      const height = Math.min(100, Math.max(8, Math.round((collectedVal / maxVal) * 100)));
      return { month: m, value: collectedVal, heightPct: height, label: `$${collectedVal.toFixed(2)}` };
    }
    return { month: m, value: 0, heightPct: 0, label: '$0.00' };
  });
});

const hoveredMonth = ref<string | null>('Jan');
</script>

<template>
  <div class="analytics-card fees-overview-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box green-box">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" />
          </svg>
        </div>
        <div class="header-text-group">
          <h3 class="card-title">Fees & Revenue Overview</h3>
          <p class="card-sub">Monthly fee collection progress</p>
        </div>
      </div>

      <!-- Filter Dropdown -->
      <div class="period-select-wrap">
        <select v-model="selectedPeriod" class="period-select">
          <option value="This Year">This Year</option>
          <option value="Last Year">Last Year</option>
        </select>
        <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Monthly Bar Chart -->
    <div class="barchart-container">
      <!-- Y-Axis Scale -->
      <div class="y-axis">
        <span>$500</span>
        <span>$400</span>
        <span>$300</span>
        <span>$200</span>
        <span>$100</span>
        <span>$0</span>
      </div>

      <!-- Bars Area -->
      <div class="bars-wrapper">
        <div
          v-for="item in monthlyData"
          :key="item.month"
          class="bar-column"
          @mouseenter="hoveredMonth = item.month"
          @mouseleave="hoveredMonth = 'Jan'"
        >
          <!-- Active Value Tooltip Pill -->
          <div
            v-if="hoveredMonth === item.month"
            class="bar-tooltip"
          >
            {{ item.label }}
          </div>

          <!-- Bar Track and Fill -->
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{ height: `${item.heightPct}%` }"
            />
          </div>

          <!-- Month Label -->
          <span class="month-label" :class="{ 'active-month': hoveredMonth === item.month }">
            {{ item.month }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analytics-card {
  background: linear-gradient(145deg, #F0FDF8 0%, #E3F9EF 100%);
  border: 1.5px solid #A7F3D0;
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 8px 24px -4px rgba(16, 185, 129, 0.1), inset 0 1px 0 #FFFFFF;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.analytics-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px -4px rgba(16, 185, 129, 0.18);
  border-color: #6EE7B7;
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

.green-box {
  background-color: #ECFDF5;
  color: #10B981;
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

/* Bar Chart Layout */
.barchart-container {
  display: flex;
  gap: 0.65rem;
  height: 140px;
  padding-top: 0.85rem;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 0.68rem;
  color: #94A3B8;
  font-weight: 500;
  padding-bottom: 1.2rem;
  text-align: right;
  min-width: 32px;
}

.bars-wrapper {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex: 1;
  gap: 0.35rem;
}

.bar-column {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
  cursor: pointer;
}

.bar-tooltip {
  position: absolute;
  top: -12px;
  background-color: #0F172A;
  color: #FFFFFF;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 5;
}

.bar-track {
  width: 100%;
  max-width: 18px;
  flex: 1;
  display: flex;
  align-items: flex-end;
  background: transparent;
  margin-bottom: 0.35rem;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #3B82F6 0%, #1D4ED8 100%);
  border-radius: 5px 5px 2px 2px;
  transition: all 0.3s ease;
}

.bar-column:hover .bar-fill {
  background: linear-gradient(180deg, #60A5FA 0%, #2563EB 100%);
  transform: scaleY(1.02);
}

.month-label {
  font-size: 0.68rem;
  color: #64748B;
  font-weight: 500;
  line-height: 1;
}

.active-month {
  color: #0F172A;
  font-weight: 700;
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
  .barchart-container {
    gap: 0.25rem;
  }
}
</style>
