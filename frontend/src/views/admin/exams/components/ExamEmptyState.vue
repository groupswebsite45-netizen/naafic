<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

defineProps<{
  hasFilters?: boolean;
}>();

const emit = defineEmits<{
  (e: 'clear-filters'): void;
}>();
</script>

<template>
  <div class="empty-state-card">
    <div class="empty-icon-circle">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>

    <div class="empty-text">
      <h2 class="empty-title">
        {{ hasFilters ? 'No matching examinations found' : 'No examinations scheduled yet' }}
      </h2>
      <p class="empty-desc">
        {{
          hasFilters
            ? 'No exams match your current filter parameters. Try clearing some filters or searching for different keywords.'
            : 'Schedule your first examination to begin managing class assessments, recording student marks, and generating official report cards.'
        }}
      </p>
    </div>

    <div class="empty-actions">
      <button
        v-if="hasFilters"
        type="button"
        class="secondary-btn"
        @click="emit('clear-filters')"
      >
        Clear Filters
      </button>
      <button
        type="button"
        class="primary-btn"
        @click="router.push('/admin/exams/create')"
      >
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        <span>Schedule Examination</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.empty-state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1.5rem;
  background-color: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
}

.empty-icon-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background-color: #f1f5f9;
  border-radius: 50%;
  color: #64748b;
  margin-bottom: 1.25rem;
}

.empty-icon {
  width: 32px;
  height: 32px;
}

.empty-text {
  max-width: 440px;
  margin-bottom: 1.5rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.empty-desc {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.5;
  margin: 0;
}

.empty-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  border: 1px solid #4338ca;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
  transform: translateY(-1px);
}

.secondary-btn {
  padding: 0.6rem 1.15rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  background-color: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  cursor: pointer;
}

.secondary-btn:hover {
  background-color: #f8fafc;
}

.btn-icon {
  width: 16px;
  height: 16px;
}
</style>
