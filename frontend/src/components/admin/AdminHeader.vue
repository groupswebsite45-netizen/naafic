<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

interface Props {
  pageTitle?: string;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'toggle-sidebar'): void;
}>();

const router = useRouter();
const authStore = useAuthStore();
const isProfileDropdownOpen = ref(false);
const searchQuery = ref('');

const adminDisplayName = computed(() => {
  return authStore.user?.full_name || 'Abdikadir Ali Mire';
});

const adminRoleName = computed(() => {
  if (authStore.isSuperAdmin) return 'Super Admin';
  return 'Super Admin';
});

function toggleProfileDropdown() {
  isProfileDropdownOpen.value = !isProfileDropdownOpen.value;
}

function closeDropdown(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.profile-menu-container')) {
    isProfileDropdownOpen.value = false;
  }
}

async function handleLogout() {
  isProfileDropdownOpen.value = false;
  await authStore.logout();
  router.push('/login');
}

onMounted(() => {
  window.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown);
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
          placeholder="Search students, teachers, classes, subjects, exams..."
          aria-label="Search across system"
        />
        <div class="shortcut-badge">
          <span>Ctrl + K</span>
        </div>
      </div>
    </div>

    <div class="header-right">
      <!-- Language Selector Dropdown Pill -->
      <div class="language-pill" title="Current Language: English">
        <span class="flag-icon">🇺🇸</span>
        <span class="lang-text">EN</span>
        <svg class="dropdown-chevron" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>

      <!-- Notification Bell with Red Badge "3" -->
      <button type="button" class="header-icon-btn" aria-label="Notifications" title="3 New Notifications" @click="router.push('/admin/notifications')">
        <svg class="header-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <span class="notification-badge">3</span>
      </button>

      <!-- Messages Envelope with Red Badge "5" -->
      <button type="button" class="header-icon-btn" aria-label="Messages" title="5 Unread Messages">
        <svg class="header-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span class="notification-badge">5</span>
      </button>

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

        <!-- Dropdown Menu -->
        <transition name="dropdown-fade">
          <div v-if="isProfileDropdownOpen" class="profile-dropdown" role="menu">
            <div class="dropdown-header">
              <p class="user-fullname">{{ adminDisplayName }}</p>
              <p class="user-email">{{ authStore.user?.email || 'admin@hawlwadaagschool.edu.so' }}</p>
              <span class="user-role-badge">Super Admin</span>
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
              My Profile
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
              System Settings
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
              Sign Out
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
}

.language-pill:hover {
  background-color: #F1F5F9;
}

.flag-icon {
  font-size: 1rem;
}

.dropdown-chevron {
  width: 16px;
  height: 16px;
  color: #64748B;
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

.header-icon-btn:hover {
  background-color: #F1F5F9;
  color: #1E293B;
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
  padding: 0 3px;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.4);
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

/* Dropdown */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
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

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
