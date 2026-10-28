<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { TimetableEntry } from '../../../../types/school';

const props = defineProps<{
  entry: TimetableEntry;
  compact?: boolean;
}>();

const emit = defineEmits<{
  (e: 'edit', entry: TimetableEntry): void;
  (e: 'delete', entry: TimetableEntry): void;
}>();

const isMenuOpen = ref(false);
const menuRef = ref<HTMLElement | null>(null);

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value;
}

function closeMenu() {
  isMenuOpen.value = false;
}

function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    closeMenu();
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

function handleEdit() {
  closeMenu();
  emit('edit', props.entry);
}

function handleDelete() {
  closeMenu();
  emit('delete', props.entry);
}
</script>

<template>
  <!-- Break / Recess Period Card -->
  <div v-if="entry.is_break" class="schedule-card break-card" :class="{ 'compact-mode': compact }">
    <div class="break-content">
      <div class="break-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
          <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
          <line x1="6" y1="1" x2="6" y2="4" />
          <line x1="10" y1="1" x2="10" y2="4" />
          <line x1="14" y1="1" x2="14" y2="4" />
        </svg>
      </div>
      <div class="break-details">
        <span class="break-title">{{ entry.subject?.name || entry.subject_name || 'Recess / Break' }}</span>
        <span class="break-time">{{ entry.start_time.slice(0, 5) }} – {{ entry.end_time.slice(0, 5) }}</span>
      </div>
    </div>
    <!-- Action Menu for Break -->
    <div ref="menuRef" class="action-wrap" @click.stop>
      <button
        type="button"
        class="card-action-trigger"
        title="Slot actions"
        @click="toggleMenu"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="1" />
          <circle cx="12" cy="5" r="1" />
          <circle cx="12" cy="19" r="1" />
        </svg>
      </button>

      <div v-if="isMenuOpen" class="card-dropdown-menu">
        <button type="button" class="dropdown-item" @click="handleEdit">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
            <path d="m15 5 4 4" />
          </svg>
          <span>Edit Break</span>
        </button>
        <button type="button" class="dropdown-item danger" @click="handleDelete">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18" />
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
          </svg>
          <span>Delete</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Regular Teaching Lesson Card -->
  <div v-else class="schedule-card" :class="{ 'compact-mode': compact, 'is-published': entry.status === 'PUBLISHED' }">
    <!-- Card Header -->
    <div class="card-header-row">
      <div class="subject-info">
        <span v-if="entry.period_number" class="period-pill">
          P{{ entry.period_number }}
        </span>
        <span class="subject-name">
          {{ entry.subject?.name || entry.subject_name || 'Subject' }}
        </span>
        <span v-if="entry.subject?.code || entry.subject_code" class="subject-code-tag">
          {{ entry.subject?.code || entry.subject_code }}
        </span>
      </div>

      <!-- Action Menu -->
      <div ref="menuRef" class="action-wrap" @click.stop>
        <button
          type="button"
          class="card-action-trigger"
          title="Slot actions"
          @click="toggleMenu"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="1" />
            <circle cx="12" cy="5" r="1" />
            <circle cx="12" cy="19" r="1" />
          </svg>
        </button>

        <div v-if="isMenuOpen" class="card-dropdown-menu">
          <button type="button" class="dropdown-item" @click="handleEdit">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
              <path d="m15 5 4 4" />
            </svg>
            <span>Edit Slot</span>
          </button>
          <button type="button" class="dropdown-item danger" @click="handleDelete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18" />
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
            </svg>
            <span>Delete Slot</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Class & Teacher Details -->
    <div class="card-details-group">
      <!-- Class -->
      <div class="meta-row class-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
        </svg>
        <span class="meta-text class-name">
          {{ entry.school_class?.name || entry.class_name || `Class ${entry.class_id}` }}
        </span>
      </div>

      <!-- Teacher -->
      <div class="meta-row teacher-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
        </svg>
        <span class="meta-text teacher-name">
          {{
            entry.teacher?.full_name ||
            (entry.teacher ? `${entry.teacher.first_name} ${entry.teacher.last_name}` : entry.teacher_name || 'Unassigned')
          }}
        </span>
      </div>
    </div>

    <!-- Footer: Time & Room & Status -->
    <div class="card-footer-row">
      <div class="time-badge">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        <span>{{ entry.start_time.slice(0, 5) }} – {{ entry.end_time.slice(0, 5) }}</span>
      </div>

      <div class="footer-badges">
        <div v-if="entry.room || entry.room_number" class="room-pill">
          {{ entry.room || entry.room_number }}
        </div>
        <span
          class="status-dot-badge"
          :class="entry.status === 'PUBLISHED' ? 'status-published' : 'status-draft'"
          :title="entry.status === 'PUBLISHED' ? 'Published to Portals' : 'Draft'"
        >
          {{ entry.status === 'PUBLISHED' ? 'Live' : 'Draft' }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-left: 3px solid var(--brand-primary, #1e40af);
  border-radius: var(--radius-md, 0.5rem);
  padding: 0.625rem 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  transition: all 0.15s ease;
  position: relative;
  box-sizing: border-box;
}

.schedule-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
  border-color: #94a3b8;
  border-left-color: var(--brand-primary, #1e40af);
  transform: translateY(-1px);
}

.schedule-card.compact-mode {
  padding: 0.5rem 0.625rem;
  gap: 0.25rem;
}

.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.375rem;
}

