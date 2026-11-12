<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { inquiryService } from '../../services/inquiryService';
import { Inquiry, InquiryStats, InquiryStatus, InquiryPriority } from '../../types/inquiry';

// State
const inquiries = ref<Inquiry[]>([]);
const stats = ref<InquiryStats>({
  total: 0,
  unread: 0,
  in_review: 0,
  contacted: 0,
  converted: 0,
  today: 0,
});
const selectedInquiry = ref<Inquiry | null>(null);
const isLoading = ref(true);
const isRefreshing = ref(false);
const searchQuery = ref('');
const activeFilter = ref<'ALL' | InquiryStatus>('ALL');
const priorityFilter = ref<string>('ALL');

// Mobile view state: 'list' | 'detail'
const mobileActivePane = ref<'list' | 'detail'>('list');

// Update / CRM action state
const isUpdating = ref(false);
const adminNotesInput = ref('');
const contactedByInput = ref('');
const notesSavedToast = ref(false);

// Conversion modal state
const isConvertModalOpen = ref(false);
const isConverting = ref(false);
const convertInstitutionType = ref('School');
const convertRegion = ref('Banaadir');
const convertCity = ref('Mogadishu');
const convertPlan = ref('Professional School');
const convertAdminUsername = ref('');
const conversionResult = ref<any | null>(null);
const conversionError = ref<string | null>(null);

// Delete state
const isDeleting = ref(false);

// Fetch data
async function loadInquiries(preserveSelection = true) {
  isRefreshing.value = true;
  try {
    const [listData, statsData] = await Promise.all([
      inquiryService.getInquiries({
        status: activeFilter.value === 'ALL' ? undefined : activeFilter.value,
        priority: priorityFilter.value === 'ALL' ? undefined : priorityFilter.value,
        search: searchQuery.value ? searchQuery.value.trim() : undefined,
      }),
      inquiryService.getInquiryStats(),
    ]);

    inquiries.value = listData.items;
    stats.value = statsData;

    if (preserveSelection && selectedInquiry.value) {
      const refreshed = inquiries.value.find((i) => i.id === selectedInquiry.value?.id);
      if (refreshed) {
        selectedInquiry.value = refreshed;
      }
    } else if (inquiries.value.length > 0 && !selectedInquiry.value) {
      selectInquiry(inquiries.value[0], false);
    }
  } catch (err) {
    console.error('Failed to load inquiries:', err);
  } finally {
    isLoading.value = false;
    isRefreshing.value = false;
  }
}

async function selectInquiry(inquiry: Inquiry, switchMobilePane = true) {
  selectedInquiry.value = inquiry;
  adminNotesInput.value = inquiry.admin_notes || '';
  contactedByInput.value = inquiry.contacted_by || '';
  conversionResult.value = null;
  conversionError.value = null;

  if (switchMobilePane) {
    mobileActivePane.value = 'detail';
  }

  // If status is UNREAD, automatically update to READ
  if (inquiry.status === 'UNREAD') {
    try {
      const updated = await inquiryService.getInquiry(inquiry.id);
      inquiry.status = updated.status;
      if (stats.value.unread > 0) stats.value.unread--;
    } catch (e) {
      // ignore
    }
  }
}

async function updateStatus(newStatus: InquiryStatus) {
  if (!selectedInquiry.value) return;
  isUpdating.value = true;
  try {
    const updated = await inquiryService.updateInquiry(selectedInquiry.value.id, {
      status: newStatus,
    });
    selectedInquiry.value.status = updated.status;
    const idx = inquiries.value.findIndex((i) => i.id === updated.id);
    if (idx !== -1) inquiries.value[idx].status = updated.status;
    const updatedStats = await inquiryService.getInquiryStats();
    stats.value = updatedStats;
  } catch (err) {
    console.error('Failed to update status:', err);
  } finally {
    isUpdating.value = false;
  }
}

async function updatePriority(newPriority: InquiryPriority) {
  if (!selectedInquiry.value) return;
  isUpdating.value = true;
  try {
    const updated = await inquiryService.updateInquiry(selectedInquiry.value.id, {
      priority: newPriority,
    });
    selectedInquiry.value.priority = updated.priority;
    const idx = inquiries.value.findIndex((i) => i.id === updated.id);
    if (idx !== -1) inquiries.value[idx].priority = updated.priority;
  } catch (err) {
    console.error('Failed to update priority:', err);
  } finally {
    isUpdating.value = false;
  }
}

