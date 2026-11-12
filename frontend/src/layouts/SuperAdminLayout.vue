<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { inquiryService } from '../services/inquiryService';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// Navigation states
const isCollapsed = ref(false);
const isMobileOpen = ref(false);
const isUserMenuOpen = ref(false);
const isLangMenuOpen = ref(false);
const currentLang = ref<'en' | 'so'>('en');
const searchQuery = ref('');
const unreadInquiries = ref(0);

async function fetchInquiryBadge() {
  try {
    const stats = await inquiryService.getInquiryStats();
    unreadInquiries.value = stats.unread;
  } catch (e) {
    // ignore
  }
}

let badgeTimer: any = null;
onMounted(() => {
  fetchInquiryBadge();
  badgeTimer = setInterval(fetchInquiryBadge, 25000);
});

onUnmounted(() => {
  if (badgeTimer) clearInterval(badgeTimer);
});

// Primary navigation items
const navItems = [
  {
    name: 'Dashboard',
    to: '/super-admin/dashboard',
    icon: 'home',
  },
  {
    name: 'Inbox',
    to: '/super-admin/inbox',
    icon: 'inbox',
  },
  {
    name: 'Institutions',
    to: '/super-admin/institutions',
    icon: 'institutions',
  },
  {
    name: 'Subscriptions',
    to: '/super-admin/subscriptions',
    icon: 'subscriptions',
  },
  {
    name: 'Payments',
    to: '/super-admin/payments',
    icon: 'payments',
  },
  {
    name: 'Reports',
    to: '/super-admin/reports',
    icon: 'reports',
  },
  {
    name: 'Settings',
    to: '/super-admin/settings',
    icon: 'settings',
  },
];

function toggleSidebar() {
  if (window.innerWidth < 1024) {
    isMobileOpen.value = !isMobileOpen.value;
  } else {
    isCollapsed.value = !isCollapsed.value;
  }
}

function closeMobileSidebar() {
  isMobileOpen.value = false;
}

function toggleUserMenu() {
  isUserMenuOpen.value = !isUserMenuOpen.value;
  if (isUserMenuOpen.value) isLangMenuOpen.value = false;
}

function toggleLangMenu() {
  isLangMenuOpen.value = !isLangMenuOpen.value;
  if (isLangMenuOpen.value) isUserMenuOpen.value = false;
}

function selectLanguage(lang: 'en' | 'so') {
  currentLang.value = lang;
  isLangMenuOpen.value = false;
}

async function handleLogout() {
  await authStore.logout();
  router.push('/login');
}

function handleSearch(e: KeyboardEvent) {
  if (e.key === 'Enter' && searchQuery.value.trim()) {
    router.push({
      path: '/super-admin/institutions',
      query: { q: searchQuery.value.trim() },
    });
  }
}

function handleGlobalClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.sa-user-menu-wrapper')) {
    isUserMenuOpen.value = false;
  }
  if (!target.closest('.sa-lang-box')) {
    isLangMenuOpen.value = false;
  }
}

onMounted(() => {
  window.addEventListener('click', handleGlobalClick);
});

onUnmounted(() => {
  window.removeEventListener('click', handleGlobalClick);
});
</script>

