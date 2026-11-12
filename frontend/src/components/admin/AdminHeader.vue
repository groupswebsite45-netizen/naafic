<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useNotificationStore } from '../../stores/notification';
import { useSchoolBrandingStore } from '../../stores/schoolBranding';
import { useI18n, type Locale } from '../../i18n';
import type { NotificationItem } from '../../types/notification';

interface Props {
  pageTitle?: string;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'toggle-sidebar'): void;
}>();

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const brandingStore = useSchoolBrandingStore();
const { t, locale, currentLanguage, supportedLanguages, setLocale, formatRelativeTime } = useI18n();

// Dropdown states
const isProfileDropdownOpen = ref(false);
const isLanguageDropdownOpen = ref(false);
const isNotificationDropdownOpen = ref(false);

// Header search query & notification filter
const searchQuery = ref('');
const notificationFilter = ref<'ALL' | 'UNREAD'>('ALL');

// Admin User Info
const adminDisplayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || brandingStore.adminName || 'Administrator';
});

const adminRoleName = computed(() => {
  if (authStore.isSuperAdmin) return t('header.superAdmin');
  return t('header.schoolAdmin');
});

// Notifications
const unreadCount = computed(() => notificationStore.unreadCount);

const unreadBadgeText = computed(() => {
  if (unreadCount.value > 99) return '99+';
  return String(unreadCount.value);
});

const filteredNotifications = computed(() => {
  const list = notificationStore.headerNotifications;
  if (notificationFilter.value === 'UNREAD') {
    return list.filter(n => !n.read_at && n.status !== 'READ');
  }
  return list;
});

// Dropdown Toggles
function toggleProfileDropdown(e: MouseEvent) {
  e.stopPropagation();
  isProfileDropdownOpen.value = !isProfileDropdownOpen.value;
  isLanguageDropdownOpen.value = false;
  isNotificationDropdownOpen.value = false;
}

function toggleLanguageDropdown(e: MouseEvent) {
  e.stopPropagation();
  isLanguageDropdownOpen.value = !isLanguageDropdownOpen.value;
  isProfileDropdownOpen.value = false;
  isNotificationDropdownOpen.value = false;
}

async function toggleNotificationDropdown(e: MouseEvent) {
  e.stopPropagation();
  const willOpen = !isNotificationDropdownOpen.value;
  isNotificationDropdownOpen.value = willOpen;
  isProfileDropdownOpen.value = false;
  isLanguageDropdownOpen.value = false;

  if (willOpen) {
    await notificationStore.fetchHeaderNotifications();
  }
}

function selectLanguage(code: Locale) {
  setLocale(code);
  isLanguageDropdownOpen.value = false;
}

// Notification Actions
async function handleMarkSingleRead(id: number) {
  try {
    await notificationStore.markNotificationRead(id);
  } catch (err) {
    console.error('Failed to mark notification read', err);
  }
}

async function handleMarkAllRead() {
  try {
    await notificationStore.markAllNotificationsRead();
  } catch (err) {
    console.error('Failed to mark all notifications read', err);
  }
}

async function handleNotificationClick(notif: NotificationItem) {
  // Mark as read if not already read
  if (!notif.read_at && notif.status !== 'READ') {
    await handleMarkSingleRead(notif.id);
  }
  isNotificationDropdownOpen.value = false;

  // Smart routing based on notification metadata
  if (notif.related_exam_id || notif.related_result_id || notif.notification_type === 'RESULT_RELEASED') {
    router.push('/admin/results');
  } else if (notif.notification_type === 'FEE_REMINDER') {
    router.push('/admin/fees');
  } else if (notif.notification_type === 'ATTENDANCE_ABSENT') {
    router.push('/admin/notifications');
  } else {
    router.push('/admin/notifications');
  }
}

function handleViewAll() {
  isNotificationDropdownOpen.value = false;
  router.push('/admin/notifications');
}

