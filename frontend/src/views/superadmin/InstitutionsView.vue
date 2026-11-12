<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { superAdminService } from '../../services/superAdminService';
import { useAuthStore } from '../../stores/auth';
import { Institution, InstitutionUpdatePayload } from '../../types/institution';
import RegisterInstitutionModal from './components/RegisterInstitutionModal.vue';

const router = useRouter();
const authStore = useAuthStore();

const institutions = ref<Institution[]>([]);
const isLoading = ref(true);
const searchQuery = ref('');
const selectedType = ref('');
const selectedStatus = ref('');
const isModalOpen = ref(false);

// Edit Modal State
const editModalOpen = ref(false);
const editingInst = ref<Institution | null>(null);
const isEditing = ref(false);
const editAdminUsername = ref('');
const editAdminEmail = ref('');
const resetPasswordInput = ref('');
const showResetPassword = ref(false);
const editSuccessMsg = ref('');
const editErrorMsg = ref('');

function generateRandomPassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789@#$';
  let pass = '';
  for (let i = 0; i < 10; i++) {
    pass += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  resetPasswordInput.value = pass;
  showResetPassword.value = true;
}

// High-Security Deletion Modal State
const deleteModalOpen = ref(false);
const deletingInst = ref<Institution | null>(null);
const confirmCodeInput = ref('');
const isAcknowledged = ref(false);
const isDeleting = ref(false);
const deleteError = ref('');

function openDeleteModal(inst: Institution) {
  deletingInst.value = inst;
  confirmCodeInput.value = '';
  isAcknowledged.value = false;
  deleteError.value = '';
  deleteModalOpen.value = true;
}

function closeDeleteModal() {
  if (isDeleting.value) return;
  deleteModalOpen.value = false;
  deletingInst.value = null;
  confirmCodeInput.value = '';
  isAcknowledged.value = false;
  deleteError.value = '';
}

const canConfirmDelete = computed(() => {
  if (!deletingInst.value) return false;
  const targetCode = deletingInst.value.code ? deletingInst.value.code.trim().toUpperCase() : '';
  const typedCode = confirmCodeInput.value ? confirmCodeInput.value.trim().toUpperCase() : '';
  return isAcknowledged.value && typedCode === targetCode;
});

async function executeDelete() {
  if (!deletingInst.value || !canConfirmDelete.value || isDeleting.value) return;

  isDeleting.value = true;
  deleteError.value = '';

  try {
    const code = deletingInst.value.code.trim().toUpperCase();
    await superAdminService.deleteInstitution(deletingInst.value.id, code);

    // Remove from local list
    const deletedId = deletingInst.value.id;
    institutions.value = institutions.value.filter((i) => i.id !== deletedId);

    // If active in authStore, clear it
    if (authStore.activeInstitution?.id === deletedId) {
      authStore.clearActiveInstitution();
    }

    deleteModalOpen.value = false;
    deletingInst.value = null;
  } catch (err: any) {
    console.error('Delete error:', err);
    deleteError.value = err.response?.data?.detail || 'Failed to delete institution. Please try again.';
  } finally {
    isDeleting.value = false;
  }
}

async function loadInstitutions() {
  isLoading.value = true;
  try {
    institutions.value = await superAdminService.getInstitutions({
      q: searchQuery.value || undefined,
      type: selectedType.value || undefined,
      status: selectedStatus.value || undefined,
    });
  } catch (err) {
    console.error('Failed to load institutions:', err);
  } finally {
    isLoading.value = false;
  }
}

watch([selectedType, selectedStatus], () => {
  loadInstitutions();
});

let debounceTimer: any = null;
function handleSearchInput() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    loadInstitutions();
  }, 300);
}

function openSms(inst: Institution) {
  authStore.setActiveInstitution(inst);
  router.push({ path: '/login', query: { institution: inst.code } });
}

async function handleToggleStatus(inst: Institution) {
  const nextStatus = inst.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
  if (confirm(`Are you sure you want to change status of '${inst.name}' to ${nextStatus}?`)) {
    try {
      await superAdminService.toggleInstitutionStatus(inst.id, nextStatus);
      inst.status = nextStatus;
    } catch (err) {
      alert('Failed to update status.');
    }
  }
}

