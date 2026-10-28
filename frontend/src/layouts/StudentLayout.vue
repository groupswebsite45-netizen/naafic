<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { SCHOOL_BRANDING } from '../constants/branding';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isSidebarOpen = ref(false);

const studentDisplayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || 'Student';
});

async function handleLogout() {
  await authStore.logout();
  router.push('/login');
}

function closeMobileSidebar() {
  isSidebarOpen.value = false;
}
</script>

<template>
  <div class="portal-layout">
    <!-- Mobile Backdrop -->
    <div
      v-if="isSidebarOpen"
      class="sidebar-backdrop"
      @click="closeMobileSidebar"
    />

    <!-- Sidebar -->
    <aside class="portal-sidebar" :class="{ 'open': isSidebarOpen }">
      <div class="sidebar-header">
        <div class="brand-logo-wrap">
          <img :src="SCHOOL_BRANDING.logoUrl" alt="Emblem" class="brand-logo" />
        </div>
        <div class="brand-details">
          <h2 class="brand-title">{{ SCHOOL_BRANDING.shortName }}</h2>
          <span class="portal-tag">Student Portal</span>
        </div>
        <button class="close-btn" aria-label="Close Sidebar" @click="closeMobileSidebar">&times;</button>
      </div>

      <div class="sidebar-scrollable">
        <nav class="nav-links">
          <!-- 1. Dashboard -->
          <router-link
            to="/student/dashboard"
            class="nav-item"
            :class="{ active: route.path === '/student/dashboard' }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>Dashboard</span>
          </router-link>

          <!-- 2. My Profile -->
          <router-link
            to="/student/profile"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/profile') }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>My Profile</span>
          </router-link>


          <!-- 4. My Timetable -->
          <router-link
            to="/student/timetable"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/timetable') }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>My Timetable</span>
          </router-link>

          <!-- 5. My Attendance -->
          <router-link
            to="/student/attendance"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/attendance') }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <span>My Attendance</span>
          </router-link>

          <!-- 6. My Fees & Billing -->
          <router-link
            to="/student/fees"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/fees') }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>My Fees & Billing</span>
          </router-link>

          <!-- 7. My Exams & Results -->
          <router-link
            to="/student/exams"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/exams') }"
            @click="closeMobileSidebar"
          >
            <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>My Exams & Results</span>
          </router-link>
        </nav>
      </div>

      <!-- User Info & Sign Out Footer -->
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-dot" />
          <div class="user-info">
            <span class="user-name">{{ studentDisplayName }}</span>
            <span class="user-role">Student &bull; Online</span>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout">
          <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
          <button class="menu-btn" aria-label="Open Navigation Menu" @click="isSidebarOpen = true">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div class="header-title">Education Management System Student Portal</div>
        </div>
        <div class="header-user">
          <span class="badge">Student Account</span>
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
  min-height: 100vh;
  background-color: var(--bg-app);
}

.portal-sidebar {
  width: 260px;
  height: 100vh;
  background-color: #0f172a;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  border-right: 1px solid #1e293b;
  transition: transform 0.25s ease;
}

.sidebar-header {
  height: 70px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid #1e293b;
}

.brand-logo-wrap {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-logo {
  width: 28px;
  height: 28px;
}

.brand-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.portal-tag {
  font-size: 0.7rem;
  color: #10b981;
  font-weight: 600;
}

.close-btn {
  display: none;
  margin-left: auto;
  font-size: 1.5rem;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
}

.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 0.85rem;
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
  padding: 0.7rem 0.85rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: #cbd5e1;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: #1e293b;
  color: #fff;
}

.nav-item.active {
  background: linear-gradient(90deg, #047857, #10b981);
  color: #fff;
  font-weight: 600;
}

.nav-icon {
  width: 1.2rem;
  height: 1.2rem;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 1rem;
  background-color: #0b1120;
  border-top: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem;
  background: #1e293b;
  border-radius: 6px;
}

.user-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
}

.user-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
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
  padding: 0.5rem;
  border-radius: 6px;
  color: #f87171;
  background: rgba(239, 68, 68, 0.1);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background: #ef4444;
  color: #fff;
}

.portal-main {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: calc(100% - 260px);
}

.portal-header {
  height: 70px;
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  position: sticky;
  top: 0;
  z-index: 30;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-primary);
  padding: 0.35rem;
  border-radius: 6px;
}

.menu-btn:hover {
  background-color: var(--bg-surface-secondary);
}

.header-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--brand-primary);
}

.badge {
  background: #dcfce7;
  color: #15803d;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: 12px;
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
  background: rgba(0,0,0,0.5);
  z-index: 35;
}

@media (max-width: 1024px) {
  .portal-sidebar {
    transform: translateX(-100%);
  }
  .portal-sidebar.open {
    transform: translateX(0);
  }
  .close-btn, .menu-btn {
    display: block;
  }
  .portal-main {
    margin-left: 0;
    width: 100%;
  }
  .portal-content {
    padding: 1rem;
  }
}
</style>
