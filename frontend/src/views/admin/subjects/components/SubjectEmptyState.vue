<script setup lang="ts">
defineProps<{
  hasFilters?: boolean;
}>();

const emit = defineEmits<{
  (e: 'create'): void;
  (e: 'reset'): void;
}>();
</script>

<template>
  <div class="empty-state-card">
    <div class="empty-icon-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
        <path d="M6 6h10" />
        <path d="M6 10h10" />
      </svg>
    </div>

    <h3 class="empty-title">
      {{ hasFilters ? 'No matching subjects found' : 'No academic subjects registered' }}
    </h3>
    <p class="empty-description">
      {{
        hasFilters
          ? 'Try adjusting your search query, status filters, or department selection.'
          : 'Create your first academic subject to organize curriculum, assign classes, allocate faculty, and generate timetables.'
      }}
    </p>

    <div class="empty-actions">
      <button
        v-if="hasFilters"
        type="button"
        class="btn-reset"
        @click="emit('reset')"
      >
        Clear All Filters
      </button>
      <button
        type="button"
        class="btn-create"
        @click="emit('create')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14" />
          <path d="M12 5v14" />
        </svg>
        <span>Add Subject</span>
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
  background-color: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 3rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  width: 100%;
  box-sizing: border-box;
}

.empty-icon-wrap {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background-color: #f1f5f9;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.empty-icon-wrap svg {
  width: 1.75rem;
  height: 1.75rem;
}

.empty-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.35rem 0;
}

.empty-description {
  font-size: 0.8125rem;
  color: #64748b;
  max-width: 24rem;
  margin: 0 0 1.25rem 0;
  line-height: 1.5;
}

.empty-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  height: 2.25rem;
  padding: 0 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-reset:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.25rem;
  padding: 0 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  background: var(--brand-primary, #1e40af);
  border: none;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-create:hover {
  background: #1d4ed8;
}

.btn-create svg {
  width: 0.875rem;
  height: 0.875rem;
}
</style>
