<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useNotificationStore } from '../../stores/notification';

interface Props {
  isOpen: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const router = useRouter();
const route = useRoute();
const notificationStore = useNotificationStore();

onMounted(() => {
  notificationStore.fetchStats();
});
</script>

<template>
  <div>
    <!-- Mobile Backdrop Overlay -->
    <div
      v-if="isOpen"
      class="sidebar-backdrop"
      aria-hidden="true"
      @click="emit('close')"
    />

    <!-- Main Sidebar Container -->
    <aside
      class="admin-sidebar"
      :class="{ 'sidebar-open': isOpen }"
      aria-label="Admin Navigation Sidebar"
    >
      <!-- SOMROYAL Header Branding -->
      <div class="sidebar-header">
        <div class="brand-logo-wrap">
          <!-- Crown Icon + Stylized S Logo -->
          <svg class="somroyal-crown-icon" viewBox="0 0 24 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 13L4 4L8.5 8.5L12 2L15.5 8.5L20 4L22 13H2Z" fill="#F59E0B" stroke="#D97706" stroke-width="1.2" stroke-linejoin="round"/>
            <circle cx="4" cy="4" r="1.2" fill="#FDE68A" />
            <circle cx="12" cy="2" r="1.2" fill="#FDE68A" />
            <circle cx="20" cy="4" r="1.2" fill="#FDE68A" />
          </svg>
          <div class="somroyal-s-wrap">
            <span class="somroyal-s-letter">S</span>
          </div>
        </div>
        <div class="brand-details">
          <h2 class="brand-title">SOMROYAL</h2>
          <span class="brand-subtitle">EDUCATIONAL MANAGEMENT SYSTEM</span>
        </div>

        <!-- Mobile Close Button -->
        <button
          type="button"
          class="close-sidebar-btn"
          aria-label="Close sidebar"
          @click="emit('close')"
        >
          <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation Links -->
      <div class="sidebar-scrollable">
        <nav class="nav-links">
          <!-- 1. Dashboard (Active Orange Pill) -->
          <router-link
            to="/admin/dashboard"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/dashboard' }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="nav-label">Dashboard</span>
          </router-link>

          <!-- 2. Students -->
          <router-link
            to="/admin/students"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/students') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span class="nav-label">Students</span>
          </router-link>

          <!-- 3. Teachers -->
          <router-link
            to="/admin/teachers"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/teachers') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span class="nav-label">Teachers</span>
          </router-link>

          <!-- 4. Classes -->
          <router-link
            to="/admin/classes"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/classes' || (route.path.startsWith('/admin/classes') && !route.path.includes('promotion')) }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span class="nav-label">Classes</span>
          </router-link>

          <!-- 5. Class Promotion -->
          <router-link
            to="/admin/class-promotion"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/class-promotion') || route.path.includes('classes/promotion') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 11l3-3m0 0l3 3m-3-3v8m0-13a9 9 0 110 18 9 9 0 010-18z" />
            </svg>
            <span class="nav-label">Class Promotion</span>
          </router-link>

          <!-- 6. Subjects -->
          <router-link
            to="/admin/subjects"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/subjects') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span class="nav-label">Subjects</span>
          </router-link>

          <!-- 7. Timetable -->
          <router-link
            to="/admin/timetable"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/timetable') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="nav-label">Timetable</span>
          </router-link>

          <!-- 8. Exams -->
          <router-link
            to="/admin/exams"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/exams' || route.path.startsWith('/admin/exams/create') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <span class="nav-label">Exams</span>
          </router-link>

          <!-- 9. Results Management -->
          <router-link
            to="/admin/results"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/results') || route.path.startsWith('/admin/exams/results') || route.path.startsWith('/admin/exams/submissions') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="nav-label">Results Management</span>
          </router-link>

          <!-- 10. Fees & Payments (with Chevron >) -->
          <router-link
            to="/admin/fees"
            class="nav-item"
            :class="{ 'active': route.path.startsWith('/admin/fees') }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="nav-label">Fees & Payments</span>
            <svg class="nav-chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </router-link>

          <!-- 11. Reports (with Chevron >) -->
          <router-link
            to="/admin/results"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/reports' }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="nav-label">Reports</span>
            <svg class="nav-chevron" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </router-link>

