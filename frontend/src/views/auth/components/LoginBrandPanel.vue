<script setup lang="ts">
import { SCHOOL_BRANDING } from '../../../constants/branding';
</script>

<template>
  <aside class="brand-panel" aria-label="School Institutional Overview">
    <!-- Ambient Background Lighting & Effects -->
    <div class="ambient-glow glow-top" aria-hidden="true"></div>
    <div class="ambient-glow glow-bottom" aria-hidden="true"></div>
    <div class="geometric-pattern" aria-hidden="true"></div>

    <!-- Main Content Container -->
    <div class="brand-content-wrapper">
      
      <!-- Top School Header -->
      <div class="brand-top-bar">
        <div class="brand-logo-pill">
          <img
            src="/somroyal-logo-transparent.png"
            alt="Somroyal Technology Solutions"
            class="brand-logo-img-left"
          />
        </div>
        <div class="top-title-wrap">
          <span class="motto-pill">
            <span class="star-icon" aria-hidden="true">★</span>
            EXCELLENCE IN EDUCATION & CHARACTER
          </span>
          <h2 class="school-name-text">{{ SCHOOL_BRANDING.institutionName }}</h2>
        </div>
      </div>

      <!-- Hero Headline & Description -->
      <div class="brand-hero-section">
        <h1 class="hero-display-headline">
          Empowering<br />
          Every Student.<br />
          <span class="hero-highlight">Building Every Future.</span>
        </h1>
        <p class="hero-subtext">
          One secure platform for academic management, teachers, students, attendance, exams, and school operations.
        </p>
      </div>

      <!-- 3 Premium Feature Highlights -->
      <div class="features-list">
        <!-- Feature 01 -->
        <div class="feature-card">
          <div class="feature-num-badge">01</div>
          <div class="feature-icon-wrap" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
              <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
            </svg>
          </div>
          <div class="feature-body">
            <h3 class="feature-name">Academic Management</h3>
            <p class="feature-desc">Curriculum, classes & schedules</p>
          </div>
        </div>

        <!-- Feature 02 -->
        <div class="feature-card">
          <div class="feature-num-badge">02</div>
          <div class="feature-icon-wrap" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
          </div>
          <div class="feature-body">
            <h3 class="feature-name">Student Success</h3>
            <p class="feature-desc">Exams, grading & progression</p>
          </div>
        </div>

        <!-- Feature 03 -->
        <div class="feature-card">
          <div class="feature-num-badge">03</div>
          <div class="feature-icon-wrap" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              <polyline points="9 12 11 14 15 10"></polyline>
            </svg>
          </div>
          <div class="feature-body">
            <h3 class="feature-name">Secure School Portal</h3>
            <p class="feature-desc">Centralized institutional control</p>
          </div>
        </div>
      </div>

      <!-- Bottom Institutional Footer -->
      <div class="brand-bottom-footer">
        <div class="footer-meta">
          <span class="footer-app-name">Education Management System</span>
          <span class="footer-divider">&bull;</span>
          <span class="footer-tagline">Secure &bull; Modern &bull; Connected</span>
        </div>
      </div>

    </div>

    <!-- =================================================================== -->
    <!-- ORGANIC CURVED TRANSITIONS (Desktop Vertical & Mobile Horizontal)   -->
    <!-- =================================================================== -->
    <!-- Desktop Vertical Organic Curve (Seamless transition to #F7F9FC) -->
    <div class="desktop-curve-container" aria-hidden="true">
      <svg
        class="desktop-curve-svg"
        viewBox="0 0 160 1000"
        preserveAspectRatio="none"
      >
        <!-- Soft translucent ambient wave -->
        <path
          d="M0,0 C65,180 135,360 85,580 C40,780 115,910 130,1000 L160,1000 L160,0 Z"
          fill="rgba(255, 255, 255, 0.12)"
        />
        <!-- Main organic curve matching right background -->
        <path
          d="M50,0 C100,190 145,370 105,570 C65,760 125,900 140,1000 L160,1000 L160,0 Z"
          fill="#f7f9fc"
        />
      </svg>
    </div>

    <!-- Mobile Horizontal Organic Wave (Seamless transition to #F7F9FC) -->
    <div class="mobile-curve-container" aria-hidden="true">
      <svg
        class="mobile-curve-svg"
        viewBox="0 0 1440 140"
        preserveAspectRatio="none"
      >
        <!-- Ambient wave layer -->
        <path
          d="M0,35 C380,110 720,20 1080,80 C1240,110 1360,85 1440,60 L1440,140 L0,140 Z"
          fill="rgba(255, 255, 255, 0.18)"
        />
        <!-- Main wave matching lower background -->
        <path
          d="M0,58 C360,130 760,40 1100,95 C1260,120 1380,90 1440,75 L1440,140 L0,140 Z"
          fill="#f7f9fc"
        />
      </svg>
    </div>

  </aside>
</template>

<style scoped>
.brand-panel {
  flex: 1.15;
  height: 100vh;
  max-height: 100vh;
  position: relative;
  background: linear-gradient(145deg, #031A3A 0%, #071F49 45%, #0B2B68 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.25rem 3.5rem;
  overflow: hidden;
  z-index: 1;
}

/* Ambient Visual Effects */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
  pointer-events: none;
  opacity: 0.45;
  z-index: 1;
}

.glow-top {
  width: 500px;
  height: 500px;
  top: -140px;
  left: -120px;
  background: radial-gradient(circle, rgba(255, 101, 0, 0.25) 0%, rgba(7, 31, 73, 0) 70%);
}

.glow-bottom {
  width: 550px;
  height: 550px;
  bottom: -160px;
  right: -60px;
  background: radial-gradient(circle, rgba(14, 52, 122, 0.7) 0%, rgba(3, 26, 58, 0) 70%);
}

.geometric-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 45%, transparent 80%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 45%, transparent 80%);
  pointer-events: none;
  z-index: 2;
}

