<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useSchoolBrandingStore } from '../stores/schoolBranding';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const brandingStore = useSchoolBrandingStore();

const isSidebarOpen = ref(false);

const teacherDisplayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || 'Teacher';
});

const teacherInitials = computed(() => {
  const name = teacherDisplayName.value.trim();
  const parts = name.split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return name.slice(0, 2).toUpperCase();
});

const currentPageTitle = computed(() => {
  if (route.path === '/teacher/dashboard') return 'Dashboard';
  if (route.path.startsWith('/teacher/classes')) return 'My Classes & Subjects';
  if (route.path.startsWith('/teacher/students')) return 'Assigned Students';
  if (route.path.startsWith('/teacher/attendance')) return 'Class Attendance';
  if (route.path.startsWith('/teacher/timetable')) return 'My Timetable';
  if (route.path.startsWith('/teacher/exams')) return 'Exams & Marks Entry';
  return (route.meta.title as string) || 'Teacher Portal';
});

// Lock body scroll when mobile drawer is open
watch(isSidebarOpen, (open) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = open ? 'hidden' : '';
  }
});

// Auto-close drawer on route navigation
watch(
  () => route.fullPath,
  () => {
    isSidebarOpen.value = false;
  }
);

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

function closeMobileSidebar() {
  isSidebarOpen.value = false;
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
        @click="closeMobileSidebar"
      />
    </transition>

    <!-- Somroyal Teacher Sidebar Drawer -->
    <aside
      class="portal-sidebar"
      :class="{ 'open': isSidebarOpen }"
      aria-label="Teacher Portal Navigation"
    >
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
          <span class="portal-tag">TEACHER PORTAL</span>
        </div>
        <button
          type="button"
          class="close-btn"
          aria-label="Close navigation sidebar"
          @click="closeMobileSidebar"
        >
          <svg class="close-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Links -->
      <div class="sidebar-scrollable">
        <div class="nav-section-label">TEACHER SUITE</div>
        <nav class="nav-links">
          <!-- 1. Dashboard -->
          <router-link
            to="/teacher/dashboard"
            class="nav-item"
            :class="{ active: route.path === '/teacher/dashboard' }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <span class="nav-label">Dashboard</span>
            <div v-if="route.path === '/teacher/dashboard'" class="active-indicator" />
          </router-link>

          <!-- 2. My Classes & Subjects -->
          <router-link
            to="/teacher/classes"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/classes') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <span class="nav-label">My Classes &amp; Subjects</span>
            <div v-if="route.path.startsWith('/teacher/classes')" class="active-indicator" />
          </router-link>

          <!-- 3. Assigned Students -->
          <router-link
            to="/teacher/students"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/students') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <span class="nav-label">Assigned Students</span>
            <div v-if="route.path.startsWith('/teacher/students')" class="active-indicator" />
          </router-link>

          <!-- 4. Class Attendance -->
          <router-link
            to="/teacher/attendance"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/attendance') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span class="nav-label">Class Attendance</span>
            <div v-if="route.path.startsWith('/teacher/attendance')" class="active-indicator" />
          </router-link>

          <!-- 5. My Timetable -->
          <router-link
            to="/teacher/timetable"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/timetable') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span class="nav-label">My Timetable</span>
            <div v-if="route.path.startsWith('/teacher/timetable')" class="active-indicator" />
          </router-link>

          <!-- 6. Exams & Marks Entry -->
          <router-link
            to="/teacher/exams"
            class="nav-item"
            :class="{ active: route.path.startsWith('/teacher/exams') }"
            @click="closeMobileSidebar"
          >
            <div class="nav-icon-wrap">
              <svg class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <span class="nav-label">Exams &amp; Marks Entry</span>
            <div v-if="route.path.startsWith('/teacher/exams')" class="active-indicator" />
          </router-link>
        </nav>
      </div>

      <!-- User Profile Card in Sidebar Footer -->
      <div class="sidebar-footer">
        <div class="user-card">
          <div class="user-avatar-wrap">
            <div class="user-avatar-circle">
              {{ teacherInitials }}
            </div>
            <span class="online-indicator" title="Connected" />
          </div>
          <div class="user-info">
            <span class="user-name" :title="teacherDisplayName">{{ teacherDisplayName }}</span>
            <span class="user-role">Teaching Faculty</span>
          </div>
        </div>

        <button
          type="button"
          class="logout-btn"
          aria-label="Sign Out"
          @click="handleLogout"
        >
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
          <button
            type="button"
            class="menu-btn"
            aria-label="Toggle navigation menu"
            @click="isSidebarOpen = true"
          >
            <svg class="menu-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div class="header-breadcrumb">
            <span class="header-school-name">Somroyal EMS</span>
            <span class="crumb-sep">/</span>
            <span class="header-page-title">{{ currentPageTitle }}</span>
          </div>
        </div>

        <div class="header-right">
          <!-- Institutional Faculty Badge -->
          <div class="portal-badge-faculty">
            <span class="status-dot green" />
            <span>FACULTY PORTAL</span>
          </div>

          <!-- User Quick Menu -->
          <div class="header-user-wrap">
            <div class="header-avatar" :title="teacherDisplayName">
              {{ teacherInitials }}
            </div>
            <div class="header-user-info">
              <span class="header-user-name">{{ teacherDisplayName }}</span>
              <span class="header-user-role">Teacher</span>
            </div>
          </div>
        </div>
      </header>

      <!-- Page View Render -->
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
  background-color: #F8FAFC;
  width: 100%;
  overflow-x: clip;
}

