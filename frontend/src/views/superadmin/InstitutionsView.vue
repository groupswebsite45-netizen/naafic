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

function handleInstitutionCreated() {
  isModalOpen.value = false;
  loadInstitutions();
}

function formatDate(dStr?: string | null) {
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
  loadInstitutions();
});
</script>

<template>
  <div class="sai-page-container">
    <!-- Header -->
    <div class="sai-header">
      <div>
        <h1 class="sai-title">Institution Management</h1>
        <p class="sai-sub">Manage and monitor all schools, colleges, and academies registered on Somroyal EMS.</p>
      </div>

      <button class="sai-btn-add" @click="isModalOpen = true">
        <svg class="w-5 h-5 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Register New Institution</span>
      </button>
    </div>

    <!-- Filters Row -->
    <div class="sai-filters-row">
      <div class="sai-search-wrap">
        <svg class="sai-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="searchQuery"
          @input="handleSearchInput"
          type="text"
          placeholder="Search by institution name, code, contact, or city..."
          class="sai-search-input"
        />
        <button
          v-if="searchQuery"
          @click="searchQuery = ''; handleSearchInput();"
          class="sai-clear-btn"
          title="Clear search"
        >
          ×
        </button>
      </div>

      <div class="sai-selects-group">
        <select v-model="selectedType" class="sai-select">
          <option value="">All Types</option>
          <option value="Primary School">Primary School</option>
          <option value="Secondary School">Secondary School</option>
          <option value="Primary & Secondary School">Primary & Secondary School</option>
          <option value="Academy">Academy</option>
          <option value="College">College</option>
          <option value="Institute">Institute</option>
        </select>

        <select v-model="selectedStatus" class="sai-select">
          <option value="">All Statuses</option>
          <option value="ACTIVE">Active</option>
          <option value="SUSPENDED">Suspended</option>
          <option value="PENDING">Pending</option>
        </select>

        <span class="sai-count-pill">
          {{ institutions.length }} {{ institutions.length === 1 ? 'institution' : 'institutions' }}
        </span>
      </div>
    </div>

    <!-- Institutions Table Card -->
    <div class="sai-card">
      <div class="sai-table-wrap">
        <table class="sai-table">
          <thead>
            <tr>
              <th>ID & Code</th>
              <th>Institution Details</th>
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
                <div class="font-medium text-slate-800">{{ inst.contact_person || 'N/A' }}</div>
                <div class="text-xs text-slate-500">{{ inst.phone || '' }}</div>
              </td>
              <td>
                <div class="text-slate-700">{{ inst.city || inst.region || 'Mogadishu' }}</div>
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
                    :class="inst.status === 'ACTIVE' ? 'text-red-500 hover:bg-red-50' : 'text-emerald-500 hover:bg-emerald-50'"
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
                No educational institutions match your search criteria.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal with Administrator Account Reset -->
    <div v-if="editModalOpen && editingInst" class="sai-modal-backdrop" @click.self="editModalOpen = false">
      <div class="sai-modal sai-edit-modal">
        <!-- Modal Header -->
        <div class="sai-modal-header sai-edit-header">
          <div class="sai-edit-header-title-wrap">
            <div class="sai-edit-badge">{{ editingInst.code }}</div>
            <div>
              <h3 class="sai-modal-title">Wax-ka-beddelka Machadka & Furayaasha</h3>
              <p class="sai-edit-sub">Cusboonaysii xogta {{ editingInst.name }} ama dib-u-deji akoonka maamulaha.</p>
            </div>
          </div>
          <button class="sai-modal-close" @click="editModalOpen = false">✕</button>
        </div>

        <div class="sai-modal-body sai-edit-body">
          <!-- Notification Banners -->
          <div v-if="editSuccessMsg" class="sai-edit-alert-success">
            <svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>{{ editSuccessMsg }}</span>
          </div>

          <div v-if="editErrorMsg" class="sai-edit-alert-error">
            <svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <span>{{ editErrorMsg }}</span>
          </div>

          <!-- Section 1: Institution Details -->
          <div class="sai-form-section">
            <div class="sai-form-section-header">
              <svg class="sai-section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <h4 class="sai-form-section-title">1. Macluumaadka Guud ee Machadka (Institution Info)</h4>
            </div>

            <div class="sai-modal-field">
              <label class="sai-modal-label">Magaca Machadka (Institution Name) <span class="text-red-500">*</span></label>
              <input v-model="editingInst.name" type="text" class="sai-modal-input" placeholder="e.g. Garasale Primary & Secondary School" />
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Nooca Machadka (Type)</label>
                <select v-model="editingInst.type" class="sai-modal-select">
                  <option value="School">School</option>
                  <option value="Primary School">Primary School</option>
                  <option value="Secondary School">Secondary School</option>
                  <option value="Academy">Academy</option>
                  <option value="College">College</option>
                  <option value="Institute">Institute</option>
                  <option value="University">University</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div class="sai-modal-field">
                <label class="sai-modal-label">Xaaladda (Status)</label>
                <select v-model="editingInst.status" class="sai-modal-select">
                  <option value="ACTIVE">ACTIVE (Firfircoon)</option>
                  <option value="SUSPENDED">SUSPENDED (Hakad)</option>
                  <option value="PENDING">PENDING (Sugaya)</option>
                </select>
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Qorshaha Diiwaangelinta (Subscription Plan)</label>
                <select v-model="editingInst.subscription_plan" class="sai-modal-select">
                  <option value="Basic School">Basic School ($25/mo)</option>
                  <option value="Standard Academy">Standard Academy ($35/mo)</option>
                  <option value="Professional School">Professional School ($45/mo)</option>
                  <option value="Enterprise Institution">Enterprise Institution ($75/mo)</option>
                </select>
              </div>

              <div class="sai-modal-field">
                <label class="sai-modal-label">Magaalada (City)</label>
                <input v-model="editingInst.city" type="text" class="sai-modal-input" placeholder="e.g. Mogadishu" />
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Qofka Xiriirka (Contact Person)</label>
                <input v-model="editingInst.contact_person" type="text" class="sai-modal-input" placeholder="e.g. Mohamed Ali" />
              </div>

              <div class="sai-modal-field">
                <label class="sai-modal-label">Email-ka Machadka</label>
                <input v-model="editingInst.email" type="email" class="sai-modal-input" placeholder="e.g. info@school.edu.so" />
              </div>
            </div>

            <div class="sai-modal-grid">
              <div class="sai-modal-field">
                <label class="sai-modal-label">Telefoonka (Phone)</label>
                <input v-model="editingInst.phone" type="text" class="sai-modal-input" placeholder="e.g. +252 61 5000000" />
              </div>

              <div class="sai-modal-field">
                <label class="sai-modal-label">Cinwaanka / Xarunta (Campus Address)</label>
                <input v-model="editingInst.address" type="text" class="sai-modal-input" placeholder="e.g. Wadada Maka Al-Mukarama" />
              </div>
            </div>
          </div>

          <!-- Section 2: Administrator Credentials & Password Reset -->
          <div class="sai-admin-reset-card">
            <div class="sai-admin-card-top">
              <div class="sai-admin-icon-box">
                <svg class="sai-admin-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
              </div>
              <div class="sai-admin-top-text">
                <div class="sai-admin-top-title">2. Akoonka Maamulaha & Furaha Sirta ah (Credentials Reset)</div>
                <div class="sai-admin-top-desc">Haddii maamulaha machadka uu ilaawo username-ka ama password-ka, halkan kaga beddel oo sii kuwo cusub.</div>
              </div>
            </div>

            <div class="sai-admin-fields-wrap">
              <div class="sai-modal-grid">
                <div class="sai-modal-field">
                  <label class="sai-modal-label">
                    Magaca Isticmaalaha Maamulaha (Admin Username)
                  </label>
                  <div class="sai-input-icon-wrap">
                    <svg class="sai-input-prefix-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <input
                      v-model="editAdminUsername"
                      type="text"
                      class="sai-modal-input sai-icon-padded"
                      placeholder="e.g. admin_garasale"
                    />
                  </div>
                  <span class="sai-field-hint">Kani waa username-ka uu maamuluhu ku galo nidaamka machadka.</span>
                </div>

                <div class="sai-modal-field">
                  <label class="sai-modal-label">
                    Email-ka Maamulaha (Admin Email)
                  </label>
                  <div class="sai-input-icon-wrap">
                    <svg class="sai-input-prefix-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <input
                      v-model="editAdminEmail"
                      type="email"
                      class="sai-modal-input sai-icon-padded"
                      placeholder="e.g. admin@school.edu.so"
                    />
                  </div>
                  <span class="sai-field-hint">Email-ka rasmiga ah ee maamulaha machadka.</span>
                </div>
              </div>

              <!-- Password Reset Field -->
              <div class="sai-modal-field sai-pass-reset-field">
                <div class="sai-pass-label-row">
                  <label class="sai-modal-label font-semibold text-slate-800">
                    Furaha Cusub ee Maamulaha (New Admin Password)
                  </label>
                  <button
                    type="button"
                    class="sai-btn-generate"
                    @click="generateRandomPassword"
                    title="U samee furaha adag oo toos ah"
                  >
                    <svg class="w-3.5 h-3.5 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>Samee Furaha (Generate)</span>
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
                    placeholder="Kaga tag maran haddii aadan doonayn inaad beddesho furaha"
                    autocomplete="new-password"
                  />
                  <button
                    type="button"
                    class="sai-toggle-pass-btn"
                    @click="showResetPassword = !showResetPassword"
                    :title="showResetPassword ? 'Qari furaha' : 'Muuji furaha'"
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

                <div class="sai-pass-info-note">
                  <svg class="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <span>
                    <strong>Xusuusin:</strong> Haddii aad furaha sirta ah geliso ama riixdo <em>Generate</em>, furahan cusub ayaa isla markiiba loogu gali karaa nidaamka SMS ee machadka (Database: <code>{{ editingInst.database_name || 'sms' }}</code>).
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="sai-modal-footer">
          <button class="sai-btn-cancel" :disabled="isEditing" @click="editModalOpen = false">
            Jooji (Cancel)
          </button>
          <button class="sai-btn-save" :disabled="isEditing" @click="saveEdit">
            <span v-if="isEditing">Kaydinaya...</span>
            <span v-else>Kaydi Isbeddellada (Save Changes)</span>
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
            <h3 class="sai-delete-title">Tirtir Machadka (High Risk Action)</h3>
            <p class="sai-delete-subtitle">Tallaabadani waa mid joogto ah oo aan dib looga noqon karin</p>
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

          <!-- Red Warning Explanation Box -->
          <div class="sai-danger-alert">
            <svg class="sai-alert-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <div class="sai-alert-text">
              <strong>Digniin Adag:</strong> Tirtiridda machadkani waxay gebi ahaanba tirtiri doontaa dhammaan xogtiisa, diiwaannada subscription-ka, taariikhda lacag-bixinta, iyo marin-u-helka nidaamka SMS-ka. Xogtan dib looma soo celin karo!
            </div>
          </div>

          <!-- Server Error Message if any -->
          <div v-if="deleteError" class="sai-delete-error-msg">
            {{ deleteError }}
          </div>

          <!-- Step 1: Checkbox Acknowledgment -->
          <div class="sai-verify-step">
            <label class="sai-checkbox-label">
              <input
                type="checkbox"
                v-model="isAcknowledged"
                :disabled="isDeleting"
                class="sai-checkbox"
              />
              <span class="sai-checkbox-text">
                Waxaan si buuxda u fahamsanahay in falkani yahay <strong>mid joogto ah (permanent)</strong> oo aan dib loo soo celin karin.
              </span>
            </label>
          </div>

          <!-- Step 2: Exact Code Match Verification -->
          <div class="sai-verify-step">
            <label class="sai-input-prompt">
              Si aad u xaqiijiso tirtiridda, ku qor koodhka machadka <strong class="sai-highlight-code">{{ deletingInst.code }}</strong> sanduuqa hoose:
            </label>
            <div class="sai-code-input-wrap">
              <input
                v-model="confirmCodeInput"
                type="text"
                :disabled="isDeleting"
                :placeholder="'Ku qor: ' + deletingInst.code"
                class="sai-confirm-input"
                :class="{
                  'input-matched': confirmCodeInput.trim().toUpperCase() === deletingInst.code.trim().toUpperCase(),
                  'input-mismatched': confirmCodeInput && confirmCodeInput.trim().toUpperCase() !== deletingInst.code.trim().toUpperCase()
                }"
              />
              <span
                v-if="confirmCodeInput.trim().toUpperCase() === deletingInst.code.trim().toUpperCase()"
                class="sai-code-match-badge"
              >
                ✓ Koodhku wuu saxan yahay
              </span>
            </div>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="sai-modal-footer sai-delete-footer">
          <button
            type="button"
            class="sai-btn-cancel"
            :disabled="isDeleting"
            @click="closeDeleteModal"
          >
            Jooji (Cancel)
          </button>
          
          <button
            type="button"
            class="sai-btn-danger-confirm"
            :disabled="!canConfirmDelete || isDeleting"
            @click="executeDelete"
          >
            <svg v-if="!isDeleting" class="sai-btn-trash-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span v-if="isDeleting">Tirtiraya...</span>
            <span v-else>Xaqiiji oo Tirtir Machadka</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Register Modal -->
    <RegisterInstitutionModal
      v-if="isModalOpen"
      @close="isModalOpen = false"
      @created="handleInstitutionCreated"
    />
  </div>
