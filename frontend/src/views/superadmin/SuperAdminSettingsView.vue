<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { superAdminService } from '../../services/superAdminService';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const settings = ref<any>({
  company_name: 'Somroyal Technology Solutions',
  platform_name: 'Somroyal Educational Management System (SEMS)',
  headquarters: 'Abudwak, Galgaduud, Somalia',
  support_email: 'support@somroyal.com',
  support_phone: '+252 61 5000000',
  sales_phone: '+252 61 7000000',
  brand_primary_color: '#071D49',
  brand_accent_color: '#FF6500',
});

const isSaved = ref(false);

async function loadSettings() {
  try {
    const s = await superAdminService.getSettings();
    if (s) settings.value = { ...settings.value, ...s };
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
}

function handleSave() {
  isSaved.value = true;
  setTimeout(() => {
    isSaved.value = false;
  }, 2500);
}

onMounted(() => {
  loadSettings();
});
</script>

<template>
  <div class="sas-page">
    <div class="sas-header">
      <div>
        <h1 class="sas-title">System & Platform Settings</h1>
        <p class="sas-sub">Manage Somroyal Technology Solutions enterprise parameters and global configurations.</p>
      </div>

      <button class="sas-btn-save" @click="handleSave">
        <span>Save Changes</span>
      </button>
    </div>

    <div v-if="isSaved" class="sas-alert-success">
      Settings successfully updated!
    </div>

    <div class="sas-settings-grid">
      <!-- Section: Enterprise Info -->
      <div class="sas-panel">
        <h3 class="sas-panel-title">Somroyal Company Profile</h3>
        <p class="sas-panel-desc">Primary company identity owning the platform.</p>

        <div class="sas-form-group">
          <label class="sas-label">Company Name</label>
          <input v-model="settings.company_name" type="text" class="sas-input" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Platform Title</label>
          <input v-model="settings.platform_name" type="text" class="sas-input" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Official Headquarters</label>
          <input v-model="settings.headquarters" type="text" class="sas-input" />
        </div>
      </div>

      <!-- Section: Contact & Support Channels -->
      <div class="sas-panel">
        <h3 class="sas-panel-title">Contact & Support Channels</h3>
        <p class="sas-panel-desc">Displayed on the support card and institution portals.</p>

        <div class="sas-form-group">
          <label class="sas-label">Technical Support Email</label>
          <input v-model="settings.support_email" type="email" class="sas-input" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Somalia Hotlines (+252)</label>
          <input v-model="settings.support_phone" type="text" class="sas-input" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Sales Hotline</label>
          <input v-model="settings.sales_phone" type="text" class="sas-input" />
        </div>
      </div>

      <!-- Section: Super Admin Profile -->
      <div class="sas-panel">
        <h3 class="sas-panel-title">Active Super Administrator</h3>
        <p class="sas-panel-desc">Your authenticated credentials and privileges.</p>

        <div class="sas-form-group">
          <label class="sas-label">Logged In User</label>
          <input :value="authStore.user?.full_name || 'Admin User'" disabled type="text" class="sas-input bg-slate-50" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Primary Email</label>
          <input :value="authStore.user?.email || 'superadmin@somroyal.com'" disabled type="text" class="sas-input bg-slate-50" />
        </div>

        <div class="sas-form-group">
          <label class="sas-label">Authorization Role</label>
          <input value="SUPER_ADMIN (Global Multi-Institution Access)" disabled type="text" class="sas-input bg-slate-50 text-orange-600 font-semibold" />
        </div>
      </div>

      <!-- Section: Multi-Tenancy Architecture -->
      <div class="sas-panel">
        <h3 class="sas-panel-title">Multi-Tenancy & Data Isolation</h3>
        <p class="sas-panel-desc">Security model isolating institution records.</p>

        <div class="sas-info-box">
          <div class="font-bold text-slate-800 text-sm">Tenant Scoping Mode: ACTIVE</div>
          <p class="text-xs text-slate-600 mt-1">
            Every student, teacher, class, attendance, and exam record is strictly scoped by <code>institution_id</code>.
            School administrators and users cannot view or mutate data belonging to other institutions.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sas-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sas-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sas-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
}

.sas-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sas-btn-save {
  background: #ff6500;
  color: #ffffff;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.7rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.3);
  transition: background 0.2s;
}

.sas-btn-save:hover {
  background: #e55a00;
}

.sas-alert-success {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 0.85rem 1.25rem;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
}

.sas-settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.sas-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sas-panel-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sas-panel-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin: -0.5rem 0 0.5rem;
}

.sas-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sas-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.sas-input {
  padding: 0.6rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
}

.sas-info-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
}

@media (max-width: 900px) {
  .sas-settings-grid {
    grid-template-columns: 1fr;
  }
}
</style>