// Global outside-click and keydown handlers
function closeDropdowns(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.profile-menu-container')) {
    isProfileDropdownOpen.value = false;
  }
  if (!target.closest('.language-container')) {
    isLanguageDropdownOpen.value = false;
  }
  if (!target.closest('.notification-container')) {
    isNotificationDropdownOpen.value = false;
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    isProfileDropdownOpen.value = false;
    isLanguageDropdownOpen.value = false;
    isNotificationDropdownOpen.value = false;
  }
}

async function handleLogout() {
  isProfileDropdownOpen.value = false;
  await authStore.logout();
  router.push('/login');
}

onMounted(() => {
  window.addEventListener('click', closeDropdowns);
  window.addEventListener('keydown', handleKeyDown);
  notificationStore.startNotificationPolling(30000);
});

onUnmounted(() => {
  window.removeEventListener('click', closeDropdowns);
  window.removeEventListener('keydown', handleKeyDown);
  notificationStore.stopNotificationPolling();
});
</script>

<template>
  <header class="admin-header">
    <div class="header-left">
      <!-- Hamburger Toggle Button -->
      <button
        type="button"
        class="menu-toggle-btn"
        aria-label="Toggle navigation menu"
        @click="emit('toggle-sidebar')"
      >
        <svg class="hamburger-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="3" y1="6" x2="21" y2="6" stroke-linecap="round" />
          <line x1="3" y1="12" x2="21" y2="12" stroke-linecap="round" />
          <line x1="3" y1="18" x2="21" y2="18" stroke-linecap="round" />
        </svg>
      </button>

      <!-- Expandable Search Bar with Ctrl + K badge -->
      <div class="search-container">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" stroke-linecap="round" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          :placeholder="t('header.searchPlaceholder')"
          aria-label="Search across system"
        />
        <div class="shortcut-badge">
          <span>{{ t('header.ctrlK') }}</span>
        </div>
      </div>
    </div>

    <div class="header-right">
      <!-- 1. FULLY FUNCTIONAL LANGUAGE SELECTOR (US / EN / SO) -->
      <div class="language-container">
        <button
          type="button"
          class="language-pill"
          :class="{ 'is-active': isLanguageDropdownOpen }"
          :aria-expanded="isLanguageDropdownOpen"
          aria-haspopup="true"
          :title="`${t('header.currentLanguage')}: ${currentLanguage.label}`"
          @click="toggleLanguageDropdown"
        >
          <span class="flag-icon">{{ currentLanguage.flag }}</span>
          <span class="lang-text">{{ currentLanguage.shortLabel }}</span>
          <svg
            class="dropdown-chevron"
            :class="{ 'rotate-180': isLanguageDropdownOpen }"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>

        <!-- Language Dropdown Menu -->
        <transition name="dropdown-fade">
          <div
            v-if="isLanguageDropdownOpen"
            class="language-dropdown"
            role="menu"
            aria-orientation="vertical"
          >
            <div class="dropdown-header-sm">
              <span class="header-sm-title">{{ t('header.language') }}</span>
            </div>

            <button
              v-for="lang in supportedLanguages"
              :key="lang.code"
              type="button"
              class="lang-option-btn"
              :class="{ 'selected': locale === lang.code }"
              role="menuitem"
              @click="selectLanguage(lang.code)"
            >
              <span class="lang-option-flag">{{ lang.flag }}</span>
              <div class="lang-option-info">
                <span class="lang-option-name">{{ lang.nativeLabel }}</span>
                <span class="lang-option-sub">{{ lang.label }}</span>
              </div>
              <svg
                v-if="locale === lang.code"
                class="lang-check-icon"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </transition>
      </div>

      <!-- 2. FULLY FUNCTIONAL NOTIFICATIONS (BELL) -->
      <div class="notification-container">
        <button
          type="button"
          class="header-icon-btn"
          :class="{ 'is-active': isNotificationDropdownOpen }"
          :aria-expanded="isNotificationDropdownOpen"
          aria-haspopup="true"
          :aria-label="t('header.notifications')"
          :title="unreadCount > 0 ? t('header.newNotifications', { count: unreadCount }) : t('header.notifications')"
          @click="toggleNotificationDropdown"
        >
          <svg class="header-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
          <!-- Dynamic Unread Badge from Database -->
          <span v-if="unreadCount > 0" class="notification-badge">
            {{ unreadBadgeText }}
          </span>
        </button>

        <!-- Professional Notifications Dropdown -->
        <transition name="dropdown-fade">
          <div
            v-if="isNotificationDropdownOpen"
            class="notifications-dropdown"
            role="dialog"
            aria-label="Notifications"
          >
            <!-- Dropdown Header -->
            <div class="notif-dropdown-header">
              <div class="notif-header-title-wrap">
                <h3 class="notif-header-title">{{ t('header.notifications') }}</h3>
                <span v-if="unreadCount > 0" class="notif-unread-pill">
                  {{ t('header.unreadCountBadge', { count: unreadCount }) }}
                </span>
              </div>
              <button
                v-if="unreadCount > 0"
                type="button"
                class="mark-all-read-btn"
                :disabled="notificationStore.isActionLoading"
                :title="t('header.markAllRead')"
                @click="handleMarkAllRead"
              >
                <svg class="check-double-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span>{{ t('header.markAllRead') }}</span>
              </button>
            </div>

            <!-- Filter Switcher -->
            <div class="notif-filter-bar">
              <button
                type="button"
                class="notif-filter-tab"
                :class="{ 'active': notificationFilter === 'ALL' }"
                @click="notificationFilter = 'ALL'"
              >
                {{ t('header.all') }}
              </button>
              <button
                type="button"
                class="notif-filter-tab"
                :class="{ 'active': notificationFilter === 'UNREAD' }"
                @click="notificationFilter = 'UNREAD'"
              >
                {{ t('header.unread') }}
                <span v-if="unreadCount > 0" class="filter-count">({{ unreadCount }})</span>
              </button>
            </div>

            <!-- Notification Items Scrollable List -->
            <div class="notif-list-container">
              <!-- Loading State -->
              <div v-if="notificationStore.isHeaderLoading" class="notif-loading-state">
                <div class="spinner-circle" />
                <p>{{ t('common.loading') }}</p>
              </div>

              <!-- Empty State -->
              <div
                v-else-if="filteredNotifications.length === 0"
                class="notif-empty-state"
              >
                <div class="empty-icon-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 class="empty-title">
                  {{ notificationFilter === 'UNREAD' ? t('header.allCaughtUp') : t('header.noNotifications') }}
                </h4>
                <p class="empty-desc">
                  {{ notificationFilter === 'UNREAD' ? t('header.allCaughtUpDesc') : t('header.noNotificationsDesc') }}
                </p>
              </div>

              <!-- Notifications Feed -->
              <div v-else class="notif-feed">
                <div
                  v-for="notif in filteredNotifications"
                  :key="notif.id"
                  class="notif-item-card"
                  :class="{ 'is-unread': !notif.read_at && notif.status !== 'READ' }"
                  tabindex="0"
                  role="button"
                  @click="handleNotificationClick(notif)"
                  @keydown.enter="handleNotificationClick(notif)"
                >
                  <!-- Type Icon Circle -->
                  <div
                    class="notif-type-icon"
                    :class="{
                      'type-attendance': notif.notification_type === 'ATTENDANCE_ABSENT',
                      'type-result': notif.notification_type === 'RESULT_RELEASED',
                      'type-fee': notif.notification_type === 'FEE_REMINDER',
                      'type-general': notif.notification_type === 'GENERAL_ANNOUNCEMENT' || notif.notification_type === 'CUSTOM',
                    }"
                  >
                    <!-- Attendance Clock/Calendar Icon -->
                    <svg v-if="notif.notification_type === 'ATTENDANCE_ABSENT'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>

                    <!-- Result Certificate Icon -->
                    <svg v-else-if="notif.notification_type === 'RESULT_RELEASED'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                      <line x1="16" y1="13" x2="8" y2="13" />
                      <line x1="16" y1="17" x2="8" y2="17" />
                      <polyline points="10 9 9 9 8 9" />
                    </svg>

                    <!-- Fee Currency Icon -->
                    <svg v-else-if="notif.notification_type === 'FEE_REMINDER'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="1" x2="12" y2="23" />
                      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                    </svg>

                    <!-- General Bell Icon -->
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                    </svg>
                  </div>

                  <!-- Content Area -->
                  <div class="notif-content-wrap">
                    <div class="notif-top-row">
                      <h5 class="notif-title">{{ notif.title }}</h5>
                      <span v-if="!notif.read_at && notif.status !== 'READ'" class="unread-glow-dot" :title="t('header.unread')" />
                    </div>

                    <p class="notif-message-text">{{ notif.message }}</p>

                    <div class="notif-bottom-row">
                      <span class="notif-time-ago">
                        {{ formatRelativeTime(notif.created_at) }}
                      </span>

                      <span v-if="notif.student_name" class="notif-tag">
                        {{ notif.student_name }}
                      </span>

                      <!-- Inline Mark Read Action -->
                      <button
                        v-if="!notif.read_at && notif.status !== 'READ'"
                        type="button"
                        class="single-mark-read-btn"
                        :title="t('header.markRead')"
                        @click.stop="handleMarkSingleRead(notif.id)"
                      >
                        <svg viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                        <span>{{ t('header.markRead') }}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Dropdown Footer -->
            <div class="notif-dropdown-footer">
              <button
                type="button"
                class="view-all-notifs-btn"
                @click="handleViewAll"
              >
                <span>{{ t('header.viewAllNotifications') }}</span>
                <span class="footer-arrow">&rarr;</span>
              </button>
            </div>
          </div>
        </transition>
      </div>

      <!-- NOTE: Messages Envelope icon has been completely removed per requirement #3 -->

      <!-- Admin Profile Avatar & Metadata -->
      <div class="profile-menu-container">
        <button
          type="button"
          class="profile-trigger-btn"
          :aria-expanded="isProfileDropdownOpen"
          aria-haspopup="true"
          @click="toggleProfileDropdown"
        >
          <div class="avatar-circle">
            {{ adminDisplayName.charAt(0).toUpperCase() }}
          </div>
          <div class="profile-info-text">
            <span class="profile-name">{{ adminDisplayName }}</span>
            <span class="profile-role">{{ adminRoleName }}</span>
          </div>
        </button>

        <!-- Profile Dropdown Menu -->
        <transition name="dropdown-fade">
          <div v-if="isProfileDropdownOpen" class="profile-dropdown" role="menu">
            <div class="dropdown-header">
              <p class="user-fullname">{{ adminDisplayName }}</p>
              <p class="user-email">{{ authStore.user?.email || brandingStore.contactEmail || 'administrator@portal.edu.so' }}</p>
              <div class="dropdown-badges-row">
                <span class="user-role-badge">{{ adminRoleName }}</span>
                <span class="school-name-badge">{{ brandingStore.schoolName }}</span>
              </div>
            </div>

            <div class="dropdown-divider" />

            <router-link
              to="/admin/profile"
              class="dropdown-item"
              role="menuitem"
              @click="isProfileDropdownOpen = false"
            >
              <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              {{ t('header.myProfile') }}
            </router-link>

            <router-link
              to="/admin/settings"
              class="dropdown-item"
              role="menuitem"
              @click="isProfileDropdownOpen = false"
            >
              <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ t('header.systemSettings') }}
            </router-link>

            <div class="dropdown-divider" />

            <button
              type="button"
              class="dropdown-item logout-item"
              role="menuitem"
              @click="handleLogout"
            >
              <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              {{ t('header.signOut') }}
            </button>
          </div>
        </transition>
      </div>
    </div>
  </header>
