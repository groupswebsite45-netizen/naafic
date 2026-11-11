<template>
  <header class="public-navbar" :class="{ 'scrolled': isScrolled }">
    <div class="nav-container">
      <!-- Brand Logo -->
      <a href="#hero" class="brand-link" @click.prevent="scrollToSection('hero')">
        <img src="/somroyal-logo-transparent.png" alt="Somroyal Technology Solutions" class="brand-logo" />
      </a>

      <!-- Desktop Navigation Links -->
      <nav class="desktop-nav" aria-label="Main Navigation">
        <a href="#hero" class="nav-item" :class="{ 'active': activeSection === 'hero' }" @click.prevent="scrollToSection('hero')">
          {{ t.nav.home }}
        </a>
        <a href="#features" class="nav-item" :class="{ 'active': activeSection === 'features' }" @click.prevent="scrollToSection('features')">
          {{ t.nav.features }}
        </a>
        <a href="#about" class="nav-item" :class="{ 'active': activeSection === 'about' }" @click.prevent="scrollToSection('about')">
          {{ t.nav.about }}
        </a>
        <a href="#how-it-works" class="nav-item" :class="{ 'active': activeSection === 'how-it-works' }" @click.prevent="scrollToSection('how-it-works')">
          {{ t.nav.howItWorks }}
        </a>
        <a href="#pricing" class="nav-item" :class="{ 'active': activeSection === 'pricing' }" @click.prevent="scrollToSection('pricing')">
          {{ t.nav.pricing }}
        </a>
        <a href="#contact" class="nav-item" :class="{ 'active': activeSection === 'contact' }" @click.prevent="scrollToSection('contact')">
          {{ t.nav.contact }}
        </a>
      </nav>

      <!-- Right Action Controls -->
      <div class="nav-actions">
        <!-- Language Switcher with Globe Icon -->
        <div class="lang-selector-group">
          <svg class="globe-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" x2="22" y1="12" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
          <div class="lang-switch-box" role="group" aria-label="Language selector">
            <button
              type="button"
              class="lang-btn"
              :class="{ 'active': currentLang === 'en' }"
              @click="setLanguage('en')"
              title="English"
            >
              EN
            </button>
            <button
              type="button"
              class="lang-btn"
              :class="{ 'active': currentLang === 'so' }"
              @click="setLanguage('so')"
              title="Af-Soomaali"
            >
              SO
            </button>
          </div>
        </div>

        <!-- Auth Conditional: Login or Dashboard -->
        <template v-if="isAuthenticated">
          <router-link :to="userDefaultRoute" class="btn btn-secondary-nav">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            {{ t.nav.dashboard }}
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-ghost-login">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            {{ t.nav.login }}
          </router-link>
        </template>

        <!-- CTA Trial / Demo Button -->
        <a href="#contact" class="btn btn-primary-cta" @click.prevent="scrollToSection('contact')">
          <span>{{ t.nav.startTrial }}</span>
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </a>

        <!-- Mobile Menu Toggle Button -->
        <button
          type="button"
          class="mobile-toggle"
          :aria-expanded="isMobileMenuOpen"
          aria-label="Toggle navigation menu"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Drawer Navigation -->
    <transition name="drawer-fade">
      <div v-if="isMobileMenuOpen" class="mobile-drawer-backdrop" @click="isMobileMenuOpen = false">
        <div class="mobile-drawer" @click.stop>
          <div class="drawer-header">
            <img src="/somroyal-logo-transparent.png" alt="Somroyal Technology Solutions" class="drawer-logo" />
            <button
              type="button"
              class="drawer-close"
              aria-label="Close menu"
              @click="isMobileMenuOpen = false"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="drawer-nav">
            <a href="#hero" class="drawer-link" @click.prevent="mobileNav('hero')">{{ t.nav.home }}</a>
            <a href="#features" class="drawer-link" @click.prevent="mobileNav('features')">{{ t.nav.features }}</a>
            <a href="#about" class="drawer-link" @click.prevent="mobileNav('about')">{{ t.nav.about }}</a>
            <a href="#how-it-works" class="drawer-link" @click.prevent="mobileNav('how-it-works')">{{ t.nav.howItWorks }}</a>
            <a href="#pricing" class="drawer-link" @click.prevent="mobileNav('pricing')">{{ t.nav.pricing }}</a>
            <a href="#contact" class="drawer-link" @click.prevent="mobileNav('contact')">{{ t.nav.contact }}</a>
          </div>

          <div class="drawer-footer">
            <div class="drawer-lang-toggle">
              <span class="text-xs text-slate-500 font-semibold">Language:</span>
              <div class="lang-switch-box">
                <button
                  type="button"
                  class="lang-btn"
                  :class="{ 'active': currentLang === 'en' }"
                  @click="setLanguage('en')"
                >
                  English
                </button>
                <span class="lang-divider">|</span>
                <button
                  type="button"
                  class="lang-btn"
                  :class="{ 'active': currentLang === 'so' }"
                  @click="setLanguage('so')"
                >
                  Soomaali
                </button>
              </div>
            </div>

            <template v-if="isAuthenticated">
              <router-link :to="userDefaultRoute" class="btn btn-secondary-nav w-full justify-center">
                {{ t.nav.dashboard }}
              </router-link>
            </template>
            <template v-else>
              <router-link to="/login" class="btn btn-ghost-login w-full justify-center">
                {{ t.nav.login }}
              </router-link>
            </template>

            <a href="#contact" class="btn btn-primary-cta w-full justify-center" @click.prevent="mobileNav('contact')">
              {{ t.nav.startTrial }}
            </a>
          </div>
        </div>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useAuthStore } from '../../../stores/auth';
