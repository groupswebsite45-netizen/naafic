<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../../stores/auth';
import { SCHOOL_BRANDING } from '../../../constants/branding';

const router = useRouter();
const authStore = useAuthStore();

const activeInstitution = computed(() => authStore.activeInstitution);

function handleClearInstitution() {
  authStore.clearActiveInstitution();
  router.replace({ path: '/login' });
}

interface Props {
  isLoading: boolean;
  generalError?: string;
  isExpired?: boolean;
}

withDefaults(defineProps<Props>(), {
  isLoading: false,
  generalError: '',
  isExpired: false,
});

const emit = defineEmits<{
  (e: 'submit', payload: { identifier: string; password: string; remember_me: boolean }): void;
}>();

const formData = reactive({
  identifier: '',
  password: '',
  remember_me: false,
});

const errors = reactive({
  identifier: '',
  password: '',
});

const showPassword = ref(false);
const isForgotModalOpen = ref(false);

function validateForm(): boolean {
  let valid = true;
  errors.identifier = '';
  errors.password = '';

  if (!formData.identifier.trim()) {
    errors.identifier = 'Please enter your email or username.';
    valid = false;
  }

  if (!formData.password) {
    errors.password = 'Please enter your password.';
    valid = false;
  }

  return valid;
}

function handleFormSubmit() {
  if (!validateForm()) return;
  emit('submit', {
    identifier: formData.identifier.trim(),
    password: formData.password,
    remember_me: formData.remember_me,
  });
}
</script>