</template>

<style scoped>
.admin-header {
  height: var(--header-height, 70px);
  background-color: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.75rem;
  position: sticky;
  top: 0;
  z-index: 30;
  width: 100%;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex: 1;
  max-width: 600px;
}

.menu-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  color: #334155;
  border-radius: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s ease;
  flex-shrink: 0;
}

.menu-toggle-btn:hover {
  background-color: #F1F5F9;
}

.hamburger-icon {
  width: 20px;
  height: 20px;
}

/* Expandable Search Bar with Ctrl + K */
.search-container {
  display: flex;
  align-items: center;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  width: 100%;
  max-width: 480px;
  gap: 0.65rem;
  transition: all 0.2s ease;
}

.search-container:focus-within {
  background-color: #FFFFFF;
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #94A3B8;
  flex-shrink: 0;
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.86rem;
  color: #1E293B;
  width: 100%;
}

.search-input::placeholder {
  color: #94A3B8;
}

.shortcut-badge {
  background-color: #FFFFFF;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  padding: 0.15rem 0.45rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748B;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Right Section */
.header-right {
  display: flex;
  align-items: center;
  gap: 1.15rem;
  flex-shrink: 0;
}

/* 1. Language Dropdown Pill */
.language-container {
  position: relative;
}

.language-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 9999px;
  padding: 0.4rem 0.8rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  user-select: none;
}