<template>
  <div class="super-admin-layout" :class="{ 'sidebar-collapsed': isCollapsed }">
    <!-- Mobile Backdrop Overlay -->
    <transition name="fade">
      <div
        v-if="isMobileOpen"
        class="sidebar-backdrop"
        @click="closeMobileSidebar"
      ></div>
    </transition>

    <!-- Left Deep Navy Sidebar -->
    <aside
      class="sa-sidebar"
      :class="{
        'collapsed': isCollapsed,
        'mobile-open': isMobileOpen
      }"
    >
      <!-- Logo Header Section -->
      <div class="sa-logo-section">
        <router-link to="/super-admin/dashboard" class="sa-logo-link" @click="closeMobileSidebar">
          <!-- Crown & Shield Emblem -->
          <div class="sa-emblem-wrap">
            <!-- Crown SVG -->
            <svg class="sa-crown-svg" viewBox="0 0 24 14" fill="none">
              <path d="M2 13L4 3L8.5 8L12 1L15.5 8L20 3L22 13H2Z" fill="#F59E0B" stroke="#D97706" stroke-width="0.75" />
              <circle cx="12" cy="1.5" r="1.5" fill="#FBBF24" />
              <circle cx="4" cy="3.5" r="1.2" fill="#FBBF24" />
              <circle cx="20" cy="3.5" r="1.2" fill="#FBBF24" />
            </svg>
            <!-- Shield Mark -->
            <div class="sa-shield-icon">
              <svg viewBox="0 0 36 40" fill="none" class="w-full h-full">
                <path d="M18 2L4 7V18C4 28 10 36 18 39C26 36 32 28 32 18V7L18 2Z" fill="#0A2558" stroke="#1E40AF" stroke-width="1.5"/>
                <!-- Orange "S" -->
                <path d="M22.5 12C20.5 10.8 17.5 10.5 15 11.8C13 12.8 12 14.5 12 16.5C12 20 23.5 19 23.5 24C23.5 27.5 19.5 29 16 28C13.5 27.2 12 25.5 11.5 24.5" stroke="#FF6500" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- Typography (Hidden when collapsed) -->
          <div v-show="!isCollapsed" class="sa-brand-text">
            <span class="sa-brand-name">SOMROYAL</span>
            <span class="sa-brand-tagline">SUPER ADMIN PORTAL</span>
          </div>
        </router-link>

        <!-- Close button for mobile drawer -->
        <button class="sa-close-mobile-btn" @click="closeMobileSidebar" aria-label="Close menu">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Menu -->
      <nav class="sa-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="sa-nav-item"
          :class="{ 'active': route.path === item.to || (item.to !== '/super-admin/dashboard' && route.path.startsWith(item.to)) }"
          :title="isCollapsed ? item.name : undefined"
          @click="closeMobileSidebar"
        >
          <!-- Home Icon -->
          <svg v-if="item.icon === 'home'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1V9.5z" />
          </svg>

          <!-- Inbox Icon -->
          <svg v-else-if="item.icon === 'inbox'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>

          <!-- Institutions (Pillars) Icon -->
          <svg v-else-if="item.icon === 'institutions'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 21h18M3 7v14M21 7v14M6 21V11M10 21V11M14 21V11M18 21V11M12 3L2 7h20L12 3z" />
          </svg>

          <!-- Subscriptions (Stacked Database) Icon -->
          <svg v-else-if="item.icon === 'subscriptions'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <ellipse cx="12" cy="5" rx="9" ry="3" />
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
          </svg>

          <!-- Payments (Card/Wallet) Icon -->
          <svg v-else-if="item.icon === 'payments'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="5" width="20" height="14" rx="2" />
            <line x1="2" y1="10" x2="22" y2="10" />
            <line x1="6" y1="15" x2="10" y2="15" />
          </svg>

          <!-- Reports (Analytics Columns) Icon -->
          <svg v-else-if="item.icon === 'reports'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
            <line x1="2" y1="20" x2="22" y2="20" />
          </svg>

          <!-- Settings (Gear) Icon -->
          <svg v-else-if="item.icon === 'settings'" class="sa-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>

          <span v-show="!isCollapsed" class="sa-nav-label">{{ item.name }}</span>
          <span v-if="item.name === 'Inbox' && unreadInquiries > 0" class="sa-sidebar-unread-badge">
            {{ unreadInquiries }}
          </span>
        </router-link>
      </nav>

      <!-- Bottom Dedicated Support Card -->
      <div class="sa-sidebar-footer">
        <div v-if="!isCollapsed" class="sa-support-card">
          <div class="sa-support-header">
            <div class="sa-support-icon">
              <svg class="w-5 h-5 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
                <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
              </svg>
            </div>
            <div>
              <h4 class="sa-support-title">Need Help?</h4>
              <p class="sa-support-desc">Somroyal 24/7 technical assistance.</p>
            </div>
          </div>
          <router-link to="/super-admin/settings" class="sa-support-btn" @click="closeMobileSidebar">
            <span>Contact Support</span>
            <svg class="w-4 h-4 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </router-link>
        </div>

        <!-- Collapsed Icon-only Support Indicator -->
        <router-link
          v-else
          to="/super-admin/settings"
          class="sa-collapsed-support"
          title="Contact Support"
        >
          <svg class="w-5 h-5 text-orange-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
            <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
          </svg>
        </router-link>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="sa-main-wrapper" :class="{ 'collapsed': isCollapsed }">
      <!-- Clean Top Header Bar -->
      <header class="sa-topbar">
        <!-- Left: Sidebar Toggle & Search Input -->
        <div class="sa-topbar-left">
          <button class="sa-hamburger-btn" @click="toggleSidebar" aria-label="Toggle navigation" title="Toggle sidebar">
            <svg class="sa-hamburger-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5" />
            </svg>
          </button>

          <!-- Search Bar with Ctrl + K badge -->
          <div class="sa-search-box">
            <svg class="sa-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              v-model="searchQuery"
              @keydown="handleSearch"
              class="sa-search-input"
              placeholder="Search institutions, subscriptions, payments..."
            />
            <span class="sa-search-shortcut">Ctrl + K</span>
          </div>
        </div>

        <!-- Right Controls: Language Dropdown, Notifications, Messages, Super Admin Profile -->
        <div class="sa-topbar-right">
          <!-- Language Selector -->
          <div class="sa-lang-box" @click.stop>
            <button
              type="button"
              class="sa-lang-dropdown-btn"
              @click="toggleLangMenu"
              aria-haspopup="true"
            >
              <!-- Vector Flag -->
              <span class="sa-flag-wrap" v-if="currentLang === 'en'" title="United States">
                <svg class="sa-flag-svg" viewBox="0 0 640 480">
                  <path fill="#bd3d44" d="M0 0h640v480H0z"/>
                  <path stroke="#fff" stroke-width="37" d="M0 55.5h640M0 129h640M0 203h640M0 277h640M0 351h640M0 424.5h640"/>
                  <path fill="#192f5d" d="M0 0h260v259H0z"/>
                  <circle cx="35" cy="35" r="7" fill="#fff"/>
                  <circle cx="85" cy="35" r="7" fill="#fff"/>
                  <circle cx="135" cy="35" r="7" fill="#fff"/>
                  <circle cx="185" cy="35" r="7" fill="#fff"/>
                  <circle cx="235" cy="35" r="7" fill="#fff"/>
                  <circle cx="60" cy="70" r="7" fill="#fff"/>
                  <circle cx="110" cy="70" r="7" fill="#fff"/>
                  <circle cx="160" cy="70" r="7" fill="#fff"/>
                  <circle cx="210" cy="70" r="7" fill="#fff"/>
                  <circle cx="35" cy="105" r="7" fill="#fff"/>
                  <circle cx="85" cy="105" r="7" fill="#fff"/>
                  <circle cx="135" cy="105" r="7" fill="#fff"/>
                  <circle cx="185" cy="105" r="7" fill="#fff"/>
                  <circle cx="235" cy="105" r="7" fill="#fff"/>
                  <circle cx="60" cy="140" r="7" fill="#fff"/>
                  <circle cx="110" cy="140" r="7" fill="#fff"/>
                  <circle cx="160" cy="140" r="7" fill="#fff"/>
                  <circle cx="210" cy="140" r="7" fill="#fff"/>
                  <circle cx="35" cy="175" r="7" fill="#fff"/>
                  <circle cx="85" cy="175" r="7" fill="#fff"/>
                  <circle cx="135" cy="175" r="7" fill="#fff"/>
                  <circle cx="185" cy="175" r="7" fill="#fff"/>
                  <circle cx="235" cy="175" r="7" fill="#fff"/>
                  <circle cx="60" cy="210" r="7" fill="#fff"/>
                  <circle cx="110" cy="210" r="7" fill="#fff"/>
                  <circle cx="160" cy="210" r="7" fill="#fff"/>
                  <circle cx="210" cy="210" r="7" fill="#fff"/>
                </svg>
              </span>
              <span class="sa-flag-wrap" v-else title="Somalia">
                <svg class="sa-flag-svg" viewBox="0 0 640 480">
                  <rect width="640" height="480" fill="#4189DD"/>
                  <polygon points="320,120 357,235 478,235 380,306 418,421 320,350 222,421 260,306 162,235 283,235" fill="#FFFFFF"/>
                </svg>
              </span>
              <span class="sa-lang-label">{{ currentLang === 'en' ? 'EN' : 'SO' }}</span>
              <svg class="sa-dropdown-chevron" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>

            <!-- Dropdown Options -->
            <transition name="fade-slide">
              <div v-if="isLangMenuOpen" class="sa-lang-dropdown-menu">
                <button
                  type="button"
                  class="sa-lang-option"
                  :class="{ 'active': currentLang === 'en' }"
                  @click="selectLanguage('en')"
                >
                  <span class="sa-flag-wrap">
                    <svg class="sa-flag-svg" viewBox="0 0 640 480">
                      <path fill="#bd3d44" d="M0 0h640v480H0z"/>
                      <path stroke="#fff" stroke-width="37" d="M0 55.5h640M0 129h640M0 203h640M0 277h640M0 351h640M0 424.5h640"/>
                      <path fill="#192f5d" d="M0 0h260v259H0z"/>
                    </svg>
                  </span>
                  <span class="sa-lang-opt-name">English</span>
                </button>
                <button
                  type="button"
                  class="sa-lang-option"
                  :class="{ 'active': currentLang === 'so' }"
                  @click="selectLanguage('so')"
                >
                  <span class="sa-flag-wrap">
                    <svg class="sa-flag-svg" viewBox="0 0 640 480">
                      <rect width="640" height="480" fill="#4189DD"/>
                      <polygon points="320,120 357,235 478,235 380,306 418,421 320,350 222,421 260,306 162,235 283,235" fill="#FFFFFF"/>
                    </svg>
                  </span>
                  <span class="sa-lang-opt-name">Soomaali</span>
                </button>
              </div>
            </transition>
          </div>

          <!-- Notification Bell with Counter -->
          <div class="sa-icon-btn-wrap">
            <button class="sa-header-icon-btn" aria-label="Notifications" title="System Notifications">
              <svg class="sa-header-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span class="sa-header-badge">3</span>
            </button>
          </div>

          <!-- Messages Envelope Icon with Dynamic Unread Counter -->
          <div class="sa-icon-btn-wrap">
            <router-link
              to="/super-admin/inbox"
              class="sa-header-icon-btn"
              aria-label="Messages"
              title="Super Admin Inquiries & Leads Inbox"
            >
              <svg class="sa-header-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke-linecap="round" stroke-linejoin="round" />
                <polyline points="22,6 12,13 2,6" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <span v-if="unreadInquiries > 0" class="sa-header-badge sa-header-badge-pulse">{{ unreadInquiries }}</span>
            </router-link>
          </div>

          <!-- Super Admin Profile Dropdown -->
          <div class="sa-user-menu-wrapper" @click.stop>
            <button class="sa-user-btn" @click="toggleUserMenu" :aria-expanded="isUserMenuOpen">
              <div class="sa-user-avatar">
                <span>SA</span>
              </div>
              <div class="sa-user-info">
                <span class="sa-user-name">Somroyal Admin</span>
                <span class="sa-user-role">Super Administrator</span>
              </div>
              <svg class="sa-user-chevron" :class="{ 'rotate-180': isUserMenuOpen }" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>

            <!-- Dropdown Menu -->
            <transition name="fade-slide">
              <div v-if="isUserMenuOpen" class="sa-dropdown-menu">
                <div class="sa-dropdown-header">
                  <p class="sa-dd-name">Somroyal Super Admin</p>
                  <p class="sa-dd-email">superadmin@somroyal.com</p>
                </div>
                <div class="sa-dropdown-divider"></div>
                <router-link to="/super-admin/settings" class="sa-dd-item" @click="isUserMenuOpen = false">
                  <svg class="sa-dd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
                  </svg>
                  System Settings
                </router-link>
                <router-link to="/super-admin/inbox" class="sa-dd-item" @click="isUserMenuOpen = false">
                  <svg class="sa-dd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  CRM Inquiries
                </router-link>
                <div class="sa-dropdown-divider"></div>
                <button class="sa-dd-item sa-dd-danger" @click="handleLogout">
                  <svg class="sa-dd-icon sa-icon-danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                  Sign Out
                </button>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <!-- Main Body View -->
      <main class="sa-content-view">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.super-admin-layout {
  min-height: 100vh;
  display: flex;
  background-color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
  color: #1e293b;
  position: relative;
  overflow-x: hidden;
}

