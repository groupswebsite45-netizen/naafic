<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { adminService } from '../../services/adminService';
import { authService } from '../../services/authService';
import InputField from '../../components/common/InputField.vue';
import AppButton from '../../components/common/AppButton.vue';
import StatusBadge from '../../components/common/StatusBadge.vue';

const authStore = useAuthStore();

// Profile Edit Form State
const profileForm = reactive({
  full_name: authStore.user?.full_name || '',
  phone_number: authStore.user?.phone_number || '',
});
const isSavingProfile = ref(false);
const profileSuccessMsg = ref<string | null>(null);
const profileErrorMsg = ref<string | null>(null);

// Password Change Form State
const pwdForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});
const pwdErrors = reactive({
  current: '',
  new: '',
  confirm: '',
  general: '',
});
const isSavingPwd = ref(false);
const pwdSuccessMsg = ref<string | null>(null);

const userRoleNames = computed(() => {
  return authStore.user?.roles.map((r) => r.name).join(', ') || 'ADMIN';
});

async function handleSaveProfile() {
  isSavingProfile.value = true;
  profileSuccessMsg.value = null;
  profileErrorMsg.value = null;

  try {
    const updated = await adminService.updateProfile({
      full_name: profileForm.full_name,
      phone_number: profileForm.phone_number,
    });
    authStore.updateUserProfile(updated);
    profileSuccessMsg.value = 'Profile information updated successfully.';
  } catch (err: any) {
    profileErrorMsg.value = err.response?.data?.error?.message || 'Failed to update profile.';
  } finally {
    isSavingProfile.value = false;
  }
}

function validatePwdForm(): boolean {
  let valid = true;
  pwdErrors.current = '';
  pwdErrors.new = '';
  pwdErrors.confirm = '';
  pwdErrors.general = '';

  if (!pwdForm.current_password) {
    pwdErrors.current = 'Please enter your current password.';
    valid = false;
  }
  if (!pwdForm.new_password || pwdForm.new_password.length < 8) {
    pwdErrors.new = 'New password must be at least 8 characters.';
    valid = false;
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    pwdErrors.confirm = 'New passwords do not match.';
    valid = false;
  }

  return valid;
}

async function handleChangePassword() {
  if (!validatePwdForm()) return;

  isSavingPwd.value = true;
  pwdSuccessMsg.value = null;

  try {
    const res = await authService.changePassword({
      current_password: pwdForm.current_password,
      new_password: pwdForm.new_password,
    });
    pwdSuccessMsg.value = res.message || 'Password changed successfully.';
    pwdForm.current_password = '';
    pwdForm.new_password = '';
    pwdForm.confirm_password = '';
  } catch (err: any) {
    pwdErrors.general = err.response?.data?.error?.message || err.response?.data?.detail || 'Password change failed.';
  } finally {
    isSavingPwd.value = false;
  }
}
</script>

