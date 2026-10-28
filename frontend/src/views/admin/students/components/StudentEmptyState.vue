<script setup lang="ts">
defineProps<{
  hasFilters: boolean;
}>();

const emit = defineEmits<{
  (e: 'register'): void;
  (e: 'clearFilters'): void;
}>();
</script>

<template>
  <div class="empty-state-card">
    <div class="empty-icon-circle">
      <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    </div>
    <h3 class="empty-title">No Students Found</h3>
    <p class="empty-subtitle">
      {{ hasFilters ? 'No student records match your active search or filter criteria.' : 'There are currently no registered students in the school database.' }}
    </p>
    <div class="empty-actions">
      <button
        v-if="hasFilters"
        type="button"
        class="btn-secondary"
        @click="emit('clearFilters')"
      >
        Clear Active Filters
      </button>
      <button
        type="button"
        class="btn-primary"
        @click="emit('register')"
      >
        + Register New Student
      </button>
    </div>
  </div>
</template>

<style scoped>
.empty-state-card {
  padding: 3.5rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #ffffff;
}

.empty-icon-circle {
  width: 56px;
  height: 56px;
  border-radius: 9999px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.empty-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  max-width: 400px;
  margin: 0.375rem 0 1.25rem;
  line-height: 1.4;
}

.empty-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  height: 38px;
  padding: 0 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s ease;
}

.btn-primary {
  background: #2563eb;
  border: none;
  color: #ffffff;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
}

.btn-secondary:hover {
  background: #f8fafc;
}
</style>