/* Sidebar */
.sa-sidebar {
  width: 255px;
  background: radial-gradient(130% 90% at 20% 90%, #0d2859 0%, #061737 60%, #030d1d 100%);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 50;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.18);
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sa-sidebar.collapsed {
  width: 80px;
}

.sa-logo-section {
  padding: 1.25rem 1.15rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 72px;
  box-sizing: border-box;
}

.sa-logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  min-width: 0;
}

.sa-emblem-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex-shrink: 0;
}

.sa-crown-svg {
  width: 20px;
  height: 10px;
  margin-bottom: -2px;
}

.sa-shield-icon {
  width: 32px;
  height: 36px;
}

.sa-brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  white-space: nowrap;
}

.sa-brand-name {
  font-size: 1.15rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: 0.05em;
  background: linear-gradient(135deg, #ffffff 0%, #fed7aa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sa-brand-tagline {
  font-size: 0.58rem;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
  margin-top: 2px;
}

.sa-close-mobile-btn {
  display: none;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #cbd5e1;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 8px;
  transition: all 0.15s;
}

.sa-close-mobile-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

/* Nav */
.sa-nav {
  flex: 1;
  padding: 1.25rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  overflow-y: auto;
}

.sa-nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  gap: 0.85rem;
  white-space: nowrap;
}

