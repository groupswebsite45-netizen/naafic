<script setup lang="ts">
import { useRouter } from 'vue-router';
import { Student } from '../../../../types/school';
import { studentService } from '../../../../services/studentService';
import StudentActionMenu from './StudentActionMenu.vue';
import StudentStatusBadge from './StudentStatusBadge.vue';

defineProps<{
  students: Student[];
}>();

const emit = defineEmits<{
  (e: 'edit', student: Student): void;
  (e: 'changeClass', student: Student): void;
  (e: 'managePortal', student: Student): void;
  (e: 'togglePortal', student: Student): void;
  (e: 'loginPortal', student: Student): void;
  (e: 'toggleStatus', student: Student): void;
}>();

const router = useRouter();

function getInitials(name: string): string {
  if (!name) return 'ST';
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
  for (let i = 0; i < (name || '').length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return gradients[Math.abs(hash) % gradients.length];
}

function getStudentPhotoSrc(student: Student): string | null {
  return studentService.getPhotoUrl(student.id, student.photo_path);
}

function navigateToProfile(id: number) {
  router.push(`/admin/students/${id}`);
}
</script>

<template>
  <div class="card-list-stack" aria-label="Student mobile cards roster">
    <article
      v-for="student in students"
      :key="student.id"
      class="student-mobile-card"
      tabindex="0"
      role="button"
      :aria-label="`Student card for ${student.full_name || student.first_name}`"
      @click="navigateToProfile(student.id)"
      @keydown.enter="navigateToProfile(student.id)"
    >
      <!-- Card Top Header: Avatar + Student Name + ID + Action Menu -->
      <div class="card-header-row">
        <div class="card-profile-cell">
          <div
            class="student-avatar"
            :class="{ 'has-photo': !!student.photo_path }"
            :style="!student.photo_path ? { background: getAvatarBg(student.full_name || student.first_name) } : {}"
            aria-hidden="true"
          >
            <img
              v-if="student.photo_path"
              :src="getStudentPhotoSrc(student) || ''"
              :alt="student.full_name || student.first_name"
              class="student-avatar-img"
              @error="student.photo_path = null"
            />
            <span v-else>{{ getInitials(student.full_name || student.first_name) }}</span>
          </div>
          <div class="student-name-block">
            <h4 class="student-name">
              {{ student.full_name || `${student.first_name} ${student.last_name}` }}
            </h4>
            <div class="student-meta-sub">
              <span class="student-id-tag">STU-{{ String(student.id).padStart(4, '0') }}</span>
              <span class="bullet">•</span>
              <span class="gender-tag">{{ student.gender }}</span>
            </div>
          </div>
        </div>

        <div class="card-action-slot" @click.stop>
          <StudentActionMenu
            :student="student"
            @edit="emit('edit', $event)"
            @change-class="emit('changeClass', $event)"
            @manage-portal="emit('managePortal', $event)"
            @toggle-status="emit('toggleStatus', $event)"
          />
        </div>
      </div>

      <!-- Divider -->
      <div class="card-divider" />

      <!-- Card Metadata Grid (Class, Status, Admission, Portal, Guardian) -->
      <div class="card-data-grid">
        <!-- Class -->
        <div class="data-cell">
          <span class="data-label">Class</span>
          <div class="data-content">
            <span v-if="student.current_class" class="class-pill" :title="student.current_class.name">
              {{ student.current_class.name }} {{ student.current_class.section ? `(${student.current_class.section})` : '' }}
            </span>
            <span v-else-if="student.enrollments && student.enrollments.length > 0" class="class-pill" :title="student.enrollments[0].school_class?.name || 'Assigned'">
              {{ student.enrollments[0].school_class?.name || 'Assigned' }}
            </span>
            <span v-else class="text-unassigned">Not enrolled</span>
          </div>
        </div>

        <!-- Status -->
        <div class="data-cell">
          <span class="data-label">Status</span>
          <div class="data-content">
            <StudentStatusBadge :status="student.status" size="sm" />
          </div>
        </div>

        <!-- Admission Number -->
        <div class="data-cell">
          <span class="data-label">Admission #</span>
          <div class="data-content">
            <span class="admission-code">{{ student.admission_number }}</span>
          </div>
        </div>

        <!-- Portal Access -->
        <div class="data-cell">
          <span class="data-label">Portal</span>
          <div class="data-content">
            <button
              type="button"
              class="portal-pill interactive-pill"
              :class="student.has_portal_access ? 'enabled' : 'disabled'"
              :title="student.has_portal_access ? 'Click to Disable Portal' : 'Click to Enable Portal'"
              @click.stop="emit('togglePortal', student)"
            >
              <span class="dot" />
              <span>{{ student.has_portal_access ? 'Enabled' : 'Disabled' }}</span>
            </button>
          </div>
        </div>

        <!-- Guardian (Full Row on Small Cards if present) -->
        <div class="data-cell span-2">
          <span class="data-label">Guardian</span>
          <div class="data-content">
            <div v-if="student.guardian_name" class="guardian-row">
              <span class="guardian-name">{{ student.guardian_name }}</span>
              <span v-if="student.guardian_phone" class="guardian-phone">{{ student.guardian_phone }}</span>
            </div>
            <span v-else class="text-unassigned">—</span>
          </div>
        </div>
      </div>

      <!-- Action Button -->
      <button
        type="button"
        class="btn-card-details"
        :aria-label="`View full profile for ${student.full_name || student.first_name}`"
        @click.stop="navigateToProfile(student.id)"
      >
        <span>View Student Profile</span>
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

.student-mobile-card {
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

.student-mobile-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.student-mobile-card:focus-visible {
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

.student-avatar {
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
  overflow: hidden;
}

.student-avatar.has-photo {
  background: #f1f5f9;
}

.student-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.student-name-block {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1 1 0%;
}

.student-name {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.25;
}

.student-meta-sub {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.15rem;
  font-size: 0.71875rem;
  color: #64748b;
}

.student-id-tag {
  font-weight: 600;
  color: #475569;
}

.bullet {
  color: #cbd5e1;
}

.gender-tag {
  color: #64748b;
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

.class-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  box-sizing: border-box;
}

.admission-code {
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

.portal-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.125rem 0.45rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: nowrap;
}

.portal-pill .dot {
  width: 5px;
  height: 5px;
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

.guardian-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  min-width: 0;
}

.guardian-name {
  font-size: 0.78125rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.guardian-phone {
  font-size: 0.71875rem;
  color: #64748b;
  font-family: monospace;
}

.text-unassigned {
  font-size: 0.75rem;
  color: #94a3b8;
  font-style: italic;
  white-space: nowrap;
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

/* Very narrow mobile (<360px) */
@media (max-width: 359px) {
  .student-mobile-card {
    padding: 0.75rem 0.75rem;
  }
  
  .card-data-grid {
    grid-template-columns: 1fr;
  }

  .data-cell.span-2 {
    grid-column: span 1;
  }
}
</style>
