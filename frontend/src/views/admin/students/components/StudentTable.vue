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

function handleRowClick(student: Student, e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (target.closest('.action-menu-container') || target.closest('button')) return;
  router.push(`/admin/students/${student.id}`);
}
</script>

<template>
  <div class="table-responsive-box">
    <table class="premium-student-table" aria-label="Students roster">
      <thead>
        <tr>
          <th scope="col" class="th-student">Student</th>
          <th scope="col" class="th-admission">Admission #</th>
          <th scope="col" class="th-class">Class</th>
          <th scope="col" class="th-guardian hide-tablet">Guardian</th>
          <th scope="col" class="th-portal">Portal</th>
          <th scope="col" class="th-status">Status</th>
          <th scope="col" class="th-actions">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="student in students"
          :key="student.id"
          class="table-row"
          tabindex="0"
          role="button"
          :aria-label="`View details for ${student.full_name || student.first_name}`"
          @click="handleRowClick(student, $event)"
          @keydown.enter="router.push(`/admin/students/${student.id}`)"
        >
          <!-- Student Identity Column -->
          <td class="td-student">
            <div class="student-cell">
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
              <div class="student-text">
                <span class="student-full-name">
                  {{ student.full_name || `${student.first_name} ${student.last_name}` }}
                </span>
                <span class="student-secondary-id">
                  STU-{{ String(student.id).padStart(4, '0') }} • {{ student.gender }}
                </span>
              </div>
            </div>
          </td>

          <!-- Admission # -->
          <td class="td-admission">
            <span class="admission-pill">
              {{ student.admission_number }}
            </span>
          </td>

          <!-- Enrolled Class -->
          <td class="td-class">
            <div v-if="student.current_class" class="class-tag">
              <span class="class-title">{{ student.current_class.name }}</span>
              <span v-if="student.current_class.section" class="class-sec">({{ student.current_class.section }})</span>
            </div>
            <div v-else-if="student.enrollments && student.enrollments.length > 0" class="class-tag">
              <span class="class-title">{{ student.enrollments[0].school_class?.name || 'Assigned' }}</span>
            </div>
            <div v-else class="unassigned-pill">
              <span>Not enrolled</span>
            </div>
          </td>

          <!-- Guardian (Hidden on Compact Tablet) -->
          <td class="td-guardian hide-tablet">
            <div v-if="student.guardian_name" class="guardian-block">
              <span class="guardian-name">{{ student.guardian_name }}</span>
              <span v-if="student.guardian_phone" class="guardian-phone">{{ student.guardian_phone }}</span>
            </div>
            <span v-else class="text-muted">—</span>
          </td>

          <!-- Portal Access -->
          <td class="td-portal">
            <button
              type="button"
              class="portal-status-pill interactive"
              :class="student.has_portal_access ? 'enabled' : 'disabled'"
              :title="student.has_portal_access ? 'Click to Disable Portal Access' : 'Click to Enable Portal Access'"
              @click.stop="emit('togglePortal', student)"
            >
              <span class="dot" />
              <span>{{ student.has_portal_access ? 'Enabled' : 'Disabled' }}</span>
            </button>
          </td>

          <!-- Status -->
          <td class="td-status">
            <StudentStatusBadge :status="student.status" size="md" />
          </td>

          <!-- Actions -->
          <td class="td-actions" @click.stop>
            <StudentActionMenu
              :student="student"
              @edit="emit('edit', $event)"
              @change-class="emit('changeClass', $event)"
              @manage-portal="emit('managePortal', $event)"
              @toggle-portal="emit('togglePortal', $event)"
              @login-portal="emit('loginPortal', $event)"
              @toggle-status="emit('toggleStatus', $event)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-responsive-box {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.premium-student-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.premium-student-table thead th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.74rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 1.15rem 1.25rem;
  border-bottom: 1.5px solid #e2e8f0;
  white-space: nowrap;
}

.premium-student-table thead th.th-actions {
  text-align: right;
  padding-right: 1.5rem;
}

.table-row {
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.table-row:hover {
  background-color: #f8fafc;
}

.table-row:focus-visible {
  outline: 2px solid #2563eb;
  background-color: #eff6ff;
}

.premium-student-table tbody td {
  padding: 1.05rem 1.25rem;
  vertical-align: middle;
  color: #1e293b;
}

.premium-student-table tbody td.td-actions {
  text-align: right;
  padding-right: 1.25rem;
}

/* Student Identity Cell */
.student-cell {
  display: flex;
  align-items: center;
  gap: 0.95rem;
}

.student-avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.35);
  letter-spacing: 0.03em;
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

.student-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.student-full-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.table-row:hover .student-full-name {
  color: #2563eb;
}

.student-secondary-id {
  font-size: 0.76rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 0.2rem;
  font-family: 'JetBrains Mono', monospace;
}

/* Admission Pill */
.admission-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 38px;
  height: 28px;
  padding: 0 0.65rem;
  background: #f8fafc;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

/* Class Tag */
.class-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.85rem;
  background: linear-gradient(135deg, #eff6fe 0%, #dbeafe 100%);
  border: 1.5px solid #bfdbfe;
  border-radius: 9999px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #1d4ed8;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08);
}

.unassigned-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #94a3b8;
  background: #f1f5f9;
  border: 1.5px solid #e2e8f0;
  font-weight: 600;
}

/* Guardian */
.guardian-block {
  display: flex;
  flex-direction: column;
}

.guardian-name {
  font-size: 0.86rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
}

.guardian-phone {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  margin-top: 0.15rem;
  font-family: 'JetBrains Mono', monospace;
}

/* Portal Pill */
.portal-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.28rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}

.portal-status-pill.interactive {
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  outline: none;
}

.portal-status-pill.interactive:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.portal-status-pill.interactive:active {
  transform: translateY(0);
}

.portal-status-pill .dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: currentColor;
}

.portal-status-pill.enabled {
  background: #ecfdf5;
  color: #047857;
  border: 1.5px solid #a7f3d0;
}

.portal-status-pill.enabled .dot {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.portal-status-pill.disabled {
  background: #f8fafc;
  color: #64748b;
  border: 1.5px solid #cbd5e1;
}

.portal-status-pill.disabled .dot {
  background: #94a3b8;
}

.text-muted {
  color: #94a3b8;
}

@media (max-width: 1024px) {
  .hide-tablet {
    display: none;
  }
}
</style>
