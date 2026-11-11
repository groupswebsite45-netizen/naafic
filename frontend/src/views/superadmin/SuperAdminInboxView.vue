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
      selectInquiry(inquiries.value[0]);
    }
  } catch (err) {
    console.error('Failed to load inquiries:', err);
  } finally {
    isLoading.value = false;
    isRefreshing.value = false;
  }
}

async function selectInquiry(inquiry: Inquiry) {
  selectedInquiry.value = inquiry;
  adminNotesInput.value = inquiry.admin_notes || '';
  contactedByInput.value = inquiry.contacted_by || '';
  conversionResult.value = null;
  conversionError.value = null;

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
    <!-- TOP HEADER & KPI METRICS BAR -->
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
            type="button"
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
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            <span>{{ isRefreshing ? 'Refreshing...' : 'Refresh Inbox' }}</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Cards Grid -->
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
            <span class="kpi-label">Total Leads</span>
          </div>
        </div>

        <div class="kpi-card highlight-unread" :class="{ 'active-card': activeFilter === 'UNREAD' }" @click="activeFilter = 'UNREAD'">
          <div class="kpi-icon-wrap bg-orange-50 text-orange-600">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value text-orange-600">{{ stats.unread }}</span>
            <span class="kpi-label">Unread Messages</span>
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

    <!-- MAIN TWO-COLUMN SPLIT WORKSPACE -->
    <div class="inbox-workspace">
      <!-- LEFT COLUMN: Inquiry Feed & Filter List -->
      <section class="inbox-list-column">
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
              placeholder="Search by school, contact, email, phone..."
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

        <!-- Inquiries Scrollable List -->
        <div class="inquiries-scroll-container">
          <div v-if="isLoading" class="list-loading-state">
            <div class="loading-spinner"></div>
            <span>Loading inquiry messages...</span>
          </div>

          <div v-else-if="inquiries.length === 0" class="list-empty-state">
            <div class="empty-icon-box">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
              </svg>
            </div>
            <h4>No inquiries found</h4>
            <p>No messages match the current filter criteria or search query.</p>
          </div>

          <div
            v-for="item in inquiries"
            :key="item.id"
            class="inquiry-card"
            :class="{
              'is-selected': selectedInquiry?.id === item.id,
              'is-unread': item.status === 'UNREAD',
            }"
            @click="selectInquiry(item)"
          >
            <div class="card-left-indicator">
              <span v-if="item.status === 'UNREAD'" class="unread-dot" title="Unread Lead"></span>
            </div>

            <div class="card-main">
              <div class="card-top-row">
                <div class="sender-info">
                  <div class="avatar-circle">
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
                  ✓ School Provisioned
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- RIGHT COLUMN: Selected Inquiry Detail & CRM Control Panel -->
      <section class="inbox-detail-column">
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
          <!-- DETAIL TOP BAR: Lead Identity & Quick Status Transitions -->
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
                    title="Click to Change Lead Priority"
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
                  :class="{ active: selectedInquiry.status === 'ARCHIVED' }"
                  @click="updateStatus('ARCHIVED')"
                >
                  Archive
                </button>
              </div>

              <!-- High-Value 1-Click Convert to Institution Button -->
              <div class="convert-btn-wrapper">
                <button
                  v-if="!selectedInquiry.converted_institution_id"
                  type="button"
                  class="btn-convert-institution"
                  @click="openConvertModal"
                >
                  <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5" />
                    <path d="M2 12l10 5 10-5" />
                  </svg>
                  Convert to School
                </button>

                <router-link
                  v-else
                  to="/super-admin/institutions"
                  class="btn-converted-link"
                >
                  <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  View Active School
                </router-link>

                <button
                  type="button"
                  class="btn-delete-inquiry"
                  :disabled="isDeleting"
                  @click="deleteCurrentInquiry"
                  title="Delete Inquiry"
                >
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- DIRECT CLIENT ENGAGEMENT STRIP (WhatsApp, Email, Phone) -->
          <div class="direct-engagement-bar">
            <h4 class="engagement-title">Direct Outreach Channels:</h4>
            <div class="channel-buttons-row">
              <a
                :href="getWhatsAppUrl(selectedInquiry.phone, selectedInquiry.school_name, selectedInquiry.full_name)"
                target="_blank"
                class="btn-channel btn-whatsapp"
              >
                <svg class="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91C2.13 13.66 2.59 15.36 3.45 16.86L2.05 22L7.3 20.62C8.75 21.41 10.38 21.83 12.04 21.83C17.5 21.83 21.95 17.38 21.95 11.92C21.95 9.27 20.92 6.78 19.05 4.91C17.18 3.03 14.69 2 12.04 2M12.05 3.67C14.25 3.67 16.31 4.53 17.87 6.09C19.42 7.65 20.28 9.72 20.28 11.92C20.28 16.46 16.58 20.15 12.04 20.15C10.56 20.15 9.11 19.76 7.85 19L7.55 18.83L4.43 19.65L5.26 16.61L5.06 16.29C4.24 14.99 3.8 13.47 3.8 11.91C3.81 7.37 7.5 3.67 12.05 3.67Z" />
                </svg>
                Chat on WhatsApp
              </a>

              <a
                :href="`mailto:${selectedInquiry.email}?subject=Somroyal%20EMS%20Inquiry%20-%20${encodeURIComponent(selectedInquiry.school_name)}`"
                class="btn-channel btn-email"
              >
                <svg class="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                Send Email
              </a>

              <a
                :href="`tel:${selectedInquiry.phone}`"
                class="btn-channel btn-phone"
              >
                <svg class="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
                Call Lead
              </a>
            </div>
          </div>

          <!-- CLIENT PROFILE SPECIFICATION GRID -->
          <div class="lead-specs-grid">
            <div class="spec-card">
              <span class="spec-label">Official Email:</span>
              <div class="spec-value-row">
                <span class="spec-value font-mono">{{ selectedInquiry.email }}</span>
                <button
                  class="btn-copy"
                  @click="copyToClipboard(selectedInquiry.email, 'Email')"
                  title="Copy email"
                >
                  📋
                </button>
              </div>
            </div>

            <div class="spec-card">
              <span class="spec-label">Phone / WhatsApp:</span>
              <div class="spec-value-row">
                <span class="spec-value font-mono">{{ selectedInquiry.phone }}</span>
                <button
                  class="btn-copy"
                  @click="copyToClipboard(selectedInquiry.phone, 'Phone number')"
                  title="Copy phone"
                >
                  📋
                </button>
              </div>
            </div>

            <div class="spec-card">
              <span class="spec-label">Interested Plan / Tier:</span>
              <span class="spec-value text-blue-700 font-semibold">{{ selectedInquiry.plan || 'Not specified' }}</span>
            </div>

            <div class="spec-card">
              <span class="spec-label">Submission Date:</span>
              <span class="spec-value">{{ formatDate(selectedInquiry.created_at) }}</span>
            </div>
          </div>

          <!-- FULL INQUIRY MESSAGE TEXT -->
          <div class="inquiry-message-card">
            <div class="msg-card-header">
              <svg class="w-5 h-5 text-orange-500 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <h4>Submitted Requirements & Inquiry Message</h4>
            </div>
            <div class="msg-body-box">
              <p class="msg-text">{{ selectedInquiry.message }}</p>
            </div>
          </div>

          <!-- INTERNAL CRM NOTES & ACCOUNT MANAGEMENT -->
          <div class="crm-notes-card">
            <div class="crm-header-row">
              <div>
                <h4 class="crm-title">Internal CRM Notes & Consultation Records</h4>
                <p class="crm-subtitle">Document telephone consultations, demo meeting schedules, and quotation details.</p>
              </div>
              <transition name="fade">
                <span v-if="notesSavedToast" class="toast-saved">✓ Saved successfully</span>
              </transition>
            </div>

            <div class="crm-form-fields">
              <div class="crm-input-group">
                <label class="crm-label">Contacted By Staff Member:</label>
                <input
                  v-model="contactedByInput"
                  type="text"
                  class="crm-text-input"
                  placeholder="e.g. Somroyal Sales Specialist / Eng. Ahmed"
                />
              </div>

              <div class="crm-input-group">
                <label class="crm-label">Follow-up Notes & Agreements:</label>
                <textarea
                  v-model="adminNotesInput"
                  rows="4"
                  class="crm-textarea"
                  placeholder="Enter detailed notes regarding discussions with the school principal or administrator..."
                ></textarea>
              </div>

              <div class="crm-btn-row">
                <button
                  type="button"
                  class="btn-save-notes"
                  :disabled="isUpdating"
                  @click="saveAdminNotes"
                >
                  {{ isUpdating ? 'Saving...' : 'Save CRM Notes' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- MODAL: CONVERT INQUIRY TO REGISTERED INSTITUTION -->
    <div v-if="isConvertModalOpen" class="modal-overlay" @click.self="isConvertModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h3 class="modal-title">Convert Inquiry to Active Institution</h3>
            <p class="modal-subtitle">
              Provisioning dedicated database and administrative credentials for {{ selectedInquiry?.school_name }}.
            </p>
          </div>
          <button class="modal-close-btn" @click="isConvertModalOpen = false">✕</button>
        </div>

        <div v-if="conversionResult" class="modal-success-box">
          <div class="success-icon-badge">✓</div>
          <h4>School Provisioned Successfully!</h4>
          <p>{{ conversionResult.message }}</p>

          <div class="cred-table">
            <div class="cred-row">
              <span class="cred-label">Institution Code:</span>
              <span class="cred-val">{{ conversionResult.institution_code }}</span>
            </div>
            <div class="cred-row">
              <span class="cred-label">Admin Username:</span>
              <span class="cred-val">{{ conversionResult.admin_username }}</span>
            </div>
            <div class="cred-row">
              <span class="cred-label">Temporary Password:</span>
              <span class="cred-val text-orange-600 font-mono">{{ conversionResult.temporary_password }}</span>
            </div>
          </div>

          <div class="modal-actions-right">
            <router-link to="/super-admin/institutions" class="btn-primary-action">
              Go to Institutions Management
            </router-link>
            <button class="btn-cancel-modal" @click="isConvertModalOpen = false">
              Close
            </button>
          </div>
        </div>

        <form v-else @submit.prevent="executeConversion" class="modal-form">
          <div v-if="conversionError" class="modal-error-banner">
            {{ conversionError }}
          </div>

          <div class="form-row-2">
            <div class="form-group">
              <label class="form-label">School / Institution Name</label>
              <input
                type="text"
                class="form-input"
                :value="selectedInquiry?.school_name"
                disabled
              />
            </div>

            <div class="form-group">
              <label class="form-label">Institution Type</label>
              <select v-model="convertInstitutionType" class="form-input">
                <option value="School">School (Primary & Secondary)</option>
                <option value="Academy">Academy / College</option>
                <option value="University">University</option>
                <option value="Machad">Machad / Institute</option>
              </select>
            </div>
          </div>

          <div class="form-row-2">
            <div class="form-group">
              <label class="form-label">Administrative Region</label>
              <input v-model="convertRegion" type="text" class="form-input" placeholder="e.g. Banaadir" />
            </div>

            <div class="form-group">
              <label class="form-label">City</label>
              <input v-model="convertCity" type="text" class="form-input" placeholder="e.g. Mogadishu" />
            </div>
          </div>

          <div class="form-row-2">
            <div class="form-group">
              <label class="form-label">Subscription Plan</label>
              <select v-model="convertPlan" class="form-input">
                <option value="Starter Academy">Starter Academy ($15/mo)</option>
                <option value="Professional School">Professional School ($25/mo)</option>
                <option value="Enterprise Network">Enterprise Network ($45/mo)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Generated Admin Username</label>
              <input v-model="convertAdminUsername" type="text" class="form-input" />
            </div>
          </div>

          <div class="modal-actions-right">
            <button
              type="button"
              class="btn-cancel-modal"
              :disabled="isConverting"
              @click="isConvertModalOpen = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn-primary-action"
              :disabled="isConverting"
            >
              {{ isConverting ? 'Provisioning School...' : 'Provision Institution' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==========================================================================
   SOMROYAL SUPER ADMIN CRM INBOX STYLES (PREMIUM HEER SARE AH)
   ========================================================================== */

.inbox-page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: calc(100vh - 120px);
  color: #1e293b;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* TOP HEADER & KPIS */
.inbox-header {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
}

.header-main-info {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 24px;
}

.header-badge-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  border-radius: 9999px;
  margin-bottom: 8px;
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
  font-size: 26px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.02em;
  margin: 0 0 6px;
}

.header-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #e2e8f0;
  color: #0f172a;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(170px, 100%), 1fr));
  gap: 16px;
}

.kpi-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.kpi-card:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.kpi-card.active-card {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 4px 12px rgba(255, 101, 0, 0.12);
}

.kpi-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  flex-shrink: 0;
}

.kpi-data {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.badge-unread-chip {
  position: absolute;
  top: 10px;
  right: 12px;
  padding: 2px 8px;
  background: #ff6500;
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  border-radius: 9999px;
}

/* MAIN WORKSPACE */
.inbox-workspace {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 20px;
  min-height: 640px;
}

@media (max-width: 1100px) {
  .inbox-workspace {
    grid-template-columns: 1fr;
  }
}

/* LEFT COLUMN */
.inbox-list-column {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.list-controls-bar {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 10px 36px 10px 36px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  color: #0f172a;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.btn-clear-search {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.priority-select {
  width: 100%;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  outline: none;
}

.status-tabs-row {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
}

.tab-pill {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.tab-pill:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.tab-pill.active {
  background: #0f172a;
  color: #ffffff;
}

.inquiries-scroll-container {
  flex: 1;
  overflow-y: auto;
  max-height: 720px;
}

.list-loading-state,
.list-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
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
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: #94a3b8;
}

/* INQUIRY CARD */
.inquiry-card {
  position: relative;
  display: flex;
  padding: 16px 18px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.15s ease;
}

.inquiry-card:hover {
  background: #f8fafc;
}

.inquiry-card.is-selected {
  background: #fff8f3;
  border-left: 4px solid #ff6500;
}

.inquiry-card.is-unread {
  background: #ffffff;
}

.inquiry-card.is-unread .sender-name {
  font-weight: 800;
}

.card-left-indicator {
  width: 14px;
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 6px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #ff6500;
  border-radius: 50%;
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
  gap: 10px;
  min-width: 0;
}

.sender-info > div {
  min-width: 0;
}

.avatar-circle {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #0f172a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.sender-name {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.school-name {
  font-size: 12px;
  color: #64748b;
  margin: 2px 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.meta-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.time-ago {
  font-size: 11px;
  color: #94a3b8;
}

.priority-chip {
  padding: 2px 6px;
  font-size: 10px;
  font-weight: 700;
  border-radius: 6px;
  text-transform: uppercase;
}

.priority-urgent { background: #fee2e2; color: #b91c1c; }
.priority-high { background: #ffedd5; color: #c2410c; }
.priority-normal { background: #eff6ff; color: #1d4ed8; }
.priority-low { background: #f1f5f9; color: #64748b; }

.message-preview {
  font-size: 12px;
  color: #475569;
  margin: 0 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.card-bottom-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-plan {
  padding: 2px 8px;
  background: #f1f5f9;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #334155;
}

.tag-status {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.status-unread { background: #fef3c7; color: #92400e; }
.status-read { background: #f1f5f9; color: #64748b; }
.status-in_review { background: #f3e8ff; color: #7e22ce; }
.status-contacted { background: #e0e7ff; color: #4338ca; }
.status-converted { background: #dcfce7; color: #15803d; }
.status-archived { background: #e2e8f0; color: #475569; }

.tag-converted {
  font-size: 10px;
  font-weight: 700;
  color: #16a34a;
}

/* RIGHT COLUMN DETAIL */
.inbox-detail-column {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
}

.detail-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 30px;
  text-align: center;
  color: #64748b;
}

.detail-empty-art {
  margin-bottom: 16px;
}

.detail-content-scroll {
  padding: 28px;
  overflow-y: auto;
  max-height: 820px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Lead Top Identity Card */
.detail-top-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 22px;
}

.detail-identity-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px 18px;
  margin-bottom: 20px;
}

.lead-avatar-large {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #071f49, #1264e8);
  color: #ffffff;
  font-size: 20px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(18, 100, 232, 0.25);
  flex-shrink: 0;
}

.lead-tags-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.lead-id-pill {
  font-size: 11px;
  font-weight: 700;
  background: #e2e8f0;
  color: #334155;
  padding: 2px 8px;
  border-radius: 6px;
}

.priority-badge-select,
.status-badge-lg {
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 6px;
  border: 1px solid transparent;
  text-transform: uppercase;
  cursor: pointer;
  outline: none;
}

.lead-person-name {
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
}

.lead-institution-title {
  font-size: 15px;
  font-weight: 600;
  color: #475569;
  margin: 0;
}

.detail-action-ribbon {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
  gap: 12px;
}

.status-change-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.action-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-right: 4px;
}

.btn-status-action {
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-status-action:hover {
  background: #f1f5f9;
}

.btn-status-action.active {
  background: #ff6500;
  color: #ffffff;
  border-color: #ff6500;
}

.convert-btn-wrapper {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-convert-institution {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #16a34a;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-convert-institution:hover {
  background: #15803d;
}

.btn-converted-link {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.btn-delete-inquiry {
  padding: 8px;
  background: #ffffff;
  border: 1px solid #fecaca;
  color: #ef4444;
  border-radius: 8px;
  cursor: pointer;
}

.btn-delete-inquiry:hover {
  background: #fee2e2;
}

/* OUTREACH BAR */
.direct-engagement-bar {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 20px;
}

.engagement-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin: 0 0 10px;
}

.channel-buttons-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-channel {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-whatsapp {
  background: #25d366;
  color: #ffffff;
}

.btn-whatsapp:hover {
  background: #20bd5a;
  box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
}

.btn-email {
  background: #0f172a;
  color: #ffffff;
}

.btn-email:hover {
  background: #1e293b;
}

.btn-phone {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
}

.btn-phone:hover {
  background: #dbeafe;
}

/* SPECS GRID */
.lead-specs-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.spec-card {
  background: #f8fafc;
  border: 1px solid #f1f5f9;
  border-radius: 10px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.spec-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
}

.spec-value-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.spec-value {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  overflow-wrap: anywhere;
  min-width: 0;
}

.btn-copy {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  min-width: 28px;
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* MESSAGE CARD */
.inquiry-message-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.msg-card-header {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.msg-card-header h4 {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.msg-body-box {
  padding: 20px;
  background: #ffffff;
}

.msg-text {
  font-size: 15px;
  line-height: 1.6;
  color: #1e293b;
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

/* CRM NOTES CARD */
.crm-notes-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.crm-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.crm-title {
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 2px;
}

.crm-subtitle {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.toast-saved {
  font-size: 12px;
  font-weight: 700;
  color: #16a34a;
  background: #dcfce7;
  padding: 4px 10px;
  border-radius: 6px;
}

.crm-form-fields {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.crm-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.crm-label {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}

.crm-text-input,
.crm-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13px;
  color: #0f172a;
  outline: none;
  font-family: inherit;
}

.crm-text-input:focus,
.crm-textarea:focus {
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.crm-btn-row {
  display: flex;
  justify-content: flex-end;
}

.btn-save-notes {
  padding: 9px 20px;
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-save-notes:hover:not(:disabled) {
  background: #ff6500;
}

/* MODAL STYLES */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 0.75rem;
}

.modal-card {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 580px;
  max-height: calc(100dvh - 1.5rem);
  overflow-y: auto;
  padding: clamp(1rem, 4vw, 1.75rem);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 20px;
}

.modal-title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 4px;
}

.modal-subtitle {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #94a3b8;
  cursor: pointer;
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}

.form-input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}

.form-input:focus {
  border-color: #ff6500;
}

.modal-actions-right {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

.btn-cancel-modal {
  padding: 9px 18px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

.btn-primary-action {
  padding: 9px 20px;
  background: #ff6500;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  text-decoration: none;
}

.modal-success-box {
  text-align: center;
  padding: 10px 0;
}

.success-icon-badge {
  width: 52px;
  height: 52px;
  background: #dcfce7;
  color: #16a34a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
  margin: 0 auto 16px;
}

.cred-table {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 18px;
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cred-row {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.25rem 0.75rem;
  font-size: 13px;
}

.cred-label {
  font-weight: 600;
  color: #64748b;
}

.cred-val {
  font-weight: 700;
  color: #0f172a;
  overflow-wrap: anywhere;
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
  }

  .kpi-card {
    padding: 0.75rem;
    gap: 0.6rem;
    min-width: 0;
  }

  .kpi-icon-wrap {
    width: 36px;
    height: 36px;
  }

  .inbox-header,
  .detail-header-card,
  .direct-engagement-bar,
  .msg-card-header,
  .msg-body-box,
  .crm-notes-card {
    padding: 1rem;
  }

  .header-title {
    font-size: 1.35rem;
  }

  .lead-person-name {
    font-size: 1.2rem;
  }

  .btn-refresh {
    width: 100%;
    justify-content: center;
  }

  .lead-specs-grid,
  .form-row-2 {
    grid-template-columns: 1fr;
  }

  .btn-channel {
    flex: 1 1 140px;
    justify-content: center;
    min-height: 44px;
  }

  .modal-actions-right {
    flex-wrap: wrap;
  }
}
</style>
