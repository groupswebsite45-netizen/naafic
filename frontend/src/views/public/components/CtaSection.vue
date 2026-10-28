<template>
  <section class="cta-section">
    <div class="cta-container">
      <div class="cta-card">
        <!-- Background Decorative Orbs -->
        <div class="cta-orb orb-1" aria-hidden="true"></div>
        <div class="cta-orb orb-2" aria-hidden="true"></div>

        <div class="cta-content">
          <span class="cta-pill">INSTITUTIONAL EMPOWERMENT</span>
          <h2 class="cta-title">{{ t.cta.title }}</h2>
          <p class="cta-subtitle">{{ t.cta.subtitle }}</p>

          <div class="cta-btn-group">
            <a href="#contact" class="btn btn-cta-primary" @click.prevent="emitScroll('contact')">
              <span>{{ t.cta.primaryCta }}</span>
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </a>

            <router-link to="/login" class="btn btn-cta-ghost">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              <span>{{ t.cta.loginBtn }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

const emit = defineEmits<{
  (e: 'scroll', target: string): void;
}>();

function emitScroll(target: string) {
  emit('scroll', target);
}
</script>

<style scoped>
.cta-section {
  padding: 60px 0;
  background-color: #f8fafc;
}

.cta-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.cta-card {
  position: relative;
  background: linear-gradient(135deg, #071735 0%, #0B1F4B 60%, #12264A 100%);
  border-radius: 24px;
  padding: 4.5rem 2rem;
  overflow: hidden;
  box-shadow: 0 24px 60px -12px rgba(7, 23, 53, 0.45);
  text-align: center;
}

.cta-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}

.orb-1 {
  top: -60px;
  right: -60px;
  width: 320px;
  height: 320px;
  background: #FF6B00;
  opacity: 0.25;
}

.orb-2 {
  bottom: -60px;
  left: -60px;
  width: 320px;
  height: 320px;
  background: #0B1F4B;
  opacity: 0.4;
}

.cta-content {
  position: relative;
  z-index: 1;
  max-width: 780px;
  margin: 0 auto;
}

.cta-pill {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 800;
  color: #FFEDD5;
  background: rgba(255, 107, 0, 0.2);
  border: 1px solid rgba(255, 107, 0, 0.4);
  padding: 0.35rem 1rem;
  border-radius: 20px;
  letter-spacing: 0.08em;
  margin-bottom: 1.25rem;
}

.cta-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.65rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.2;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.cta-subtitle {
  font-size: 1.15rem;
  color: #EAF0F8;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.cta-btn-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.95rem 2rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #ffffff;
  background: #FF6B00;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(255, 107, 0, 0.3);
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-cta-primary:hover {
  background: #E85D00;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 107, 0, 0.45);
  color: #ffffff;
}

.btn-cta-ghost {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.95rem 2rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(8px);
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-cta-ghost:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: #ffffff;
  transform: translateY(-2px);
}

@media (max-width: 640px) {
  .cta-title {
    font-size: 2rem;
  }
  .cta-card {
    padding: 3rem 1.5rem;
  }
}
</style>