.language-pill:hover,
.language-pill.is-active {
  background-color: #F1F5F9;
  border-color: #CBD5E1;
  color: #0F172A;
}

.flag-icon {
  font-size: 1.05rem;
  line-height: 1;
}

.lang-text {
  letter-spacing: 0.02em;
}

.dropdown-chevron {
  width: 16px;
  height: 16px;
  color: #64748B;
  transition: transform 0.2s ease;
}

.dropdown-chevron.rotate-180 {
  transform: rotate(180deg);
}

.language-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
  width: 220px;
  padding: 0.5rem;
  z-index: 50;
}

.dropdown-header-sm {
  padding: 0.4rem 0.6rem;
  border-bottom: 1px solid #F1F5F9;
  margin-bottom: 0.35rem;
}

.header-sm-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94A3B8;
}

.lang-option-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.15s ease;
}

.lang-option-btn:hover {
  background-color: #F8FAFC;
}

.lang-option-btn.selected {
  background-color: #EFF6FF;
}

.lang-option-flag {
  font-size: 1.25rem;
  line-height: 1;
}

.lang-option-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.lang-option-name {
  font-size: 0.84rem;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.2;
}

.lang-option-btn.selected .lang-option-name {
  color: #1D4ED8;
}

.lang-option-sub {
  font-size: 0.72rem;
  color: #64748B;
}

