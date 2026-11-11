<script setup lang="ts">
interface Props {
  title: string;
  value: string | number;
  subtext?: string;
  iconVariant?: 'blue' | 'green' | 'purple' | 'orange' | 'amber' | 'red' | 'emerald';
  trendBadge?: string;
  hasChevron?: boolean;
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  subtext: '',
  iconVariant: 'blue',
  trendBadge: '',
  hasChevron: false,
  loading: false,
});
</script>

<template>
  <div
    class="stat-card"
    :class="[
      `variant-${iconVariant}`,
      { 'is-primary-kpi': !hasChevron, 'is-operational-kpi': hasChevron }
    ]"
  >
    <!-- Icon Container -->
    <div class="stat-icon-wrap">
      <slot name="icon">
        <!-- Blue: Graduation Cap (Total Students) -->
        <svg v-if="iconVariant === 'blue'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 3L1 9L12 15L21 10.09V17H23V9M5 13.18V17.18C5 19.94 8.13 22.18 12 22.18C15.87 22.18 19 19.94 19 17.18V13.18L12 17L5 13.18Z" />
        </svg>

        <!-- Green: Faculty Group (Total Teachers) -->
        <svg v-else-if="iconVariant === 'green'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
        </svg>

        <!-- Purple: Open Book (Total Classes) -->
        <svg v-else-if="iconVariant === 'purple'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" />
        </svg>

        <!-- Orange: Curriculum Book (Total Subjects) -->
        <svg v-else-if="iconVariant === 'orange'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 5c-1.11-.35-2.33-.5-3.5-.5-1.95 0-4.05.4-5.5 1.5-1.45-1.1-3.55-1.5-5.5-1.5S2.45 4.9 1 6v14.65c0 .25.25.5.5.5.1 0 .15-.05.25-.05C3.1 20.45 5.05 20 6.5 20c1.95 0 4.05.4 5.5 1.5 1.35-.85 3.8-1.5 5.5-1.5 1.65 0 3.35.3 4.75 1.05.1.05.15.05.25.05.25 0 .5-.25.5-.5V6c-.6-.45-1.25-.75-2-1zm-1 13.5c-1.1-.35-2.3-.5-3.5-.5-1.7 0-4.15.65-5.5 1.5V8c1.35-.85 3.8-1.5 5.5-1.5 1.2 0 2.4.15 3.5.5v11.5z" />
        </svg>

        <!-- Amber: Calendar / Clock (Today's Classes) -->
        <svg v-else-if="iconVariant === 'amber'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z" />
        </svg>

        <!-- Red: Clipboard (Upcoming Exams) -->
        <svg v-else-if="iconVariant === 'red'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
        </svg>

        <!-- Emerald: Money / Dollar (Fees Collected) -->
        <svg v-else-if="iconVariant === 'emerald'" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14.5h-2v-1c-1.65 0-3-.89-3-2.5 0-1.61 1.35-2.5 3-2.5v-3c-.83 0-1.5.67-1.5 1.5H8c0-1.66 1.34-3 3-3v-1h2v1c1.65 0 3 .89 3 2.5 0 1.61-1.35 2.5-3 2.5v3c.83 0 1.5-.67 1.5-1.5h1.5c0 1.66-1.34 3-3 3v1z" />
        </svg>

        <!-- Generic / Pie chart (Outstanding Fees) -->
        <svg v-else viewBox="0 0 24 24" fill="currentColor">
          <path d="M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2 0v8.99L21.99 11C21.47 5.92 17.08 2 13 2zm0 11.01V22c4.08 0 7.47-3.92 7.99-9H13z" />
        </svg>
      </slot>
    </div>

    <!-- Main Card Body -->
    <div class="stat-body">
      <div class="stat-top-meta">
        <span class="stat-title">{{ title }}</span>
        <!-- Trend Badge Pill -->
        <span v-if="trendBadge" class="trend-badge">
          {{ trendBadge }}
        </span>
      </div>

      <div class="stat-value-row">
        <div v-if="loading" class="stat-skeleton-val"></div>
        <span v-else class="stat-value">{{ value }}</span>
      </div>

      <span v-if="subtext" class="stat-subtext">{{ subtext }}</span>
    </div>

    <!-- Optional Right Chevron for Operational Cards -->
    <div v-if="hasChevron" class="stat-chevron-wrap">
      <div class="chevron-circle">
        <svg class="chevron-arrow" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  border-radius: 20px;
  padding: 1.35rem 1.45rem;
  display: flex;
  align-items: center;
  gap: 1.15rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-3px);
}

/* =========================================================
   1. PRIMARY TOP KPI CARDS (Row 1 - Rich Pastel Gradients)
   ========================================================= */

