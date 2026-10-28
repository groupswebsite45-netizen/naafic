<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Teacher } from '../../../../types/school';
import TeacherActionMenu from './TeacherActionMenu.vue';
import TeacherStatusBadge from './TeacherStatusBadge.vue';

defineProps<{
  teachers: Teacher[];
}>();

const emit = defineEmits<{
  (e: 'edit', teacher: Teacher): void;
  (e: 'assign', teacher: Teacher): void;
  (e: 'managePortal', teacher: Teacher): void;
  (e: 'toggleStatus', teacher: Teacher): void;
}>();

const router = useRouter();

function getInitials(name: string): string {
  if (!name) return 'TC';
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

function getAvatarBg(name: string): string {
  const gradients = [
    'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
    'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
    'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
    'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
    'linear-gradient(135deg, #EC4899 0%, #BE185D 100%)',
    'linear-gradient(135deg, #6366F1 0%, #4338CA 100%)',
    'linear-gradient(135deg, #14B8A6 0%, #0D9488 100%)'
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return gradients[Math.abs(hash) % gradients.length];
}

function navigateToProfile(id: number) {
  router.push(`/admin/teachers/${id}`);
}
</script>

<template>
  <div class="card-list-stack" aria-label="Faculty mobile cards roster">
    <article
      v-for="teacher in teachers"
      :key="teacher.id"
      class="teacher-mobile-card"
      tabindex="0"
      role="button"
      :aria-label="`Teacher card for ${teacher.full_name || teacher.first_name}`"
      @click="navigateToProfile(teacher.id)"
      @keydown.enter="navigateToProfile(teacher.id)"
    >
      <!-- Card Top Header -->
      <div class="card-header-row">
        <div class="card-profile-cell">
          <div
            class="teacher-avatar"
            :style="{ background: getAvatarBg(teacher.full_name || teacher.first_name) }"
            aria-hidden="true"
          >
            {{ getInitials(teacher.full_name || teacher.first_name) }}
          </div>
          <div class="teacher-name-block">
            <h4 class="teacher-name">
              {{ teacher.full_name || `${teacher.first_name} ${teacher.last_name}` }}
            </h4>
            <span class="teacher-role-tag">{{ teacher.qualification || 'Faculty Member' }}</span>
          </div>
        </div>

        <div class="card-action-slot" @click.stop>
          <TeacherActionMenu
            :teacher="teacher"
            @edit="emit('edit', $event)"
            @assign="emit('assign', $event)"
            @manage-portal="emit('managePortal', $event)"
            @toggle-status="emit('toggleStatus', $event)"
          />
        </div>
      </div>

      <!-- Divider -->
      <div class="card-divider" />

      <!-- Card Metadata Grid -->
      <div class="card-data-grid">
        <!-- Teacher ID -->
        <div class="data-cell">
          <span class="data-label">Teacher ID</span>
          <div class="data-content">
            <span class="id-badge">
              {{ teacher.teacher_number || teacher.employee_id || `TCH-${teacher.id}` }}
            </span>
          </div>
        </div>

        <!-- Status -->
        <div class="data-cell">
          <span class="data-label">Status</span>
          <div class="data-content">
            <TeacherStatusBadge :status="teacher.status" size="sm" />
          </div>
        </div>

        <!-- Teaching Workload -->
        <div class="data-cell span-2">
          <span class="data-label">Teaching Workload</span>
          <div class="data-content workload-wrap">
            <span class="workload-chip class-chip">
              <strong>{{ teacher.classes_count ?? (teacher.assignments?.length ? new Set(teacher.assignments.map(a => a.class_id)).size : 0) }}</strong> Classes
            </span>
            <span class="workload-chip subject-chip">
              <strong>{{ teacher.subjects_count ?? (teacher.assignments?.length ?? 0) }}</strong> Subjects
            </span>
          </div>
        </div>

        <!-- Contact Email -->
        <div class="data-cell span-2">
          <span class="data-label">Contact</span>
          <div class="data-content contact-line">
            <span class="contact-email">{{ teacher.email || '—' }}</span>
            <span v-if="teacher.phone" class="contact-phone">· {{ teacher.phone }}</span>
          </div>
        </div>

        <!-- Portal Access -->
        <div class="data-cell span-2">
          <span class="data-label">Portal Account</span>
          <div class="data-content">
            <span class="portal-pill" :class="teacher.has_portal_access ? 'enabled' : 'disabled'">
              <span class="dot" />
              <span>{{ teacher.has_portal_access ? 'Active Portal Account' : 'Portal Disabled / Not Created' }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Action CTA Button -->
      <button
        type="button"
        class="btn-card-details"
        :aria-label="`View full profile for ${teacher.full_name || teacher.first_name}`"
        @click.stop="navigateToProfile(teacher.id)"
      >
        <span>View Faculty Profile</span>
        <svg class="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </article>
  </div>
</template>

<style scoped>
.card-list-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.5rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.teacher-mobile-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 0.875rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.teacher-mobile-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.teacher-mobile-card:focus-visible {
  outline: 2px solid #2563eb;
}

.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.625rem;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.card-profile-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  flex: 1 1 0%;
}

.teacher-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.teacher-name-block {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1 1 0%;
}

.teacher-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.25;
}

.teacher-role-tag {
  font-size: 0.71875rem;
  color: #64748b;
  margin-top: 0.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-action-slot {
  flex-shrink: 0;
}

.card-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.625rem 0;
  width: 100%;
}

.card-data-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem 0.75rem;
  width: 100%;
  box-sizing: border-box;
}

.data-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
  overflow: hidden;
}

.data-cell.span-2 {
  grid-column: span 2;
}

.data-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.data-content {
  display: flex;
  align-items: center;
  min-width: 0;
}

.id-badge {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  font-size: 0.71875rem;
  font-family: monospace;
  font-weight: 600;
  color: #334155;
  white-space: nowrap;
}

.workload-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.workload-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.725rem;
  font-weight: 500;
}

.class-chip {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.subject-chip {
  background: #f5f3ff;
  color: #6d28d9;
  border: 1px solid #ddd6fe;
}

.contact-line {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
  font-size: 0.78125rem;
}

.contact-email {
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-phone {
  color: #64748b;
  font-family: monospace;
  font-size: 0.725rem;
}

.portal-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.71875rem;
  font-weight: 600;
  white-space: nowrap;
}

.portal-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: currentColor;
}

.portal-pill.enabled {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.portal-pill.disabled {
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-card-details {
  width: 100%;
  max-width: 100%;
  margin-top: 0.625rem;
  height: 38px;
  min-height: 38px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.78125rem;
  font-weight: 600;
  color: #2563eb;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  box-sizing: border-box;
}

.btn-card-details:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}

.arrow-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

@media (max-width: 359px) {
  .card-data-grid {
    grid-template-columns: 1fr;
  }
}
</style>
