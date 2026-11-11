<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { SCHOOL_BRANDING } from '../constants/branding';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isSidebarOpen = ref(false);

// Lock body scroll when mobile drawer is open
watch(isSidebarOpen, (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : '';
  }
});

// Auto-close drawer on route navigation
watch(() => route.fullPath, () => {
  isSidebarOpen.value = false;
});

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = '';
  }
});

async function handleLogout() {
  isSidebarOpen.value = false;
  await authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="portal-layout">
    <!-- Mobile Backdrop -->
    <transition name="fade">
      <div
        v-if="isSidebarOpen"
        class="sidebar-backdrop"
        aria-hidden="true"
        @click="isSidebarOpen = false"
      />
    </transition>

    <!-- Sidebar Drawer -->
    <aside
      class="portal-sidebar"
      :class="{ 'open': isSidebarOpen }"
      :aria-hidden="!isSidebarOpen"
      aria-label="Teacher Navigation"
    >
      <div class="sidebar-header">
        <div class="brand-logo-wrap">
          <img :src="SCHOOL_BRANDING.logoUrl" alt="Education Management System Emblem" class="brand-logo" />
        </div>
        <div class="brand-details">
          <h2 class="brand-title">{{ SCHOOL_BRANDING.shortName }}</h2>
          <span class="portal-tag">Teacher Portal</span>
        </div>
        <button
          class="close-btn"
          aria-label="Close Navigation Menu"
          @click="isSidebarOpen = false"
        >
          &times;
        </button>
      </div>

      <div class="sidebar-scrollable">
        <nav class="nav-links">
          <router-link
            to="/teacher/dashboard"
            class="nav-item"
            :class="{ active: route.path === '/teacher/dashboard' }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>Dashboard</span>
          </router-link>

          <router-link
            to="/teacher/classes"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/classes') }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span>My Classes & Subjects</span>
          </router-link>

          <router-link
            to="/teacher/students"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/students') }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span>Assigned Students</span>
          </router-link>

          <router-link
            to="/teacher/attendance"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/attendance') }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Class Attendance</span>
          </router-link>

          <router-link
            to="/teacher/timetable"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/timetable') }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>My Timetable</span>
          </router-link>

          <router-link
            to="/teacher/exams"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/exams') }"
            @click="isSidebarOpen = false"
          >
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <span>Exams & Marks Entry</span>
          </router-link>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar-circle">
            {{ (authStore.user?.full_name || authStore.user?.username || 'T').charAt(0).toUpperCase() }}
          </div>
          <div class="user-info">
            <span class="user-name">{{ authStore.user?.full_name || authStore.user?.username }}</span>
            <span class="user-role">Teaching Faculty</span>
          </div>
        </div>
        <button class="logout-btn" aria-label="Sign Out" @click="handleLogout">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="portal-main">
      <header class="portal-header">
        <div class="header-left">
          <button
            class="menu-btn"
            aria-label="Open Navigation Menu"
            @click="isSidebarOpen = true"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="menu-svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div class="brand-mobile-heading">
            <span class="header-school-name">{{ SCHOOL_BRANDING.shortName }}</span>
            <span class="header-portal-name">Teacher Portal</span>
          </div>
        </div>

        <div class="header-right">
          <span class="faculty-badge">Faculty Account</span>
          <div class="header-user-avatar" :title="authStore.user?.full_name || authStore.user?.username">
            {{ (authStore.user?.full_name || authStore.user?.username || 'T').charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <main class="portal-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.portal-layout {
  display: flex;
  min-height: 100dvh;
  background-color: var(--bg-app);
  width: 100%;
  max-width: 100%;
  overflow-x: clip;
}

.portal-sidebar {
  width: 260px;
  max-width: min(260px, 85dvw);
  height: 100dvh;
  background-color: #0f172a;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  border-right: 1px solid #1e293b;
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.sidebar-header {
  height: 68px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid #1e293b;
  flex-shrink: 0;
}

.brand-logo-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-logo {
  width: 26px;
  height: 26px;
  object-fit: contain;
}

.brand-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.brand-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.portal-tag {
  font-size: 0.68rem;
  color: #38bdf8;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.close-btn {
  display: none;
  margin-left: auto;
  font-size: 1.6rem;
  line-height: 1;
  color: #94a3b8;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.4rem;
  min-width: 44px;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: color 0.2s, background-color 0.2s;
}

.close-btn:hover {
  color: #ffffff;
  background-color: #1e293b;
}

.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0.75rem;
  -webkit-overflow-scrolling: touch;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.85rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: #cbd5e1;
  border-radius: 8px;
  text-decoration: none;
  min-height: 44px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-item:hover {
  background-color: #1e293b;
  color: #ffffff;
}

.nav-item.active {
  background: linear-gradient(90deg, #0284c7, #0369a1);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
}

.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 0.85rem 1rem;
  background-color: #0b1120;
  border-top: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  flex-shrink: 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0.65rem;
  background: #1e293b;
  border-radius: 8px;
  overflow: hidden;
}

.user-avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #0284c7;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.68rem;
  color: #94a3b8;
  display: block;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem;
  min-height: 44px;
  border-radius: 8px;
  color: #f87171;
  background: rgba(239, 68, 68, 0.1);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(239, 68, 68, 0.2);
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}

.portal-main {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 0;
  width: calc(100% - 260px);
}

.portal-header {
  height: 68px;
  background: var(--bg-surface, #ffffff);
  border-bottom: 1px solid var(--border-subtle, #e2e8f0);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  position: sticky;
  top: 0;
  z-index: 30;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-primary, #0f172a);
  padding: 0.4rem;
  min-width: 44px;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.menu-btn:hover {
  background-color: var(--bg-surface-secondary, #f8fafc);
}

.menu-svg {
  width: 24px;
  height: 24px;
}

.brand-mobile-heading {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header-school-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--brand-primary, #0284c7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.header-portal-name {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-muted, #64748b);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.faculty-badge {
  background: #e0f2fe;
  color: #0369a1;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.3rem 0.65rem;
  border-radius: 12px;
  white-space: nowrap;
}

.header-user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #0284c7;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.portal-content {
  flex: 1;
  padding: 1.5rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(2px);
  z-index: 35;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .portal-sidebar {
    transform: translateX(-100%);
  }
  .portal-sidebar.open {
    transform: translateX(0);
  }
  .close-btn {
    display: flex;
  }
  .menu-btn {
    display: flex;
  }
  .portal-main {
    margin-left: 0;
    width: 100%;
  }
  .portal-header {
    padding: 0 1rem;
    height: 64px;
  }
  .portal-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .faculty-badge {
    display: none;
  }
  .header-school-name {
    font-size: 0.95rem;
  }
  .portal-content {
    padding: 0.75rem;
  }
}

@media (max-width: 359px) {
  .portal-content {
    padding: 0.5rem;
  }
}
</style>
