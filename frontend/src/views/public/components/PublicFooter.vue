<template>
  <footer class="public-footer">
    <!-- Top Organic Wave Transition -->
    <div class="footer-top-wave-container" aria-hidden="true">
      <svg
        class="footer-top-wave-svg"
        viewBox="0 0 1440 85"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="waveOrangeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FF7A00" />
            <stop offset="100%" stop-color="#FF5500" />
          </linearGradient>
        </defs>

        <!-- Deep navy base fill -->
        <path d="M 0,0 L 1440,0 L 1440,85 L 0,85 Z" fill="#061B3B" />

        <!-- Top-left orange wave swoosh -->
        <path d="M 0,0 L 460,0 C 370,26 230,68 100,68 C 45,68 12,50 0,36 Z" fill="url(#waveOrangeGrad)" />
        <!-- Top-left white cap -->
        <path d="M 0,0 L 410,0 C 320,16 190,44 75,44 C 28,44 8,28 0,16 Z" fill="#FFFFFF" />

        <!-- Top-right orange wave swoosh -->
        <path d="M 940,0 C 1030,16 1140,62 1270,62 C 1350,62 1408,30 1440,0 Z" fill="url(#waveOrangeGrad)" />
        <!-- Top-right white cap -->
        <path d="M 1010,0 C 1085,12 1175,40 1270,40 C 1345,40 1402,16 1440,0 Z" fill="#FFFFFF" />

        <!-- Ambient orange sheen line -->
        <path d="M 0,36 C 12,50 45,68 100,68 C 230,68 370,26 460,0" fill="none" stroke="rgba(255, 122, 0, 0.45)" stroke-width="1.5" />
        <path d="M 940,0 C 1030,16 1140,62 1270,62 C 1350,62 1408,30 1440,0" fill="none" stroke="rgba(255, 122, 0, 0.45)" stroke-width="1.5" />
      </svg>
    </div>

    <!-- Background Decorative Elements -->
    <div class="footer-bg-decorations" aria-hidden="true">
      <!-- Subtle Dotted World Map spanning Left & Center -->
      <img src="/world-map-dots.svg" alt="" class="footer-bg-map" />
      <!-- Subtle Crown & Diamond Emblem Watermark on Right -->
      <img src="/somroyal-watermark.png" alt="" class="footer-bg-watermark" />
      <!-- Soft ambient radial blue glow -->
      <div class="footer-ambient-glow"></div>
    </div>

    <div class="footer-container">
      <!-- MAIN 4-COLUMN GRID -->
      <div class="footer-main-grid">
        <!-- COLUMN 1: Brand & Contact Information -->
        <div class="footer-col col-brand">
          <a href="#hero" class="footer-logo-link" @click.prevent="emitScroll('hero')" title="Somroyal EMS Home">
            <img
              src="/somroyal-logo-dark.png"
              alt="Somroyal Technology Solutions"
              class="footer-brand-logo"
            />
          </a>

          <p class="footer-brand-desc">
            Somroyal Educational Management System (SEMS) is a premier school management platform providing modern administration, examination, and fee tracking solutions for schools of all sizes.
          </p>

          <!-- Contact Details with Orange Lucide Icons -->
          <div class="footer-contact-list">
            <div class="contact-item">
              <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span class="contact-text">Abudwak, Galgaduud, Somalia</span>
            </div>

            <a href="tel:+252612508505" class="contact-item contact-link">
              <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
              </svg>
              <span class="contact-text">+252 61 250 8505</span>
            </a>

            <a href="mailto:somroyaltech@gmail.com" class="contact-item contact-link">
              <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="20" height="16" x="2" y="4" rx="2" />
                <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
              </svg>
              <span class="contact-text">somroyaltech@gmail.com</span>
            </a>

            <a href="https://www.somroyal.com" target="_blank" rel="noopener noreferrer" class="contact-item contact-link">
              <svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="2" x2="22" y1="12" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              <span class="contact-text">www.somroyal.com</span>
            </a>
          </div>

          <!-- Circular Social Media Buttons -->
          <div class="footer-social-row">
            <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" class="social-btn" aria-label="Facebook">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" />
              </svg>
            </a>
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" class="social-btn" aria-label="X / Twitter">
              <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" class="social-btn" aria-label="LinkedIn">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76a1.53 1.53 0 1 0 0-3.06 1.53 1.53 0 0 0 0 3.06m1.39 9.74v-8.37H5.07v8.37h2.78z" />
              </svg>
            </a>
            <a href="https://youtube.com" target="_blank" rel="noopener noreferrer" class="social-btn" aria-label="YouTube">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" class="social-btn" aria-label="Instagram">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z" />
              </svg>
            </a>
          </div>
        </div>

        <!-- COLUMN 2: Quick Navigation -->
        <div class="footer-col col-nav">
          <div class="col-heading-group">
            <h4 class="footer-col-title">Quick Navigation</h4>
            <div class="orange-accent-line"></div>
          </div>

          <ul class="footer-icon-list">
            <li>
              <a href="#hero" class="nav-item-link" @click.prevent="emitScroll('hero')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                    <polyline points="9 22 9 12 15 12 15 22" />
                  </svg>
                  <span>Home</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" x2="8" y1="13" y2="13" />
                    <line x1="16" x2="8" y1="17" y2="17" />
                    <line x1="10" x2="8" y1="9" y2="9" />
                  </svg>
                  <span>Features</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#about" class="nav-item-link" @click.prevent="emitScroll('about')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                  <span>About Us</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#benefits" class="nav-item-link" @click.prevent="emitScroll('benefits')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    <path d="m9 12 2 2 4-4" />
                  </svg>
                  <span>Benefits</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#how-it-works" class="nav-item-link" @click.prevent="emitScroll('how-it-works')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                  </svg>
                  <span>How It Works</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#pricing" class="nav-item-link" @click.prevent="emitScroll('pricing')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                    <line x1="7" x2="7.01" y1="7" y2="7" />
                  </svg>
                  <span>Pricing</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#contact" class="nav-item-link" @click.prevent="emitScroll('contact')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  <span>Contact</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>
          </ul>
        </div>

        <!-- COLUMN 3: Platform Modules -->
        <div class="footer-col col-modules">
          <div class="col-heading-group">
            <h4 class="footer-col-title">Platform Modules</h4>
            <div class="orange-accent-line"></div>
          </div>

          <ul class="footer-icon-list">
            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                    <path d="M6 12v5c3 3 9 3 12 0v-5" />
                  </svg>
                  <span>Student Bio-Data</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                  </svg>
                  <span>Class Streams & Sections</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" x2="8" y1="13" y2="13" />
                    <line x1="16" x2="8" y1="17" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                  </svg>
                  <span>Examinations & Grading</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="20" height="14" x="2" y="5" rx="2" />
                    <line x1="2" x2="22" y1="10" y2="10" />
                  </svg>
                  <span>Fee Invoicing (EVC/ZAAD)</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <span>Hormuud SMS Alerts</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                  <span>Faculty Teacher Portal</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>

            <li>
              <a href="#features" class="nav-item-link" @click.prevent="emitScroll('features')">
                <span class="nav-link-left">
                  <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="20" height="14" x="2" y="3" rx="2" />
                    <line x1="8" x2="16" y1="21" y2="21" />
                    <line x1="12" x2="12" y1="17" y2="21" />
                  </svg>
                  <span>Student Self-Service Portal</span>
                </span>
                <svg class="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </a>
            </li>
          </ul>
        </div>

        <!-- COLUMN 4: Portal Access -->
        <div class="footer-col col-portal">
          <div class="col-heading-group">
            <h4 class="footer-col-title">Portal Access</h4>
            <div class="orange-accent-line"></div>
          </div>

          <p class="portal-desc">
            Existing faculty, administrators, and enrolled students can sign in securely through the unified authentication portal.
          </p>

          <!-- Large Prominent Orange Sign In CTA Button -->
          <router-link to="/login" class="btn-portal-signin" id="footer-btn-signin">
            <span class="signin-btn-inner">
              <svg class="signin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" x2="3" y1="12" y2="12" />
              </svg>
              <span class="signin-text">Sign In to System</span>
              <svg class="signin-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </span>
          </router-link>
        </div>
      </div>

      <!-- TRUST & BENEFITS STRIP -->
      <div class="footer-benefits-strip">
        <!-- Benefit 1 -->
        <div class="benefit-item">
          <div class="benefit-icon-badge">
            <svg class="benefit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <div class="benefit-text">
            <h5 class="benefit-title">Secure &amp; Reliable</h5>
            <p class="benefit-subtitle">Your data is always safe</p>
          </div>
        </div>

        <div class="benefit-divider" aria-hidden="true"></div>

        <!-- Benefit 2 -->
        <div class="benefit-item">
          <div class="benefit-icon-badge">
            <svg class="benefit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 18v-6a9 9 0 0 1 18 0v6" />
              <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" />
              <path d="M17 19a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2" />
            </svg>
          </div>
          <div class="benefit-text">
            <h5 class="benefit-title">24/7 Support</h5>
            <p class="benefit-subtitle">We are here to help</p>
          </div>
        </div>

        <div class="benefit-divider" aria-hidden="true"></div>

        <!-- Benefit 3 -->
        <div class="benefit-item">
          <div class="benefit-icon-badge">
            <svg class="benefit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="14" height="10" x="2" y="3" rx="1.5" />
              <rect width="7" height="12" x="15" y="9" rx="1.5" />
              <line x1="6" x2="10" y1="17" y2="17" />
            </svg>
          </div>
          <div class="benefit-text">
            <h5 class="benefit-title">Multi-Device</h5>
            <p class="benefit-subtitle">Access anywhere</p>
          </div>
        </div>

        <div class="benefit-divider" aria-hidden="true"></div>

        <!-- Benefit 4 -->
        <div class="benefit-item">
          <div class="benefit-icon-badge">
            <svg class="benefit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div class="benefit-text">
            <h5 class="benefit-title">Trusted by Schools</h5>
            <p class="benefit-subtitle">Across Somalia</p>
          </div>
        </div>
      </div>

      <!-- COPYRIGHT AND LEGAL ROW -->
      <div class="footer-copyright-row">
        <div class="footer-copy-text">
          &copy; {{ currentYear }} Somroyal Educational Management System (SEMS). All rights reserved.
        </div>
        <div class="footer-legal-links">
          <button type="button" class="legal-link-btn" @click="emit('open-privacy')">
            Privacy Policy
          </button>
          <span class="legal-pipe" aria-hidden="true">|</span>
          <button type="button" class="legal-link-btn" @click="emit('open-terms')">
            Terms of Service
          </button>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

