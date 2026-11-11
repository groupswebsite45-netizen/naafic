<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

defineProps<{
  title?: string;
  subtitle?: string;
}>();

function navigateToResults() {
  router.push('/admin/results');
}
</script>

<template>
  <div class="exam-header-container">
    <div class="exam-header-info">
      <div class="title-row">
        <div class="exam-icon-badge">
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h1 class="exam-title">{{ title || 'Examinations Monitoring' }}</h1>
          <p class="exam-subtitle">
            {{ subtitle || 'Monitor teacher-created examinations, class schedules, and review submitted assessment results.' }}
          </p>
        </div>
      </div>
    </div>

    <div class="exam-header-actions">
      <button
        type="button"
        class="results-btn"
        @click="navigateToResults"
      >
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
        </svg>
        <span>Results Management</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.exam-header-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
}

.exam-header-info {
  min-width: 0;
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.exam-icon-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4338ca 0%, #312e81 100%);
  color: #ffffff;
  flex-shrink: 0;
  box-shadow: 0 4px 6px -1px rgba(67, 56, 202, 0.2);
}

.icon-svg {
  width: 24px;
  height: 24px;
}

.exam-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.25;
}

.exam-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary, #64748b);
  margin-top: 0.25rem;
  line-height: 1.4;
}

.exam-header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.schedule-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.55rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  border: 1px solid #4338ca;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.schedule-btn:hover {
  background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
  box-shadow: 0 4px 8px rgba(79, 70, 229, 0.3);
  transform: translateY(-1px);
}

.schedule-btn:active {
  transform: translateY(0);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

@media (max-width: 640px) {
  .exam-header-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.875rem;
    padding: 0.75rem 0;
  }

  .exam-header-actions {
    width: 100%;
  }

  .schedule-btn {
    width: 100%;
  }

  .exam-title {
    font-size: 1.25rem;
  }

  .exam-subtitle {
    font-size: 0.8125rem;
  }

  .exam-icon-badge {
    width: 38px;
    height: 38px;
  }

  .icon-svg {
    width: 20px;
    height: 20px;
  }
}
</style>