function openEditModal(inst: Institution) {
  editingInst.value = { ...inst };
  editAdminUsername.value = inst.admin_username || '';
  editAdminEmail.value = inst.admin_email || inst.email || '';
  resetPasswordInput.value = '';
  showResetPassword.value = false;
  editSuccessMsg.value = '';
  editErrorMsg.value = '';
  editModalOpen.value = true;
}

async function saveEdit() {
  if (!editingInst.value) return;
  isEditing.value = true;
  editErrorMsg.value = '';
  editSuccessMsg.value = '';

  try {
    const payload: InstitutionUpdatePayload = {
      name: editingInst.value.name,
      type: editingInst.value.type,
      logo_url: editingInst.value.logo_url || null,
      contact_person: editingInst.value.contact_person,
      email: editingInst.value.email,
      phone: editingInst.value.phone,
      region: editingInst.value.region,
      city: editingInst.value.city,
      address: editingInst.value.address,
      status: editingInst.value.status,
      subscription_plan: editingInst.value.subscription_plan,
      admin_username: editAdminUsername.value.trim() || undefined,
      admin_email: editAdminEmail.value.trim() || undefined,
    };

    if (resetPasswordInput.value.trim()) {
      if (resetPasswordInput.value.trim().length < 6) {
        editErrorMsg.value = 'Furaha sirta ah (Password) waa inuu ka koobnaadaa ugu yaraan 6 xaraf.';
        isEditing.value = false;
        return;
      }
      payload.admin_password = resetPasswordInput.value.trim();
    }

    const updated = await superAdminService.updateInstitution(editingInst.value.id, payload);
    const idx = institutions.value.findIndex((i) => i.id === updated.id);
    if (idx !== -1) institutions.value[idx] = updated;

    editSuccessMsg.value = 'Xogta machadka iyo furayaasha maamulka si guul leh ayaa loo cusboonaysiiyay!';
    setTimeout(() => {
      editModalOpen.value = false;
    }, 1200);
  } catch (err: any) {
    console.error('Failed to update institution:', err);
    editErrorMsg.value = err.response?.data?.detail || 'Lama cusboonaysiin karin xogta machadka. Fadlan dib u eeg macluumaadka.';
  } finally {
    isEditing.value = false;
  }
}

function handleInstitutionCreated(_inst: Institution) {
  isModalOpen.value = false;
  loadInstitutions();
}