const emit = defineEmits<{
  (e: 'scroll', target: string): void;
  (e: 'open-privacy'): void;
  (e: 'open-terms'): void;
}>();

const currentYear = computed(() => new Date().getFullYear());

function emitScroll(target: string) {
  emit('scroll', target);
}
</script>

<style scoped>
/* MAIN FOOTER WRAPPER */
.public-footer {
  position: relative;
  background: linear-gradient(180deg, #061B3B 0%, #071A36 60%, #05152F 100%);
  color: #B8C8E0;
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
  margin-top: 0;
  padding: 0 0 2rem;
  box-sizing: border-box;
}

/* TOP ORGANIC WAVE HEADER */
.footer-top-wave-container {
  width: 100%;
  line-height: 0;
  margin-bottom: 2rem;
}

.footer-top-wave-svg {
  width: 100%;
  height: 65px;
  display: block;
}

/* BACKGROUND DECORATIONS */
.footer-bg-decorations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1;
}

.footer-bg-map {
  position: absolute;
  top: 15px;
  left: 2%;
  width: 780px;
  max-width: 65vw;
  opacity: 0.16;
  filter: drop-shadow(0 0 12px rgba(85, 142, 210, 0.25));
  mix-blend-mode: screen;
}

.footer-bg-watermark {
  position: absolute;
  top: 20px;
  right: -30px;
  width: 380px;
  max-width: 32vw;
  opacity: 0.12;
  filter: drop-shadow(0 8px 30px rgba(0, 0, 0, 0.4));
}