.lang-check-icon {
  width: 18px;
  height: 18px;
  color: #2563EB;
}

/* 2. Notifications Dropdown & Bell */
.notification-container {
  position: relative;
}

.header-icon-btn {
  position: relative;
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background-color: #F8FAFC;
  border: 1px solid #E2E8F0;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}

.header-icon-btn:hover,
.header-icon-btn.is-active {
  background-color: #F1F5F9;
  color: #1E293B;
  border-color: #CBD5E1;
}

.header-svg-icon {
  width: 20px;
  height: 20px;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: #EF4444;
  color: #FFFFFF;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 9999px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.4);
  animation: pulse-badge 2s infinite ease-in-out;
}

@keyframes pulse-badge {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
}

/* Notifications Dropdown Container */
.notifications-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: -60px;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 16px;
  box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.14), 0 6px 12px -4px rgba(15, 23, 42, 0.08);
  width: 390px;
  max-width: calc(100vw - 32px);
  z-index: 50;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notif-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.15rem;
  border-bottom: 1px solid #F1F5F9;
  background-color: #FFFFFF;
}

.notif-header-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.notif-header-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.notif-unread-pill {
  font-size: 0.7rem;
  font-weight: 700;
  color: #DC2626;
  background-color: #FEF2F2;
  border: 1px solid #FEE2E2;
  border-radius: 9999px;
  padding: 0.12rem 0.5rem;
}

