<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { superAdminService } from '../../services/superAdminService';
import { User } from '../../types/user';

const users = ref<User[]>([]);
const isLoading = ref(true);

async function loadUsers() {
  isLoading.value = true;
  try {
    users.value = await superAdminService.getCompanyUsers();
  } catch (err) {
    console.error('Failed to load company users:', err);
  } finally {
    isLoading.value = false;
  }
}

function formatDate(dStr?: string) {
  if (!dStr) return '-';
  try {
    return new Date(dStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dStr;
  }
}

onMounted(() => {
  loadUsers();
});
</script>

<template>
  <div class="sau-page">
    <div class="sau-header">
      <div>
        <h1 class="sau-title">Users & Roles</h1>
        <p class="sau-sub">Manage Somroyal Technology Solutions platform administrators and system permissions.</p>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="sau-stats-grid">
      <div class="sau-stat-card">
        <div class="sau-stat-icon bg-blue-50 text-blue-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
        </div>
        <div>
          <span class="sau-stat-label">Platform Administrators</span>
          <span class="sau-stat-val text-slate-800">{{ users.length }}</span>
        </div>
      </div>

      <div class="sau-stat-card">
        <div class="sau-stat-icon bg-emerald-50 text-emerald-600">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
        </div>
        <div>
          <span class="sau-stat-label">Multi-Tenant Root Access</span>
          <span class="sau-stat-val text-emerald-600">Enforced</span>
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div class="sau-card sau-desktop-only">
      <div class="sau-table-wrap">
        <table class="sau-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Username</th>
              <th>Email</th>
              <th>Platform Role</th>
              <th>Superuser</th>
              <th>Status</th>
              <th>Last Login</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>
                <div class="flex items-center gap-3">
                  <div class="sau-avatar">
                    {{ u.full_name.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-bold text-slate-900">{{ u.full_name }}</div>
                    <div class="text-xs text-slate-400">ID #{{ u.id }}</div>
                  </div>
                </div>
              </td>
              <td class="font-mono text-slate-700 text-xs">{{ u.username }}</td>
              <td class="text-slate-600 text-xs">{{ u.email }}</td>
              <td>
                <span class="sau-badge-role">SUPER_ADMIN</span>
              </td>
              <td>
                <span v-if="u.is_superuser" class="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">Yes</span>
                <span v-else class="text-xs text-slate-400">No</span>
              </td>
              <td>
                <span class="sau-status-active">Active</span>
              </td>
              <td class="text-xs text-slate-500">{{ formatDate(u.last_login_at) }}</td>
            </tr>

            <tr v-if="!users.length && !isLoading">
              <td colspan="7" class="text-center py-12 text-slate-400">
                No administrative users found.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Cards View (<768px) -->
    <div class="sau-mobile-cards sau-mobile-only">
      <div
        v-for="u in users"
        :key="`mu-${u.id}`"
        class="sau-mobile-card"
      >
        <div class="sau-mcard-top">
          <div class="sau-avatar">
            {{ u.full_name.charAt(0).toUpperCase() }}
          </div>
          <div class="flex-1">
            <div class="font-bold text-slate-900 text-sm">{{ u.full_name }}</div>
            <div class="text-xs text-slate-400 font-mono">{{ u.username }}</div>
          </div>
          <span class="sau-status-active">Active</span>
        </div>

        <div class="sau-mcard-body">
          <div class="sau-mcard-row">
            <span class="text-xs text-slate-500">Email:</span>
            <span class="text-xs font-semibold text-slate-800">{{ u.email }}</span>
          </div>
          <div class="sau-mcard-row">
            <span class="text-xs text-slate-500">Platform Role:</span>
            <span class="sau-badge-role">SUPER_ADMIN</span>
          </div>
          <div class="sau-mcard-row">
            <span class="text-xs text-slate-500">Superuser:</span>
            <span class="text-xs font-bold text-emerald-600">{{ u.is_superuser ? 'Yes' : 'No' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sau-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sau-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sau-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sau-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sau-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.sau-stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sau-stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sau-stat-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.sau-stat-val {
  font-size: 1.65rem;
  font-weight: 800;
  line-height: 1.2;
}

.sau-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sau-table-wrap {
  overflow-x: auto;
}

.sau-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sau-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.04em;
}

.sau-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sau-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #061737 0%, #1e40af 100%);
  color: #ffffff;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.sau-badge-role {
  background: #fff7ed;
  color: #ff6500;
  border: 1px solid #fed7aa;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.sau-status-active {
  background: #ecfdf5;
  color: #059669;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
}

/* Visibility */
.sau-desktop-only {
  display: block;
}

.sau-mobile-only {
  display: none;
}

/* Mobile cards */
.sau-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.sau-mobile-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sau-mcard-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sau-mcard-body {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.sau-mcard-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@media (max-width: 768px) {
  .sau-stats-grid {
    grid-template-columns: 1fr;
  }

  .sau-desktop-only {
    display: none;
  }

  .sau-mobile-only {
    display: flex;
  }
}
</style>
