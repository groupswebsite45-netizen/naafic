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

function handleRowClick(teacher: Teacher, e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (target.closest('.action-menu-container') || target.closest('button')) return;
  router.push(`/admin/teachers/${teacher.id}`);
}
</script>

<template>
  <div class="table-responsive-box">
    <table class="premium-teacher-table" aria-label="Faculty member directory">
      <thead>
        <tr>
          <th scope="col" class="th-teacher">Faculty Member</th>
          <th scope="col" class="th-id">Teacher ID</th>
          <th scope="col" class="th-contact hide-tablet">Contact</th>
          <th scope="col" class="th-workload">Teaching Workload</th>
          <th scope="col" class="th-portal">Portal</th>
          <th scope="col" class="th-status">Status</th>
          <th scope="col" class="th-actions">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="teacher in teachers"
          :key="teacher.id"
          class="table-row"
          tabindex="0"
          role="button"
          :aria-label="`View details for ${teacher.full_name || teacher.first_name}`"
          @click="handleRowClick(teacher, $event)"
          @keydown.enter="router.push(`/admin/teachers/${teacher.id}`)"
        >
          <!-- Faculty Column -->
          <td class="td-teacher">
            <div class="teacher-cell">
              <div
                class="teacher-avatar"
                :style="{ background: getAvatarBg(teacher.full_name || teacher.first_name) }"
                aria-hidden="true"
              >
                {{ getInitials(teacher.full_name || teacher.first_name) }}
              </div>
              <div class="teacher-text">
                <span class="teacher-full-name">
                  {{ teacher.full_name || `${teacher.first_name} ${teacher.last_name}` }}
                </span>
                <span class="teacher-qualification">
                  {{ teacher.qualification || teacher.gender || 'Faculty Member' }}
                </span>
              </div>
            </div>
          </td>

          <!-- Teacher ID -->
          <td class="td-id">
            <span class="id-pill">
              {{ teacher.teacher_number || teacher.employee_id || `TCH-${teacher.id}` }}
            </span>
          </td>

          <!-- Contact (Hidden on compact tablet) -->
          <td class="td-contact hide-tablet">
            <div class="contact-block">
              <span class="contact-email">{{ teacher.email || '—' }}</span>
              <span v-if="teacher.phone" class="contact-phone">{{ teacher.phone }}</span>
            </div>
          </td>

          <!-- Workload -->
          <td class="td-workload">
            <div class="workload-tags">
              <span class="workload-pill class-pill">
                <svg class="pill-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <span>{{ teacher.classes_count ?? (teacher.assignments?.length ? new Set(teacher.assignments.map(a => a.class_id)).size : 0) }} Classes</span>
              </span>
              <span class="workload-pill subject-pill">
                <svg class="pill-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span>{{ teacher.subjects_count ?? (teacher.assignments?.length ?? 0) }} Subjects</span>
              </span>
            </div>
          </td>

          <!-- Portal Access -->
          <td class="td-portal">
            <span
              class="portal-status-pill"
              :class="teacher.has_portal_access ? 'enabled' : 'disabled'"
            >
              <span class="dot" />
              <span>{{ teacher.has_portal_access ? 'Enabled' : 'Disabled' }}</span>
            </span>
          </td>

          <!-- Status -->
          <td class="td-status">
            <TeacherStatusBadge :status="teacher.status" size="md" />
          </td>

          <!-- Actions -->
          <td class="td-actions" @click.stop>
            <TeacherActionMenu
              :teacher="teacher"
              @edit="emit('edit', $event)"
              @assign="emit('assign', $event)"
              @manage-portal="emit('managePortal', $event)"
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

.premium-teacher-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.premium-teacher-table thead th {
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

.premium-teacher-table thead th.th-actions {
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

.premium-teacher-table tbody td {
  padding: 1.05rem 1.25rem;
  vertical-align: middle;
  color: #1e293b;
}

.premium-teacher-table tbody td.td-actions {
  text-align: right;
  padding-right: 1.25rem;
}

.teacher-cell {
  display: flex;
  align-items: center;
  gap: 0.95rem;
}

.teacher-avatar {
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
}

.teacher-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.teacher-full-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.table-row:hover .teacher-full-name {
  color: #2563eb;
}

.teacher-qualification {
  font-size: 0.76rem;
  color: #64748b;
  margin-top: 0.2rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.id-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.65rem;
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

.contact-block {
  display: flex;
  flex-direction: column;
}

.contact-email {
  font-size: 0.86rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
}

.contact-phone {
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500;
  margin-top: 0.15rem;
}

.workload-tags {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.workload-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.32rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}

.pill-icon {
  width: 14px;
  height: 14px;
}

.class-pill {
  background: linear-gradient(135deg, #eff6fe 0%, #dbeafe 100%);
  color: #1d4ed8;
  border: 1.5px solid #bfdbfe;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08);
}

.subject-pill {
  background: linear-gradient(135deg, #f7f3fe 0%, #e9e0fd 100%);
  color: #6d28d9;
  border: 1.5px solid #ddd6fe;
  box-shadow: 0 1px 3px rgba(139, 92, 246, 0.08);
}

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

@media (max-width: 1024px) {
  .hide-tablet {
    display: none;
  }
}
</style>