<template>
  <main class="login-workspace">
    <div class="login-card-wrapper">
      
      <!-- Card Container -->
      <div class="login-card">
        
        <!-- Header -->
        <div class="card-header">
          <div class="card-brand-header">
            <img
              src="/somroyal-logo-transparent.png"
              alt="Somroyal Educational Management System"
              class="card-brand-logo"
            />
          </div>
          <div class="header-badge-row">
            <span class="welcome-badge">WELCOME BACK</span>
            <span class="badge-dot" aria-hidden="true"></span>
            <span class="system-badge">PORTAL ACCESS</span>
          </div>
          <h2 class="card-main-heading">Sign in to your account</h2>
          <p class="card-sub-heading">Access your authorized school portal securely.</p>
        </div>

        <!-- Multi-Tenant Institution Context Banner -->
        <div v-if="activeInstitution" class="inst-portal-banner">
          <div class="inst-portal-header">
            <div class="inst-portal-icon">
              <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="inst-portal-info">
              <div class="inst-portal-name">{{ activeInstitution.name }}</div>
              <div class="inst-portal-code">Tenant Workspace: {{ activeInstitution.code }}</div>
            </div>
            <button
              type="button"
              @click="handleClearInstitution"
              class="inst-portal-clear-btn"
              title="Switch to default / clear institution"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Session Expired Alert -->
        <div v-if="isExpired" class="feedback-banner info-banner" role="status">
          <svg class="feedback-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <div class="feedback-text">Your session has expired. Please sign in again.</div>
        </div>

        <!-- General Error Alert -->
        <div v-if="generalError" class="feedback-banner error-banner" role="alert">
          <svg class="feedback-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <div class="feedback-text">{{ generalError }}</div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleFormSubmit" novalidate class="auth-form">
          
          <!-- Email / Username Field -->
          <div class="form-item" :class="{ 'has-error': !!errors.identifier }">
            <label for="login-identifier" class="field-label">
              Email or Username
              <span class="required-star" aria-hidden="true">*</span>
            </label>
            <div class="input-control-box">
              <span class="leading-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </span>
              <input
                id="login-identifier"
                v-model="formData.identifier"
                type="text"
                placeholder="Enter your email or username"
                class="modern-input"
                :disabled="isLoading"
                :aria-invalid="!!errors.identifier"
                :aria-describedby="errors.identifier ? 'identifier-error' : undefined"
                autocomplete="username"
              />
            </div>
            <p v-if="errors.identifier" id="identifier-error" class="validation-msg" role="alert">
              {{ errors.identifier }}
            </p>
          </div>

          <!-- Password Field -->
          <div class="form-item" :class="{ 'has-error': !!errors.password }">
            <div class="label-actions-row">
              <label for="login-password" class="field-label">
                Password
                <span class="required-star" aria-hidden="true">*</span>
              </label>
              <button
                type="button"
                class="forgot-password-link"
                @click="isForgotModalOpen = true"
              >
                Forgot Password?
              </button>
            </div>
            <div class="input-control-box">
              <span class="leading-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </span>
              <input
                id="login-password"
                v-model="formData.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter your password"
                class="modern-input has-trailing"
                :disabled="isLoading"
                :aria-invalid="!!errors.password"
                :aria-describedby="errors.password ? 'password-error' : undefined"
                autocomplete="current-password"
              />
              <!-- Password Toggle Button -->
              <button
                type="button"
                class="trailing-action-btn"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                tabindex="0"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <p v-if="errors.password" id="password-error" class="validation-msg" role="alert">
              {{ errors.password }}
            </p>
          </div>

          <!-- Remember Me Checkbox -->
          <div class="checkbox-row">
            <label class="custom-checkbox" for="remember-me">
              <input
                id="remember-me"
                v-model="formData.remember_me"
                type="checkbox"
                class="native-checkbox"
                :disabled="isLoading"
              />
              <span class="custom-box" aria-hidden="true">
                <svg class="check-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </span>
              <span class="checkbox-text">Keep me signed in</span>
            </label>
          </div>

          <!-- Primary Submit CTA Button -->
          <button
            type="submit"
            class="submit-cta-btn"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="btn-spinner" aria-hidden="true"></span>
            <span class="btn-text">{{ isLoading ? 'Signing In...' : 'Sign In to Dashboard' }}</span>
            <svg v-if="!isLoading" class="btn-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </form>

        <!-- Security Footer -->
        <div class="security-footer">
          <div class="security-meta">
            <svg class="shield-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              <polyline points="9 12 11 14 15 10"></polyline>
            </svg>
            <span class="security-text">Secure access &bull; Authorized users only</span>
          </div>
          <span class="security-school">{{ SCHOOL_BRANDING.institutionName }}</span>
        </div>

      </div>
    </div>

    <!-- Forgot Password Modal -->
    <div
      v-if="isForgotModalOpen"
      class="modal-backdrop"
      role="dialog"
      aria-labelledby="forgot-title"
      aria-modal="true"
      @click.self="isForgotModalOpen = false"
    >
      <div class="modal-box">
        <div class="modal-header">
          <div class="modal-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
          </div>
          <div>
            <h3 id="forgot-title" class="modal-title">Password Reset Assistance</h3>
            <span class="modal-sub">Institutional Security Protocol</span>
          </div>
          <button
            type="button"
            class="modal-close"
            aria-label="Close dialog"
            @click="isForgotModalOpen = false"
          >
            &times;
          </button>
        </div>

        <div class="modal-body">
          <p class="modal-desc">
            To ensure institutional security compliance, password resets and account credentials are managed directly by the Education Management System Administrator and IT Helpdesk.
          </p>
          <div class="support-entries">
            <div class="support-item">
              <span class="support-label">Official IT Support:</span>
              <span class="support-val">{{ activeInstitution?.email || SCHOOL_BRANDING.contactEmail }}</span>
            </div>
            <div class="support-item">
              <span class="support-label">Campus Administration:</span>
              <span class="support-val">{{ activeInstitution?.phone || SCHOOL_BRANDING.contactPhone }}</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="modal-btn"
            @click="isForgotModalOpen = false"
          >
            Understood
          </button>
        </div>
      </div>
    </div>

  </main>
</template>

<style scoped>
.login-workspace {
  flex: 1;
  height: 100vh;
  max-height: 100vh;
  background-color: #f7f9fc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem 2.5rem;
  position: relative;
  z-index: 2;
  overflow-y: auto;
  scrollbar-width: none;
}