.mark-all-read-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: transparent;
  border: none;
  font-size: 0.74rem;
  font-weight: 600;
  color: #2563EB;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.mark-all-read-btn:hover {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

.mark-all-read-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.check-double-icon {
  width: 14px;
  height: 14px;
}

/* Filter bar (All / Unread) */
.notif-filter-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0.45rem 1.15rem;
  background-color: #F8FAFC;
  border-bottom: 1px solid #F1F5F9;
}

.notif-filter-tab {
  background: transparent;
  border: none;
  font-size: 0.78rem;
  font-weight: 600;
  color: #64748B;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.notif-filter-tab:hover {
  color: #1E293B;
}

.notif-filter-tab.active {
  background-color: #FFFFFF;
  color: #0F172A;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.filter-count {
  color: #EF4444;
  font-weight: 700;
}

/* List container */
.notif-list-container {
  max-height: 380px;
  overflow-y: auto;
}

.notif-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2.5rem 1.5rem;
  color: #64748B;
  font-size: 0.82rem;
}

.spinner-circle {
  width: 24px;
  height: 24px;
  border: 2.5px solid #E2E8F0;
  border-top-color: #2563EB;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty State */
.notif-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2.5rem 1.5rem;
}

.empty-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #F0FDF4;
  color: #16A34A;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.empty-icon-wrap svg {
  width: 24px;
  height: 24px;
}

.empty-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 0.25rem 0;
}

.empty-desc {
  font-size: 0.75rem;
  color: #64748B;
  margin: 0;
  max-width: 260px;
  line-height: 1.4;
}

/* Notification Items Feed */
.notif-feed {
  display: flex;
  flex-direction: column;
}

.notif-item-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1.15rem;
  border-bottom: 1px solid #F8FAFC;
  cursor: pointer;
  background-color: #FFFFFF;
  transition: all 0.15s ease;
  position: relative;
  text-align: left;
}

.notif-item-card:hover {
  background-color: #F8FAFC;
}

.notif-item-card.is-unread {
  background-color: #F0F7FF;
}

.notif-item-card.is-unread:hover {
  background-color: #E6F0FD;
}

/* Notification Type Icon Circles */
.notif-type-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.notif-type-icon svg {
  width: 17px;
  height: 17px;
}

.type-attendance {
  background-color: #FEF3C7;
  color: #D97706;
}

.type-result {
  background-color: #DCFCE7;
  color: #16A34A;
}

.type-fee {
  background-color: #DBEAFE;
  color: #2563EB;
}

.type-general {
  background-color: #F3E8FF;
  color: #9333EA;
}

/* Content Area */
.notif-content-wrap {
  flex: 1;
  min-width: 0;
}

.notif-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.notif-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notif-item-card.is-unread .notif-title {
  font-weight: 700;
  color: #0F172A;
}

.unread-glow-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #2563EB;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
  flex-shrink: 0;
}

.notif-message-text {
  font-size: 0.75rem;
  color: #475569;
  margin: 0 0 0.35rem 0;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-bottom-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.notif-time-ago {
  font-size: 0.68rem;
  color: #94A3B8;
  font-weight: 500;
}

.notif-tag {
  font-size: 0.68rem;
  color: #475569;
  background-color: #F1F5F9;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
}

.single-mark-read-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  background: transparent;
  border: none;
  font-size: 0.68rem;
  font-weight: 600;
  color: #2563EB;
  cursor: pointer;
  padding: 0.15rem 0.35rem;
  border-radius: 4px;
  margin-left: auto;
  transition: all 0.15s ease;
}

.single-mark-read-btn:hover {
  background-color: #DBEAFE;
  color: #1D4ED8;
}

.single-mark-read-btn svg {
  width: 12px;
  height: 12px;
}

/* Dropdown Footer */
.notif-dropdown-footer {
  padding: 0.65rem 1.15rem;
  border-top: 1px solid #F1F5F9;
  background-color: #F8FAFC;
  text-align: center;
}