/* Sidebar Backdrop */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 25, 47, 0.7);
  backdrop-filter: blur(4px);
  z-index: 45;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Sidebar Drawer */
.portal-sidebar {
  width: 270px;
  height: 100vh;
  background-color: #0A192F;
  color: #F8FAFC;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 50;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.25);
}

/* Sidebar Header */
.sidebar-header {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
  background: #071224;
}

.brand-logo-wrap {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6500 0%, #FF8A00 100%);
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 2px 8px rgba(255, 101, 0, 0.35);
  flex-shrink: 0;
}

.somroyal-crown {
  width: 20px;
  height: 12px;
  margin-top: -2px;
}

.somroyal-s {
  font-size: 0.75rem;
  font-weight: 900;
  color: #FFFFFF;
  line-height: 1;
  letter-spacing: -0.05em;
  margin-top: -1px;
}

.brand-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.brand-title {
  font-size: 0.95rem;
  font-weight: 900;
  color: #FFFFFF;
  letter-spacing: 0.08em;
  margin: 0;
  white-space: nowrap;
}

.portal-tag {
  font-size: 0.65rem;
  color: #38BDF8;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.close-btn {
  display: none;
  margin-left: auto;
  color: #94A3B8;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  padding: 0.4rem;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #FFFFFF;
  background-color: rgba(239, 68, 68, 0.2);
  border-color: #EF4444;
}

.close-icon {
  width: 20px;
  height: 20px;
}

/* Nav Section */
.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 0.85rem;
  -webkit-overflow-scrolling: touch;
}

.nav-section-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: #64748B;
  letter-spacing: 0.08em;
  padding: 0 0.75rem 0.6rem 0.75rem;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.75rem 0.9rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: #94A3B8;
  border-radius: 10px;
  text-decoration: none;
  min-height: 44px;
  position: relative;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
  color: #FFFFFF;
}

.nav-item.active {
  background: linear-gradient(135deg, #FF6B35 0%, #FF5722 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(255, 87, 34, 0.4);
}

.nav-icon-wrap {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  color: #94A3B8;
  transition: color 0.2s;
}

.nav-item:hover .nav-icon {
  color: #FFFFFF;
}

.nav-item.active .nav-icon {
  color: #FFFFFF;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.active-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 1rem;
  background-color: #071224;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex-shrink: 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.user-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.user-avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #1E293B;
  color: #FFFFFF;
  font-weight: 800;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(30, 41, 59, 0.25);
}

.online-indicator {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  background: #10B981;
  border: 2px solid #071224;
  border-radius: 50%;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.user-name {
  font-size: 0.84rem;
  font-weight: 700;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.7rem;
  color: #94A3B8;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem;
  min-height: 40px;
  border-radius: 8px;
  color: #F87171;
  background: rgba(239, 68, 68, 0.08);
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(239, 68, 68, 0.2);
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #EF4444;
  color: #FFFFFF;
  border-color: #EF4444;
}

.logout-icon {
  width: 16px;
  height: 16px;
}

/* Main Content Wrapper */
.portal-main {
  flex: 1;
  margin-left: 270px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 0;
  width: calc(100% - 270px);
}

/* Top Sticky Header */
.portal-header {
  height: 72px;
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.75rem;
  position: sticky;
  top: 0;
  z-index: 30;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.menu-btn {
  display: none;
  background: #F1F5F9;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  color: #0A192F;
  padding: 0.45rem;
  width: 42px;
  height: 42px;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  transition: all 0.2s;
}

.menu-btn:hover {
  background-color: #E2E8F0;
}

.menu-icon {
  width: 22px;
  height: 22px;
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.header-school-name {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0A192F;
  white-space: nowrap;
}

.crumb-sep {
  color: #CBD5E1;
  font-weight: 600;
}

.header-page-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0F172A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.portal-badge-faculty {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  letter-spacing: 0.04em;
}

.status-dot.green {
  width: 7px;
  height: 7px;
  background: #10B981;
  border-radius: 50%;
}

.header-user-wrap {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.header-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #0A192F;
  color: #FFFFFF;
  font-weight: 800;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #E2E8F0;
  flex-shrink: 0;
}

.header-user-info {
  display: flex;
  flex-direction: column;
}

.header-user-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: #0A192F;
  line-height: 1.2;
}

.header-user-role {
  font-size: 0.68rem;
  color: #64748B;
}

/* Page Content */
.portal-content {
  flex: 1;
  padding: 1.75rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

/* Responsive Rules */
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
    padding: 1.25rem 1rem;
  }
}

@media (max-width: 640px) {
  .header-user-info {
    display: none;
  }
  .portal-badge-faculty {
    display: none;
  }
  .crumb-sep, .header-page-title {
    display: none;
  }
  .portal-content {
    padding: 1rem 0.75rem;
  }
}
</style>