.login-workspace::-webkit-scrollbar {
  display: none;
}

.login-card-wrapper {
  position: relative;
  width: 100%;
  max-width: 460px;
  animation: cardSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Ambient glowing aura behind the card wrapper */
.login-card-wrapper::before {
  content: '';
  position: absolute;
  inset: -14px;
  border-radius: 34px;
  background: radial-gradient(circle at 50% 12%, rgba(255, 105, 0, 0.32) 0%, rgba(255, 105, 0, 0.14) 45%, rgba(11, 31, 75, 0.08) 70%, transparent 85%);
  filter: blur(20px);
  z-index: 0;
  pointer-events: none;
  animation: ambientAura 4.5s ease-in-out infinite alternate;
}

@keyframes ambientAura {
  0% {
    opacity: 0.75;
    transform: scale(0.98);
  }
  100% {
    opacity: 1;
    transform: scale(1.02);
  }
}

.login-card {
  position: relative;
  z-index: 1;
  background: linear-gradient(180deg, #ffffff 0%, #fafcff 100%);
  border: 1.5px solid rgba(255, 105, 0, 0.42);
  border-radius: 24px;
  padding: 1.85rem 2.25rem;
  box-shadow: 
    0 0 0 1px rgba(255, 105, 0, 0.2),
    0 0 24px -2px rgba(255, 105, 0, 0.32),
    0 0 50px 4px rgba(255, 105, 0, 0.14),
    0 20px 45px -10px rgba(7, 23, 53, 0.14);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Illuminated top accent glow line */
.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #FF6900 0%, #FFA858 50%, #0B1F4B 100%);
  box-shadow: 0 2px 14px rgba(255, 105, 0, 0.65);
  z-index: 2;
}

/* Corner ambient soft glow refraction */
.login-card::after {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 130px;
  height: 130px;
  background: radial-gradient(circle, rgba(255, 105, 0, 0.16) 0%, transparent 70%);
  filter: blur(20px);
  pointer-events: none;
  z-index: 1;
}

.login-card:hover,
.login-card:focus-within {
  border-color: rgba(255, 105, 0, 0.7);
  box-shadow: 
    0 0 0 2px rgba(255, 105, 0, 0.35),
    0 0 32px 0 rgba(255, 105, 0, 0.42),
    0 0 65px 8px rgba(255, 105, 0, 0.2),
    0 25px 55px -10px rgba(7, 23, 53, 0.18);
  transform: translateY(-2px);
}

/* Header */
.card-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 0.85rem;
  position: relative;
  z-index: 2;
}

.card-brand-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-brand-logo {
  height: 44px;
  width: auto;
  max-width: 220px;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.04));
  transition: transform 0.2s ease;
}

.card-brand-logo:hover {
  transform: scale(1.02);
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.45rem;
}

.welcome-badge {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #EA580C;
  background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
  border: 1px solid rgba(255, 105, 0, 0.3);
  box-shadow: 0 2px 8px rgba(255, 105, 0, 0.1);
  padding: 0.2rem 0.65rem;
  border-radius: 6px;
}

.badge-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #cbd5e1;
}

.system-badge {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #071F49;
  background: #F0F4FA;
  border: 1px solid rgba(7, 31, 73, 0.12);
  padding: 0.2rem 0.65rem;
  border-radius: 6px;
}

.card-main-heading {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 1.45rem;
  font-weight: 700;
  color: #071F49;
  line-height: 1.2;
  letter-spacing: -0.015em;
  margin-bottom: 0.15rem;
}

.card-sub-heading {
  font-size: 0.825rem;
  color: #64748b;
  line-height: 1.35;
}

/* Feedback Banners */
.feedback-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  line-height: 1.45;
  margin-bottom: 1.35rem;
}

.feedback-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 1px;
}

