<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { superAdminService } from '../../services/superAdminService';

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
        <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        <span>Save Changes</span>
      </button>
    </div>

    <!-- Feedback Banner -->
    <transition name="fade">
      <div v-if="isSaved" class="sas-alert-success">
        <svg class="w-5 h-5 text-emerald-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span>Platform settings successfully updated!</span>
      </div>
    </transition>

    <div class="sas-settings-grid">
      <!-- Section: Enterprise Info -->
      <div class="sas-panel">
        <div class="sas-panel-header">
          <div class="sas-panel-icon bg-blue-50 text-blue-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
            </svg>
          </div>
          <div>
            <h3 class="sas-panel-title">Somroyal Company Profile</h3>
            <p class="sas-panel-desc">Primary company identity owning and operating the platform.</p>
          </div>
        </div>

        <div class="sas-panel-body">
          <div class="sas-form-group">
            <label class="sas-label">Company Legal Name</label>
            <input v-model="settings.company_name" type="text" class="sas-input" />
          </div>

          <div class="sas-form-group">
            <label class="sas-label">Platform Title</label>
            <input v-model="settings.platform_name" type="text" class="sas-input" />
          </div>

          <div class="sas-form-group">
            <label class="sas-label">Corporate Headquarters</label>
            <input v-model="settings.headquarters" type="text" class="sas-input" />
          </div>

          <div class="sas-form-grid">
            <div class="sas-form-group">
              <label class="sas-label">Support Email</label>
              <input v-model="settings.support_email" type="email" class="sas-input" />
            </div>

            <div class="sas-form-group">
              <label class="sas-label">Support Phone</label>
              <input v-model="settings.support_phone" type="text" class="sas-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- Section: Brand & Visual Identity -->
      <div class="sas-panel">
        <div class="sas-panel-header">
          <div class="sas-panel-icon bg-orange-50 text-orange-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
              <path d="M2 12h20" />
            </svg>
          </div>
          <div>
            <h3 class="sas-panel-title">Branding & Color Tokens</h3>
            <p class="sas-panel-desc">Primary SaaS visual themes applied across portals.</p>
          </div>
        </div>

        <div class="sas-panel-body">
          <div class="sas-color-row">
            <div class="sas-color-preview-box" :style="{ backgroundColor: settings.brand_primary_color }"></div>
            <div class="flex-1">
              <label class="sas-label">Primary Brand Color (Deep Navy Blue)</label>
              <input v-model="settings.brand_primary_color" type="text" class="sas-input font-mono" />
            </div>
          </div>

          <div class="sas-color-row">
            <div class="sas-color-preview-box" :style="{ backgroundColor: settings.brand_accent_color }"></div>
            <div class="flex-1">
              <label class="sas-label">Accent Brand Color (Vibrant Orange)</label>
              <input v-model="settings.brand_accent_color" type="text" class="sas-input font-mono" />
            </div>
          </div>

          <div class="sas-branding-card mt-3">
            <span class="text-xs font-bold text-slate-700">Somroyal Official Logo Asset</span>
            <div class="flex items-center gap-3 mt-2">
              <img src="/somroyal-official-logo.png" alt="Somroyal" class="h-10 object-contain" />
              <span class="text-xs text-slate-400">Default SVG/PNG deployed across public & tenant portals.</span>
            </div>
          </div>
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
  flex-wrap: wrap;
  gap: 1rem;
}

.sas-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sas-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sas-btn-save {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  border: none;
  font-size: 0.88rem;
  font-weight: 700;
  height: 44px;
  padding: 0 1.35rem;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(255, 101, 0, 0.35);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.sas-btn-save:hover {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(255, 101, 0, 0.45);
}

.sas-alert-success {
  display: flex;
  align-items: center;
  padding: 0.85rem 1.25rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 12px;
  color: #065f46;
  font-weight: 600;
  font-size: 0.88rem;
}

.sas-settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.sas-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sas-panel-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.sas-panel-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sas-panel-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sas-panel-desc {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0.2rem 0 0;
}

.sas-panel-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sas-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sas-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  outline: none;
  transition: all 0.15s ease;
}

.sas-input:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sas-color-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sas-color-preview-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.sas-branding-card {
  padding: 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

@media (max-width: 900px) {
  .sas-settings-grid {
    grid-template-columns: 1fr;
  }

  .sas-form-grid {
    grid-template-columns: 1fr;
  }

  .sas-btn-save {
    width: 100%;
    justify-content: center;
  }
}
</style>
