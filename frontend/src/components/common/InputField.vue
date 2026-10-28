<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  id: string;
  modelValue?: string | number | null;
  label: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'date' | 'time';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string | null;
  hint?: string;
  autocomplete?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  required: false,
  disabled: false,
  error: null,
  hint: '',
  autocomplete: 'off',
});

const emit = defineEmits<{
  (e: 'update:modelValue', val: any): void;
}>();

const showPassword = ref(false);

const computedType = computed(() => {
  if (props.type === 'password') {
    return showPassword.value ? 'text' : 'password';
  }
  return props.type;
});

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement;
  if (props.type === 'number') {
    emit('update:modelValue', target.value === '' ? '' : Number(target.value));
  } else {
    emit('update:modelValue', target.value);
  }
}
</script>

<template>
  <div class="form-group" :class="{ 'has-error': !!error }">
    <div class="label-row">
      <label :for="id" class="form-label">
        {{ label }}
        <span v-if="required" class="required-mark" aria-hidden="true">*</span>
      </label>
      <slot name="label-right" />
    </div>

    <div class="input-wrapper">
      <slot name="prefix-icon" />
      <input
        :id="id"
        :type="computedType"
        :value="modelValue ?? ''"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : (hint ? `${id}-hint` : undefined)"
        class="form-control"
        @input="handleInput"
      />
      
      <!-- Password toggle button -->
      <button
        v-if="type === 'password'"
        type="button"
        class="toggle-pwd-btn"
        :aria-label="showPassword ? 'Hide password' : 'Show password'"
        tabindex="-1"
        @click="showPassword = !showPassword"
      >
        <svg v-if="!showPassword" class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <svg v-else class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
        </svg>
      </button>
    </div>

    <!-- Error message display -->
    <p v-if="error" :id="`${id}-error`" class="error-msg" role="alert">
      {{ error }}
    </p>
    <!-- Hint text -->
    <p v-else-if="hint" :id="`${id}-hint`" class="hint-msg">
      {{ hint }}
    </p>
  </div>
</template>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.2rem;
  width: 100%;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

.required-mark {
  color: var(--danger);
  margin-left: 0.2rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-control {
  width: 100%;
  padding: 0.75rem 0.95rem;
  font-size: 0.925rem;
  color: var(--text-primary);
  background-color: var(--bg-surface);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-control:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-control:disabled {
  background-color: var(--bg-surface-secondary);
  cursor: not-allowed;
  opacity: 0.75;
}

.has-error .form-control {
  border-color: var(--danger);
}

.has-error .form-control:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
}

.toggle-pwd-btn {
  position: absolute;
  right: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  padding: 0.25rem;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}

.toggle-pwd-btn:hover {
  color: var(--text-primary);
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
}

.error-msg {
  font-size: 0.8rem;
  color: var(--danger);
  margin-top: 0.35rem;
}

.hint-msg {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 0.35rem;
}
</style>
