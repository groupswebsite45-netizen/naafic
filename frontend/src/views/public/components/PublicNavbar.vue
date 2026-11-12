<template>
  <header class="public-navbar" :class="{ 'scrolled': isScrolled }" role="banner">
    <div class="nav-container">
      <!-- Brand Logo -->
      <a href="#hero" class="brand-link" @click.prevent="scrollToSection('hero')" aria-label="Somroyal Technology Solutions Home">
        <img src="/somroyal-logo-transparent.png" alt="Somroyal Technology Solutions" class="brand-logo" />
      </a>

      <!-- Desktop Navigation Links (>= 1140px) -->
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
              aria-label="Switch to English"
            >
              EN
            </button>
            <button
              type="button"
              class="lang-btn"
              :class="{ 'active': currentLang === 'so' }"
              @click="setLanguage('so')"
              title="Af-Soomaali"
              aria-label="U bedel Af-Soomaali"
            >
              SO
            </button>
          </div>
        </div>

        <!-- Auth Conditional: Login or Dashboard (Desktop & Tablet) -->
        <template v-if="isAuthenticated">
          <router-link :to="userDefaultRoute" class="btn btn-secondary-nav">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span>{{ t.nav.dashboard }}</span>
          </router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-ghost-login">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            <span>{{ t.nav.login }}</span>
          </router-link>
        </template>

        <!-- CTA Trial / Demo Button (Desktop & Tablet) -->
        <a href="#contact" class="btn btn-primary-cta" @click.prevent="scrollToSection('contact')">
          <span>{{ t.nav.startTrial }}</span>
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </a>

        <!-- Mobile & Tablet Menu Hamburger Button -->
        <button
          type="button"
          class="mobile-toggle"
          :class="{ 'is-active': isMobileMenuOpen }"
          :aria-expanded="isMobileMenuOpen"
          aria-controls="mobile-nav-drawer"
          aria-label="Toggle navigation menu"
          @click="toggleMobileMenu"
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

    <!-- Mobile Drawer Navigation (Teleported to body to escape navbar containing block) -->
    <Teleport to="body">
      <transition name="drawer-fade">
        <div
          v-if="isMobileMenuOpen"
          id="mobile-nav-drawer"
          class="mobile-drawer-backdrop"
          @click="closeMobileMenu"
          @keydown.esc="closeMobileMenu"
        >
          <div class="mobile-drawer" @click.stop role="dialog" aria-modal="true" aria-label="Mobile Navigation Menu">
            <!-- Drawer Header -->
            <div class="drawer-header">
              <a href="#hero" class="drawer-brand" @click.prevent="mobileNav('hero')">
                <img src="/somroyal-logo-transparent.png" alt="Somroyal Technology Solutions" class="drawer-logo" />
              </a>
              <button
                type="button"
                class="drawer-close"
                aria-label="Close menu"
                @click="closeMobileMenu"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Language Switcher Strip in Drawer -->
            <div class="drawer-lang-strip">
              <span class="drawer-lang-title">
                <svg class="w-4 h-4 text-orange" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" x2="22" y1="12" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <span>{{ currentLang === 'so' ? 'Dooro Luqadda' : 'Select Language' }}</span>
              </span>
              <div class="lang-switch-box-drawer" role="group" aria-label="Language selection">
                <button
                  type="button"
                  class="lang-btn-drawer"
                  :class="{ 'active': currentLang === 'en' }"
                  @click="setLanguage('en')"
                >
                  English
                </button>
                <button
                  type="button"
                  class="lang-btn-drawer"
                  :class="{ 'active': currentLang === 'so' }"
                  @click="setLanguage('so')"
                >
                  Af-Soomaali
                </button>
              </div>
            </div>

            <!-- Section Label -->
            <div class="drawer-section-label">
              <span>{{ currentLang === 'so' ? 'LIISKA BOGAGGA' : 'NAVIGATION MENU' }}</span>
            </div>

            <!-- Professional Menu Links -->
            <nav class="drawer-nav" aria-label="Mobile Navigation Links">
              <!-- 1. Home -->
              <a href="#hero" class="drawer-link" :class="{ 'active': activeSection === 'hero' }" @click.prevent="mobileNav('hero')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.home }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? 'Dulmar Guud & Furaha' : 'Overview & Hero Highlights' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>

              <!-- 2. Features -->
              <a href="#features" class="drawer-link" :class="{ 'active': activeSection === 'features' }" @click.prevent="mobileNav('features')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.features }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? 'Ardayda, Imtixaanka, Lacagaha' : 'Academics, Exams & Finance' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>

              <!-- 3. About Us -->
              <a href="#about" class="drawer-link" :class="{ 'active': activeSection === 'about' }" @click.prevent="mobileNav('about')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.about }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? 'Hadafka Somroyal & Horumarka' : 'Company Mission & Somali Legacy' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>

              <!-- 4. How It Works -->
              <a href="#how-it-works" class="drawer-link" :class="{ 'active': activeSection === 'how-it-works' }" @click.prevent="mobileNav('how-it-works')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.howItWorks }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? '4 Tallaabo oo Fudud' : 'Simple 4-Step Rollout' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>

              <!-- 5. Pricing -->
              <a href="#pricing" class="drawer-link" :class="{ 'active': activeSection === 'pricing' }" @click.prevent="mobileNav('pricing')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.pricing }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? 'Qorshayaal U Qalmo Dugsigaaga' : 'Transparent Pricing & ROI' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>

              <!-- 6. Contact -->
              <a href="#contact" class="drawer-link" :class="{ 'active': activeSection === 'contact' }" @click.prevent="mobileNav('contact')">
                <span class="drawer-link-icon">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </span>
                <div class="drawer-link-text">
                  <span class="link-title">{{ t.nav.contact }}</span>
                  <span class="link-desc">{{ currentLang === 'so' ? 'Nala Soo Xiriir / Demo Toos Ah' : 'Book a Demo & Dedicated Support' }}</span>
                </div>
                <svg class="drawer-link-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </nav>

            <!-- Direct Hotline Quick Call -->
            <a href="tel:+252612508505" class="drawer-hotline-card">
              <span class="hotline-icon">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
              </span>
              <div class="hotline-info">
                <span class="hotline-title">{{ currentLang === 'so' ? 'Khadka Tooska ah ee Dugsiyada' : 'Direct School Hotline' }}</span>
                <span class="hotline-number">+252 61 250 8505</span>
              </div>
            </a>

            <!-- Action CTAs: Login + Start Trial -->
            <div class="drawer-footer">
              <template v-if="isAuthenticated">
                <router-link :to="userDefaultRoute" class="btn btn-secondary-nav w-full justify-center drawer-btn">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  <span>{{ t.nav.dashboard }}</span>
                </router-link>
              </template>
              <template v-else>
                <router-link to="/login" class="btn btn-drawer-login w-full justify-center drawer-btn" @click="closeMobileMenu">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  <span>{{ t.nav.login }}</span>
                </router-link>
              </template>

              <a href="#contact" class="btn btn-drawer-cta w-full justify-center drawer-btn" @click.prevent="mobileNav('contact')">
                <span>{{ t.nav.startTrial }}</span>
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </a>

              <div class="drawer-trust-badge">
                <svg class="w-3.5 h-3.5 text-orange flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span>Somroyal EMS &bull; 100% Cloud Native &bull; Mogadishu</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
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

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false;
}

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
  closeMobileMenu();
  scrollToSection(id);
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isMobileMenuOpen.value) {
    closeMobileMenu();
  }
}