</template>

<style scoped>
.sai-page-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

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
  background: #ff6500;
  color: #ffffff;
  border: none;
  font-size: 0.88rem;
  font-weight: 600;
  height: 42px;
  padding: 0 1.25rem;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(255, 101, 0, 0.25);
  transition: all 0.2s;
  white-space: nowrap;
}

.sai-btn-add svg {
  width: 18px;
  height: 18px;
  stroke: #ffffff;
  flex-shrink: 0;
}

.sai-btn-add:hover {
  background: #e55a00;
  transform: translateY(-1px);
}

.sai-filters-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.sai-search-wrap {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0 0.85rem;
  height: 40px;
  width: 100%;
  max-width: 440px;
  gap: 0.65rem;
  transition: all 0.15s ease;
  position: relative;
}

.sai-search-wrap:focus-within {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.1);
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
  background: #e2e8f0;
  color: #64748b;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  border: none;
  padding: 0;
  flex-shrink: 0;
}

.sai-clear-btn:hover {
  background: #cbd5e1;
  color: #1e293b;
}

.sai-selects-group {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.sai-select {
  height: 40px;
  padding: 0 0.85rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.85rem;
  font-weight: 500;
  color: #334155;
  outline: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.sai-select:focus {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.1);
}

.sai-count-pill {
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  white-space: nowrap;
}

.sai-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  overflow: hidden;
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
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.sai-table td {
  padding: 1rem 1.25rem;
  font-size: 0.85rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.sai-table tr:hover td {
  background: #fbfcfe;
}

.sai-code-badge {
  font-family: monospace;
  font-weight: 700;
  color: #061737;
  background: #f1f5f9;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  font-size: 0.78rem;
}

.sai-inst-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sai-inst-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #061737;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-inst-name {
  font-weight: 700;
  color: #0f172a;
}

.sai-inst-email {
  font-size: 0.75rem;
  color: #64748b;
}

.sai-type-badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-school {
  background: #eff6ff;
  color: #2563eb;
}

.badge-academy {
  background: #fff7ed;
  color: #ea580c;
}

.sai-sub-badge {
  font-size: 0.78rem;
  font-weight: 600;
  color: #061737;
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
  color: #059669;
}

.status-pending {
  background: #fffbeb;
  color: #d97706;
}

.status-suspended {
  background: #fef2f2;
  color: #dc2626;
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
  gap: 0.35rem;
  background: #061737;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 600;
  height: 32px;
  padding: 0 0.75rem;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.sai-btn-open:hover {
  background: #ff6500;
}

.sai-btn-open svg {
  width: 13px;
  height: 13px;
  stroke: #ffffff;
  flex-shrink: 0;
}

.sai-btn-action {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
  color: #64748b;
  padding: 0;
}

.sai-btn-action svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.sai-btn-action:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

/* Edit Modal */
.sai-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 23, 55, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1.5rem;
}

.sai-modal {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: 580px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.sai-modal-header {
  padding: 1.25rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
}

.sai-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  padding: 0.55rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
}

.sai-modal-select {
  padding: 0.55rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  background: #ffffff;
  outline: none;
}

.sai-modal-select:focus,
.sai-modal-input:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

/* Edit Modal Specialized Styles */
.sai-edit-modal {
  max-width: 660px;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

.sai-edit-header {
  padding: 1.1rem 1.5rem;
}

.sai-edit-header-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sai-edit-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.25rem 0.55rem;
  background: #061737;
  color: #ffffff;
  border-radius: 6px;
  letter-spacing: 0.04em;
}

.sai-edit-sub {
  font-size: 0.78rem;
  color: #64748b;
  margin: 0.15rem 0 0;
}

.sai-edit-body {
  max-height: calc(90vh - 145px);
  overflow-y: auto;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.sai-edit-alert-success {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
}

.sai-edit-alert-error {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 500;
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

/* Administrator Card & Credentials Reset */
.sai-admin-reset-card {
  background: linear-gradient(135deg, #f0f7ff 0%, #f8fafc 100%);
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.04);
}

.sai-admin-card-top {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.sai-admin-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 9px;
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
}

.sai-admin-top-desc {
  font-size: 0.77rem;
  color: #475569;
  margin-top: 0.15rem;
  line-height: 1.35;
}

.sai-admin-fields-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.sai-input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.sai-input-prefix-icon {
  position: absolute;
  left: 0.75rem;
  width: 16px;
  height: 16px;
  stroke: #94a3b8;
  pointer-events: none;
}

.sai-icon-padded {
  padding-left: 2.25rem !important;
  width: 100%;
}

.sai-field-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.sai-pass-reset-field {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 0.85rem;
}

.sai-pass-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.2rem;
}

.sai-btn-generate {
  display: inline-flex;
  align-items: center;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
  font-size: 0.74rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.sai-btn-generate:hover {
  background: #dbeafe;
  border-color: #93c5fd;
}

.sai-pass-input {
  padding-right: 2.5rem !important;
}

.sai-toggle-pass-btn {
  position: absolute;
  right: 0.65rem;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
}

.sai-pass-info-note {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  font-size: 0.74rem;
  color: #475569;
  line-height: 1.35;
  margin-top: 0.35rem;
}

.sai-pass-info-note code {
  background: #f1f5f9;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-weight: 600;
  color: #ff6500;
}

.sai-modal-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.sai-btn-cancel {
  padding: 0.55rem 1rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.sai-btn-save {
  padding: 0.55rem 1.25rem;
  border: none;
  background: #ff6500;
  color: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

/* Table Action Delete Button */
.sai-btn-delete {
  background: #fef2f2;
  border-color: #fee2e2;
  color: #ef4444;
}

.sai-btn-delete:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
  transform: translateY(-1px);
}

.sai-btn-trash-icon {
  width: 15px;
  height: 15px;
  stroke: #ef4444;
  flex-shrink: 0;
  transition: stroke 0.15s;
}

.sai-btn-delete:hover .sai-btn-trash-icon {
  stroke: #dc2626;
}

/* Hardened Deletion Modal */
.sai-delete-modal {
  max-width: 540px;
  border-radius: 16px;
  border: 1px solid #fee2e2;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.22);
  overflow: hidden;
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
  width: 42px;
  height: 42px;
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
  flex-shrink: 0;
}

.sai-delete-header-text {
  flex: 1;
  text-align: left;
}

.sai-delete-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #991b1b;
  margin: 0;
}

.sai-delete-subtitle {
  font-size: 0.75rem;
  color: #b91c1c;
  margin: 0.15rem 0 0;
}

/* Target institution snapshot card */
.sai-delete-target-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
}

.sai-target-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #061737;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sai-target-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.sai-target-name {
  font-size: 0.92rem;
  font-weight: 700;
  color: #0f172a;
}

.sai-target-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.15rem;
}