function formatDate(dateStr?: string | null) {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

// Stats overview
const totalCount = computed(() => institutions.value.length);
const activeCount = computed(() => institutions.value.filter(i => i.status === 'ACTIVE').length);
const suspendedCount = computed(() => institutions.value.filter(i => i.status === 'SUSPENDED').length);

onMounted(() => {
  loadInstitutions();
});
</script>

<template>
  <div class="sai-page-container">
    <!-- Top Header -->
    <div class="sai-header">
      <div class="sai-header-left">
        <h1 class="sai-title">Institutions Management</h1>
        <p class="sai-sub">Overview, provision, and configure school and academy tenants across the platform.</p>
      </div>

      <button class="sai-btn-add" @click="isModalOpen = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Register New Institution</span>
      </button>
    </div>

    <!-- Overview Stats Bar -->
    <div class="sai-stats-grid">
      <div class="sai-stat-card">
        <div class="sai-stat-icon-wrap bg-blue-50 text-blue-600">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
          </svg>
        </div>
        <div>
          <span class="sai-stat-label">Total Registered</span>
          <div class="sai-stat-val">{{ totalCount }}</div>
        </div>
      </div>

      <div class="sai-stat-card">
        <div class="sai-stat-icon-wrap bg-emerald-50 text-emerald-600">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </div>
        <div>
          <span class="sai-stat-label">Active Workspaces</span>
          <div class="sai-stat-val text-emerald-600">{{ activeCount }}</div>
        </div>
      </div>

      <div class="sai-stat-card">
        <div class="sai-stat-icon-wrap bg-rose-50 text-rose-600">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <div>
          <span class="sai-stat-label">Suspended</span>
          <div class="sai-stat-val text-rose-600">{{ suspendedCount }}</div>
        </div>
      </div>
    </div>

    <!-- Filter & Search Controls Bar -->
    <div class="sai-filters-row">
      <div class="sai-search-wrap">
        <svg class="sai-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="sai-search-input"
          placeholder="Search by institution name, code, contact or email..."
          @input="handleSearchInput"
        />
        <button v-if="searchQuery" class="sai-clear-btn" @click="searchQuery = ''; loadInstitutions()">✕</button>
      </div>

      <div class="sai-filter-selects">
        <select v-model="selectedType" class="sai-select" aria-label="Filter by type">
          <option value="">All Types</option>
          <option value="Primary School">Primary School</option>
          <option value="Secondary School">Secondary School</option>
          <option value="Primary & Secondary School">Primary & Secondary</option>
          <option value="Academy">Academy</option>
          <option value="College">College</option>
          <option value="Institute">Institute</option>
        </select>

        <select v-model="selectedStatus" class="sai-select" aria-label="Filter by status">
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="SUSPENDED">Suspended</option>
          <option value="PENDING">Pending</option>
        </select>

        <div class="sai-badge-count">
          <span>{{ institutions.length }}</span> institutions
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div class="sai-card sai-desktop-table">
      <div class="sai-table-wrap">
        <table class="sai-table">
          <thead>
            <tr>
              <th>Code / ID</th>
              <th>Institution Name</th>
              <th>Type</th>
              <th>Contact Person</th>
              <th>Location</th>
              <th>Subscription</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inst in institutions" :key="inst.id">
              <td>
                <div class="sai-code-badge">{{ inst.code }}</div>
                <div class="text-xs text-slate-400 mt-1">ID #{{ inst.id }}</div>
              </td>
              <td>
                <div class="sai-inst-info">
                  <div class="sai-inst-avatar">
                    <img v-if="inst.logo_url" :src="inst.logo_url" alt="" class="w-full h-full object-cover rounded-full" />
                    <span v-else>{{ inst.name.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div>
                    <div class="sai-inst-name">{{ inst.name }}</div>
                    <div class="sai-inst-email">{{ inst.email || 'No email provided' }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span
                  class="sai-type-badge"
                  :class="inst.type.toLowerCase().includes('school') ? 'badge-school' : 'badge-academy'"
                >
                  {{ inst.type }}
                </span>
              </td>
              <td>
                <div class="font-medium text-slate-800 text-sm">{{ inst.contact_person || 'N/A' }}</div>
                <div class="text-xs text-slate-500">{{ inst.phone || '' }}</div>
              </td>
              <td>
                <div class="text-slate-700 text-sm">{{ inst.city || inst.region || 'Mogadishu' }}</div>
                <div class="text-xs text-slate-400">{{ inst.region || 'Somalia' }}</div>
              </td>
              <td>
                <span class="sai-sub-badge">{{ inst.subscription_plan }}</span>
                <div class="text-xs text-slate-400 mt-1">Exp: {{ formatDate(inst.subscription_expiry_date) }}</div>
              </td>
              <td>
                <span
                  class="sai-status-badge"
                  :class="inst.status === 'ACTIVE' ? 'status-active' : inst.status === 'PENDING' ? 'status-pending' : 'status-suspended'"
                >
                  {{ inst.status }}
                </span>
              </td>
              <td class="text-right">
                <div class="sai-actions-group">
                  <button
                    class="sai-btn-open"
                    @click="openSms(inst)"
                    title="Launch School Management System in this institution's workspace"
                  >
                    <span>Open SMS</span>
                    <svg class="w-3.5 h-3.5 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>

                  <button
                    class="sai-btn-action"
                    @click="openEditModal(inst)"
                    title="Edit institution"
                  >
                    <svg class="w-4 h-4 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                  </button>

                  <button
                    class="sai-btn-action"
                    :class="inst.status === 'ACTIVE' ? 'text-amber-600 hover:bg-amber-50' : 'text-emerald-600 hover:bg-emerald-50'"
                    @click="handleToggleStatus(inst)"
                    :title="inst.status === 'ACTIVE' ? 'Suspend Institution' : 'Activate Institution'"
                  >
                    <svg v-if="inst.status === 'ACTIVE'" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                    </svg>
                    <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </button>

                  <!-- High-Security Delete Action Button -->
                  <button
                    class="sai-btn-action sai-btn-delete"
                    @click="openDeleteModal(inst)"
                    title="Delete institution (High-security verification required)"
                  >
                    <svg class="sai-btn-trash-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="!institutions.length && !isLoading">
              <td colspan="8" class="text-center py-12 text-slate-400">
                No institution records found matching your filters.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Mobile Responsive Cards View (<768px) -->
    <div class="sai-mobile-cards">
      <div
        v-for="inst in institutions"
        :key="`mc-${inst.id}`"
        class="sai-inst-card-mobile"
      >
        <div class="sai-mcard-top">
          <div class="sai-inst-avatar">
            <img v-if="inst.logo_url" :src="inst.logo_url" alt="" class="w-full h-full object-cover rounded-full" />
            <span v-else>{{ inst.name.charAt(0).toUpperCase() }}</span>
          </div>
          <div class="sai-mcard-title-box">
            <div class="sai-inst-name">{{ inst.name }}</div>
            <div class="sai-code-badge">{{ inst.code }}</div>
          </div>
          <span
            class="sai-status-badge"
            :class="inst.status === 'ACTIVE' ? 'status-active' : inst.status === 'PENDING' ? 'status-pending' : 'status-suspended'"
          >
            {{ inst.status }}
          </span>
        </div>

        <div class="sai-mcard-info-grid">
          <div class="sai-minfo-item">
            <span class="sai-minfo-label">Type:</span>
            <span class="sai-minfo-val font-semibold">{{ inst.type }}</span>
          </div>
          <div class="sai-minfo-item">
            <span class="sai-minfo-label">Location:</span>
            <span class="sai-minfo-val">{{ inst.city || inst.region || 'Mogadishu' }}</span>
          </div>
          <div class="sai-minfo-item">
            <span class="sai-minfo-label">Plan:</span>
            <span class="sai-minfo-val text-blue-700 font-semibold">{{ inst.subscription_plan }}</span>
          </div>
          <div class="sai-minfo-item">
            <span class="sai-minfo-label">Contact:</span>
            <span class="sai-minfo-val">{{ inst.contact_person || 'N/A' }}</span>
          </div>
        </div>

        <div class="sai-mcard-actions">
          <button class="sai-btn-open w-full" @click="openSms(inst)">
            <span>Open SMS Portal</span>
            <svg class="w-4 h-4 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
          <div class="sai-mcard-sub-actions">
            <button class="sai-btn-action flex-1" @click="openEditModal(inst)">
              Edit Profile
            </button>
            <button
              class="sai-btn-action flex-1"
              :class="inst.status === 'ACTIVE' ? 'text-amber-600' : 'text-emerald-600'"
              @click="handleToggleStatus(inst)"
            >
              {{ inst.status === 'ACTIVE' ? 'Suspend' : 'Activate' }}
            </button>
            <button class="sai-btn-action sai-btn-delete px-3" @click="openDeleteModal(inst)">
              Delete
            </button>
          </div>
        </div>
      </div>

      <div v-if="!institutions.length && !isLoading" class="text-center py-10 text-slate-400 bg-white rounded-xl border border-slate-200">
        No institution records found.
      </div>
    </div>

    <!-- Registration Modal -->
    <RegisterInstitutionModal
      v-if="isModalOpen"
      @close="isModalOpen = false"
      @created="handleInstitutionCreated"
    />

    <!-- Edit Institution Modal -->
    <div v-if="editModalOpen && editingInst" class="sai-modal-backdrop" @click.self="editModalOpen = false">
      <div class="sai-modal">
        <div class="sai-modal-header">
          <div class="flex items-center gap-2.5">
            <div class="sai-modal-icon-badge">
              <svg class="w-5 h-5 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </div>
            <div>
              <h3 class="sai-modal-title">Edit Institution Profile</h3>
              <p class="text-xs text-slate-500">{{ editingInst.name }} ({{ editingInst.code }})</p>
            </div>
          </div>
          <button class="sai-modal-close" @click="editModalOpen = false">✕</button>
        </div>

        <div class="sai-modal-body">
          <div v-if="editSuccessMsg" class="sai-alert-success">
            <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>{{ editSuccessMsg }}</span>
          </div>

          <div v-if="editErrorMsg" class="sai-alert-error">
            <svg class="w-4 h-4 text-red-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <span>{{ editErrorMsg }}</span>
          </div>

          <!-- Section 1: Basic Information -->
          <div class="sai-form-section">
            <div class="sai-form-section-header">
              <svg class="sai-section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
              </svg>
              <h4 class="sai-form-section-title">General Institution Information</h4>
            </div>

            <div class="sai-modal-field">
              <label class="sai-modal-label">Institution Name</label>
              <input v-model="editingInst.name" type="text" class="sai-modal-input" />
            </div>

            <div class="sai-modal-field">
              <label class="sai-modal-label">School Logo / Emblem URL</label>
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center overflow-hidden flex-shrink-0">
                  <img v-if="editingInst.logo_url" :src="editingInst.logo_url" alt="" class="w-full h-full object-contain" />
                  <svg v-else class="w-5 h-5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <input v-model="editingInst.logo_url" type="text" class="sai-modal-input flex-1" placeholder="/uploads/institution_logos/logo.png or https://..." />
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Classification / Type</label>
                <select v-model="editingInst.type" class="sai-modal-input">
                  <option value="Primary School">Primary School</option>
                  <option value="Secondary School">Secondary School</option>
                  <option value="Primary & Secondary School">Primary & Secondary</option>
                  <option value="Academy">Academy</option>
                  <option value="College">College</option>
                  <option value="Institute">Institute</option>
                </select>
              </div>

              <div class="sai-modal-field">
                <label class="sai-modal-label">Account Status</label>
                <select v-model="editingInst.status" class="sai-modal-input">
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="SUSPENDED">SUSPENDED</option>
                  <option value="PENDING">PENDING</option>
                </select>
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Contact Person</label>
                <input v-model="editingInst.contact_person" type="text" class="sai-modal-input" />
              </div>
              <div class="sai-modal-field">
                <label class="sai-modal-label">Official Phone</label>
                <input v-model="editingInst.phone" type="text" class="sai-modal-input" />
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Official Email</label>
                <input v-model="editingInst.email" type="email" class="sai-modal-input" />
              </div>
              <div class="sai-modal-field">
                <label class="sai-modal-label">City / Region</label>
                <input v-model="editingInst.city" type="text" class="sai-modal-input" />
              </div>
            </div>
          </div>

          <!-- Section 2: Administrator Account Setup & Password Reset -->
          <div class="sai-admin-reset-card">
            <div class="sai-admin-card-top">
              <div class="sai-admin-icon-box">
                <svg class="sai-admin-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="8.5" cy="7" r="4" />
                  <polyline points="17 11 19 13 23 9" />
                </svg>
              </div>
              <div class="sai-admin-top-text">
                <h4 class="sai-admin-top-title">Administrator Credentials (Super Admin Override)</h4>
                <p class="sai-admin-top-desc">
                  Reset the principal or admin credentials directly for this institution without affecting existing student records.
                </p>
              </div>
            </div>

            <div class="sai-admin-fields-wrap">
              <div class="sai-modal-grid">
                <div class="sai-modal-field">
                  <label class="sai-modal-label">Admin Username</label>
                  <input
                    v-model="editAdminUsername"
                    type="text"
                    class="sai-modal-input"
                    placeholder="e.g. admin_hodan"
                    autocomplete="off"
                  />
                </div>
                <div class="sai-modal-field">
                  <label class="sai-modal-label">Admin Email</label>
                  <input
                    v-model="editAdminEmail"
                    type="email"
                    class="sai-modal-input"
                    placeholder="admin@hodan.edu.so"
                  />
                </div>
              </div>

              <!-- Reset Password Input with Generate Button -->
              <div class="sai-modal-field">
                <div class="flex items-center justify-between mb-1">
                  <label class="sai-modal-label font-bold text-slate-800">
                    Beddel Furaha Sirta ah (New Password)
                  </label>
                  <button
                    type="button"
                    class="sai-btn-generate-pass"
                    @click="generateRandomPassword"
                  >
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                    </svg>
                    <span>Generate Strong Password</span>
                  </button>
                </div>

                <div class="sai-input-icon-wrap">
                  <svg class="sai-input-prefix-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0110 0v4" />
                  </svg>
                  <input
                    v-model="resetPasswordInput"
                    :type="showResetPassword ? 'text' : 'password'"
                    class="sai-modal-input sai-icon-padded sai-pass-input"
                    placeholder="Leave blank to keep existing password"
                    autocomplete="new-password"
                  />
                  <button
                    type="button"
                    class="sai-toggle-pass-btn"
                    @click="showResetPassword = !showResetPassword"
                    :title="showResetPassword ? 'Hide password' : 'Show password'"
                  >
                    <svg v-if="!showResetPassword" class="w-4 h-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="w-4 h-4 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="sai-modal-footer">
          <button class="sai-btn-cancel" :disabled="isEditing" @click="editModalOpen = false">
            Cancel
          </button>
          <button class="sai-btn-save" :disabled="isEditing" @click="saveEdit">
            <span v-if="isEditing">Saving Changes...</span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Hardened High-Security Deletion Modal -->
    <div
      v-if="deleteModalOpen && deletingInst"
      class="sai-modal-backdrop"
      @click.self="closeDeleteModal"
    >
      <div class="sai-modal sai-delete-modal">
        <!-- Danger Warning Header -->
        <div class="sai-delete-header">
          <div class="sai-danger-icon-wrap">
            <svg class="sai-danger-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <div class="sai-delete-header-text">
            <h3 class="sai-delete-title">Delete Institution (Irreversible Action)</h3>
            <p class="sai-delete-subtitle">This action permanently deletes this institution workspace.</p>
          </div>
          <button class="sai-modal-close" :disabled="isDeleting" @click="closeDeleteModal">✕</button>
        </div>

        <div class="sai-modal-body">
          <!-- Target Institution Summary Card -->
          <div class="sai-delete-target-card">
            <div class="sai-target-avatar">
              <img v-if="deletingInst.logo_url" :src="deletingInst.logo_url" alt="" class="w-full h-full object-cover rounded-full" />
              <span v-else>{{ deletingInst.name.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="sai-target-info">
              <div class="sai-target-name">{{ deletingInst.name }}</div>
              <div class="sai-target-meta">
                <span class="sai-target-code">{{ deletingInst.code }}</span>
                <span>•</span>
                <span>{{ deletingInst.type }}</span>
                <span>•</span>
                <span>{{ deletingInst.city || 'Mogadishu' }}</span>
              </div>
            </div>
          </div>

          <div v-if="deleteError" class="sai-alert-error">
            <svg class="w-4 h-4 text-red-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <span>{{ deleteError }}</span>
          </div>

          <!-- Confirmation Checkbox -->
          <div class="sai-delete-check-box">
            <label class="sai-checkbox-label">
              <input
                v-model="isAcknowledged"
                type="checkbox"
                class="sai-checkbox"
                :disabled="isDeleting"
              />
              <span class="sai-checkbox-text">
                I understand this action will permanently remove this institution, its configurations, and records.
              </span>
            </label>
          </div>

          <!-- Code Typing Verification Input -->
          <div class="sai-delete-confirm-box">
            <label class="sai-input-prompt">
              To proceed, please type the institution code
              <strong class="sai-highlight-code">{{ deletingInst.code }}</strong> below:
            </label>
            <div class="sai-code-input-wrap">
              <input
                v-model="confirmCodeInput"
                type="text"
                class="sai-confirm-input"
                :class="{
                  'input-matched': canConfirmDelete,
                  'input-mismatched': confirmCodeInput && !canConfirmDelete
                }"
                :placeholder="`Type ${deletingInst.code} to confirm`"
                :disabled="isDeleting"
                autocomplete="off"
                spellcheck="false"
              />
              <span v-if="canConfirmDelete" class="sai-code-match-badge">
                ✓ Code matches
              </span>
            </div>
          </div>
        </div>

        <!-- Deletion Footer Actions -->
        <div class="sai-modal-footer sai-delete-footer">
          <button
            class="sai-btn-cancel"
            :disabled="isDeleting"
            @click="closeDeleteModal"
          >
            Cancel
          </button>
          <button
            class="sai-btn-danger-confirm"
            :disabled="!canConfirmDelete || isDeleting"
            @click="executeDelete"
          >
            <svg class="sai-btn-trash-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span v-if="isDeleting">Deleting Institution...</span>
            <span v-else>Confirm Permanent Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sai-page-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.sai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.sai-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
  letter-spacing: -0.02em;
}

.sai-sub {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.sai-btn-add {
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

.sai-btn-add svg {
  width: 18px;
  height: 18px;
  stroke: #ffffff;
  flex-shrink: 0;
}

.sai-btn-add:hover {
  background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(255, 101, 0, 0.45);
}

/* Stats Grid */
.sai-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.sai-stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.15rem 1.35rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sai-stat-icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-stat-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  display: block;
}

.sai-stat-val {
  font-size: 1.5rem;
  font-weight: 800;
  color: #061737;
  line-height: 1.2;
}

/* Filter Row */
.sai-filters-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 0.85rem 1.15rem;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.sai-search-wrap {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0 0.85rem;
  height: 42px;
  width: 100%;
  max-width: 440px;
  gap: 0.65rem;
  transition: all 0.15s ease;
  position: relative;
}

.sai-search-wrap:focus-within {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sai-search-icon {
  width: 17px;
  height: 17px;
  color: #94a3b8;
  stroke: #94a3b8;
  flex-shrink: 0;
}

.sai-search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  width: 100%;
  padding: 0;
}

.sai-clear-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.2rem;
  font-size: 0.8rem;
}

.sai-filter-selects {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.sai-select {
  padding: 0.45rem 0.85rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.82rem;
  color: #334155;
  background: #f8fafc;
  outline: none;
  cursor: pointer;
  height: 40px;
  transition: border-color 0.15s;
}

.sai-select:focus {
  border-color: #ff6500;
}

.sai-badge-count {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  white-space: nowrap;
}

.sai-badge-count span {
  color: #061737;
  font-weight: 800;
}

/* Card & Table */
.sai-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sai-table-wrap {
  overflow-x: auto;
}

.sai-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.sai-table th {
  padding: 0.85rem 1.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  letter-spacing: 0.04em;
}

.sai-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sai-table tr:hover td {
  background: #fbfcfe;
}

.sai-code-badge {
  display: inline-block;
  font-family: monospace;
  font-weight: 700;
  font-size: 0.78rem;
  background: #f1f5f9;
  color: #061737;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.sai-inst-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sai-inst-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #061737;
  flex-shrink: 0;
  overflow: hidden;
}

.sai-inst-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.88rem;
}

.sai-inst-email {
  font-size: 0.75rem;
  color: #64748b;
}

.sai-type-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
}

.badge-school {
  background: #eff6ff;
  color: #1e40af;
}

.badge-academy {
  background: #fff7ed;
  color: #c2410c;
}

.sai-sub-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1e3a8a;
  background: #eff6ff;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.sai-status-badge {
  display: inline-block;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-active {
  background: #ecfdf5;
  color: #047857;
}

.status-suspended {
  background: #fef2f2;
  color: #b91c1c;
}

.status-pending {
  background: #fffbeb;
  color: #b45309;
}

.sai-actions-group {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.45rem;
}

.sai-btn-open {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #061737;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  height: 34px;
  padding: 0 0.85rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.sai-btn-open:hover {
  background: #ff6500;
}

.sai-btn-action {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  color: #475569;
  padding: 0;
}

.sai-btn-action:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.sai-btn-delete {
  background: #fef2f2;
  border-color: #fee2e2;
  color: #ef4444;
}

.sai-btn-delete:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}

.sai-btn-trash-icon {
  width: 16px;
  height: 16px;
  stroke: #ef4444;
}

/* Mobile Cards */
.sai-mobile-cards {
  display: none;
  flex-direction: column;
  gap: 1rem;
}

.sai-inst-card-mobile {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.sai-mcard-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sai-mcard-title-box {
  flex: 1;
  min-width: 0;
}

.sai-mcard-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem 1rem;
  padding: 0.65rem 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
}

.sai-minfo-item {
  display: flex;
  flex-direction: column;
}

.sai-minfo-label {
  font-size: 0.7rem;
  color: #94a3b8;
}

.sai-minfo-val {
  font-size: 0.8rem;
  color: #1e293b;
}

.sai-mcard-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sai-mcard-sub-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modals Shared */
.sai-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 23, 55, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
  overflow-y: auto;
}

.sai-modal {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.sai-modal-header {
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sai-modal-icon-badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sai-modal-close {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.sai-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  overflow-y: auto;
}

.sai-modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.sai-modal-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sai-modal-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}

.sai-modal-input {
  padding: 0.6rem 0.85rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
  background: #ffffff;
}

.sai-modal-input:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sai-form-section {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.sai-form-section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid #f1f5f9;
}

.sai-section-icon {
  width: 17px;
  height: 17px;
  stroke: #ff6500;
  flex-shrink: 0;
}

.sai-form-section-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.sai-alert-success {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
}

.sai-alert-error {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
}

/* Administrator Card & Credentials Reset */
.sai-admin-reset-card {
  background: linear-gradient(135deg, #f0f7ff 0%, #f8fafc 100%);
  border: 1px solid #bfdbfe;
  border-radius: 14px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sai-admin-card-top {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.sai-admin-icon-box {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-admin-icon-svg {
  width: 18px;
  height: 18px;
  stroke: #1d4ed8;
}

.sai-admin-top-text {
  flex: 1;
}

.sai-admin-top-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #1e3a8a;
  margin: 0;
}

.sai-admin-top-desc {
  font-size: 0.76rem;
  color: #475569;
  margin: 0.2rem 0 0;
  line-height: 1.35;
}

.sai-admin-fields-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.sai-btn-generate-pass {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.sai-btn-generate-pass:hover {
  background: #dbeafe;
}

.sai-input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.sai-input-prefix-icon {
  position: absolute;
  left: 0.85rem;
  width: 17px;
  height: 17px;
  stroke: #94a3b8;
  pointer-events: none;
}

.sai-icon-padded {
  padding-left: 2.35rem;
}

.sai-pass-input {
  width: 100%;
  padding-right: 2.5rem;
}

.sai-toggle-pass-btn {
  position: absolute;
  right: 0.65rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sai-modal-footer {
  padding: 1.15rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sai-btn-cancel {
  padding: 0.6rem 1.25rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}

.sai-btn-cancel:hover {
  background: #f1f5f9;
}

.sai-btn-save {
  padding: 0.6rem 1.5rem;
  border: none;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(255, 101, 0, 0.35);
  transition: all 0.15s;
}

.sai-btn-save:hover:not(:disabled) {
  background: #ea580c;
  transform: translateY(-1px);
}

/* Deletion Modal */
.sai-delete-modal {
  max-width: 520px;
  border: 1px solid #fee2e2;
}

.sai-delete-header {
  padding: 1.25rem 1.5rem;
  background: #fff5f5;
  border-bottom: 1px solid #fee2e2;
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.sai-danger-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #fee2e2;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-danger-svg {
  width: 22px;
  height: 22px;
  stroke: #dc2626;
}

.sai-delete-header-text {
  flex: 1;
}

.sai-delete-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: #991b1b;
  margin: 0;
}

.sai-delete-subtitle {
  font-size: 0.75rem;
  color: #b91c1c;
  margin: 0.15rem 0 0;
}

.sai-delete-target-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.85rem 1rem;
}

.sai-target-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #0f172a;
}

.sai-target-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}

.sai-target-meta {
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: 0.15rem;
}

.sai-target-code {
  font-family: monospace;
  font-weight: 700;
  color: #061737;
}

.sai-delete-check-box {
  background: #fff8f8;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 0.85rem;
}

.sai-checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  cursor: pointer;
}

.sai-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #dc2626;
  margin-top: 0.15rem;
  cursor: pointer;
  flex-shrink: 0;
}

.sai-checkbox-text {
  font-size: 0.82rem;
  color: #7f1d1d;
  line-height: 1.4;
  font-weight: 500;
}

.sai-delete-confirm-box {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.sai-input-prompt {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
}

.sai-highlight-code {
  font-family: monospace;
  background: #fee2e2;
  color: #b91c1c;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}

.sai-confirm-input {
  padding: 0.65rem 0.85rem;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.88rem;
  font-family: monospace;
  font-weight: 700;
  color: #0f172a;
  outline: none;
}

.sai-confirm-input:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15);
}

.sai-confirm-input.input-matched {
  border-color: #16a34a;
  background: #f0fdf4;
}

.sai-code-match-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #16a34a;
}

.sai-delete-footer {
  background: #fff5f5;
  border-top: 1px solid #fee2e2;
}

.sai-btn-danger-confirm {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.65rem 1.35rem;
  border: none;
  background: #dc2626;
  color: #ffffff;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.35);
}

.sai-btn-danger-confirm:hover:not(:disabled) {
  background: #b91c1c;
  transform: translateY(-1px);
}

.sai-btn-danger-confirm:disabled {
  background: #fca5a5;
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.sai-btn-trash-svg {
  width: 16px;
  height: 16px;
  stroke: #ffffff;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 900px) {
  .sai-stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sai-desktop-table {
    display: none;
  }

  .sai-mobile-cards {
    display: flex;
  }

  .sai-filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .sai-search-wrap {
    max-width: 100%;
  }

  .sai-filter-selects {
    width: 100%;
    justify-content: space-between;
  }

  .sai-select {
    flex: 1;
  }

  .sai-modal-grid {
    grid-template-columns: 1fr;
  }

  .sai-btn-add {
    width: 100%;
    justify-content: center;
  }
}
</style>