.footer-ambient-glow {
  position: absolute;
  top: 10%;
  left: 20%;
  width: 600px;
  height: 350px;
  background: radial-gradient(circle, rgba(85, 142, 210, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

/* CONTAINER */
.footer-container {
  position: relative;
  z-index: 2;
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* 4-COLUMN MAIN GRID */
.footer-main-grid {
  display: grid;
  grid-template-columns: 1.45fr 1fr 1.15fr 1.25fr;
  gap: 2.25rem;
  padding-bottom: 2.75rem;
}

.footer-col {
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Thin vertical separators between columns on desktop */
.footer-col:not(:last-child) {
  padding-right: 1.75rem;
  border-right: 1px solid rgba(85, 142, 210, 0.16);
}

/* COLUMN 1: BRAND */
.col-brand {
  gap: 1.1rem;
}

.footer-logo-link {
  display: inline-block;
  width: fit-content;
  transition: transform 0.2s ease;
}

.footer-logo-link:hover {
  transform: translateY(-1px);
}

.footer-brand-logo {
  height: 48px;
  width: auto;
  object-fit: contain;
  display: block;
}

.footer-brand-desc {
  font-size: 0.88rem;
  line-height: 1.68;
  color: #B8C8E0;
  margin: 0;
  max-width: 380px;
}

/* CONTACT LIST */
.footer-contact-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-top: 0.25rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
  color: #D6E2F5;
  text-decoration: none;
  transition: all 0.2s ease;
}

.contact-link {
  cursor: pointer;
}

.contact-link:hover {
  color: #FFFFFF;
  transform: translateX(2px);
}

.contact-link:hover .contact-icon {
  transform: scale(1.1);
  color: #FF7A00;
}

.contact-icon {
  width: 17px;
  height: 17px;
  color: #FF6900;
  flex-shrink: 0;
  transition: transform 0.2s ease, color 0.2s ease;
}

.contact-text {
  font-weight: 400;
  letter-spacing: 0.01em;
}

/* SOCIAL MEDIA BUTTONS */
.footer-social-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.5rem;
}

.social-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  min-width: 42px;
  min-height: 42px;
  border-radius: 50%;
  background: #0C2346;
  border: 1px solid rgba(85, 142, 210, 0.28);
  color: #FFFFFF;
  text-decoration: none;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.social-btn:hover {
  background: #FF6900;
  border-color: #FF6900;
  color: #FFFFFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(255, 105, 0, 0.35);
}

/* HEADINGS & ORANGE ACCENT LINE */
.col-heading-group {
  margin-bottom: 1.15rem;
}

.footer-col-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0 0 0.5rem;
  letter-spacing: -0.01em;
}

.orange-accent-line {
  width: 36px;
  height: 3px;
  background: linear-gradient(90deg, #FF6900 0%, #FF7A00 100%);
  border-radius: 2px;
}

/* ICON LIST (COLS 2 & 3) */
.footer-icon-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-item-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.25rem;
  color: #B8C8E0;
  text-decoration: none;
  font-size: 0.88rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nav-link-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: transform 0.2s ease;
}

.item-icon {
  width: 17px;
  height: 17px;
  color: #A3B8D8;
  flex-shrink: 0;
  transition: color 0.2s ease, transform 0.2s ease;
}

.chevron-icon {
  width: 15px;
  height: 15px;
  color: rgba(184, 200, 224, 0.4);
  flex-shrink: 0;
  transition: transform 0.2s ease, color 0.2s ease;
}

.nav-item-link:hover {
  color: #FFFFFF;
}

.nav-item-link:hover .nav-link-left {
  transform: translateX(4px);
}

.nav-item-link:hover .item-icon {
  color: #FF6900;
}

.nav-item-link:hover .chevron-icon {
  color: #FF6900;
  transform: translateX(2px);
}

/* COLUMN 4: PORTAL ACCESS */
.portal-desc {
  font-size: 0.88rem;
  line-height: 1.68;
  color: #B8C8E0;
  margin: 0 0 1.5rem;
}

.btn-portal-signin {
  display: block;
  width: 100%;
  max-width: 290px;
  background: linear-gradient(135deg, #FF6900 0%, #FF7A00 100%);
  color: #FFFFFF;
  text-decoration: none;
  border-radius: 10px;
  padding: 0.9rem 1.4rem;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 6px 22px rgba(255, 105, 0, 0.38), 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-sizing: border-box;
}

.signin-btn-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.75rem;
}

.signin-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.signin-text {
  flex-grow: 1;
  text-align: left;
  letter-spacing: -0.01em;
}

.signin-arrow {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.btn-portal-signin:hover {
  background: linear-gradient(135deg, #FF7A00 0%, #FF8D1A 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(255, 105, 0, 0.5), 0 3px 8px rgba(0, 0, 0, 0.3);
}

.btn-portal-signin:hover .signin-arrow {
  transform: translateX(3px);
}

.btn-portal-signin:focus-visible {
  outline: 2px solid #FFFFFF;
  outline-offset: 3px;
}

/* TRUST & BENEFITS STRIP */
.footer-benefits-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.6rem 0;
  border-top: 1px solid rgba(85, 142, 210, 0.25);
  border-bottom: 1px solid rgba(85, 142, 210, 0.25);
  background: linear-gradient(90deg, rgba(10, 40, 82, 0.4) 0%, rgba(6, 27, 59, 0.6) 50%, rgba(10, 40, 82, 0.4) 100%);
  backdrop-filter: blur(8px);
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  padding: 0 1.25rem;
}

.benefit-icon-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: radial-gradient(circle, #0F2D59 0%, #0A2246 100%);
  border: 1px solid rgba(85, 142, 210, 0.35);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.benefit-item:hover .benefit-icon-badge {
  transform: scale(1.06);
  border-color: #FF6900;
}

.benefit-icon {
  width: 22px;
  height: 22px;
  color: #FF6900;
}

.benefit-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.benefit-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #FFFFFF;
  margin: 0;
  letter-spacing: -0.01em;
}

.benefit-subtitle {
  font-size: 0.8rem;
  color: #B8C8E0;
  margin: 0;
}

.benefit-divider {
  width: 1px;
  height: 38px;
  background: rgba(85, 142, 210, 0.25);
  flex-shrink: 0;
}

/* COPYRIGHT AND LEGAL ROW */
.footer-copyright-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.5rem;
  font-size: 0.825rem;
  color: #8E9EB5;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-copy-text {
  color: #8E9EB5;
}

.footer-legal-links {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.legal-link-btn {
  background: none;
  border: none;
  color: #B8C8E0;
  font-size: 0.825rem;
  font-family: inherit;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.legal-link-btn:hover {
  color: #FF7A00;
  text-decoration: underline;
}

.legal-pipe {
  color: rgba(85, 142, 210, 0.4);
}

/* RESPONSIVE BREAKPOINTS */
@media (max-width: 1180px) {
  .footer-main-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem;
  }
  .footer-col:not(:last-child) {
    border-right: none;
    padding-right: 0;
  }
  .footer-col:nth-child(1) {
    border-right: 1px solid rgba(85, 142, 210, 0.16);
    padding-right: 2rem;
  }
  .footer-col:nth-child(3) {
    border-right: 1px solid rgba(85, 142, 210, 0.16);
    padding-right: 2rem;
  }
  .footer-benefits-strip {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }
  .benefit-divider {
    display: none;
  }
}

@media (max-width: 768px) {
  .footer-container {
    padding: 0 clamp(0.85rem, 3vw, 1.25rem);
  }
  .footer-main-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .footer-col:nth-child(1),
  .footer-col:nth-child(3) {
    border-right: none;
    padding-right: 0;
  }
  .footer-bg-map {
    width: 100%;
    max-width: 90vw;
  }
  .footer-bg-watermark {
    width: 240px;
    opacity: 0.08;
    right: -20px;
  }
  .footer-benefits-strip {
    grid-template-columns: 1fr;
    gap: 1.25rem;
    padding: 1.25rem 1rem;
  }
  .footer-copyright-row {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.85rem;
  }
  .footer-legal-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.85rem;
  }
}

@media (max-width: 480px) {
  .footer-brand-title {
    font-size: 1.15rem;
  }
  .footer-contact-link,
  .footer-link {
    font-size: 0.85rem;
    padding: 0.25rem 0;
  }
  .legal-link-btn {
    font-size: 0.78rem;
  }
  .copyright-text {
    font-size: 0.78rem;
  }
}
</style>