async function saveAdminNotes() {
  if (!selectedInquiry.value) return;
  isUpdating.value = true;
  try {
    const updated = await inquiryService.updateInquiry(selectedInquiry.value.id, {
      admin_notes: adminNotesInput.value,
      contacted_by: contactedByInput.value,
    });
    selectedInquiry.value.admin_notes = updated.admin_notes;
    selectedInquiry.value.contacted_by = updated.contacted_by;
    notesSavedToast.value = true;
    setTimeout(() => {
      notesSavedToast.value = false;
    }, 3000);
  } catch (err) {
    console.error('Failed to save notes:', err);
  } finally {
    isUpdating.value = false;
  }
}

function openConvertModal() {
  if (!selectedInquiry.value) return;
  convertPlan.value = selectedInquiry.value.plan || 'Professional School';
  convertAdminUsername.value = `admin_${selectedInquiry.value.school_name
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .slice(0, 10)}`;
  conversionResult.value = null;
  conversionError.value = null;
  isConvertModalOpen.value = true;
}

async function executeConversion() {
  if (!selectedInquiry.value || isConverting.value) return;
  isConverting.value = true;
  conversionError.value = null;

  try {
    const res = await inquiryService.convertInquiry(selectedInquiry.value.id, {
      institution_type: convertInstitutionType.value,
      region: convertRegion.value,
      city: convertCity.value,
      subscription_plan: convertPlan.value,
      admin_username: convertAdminUsername.value || undefined,
    });
    conversionResult.value = res;
    selectedInquiry.value.status = 'CONVERTED';
    selectedInquiry.value.converted_institution_id = res.institution_id;
    const idx = inquiries.value.findIndex((i) => i.id === selectedInquiry.value?.id);
    if (idx !== -1) {
      inquiries.value[idx].status = 'CONVERTED';
      inquiries.value[idx].converted_institution_id = res.institution_id;
    }
    const updatedStats = await inquiryService.getInquiryStats();
    stats.value = updatedStats;
  } catch (err: any) {
    console.error('Conversion failed:', err);
    conversionError.value = err?.response?.data?.detail || 'Failed to convert inquiry to institution.';
  } finally {
    isConverting.value = false;
  }
}

async function deleteCurrentInquiry() {
  if (!selectedInquiry.value) return;
  if (!confirm(`Are you sure you want to delete inquiry #${selectedInquiry.value.id} from ${selectedInquiry.value.school_name}?`)) {
    return;
  }

  isDeleting.value = true;
  try {
    await inquiryService.deleteInquiry(selectedInquiry.value.id);
    inquiries.value = inquiries.value.filter((i) => i.id !== selectedInquiry.value?.id);
    selectedInquiry.value = inquiries.value.length > 0 ? inquiries.value[0] : null;
    mobileActivePane.value = 'list';
    const updatedStats = await inquiryService.getInquiryStats();
    stats.value = updatedStats;
  } catch (err) {
    console.error('Failed to delete inquiry:', err);
  } finally {
    isDeleting.value = false;
  }
}

// Helpers
function getInitials(name: string): string {
  if (!name) return 'IN';
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
}

function formatDate(isoStr: string): string {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatRelativeTime(isoStr: string): string {
  if (!isoStr) return '';
  const diffMs = Date.now() - new Date(isoStr).getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHour / 24);

  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return new Date(isoStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getWhatsAppUrl(phone: string, schoolName: string, name: string): string {
  const cleanPhone = phone.replace(/[^0-9]/g, '');
  const msg = encodeURIComponent(
    `Asc ${name}, waxaan kaala soo xiriiray Somroyal Education Solutions oo ku saabsan codsigii aad noo soo dirtay ee ${schoolName}. Ma helaysaa wakhti aan kuugu soo bandhigno demo?`
  );
  return `https://wa.me/${cleanPhone}?text=${msg}`;
}

function copyToClipboard(text: string, label: string) {
  navigator.clipboard.writeText(text);
  alert(`${label} copied to clipboard!`);
}

// Watchers
watch([activeFilter, priorityFilter], () => {
  loadInquiries(false);
});

let searchTimeout: any = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadInquiries(false);
  }, 350);
});

onMounted(() => {
  loadInquiries(false);
});
</script>

