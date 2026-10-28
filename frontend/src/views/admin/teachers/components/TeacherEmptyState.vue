<script setup lang="ts">
defineProps<{
  hasFilters: boolean;
}>();

const emit = defineEmits<{
  (e: 'clearFilters'): void;
  (e: 'register'): void;
}>();
</script>

<template>
  <div class="empty-state-box">
    <div class="empty-icon-circle">
      <svg class="empty-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    </div>
    <h3 class="empty-title">
      {{ hasFilters ? 'No matching faculty members found' : 'No faculty members registered yet' }}
    </h3>
    <p class="empty-desc">
      {{
        hasFilters
          ? 'No teachers match your search or filter criteria. Try adjusting your search query or reset active filters.'
          : 'Begin establishing your school faculty by registering teachers, assigning classes, and configuring portal accounts.'
      }}
    </p>
    <div class="empty-actions">
      <button v-if="hasFilters" type="button" class="btn-secondary" @click="emit('clearFilters')">
        Reset All Filters
      </button>
      <button type="button" class="btn-primary" @click="emit('register')">
        + Register Teacher
      </button>
    </div>
  </div>
</template>

<style scoped>
.empty-state-box {
  padding: 3.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
}

.empty-icon-circle {
  width: 52px;
  height: 52px;
  border-radius: 9999px;
  background: #eff6ff;
  color: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.875rem;
}

.empty-svg {
  width: 26px;
  height: 26px;
}

.empty-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.empty-desc {
  font-size: 0.8125rem;
  color: #64748b;
  max-width: 420px;
  margin: 0.35rem 0 1.25rem;
  line-height: 1.4;
}

.empty-actions {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-primary {
  height: 36px;
  padding: 0 1rem;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  height: 36px;
  padding: 0 0.875rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f1f5f9;
  color: #0f172a;
}
</style>
