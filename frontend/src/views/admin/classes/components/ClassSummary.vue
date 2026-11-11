<script setup lang="ts">
import { ClassSummary } from '../../../../types/school';

defineProps<{
  summary: ClassSummary | null;
  isLoading: boolean;
}>();
</script>

<template>
  <div class="stats-grid">
    <!-- Total Classes -->
    <div class="stat-card blue">
      <div class="stat-icon icon-blue">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
          <path d="M6 6h10" />
          <path d="M6 10h10" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Total Classes</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.total_classes ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Active Classes -->
    <div class="stat-card emerald">
      <div class="stat-icon icon-emerald">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Active Classes</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.active_classes ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Students Enrolled -->
    <div class="stat-card purple">
      <div class="stat-icon icon-purple">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Students Enrolled</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.total_students_enrolled ?? 0 }}
          </template>
        </div>
      </div>
    </div>

    <!-- Available Seats -->
    <div class="stat-card amber">
      <div class="stat-icon icon-amber">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect width="18" height="18" x="3" y="3" rx="2" />
          <path d="M3 9h18" />
          <path d="M9 21V9" />
        </svg>
      </div>
      <div class="stat-content">
        <span class="stat-label">Available Seats</span>
        <div class="stat-value">
          <template v-if="isLoading">
            <div class="stat-skeleton"></div>
          </template>
          <template v-else>
            {{ summary?.available_seats ?? 0 }}
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1.15rem;
  width: 100%;
}

.stat-card {
  border-radius: 18px;
  padding: 1.25rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1.15rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-3px);
}

/* 1. Total Classes: Soft Ice Blue */
.stat-card.blue {
  background: linear-gradient(135deg, #EEF5FE 0%, #E0EEFF 100%);
  border: 1.5px solid #BFDBFE;
  box-shadow: 0 6px 20px -2px rgba(37, 99, 235, 0.12), inset 0 1px 0 #FFFFFF;
}
.stat-card.blue:hover {
  border-color: #60A5FA;
  box-shadow: 0 10px 28px -3px rgba(37, 99, 235, 0.22);
}
.stat-card.blue .stat-icon {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}
.stat-card.blue .stat-label {
  color: #1D4ED8;
}

/* 2. Active Classes: Soft Mint Green */
.stat-card.emerald {
  background: linear-gradient(135deg, #EDFCF7 0%, #D4F7EA 100%);
  border: 1.5px solid #A7F3D0;
  box-shadow: 0 6px 20px -2px rgba(16, 185, 129, 0.12), inset 0 1px 0 #FFFFFF;
}
.stat-card.emerald:hover {
  border-color: #34D399;
  box-shadow: 0 10px 28px -3px rgba(16, 185, 129, 0.22);
}
.stat-card.emerald .stat-icon {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
}
.stat-card.emerald .stat-label {
  color: #047857;
}

/* 3. Students Enrolled: Soft Lavender Purple */
.stat-card.purple {
  background: linear-gradient(135deg, #F7F3FE 0%, #E9E0FD 100%);
  border: 1.5px solid #DDD6FE;
  box-shadow: 0 6px 20px -2px rgba(139, 92, 246, 0.12), inset 0 1px 0 #FFFFFF;
}
.stat-card.purple:hover {
  border-color: #8B5CF6;
  box-shadow: 0 10px 28px -3px rgba(139, 92, 246, 0.22);
}
.stat-card.purple .stat-icon {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
}
.stat-card.purple .stat-label {
  color: #6D28D9;
}

/* 4. Available Seats: Soft Sunny Amber */
.stat-card.amber {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1.5px solid #FDE68A;
  box-shadow: 0 6px 20px -2px rgba(245, 158, 11, 0.12), inset 0 1px 0 #FFFFFF;
}
.stat-card.amber:hover {
  border-color: #F59E0B;
  box-shadow: 0 10px 28px -3px rgba(245, 158, 11, 0.22);
}
.stat-card.amber .stat-icon {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: #FFFFFF;
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.35);
}
.stat-card.amber .stat-label {
  color: #B45309;
}

/* Icon Box */
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.08);
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

/* Content */
.stat-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.stat-label {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.2rem;
}

.stat-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0F172A;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.stat-skeleton {
  width: 48px;
  height: 1.85rem;
  background-color: rgba(226, 232, 240, 0.7);
  border-radius: 6px;
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
  }
  .stat-card {
    padding: 0.75rem;
    gap: 0.5rem;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
