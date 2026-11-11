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

    <div class="sau-card">
      <div class="sau-table-wrap sau-desktop-table" tabindex="0" role="region" aria-label="Company users table">
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
              <td class="text-slate-600">{{ u.email }}</td>
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
              <td class="text-xs text-slate-500 whitespace-nowrap">{{ formatDate(u.last_login_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Company Users Cards (<= 768px) -->
      <div class="sau-mobile-cards">
        <article v-for="u in users" :key="'m-usr-' + u.id" class="sau-mobile-card">
          <div class="sau-mobile-head">
            <div class="sau-mobile-user">
              <div class="sau-avatar">{{ u.full_name.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="sau-mobile-name">{{ u.full_name }}</div>
                <div class="sau-mobile-id">ID #{{ u.id }} • @{{ u.username }}</div>
              </div>
            </div>
            <span class="sau-status-active">Active</span>
          </div>
          <div class="sau-mobile-kv-grid">
            <div class="sau-mobile-kv sau-kv-span">
              <span class="sau-kv-label">Email</span>
              <span class="sau-kv-val sau-kv-email">{{ u.email }}</span>
            </div>
            <div class="sau-mobile-kv">
              <span class="sau-kv-label">Role</span>
              <span class="sau-badge-role">SUPER_ADMIN</span>
            </div>
            <div class="sau-mobile-kv">
              <span class="sau-kv-label">Superuser</span>
              <span class="sau-kv-val">{{ u.is_superuser ? 'Yes' : 'No' }}</span>
            </div>
            <div class="sau-mobile-kv sau-kv-span">
              <span class="sau-kv-label">Last Login</span>
              <span class="sau-kv-val">{{ formatDate(u.last_login_at) }}</span>
            </div>
          </div>
        </article>
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
  flex-wrap: wrap;
  gap: 0.75rem;
}

.sau-title {
  font-size: clamp(1.35rem, 4vw, 1.75rem);
  font-weight: 800;
  color: #061737;
  margin: 0;
}

.sau-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sau-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: clip;
  min-width: 0;
}

.sau-table-wrap {
  overflow-x: auto;
}

.sau-table {
  width: 100%;
  min-width: 740px;
  border-collapse: collapse;
  text-align: left;
}

.sau-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.sau-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.875rem;
}

.sau-mobile-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.sau-mobile-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sau-mobile-user {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}

.sau-mobile-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #061737;
}

.sau-mobile-id {
  font-family: monospace;
  font-size: 0.74rem;
  color: #64748b;
}

.sau-mobile-kv-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem 0.75rem;
  padding-top: 0.45rem;
  border-top: 1px dashed #e2e8f0;
}

.sau-mobile-kv {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
  min-width: 0;
}

.sau-kv-span {
  grid-column: 1 / -1;
}

.sau-kv-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #64748b;
}

.sau-kv-val {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1e293b;
}

.sau-kv-email {
  overflow-wrap: break-word;
  word-break: break-all;
}

.sau-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sau-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #061737;
  color: #ffffff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
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
  white-space: nowrap;
}

@media (max-width: 768px) {
  .sau-desktop-table {
    display: none;
  }

  .sau-mobile-cards {
    display: flex;
  }
}

@media (max-width: 640px) {
  .sau-table th,
  .sau-table td {
    padding: 0.75rem 0.85rem;
  }
}
</style>
