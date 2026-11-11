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
              <td class="text-xs text-slate-500">{{ formatDate(u.last_login_at) }}</td>
            </tr>
          </tbody>
        </table>
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
  overflow: hidden;
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
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
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
}
</style>