.error-banner {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.error-banner .feedback-icon {
  stroke: #dc2626;
}

.info-banner {
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #174ea6;
}

.info-banner .feedback-icon {
  stroke: #2563eb;
}

/* Form Styles */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 100%;
}

.label-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.field-label {
  font-size: 0.865rem;
  font-weight: 600;
  color: #334155;
}

.required-star {
  color: #ef4444;
  margin-left: 2px;
}

.forgot-password-link {
  font-size: 0.8rem;
  font-weight: 600;
  color: #174ea6;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  transition: color 0.15s ease;
}

.forgot-password-link:hover {
  color: #1e40af;
  text-decoration: underline;
}

.input-control-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.leading-icon {
  position: absolute;
  left: 1.15rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  pointer-events: none;
  transition: color 0.2s ease;
}

.leading-icon svg {
  width: 19px;
  height: 19px;
}

.modern-input {
  width: 100%;
  height: 46px;
  padding: 0 1.15rem 0 3rem;
  font-size: 0.95rem;
  color: #0f172a;
  background-color: #ffffff;
  border: 1.5px solid #cbd5e1;
  border-radius: 14px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.modern-input.has-trailing {
  padding-right: 3rem;
}

.modern-input::placeholder {
  color: #94a3b8;
  font-size: 0.885rem;
}

.modern-input:focus {
  border-color: #FF6900;
  box-shadow: 0 0 0 3.5px rgba(255, 105, 0, 0.18), 0 2px 8px rgba(255, 105, 0, 0.08);
}

.input-control-box:focus-within .leading-icon {
  color: #FF6900;
}

.has-error .modern-input {
  border-color: #ef4444;
  background-color: #fffbfb;
}

.has-error .modern-input:focus {
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.12);
}

.has-error .leading-icon {
  color: #ef4444;
}

.trailing-action-btn {
  position: absolute;
  right: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #64748b;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.trailing-action-btn:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

.trailing-action-btn svg {
  width: 19px;
  height: 19px;
}

.validation-msg {
  font-size: 0.785rem;
  color: #dc2626;
  margin-top: 0.15rem;
}

/* Remember Me Checkbox */
.checkbox-row {
  display: flex;
  align-items: center;
  margin: 0.15rem 0 0.4rem 0;
}

.custom-checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  cursor: pointer;
  user-select: none;
}