.sa-sidebar.collapsed .sa-nav-item {
  justify-content: center;
  padding: 0.75rem 0;
}

.sa-nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.08);
  transform: translateX(2px);
}

.sa-sidebar.collapsed .sa-nav-item:hover {
  transform: none;
}

.sa-nav-item.active {
  background: linear-gradient(135deg, #ff6500 0%, #ea580c 100%);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(255, 101, 0, 0.35);
}

.sa-nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.sa-sidebar-unread-badge {
  margin-left: auto;
  background: #ff6500;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.2rem 0.55rem;
  border-radius: 9999px;
  line-height: 1;
  box-shadow: 0 2px 6px rgba(255, 101, 0, 0.4);
}

/* Sidebar Footer Support Card */
.sa-sidebar-footer {
  padding: 1rem 0.85rem 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.sa-support-card {
  background: linear-gradient(180deg, rgba(14, 38, 77, 0.9) 0%, rgba(7, 23, 49, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.sa-support-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.sa-support-icon {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.45rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sa-support-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.sa-support-desc {
  font-size: 0.72rem;
  color: #94a3b8;
  margin: 0.15rem 0 0;
  line-height: 1.35;
}

.sa-support-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  background: #ff6500;
  color: #ffffff;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(255, 101, 0, 0.35);
  transition: all 0.2s;
}

.sa-support-btn svg {
  width: 15px;
  height: 15px;
  stroke: #ffffff;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.sa-support-btn:hover {
  background: #e55a00;
  transform: translateY(-1px);
}

.sa-support-btn:hover svg {
  transform: translateX(2px);
}

.sa-collapsed-support {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  text-decoration: none;
  transition: background 0.2s;
}

.sa-collapsed-support:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Main Area */
.sa-main-wrapper {
  flex: 1;
  margin-left: 255px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 0;
  transition: margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.sa-main-wrapper.collapsed {
  margin-left: 80px;
}

/* Topbar */
.sa-topbar {
  height: 72px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.75rem;
  position: sticky;
  top: 0;
  z-index: 40;
  gap: 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.sa-topbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
  max-width: 580px;
}

.sa-hamburger-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #1e293b;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.sa-hamburger-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.sa-hamburger-svg {
  width: 20px;
  height: 20px;
  stroke: #1e293b;
  flex-shrink: 0;
  display: block;
}

.sa-search-box {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0 0.85rem;
  height: 42px;
  width: 100%;
  gap: 0.65rem;
  transition: all 0.15s ease;
}

.sa-search-box:focus-within {
  background: #ffffff;
  border-color: #ff6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.sa-search-icon {
  width: 17px;
  height: 17px;
  color: #94a3b8;
  stroke: #94a3b8;
  flex-shrink: 0;
}

.sa-search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  width: 100%;
  padding: 0;
}

.sa-search-input::placeholder {
  color: #94a3b8;
}

.sa-search-shortcut {
  font-size: 0.72rem;
  font-weight: 600;
  color: #64748b;
  background: #e2e8f0;
  padding: 0.2rem 0.5rem;
  border-radius: 5px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Topbar Right */
.sa-topbar-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-shrink: 0;
}

/* Language Box */
.sa-lang-box {
  position: relative;
  flex-shrink: 0;
}

.sa-lang-dropdown-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.35rem 0.65rem;
  height: 40px;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  flex-shrink: 0;
  white-space: nowrap;
  transition: all 0.15s;
}

.sa-lang-dropdown-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.sa-flag-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 3px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
  width: 20px;
  height: 14px;
}

.sa-flag-svg {
  width: 20px;
  height: 14px;
  display: block;
}

.sa-dropdown-chevron {
  width: 14px;
  height: 14px;
  color: #64748b;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.sa-lang-dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 0.4rem;
  width: 140px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.sa-lang-option {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  font-size: 0.82rem;
  color: #334155;
  border: none;
  background: transparent;
  width: 100%;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.sa-lang-option:hover {
  background: #f1f5f9;
}

.sa-lang-option.active {
  background: #eff6ff;
  color: #1e40af;
  font-weight: 700;
}

.sa-lang-opt-name {
  font-weight: 600;
}

/* Icon Buttons with badge */
.sa-icon-btn-wrap {
  position: relative;
  flex-shrink: 0;
}

.sa-header-icon-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  flex-shrink: 0;
  padding: 0;
  transition: all 0.15s ease;
}

.sa-header-icon-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.sa-header-icon-svg {
  width: 19px;
  height: 19px;
  color: #334155;
  stroke: #334155;
  flex-shrink: 0;
}

.sa-header-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ff6500;
  color: #ffffff;
  font-size: 0.7rem;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #ffffff;
  line-height: 1;
}

.sa-header-badge-pulse {
  animation: badge-pulse 2s infinite;
}

@keyframes badge-pulse {
  0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 101, 0, 0.7); }
  70% { transform: scale(1.08); box-shadow: 0 0 0 6px rgba(255, 101, 0, 0); }
  100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 101, 0, 0); }
}