<template>
  <div class="inbox-page-wrapper">
    <!-- Header & KPI Metrics -->
    <header class="inbox-header">
      <div class="header-main-info">
        <div class="header-title-group">
          <div class="header-badge-tag">
            <span class="pulse-indicator"></span>
            Super Admin CRM Inbox
          </div>
          <h1 class="header-title">Institutional Inquiries & Leads</h1>
          <p class="header-subtitle">
            Manage prospective schools, consultation requests, and licensing inquiries submitted from the public landing page.
          </p>
        </div>

        <div class="header-actions">
          <button
            class="btn-refresh"
            :disabled="isRefreshing"
            @click="loadInquiries(true)"
            title="Refresh Inquiries"
          >
            <svg
              class="w-4 h-4"
              :class="{ 'animate-spin': isRefreshing }"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            <span>{{ isRefreshing ? 'Refreshing...' : 'Refresh' }}</span>
          </button>
        </div>
      </div>

      <!-- KPI Metrics Strip -->
      <div class="kpi-grid">
        <div class="kpi-card" :class="{ 'active-card': activeFilter === 'ALL' }" @click="activeFilter = 'ALL'">
          <div class="kpi-icon-wrap bg-blue-50 text-blue-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">{{ stats.total }}</span>
            <span class="kpi-label">Total Inquiries</span>
          </div>
        </div>

        <div class="kpi-card" :class="{ 'active-card': activeFilter === 'UNREAD' }" @click="activeFilter = 'UNREAD'">
          <div class="kpi-icon-wrap bg-orange-50 text-orange-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value text-orange-600">{{ stats.unread }}</span>
            <span class="kpi-label">Unread Leads</span>
          </div>
          <span v-if="stats.unread > 0" class="badge-unread-chip">{{ stats.unread }} New</span>
        </div>

        <div class="kpi-card" :class="{ 'active-card': activeFilter === 'IN_REVIEW' }" @click="activeFilter = 'IN_REVIEW'">
          <div class="kpi-icon-wrap bg-purple-50 text-purple-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">{{ stats.in_review }}</span>
            <span class="kpi-label">In Review</span>
          </div>
        </div>

        <div class="kpi-card" :class="{ 'active-card': activeFilter === 'CONTACTED' }" @click="activeFilter = 'CONTACTED'">
          <div class="kpi-icon-wrap bg-indigo-50 text-indigo-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">{{ stats.contacted }}</span>
            <span class="kpi-label">Contacted</span>
          </div>
        </div>

        <div class="kpi-card" :class="{ 'active-card': activeFilter === 'CONVERTED' }" @click="activeFilter = 'CONVERTED'">
          <div class="kpi-icon-wrap bg-emerald-50 text-emerald-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value text-emerald-600">{{ stats.converted }}</span>
            <span class="kpi-label">Converted Schools</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Two-Column Split Workspace -->
    <div class="inbox-workspace">
      <!-- LEFT COLUMN: Inquiry Feed -->
      <section
        class="inbox-list-column"
        :class="{ 'mobile-hidden': mobileActivePane === 'detail' }"
      >
        <!-- Search & Priority Bar -->
        <div class="list-controls-bar">
          <div class="search-input-wrap">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search by school, contact, email..."
            />
            <button v-if="searchQuery" class="btn-clear-search" @click="searchQuery = ''">
              ✕
            </button>
          </div>

          <div class="filter-dropdown-wrap">
            <select v-model="priorityFilter" class="priority-select" title="Filter by priority">
              <option value="ALL">All Priorities</option>
              <option value="URGENT">🔴 Urgent</option>
              <option value="HIGH">🟠 High</option>
              <option value="NORMAL">🔵 Normal</option>
              <option value="LOW">⚪ Low</option>
            </select>
          </div>
        </div>

        <!-- Filter Pill Tabs -->
        <div class="status-tabs-row">
          <button
            class="tab-pill"
            :class="{ active: activeFilter === 'ALL' }"
            @click="activeFilter = 'ALL'"
          >
            All ({{ stats.total }})
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeFilter === 'UNREAD' }"
            @click="activeFilter = 'UNREAD'"
          >
            Unread ({{ stats.unread }})
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeFilter === 'IN_REVIEW' }"
            @click="activeFilter = 'IN_REVIEW'"
          >
            In Review ({{ stats.in_review }})
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeFilter === 'CONTACTED' }"
            @click="activeFilter = 'CONTACTED'"
          >
            Contacted ({{ stats.contacted }})
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeFilter === 'CONVERTED' }"
            @click="activeFilter = 'CONVERTED'"
          >
            Converted ({{ stats.converted }})
          </button>
        </div>

        <!-- Inquiries Feed Scroll Container -->
        <div class="inquiries-scroll-container">
          <div v-if="isLoading" class="list-loading-state">
            <div class="loading-spinner"></div>
            <p>Loading inquiries...</p>
          </div>

          <div v-else-if="inquiries.length === 0" class="list-empty-state">
            <div class="empty-icon-box">
              <svg class="w-8 h-8 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M8 12h8" />
              </svg>
            </div>
            <h4>No Inquiries Found</h4>
            <p>No messages match the current filter criteria.</p>
          </div>

          <div v-else class="inquiry-cards-list">
            <div
              v-for="item in inquiries"
              :key="item.id"
              class="inquiry-card"
              :class="{
                'is-selected': selectedInquiry?.id === item.id,
                'is-unread': item.status === 'UNREAD'
              }"
              @click="selectInquiry(item, true)"
            >
              <div class="card-left-indicator">
                <span v-if="item.status === 'UNREAD'" class="unread-dot"></span>
              </div>

              <div class="card-main">
                <div class="card-top-row">
                  <div class="sender-info">
                    <div class="sender-avatar">
                      {{ getInitials(item.full_name) }}
                    </div>
                    <div>
                      <h3 class="sender-name">{{ item.full_name }}</h3>
                      <p class="school-name">{{ item.school_name }}</p>
                    </div>
                  </div>

                  <div class="meta-right">
                    <span class="time-ago">{{ formatRelativeTime(item.created_at) }}</span>
                    <span
                      class="priority-chip"
                      :class="`priority-${item.priority.toLowerCase()}`"
                    >
                      {{ item.priority }}
                    </span>
                  </div>
                </div>

                <p class="message-preview">
                  {{ item.message }}
                </p>

                <div class="card-bottom-tags">
                  <span v-if="item.plan" class="tag-plan">
                    🏷️ {{ item.plan }}
                  </span>
                  <span class="tag-status" :class="`status-${item.status.toLowerCase()}`">
                    {{ item.status.replace('_', ' ') }}
                  </span>
                  <span v-if="item.converted_institution_id" class="tag-converted">
                    ✓ Provisioned
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- RIGHT COLUMN: Selected Inquiry Detail -->
      <section
        class="inbox-detail-column"
        :class="{ 'mobile-hidden': mobileActivePane === 'list' }"
      >
        <!-- Mobile Back Button -->
        <div class="mobile-back-row">
          <button class="btn-mobile-back" @click="mobileActivePane = 'list'">
            <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back to Inquiries List</span>
          </button>
        </div>

        <div v-if="!selectedInquiry" class="detail-empty-state">
          <div class="detail-empty-art">
            <svg class="w-16 h-16 text-slate-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
              <polyline points="22,6 12,13 2,6" />
            </svg>
          </div>
          <h3>Select an Inquiry to Inspect</h3>
          <p>Choose any inquiry card on the left to read full requirements, contact the client, take notes, or convert to a school.</p>
        </div>

        <div v-else class="detail-content-scroll">
          <!-- DETAIL TOP BAR: Lead Identity & Status -->
          <div class="detail-top-card">
            <div class="detail-identity-header">
              <div class="lead-avatar-large">
                {{ getInitials(selectedInquiry.full_name) }}
              </div>
              <div class="lead-title-box">
                <div class="lead-tags-row">
                  <span class="lead-id-pill">Inquiry #{{ selectedInquiry.id }}</span>
                  <select
                    class="priority-badge-select"
                    :class="`priority-${selectedInquiry.priority.toLowerCase()}`"
                    :value="selectedInquiry.priority"
                    @change="updatePriority(($event.target as HTMLSelectElement).value as InquiryPriority)"
                    title="Change Lead Priority"
                  >
                    <option value="URGENT">🔴 Urgent Priority</option>
                    <option value="HIGH">🟠 High Priority</option>
                    <option value="NORMAL">🔵 Normal Priority</option>
                    <option value="LOW">⚪ Low Priority</option>
                  </select>
                  <span class="status-badge-lg" :class="`status-${selectedInquiry.status.toLowerCase()}`">
                    {{ selectedInquiry.status.replace('_', ' ') }}
                  </span>
                </div>
                <h2 class="lead-person-name">{{ selectedInquiry.full_name }}</h2>
                <h3 class="lead-institution-title">{{ selectedInquiry.school_name }}</h3>
              </div>
            </div>

            <!-- Action Ribbon: Status Changes & Convert -->
            <div class="detail-action-ribbon">
              <div class="status-change-group">
                <span class="action-label">Change Status:</span>
                <button
                  type="button"
                  class="btn-status-action"
                  :class="{ active: selectedInquiry.status === 'IN_REVIEW' }"
                  @click="updateStatus('IN_REVIEW')"
                >
                  In Review
                </button>
                <button
                  type="button"
                  class="btn-status-action"
                  :class="{ active: selectedInquiry.status === 'CONTACTED' }"
                  @click="updateStatus('CONTACTED')"
                >
                  Contacted
                </button>
                <button
                  type="button"
                  class="btn-status-action"
                  :class="{ active: selectedInquiry.status === 'CONVERTED' }"
                  @click="updateStatus('CONVERTED')"
                >
                  Converted
                </button>
                <button
                  type="button"
                  class="btn-status-action"
                  :class="{ active: selectedInquiry.status === 'ARCHIVED' }"
                  @click="updateStatus('ARCHIVED')"
                >
                  Archive
                </button>
              </div>

              <div class="convert-btn-wrapper">
                <button
                  v-if="!selectedInquiry.converted_institution_id"
                  class="btn-convert-institution"
                  @click="openConvertModal"
                >
                  <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="8.5" cy="7" r="4" />
                    <polyline points="17 11 19 13 23 9" />
                  </svg>
                  <span>Provision As Institution</span>
                </button>

                <router-link
                  v-else
                  :to="`/super-admin/institutions?q=${encodeURIComponent(selectedInquiry.school_name)}`"
                  class="btn-converted-link"
                >
                  <span>View Provisioned School →</span>
                </router-link>

                <button
                  class="btn-delete-inquiry"
                  :disabled="isDeleting"
                  @click="deleteCurrentInquiry"
                  title="Delete Inquiry"
                >
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Quick Engagement Bar -->
          <div class="direct-engagement-bar">
            <h4 class="engagement-title">Immediate Outreach Actions</h4>
            <div class="engagement-buttons">
              <a
                :href="`tel:${selectedInquiry.phone}`"
                class="btn-engage btn-call"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
                <span>Call Phone</span>
              </a>

              <a
                :href="getWhatsAppUrl(selectedInquiry.phone, selectedInquiry.school_name, selectedInquiry.full_name)"
                target="_blank"
                rel="noopener"
                class="btn-engage btn-whatsapp"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.312.045-.634.075-1.922-.444-1.503-.607-2.482-2.146-2.56-2.247-.074-.101-.617-.821-.617-1.564 0-.743.388-1.109.526-1.261.137-.152.3-.19.4-.19.101 0 .202.001.29.006.091.004.214-.034.335.257.126.302.43 1.05.468 1.127.038.077.064.167.013.27-.051.101-.077.164-.153.253-.076.088-.16.197-.229.265-.077.077-.157.161-.067.315.09.153.399.658.857 1.066.589.524 1.087.687 1.24.764.153.076.242.064.332-.039.09-.102.385-.45.488-.603.103-.153.205-.128.346-.076.141.051.897.423 1.05.5.153.076.256.115.295.179.038.064.038.371-.106.776z"/>
                </svg>
                <span>WhatsApp Client</span>
              </a>

              <a
                :href="`mailto:${selectedInquiry.email}?subject=Somroyal%20EMS%20Inquiry%20Response%20-%20${encodeURIComponent(selectedInquiry.school_name)}`"
                class="btn-engage btn-email"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                <span>Send Email</span>
              </a>
            </div>
          </div>

          <!-- Lead Details Grid -->
          <div class="lead-specs-grid">
            <div class="spec-card">
              <span class="spec-label">Official Email</span>
              <div class="spec-val-row">
                <span class="spec-value">{{ selectedInquiry.email }}</span>
                <button class="btn-copy" @click="copyToClipboard(selectedInquiry.email, 'Email')" title="Copy Email">📋</button>
              </div>
            </div>

            <div class="spec-card">
              <span class="spec-label">Direct Phone</span>
              <div class="spec-val-row">
                <span class="spec-value">{{ selectedInquiry.phone }}</span>
                <button class="btn-copy" @click="copyToClipboard(selectedInquiry.phone, 'Phone')" title="Copy Phone">📋</button>
              </div>
            </div>

            <div class="spec-card">
              <span class="spec-label">Requested Tier</span>
              <div class="spec-val-row">
                <span class="spec-value font-bold text-blue-900">{{ selectedInquiry.plan || 'Not specified' }}</span>
              </div>
            </div>

            <div class="spec-card">
              <span class="spec-label">Preferred Channel</span>
              <div class="spec-val-row">
                <span class="spec-value">{{ selectedInquiry.preferred_channel || 'Any / Direct' }}</span>
              </div>
            </div>
          </div>

          <!-- Message Body Card -->
          <div class="inquiry-message-card">
            <div class="msg-card-header flex items-center justify-between">
              <h4>Client Message & Requirements</h4>
              <span class="text-xs text-slate-400 font-medium">{{ formatDate(selectedInquiry.created_at) }}</span>
            </div>
            <div class="msg-body-box">
              <p class="msg-text">{{ selectedInquiry.message }}</p>
            </div>
          </div>

          <!-- CRM Notes Card -->
          <div class="crm-notes-card">
            <div class="crm-header-row">
              <div>
                <h4 class="crm-title">Internal CRM Notes & Staff Outreach</h4>
                <p class="crm-subtitle">Notes are private to Super Admin team members.</p>
              </div>
              <span v-if="notesSavedToast" class="toast-saved">✓ Notes Saved</span>
            </div>

            <div class="crm-form-fields">
              <div class="crm-input-group">
                <label class="crm-label">Admin Follow-up Notes</label>
                <textarea
                  v-model="adminNotesInput"
                  rows="3"
                  class="crm-textarea"
                  placeholder="Record call notes, client requirements, pricing quotes or demo scheduling details..."
                ></textarea>
              </div>

              <div class="crm-bottom-row">
                <div class="crm-input-group flex-1">
                  <label class="crm-label">Contacted By (Staff Member)</label>
                  <input
                    v-model="contactedByInput"
                    type="text"
                    class="crm-input"
                    placeholder="e.g. Somroyal Sales / Support Team"
                  />
                </div>

                <button
                  type="button"
                  class="btn-save-notes"
                  :disabled="isUpdating"
                  @click="saveAdminNotes"
                >
                  <span v-if="isUpdating">Saving...</span>
                  <span v-else>Save CRM Notes</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Convert to Institution Modal -->
    <div v-if="isConvertModalOpen" class="modal-backdrop" @click.self="isConvertModalOpen = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3 class="modal-title">Provision New Institution from Lead</h3>
          <button class="modal-close-btn" @click="isConvertModalOpen = false">✕</button>
        </div>

        <div v-if="!conversionResult" class="modal-body">
          <p class="modal-intro">
            This will provision a full tenant workspace for <strong>{{ selectedInquiry?.school_name }}</strong> and generate administrator credentials.
          </p>

          <div v-if="conversionError" class="modal-error-alert">
            {{ conversionError }}
          </div>

          <div class="modal-form-grid">
            <div class="form-group">
              <label class="form-label">Institution Type</label>
              <select v-model="convertInstitutionType" class="form-input">
                <option value="School">Primary & Secondary School</option>
                <option value="Academy">Academy</option>
                <option value="College">College</option>
                <option value="Institute">Training Institute</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Subscription Licensing</label>
              <select v-model="convertPlan" class="form-input">
                <option value="Starter Academy">Starter Academy ($250/yr)</option>
                <option value="Professional School">Professional School ($350/yr)</option>
                <option value="Enterprise Institution">Enterprise Institution ($600/yr)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Region</label>
              <input v-model="convertRegion" type="text" class="form-input" />
            </div>

            <div class="form-group">
              <label class="form-label">City</label>
              <input v-model="convertCity" type="text" class="form-input" />
            </div>
          </div>

          <div class="form-group mt-3">
            <label class="form-label">Admin Username</label>
            <input v-model="convertAdminUsername" type="text" class="form-input" />
          </div>

          <div class="modal-actions-right">
            <button class="btn-cancel-modal" @click="isConvertModalOpen = false">Cancel</button>
            <button class="btn-primary-action" :disabled="isConverting" @click="executeConversion">
              <span v-if="isConverting">Provisioning...</span>
              <span v-else>Provision Institution</span>
            </button>
          </div>
        </div>

        <!-- Success Result -->
        <div v-else class="modal-body modal-success-box">
          <div class="success-icon-badge">✓</div>
          <h3>Institution Provisioned Successfully!</h3>
          <p>{{ conversionResult.message }}</p>

          <div class="cred-table">
            <div class="cred-row">
              <span class="cred-label">Institution Code:</span>
              <span class="cred-val font-mono">{{ conversionResult.institution_code }}</span>
            </div>
            <div class="cred-row">
              <span class="cred-label">Admin Username:</span>
              <span class="cred-val">{{ conversionResult.admin_username }}</span>
            </div>
            <div class="cred-row">
              <span class="cred-label">Admin Password:</span>
              <span class="cred-val font-mono">{{ conversionResult.admin_password }}</span>
            </div>
          </div>

          <div class="modal-actions-right">
            <router-link
              :to="`/super-admin/institutions?q=${conversionResult.institution_code}`"
              class="btn-primary-action"
              @click="isConvertModalOpen = false"
            >
              Open Institutions View →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.inbox-page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.inbox-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.header-main-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-badge-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  border-radius: 9999px;
  margin-bottom: 6px;
  border: 1px solid #bfdbfe;
}

