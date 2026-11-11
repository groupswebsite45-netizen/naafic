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
  <div class="table-card">
    <div tabindex="0" role="region" aria-label="Subjects directory table" class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-subject">Subject</th>
            <th class="col-dept">Department</th>
            <th class="col-classes">Classes</th>
            <th class="col-teachers">Teachers</th>
            <th class="col-status">Status</th>
            <th class="col-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="sub in subjects"
            :key="sub.id"
            class="table-row"
            @click="goToProfile(sub.id)"
          >
            <!-- Subject Identity -->
            <td class="col-subject" @click.stop="goToProfile(sub.id)">
              <div class="subject-identity">
                <div class="subject-avatar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                    <path d="M6 6h10" />
                    <path d="M6 10h10" />
                  </svg>
                </div>
                <div class="subject-details">
                  <span class="subject-name">{{ sub.name }}</span>
                  <div class="subject-meta">
                    <span class="code-badge">{{ sub.code }}</span>
                    <span v-if="sub.department" class="dept-sub-tag">{{ sub.department }}</span>
                  </div>
                </div>
              </div>
            </td>

            <!-- Department Column -->
            <td class="col-dept" @click.stop="goToProfile(sub.id)">
              <div class="dept-cell">
                <span v-if="sub.department" class="dept-pill">{{ sub.department }}</span>
                <span v-else class="text-empty">General</span>
              </div>
            </td>

            <!-- Classes Allocation -->
            <td class="col-classes" @click.stop="goToProfile(sub.id)">
              <div v-if="(sub.classes_count ?? 0) > 0" class="metric-pill active">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                </svg>
                <span>{{ sub.classes_count }} {{ sub.classes_count === 1 ? 'Class' : 'Classes' }}</span>
              </div>
              <span v-else class="text-unassigned">No classes assigned</span>
            </td>

            <!-- Teachers Allocation -->
            <td class="col-teachers" @click.stop="goToProfile(sub.id)">
              <div v-if="(sub.teachers_count ?? 0) > 0" class="metric-pill active">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                </svg>
                <span>{{ sub.teachers_count }} {{ sub.teachers_count === 1 ? 'Teacher' : 'Teachers' }}</span>
              </div>
              <span v-else class="text-unassigned">No teachers assigned</span>
            </td>

            <!-- Status -->
            <td class="col-status" @click.stop>
              <SubjectStatusBadge :status="sub.status" size="sm" />
            </td>

            <!-- Actions -->
            <td class="col-actions" @click.stop>
              <SubjectActionMenu
                :subject="sub"
                @edit="emit('edit', sub)"
                @assignClass="emit('assignClass', sub)"
                @assignTeacher="emit('assignTeacher', sub)"
                @toggleStatus="emit('toggleStatus', sub)"
                @delete="emit('delete', sub)"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.table-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: var(--radius-lg, 0.75rem);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.data-table thead tr {
  background: var(--bg-main, #f8fafc);
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.data-table th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #64748b);
  white-space: nowrap;
}

.table-row {
  border-bottom: 1px solid var(--border-color, #f1f5f9);
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: #f8fafc;
}

.data-table td {
  padding: 0.875rem 1rem;
  vertical-align: middle;
  color: var(--text-main, #0f172a);
}

/* Subject Identity */
.subject-identity {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 220px;
}

.subject-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-md, 0.5rem);
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  flex-shrink: 0;
}

.subject-avatar svg {
  width: 1.125rem;
  height: 1.125rem;
}

.subject-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.subject-name {
  font-weight: 600;
  color: var(--text-main, #0f172a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subject-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.code-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.1rem 0.375rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-family: monospace;
  font-weight: 700;
  color: #334155;
  letter-spacing: 0.025em;
}

.dept-sub-tag {
  font-size: 0.6875rem;
  color: #64748b;
  display: none;
}

/* Department Cell */
.dept-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  color: #334155;
}

.text-empty {
  font-size: 0.75rem;
  color: #94a3b8;
  font-style: italic;
}

/* Metric Pills */
.metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
}

.metric-pill.active {
  color: #1e293b;
  font-weight: 600;
}

.metric-pill svg {
  width: 0.875rem;
  height: 0.875rem;
  color: #64748b;
}

.text-unassigned {
  font-size: 0.75rem;
  color: #94a3b8;
}

.col-actions {
  text-align: right;
  width: 60px;
}

@media (max-width: 912px) {
  .dept-sub-tag {
    display: inline;
  }
}
</style>