.subject-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
  min-width: 0;
}

.subject-name {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  line-height: 1.25;
  white-space: normal;
  word-break: break-word;
}

.subject-code-tag {
  font-size: 0.625rem;
  font-family: monospace;
  font-weight: 700;
  padding: 0.05rem 0.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  color: #475569;
}

.action-wrap {
  position: relative;
  flex-shrink: 0;
}

.card-action-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.375rem;
  height: 1.375rem;
  border-radius: 0.25rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.12s ease;
}

.card-action-trigger:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.card-action-trigger svg {
  width: 0.875rem;
  height: 0.875rem;
}

.card-dropdown-menu {
  position: absolute;
  top: calc(100% + 2px);
  right: 0;
  width: 130px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md, 0.5rem);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  padding: 0.25rem;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  animation: fadeIn 0.12s ease-out;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  width: 100%;
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #334155;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.12s ease;
  box-sizing: border-box;
}

.dropdown-item svg {
  width: 0.75rem;
  height: 0.75rem;
  flex-shrink: 0;
}

.dropdown-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.dropdown-item.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

.card-details-group {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #475569;
}

.meta-row svg {
  width: 0.6875rem;
  height: 0.6875rem;
  color: #64748b;
  flex-shrink: 0;
}

.meta-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.class-name {
  font-weight: 600;
  color: #1e293b;
}

.teacher-name {
  color: #475569;
}

.card-footer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.375rem;
  margin-top: 0.125rem;
  padding-top: 0.25rem;
  border-top: 1px dashed #f1f5f9;
}

.time-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #475569;
}

.time-badge svg {
  width: 0.625rem;
  height: 0.625rem;
  color: #64748b;
}

.room-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.05rem 0.35rem;
  background: #f1f5f9;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
  color: #334155;
}

.break-card {
  background: #f8fafc;
  border-left: 3px solid #f59e0b;
  border-style: dashed;
}

.break-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.break-icon-wrap {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 0.25rem;
  background: #fef3c7;
  color: #d97706;
  display: flex;
  align-items: center;
  justify-content: center;
}

.break-icon-wrap svg {
  width: 0.875rem;
  height: 0.875rem;
}

.break-details {
  display: flex;
  flex-direction: column;
}

.break-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #78350f;
}

.break-time {
  font-size: 0.6875rem;
  color: #92400e;
}

.period-pill {
  font-size: 0.625rem;
  font-weight: 800;
  background: #eff6ff;
  color: var(--brand-primary, #1e40af);
  border: 1px solid #bfdbfe;
  padding: 0.05rem 0.25rem;
  border-radius: 0.25rem;
}

.footer-badges {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-dot-badge {
  font-size: 0.5625rem;
  font-weight: 700;
  padding: 0.05rem 0.3rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-published {
  background: #dcfce7;
  color: #15803d;
}

.status-draft {
  background: #f1f5f9;
  color: #64748b;
}

.schedule-card.is-published {
  border-left-color: #10b981;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-3px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