/* User Profile */
.sa-user-menu-wrapper {
  position: relative;
  flex-shrink: 0;
}

.sa-user-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.sa-user-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.sa-user-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  min-height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #061737 0%, #1e40af 100%);
  color: #ffffff;
  font-weight: 800;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(6, 23, 55, 0.2);
  flex-shrink: 0;
}

.sa-user-info {
  display: flex;
  flex-direction: column;
  text-align: left;
  white-space: nowrap;
  flex-shrink: 0;
}

.sa-user-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.25;
}

.sa-user-role {
  font-size: 0.7rem;
  font-weight: 600;
  color: #ff6500;
  line-height: 1.2;
  margin-top: 2px;
}

.sa-user-chevron {
  width: 14px;
  height: 14px;
  color: #64748b;
  flex-shrink: 0;
  margin-left: 2px;
  transition: transform 0.2s ease;
}

.sa-user-chevron.rotate-180 {
  transform: rotate(180deg);
}

.sa-dropdown-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 230px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  padding: 0.5rem;
  z-index: 50;
}

.sa-dropdown-header {
  padding: 0.6rem 0.75rem;
}

.sa-dd-name {
  font-size: 0.88rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.sa-dd-email {
  font-size: 0.72rem;
  color: #64748b;
  margin: 0.2rem 0 0;
}

.sa-dropdown-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0.4rem 0;
}

