<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Teacher, SchoolClass, Subject } from '../../../../types/school';

const props = defineProps<{
  isOpen: boolean;
  teacher: Teacher | null;
  availableClasses: SchoolClass[];
  availableSubjects: Subject[];
  isSubmitting: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'assign', payload: { class_id: number; subject_id: number; academic_year: string; section?: string }): void;
  (e: 'removeAssignment', assignmentId: number): void;
}>();

const form = reactive({
  class_id: 0,
  subject_id: 0,
  academic_year: '2025-2026',
  section: '',
});

const formError = ref('');

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      form.class_id = props.availableClasses.length > 0 ? props.availableClasses[0].id : 0;
      form.subject_id = props.availableSubjects.length > 0 ? props.availableSubjects[0].id : 0;
      form.academic_year = '2025-2026';
      form.section = '';
      formError.value = '';
    }
  },
  { immediate: true }
);

function handleAddAssignment() {
  formError.value = '';
  if (!form.class_id) {
    formError.value = 'Please select a valid school class.';
    return;
  }
  if (!form.subject_id) {
    formError.value = 'Please select a valid subject.';
    return;
  }

  // Check duplicate in existing assignments
  if (props.teacher?.assignments) {
    const isDup = props.teacher.assignments.some(
      (a) => a.class_id === Number(form.class_id) && a.subject_id === Number(form.subject_id) && a.academic_year === form.academic_year
    );
    if (isDup) {
      formError.value = 'This teacher is already assigned to this subject and class for this academic year.';
      return;
    }
  }

  emit('assign', {
    class_id: Number(form.class_id),
    subject_id: Number(form.subject_id),
    academic_year: form.academic_year.trim(),
    section: form.section.trim() || undefined,
  });
}
</script>

<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
      <div class="modal-dialog" @click.stop>
        <!-- Header -->
        <div class="modal-header">
          <div class="modal-title-box">
            <svg class="modal-title-icon text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <div>
              <h3 class="modal-title">Manage Teaching Assignments</h3>
              <p class="modal-subtitle">
                Allocate classes and subjects for <strong>{{ teacher?.full_name || teacher?.first_name }}</strong> ({{ teacher?.teacher_number || teacher?.employee_id }}).
              </p>
            </div>
          </div>
          <button type="button" class="btn-close" @click="emit('close')">&times;</button>
        </div>

        <!-- Body -->
        <div class="modal-body">
          <!-- Error alert -->
          <div v-if="formError" class="alert-box-error">
            <span>{{ formError }}</span>
          </div>

          <!-- Add Assignment Sub-form -->
          <div class="assignment-form-card">
            <h4 class="form-section-title">+ Add New Teaching Allocation</h4>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">School Class <span class="required">*</span></label>
                <select v-model="form.class_id" class="form-select">
                  <option v-for="c in availableClasses" :key="c.id" :value="c.id">
                    {{ c.name }} ({{ c.code }})
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Subject <span class="required">*</span></label>
                <select v-model="form.subject_id" class="form-select">
                  <option v-for="s in availableSubjects" :key="s.id" :value="s.id">
                    {{ s.name }} ({{ s.code }})
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Academic Year</label>
                <select v-model="form.academic_year" class="form-select">
                  <option value="2025-2026">2025-2026 (Current)</option>
                  <option value="2024-2025">2024-2025</option>
                </select>
              </div>

              <div class="form-group btn-align-bottom">
                <button
                  type="button"
                  class="btn-add-assignment"
                  :disabled="isSubmitting"
                  @click="handleAddAssignment"
                >
                  <span v-if="isSubmitting">Allocating...</span>
                  <span v-else>Assign Workload</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Existing Assignments List -->
          <div class="existing-assignments-section mt-4">
            <h4 class="section-title">Current Active Allocations ({{ teacher?.assignments?.length || 0 }})</h4>

            <div v-if="!teacher?.assignments || teacher.assignments.length === 0" class="empty-allocations">
              <p>No active class or subject assignments allocated yet for this teacher.</p>
            </div>

            <div v-else class="allocations-list">
              <div
                v-for="a in teacher.assignments"
                :key="a.id"
                class="allocation-item"
              >
                <div class="allocation-info">
                  <div class="alloc-title-row">
                    <span class="alloc-subject font-bold text-slate-900">
                      {{ a.subject?.name || a.subject_name || `Subject #${a.subject_id}` }}
                    </span>
                    <span class="alloc-class-pill">
                      {{ a.school_class?.name || a.class_name || `Class #${a.class_id}` }}
                    </span>
                  </div>
                  <span class="alloc-meta">
                    Academic Year: {{ a.academic_year }} &bull; Code: {{ a.subject?.code || a.subject_code || '—' }}
                  </span>
                </div>

                <button
                  type="button"
                  class="btn-remove-alloc"
                  title="Remove assignment"
                  @click="emit('removeAssignment', a.id)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Remove</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="emit('close')">
            Close
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  box-sizing: border-box;
}

.modal-dialog {
  width: 100%;
  max-width: min(640px, calc(100vw - 20px));
  max-height: calc(100vh - 24px);
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.modal-title-box {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  min-width: 0;
}

.modal-title-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  margin-top: 2px;
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.15rem 0 0;
  line-height: 1.35;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.12s ease;
  flex-shrink: 0;
}

.btn-close:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  flex: 1 1 0%;
  box-sizing: border-box;
}

.alert-box-error {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 0.55rem 0.75rem;
  border-radius: 6px;
  font-size: 0.78125rem;
  margin-bottom: 0.875rem;
}

.assignment-form-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.875rem;
}

.form-section-title {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.65rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.btn-align-bottom {
  display: flex;
  align-items: flex-end;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
}

.required {
  color: #e11d48;
}

.form-select {
  height: 38px;
  padding: 0 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  font-size: 0.8125rem;
  color: #0f172a;
  outline: none;
  box-sizing: border-box;
  width: 100%;
}

.btn-add-assignment {
  width: 100%;
  height: 38px;
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.12s ease;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-add-assignment:hover {
  background: #1d4ed8;
}

.section-title {
  font-size: 0.84375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem;
}

.empty-allocations {
  padding: 1.25rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.78125rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
}

.allocations-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.allocation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.875rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
  gap: 0.5rem;
}

.alloc-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.alloc-class-pill {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
}

.alloc-meta {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.1rem;
  display: block;
}

.btn-remove-alloc {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #e11d48;
  padding: 0.35rem 0.65rem;
  min-height: 32px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s ease;
  flex-shrink: 0;
}

.btn-remove-alloc:hover {
  background: #ffe4e6;
}

.modal-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  position: sticky;
  bottom: 0;
  z-index: 10;
  flex-shrink: 0;
}

.btn-cancel {
  height: 40px;
  padding: 0 1.25rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.btn-cancel:hover {
  background: #f1f5f9;
  color: #0f172a;
}

@media (max-width: 580px) {
  .modal-backdrop {
    padding: 8px;
  }

  .modal-dialog {
    max-width: calc(100vw - 16px);
    max-height: calc(100vh - 16px);
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .btn-cancel {
    width: 100%;
    height: 44px;
  }
}
</style>