// Lock body scroll when mobile menu is open
watch(isMobileMenuOpen, (val) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = val ? 'hidden' : '';
  }
});

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('keydown', handleKeydown);
  handleScroll();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('keydown', handleKeydown);
  if (typeof document !== 'undefined') {
    document.body.style.overflow = '';
  }
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
  gap: 0.4rem;
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
  padding: 4px 9px;
  min-height: 28px;
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
  min-height: 40px;
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
  min-height: 40px;
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
  min-height: 40px;
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
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 0.5rem;
  background: #F7F9FC;
  border: 1px solid #D9E2EC;
  border-radius: 8px;
  color: #0B1F4B;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.mobile-toggle:hover,
.mobile-toggle.is-active {
  background: #FFF7ED;
  border-color: #FF6B00;
  color: #FF6B00;
}

/* Mobile Drawer */
.mobile-drawer-backdrop {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  height: 100dvh;
  background: rgba(7, 23, 53, 0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 99999;
  display: flex;
  justify-content: flex-end;
}

.mobile-drawer {
  width: 88%;
  max-width: 380px;
  height: 100%;
  height: 100dvh;
  background: #ffffff;
  padding: 1.25rem 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  box-shadow: -10px 0 36px rgba(7, 23, 53, 0.35);
  padding-top: max(1.25rem, env(safe-area-inset-top));
  padding-bottom: max(1.25rem, env(safe-area-inset-bottom));
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.drawer-brand {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.drawer-logo {
  height: 38px;
  width: auto;
  object-fit: contain;
}

.drawer-close {
  background: #F7F9FC;
  border: 1px solid #E2E8F0;
  width: 42px;
  height: 42px;
  min-width: 42px;
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: #586983;
  cursor: pointer;
  transition: all 0.2s;
}

.drawer-close:hover {
  background: #FFF7ED;
  border-color: #FF6B00;
  color: #FF6B00;
}

/* Language strip in drawer */
.drawer-lang-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem 0.85rem;
  margin-top: 0.85rem;
  background: #F8FAFC;
  border: 1px solid #EAEFF5;
  border-radius: 12px;
  flex-shrink: 0;
}

.drawer-lang-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.82rem;
  font-weight: 700;
  color: #0B1F4B;
}

.lang-switch-box-drawer {
  display: inline-flex;
  align-items: center;
  background: #FFFFFF;
  border: 1px solid #D9E2EC;
  border-radius: 20px;
  padding: 2px;
  gap: 2px;
}

.lang-btn-drawer {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  min-height: 28px;
  border-radius: 14px;
  color: #52678A;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-btn-drawer.active {
  background: #FF6900;
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(255, 105, 0, 0.3);
}

/* Section Label */
.drawer-section-label {
  padding: 1rem 0.25rem 0.4rem;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #8C9BAE;
  text-transform: uppercase;
  flex-shrink: 0;
}

/* Core Navigation Menu List */
.drawer-nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.25rem 0;
  flex-shrink: 0;
}

