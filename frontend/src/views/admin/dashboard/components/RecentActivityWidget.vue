<script setup lang="ts">
import { computed } from 'vue';

interface AuditLogItem {
  id: number;
  action: string;
  status: string;
  ip_address?: string;
  created_at: string;
  details?: Record<string, any>;
}

interface Props {
  logs?: AuditLogItem[];
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  logs: () => [],
  loading: false,
});

function formatRelativeTime(dateStr?: string) {
  if (!dateStr) return 'Just now';
  try {
    const diffMs = Date.now() - new Date(dateStr).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  } catch {
    return 'Recently';
  }
}

const activities = computed(() => {
  if (!props.logs || props.logs.length === 0) return [];
  return props.logs.slice(0, 5).map((log) => {
    let icon = 'user';
    let iconBg = '#EFF6FF';
    let iconColor = '#2563EB';
    let dotColor = '#10B981';

    const actionLower = (log.action || '').toLowerCase();
    if (actionLower.includes('exam')) {
      icon = 'exam';
      iconBg = '#FEF2F2';
      iconColor = '#EF4444';
      dotColor = '#EF4444';
    } else if (actionLower.includes('class') || actionLower.includes('timetable') || actionLower.includes('schedule')) {
      icon = 'calendar';
      iconBg = '#FFF7ED';
      iconColor = '#F97316';
      dotColor = '#F97316';
    }

    return {
      id: log.id,
      title: log.action || 'System Event',
      entity: log.details?.entity || log.status || 'Completed',
      time: formatRelativeTime(log.created_at),
      icon,
      iconBg,
      iconColor,
      dotColor,
    };
  });
});
</script>

<template>
  <div class="bottom-card recent-activities-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box green-box">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" />
          </svg>
        </div>
        <h3 class="card-title">Recent Activities</h3>
      </div>

      <router-link to="/admin/notifications" class="view-all-link">
        <span>View All</span>
        <span class="arrow">&rarr;</span>
      </router-link>
    </div>

    <!-- Empty State when 0 logs -->
    <div v-if="activities.length === 0" class="empty-activities">
      <div class="empty-icon-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="empty-title">No Recent Activities</p>
      <p class="empty-desc">System events and operational logs will appear here as records are created.</p>
    </div>

    <!-- Activity Rows -->
    <div v-else class="activities-list">
      <div
        v-for="act in activities"
        :key="act.id"
        class="activity-row"
      >
        <!-- Icon -->
        <div
          class="activity-icon-wrap"
          :style="{ backgroundColor: act.iconBg, color: act.iconColor }"
        >
          <!-- User -->
          <svg v-if="act.icon === 'user'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
          <!-- Calendar -->
          <svg v-else-if="act.icon === 'calendar'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z" />
          </svg>
          <!-- Exam -->
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" />
          </svg>
        </div>

        <!-- Title & Entity -->
        <div class="activity-details">
          <span class="activity-title">{{ act.title }}</span>
          <span class="activity-entity">{{ act.entity }}</span>
        </div>

        <!-- Time & Status Dot -->
        <div class="activity-time-group">
          <span class="activity-time">{{ act.time }}</span>
          <span
            class="status-dot"
            :style="{ backgroundColor: act.dotColor }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bottom-card {
  background: linear-gradient(145deg, #F8FAFC 0%, #F1F5F9 50%, #EAEFF5 100%);
  border: 1.5px solid #CBD5E1;
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08), inset 0 1px 0 #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.bottom-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.12);
  border-color: #94A3B8;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.header-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.green-box {
  background-color: #D1FAE5;
  color: #059669;
}

.header-icon-box svg {
  width: 18px;
  height: 18px;
}

.card-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.view-all-link {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #FF5722;
  text-decoration: none;
  transition: transform 0.15s ease;
}

.view-all-link:hover {
  transform: translateX(2px);
}

.arrow {
  font-size: 0.95rem;
}

/* Activities List */
.activities-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.activity-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
  transition: all 0.2s ease;
}

.activity-row:hover {
  background: #FFFFFF;
  transform: translateX(2px);
  border-color: #CBD5E1;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.05);
}

.activity-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon-wrap svg {
  width: 18px;
  height: 18px;
}

.activity-details {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 1.5rem;
  min-width: 0;
}

.activity-title {
  font-size: 0.86rem;
  font-weight: 600;
  color: #0F172A;
  white-space: nowrap;
}

.activity-entity {
  font-size: 0.82rem;
  color: #64748B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-time-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-left: auto;
  flex-shrink: 0;
}

.activity-time {
  font-size: 0.78rem;
  color: #94A3B8;
  white-space: nowrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Empty State */
.empty-activities {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.5rem 1rem;
}

.empty-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #F1F5F9;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.65rem;
}

.empty-icon-box svg {
  width: 22px;
  height: 22px;
}

.empty-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #334155;
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.8rem;
  color: #94A3B8;
  max-width: 320px;
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 600px) {
  .activity-row {
    flex-wrap: wrap;
    align-items: flex-start;
  }
  .activity-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  .activity-time-group {
    margin-left: 0;
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