import { TranslationContent, Language } from '../translations';

defineProps<{
  t: TranslationContent;
  currentLang: Language;
}>();

const emit = defineEmits<{
  (e: 'update:language', lang: Language): void;
}>();

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const userDefaultRoute = computed(() => authStore.defaultRoute || '/admin/dashboard');

const isScrolled = ref(false);
const isMobileMenuOpen = ref(false);
const activeSection = ref('hero');

function setLanguage(lang: Language) {
  emit('update:language', lang);
}

function handleScroll() {
  isScrolled.value = window.scrollY > 20;

  // Track active section for nav highlight
  const sections = ['hero', 'features', 'about', 'how-it-works', 'pricing', 'contact'];
  const scrollPos = window.scrollY + 100;
  for (const sec of sections) {
    const el = document.getElementById(sec);
    if (el) {
      const top = el.offsetTop;
      const height = el.offsetHeight;
      if (scrollPos >= top && scrollPos < top + height) {
        activeSection.value = sec;
        break;
      }
    }
  }
}

function scrollToSection(id: string) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
    activeSection.value = id;
  }
}

function mobileNav(id: string) {
  isMobileMenuOpen.value = false;
  scrollToSection(id);
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.public-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(234, 240, 248, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 76px;
  display: flex;
  align-items: center;
}

.public-navbar.scrolled {
  background-color: #ffffff;
  box-shadow: 0 4px 20px -2px rgba(11, 31, 75, 0.08);
  border-bottom-color: #e2e8f0;
  height: 70px;
}

.nav-container {
  width: 100%;
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 clamp(0.75rem, 2vw, 1.5rem);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(0.5rem, 1.2vw, 1.25rem);
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  flex-shrink: 0;
}

.brand-logo {
  height: 44px;
  width: auto;
  display: block;
  flex-shrink: 0;
  object-fit: contain;
}

/* Desktop Navigation */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: clamp(0.25rem, 0.85vw, 1.15rem);
  flex-shrink: 1;
  min-width: 0;
}

.nav-item {
  font-size: clamp(0.82rem, 0.88vw, 0.925rem);
  font-weight: 600;
  color: #0B1F4B;
  text-decoration: none;
  padding: 0.35rem clamp(0.35rem, 0.5vw, 0.6rem);
  border-radius: 6px;
  transition: all 0.2s ease;
  position: relative;
  white-space: nowrap;
  flex-shrink: 0;
}

