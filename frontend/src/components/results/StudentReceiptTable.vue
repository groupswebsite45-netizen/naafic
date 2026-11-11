<script setup lang="ts">
import { ref, computed } from 'vue';
import { StudentReceiptStatusItem } from '../../types/resultWorkflow';

interface Props {
  receipts: StudentReceiptStatusItem[];
  releasedCount: number;
  viewedCount: number;
  notViewedCount: number;
  isLoading?: boolean;
}

const props = defineProps<Props>();

const filterTab = ref<'ALL' | 'VIEWED' | 'NOT_VIEWED'>('ALL');

const filteredReceipts = computed(() => {
  if (filterTab.value === 'VIEWED') {
    return props.receipts.filter((r) => r.status === 'VIEWED');
  }
  if (filterTab.value === 'NOT_VIEWED') {
    return props.receipts.filter((r) => r.status === 'RELEASED');
  }
  return props.receipts;
});

function formatDate(dateStr?: string) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
</script>

<template>
  <div class="receipt-container">
    <!-- Header with KPI badges and Tabs -->
    <div class="receipt-header">
      <div class="receipt-title-wrap">
        <h4 class="receipt-title">Student Result Receipt & Visibility Tracking</h4>
        <p class="receipt-subtitle">Verify whether students have received and actually viewed their released results.</p>
      </div>

      <div class="receipt-kpis">
        <div class="kpi-pill released">
          <span class="kpi-pill-label">Released</span>
          <span class="kpi-pill-val">{{ releasedCount }} / {{ receipts.length }}</span>
        </div>
        <div class="kpi-pill viewed">
          <span class="kpi-pill-label">Viewed</span>
          <span class="kpi-pill-val">{{ viewedCount }}</span>
        </div>
        <div class="kpi-pill not-viewed">
          <span class="kpi-pill-label">Not Viewed</span>
          <span class="kpi-pill-val">{{ notViewedCount }}</span>
        </div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="tab-row">
      <button
        type="button"
        class="tab-btn"
        :class="{ 'active': filterTab === 'ALL' }"
        @click="filterTab = 'ALL'"
      >
        All Enrolled ({{ receipts.length }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ 'active': filterTab === 'VIEWED' }"
        @click="filterTab = 'VIEWED'"
      >
        Viewed by Student ({{ viewedCount }})
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ 'active': filterTab === 'NOT_VIEWED' }"
        @click="filterTab = 'NOT_VIEWED'"
      >
        Awaiting Student View ({{ notViewedCount }})
      </button>
    </div>

    <!-- Desktop Table -->
    <div tabindex="0" role="region" aria-label="Student receipt tracking table" class="table-wrapper desktop-only">
      <table class="receipt-table" aria-label="Student Receipt Tracking">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col">STUDENT</th>
            <th scope="col">ADMISSION NO</th>
            <th scope="col" class="text-center">DELIVERY STATUS</th>
            <th scope="col">FIRST VIEWED</th>
            <th scope="col">LAST VIEWED</th>
            <th scope="col" class="text-center">VIEW COUNT</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td colspan="7" class="loading-cell">Loading student receipt tracking records...</td>
          </tr>
          <tr v-else-if="filteredReceipts.length === 0">
            <td colspan="7" class="empty-cell">No student records found matching this filter.</td>
          </tr>
          <tr v-for="(rec, idx) in filteredReceipts" :key="rec.student_id" class="receipt-row">
            <td class="idx-col">{{ idx + 1 }}</td>
            <td class="name-col">
              <strong>{{ rec.student_name }}</strong>
            </td>
            <td class="adm-col">{{ rec.admission_number }}</td>
            <td class="text-center">
              <span
                class="status-pill"
                :class="rec.status.toLowerCase().replace('_', '-')"
              >
                <span class="status-dot" />
                {{ rec.status === 'VIEWED' ? 'VIEWED' : (rec.status === 'RELEASED' ? 'RELEASED (NOT VIEWED)' : 'NOT RELEASED') }}
              </span>
            </td>
            <td class="time-col">{{ formatDate(rec.first_viewed_at) }}</td>
            <td class="time-col">{{ formatDate(rec.last_viewed_at) }}</td>
            <td class="text-center count-col">
              <span v-if="rec.view_count > 0" class="count-badge">{{ rec.view_count }}</span>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card List -->
    <div class="mobile-only mobile-cards">
      <div
        v-for="rec in filteredReceipts"
        :key="`mob-rc-${rec.student_id}`"
        class="mobile-rec-card"
      >
        <div class="mobile-card-head">
          <div>
            <h5 class="mobile-student-name">{{ rec.student_name }}</h5>
            <span class="mobile-student-adm">{{ rec.admission_number }}</span>
          </div>
          <span
            class="status-pill"
            :class="rec.status.toLowerCase().replace('_', '-')"
          >
            {{ rec.status === 'VIEWED' ? 'VIEWED' : 'NOT VIEWED' }}
          </span>
        </div>
        <div class="mobile-meta-row">
          <div class="meta-item">
            <span class="meta-label">First Viewed</span>
            <span class="meta-val">{{ formatDate(rec.first_viewed_at) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">View Count</span>
            <span class="meta-val">{{ rec.view_count > 0 ? rec.view_count : '—' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.receipt-container {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.receipt-header {
  padding: 1.25rem 1.5rem;
  background-color: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.receipt-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.2rem 0;
}

.receipt-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.receipt-kpis {
  display: flex;
  gap: 0.5rem;
}

.kpi-pill {
  display: flex;
  flex-direction: column;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  border-width: 1px;
  border-style: solid;
}

.kpi-pill.released {
  background-color: rgba(2, 132, 199, 0.1);
  border-color: rgba(2, 132, 199, 0.3);
  color: #38bdf8;
}

.kpi-pill.viewed {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.kpi-pill.not-viewed {
  background-color: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

.kpi-pill-label {
  font-size: 0.5625rem;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.kpi-pill-val {
  font-size: 0.875rem;
  font-weight: 800;
  line-height: 1.2;
}

.tab-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #334155;
  background-color: rgba(15, 23, 42, 0.5);
  overflow-x: auto;
}

.tab-btn {
  background: none;
  border: 1px solid transparent;
  color: #94a3b8;
  padding: 0.35rem 0.85rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: #ffffff;
  background-color: #334155;
}

.tab-btn.active {
  background-color: #0284c7;
  color: #ffffff;
}

.table-wrapper {
  overflow-x: auto;
}

.receipt-table {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  font-size: 0.8125rem;
  text-align: left;
}

.receipt-table th {
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.receipt-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #334155;
  color: #f8fafc;
}

.receipt-row:hover {
  background-color: rgba(51, 65, 85, 0.4);
}

.idx-col { color: #64748b; font-size: 0.75rem; width: 40px; }
.adm-col { color: #94a3b8; font-variant-numeric: tabular-nums; }
.time-col { color: #cbd5e1; font-size: 0.75rem; font-variant-numeric: tabular-nums; }
.count-badge {
  background-color: #0f172a;
  border: 1px solid #334155;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
  color: #38bdf8;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.status-pill.viewed {
  background-color: rgba(16, 185, 129, 0.12);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-pill.released {
  background-color: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-pill.not-released {
  background-color: rgba(100, 116, 139, 0.12);
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.text-center { text-align: center; }
.text-muted { color: #64748b; }
.loading-cell, .empty-cell {
  text-align: center;
  padding: 2.5rem 1rem;
  color: #94a3b8;
}

/* Mobile Cards */
.mobile-only { display: none; }
.desktop-only { display: block; }

@media (max-width: 820px) {
  .desktop-only { display: none; }
  .mobile-only { display: block; }

  .mobile-cards {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .mobile-rec-card {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.85rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .mobile-card-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
  }

  .mobile-student-name {
    font-size: 0.875rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
  }

  .mobile-student-adm {
    font-size: 0.6875rem;
    color: #94a3b8;
  }

  .mobile-meta-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
    background-color: #1e293b;
    border-radius: 6px;
    padding: 0.5rem;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
  }

  .meta-label {
    font-size: 0.5625rem;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
  }

  .meta-val {
    font-size: 0.75rem;
    color: #cbd5e1;
    font-weight: 600;
  }
}
</style>