.view-all-notifs-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background: transparent;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  color: #2563EB;
  cursor: pointer;
  width: 100%;
  padding: 0.4rem;
  border-radius: 8px;
  transition: all 0.15s ease;
}

.view-all-notifs-btn:hover {
  background-color: #EFF6FF;
  color: #1D4ED8;
}

.footer-arrow {
  transition: transform 0.15s ease;
}

.view-all-notifs-btn:hover .footer-arrow {
  transform: translateX(3px);
}

/* User Profile */
.profile-menu-container {
  position: relative;
}

.profile-trigger-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 12px;
  transition: background-color 0.15s ease;
}

.profile-trigger-btn:hover {
  background-color: #F8FAFC;
}

.avatar-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1E293B;
  color: #FFFFFF;
  font-weight: 700;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(30, 41, 59, 0.25);
}

.profile-info-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.profile-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0F172A;
  line-height: 1.2;
}

.profile-role {
  font-size: 0.72rem;
  font-weight: 500;
  color: #64748B;
}

/* Profile Dropdown */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
  width: 230px;
  padding: 0.5rem;
  z-index: 50;
}

.dropdown-header {
  padding: 0.65rem 0.75rem;
}

.user-fullname {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.user-email {
  font-size: 0.75rem;
  color: #64748B;
  margin: 0.15rem 0 0.45rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-badge {
  display: inline-block;
  background-color: #EFF6FF;
  color: #2563EB;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
}

.dropdown-divider {
  height: 1px;
  background-color: #F1F5F9;
  margin: 0.35rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.75rem;
  font-size: 0.84rem;
  font-weight: 500;
  color: #334155;
  text-decoration: none;
  border-radius: 8px;
  border: none;
  background: transparent;
  width: 100%;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background-color: #F8FAFC;
  color: #0F172A;
}

.item-icon {
  width: 18px;
  height: 18px;
  color: #64748B;
}

.logout-item {
  color: #EF4444;
}

.logout-item:hover {
  background-color: #FEF2F2;
  color: #DC2626;
}

.logout-item .item-icon {
  color: #EF4444;
}

/* Animations */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ========================================================================= */
/* RESPONSIVE BREAKPOINTS (Tablet & Mobile UI Tuning)                        */
/* ========================================================================= */
@media (max-width: 1024px) {
  .admin-header {
    padding: 0 1.25rem;
  }

  .header-left {
    max-width: 480px;
  }
}

@media (max-width: 768px) {
  .admin-header {
    height: 64px;
    padding: 0 1rem;
    gap: 0.75rem;
  }

  .shortcut-badge {
    display: none;
  }

  .profile-info-text {
    display: none;
  }

  .header-right {
    gap: 0.75rem;
  }

  .search-container {
    padding: 0.45rem 0.65rem;
  }

  .search-input {
    font-size: 0.82rem;
  }

  .notifications-dropdown {
    right: -45px;
    width: 340px;
  }
}

@media (max-width: 640px) {
  .admin-header {
    padding: 0 0.75rem;
  }

  .header-left {
    gap: 0.5rem;
  }

  .search-container {
    max-width: 100%;
  }

  .language-pill {
    padding: 0.35rem 0.55rem;
  }

  .lang-text {
    font-size: 0.78rem;
  }

  .header-icon-btn {
    width: 36px;
    height: 36px;
  }

  .avatar-circle {
    width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }

  .notifications-dropdown {
    position: fixed;
    top: 66px;
    left: 12px;
    right: 12px;
    width: calc(100vw - 24px);
    max-width: 100%;
  }
}

@media (max-width: 420px) {
  .admin-header {
    padding: 0 0.5rem;
    gap: 0.4rem;
  }

  .header-left {
    gap: 0.35rem;
  }

  .header-right {
    gap: 0.45rem;
  }

  .search-container {
    padding: 0.35rem 0.5rem;
  }

  .dropdown-chevron {
    display: none;
  }
}
</style>
