<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import AdminSidebar from '../components/admin/AdminSidebar.vue';
import AdminHeader from '../components/admin/AdminHeader.vue';

const route = useRoute();
const isSidebarOpen = ref(false);

const currentPageTitle = computed(() => {
  return (route.meta.title as string) || 'Dashboard';
});

function toggleSidebar() {
  isSidebarOpen.value = !isSidebarOpen.value;
}

function closeSidebar() {
  isSidebarOpen.value = false;
}
</script>

<template>
  <div class="admin-layout">
    <!-- Sidebar Drawer -->
    <AdminSidebar :is-open="isSidebarOpen" @close="closeSidebar" />

    <!-- Main Content Container -->
    <div class="admin-main-wrapper">
      <AdminHeader
        :page-title="currentPageTitle"
        @toggle-sidebar="toggleSidebar"
      />

      <!-- Content Area -->
      <main class="admin-content-area">
        <router-view />
      </main>

      <!-- Minimal Admin Footer -->
      <footer class="admin-footer">
        <p class="footer-text">
          &copy; {{ new Date().getFullYear() }} Education Management System. All rights reserved.
        </p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  display: flex;
  background-color: var(--bg-app);
  box-sizing: border-box;
}

.admin-main-wrapper {
  flex: 1 1 0%;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  min-width: 0;
  transition: margin-left var(--transition-normal);
  width: calc(100% - var(--sidebar-width));
  max-width: 100%;
  box-sizing: border-box;
}

.admin-content-area {
  flex: 1 1 0%;
  padding: 1.5rem 1.75rem;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  min-width: 0;
  box-sizing: border-box;
}

.admin-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-surface);
  text-align: center;
  box-sizing: border-box;
  width: 100%;
}

.footer-text {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.4;
}

/* Tablet viewports (640px - 1024px) */
@media (max-width: 1024px) {
  .admin-main-wrapper {
    margin-left: 0;
    width: 100%;
  }

  .admin-content-area {
    padding: 1.125rem 1.25rem;
  }
}

/* Mobile viewports (320px - 639px) */
@media (max-width: 640px) {
  .admin-main-wrapper {
    margin-left: 0;
    width: 100%;
  }

  .admin-content-area {
    padding: 0.875rem 0.75rem;
  }

  .admin-footer {
    padding: 0.875rem 0.75rem;
  }
}

/* Ultra small screens (320px - 359px) */
@media (max-width: 359px) {
  .admin-content-area {
    padding: 0.75rem 0.5rem;
  }
}
</style>

