<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useSchoolBrandingStore } from '../../stores/schoolBranding';
import { adminService } from '../../services/adminService';
import { SystemSetting } from '../../types/admin';
import StatusBadge from '../../components/common/StatusBadge.vue';

const brandingStore = useSchoolBrandingStore();
const dbSettings = ref<SystemSetting[]>([]);
const isLoading = ref<boolean>(true);

async function loadSettings() {
  isLoading.value = true;
  try {
    const data = await adminService.getPublicSettings();
    dbSettings.value = data;
  } catch {
    // Fallback gracefully
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadSettings();
});
</script>

<template>
  <div class="settings-page">
    <div class="page-title-row">
      <div>
        <h2 class="section-title">System & Institutional Settings</h2>
        <p class="section-desc">Manage school branding configuration and core system parameters.</p>
      </div>
    </div>

    <!-- Branding Preview Card -->
    <div class="card branding-card">
      <div class="branding-header">
        <div class="branding-logo-box">
          <img
            v-if="brandingStore.schoolLogo"
            :src="brandingStore.schoolLogo"
            :alt="brandingStore.schoolName"
            class="branding-logo-img"
          />
          <div v-else class="school-initials-badge">
            <span class="school-initials-text">{{ brandingStore.schoolInitials }}</span>
          </div>
        </div>
        <div class="branding-info">
          <h3 class="institution-name">{{ brandingStore.schoolName }}</h3>
          <p class="institution-motto">"{{ brandingStore.schoolCode }} &bull; {{ brandingStore.schoolType }}"</p>
          <span class="location-tag">{{ brandingStore.city }}, Somalia</span>
        </div>
      </div>

      <div class="branding-meta-grid">
        <div class="meta-item">
          <span class="meta-label">Institution Code</span>
          <span class="meta-value">{{ brandingStore.schoolCode }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Primary Color</span>
          <div class="color-preview-row">
            <span class="color-swatch" :style="{ backgroundColor: '#0B1F4B' }" />
            <code>#0B1F4B (Navy)</code>
          </div>
        </div>
        <div class="meta-item">
          <span class="meta-label">Brand Accent</span>
          <div class="color-preview-row">
            <span class="color-swatch" :style="{ backgroundColor: '#FF6500' }" />
            <code>#FF6500 (Orange)</code>
          </div>
        </div>
        <div class="meta-item">
          <span class="meta-label">Contact Email</span>
          <span class="meta-value">{{ brandingStore.contactEmail || 'Not configured' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Campus Phone</span>
          <span class="meta-value">{{ brandingStore.contactPhone || 'Not configured' }}</span>
        </div>
      </div>
    </div>

    <!-- Database System Settings Table -->
    <div class="card settings-table-card">
      <div class="table-card-header">
        <h3 class="table-title">Database System Parameters (`system_settings`)</h3>
        <StatusBadge status="SYNCHRONIZED" variant="success" />
      </div>

      <div class="table-responsive">
        <table class="settings-table">
          <thead>
            <tr>
              <th>Setting Key</th>
              <th>Value</th>
              <th>Description</th>
              <th>Access</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="setting in dbSettings" :key="setting.id">
              <td>
                <code class="key-code">{{ setting.key }}</code>
              </td>
              <td class="value-cell">{{ setting.value }}</td>
              <td class="desc-cell">{{ setting.description || '-' }}</td>
              <td>
                <StatusBadge
                  :status="setting.is_public ? 'PUBLIC' : 'PRIVATE'"
                  :variant="setting.is_public ? 'info' : 'neutral'"
                />
              </td>
            </tr>
            <tr v-if="dbSettings.length === 0">
              <td colspan="4" class="empty-cell">Loading system settings...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
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

/* Branding Card */
.branding-card {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-left: 5px solid var(--brand-secondary);
}

.branding-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.branding-logo-box {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  background-color: var(--brand-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.branding-logo-img {
  width: 48px;
  height: 48px;
}

.institution-name {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
}

.institution-motto {
  font-size: 0.95rem;
  font-style: italic;
  color: var(--brand-secondary);
  margin: 0.2rem 0;
}

.location-tag {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.branding-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.meta-value {
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--text-primary);
}

.color-preview-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-swatch {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

/* Settings Table */
.settings-table-card {
  padding: 0;
  overflow: hidden;
}

.table-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.table-title {
  font-size: 1.05rem;
  font-weight: 700;
}

.table-responsive {
  overflow-x: auto;
}

.settings-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.875rem;
}

.settings-table th {
  background-color: var(--bg-surface-secondary);
  padding: 0.85rem 1.5rem;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.settings-table td {
  padding: 0.85rem 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.settings-table tr:last-child td {
  border-bottom: none;
}

.key-code {
  background: var(--bg-surface-secondary);
  padding: 0.2rem 0.45rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--brand-primary);
  font-weight: 600;
}

.value-cell {
  font-weight: 500;
  color: var(--text-primary);
}

.desc-cell {
  color: var(--text-muted);
}

.empty-cell {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}

@media (max-width: 640px) {
  .branding-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .branding-meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }
  .settings-table th,
  .settings-table td {
    padding: 0.65rem 0.85rem;
    font-size: 0.8rem;
  }
}
</style>
