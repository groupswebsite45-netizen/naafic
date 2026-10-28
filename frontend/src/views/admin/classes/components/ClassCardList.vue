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
  <div class="cards-stack">
    <div
      v-for="c in classes"
      :key="c.id"
      class="class-card"
      @click="goToProfile(c.id)"
    >
      <!-- Card Header -->
      <div class="card-header">
        <div class="header-left">
          <div
            class="card-avatar"
            :class="c.division?.toUpperCase() === 'SECONDARY' ? 'avatar-sec' : 'avatar-prim'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10" />
              <path d="M6 10h10" />
            </svg>
          </div>
          <div class="class-title-info">
            <h4 class="class-card-name">{{ c.name }}</h4>
            <div class="class-card-meta">
              <span
                class="division-badge"
                :class="c.division?.toUpperCase() === 'SECONDARY' ? 'div-sec' : 'div-prim'"
              >
                {{ c.division || 'PRIMARY' }}
              </span>
              <span class="card-code-badge">{{ c.code }}</span>
              <span v-if="c.section" class="card-section-tag">Sec {{ c.section }}</span>
              <span class="card-year-tag">· {{ c.academic_year }}</span>
            </div>
          </div>
        </div>

        <div class="header-right" @click.stop>
          <ClassActionMenu
            :school-class="c"
            @edit="emit('edit', c)"
            @manage-students="emit('manageStudents', c)"
            @assign-teacher="emit('assignTeacher', c)"
            @promote-class="emit('promoteClass', c)"
            @toggle-status="emit('toggleStatus', c)"
          />
        </div>
      </div>

      <!-- Capacity Bar Section -->
      <div class="card-capacity-section" @click.stop>
        <ClassCapacityBar
          :enrolled="c.students_count ?? 0"
          :capacity="c.capacity"
        />
      </div>

      <!-- Metrics Grid -->
      <div class="card-metrics-grid">
        <div class="metric-item">
          <span class="metric-label">TEACHERS</span>
          <span class="metric-value">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
            </svg>
            {{ c.teachers_count ?? 0 }} Assigned
          </span>
        </div>

        <div class="metric-item">
          <span class="metric-label">SUBJECTS</span>
          <span class="metric-value">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
            {{ c.subjects_count ?? 0 }} Subjects
          </span>
        </div>

        <div class="metric-item">
          <span class="metric-label">SEATS AVAILABLE</span>
          <span class="metric-value">
            {{ c.available_seats ?? Math.max(0, c.capacity - (c.students_count ?? 0)) }} Seats
          </span>
        </div>

        <div class="metric-item">
          <span class="metric-label">STATUS</span>
          <div class="status-wrap" @click.stop>
            <ClassStatusBadge :status="c.status" />
          </div>
        </div>
      </div>

      <!-- Footer CTA Button -->
      <div class="card-footer">
        <button
          type="button"
          class="view-profile-btn"
          @click.stop="goToProfile(c.id)"
        >
          <span>View Class Profile</span>
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
.cards-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.class-card {
  background-color: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.class-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 10px 24px -4px rgba(15, 23, 42, 0.08);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 0;
  flex: 1;
}

.card-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-prim {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28);
}

.avatar-sec {
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.28);
}

.card-avatar svg {
  width: 1.25rem;
  height: 1.25rem;
}

.class-title-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.class-card-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.class-card-meta {
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

.card-code-badge {
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  background-color: #f8fafc;
  color: #0f172a;
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  border: 1.5px solid #cbd5e1;
}

.card-section-tag {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
}

.card-year-tag {
  font-size: 0.75rem;
  color: #94a3b8;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

.card-capacity-section {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
}

.card-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  background-color: #f8fafc;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  min-width: 0;
}

.metric-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
}

.metric-value {
  font-size: 0.82rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.metric-value svg {
  width: 0.875rem;
  height: 0.875rem;
  color: #64748b;
  flex-shrink: 0;
}

.status-wrap {
  display: flex;
  align-items: center;
}

.card-footer {
  padding-top: 0.25rem;
}

.view-profile-btn {
  width: 100%;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background-color: #eff6ff;
  border: 1.5px solid #bfdbfe;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #2563eb;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-profile-btn:hover {
  background-color: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.view-profile-btn svg {
  width: 0.95rem;
  height: 0.95rem;
}
</style>