<template>
  <div class="profile-page">
    <div class="page-title-row">
      <div>
        <h2 class="section-title">Administrator Profile & Security</h2>
        <p class="section-desc">Manage your administrative credentials and security preferences.</p>
      </div>
    </div>

    <div class="profile-layout-grid">
      <!-- Left Column: Identity Overview Card -->
      <div class="identity-card card">
        <div class="avatar-large">
          {{ (authStore.user?.full_name || 'A').charAt(0).toUpperCase() }}
        </div>

        <h3 class="user-display-name">{{ authStore.user?.full_name }}</h3>
        <p class="user-display-username">@{{ authStore.user?.username }}</p>

        <div class="role-badge-wrap">
          <StatusBadge status="ADMINISTRATOR" variant="info" />
          <StatusBadge v-if="authStore.user?.is_active" status="ACTIVE ACCOUNT" variant="success" />
        </div>

        <div class="identity-details-list">
          <div class="detail-item">
            <span class="detail-label">Email Address</span>
            <span class="detail-value">{{ authStore.user?.email }}</span>
          </div>

          <div class="detail-item">
            <span class="detail-label">System Role</span>
            <span class="detail-value">{{ userRoleNames }}</span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Account Created</span>
            <span class="detail-value">
              {{ authStore.user?.created_at ? new Date(authStore.user.created_at).toLocaleDateString() : 'N/A' }}
            </span>
          </div>

          <div class="detail-item">
            <span class="detail-label">Last Login</span>
            <span class="detail-value">
              {{ authStore.user?.last_login_at ? new Date(authStore.user.last_login_at).toLocaleString() : 'First session' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Right Column: Edit Profile & Change Password Tabs/Panels -->
      <div class="forms-column">
        <!-- 1. Edit Profile Information -->
        <div class="card form-panel">
          <h3 class="panel-title">Personal Information</h3>
          <p class="panel-subtitle">Update your full name and campus contact phone number.</p>

          <div v-if="profileSuccessMsg" class="alert-box success">
            {{ profileSuccessMsg }}
          </div>
          <div v-if="profileErrorMsg" class="alert-box danger">
            {{ profileErrorMsg }}
          </div>

          <form @submit.prevent="handleSaveProfile" class="profile-form">
            <InputField
              id="profile-fullname"
              v-model="profileForm.full_name"
              label="Full Name"
              type="text"
              :required="true"
            />

            <InputField
              id="profile-phone"
              v-model="profileForm.phone_number"
              label="Phone Number"
              type="tel"
              placeholder="+252 61 0000000"
            />

            <div class="form-actions">
              <AppButton
                type="submit"
                variant="primary"
                :loading="isSavingProfile"
              >
                Save Profile Changes
              </AppButton>
            </div>
          </form>
        </div>

        <!-- 2. Change Password Security -->
        <div class="card form-panel">
          <h3 class="panel-title">Security & Password</h3>
          <p class="panel-subtitle">Update your password using strict security verification.</p>

          <div v-if="pwdSuccessMsg" class="alert-box success">
            {{ pwdSuccessMsg }}
          </div>
          <div v-if="pwdErrors.general" class="alert-box danger">
            {{ pwdErrors.general }}
          </div>

          <form @submit.prevent="handleChangePassword" class="password-form">
            <InputField
              id="current-password"
              v-model="pwdForm.current_password"
              label="Current Password"
              type="password"
              :required="true"
              :error="pwdErrors.current"
              placeholder="Enter your current password"
            />

            <InputField
              id="new-password"
              v-model="pwdForm.new_password"
              label="New Password"
              type="password"
              :required="true"
              :error="pwdErrors.new"
              placeholder="Minimum 8 characters"
            />

            <InputField
              id="confirm-password"
              v-model="pwdForm.confirm_password"
              label="Confirm New Password"
              type="password"
              :required="true"
              :error="pwdErrors.confirm"
              placeholder="Re-enter new password"
            />

            <div class="form-actions">
              <AppButton
                type="submit"
                variant="primary"
                :loading="isSavingPwd"
              >
                Update Password
              </AppButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.page-title-row {
  margin-bottom: 0.5rem;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
}

.section-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.profile-layout-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.75rem;
  align-items: start;
}

/* Identity Card */
.identity-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1.5rem;
}

.avatar-large {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
  color: #ffffff;
  font-size: 2.25rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-md);
}

.user-display-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.user-display-username {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 0.85rem;
}

.role-badge-wrap {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.identity-details-list {
  width: 100%;
  border-top: 1px solid var(--border-subtle);
  padding-top: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  text-align: left;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}

/* Forms Column */
.forms-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-panel {
  padding: 1.75rem;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.panel-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.alert-box {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
}

.alert-box.success {
  background-color: var(--success-bg);
  color: var(--success-text);
  border: 1px solid var(--success-border);
}

.alert-box.danger {
  background-color: var(--danger-bg);
  color: var(--danger-text);
  border: 1px solid var(--danger-border);
}

/* Responsive */
@media (max-width: 960px) {
  .profile-layout-grid {
    grid-template-columns: 1fr;
  }
}
</style>