/* 1.1 Total Students: Soft Ice Blue (#EEF5FE -> #E0EEFF) */
.is-primary-kpi.variant-blue {
  background: linear-gradient(135deg, #EEF5FE 0%, #E0EEFF 100%);
  border: 1.5px solid #BFDBFE;
  box-shadow: 0 6px 20px -2px rgba(37, 99, 235, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-primary-kpi.variant-blue:hover {
  border-color: #60A5FA;
  box-shadow: 0 10px 28px -3px rgba(37, 99, 235, 0.22);
}
.is-primary-kpi.variant-blue .stat-icon-wrap {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

/* 1.2 Total Teachers: Soft Mint Green (#EDFCF7 -> #D4F7EA) */
.is-primary-kpi.variant-green {
  background: linear-gradient(135deg, #EDFCF7 0%, #D4F7EA 100%);
  border: 1.5px solid #A7F3D0;
  box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-primary-kpi.variant-green:hover {
  border-color: #34D399;
  box-shadow: 0 10px 28px -3px rgba(16, 185, 129, 0.22);
}
.is-primary-kpi.variant-green .stat-icon-wrap {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
}

/* 1.3 Total Classes: Soft Lavender Purple (#F7F3FE -> #E9E0FD) */
.is-primary-kpi.variant-purple {
  background: linear-gradient(135deg, #F7F3FE 0%, #E9E0FD 100%);
  border: 1.5px solid #DDD6FE;
  box-shadow: 0 6px 20px -2px rgba(139, 92, 246, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-primary-kpi.variant-purple:hover {
  border-color: #A78BFA;
  box-shadow: 0 10px 28px -3px rgba(139, 92, 246, 0.22);
}
.is-primary-kpi.variant-purple .stat-icon-wrap {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}

/* 1.4 Total Subjects: Soft Peach/Amber (#FEF7EE -> #FDE7CC) */
.is-primary-kpi.variant-orange {
  background: linear-gradient(135deg, #FEF7EE 0%, #FDE7CC 100%);
  border: 1.5px solid #FED7AA;
  box-shadow: 0 6px 20px -2px rgba(249, 115, 22, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-primary-kpi.variant-orange:hover {
  border-color: #FB923C;
  box-shadow: 0 10px 28px -3px rgba(249, 115, 22, 0.22);
}
.is-primary-kpi.variant-orange .stat-icon-wrap {
  background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(249, 115, 22, 0.35);
}

/* =========================================================
   2. OPERATIONAL KPI CARDS (Row 2 - Rich Pastel Tints, NO LONGER WHITE!)
   ========================================================= */

/* 2.1 Today's Classes: Soft Warm Sunny Amber (#FFFBEB -> #FEF3C7) */
.is-operational-kpi.variant-amber {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1.5px solid #FDE68A;
  box-shadow: 0 6px 20px -2px rgba(245, 158, 11, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-operational-kpi.variant-amber:hover {
  border-color: #F59E0B;
  box-shadow: 0 10px 28px -3px rgba(245, 158, 11, 0.22);
}
.is-operational-kpi.variant-amber .stat-icon-wrap {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.35);
}
.is-operational-kpi.variant-amber .chevron-circle {
  background: rgba(245, 158, 11, 0.12);
  color: #B45309;
}

/* 2.2 Upcoming Exams: Soft Rose / Coral Red (#FEF2F2 -> #FEE2E2) */
.is-operational-kpi.variant-red {
  background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
  border: 1.5px solid #FECACA;
  box-shadow: 0 6px 20px -2px rgba(239, 68, 68, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-operational-kpi.variant-red:hover {
  border-color: #EF4444;
  box-shadow: 0 10px 28px -3px rgba(239, 68, 68, 0.22);
}
.is-operational-kpi.variant-red .stat-icon-wrap {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.35);
}
.is-operational-kpi.variant-red .chevron-circle {
  background: rgba(239, 68, 68, 0.12);
  color: #B91C1C;
}

/* 2.3 Fees Collected: Soft Emerald Mint (#ECFDF5 -> #D1FAE5) */
.is-operational-kpi.variant-emerald {
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  border: 1.5px solid #A7F3D0;
  box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-operational-kpi.variant-emerald:hover {
  border-color: #10B981;
  box-shadow: 0 10px 28px -3px rgba(16, 185, 129, 0.22);
}
.is-operational-kpi.variant-emerald .stat-icon-wrap {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
}
.is-operational-kpi.variant-emerald .chevron-circle {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

/* 2.4 Outstanding Fees: Soft Royal Purple / Violet (#FAF5FF -> #EDE9FE) */
.is-operational-kpi.variant-purple {
  background: linear-gradient(135deg, #FAF5FF 0%, #EDE9FE 100%);
  border: 1.5px solid #DDD6FE;
  box-shadow: 0 6px 20px -2px rgba(139, 92, 246, 0.12), inset 0 1px 0 #FFFFFF;
}
.is-operational-kpi.variant-purple:hover {
  border-color: #8B5CF6;
  box-shadow: 0 10px 28px -3px rgba(139, 92, 246, 0.22);
}
.is-operational-kpi.variant-purple .stat-icon-wrap {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}
.is-operational-kpi.variant-purple .chevron-circle {
  background: rgba(139, 92, 246, 0.12);
  color: #6D28D9;
}

/* =========================================================
   Shared Layout & Elements
   ========================================================= */
.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.stat-card:hover .stat-icon-wrap {
  transform: scale(1.06);
}

.stat-icon-wrap svg {
  width: 26px;
  height: 26px;
}

.stat-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.stat-top-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.stat-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
  white-space: nowrap;
}

.trend-badge {
  background-color: #DCFCE7;
  color: #15803D;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  line-height: 1.2;
}

.stat-value-row {
  margin: 0.2rem 0 0.1rem 0;
}

.stat-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.stat-subtext {
  font-size: 0.76rem;
  color: #475569;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Right Chevron with Soft Circle Badge */
.stat-chevron-wrap {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.chevron-circle {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.chevron-arrow {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease;
}

.stat-card:hover .chevron-arrow {
  transform: translateX(3px);
}

/* Skeleton loader */
.stat-skeleton-val {
  height: 1.85rem;
  width: 60px;
  background-color: rgba(226, 232, 240, 0.7);
  border-radius: 6px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
