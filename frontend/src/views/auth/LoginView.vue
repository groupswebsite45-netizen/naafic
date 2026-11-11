<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { superAdminService } from '../../services/superAdminService';
import LoginBrandPanel from './components/LoginBrandPanel.vue';
import LoginForm from './components/LoginForm.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const generalError = ref<string>('');

onMounted(async () => {
  const queryInstCode = route.query.institution as string;
  if (queryInstCode) {
    if (!authStore.activeInstitution || authStore.activeInstitution.code !== queryInstCode) {
      try {
        const insts = await superAdminService.getInstitutions({ q: queryInstCode });
        const match = insts.find((i) => i.code === queryInstCode);
        if (match) {
          authStore.setActiveInstitution(match);
        } else {
          authStore.setActiveInstitution({
            id: 0,
            code: queryInstCode,
            name: `Institution ${queryInstCode}`,
            type: 'School',
          } as any);
        }
      } catch {
        authStore.setActiveInstitution({
          id: 0,
          code: queryInstCode,
          name: `Institution ${queryInstCode}`,
          type: 'School',
        } as any);
      }
    }
  }
});

async function handleLoginSubmit(credentials: {
  identifier: string;
  password: string;
  remember_me: boolean;
}) {
  generalError.value = '';

  try {
    await authStore.login({
      identifier: credentials.identifier,
      password: credentials.password,
      remember_me: credentials.remember_me,
    });

    const redirectPath = (route.query.redirect as string) || authStore.defaultRoute;
    router.push(redirectPath);
  } catch (err: any) {
    generalError.value = err.message || 'Invalid username or password.';
  }
}
</script>

<template>
  <div class="login-view-container">
    <!-- Left Branding Panel (approx 55% desktop / top hero mobile) -->
    <LoginBrandPanel />

    <!-- Right Login Workspace (approx 45% desktop / bottom area mobile) -->
    <LoginForm
      :is-loading="authStore.isLoading"
      :general-error="generalError"
      :is-expired="!!route.query.expired"
      @submit="handleLoginSubmit"
    />
  </div>
</template>

<style scoped>
.login-view-container {
  height: 100dvh;
  max-height: 100dvh;
  width: 100%;
  max-width: 100%;
  display: flex;
  background-color: #f7f9fc;
  color: var(--text-primary, #0f172a);
  font-family: var(--font-family-base, 'Inter', -apple-system, BlinkMacSystemFont, sans-serif);
  position: relative;
  overflow: clip;
}

@media (max-width: 860px) {
  .login-view-container {
    flex-direction: column;
    height: auto;
    min-height: 100dvh;
    max-height: none;
    overflow-x: clip;
    overflow-y: auto;
  }
}
</style>
