import { ref, watch, onUnmounted } from 'vue';

export interface UseFormDraftOptions<T extends Record<string, any>> {
  storageKey: string;
  form: T;
  enabled?: () => boolean;
  isDirty?: (form: T) => boolean;
  onRestore?: (savedData: Partial<T>) => void;
  debounceMs?: number;
}

export function useFormDraft<T extends Record<string, any>>(options: UseFormDraftOptions<T>) {
  const {
    storageKey,
    form,
    enabled = () => true,
    isDirty,
    onRestore,
    debounceMs = 200,
  } = options;

  const hasDraft = ref(false);
  const isRestored = ref(false);
  let debounceTimer: any = null;

  function checkHasDraft(): boolean {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return false;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object';
    } catch {
      return false;
    }
  }

  function getDraft(): Partial<T> | null {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  function defaultIsDirty(f: T): boolean {
    return Object.entries(f).some(([key, val]) => {
      // Ignore keys that are default system values or flags
      if (['status', 'gender', 'create_portal_account', 'division'].includes(key)) {
        return false;
      }
      if (typeof val === 'string' && val.trim() !== '') {
        return true;
      }
      if (typeof val === 'number' && val > 0) {
        return true;
      }
      return false;
    });
  }

  function saveDraft() {
    if (!enabled()) return;
    try {
      const checkDirty = isDirty || defaultIsDirty;
      if (checkDirty(form)) {
        localStorage.setItem(storageKey, JSON.stringify(form));
        hasDraft.value = true;
      }
    } catch (e) {
      console.warn(`[Draft] Failed to save draft for ${storageKey}`, e);
    }
  }

  function restoreDraft(): boolean {
    if (!enabled()) return false;
    const saved = getDraft();
    if (saved && typeof saved === 'object') {
      const checkDirty = isDirty || defaultIsDirty;
      if (checkDirty(saved as T)) {
        if (onRestore) {
          onRestore(saved);
        } else {
          Object.assign(form, saved);
        }
        hasDraft.value = true;
        isRestored.value = true;
        return true;
      }
    }
    return false;
  }

  function clearDraft() {
    try {
      localStorage.removeItem(storageKey);
      hasDraft.value = false;
      isRestored.value = false;
    } catch (e) {
      console.warn(`[Draft] Failed to clear draft for ${storageKey}`, e);
    }
  }

  // Watch form changes with debounce to continuously persist user input
  const stopWatch = watch(
    () => form,
    () => {
      if (!enabled()) return;
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        saveDraft();
      }, debounceMs);
    },
    { deep: true }
  );

  onUnmounted(() => {
    if (debounceTimer) clearTimeout(debounceTimer);
    stopWatch();
  });

  return {
    hasDraft,
    isRestored,
    checkHasDraft,
    saveDraft,
    restoreDraft,
    clearDraft,
  };
}

/**
 * Utility to clear draft from external caller (e.g. parent view after successful save)
 */
export function clearFormDraft(storageKey: string) {
  try {
    localStorage.removeItem(storageKey);
  } catch (e) {
    console.warn(`[Draft] Failed to clear ${storageKey}`, e);
  }
}