/* Brand Content Layout */
.brand-content-wrapper {
  position: relative;
  z-index: 10;
  max-width: 520px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.35rem;
  animation: brandFadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Top Bar */
.brand-top-bar {
  display: flex;
  align-items: center;
  gap: 1.15rem;
}

.brand-logo-pill {
  height: 52px;
  padding: 6px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 24px -4px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.brand-logo-img-left {
  height: 38px;
  width: auto;
  max-width: 160px;
  object-fit: contain;
  display: block;
}

.top-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.motto-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.16);
  padding: 0.25rem 0.7rem;
  border-radius: 9999px;
  border: 1px solid rgba(245, 158, 11, 0.35);
  width: fit-content;
}

.star-icon {
  font-size: 0.75rem;
}

.school-name-text {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

/* Hero Section */
.brand-hero-section {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.hero-display-headline {
  font-family: var(--font-family-heading, 'Outfit', sans-serif);
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.12;
  color: #ffffff;
  letter-spacing: -0.025em;
}

.hero-highlight {
  background: linear-gradient(135deg, #38bdf8 0%, #93c5fd 60%, #ffffff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-subtext {
  font-size: 1.05rem;
  color: #cbd5e1;
  line-height: 1.6;
  max-width: 480px;
}

/* Feature Highlights Grid */
.features-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 0.65rem 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.11);
  border-color: rgba(255, 255, 255, 0.24);
  transform: translateX(4px);
}

.feature-num-badge {
  font-size: 0.75rem;
  font-weight: 800;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.feature-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(23, 78, 166, 0.4);
  border: 1px solid rgba(56, 189, 248, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7dd3fc;
  flex-shrink: 0;
}

.feature-icon-wrap svg {
  width: 17px;
  height: 17px;
}

.feature-body {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.feature-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.01em;
}

.feature-desc {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Bottom Footer */
.brand-bottom-footer {
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  font-size: 0.775rem;
  color: #94a3b8;
}

.footer-app-name {
  font-weight: 600;
  color: #cbd5e1;
}

.footer-divider {
  color: #64748b;
}

.footer-tagline {
  color: #7dd3fc;
  letter-spacing: 0.03em;
}

/* ==========================================================================
   ORGANIC CURVE DIVIDERS
   ========================================================================== */
.desktop-curve-container {
  position: absolute;
  top: 0;
  right: -1px;
  bottom: 0;
  width: 110px;
  height: 100%;
  pointer-events: none;
  z-index: 5;
}

.desktop-curve-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.mobile-curve-container {
  display: none;
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  width: 100%;
  height: 48px;
  pointer-events: none;
  z-index: 5;
}

.mobile-curve-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* ==========================================================================
   Animations
   ========================================================================== */
@keyframes brandFadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Media Queries for Brand Panel */
@media (max-width: 1280px) {
  .brand-panel {
    padding: 3.5rem 3.5rem;
  }
  .hero-display-headline {
    font-size: 2.3rem;
  }
}

@media (max-width: 1080px) and (min-width: 861px) {
  .brand-panel {
    padding: 2.5rem 2.5rem;
  }
  .hero-display-headline {
    font-size: 2rem;
  }
  .desktop-curve-container {
    width: 80px;
  }
}

@media (max-width: 860px) {
  .brand-panel {
    flex: none;
    width: 100%;
    padding: 2.75rem 1.5rem 4.25rem 1.5rem;
    align-items: flex-start;
  }

  .desktop-curve-container {
    display: none;
  }

  .mobile-curve-container {
    display: block;
  }

  .brand-content-wrapper {
    max-width: 480px;
    margin: 0 auto;
    gap: 1.25rem;
  }

  .hero-display-headline {
    font-size: 1.85rem;
  }

  .hero-subtext {
    font-size: 0.925rem;
  }

  .features-list {
    display: none; /* Keep mobile view clean, uncluttered, and fast */
  }

  .brand-bottom-footer {
    display: none;
  }
}

@media (max-width: 430px) {
  .brand-panel {
    padding: 2.25rem 1.15rem 3.75rem 1.15rem;
  }

  .logo-emblem {
    width: 52px;
    height: 52px;
  }

  .logo-img {
    width: 36px;
    height: 36px;
  }

  .hero-display-headline {
    font-size: 1.6rem;
  }
}
</style>
