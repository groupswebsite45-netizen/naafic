<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const actions = [
  {
    label: 'Register New Student',
    path: '/admin/students',
    icon: 'student',
    theme: 'blue-action',
  },
  {
    label: 'Add Teacher',
    path: '/admin/teachers',
    icon: 'teacher',
    theme: 'green-action',
  },
  {
    label: 'Create Class',
    path: '/admin/classes',
    icon: 'class',
    theme: 'purple-action',
  },
  {
    label: 'Generate Timetable',
    path: '/admin/timetable',
    icon: 'timetable',
    theme: 'orange-action',
  },
];

function navigateTo(path: string) {
  router.push(path);
}
</script>

<template>
  <div class="bottom-card quick-actions-card">
    <!-- Header -->
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon-box amber-box">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 2v11h3v9l7-12h-4l4-8z" />
          </svg>
        </div>
        <h3 class="card-title">Quick Actions</h3>
      </div>
    </div>

    <!-- 4 Pastel Action Tiles -->
    <div class="actions-grid">
      <button
        v-for="act in actions"
        :key="act.path"
        type="button"
        class="action-tile"
        :class="act.theme"
        @click="navigateTo(act.path)"
      >
        <span class="tile-icon-wrap" aria-hidden="true">
          <!-- Student Icon -->
          <svg v-if="act.icon === 'student'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
          <!-- Teacher Icon -->
          <svg v-else-if="act.icon === 'teacher'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
          </svg>
          <!-- Class Icon -->
          <svg v-else-if="act.icon === 'class'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z" />
          </svg>
          <!-- Timetable Icon -->
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z" />
          </svg>
        </span>
        <span class="action-label">{{ act.label }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.bottom-card {
  background: linear-gradient(145deg, #FFFDF5 0%, #FEF8E7 100%);
  border: 1.5px solid #FDE68A;
  border-radius: 20px;
  padding: 1.4rem 1.5rem;
  box-shadow: 0 8px 24px -4px rgba(245, 158, 11, 0.1), inset 0 1px 0 #FFFFFF;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.bottom-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px -4px rgba(245, 158, 11, 0.18);
  border-color: #F59E0B;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
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

.amber-box {
  background-color: #FDE68A;
  color: #B45309;
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

/* 4 Action Tiles Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.85rem;
}

.action-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 1.15rem 0.5rem;
  border-radius: 14px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
}

.action-tile:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.tile-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tile-icon-wrap svg {
  width: 24px;
  height: 24px;
}

.action-label {
  font-size: 0.82rem;
  font-weight: 700;
  line-height: 1.25;
}

/* Pastel Themes with borders */
.blue-action {
  background-color: #FFFFFF;
  border-color: #BFDBFE;
  color: #2563EB;
}
.blue-action:hover {
  background-color: #EFF6FF;
  border-color: #60A5FA;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.18);
}

.green-action {
  background-color: #FFFFFF;
  border-color: #A7F3D0;
  color: #059669;
}
.green-action:hover {
  background-color: #ECFDF5;
  border-color: #34D399;
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.18);
}

.purple-action {
  background-color: #FFFFFF;
  border-color: #DDD6FE;
  color: #7C3AED;
}
.purple-action:hover {
  background-color: #FAF5FF;
  border-color: #A78BFA;
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.18);
}

.orange-action {
  background-color: #FFFFFF;
  border-color: #FED7AA;
  color: #EA580C;
}
.orange-action:hover {
  background-color: #FFF7ED;
  border-color: #FB923C;
  box-shadow: 0 6px 16px rgba(234, 88, 12, 0.18);
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .bottom-card {
    padding: 1.1rem;
  }

  .action-tile {
    padding: 0.9rem 0.5rem;
    min-height: 44px;
    min-width: 0;
  }
}

@media (max-width: 359px) {
  .actions-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.6rem;
  }
  .action-tile {
    padding: 0.75rem 0.4rem;
  }
  .action-label {
    font-size: 0.76rem;
  }
}
</style>