.sai-target-code {
  font-family: monospace;
  font-weight: 700;
  color: #061737;
  background: #e2e8f0;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

/* Danger alert explanation */
.sai-danger-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  background: #fef2f2;
  border: 1px solid #fee2e2;
  border-radius: 10px;
  padding: 0.75rem 0.85rem;
}

.sai-alert-icon {
  width: 18px;
  height: 18px;
  stroke: #dc2626;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.sai-alert-text {
  font-size: 0.8rem;
  color: #991b1b;
  line-height: 1.45;
  text-align: left;
}

.sai-delete-error-msg {
  padding: 0.65rem 0.85rem;
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  color: #b91c1c;
  font-size: 0.82rem;
  font-weight: 600;
  text-align: left;
}

/* Verification steps */
.sai-verify-step {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  text-align: left;
}

.sai-checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  cursor: pointer;
  user-select: none;
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
  color: #334155;
  line-height: 1.4;
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
  font-weight: 700;
}

.sai-code-input-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.sai-confirm-input {
  padding: 0.6rem 0.85rem;
  border: 1.5px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.88rem;
  font-family: monospace;
  font-weight: 600;
  color: #0f172a;
  outline: none;
  transition: all 0.15s ease;
  background: #ffffff;
}

.sai-confirm-input:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.sai-confirm-input.input-matched {
  border-color: #16a34a;
  background: #f0fdf4;
}

.sai-confirm-input.input-mismatched {
  border-color: #ef4444;
}

.sai-code-match-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #16a34a;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Modal danger button */
.sai-delete-footer {
  background: #fff5f5;
  border-top: 1px solid #fee2e2;
}

.sai-btn-danger-confirm {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.6rem 1.25rem;
  border: none;
  background: #dc2626;
  color: #ffffff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(220, 38, 38, 0.3);
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
  transform: none;
}

.sai-btn-trash-svg {
  width: 15px;
  height: 15px;
  stroke: #ffffff;
  flex-shrink: 0;
}
</style>