.sa-dd-item {
  display: flex;
  align-items: center;
  padding: 0.6rem 0.75rem;
  font-size: 0.82rem;
  color: #334155;
  text-decoration: none;
  border-radius: 8px;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.15s;
  box-sizing: border-box;
  font-weight: 500;
}

.sa-dd-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.sa-dd-icon {
  width: 16px;
  height: 16px;
  margin-right: 0.6rem;
  flex-shrink: 0;
  color: #64748b;
}

.sa-dd-danger {
  color: #dc2626;
}

.sa-dd-danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}

.sa-icon-danger {
  color: #dc2626;
}

/* Content Area */
.sa-content-view {
  flex: 1;
  padding: 2rem 2.25rem;
  width: 100%;
  box-sizing: border-box;
  max-width: 1680px;
  margin: 0 auto;
}

/* Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Rules */
@media (max-width: 1024px) {
  .sa-sidebar {
    transform: translateX(-100%);
    width: 270px !important;
  }

  .sa-sidebar.mobile-open {
    transform: translateX(0);
  }

  .sa-close-mobile-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sa-main-wrapper {
    margin-left: 0 !important;
  }

  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(6, 23, 55, 0.65);
    backdrop-filter: blur(4px);
    z-index: 45;
  }
}

@media (max-width: 768px) {
  .sa-topbar {
    padding: 0 1rem;
    height: 64px;
    gap: 0.75rem;
  }

  .sa-content-view {
    padding: 1.25rem 1rem;
  }

  .sa-search-box {
    max-width: 200px;
    height: 38px;
  }

  .sa-search-shortcut {
    display: none;
  }

  .sa-user-info {
    display: none;
  }

  .sa-user-btn {
    padding: 0.2rem;
    border-radius: 50%;
  }

  .sa-user-chevron {
    display: none;
  }
}

@media (max-width: 480px) {
  .sa-search-box {
    max-width: 140px;
  }

  .sa-search-input::placeholder {
    content: "Search...";
  }

  .sa-lang-label {
    display: none;
  }

  .sa-lang-dropdown-btn {
    padding: 0.35rem 0.45rem;
  }
}
</style>
