<script setup lang="ts">
import { useRouter } from 'vue-router';
import { SchoolClass } from '../../../../types/school';
import ClassStatusBadge from './ClassStatusBadge.vue';
import ClassCapacityBar from './ClassCapacityBar.vue';
import ClassActionMenu from './ClassActionMenu.vue';

defineProps<{
  classes: SchoolClass[];
}>();

const emit = defineEmits<{
  (e: 'edit', schoolClass: SchoolClass): void;
  (e: 'manageStudents', schoolClass: SchoolClass): void;
  (e: 'assignTeacher', schoolClass: SchoolClass): void;
  (e: 'promoteClass', schoolClass: SchoolClass): void;
  (e: 'toggleStatus', schoolClass: SchoolClass): void;
}>();

const router = useRouter();

function goToProfile(id: number) {
  router.push(`/admin/classes/${id}`);
}
</script>

<template>
  <div class="table-card">
    <div tabindex="0" role="region" aria-label="Classes directory table" class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-class">Class Name</th>
            <th class="col-capacity">Enrollment & Capacity</th>
            <th class="col-teachers">Teachers</th>
            <th class="col-subjects">Subjects</th>
            <th class="col-year">Academic Year</th>
            <th class="col-status">Status</th>
            <th class="col-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="c in classes"
            :key="c.id"
            class="table-row"
            @click="goToProfile(c.id)"
          >
            <!-- Class Identity -->
            <td class="col-class" @click.stop="goToProfile(c.id)">
              <div class="class-identity">
                <div
                  class="class-avatar"
                  :class="c.division?.toUpperCase() === 'SECONDARY' ? 'avatar-sec' : 'avatar-prim'"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
                    <path d="M6 6h10" />
                    <path d="M6 10h10" />
                  </svg>
                </div>
                <div class="class-details">
                  <span class="class-name">{{ c.name }}</span>
                  <div class="class-meta">
                    <span
                      class="division-badge"
                      :class="c.division?.toUpperCase() === 'SECONDARY' ? 'div-sec' : 'div-prim'"
                    >
                      {{ c.division || 'PRIMARY' }}
                    </span>
                    <span class="code-badge">{{ c.code }}</span>
                    <span v-if="c.section" class="section-tag">Sec {{ c.section }}</span>
                  </div>
                </div>
              </div>
            </td>

            <!-- Capacity & Enrollment -->
            <td class="col-capacity" @click.stop>
              <div class="capacity-cell">
                <ClassCapacityBar
                  :enrolled="c.students_count ?? 0"
                  :capacity="c.capacity"
                />
              </div>
            </td>

            <!-- Teachers -->
            <td class="col-teachers" @click.stop="goToProfile(c.id)">
              <div class="metric-pill teacher-pill">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                </svg>
                <span>{{ c.teachers_count ?? 0 }} {{ (c.teachers_count === 1) ? 'Teacher' : 'Teachers' }}</span>
              </div>
            </td>

            <!-- Subjects -->
            <td class="col-subjects" @click.stop="goToProfile(c.id)">
              <div class="metric-pill subject-pill">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
                <span>{{ c.subjects_count ?? 0 }} {{ (c.subjects_count === 1) ? 'Subject' : 'Subjects' }}</span>
              </div>
            </td>

            <!-- Academic Year -->
            <td class="col-year" @click.stop="goToProfile(c.id)">
              <span class="year-pill">{{ c.academic_year }}</span>
            </td>

            <!-- Status -->
            <td class="col-status" @click.stop>
              <ClassStatusBadge :status="c.status" />
            </td>

            <!-- Actions -->
            <td class="col-actions" @click.stop>
              <ClassActionMenu
                :school-class="c"
                @edit="emit('edit', c)"
                @manage-students="emit('manageStudents', c)"
                @assign-teacher="emit('assignTeacher', c)"
                @promote-class="emit('promoteClass', c)"
                @toggle-status="emit('toggleStatus', c)"
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
  background: transparent;
  border: none;
  box-shadow: none;
  width: 100%;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.data-table thead {
  background-color: #f8fafc;
  border-bottom: 1.5px solid #e2e8f0;
}

.data-table th {
  padding: 1.15rem 1.25rem;
  font-size: 0.74rem;
  font-weight: 800;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.data-table th.col-actions {
  text-align: right;
  padding-right: 1.5rem;
}

.data-table tbody tr {
  border-bottom: 1px solid #f1f5f9;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.data-table tbody tr:last-child {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background-color: #f8fafc;
}

.data-table td {
  padding: 1.1rem 1.25rem;
  vertical-align: middle;
  color: #1e293b;
}

.data-table td.col-actions {
  text-align: right;
  padding-right: 1.25rem;
}

/* Column Widths */
.col-class {
  min-width: 15rem;
}

.col-capacity {
  min-width: 13rem;
  max-width: 16rem;
}

.col-teachers,
.col-subjects {
  min-width: 8.5rem;
  white-space: nowrap;
}

.col-year {
  min-width: 7.5rem;
  white-space: nowrap;
}

.col-status {
  min-width: 7rem;
  white-space: nowrap;
}

.col-actions {
  width: 4rem;
}

/* Identity Cell */
.class-identity {
  display: flex;
  align-items: center;
  gap: 0.95rem;
  min-width: 0;
}

.class-avatar {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #ffffff;
  transition: transform 0.2s ease;
}

.table-row:hover .class-avatar {
  transform: scale(1.05);
}

.avatar-prim {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.avatar-sec {
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.class-avatar svg {
  width: 1.25rem;
  height: 1.25rem;
}

.class-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.class-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.table-row:hover .class-name {
  color: #2563eb;
}

.class-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.division-badge {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}

.div-prim {
  background-color: #e0f2fe;
  color: #0369a1;
  border: 1.5px solid #bae6fd;
}

.div-sec {
  background-color: #ede9fe;
  color: #6d28d9;
  border: 1.5px solid #ddd6fe;
}

.code-badge {
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  background-color: #f8fafc;
  color: #0f172a;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  border: 1.5px solid #cbd5e1;
  letter-spacing: 0.02em;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.section-tag {
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
}

/* Capacity Cell */
.capacity-cell {
  width: 100%;
}

/* Metric Pills */
.metric-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  white-space: nowrap;
}

.teacher-pill {
  background: #f0fdf4;
  border: 1.5px solid #bbf7d0;
  color: #15803d;
}

.teacher-pill svg {
  width: 0.95rem;
  height: 0.95rem;
  color: #16a34a;
  flex-shrink: 0;
}

.subject-pill {
  background: #faf5ff;
  border: 1.5px solid #e9d5ff;
  color: #7e22ce;
}

.subject-pill svg {
  width: 0.95rem;
  height: 0.95rem;
  color: #9333ea;
  flex-shrink: 0;
}

.year-pill {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  display: inline-block;
}
</style>
