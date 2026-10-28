<script setup lang="ts">
interface Props {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  loading?: boolean;
  disabled?: boolean;
  block?: boolean;
}

withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  loading: false,
  disabled: false,
  block: false,
});
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'btn',
      `btn-${variant}`,
      { 'btn-block': block, 'btn-loading': loading }
    ]"
  >
    <svg
      v-if="loading"
      class="spinner"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="spinner-track"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="spinner-head"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    <slot />
  </button>
</template>

<style scoped>
.btn-block {
  width: 100%;
}

.spinner {
  width: 1.15rem;
  height: 1.15rem;
  animation: spin 0.8s linear infinite;
  margin-right: 0.35rem;
}

.spinner-track {
  opacity: 0.25;
}

.spinner-head {
  opacity: 0.85;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