.drawer-link {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.85rem;
  min-height: 52px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}

.drawer-link-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #F0F4FA;
  color: #0B1F4B;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.drawer-link-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
  text-align: left;
}

.link-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: #0B1F4B;
  line-height: 1.25;
  transition: color 0.2s;
}

.link-desc {
  font-size: 0.72rem;
  color: #718096;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drawer-link-arrow {
  width: 16px;
  height: 16px;
  color: #CBD5E0;
  flex-shrink: 0;
  transition: transform 0.2s, color 0.2s;
}

.drawer-link:hover,
.drawer-link.active {
  background: #FFF7ED;
  border-color: rgba(255, 107, 0, 0.25);
}

.drawer-link:hover .drawer-link-icon,
.drawer-link.active .drawer-link-icon {
  background: #FF6B00;
  color: #ffffff;
  box-shadow: 0 3px 10px rgba(255, 107, 0, 0.3);
}

.drawer-link:hover .link-title,
.drawer-link.active .link-title {
  color: #FF6B00;
}

.drawer-link:hover .drawer-link-arrow,
.drawer-link.active .drawer-link-arrow {
  color: #FF6B00;
  transform: translateX(4px);
}

/* Hotline Card */
.drawer-hotline-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #F0F5FF;
  border: 1px dashed #A5B4FC;
  border-radius: 12px;
  padding: 0.65rem 0.85rem;
  text-decoration: none;
  margin: 0.75rem 0 0.5rem;
  flex-shrink: 0;
  transition: all 0.2s;
}

.drawer-hotline-card:hover {
  background: #E8EFFF;
  border-color: #6366F1;
}

.hotline-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #4F46E5;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hotline-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hotline-title {
  font-size: 0.7rem;
  font-weight: 700;
  color: #4F46E5;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.hotline-number {
  font-size: 0.9rem;
  font-weight: 800;
  color: #0B1F4B;
  letter-spacing: 0.02em;
}

/* Footer CTAs */
.drawer-footer {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding-top: 0.85rem;
  border-top: 1px solid #f1f5f9;
  margin-top: auto;
  flex-shrink: 0;
}

.btn-drawer-login {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: #F0F4FA;
  border: 1px solid #CBD5E0;
  color: #0B1F4B;
  font-weight: 700;
  font-size: 0.95rem;
  min-height: 48px;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-drawer-login:hover {
  background: #E2E8F0;
  border-color: #0B1F4B;
  color: #0B1F4B;
}

.btn-drawer-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #FF6900 0%, #FF8D1A 100%);
  border: none;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.98rem;
  min-height: 50px;
  border-radius: 10px;
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(255, 105, 0, 0.35);
  transition: all 0.25s;
}

.btn-drawer-cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(255, 105, 0, 0.45);
  color: #ffffff;
}

.drawer-trust-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  color: #718096;
  font-weight: 600;
  text-align: center;
  padding: 0.35rem 0 0;
}

/* Drawer Transitions with Slide */
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-fade-enter-active .mobile-drawer,
.drawer-fade-leave-active .mobile-drawer {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

.drawer-fade-enter-from .mobile-drawer,
.drawer-fade-leave-to .mobile-drawer {
  transform: translateX(100%);
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

@media (max-width: 860px) {
  .btn-ghost-login,
  .btn-primary-cta,
  .btn-secondary-nav {
    display: none;
  }
}

@media (max-width: 768px) {
  .public-navbar {
    height: 66px;
  }

  .public-navbar.scrolled {
    height: 62px;
  }

  .brand-logo {
    height: 36px;
    max-width: 155px;
  }
}

@media (max-width: 380px) {
  .nav-container {
    padding: 0 0.65rem;
    gap: 0.35rem;
  }

  .brand-logo {
    height: 32px;
    max-width: 130px;
  }

  .globe-icon {
    display: none;
  }

  .lang-btn {
    padding: 3px 6px;
    font-size: 0.7rem;
  }
}
</style>
