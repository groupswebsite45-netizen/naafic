<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Subject } from '../../../../types/school';
import SubjectStatusBadge from './SubjectStatusBadge.vue';
import SubjectActionMenu from './SubjectActionMenu.vue';

defineProps<{
  subjects: Subject[];
}>();

const emit = defineEmits<{
  (e: 'edit', subject: Subject): void;
  (e: 'assignClass', subject: Subject): void;
  (e: 'assignTeacher', subject: Subject): void;
  (e: 'toggleStatus', subject: Subject): void;
  (e: 'delete', subject: Subject): void;
}>();

const router = useRouter();

function goToProfile(id: number) {
  router.push(`/admin/subjects/${id}`);
}
</script>

<template>
  <div class="mobile-card-list">
    <div
      v-for="sub in subjects"
      :key="sub.id"
      class="subject-card"
      @click="goToProfile(sub.id)"
    >
      <!-- Card Header -->
      <div class="card-header">
        <div class="header-left">
          <h3 class="subject-name">{{ sub.name }}</h3>
          <div class="subject-sub-meta">
            <span class="code-badge">{{ sub.code }}</span>
            <span v-if="sub.department" class="dept-badge">{{ sub.department }}</span>
          </div>
        </div>
        <div class="header-right" @click.stop>
          <SubjectActionMenu
            :subject="sub"
            @edit="emit('edit', sub)"
            @assignClass="emit('assignClass', sub)"
            @assignTeacher="emit('assignTeacher', sub)"
            @toggleStatus="emit('toggleStatus', sub)"
            @delete="emit('delete', sub)"
          />
        </div>
      </div>

      <!-- Card Metrics Grid -->
      <div class="card-metrics-grid">
        <div class="metric-item">
          <span class="metric-label">Classes</span>
          <span class="metric-value">
            {{ (sub.classes_count ?? 0) > 0 ? `${sub.classes_count} Classes` : 'Unassigned' }}
          </span>
        </div>
        <div class="metric-item">
          <span class="metric-label">Teachers</span>
          <span class="metric-value">
            {{ (sub.teachers_count ?? 0) > 0 ? `${sub.teachers_count} Teachers` : 'None' }}
          </span>
        </div>
      </div>

      <!-- Status & Details Link -->
      <div class="card-footer">
        <SubjectStatusBadge :status="sub.status" size="sm" />
        <button
          type="button"
          class="view-profile-btn"
          @click.stop="goToProfile(sub.id)"
        >
          <span>View Profile</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14" />
            <path d="m12 5 7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mobile-card-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  box-sizing: border-box;
}

.subject-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  width: 100%;
  box-sizing: border-box;
}

.subject-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.subject-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0;
  white-space: normal;
  word-break: break-word;
}

.subject-sub-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.code-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.375rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-family: monospace;
  font-weight: 700;
  color: #334155;
}

.dept-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 500;
  color: #475569;
}

.header-right {
  flex-shrink: 0;
}

.card-metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: var(--radius-md, 0.5rem);
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.metric-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.metric-value {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #1e293b;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding-top: 0.25rem;
}

.view-profile-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--brand-primary, #1e40af);
  background: #eff6ff;
  border: 1px solid #dbeafe;
  border-radius: var(--radius-md, 0.5rem);
  cursor: pointer;
  transition: all 0.15s ease;
}

.view-profile-btn:hover {
  background: #dbeafe;
  color: #1d4ed8;
}

.view-profile-btn svg {
  width: 0.75rem;
  height: 0.75rem;
}
</style>
