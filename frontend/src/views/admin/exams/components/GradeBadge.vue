<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  grade?: string | null;
}>();

const normalized = computed(() => {
  return (props.grade || '').trim().toUpperCase();
});

const gradeClass = computed(() => {
  switch (normalized.value) {
    case 'A+': return 'grade-a-plus';
    case 'A': return 'grade-a';
    case 'B': return 'grade-b';
    case 'C': return 'grade-c';
    case 'D': return 'grade-d';
    case 'F': return 'grade-f';
    default: return 'grade-na';
  }
});
</script>

<template>
  <span class="grade-badge" :class="gradeClass">
    {{ normalized || '—' }}
  </span>
</template>

<style scoped>
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  padding: 0 0.4rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 700;
  text-align: center;
}

.grade-a-plus {
  background: linear-gradient(135deg, #10b981 0%, #047857 100%);
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25);
}

.grade-a {
  background-color: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.grade-b {
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.grade-c {
  background-color: #fefce8;
  color: #a16207;
  border: 1px solid #fef08a;
}

.grade-d {
  background-color: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

.grade-f {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.grade-na {
  background-color: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
</style>