          <!-- 12. Users & Roles -->
          <router-link
            to="/admin/profile"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/users' }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span class="nav-label">Users & Roles</span>
          </router-link>

          <!-- 13. Settings -->
          <router-link
            to="/admin/settings"
            class="nav-item"
            :class="{ 'active': route.path === '/admin/settings' }"
            @click="emit('close')"
          >
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="nav-label">Settings</span>
          </router-link>
        </nav>

        <!-- Bottom Need Help? Card -->
        <div class="support-card-container">
          <div class="support-card">
            <div class="support-icon-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 100-6 3 3 0 000 6z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 11a9 9 0 0118 0v3a3 3 0 01-3 3h-1a2 2 0 01-2-2v-4a2 2 0 012-2h2M3 11v3a3 3 0 003 3h1a2 2 0 002-2v-4a2 2 0 00-2-2H5" />
              </svg>
            </div>
            <h4 class="support-title">Need Help?</h4>
            <p class="support-desc">Our support team is here to assist you.</p>
            <button type="button" class="support-btn" @click="router.push('/admin/settings')">
              <span>Contact Support</span>
              <span class="support-arrow">&rarr;</span>
            </button>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.admin-sidebar {
  width: var(--sidebar-width, 250px);
  height: 100vh;
  background-color: #0A192F;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform var(--transition-normal, 0.25s ease);
}

.sidebar-header {
  height: var(--header-height, 70px);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background-color: #081528;
}

.brand-logo-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.somroyal-crown-icon {
  width: 20px;
  height: 12px;
  margin-bottom: -2px;
}

.somroyal-s-wrap {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.somroyal-s-letter {
  font-family: 'Outfit', 'Inter', sans-serif;
  font-size: 1.65rem;
  font-weight: 900;
  color: #2563EB;
  text-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
  line-height: 1;
}

.brand-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.brand-title {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #ffffff;
  margin: 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #94A3B8;
  white-space: nowrap;
}

.close-sidebar-btn {
  display: none;
  margin-left: auto;
  color: #94a3b8;
  padding: 0.4rem;
  background: transparent;
  border: none;
  cursor: pointer;
}

.sidebar-scrollable {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0.85rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 1.5rem;
}

.sidebar-scrollable::-webkit-scrollbar {
  width: 5px;
}
.sidebar-scrollable::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
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
  padding: 0.72rem 1rem;
  font-size: 0.88rem;
  font-weight: 500;
  color: #94A3B8;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #F8FAFC;
}

/* Active Dashboard Tab with glowing vibrant orange pill background */
.nav-item.active {
  background: linear-gradient(135deg, #FF6B35 0%, #FF5722 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(255, 87, 34, 0.4);
}

.nav-item.active .nav-icon {
  color: #FFFFFF;
}

.nav-item.active .nav-chevron {
  color: #FFFFFF;
}

.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: #94A3B8;
  transition: color 0.2s ease;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
}

.nav-chevron {
  width: 1rem;
  height: 1rem;
  color: #64748B;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.nav-item:hover .nav-chevron {
  color: #CBD5E1;
  transform: translateX(2px);
}

/* Bottom Support Card */
.support-card-container {
  margin-top: auto;
  padding-top: 1rem;
}

.support-card {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.15rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(8px);
}

.support-icon-circle {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(37, 99, 235, 0.15);
  color: #38BDF8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.support-icon-circle svg {
  width: 20px;
  height: 20px;
}

.support-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
}

.support-desc {
  font-size: 0.74rem;
  color: #94A3B8;
  margin: 0;
  line-height: 1.4;
}

.support-btn {
  margin-top: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #FF6B35 0%, #FF5722 100%);
  color: #FFFFFF;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(255, 87, 34, 0.3);
}

.support-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 87, 34, 0.45);
}

.support-arrow {
  font-size: 0.95rem;
  transition: transform 0.2s ease;
}

.support-btn:hover .support-arrow {
  transform: translateX(3px);
}

/* Mobile Responsiveness */
@media (max-width: 1024px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  .admin-sidebar.sidebar-open {
    transform: translateX(0);
  }
  .close-sidebar-btn {
    display: block;
  }
  .sidebar-backdrop {
    position: fixed;
    inset: 0;
    background-color: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(4px);
    z-index: 39;
  }
}
</style>
