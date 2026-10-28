<script setup lang="ts">
import { ref } from 'vue';
import { TimetableConflictDetail } from '../../../../types/school';

defineProps<{
  conflicts: TimetableConflictDetail[];
}>();

const emit = defineEmits<{
  (e: 'reviewConflict', conflict: TimetableConflictDetail): void;
}>();

const isExpanded = ref(true);
</script>

<template>
  <div v-if="conflicts.length > 0" class="conflict-banner">
    <div class="banner-main-row">
      <div class="banner-left">
        <div class="warning-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
        <div class="banner-texts">
          <h4 class="banner-title">
            {{ conflicts.length }} Scheduling {{ conflicts.length === 1 ? 'Conflict' : 'Conflicts' }} Detected
          </h4>
          <p class="banner-subtitle">
            Overlapping time slots exist in the active academic year. Resolve these conflicts to ensure valid school operations.
          </p>
        </div>
      </div>

      <button
        type="button"
        class="toggle-expand-btn"
        @click="isExpanded = !isExpanded"
      >
        <span>{{ isExpanded ? 'Hide Details' : 'View Conflicts' }}</span>
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          :class="{ 'rotate-180': isExpanded }"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
    </div>

    <!-- Collapsible Conflict List -->
    <div v-if="isExpanded" class="conflict-items-list">
      <div
        v-for="(c, idx) in conflicts"
        :key="idx"
        class="conflict-item-card"
        @click="emit('reviewConflict', c)"
      >
        <div class="conflict-type-tag" :class="`type-${c.conflict_type.toLowerCase()}`">
          {{ c.conflict_type }} CONFLICT
        </div>
        <div class="conflict-details">
          <p class="conflict-msg">{{ c.message }}</p>
          <div class="conflict-meta">
            <span class="meta-item">
              <strong>Day:</strong> {{ c.day_of_week }}
            </span>
            <span class="meta-item">
              <strong>Time:</strong> {{ c.start_time }} – {{ c.end_time }}
            </span>
            <span v-if="c.room" class="meta-item">
              <strong>Room:</strong> {{ c.room }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.conflict-banner {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
  animation: fadeIn 0.2s ease-out;
  width: 100%;
}

.banner-main-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.banner-left {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  min-width: 0;
  flex: 1;
}

.warning-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  background: #fef3c7;
  color: #b45309;
  border-radius: var(--radius-md, 0.5rem);
  flex-shrink: 0;
}

.warning-icon-wrap svg {
  width: 1.25rem;
  height: 1.25rem;
}

.banner-texts {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.banner-title {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #92400e;
  margin: 0;
}

.banner-subtitle {
  font-size: 0.8125rem;
  color: #b45309;
  margin: 0;
}

.toggle-expand-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #92400e;
  background: #fef3c7;
  border: 1px solid #fde68a;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.toggle-expand-btn:hover {
  background: #fde68a;
}

.toggle-expand-btn svg {
  width: 0.875rem;
  height: 0.875rem;
  transition: transform 0.2s ease;
}

.rotate-180 {
  transform: rotate(180deg);
}

.conflict-items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #fde68a;
}

.conflict-item-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  background: #ffffff;
  border: 1px solid #fed7aa;
  border-radius: var(--radius-md, 0.5rem);
  box-sizing: border-box;
}

.conflict-type-tag {
  font-size: 0.6875rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 0.25rem;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.type-class {
  background: #fee2e2;
  color: #991b1b;
}

.type-teacher {
  background: #ffedd5;
  color: #9a3412;
}

.type-room {
  background: #fef3c7;
  color: #854d0e;
}

.conflict-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.conflict-msg {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.conflict-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  font-size: 0.75rem;
  color: #64748b;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