.native-checkbox {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.custom-box {
  width: 19px;
  height: 19px;
  border-radius: 6px;
  border: 1.5px solid #cbd5e1;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.check-svg {
  width: 12px;
  height: 12px;
  stroke: #ffffff;
  stroke-dasharray: 20;
  stroke-dashoffset: 20;
  transition: stroke-dashoffset 0.2s ease;
}

.native-checkbox:checked + .custom-box {
  background-color: #174ea6;
  border-color: #174ea6;
}

.native-checkbox:checked + .custom-box .check-svg {
  stroke-dashoffset: 0;
}

.native-checkbox:focus-visible + .custom-box {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.checkbox-text {
  font-size: 0.865rem;
  color: #475569;
  font-weight: 500;
}

/* Primary Submit CTA */
.submit-cta-btn {
  width: 100%;
  height: 50px;
  border-radius: 14px;
  border: 1px solid rgba(255, 105, 0, 0.28);
  background: linear-gradient(135deg, #071735 0%, #0F2759 100%);
  color: #ffffff;
  font-size: 0.98rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(7, 23, 53, 0.28), 0 0 16px rgba(255, 105, 0, 0.15);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.submit-cta-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  background: linear-gradient(135deg, #FF6900 0%, #FF851B 100%);
  border-color: #FF6900;
  box-shadow: 0 10px 28px rgba(255, 105, 0, 0.42), 0 0 20px rgba(255, 105, 0, 0.28);
}

.submit-cta-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 12px rgba(255, 105, 0, 0.25);
}

.submit-cta-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-arrow {
  width: 19px;
  height: 19px;
  transition: transform 0.2s ease;
}

.submit-cta-btn:hover:not(:disabled) .btn-arrow {
  transform: translateX(4px);
}

.btn-spinner {
  width: 19px;
  height: 19px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Security Footer */
.security-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  margin-top: 1.75rem;
  text-align: center;
}

.security-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: #64748b;
}

.shield-icon {
  width: 14px;
  height: 14px;
  stroke: #174ea6;
}

.security-school {
  font-size: 0.725rem;
  color: #94a3b8;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.25rem;
  z-index: 1000;
  animation: modalFade 0.25s ease-out;
}

.modal-box {
  background: #ffffff;
  border-radius: 20px;
  max-width: 480px;
  width: 100%;
  padding: 1.75rem 2rem;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  border: 1px solid #e2e8f0;
  animation: modalScale 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  margin-bottom: 1.25rem;
}

.modal-badge-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #174ea6;
  flex-shrink: 0;
}

.modal-badge-icon svg {
  width: 22px;
  height: 22px;
}

.modal-title {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
}

.modal-sub {
  font-size: 0.8rem;
  color: #64748b;
}

.modal-close {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.modal-close:hover {
  color: #0f172a;
  background-color: #f1f5f9;
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-desc {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.55;
  margin-bottom: 1.25rem;
}

.support-entries {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.support-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.support-label {
  font-size: 0.725rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.support-val {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
}

.modal-btn {
  padding: 0.65rem 1.4rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  background-color: #174ea6;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.modal-btn:hover {
  background-color: #1e40af;
}

/* Animations */
@keyframes cardSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes modalFade {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalScale {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive Media Queries for Form */
@media (max-width: 1080px) {
  .login-workspace {
    padding: 2.5rem;
  }
  .login-card {
    padding: 2.25rem 2rem;
  }
}

@media (max-width: 860px) {
  .login-workspace {
    flex: 1;
    width: 100%;
    padding: 1.75rem 1.5rem 3.5rem 1.5rem;
    align-items: flex-start;
  }

  .login-card-wrapper {
    max-width: 480px;
    margin: 0 auto;
  }

  .login-card {
    padding: 2rem 1.75rem;
    border-radius: 22px;
    border: 1.5px solid rgba(255, 105, 0, 0.45);
    box-shadow: 
      0 0 0 1px rgba(255, 105, 0, 0.22),
      0 0 22px -2px rgba(255, 105, 0, 0.3),
      0 0 45px 2px rgba(255, 105, 0, 0.12),
      0 16px 36px -8px rgba(7, 23, 53, 0.12);
  }

  .logo-badge-container {
    display: none; /* Logo already in mobile hero section */
  }

  .card-main-heading {
    font-size: 1.45rem;
  }
}

@media (max-width: 430px) {
  .login-workspace {
    padding: 1.25rem 1.15rem 2.75rem 1.15rem;
  }

  .login-card {
    padding: 1.75rem 1.25rem;
    border-radius: 20px;
    border: 1.5px solid rgba(255, 105, 0, 0.45);
    box-shadow: 
      0 0 0 1px rgba(255, 105, 0, 0.2),
      0 0 18px -2px rgba(255, 105, 0, 0.28),
      0 12px 28px -6px rgba(7, 23, 53, 0.1);
  }

  .modern-input {
    height: 52px;
    font-size: 0.925rem;
  }

  .submit-cta-btn {
    height: 52px;
    font-size: 0.95rem;
  }
}

/* Tenant Context Banner Styles */
.inst-portal-banner {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  padding: 0.5rem 0.85rem;
  margin-bottom: 0.75rem;
}

.inst-portal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.inst-portal-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.inst-portal-info {
  flex: 1;
  min-width: 0;
}

.inst-portal-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #14532d;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.inst-portal-code {
  font-size: 0.725rem;
  font-weight: 500;
  color: #16a34a;
}

.inst-portal-clear-btn {
  background: transparent;
  border: none;
  color: #15803d;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  line-height: 1;
  transition: background 0.15s ease;
}

.inst-portal-clear-btn:hover {
  background: #dcfce7;
}
</style>
