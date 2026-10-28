<script setup lang="ts">
interface Props {
  status: string;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
}

withDefaults(defineProps<Props>(), {
  variant: 'neutral',
});
</script>

<template>
  <span :class="['badge', `badge-${variant}`]">
    <span class="badge-dot" aria-hidden="true" />
    <slot>{{ status }}</slot>
  </span>
</template>

<style scoped>
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}
</style>