.pulse-indicator {
  width: 8px;
  height: 8px;
  background: #2563eb;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7);
  animation: pulse-ring 1.8s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(37, 99, 235, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
}

.header-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #061737;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
}

.header-subtitle {
  font-size: 0.88rem;
  color: #64748b;
  margin: 0;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  color: #334155;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8fafc;
  color: #0f172a;
  border-color: #94a3b8;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1rem;
}

.kpi-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: all 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.kpi-card.active-card {
  border-color: #ff6500;
  box-shadow: 0 4px 14px rgba(255, 101, 0, 0.15);
}

.kpi-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 10px;
  flex-shrink: 0;
}

.kpi-data {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 1.45rem;
  font-weight: 800;
  color: #061737;
  line-height: 1.2;
}

.kpi-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.badge-unread-chip {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff6500;
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 9999px;
}

/* Workspace */
.inbox-workspace {
  display: grid;
  grid-template-columns: 390px 1fr;
  gap: 1.25rem;
  min-height: 680px;
  align-items: start;
}

/* Left Column */
.inbox-list-column {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.list-controls-bar {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.55rem 2rem 0.55rem 2.25rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.85rem;
  background: #f8fafc;
  outline: none;
  transition: all 0.15s ease;
}

.search-input:focus {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.btn-clear-search {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
}

.priority-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.82rem;
  color: #334155;
  background: #f8fafc;
  outline: none;
}

.status-tabs-row {
  display: flex;
  gap: 0.35rem;
  padding: 0.65rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
}

.tab-pill {
  padding: 0.35rem 0.65rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.tab-pill:hover {
  color: #0f172a;
}

.tab-pill.active {
  background: #061737;
  color: #ffffff;
}

.inquiries-scroll-container {
  overflow-y: auto;
  max-height: 640px;
}

.list-loading-state,
.list-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  text-align: center;
  color: #64748b;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #ff6500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

/* Inquiry Card */
.inquiry-card {
  display: flex;
  padding: 1rem 1.15rem;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.15s ease;
}

.inquiry-card:hover {
  background: #fbfcfe;
}

.inquiry-card.is-selected {
  background: #fff8f3;
  border-left: 4px solid #ff6500;
}

.card-left-indicator {
  width: 14px;
  flex-shrink: 0;
  padding-top: 4px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #ff6500;
  border-radius: 50%;
  display: inline-block;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.card-top-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 6px;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sender-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #061737;
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sender-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.school-name {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.meta-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.time-ago {
  font-size: 0.7rem;
  color: #94a3b8;
}

.priority-chip {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.priority-urgent {
  background: #fef2f2;
  color: #dc2626;
}

.priority-high {
  background: #fff7ed;
  color: #ea580c;
}

.priority-normal {
  background: #eff6ff;
  color: #2563eb;
}

.priority-low {
  background: #f1f5f9;
  color: #64748b;
}

.message-preview {
  font-size: 0.78rem;
  color: #475569;
  line-height: 1.4;
  margin: 0.35rem 0 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-bottom-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-plan {
  font-size: 0.7rem;
  background: #f1f5f9;
  color: #334155;
  padding: 2px 6px;
  border-radius: 4px;
}

.tag-status {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: capitalize;
}

.status-unread {
  background: #fff7ed;
  color: #ea580c;
}

.status-in_review {
  background: #f5f3ff;
  color: #7c3aed;
}

.status-contacted {
  background: #e0e7ff;
  color: #4338ca;
}

.status-converted {
  background: #ecfdf5;
  color: #059669;
}

.status-closed {
  background: #f1f5f9;
  color: #64748b;
}

.tag-converted {
  font-size: 0.7rem;
  font-weight: 700;
  background: #ecfdf5;
  color: #059669;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Right Column */
.inbox-detail-column {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  min-height: 640px;
}

.mobile-back-row {
  display: none;
  margin-bottom: 0.5rem;
}

.btn-mobile-back {
  display: inline-flex;
  align-items: center;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #061737;
  cursor: pointer;
}

.detail-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: #64748b;
  margin: auto;
}

.detail-empty-art {
  margin-bottom: 1rem;
}

.detail-content-scroll {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.detail-top-card {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  padding-bottom: 1.15rem;
  border-bottom: 1px solid #f1f5f9;
}

.detail-identity-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.lead-avatar-large {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #061737 0%, #1e40af 100%);
  color: #ffffff;
  font-weight: 800;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(6, 23, 55, 0.2);
}

.lead-title-box {
  flex: 1;
}

.lead-tags-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.lead-id-pill {
  font-size: 0.72rem;
  font-weight: 700;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.priority-badge-select {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid transparent;
  outline: none;
  cursor: pointer;
}

.status-badge-lg {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  text-transform: capitalize;
}

.lead-person-name {
  font-size: 1.35rem;
  font-weight: 800;
  color: #061737;
  margin: 0;
}

.lead-institution-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #64748b;
  margin: 2px 0 0;
}

.detail-action-ribbon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.status-change-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.action-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.btn-status-action {
  padding: 5px 10px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-status-action:hover {
  background: #f1f5f9;
}

.btn-status-action.active {
  background: #061737;
  color: #ffffff;
  border-color: #061737;
}

.convert-btn-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-convert-institution {
  display: inline-flex;
  align-items: center;
  padding: 7px 14px;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-convert-institution:hover {
  background: #15803d;
}

.btn-converted-link {
  display: inline-flex;
  align-items: center;
  padding: 7px 14px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  text-decoration: none;
}

.btn-delete-inquiry {
  padding: 7px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #ef4444;
  border-radius: 8px;
  cursor: pointer;
}

.btn-delete-inquiry:hover {
  background: #fee2e2;
  color: #dc2626;
}

/* Outreach Bar */
.direct-engagement-bar {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.engagement-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0;
}

.engagement-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-engage {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.15s ease;
}

.btn-call {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.btn-whatsapp {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.btn-email {
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

/* Specs */
.lead-specs-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.spec-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.spec-label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 600;
}

.spec-val-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.spec-value {
  font-size: 0.82rem;
  font-weight: 600;
  color: #0f172a;
}

.btn-copy {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
}

/* Message Card */
.inquiry-message-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.msg-card-header {
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.msg-card-header h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.msg-body-box {
  padding: 1rem;
}

.msg-text {
  font-size: 0.88rem;
  line-height: 1.6;
  color: #334155;
  margin: 0;
  white-space: pre-wrap;
}

/* CRM Notes Card */
.crm-notes-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.crm-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.crm-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.crm-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 2px 0 0;
}

.toast-saved {
  font-size: 0.72rem;
  font-weight: 700;
  color: #16a34a;
  background: #dcfce7;
  padding: 3px 8px;
  border-radius: 6px;
}

.crm-form-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.crm-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.crm-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.crm-textarea,
.crm-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  background: #ffffff;
  outline: none;
}

.crm-textarea:focus,
.crm-input:focus {
  border-color: #ff6500;
}

.crm-bottom-row {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-save-notes {
  padding: 0.55rem 1.25rem;
  background: #061737;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  height: 38px;
}

.btn-save-notes:hover:not(:disabled) {
  background: #ff6500;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(6, 23, 55, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-box {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  overflow: hidden;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
}

.modal-header {
  padding: 1.15rem 1.35rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #061737;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 1.35rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-intro {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.4;
  margin: 0;
}

.modal-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #334155;
}

.form-input {
  padding: 0.55rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  outline: none;
}

.form-input:focus {
  border-color: #ff6500;
}

.modal-actions-right {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
  margin-top: 0.5rem;
}

.btn-cancel-modal {
  padding: 0.55rem 1rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-primary-action {
  padding: 0.55rem 1.25rem;
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  border: none;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  text-decoration: none;
}

.modal-success-box {
  text-align: center;
  padding: 1.5rem;
}

.success-icon-badge {
  width: 48px;
  height: 48px;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  margin: 0 auto 12px;
}

.cred-table {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  margin: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.cred-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
}

.cred-label {
  font-weight: 600;
  color: #64748b;
}

.cred-val {
  font-weight: 700;
  color: #0f172a;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .inbox-workspace {
    grid-template-columns: 1fr;
  }

  .mobile-hidden {
    display: none !important;
  }

  .mobile-back-row {
    display: block;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .lead-specs-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .modal-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
