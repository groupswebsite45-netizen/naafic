<script setup lang="ts">
import { computed } from 'vue';
import { TeacherSummary } from '../../../../types/school';

const props = defineProps<{
  summary: TeacherSummary | null;
  isLoading: boolean;
}>();

const items = computed(() => [
  {
    id: 'total',
    label: 'Total Faculty',
    shortLabel: 'Total',
    value: props.summary?.total_teachers ?? 0,
    caption: 'Teaching staff records',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    theme: 'blue',
  },
  {
    id: 'active',
    label: 'Active Teachers',
    shortLabel: 'Active',
    value: props.summary?.active_teachers ?? 0,
    caption: 'In active service',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    theme: 'emerald',
  },
  {
    id: 'inactive',
    label: 'Inactive / Leave',
    shortLabel: 'Inactive',
    value: props.summary?.inactive_teachers ?? 0,
    caption: 'Inactive accounts',
    icon: 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636',
    theme: 'amber',
  },
  {
    id: 'unassigned',
    label: 'Without Assignment',
    shortLabel: 'No Assign',
    value: props.summary?.unassigned_teachers ?? 0,
    caption: 'Needs class allocation',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    theme: 'purple',
  },
]);
</script>

<template>
  <div class="summary-strip" aria-label="Faculty statistics summary">
    <div
      v-for="item in items"
      :key="item.id"
      class="summary-tile"
      :class="item.theme"
    >
      <div class="tile-icon-box" :class="item.theme" aria-hidden="true">
        <svg class="tile-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" :d="item.icon" />
        </svg>
      </div>
      <div class="tile-content">
        <div class="tile-label-row">
          <span class="tile-label desktop-label">{{ item.label }}</span>
          <span class="tile-label mobile-label">{{ item.shortLabel }}</span>
        </div>
        <div class="tile-number-row">
          <span v-if="isLoading" class="skeleton-num" />
          <span v-else class="tile-number">{{ item.value.toLocaleString() }}</span>
          <span class="tile-caption">{{ item.caption }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.summary-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.15rem;
  margin-bottom: 1.35rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.summary-tile {
  border-radius: 18px;
  padding: 1.25rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1.15rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.summary-tile:hover {
  transform: translateY(-3px);
}

/* 1. Total Faculty: Soft Ice Blue */
.summary-tile.blue {
  background: linear-gradient(135deg, #EEF5FE 0%, #E0EEFF 100%);
  border: 1.5px solid #BFDBFE;
  box-shadow: 0 6px 20px -2px rgba(37, 99, 235, 0.12), inset 0 1px 0 #FFFFFF;
}
.summary-tile.blue:hover {
  border-color: #60A5FA;
  box-shadow: 0 10px 28px -3px rgba(37, 99, 235, 0.22);
}
.summary-tile.blue .tile-icon-box {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}
.summary-tile.blue .tile-label {
  color: #1D4ED8;
}

/* 2. Active Teachers: Soft Mint Green */
.summary-tile.emerald {
  background: linear-gradient(135deg, #EDFCF7 0%, #D4F7EA 100%);
  border: 1.5px solid #A7F3D0;
  box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.12), inset 0 1px 0 #FFFFFF;
}
.summary-tile.emerald:hover {
  border-color: #34D399;
  box-shadow: 0 10px 28px -3px rgba(16, 185, 129, 0.22);
}
.summary-tile.emerald .tile-icon-box {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
}
.summary-tile.emerald .tile-label {
  color: #047857;
}

/* 3. Inactive / Leave: Soft Sunny Amber */
.summary-tile.amber {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1.5px solid #FDE68A;
  box-shadow: 0 6px 20px -2px rgba(245, 158, 11, 0.12), inset 0 1px 0 #FFFFFF;
}
.summary-tile.amber:hover {
  border-color: #F59E0B;
  box-shadow: 0 10px 28px -3px rgba(245, 158, 11, 0.22);
}
.summary-tile.amber .tile-icon-box {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.35);
}
.summary-tile.amber .tile-label {
  color: #B45309;
}

/* 4. Without Assignment: Soft Lavender Purple */
.summary-tile.purple {
  background: linear-gradient(135deg, #F7F3FE 0%, #E9E0FD 100%);
  border: 1.5px solid #DDD6FE;
  box-shadow: 0 6px 20px -2px rgba(139, 92, 246, 0.12), inset 0 1px 0 #FFFFFF;
}
.summary-tile.purple:hover {
  border-color: #8B5CF6;
  box-shadow: 0 10px 28px -3px rgba(139, 92, 246, 0.22);
}
.summary-tile.purple .tile-icon-box {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}
.summary-tile.purple .tile-label {
  color: #6D28D9;
}

/* Icon Box */
.tile-icon-box {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.summary-tile:hover .tile-icon-box {
  transform: scale(1.08);
}

.tile-svg {
  width: 24px;
  height: 24px;
}

/* Tile Content */
.tile-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.tile-label-row {
  margin-bottom: 0.2rem;
}

.tile-label {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mobile-label {
  display: none;
}

.tile-number-row {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tile-number {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.tile-caption {
  font-size: 0.74rem;
  color: #475569;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.skeleton-num {
  display: inline-block;
  width: 48px;
  height: 1.85rem;
  background-color: rgba(226, 232, 240, 0.7);
  border-radius: 6px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 1024px) {
  .summary-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
  }
}

@media (max-width: 640px) {
  .summary-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
    margin-bottom: 1rem;
  }

  .summary-tile {
    padding: 0.85rem 0.75rem;
    gap: 0.65rem;
    border-radius: 14px;
  }

  .tile-icon-box {
    width: 38px;
    height: 38px;
    min-width: 38px;
    border-radius: 10px;
  }

  .tile-svg {
    width: 20px;
    height: 20px;
  }

  .desktop-label {
    display: none;
  }

  .mobile-label {
    display: inline-block;
    font-size: 0.72rem;
  }

  .tile-number {
    font-size: 1.35rem;
  }

  .tile-caption {
    display: none;
  }
}

@media (max-width: 360px) {
  .summary-strip {
    gap: 0.5rem;
  }

  .summary-tile {
    padding: 0.75rem 0.55rem;
    gap: 0.5rem;
    border-radius: 12px;
  }

  .tile-icon-box {
    width: 32px;
    height: 32px;
    min-width: 32px;
    border-radius: 8px;
  }

  .tile-svg {
    width: 17px;
    height: 17px;
  }

  .mobile-label {
    font-size: 0.66rem;
  }

  .tile-number {
    font-size: 1.2rem;
  }
}
</style>