.nav-item:hover {
  color: #FF6B00;
  background-color: #F7F9FC;
}

.nav-item.active {
  color: #FF6B00;
  font-weight: 700;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0.5rem;
  right: 0.5rem;
  height: 2px;
  background: #FF6B00;
  border-radius: 2px;
}

/* Nav Actions */
.nav-actions {
  display: flex;
  align-items: center;
  gap: clamp(0.4rem, 0.75vw, 0.85rem);
  flex-shrink: 0;
}

.lang-selector-group {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.globe-icon {
  width: 18px;
  height: 18px;
  color: #071D49;
  flex-shrink: 0;
}

.lang-switch-box {
  display: inline-flex;
  align-items: center;
  background: #F0F4FA;
  border: 1px solid #D9E2EC;
  border-radius: 20px;
  padding: 2px 3px;
  gap: 2px;
  flex-shrink: 0;
  white-space: nowrap;
}

.lang-btn {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 14px;
  color: #52678A;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.lang-btn.active {
  background: #FF6900;
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(255, 105, 0, 0.3);
}

/* Buttons */
.btn-ghost-login {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: clamp(0.8rem, 0.85vw, 0.9rem);
  font-weight: 600;
  color: #0B1F4B;
  background: transparent;
  border: 1px solid #D9E2EC;
  padding: 0.5rem clamp(0.6rem, 0.8vw, 1rem);
  border-radius: 8px;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-ghost-login:hover {
  background: #F7F9FC;
  border-color: #FF6B00;
  color: #FF6B00;
}

.btn-secondary-nav {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: clamp(0.8rem, 0.85vw, 0.9rem);
  font-weight: 600;
  color: #0B1F4B;
  background: #F0F4FA;
  border: 1px solid #D9E2EC;
  padding: 0.5rem clamp(0.65rem, 0.85vw, 1rem);
  border-radius: 8px;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-secondary-nav:hover {
  background: #E2E8F0;
  color: #FF6B00;
  border-color: #FF6B00;
}

.btn-primary-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: clamp(0.82rem, 0.88vw, 0.925rem);
  font-weight: 700;
  color: #ffffff;
  background: #FF6B00;
  border: none;
  padding: 0.55rem clamp(0.75rem, 1vw, 1.25rem);
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(255, 107, 0, 0.28);
  transition: all 0.25s ease;
  text-decoration: none;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-primary-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(255, 107, 0, 0.38);
  background: #E85D00;
  color: #ffffff;
}

.mobile-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: #F7F9FC;
  border: 1px solid #D9E2EC;
  border-radius: 8px;
  color: #0B1F4B;
  cursor: pointer;
  flex-shrink: 0;
}

/* Mobile Drawer */
.mobile-drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(7, 23, 53, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1100;
  display: flex;
  justify-content: flex-end;
}

.mobile-drawer {
  width: 85%;
  max-width: 340px;
  height: 100%;
  background: #ffffff;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: auto;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.2);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.drawer-logo {
  height: 38px;
  width: auto;
}

.drawer-close {
  background: #F7F9FC;
  border: none;
  padding: 0.4rem;
  border-radius: 6px;
  color: #586983;
  cursor: pointer;
}

.drawer-nav {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.5rem 0;
}

.drawer-link {
  font-size: 1.05rem;
  font-weight: 600;
  color: #0B1F4B;
  text-decoration: none;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.drawer-link:hover {
  background: #FFF7ED;
  color: #FF6B00;
}

.drawer-footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.drawer-lang-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Drawer Transitions */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

/* Responsive Breakpoints */
@media (max-width: 1140px) {
  .desktop-nav {
    display: none;
  }

  .mobile-toggle {
    display: flex;
  }
}

@media (max-width: 768px) {
  .btn-ghost-login,
  .btn-primary-cta,
  .btn-secondary-nav {
    display: none;
  }
}
</style>
