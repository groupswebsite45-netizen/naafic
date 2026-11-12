<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useSchoolBrandingStore } from '../stores/schoolBranding';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const brandingStore = useSchoolBrandingStore();

const isSidebarOpen = ref(false);

const studentDisplayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || 'Student';
});

const studentInitials = computed(() => {
  const name = studentDisplayName.value.trim();
  const parts = name.split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

const currentPageTitle = computed(() => {
  if (route.path === '/student/dashboard') return 'Dashboard';
  if (route.path.startsWith('/student/profile')) return 'My Profile';
  if (route.path.startsWith('/student/class')) return 'My Class & Subjects';
  if (route.path.startsWith('/student/timetable')) return 'My Timetable';
  if (route.path.startsWith('/student/attendance')) return 'My Attendance';
  if (route.path.startsWith('/student/fees')) return 'My Fees & Billing';
  if (route.path.startsWith('/student/exams')) return 'My Exams & Results';
  return (route.meta.title as string) || 'Student Portal';
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
    <!-- Mobile Backdrop with Blur -->
    <transition name="fade">
      <div
        v-if="isSidebarOpen"
        class="sidebar-backdrop"
        aria-hidden="true"
        @click="closeMobileSidebar"
      />
    </transition>

    <!-- Somroyal Student Sidebar -->
    <aside class="portal-sidebar" :class="{ 'open': isSidebarOpen }">
      <!-- Sidebar Header Branding -->
      <div class="sidebar-header">
        <div class="brand-logo-wrap">
          <img
            v-if="brandingStore.schoolLogo"
            :src="brandingStore.schoolLogo"
            :alt="brandingStore.schoolName"
            class="school-header-img"
            style="width: 36px; height: 36px; object-fit: contain; border-radius: 8px; background: white; padding: 2px;"
          />
          <div v-else class="somroyal-s" style="background: linear-gradient(135deg, #FF6500 0%, #FF8A00 100%);">
            <span style="font-weight: 800; color: white;">{{ brandingStore.schoolInitials }}</span>
          </div>
        </div>
        <div class="brand-details">
          <h2 class="brand-title" :title="brandingStore.schoolName" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">{{ brandingStore.schoolName }}</h2>
          <span class="portal-tag">STUDENT PORTAL</span>
        </div>
        <button
          type="button"
          class="close-btn"
          aria-label="Close navigation sidebar"
          @click="closeMobileSidebar"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Links -->
      <div class="sidebar-scrollable">
        <div class="nav-section-label">MAIN MENU</div>
        <nav class="nav-links">
          <!-- 1. Dashboard -->
          <router-link
            to="/student/dashboard"
            class="nav-item"
            :class="{ active: route.path === '/student/dashboard' }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <span>Dashboard</span>
            <div v-if="route.path === '/student/dashboard'" class="active-indicator" />
          </router-link>

          <!-- 2. My Profile -->
          <router-link
            to="/student/profile"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/profile') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <span>My Profile</span>
            <div v-if="route.path.startsWith('/student/profile')" class="active-indicator" />
          </router-link>

          <!-- 3. My Class & Subjects -->
          <router-link
            to="/student/class"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/class') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <span>My Class & Subjects</span>
            <div v-if="route.path.startsWith('/student/class')" class="active-indicator" />
          </router-link>

          <!-- 4. My Timetable -->
          <router-link
            to="/student/timetable"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/timetable') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span>My Timetable</span>
            <div v-if="route.path.startsWith('/student/timetable')" class="active-indicator" />
          </router-link>

          <!-- 5. My Attendance -->
          <router-link
            to="/student/attendance"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/attendance') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span>My Attendance</span>
            <div v-if="route.path.startsWith('/student/attendance')" class="active-indicator" />
          </router-link>

          <!-- 6. My Fees & Billing -->
          <router-link
            to="/student/fees"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/fees') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span>My Fees & Billing</span>
            <div v-if="route.path.startsWith('/student/fees')" class="active-indicator" />
          </router-link>

          <!-- 7. My Exams & Results -->
          <router-link
            to="/student/exams"
            class="nav-item"
            :class="{ active: route.path.startsWith('/student/exams') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-box">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span>My Exams & Results</span>
            <div v-if="route.path.startsWith('/student/exams')" class="active-indicator" />
          </router-link>
        </nav>
      </div>

      <!-- User Info & Sign Out Footer -->
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar-initials">
            {{ studentInitials }}
          </div>
          <div class="user-info">
            <span class="user-name" :title="studentDisplayName">{{ studentDisplayName }}</span>
            <span class="user-status-pill">
              <span class="status-pulse" />
              Student Online
            </span>
          </div>
        </div>
        <button type="button" class="logout-btn" @click="handleLogout">
          <svg class="logout-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="portal-main">
      <!-- Top Sticky Header -->
      <header class="portal-header">
        <div class="header-left">
          <!-- Mobile Hamburger Menu Button -->
          <button
            type="button"
            class="menu-btn"
            aria-label="Toggle navigation menu"
            @click="isSidebarOpen = true"
          >
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Current Page Title Breadcrumb -->
          <div class="header-breadcrumb">
            <span class="breadcrumb-prefix">Student Portal</span>
            <span class="breadcrumb-sep">/</span>
            <h1 class="header-page-title">{{ currentPageTitle }}</h1>
          </div>
        </div>

        <div class="header-right">
          <!-- Academic Term Tag -->
          <div class="term-badge">
            <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>2026/2027 Term</span>
          </div>

          <!-- User Pill -->
          <router-link to="/student/profile" class="header-user-pill">
            <div class="header-avatar-circle">
              {{ studentInitials }}
            </div>
            <div class="header-user-text">
              <span class="header-user-name">{{ studentDisplayName }}</span>
              <span class="header-user-role">Student</span>
            </div>
          </router-link>
        </div>
      </header>

      <!-- Page Content -->
      <main class="portal-content">
        <router-view />
      </main>

      <!-- Footer -->
      <footer class="portal-footer">
        <p class="footer-copy">
          &copy; {{ new Date().getFullYear() }} Somroyal Educational Management System. All rights reserved.
        </p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.portal-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background-color: #F8FAFC;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* Sidebar Styling */
.portal-sidebar {
  width: 260px;
  height: 100vh;
  background-color: #0A192F;
  color: #F8FAFC;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
}

.sidebar-header {
  height: 70px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background-color: #081528;
}

.brand-logo-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.35rem 0.5rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.somroyal-crown {
  width: 18px;
  height: 14px;
}

.somroyal-s {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: #FFFFFF;
  font-weight: 900;
  font-size: 0.85rem;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-details {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-title {
  font-size: 0.95rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: #FFFFFF;
  margin: 0;
}

.portal-tag {
  font-size: 0.65rem;
  color: #10B981;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.close-btn {
  display: none;
  margin-left: auto;
  color: #94A3B8;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
}

.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 0.85rem;
}

.nav-section-label {
  font-size: 0.68rem;
  font-weight: 700;
  color: #64748B;
  letter-spacing: 0.08em;
  padding: 0 0.65rem 0.5rem 0.65rem;
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
  padding: 0.65rem 0.85rem;
  font-size: 0.86rem;
  font-weight: 500;
  color: #94A3B8;
  border-radius: 10px;
  text-decoration: none;
  position: relative;
  transition: all 0.18s ease;
}

.nav-icon-box {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon-box svg {
  width: 1.2rem;
  height: 1.2rem;
  transition: transform 0.15s ease;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #F1F5F9;
}

.nav-item:hover .nav-icon-box svg {
  transform: scale(1.08);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(5, 150, 105, 0.28) 100%);
  color: #FFFFFF;
  font-weight: 600;
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
}

.nav-item.active .nav-icon-box {
  color: #34D399;
}

.active-indicator {
  position: absolute;
  right: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10B981;
  box-shadow: 0 0 8px #10B981;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem 0.85rem;
  background-color: #081528;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.65rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
}

.user-avatar-initials {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10B981 0%, #047857 100%);
  color: #FFFFFF;
  font-weight: 700;
  font-size: 0.82rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-status-pill {
  font-size: 0.68rem;
  color: #34D399;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.status-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #10B981;
  box-shadow: 0 0 6px #10B981;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.55rem;
  border-radius: 8px;
  color: #F87171;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.15);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}

.logout-btn:hover {
  background: #EF4444;
  color: #FFFFFF;
  border-color: #EF4444;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25);
}

.logout-icon {
  width: 16px;
  height: 16px;
}

/* Portal Main Content Area */
.portal-main {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: calc(100% - 260px);
  min-width: 0;
  box-sizing: border-box;
}

.portal-header {
  height: 70px;
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.75rem;
  position: sticky;
  top: 0;
  z-index: 30;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.menu-btn {
  display: none;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  color: #334155;
  padding: 0.45rem;
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.menu-btn:hover {
  background-color: #F1F5F9;
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.breadcrumb-prefix {
  font-size: 0.82rem;
  font-weight: 500;
  color: #64748B;
}

.breadcrumb-sep {
  font-size: 0.8rem;
  color: #CBD5E1;
}

.header-page-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0F172A;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.term-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  color: #065F46;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.65rem;
  border-radius: 9999px;
}

.header-user-pill {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.25rem 0.65rem 0.25rem 0.35rem;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 9999px;
  text-decoration: none;
  transition: all 0.15s ease;
}

.header-user-pill:hover {
  background: #F1F5F9;
  border-color: #CBD5E1;
}

.header-avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #0A192F;
  color: #FFFFFF;
  font-weight: 700;
  font-size: 0.72rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
  text-align: left;
}

.header-user-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: #0F172A;
  max-width: 140px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-user-role {
  font-size: 0.66rem;
  color: #10B981;
  font-weight: 600;
}

.portal-content {
  flex: 1;
  padding: 1.75rem;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.portal-footer {
  padding: 1rem 1.75rem;
  background-color: #FFFFFF;
  border-top: 1px solid #E2E8F0;
  text-align: center;
}

.footer-copy {
  font-size: 0.75rem;
  color: #94A3B8;
  margin: 0;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 25, 47, 0.6);
  backdrop-filter: blur(4px);
  z-index: 35;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Media Queries */
@media (max-width: 1024px) {
  .portal-sidebar {
    transform: translateX(-100%);
  }
  .portal-sidebar.open {
    transform: translateX(0);
  }
  .close-btn,
  .menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .portal-main {
    margin-left: 0;
    width: 100%;
  }
  .portal-header {
    padding: 0 1.25rem;
  }
  .portal-content {
    padding: 1.25rem;
  }
}

@media (max-width: 640px) {
  .portal-header {
    padding: 0 0.85rem;
    height: 64px;
  }
  .portal-content {
    padding: 0.85rem;
  }
  .term-badge {
    display: none;
  }
  .breadcrumb-prefix,
  .breadcrumb-sep {
    display: none;
  }
  .header-page-title {
    font-size: 0.95rem;
  }
  .header-user-text {
    display: none;
  }
  .header-user-pill {
    padding: 0.2rem;
    border-radius: 50%;
  }
}
</style>
