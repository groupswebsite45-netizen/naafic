<template>
  <section id="about" class="about-section">
    <!-- Abstract Background Decorations -->
    <div class="about-bg-decorations" aria-hidden="true">
      <div class="bg-glow-top-left"></div>
      <div class="bg-glow-center-right"></div>
      
      <!-- Top-right dashed curved arc -->
      <svg class="bg-curved-arc-svg" viewBox="0 0 350 200" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 180 C 120 40, 250 20, 340 100" stroke="#FF6900" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 4" opacity="0.45" />
      </svg>

      <!-- Bottom-Left Layered Corner Waves -->
      <div class="corner-waves-left">
        <svg viewBox="0 0 340 240" fill="none" xmlns="http://www.w3.org/2000/svg" class="corner-wave-svg">
          <path d="M0 240V120C70 140 140 170 190 240H0Z" fill="rgba(85, 142, 210, 0.22)" />
          <path d="M0 240V150C90 145 160 185 210 240H0Z" fill="#FF6900" />
          <path d="M0 240V175C70 175 130 195 165 240H0Z" fill="#071D49" />
        </svg>
      </div>

      <!-- Bottom-Right Layered Corner Waves -->
      <div class="corner-waves-right">
        <svg viewBox="0 0 340 260" fill="none" xmlns="http://www.w3.org/2000/svg" class="corner-wave-svg">
          <!-- Orange wave rising -->
          <path d="M340 260V80C270 120 230 180 150 260H340Z" fill="#FF6900" />
          <!-- Deep Navy wave -->
          <path d="M340 260V135C280 170 250 215 200 260H340Z" fill="#071D49" />
          <path d="M150 260C230 180 270 120 340 80" stroke="rgba(85, 142, 210, 0.4)" stroke-width="2" />
        </svg>
      </div>
    </div>

    <div class="about-container">
      <!-- 1. HERO SECTION (TWO-COLUMN) -->
      <div class="about-hero-grid">
        <!-- LEFT COLUMN: Brand Story & Values -->
        <div class="hero-left-content">
          <!-- Small Badge Pill -->
          <div class="about-badge-pill">
            <svg class="badge-building-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
              <path d="M9 22v-4h6v4" />
              <path d="M8 6h.01" />
              <path d="M16 6h.01" />
              <path d="M8 10h.01" />
              <path d="M16 10h.01" />
              <path d="M8 14h.01" />
              <path d="M16 14h.01" />
            </svg>
            <span>ABOUT SOMROYAL TECHNOLOGY SOLUTIONS</span>
          </div>

          <!-- Main Heading -->
          <h1 class="about-main-title">
            Innovative Software Solutions<br />
            for a <span class="highlight-orange">Smarter Tomorrow</span>
          </h1>

          <!-- Company Description -->
          <p class="about-company-desc">
            Somroyal Technology Solutions is a leading software development company dedicated to building modern, reliable, and scalable systems for businesses and institutions across Somalia and beyond. We empower organizations through technology, helping them operate more efficiently, make data-driven decisions, and achieve sustainable growth.
          </p>

          <!-- 4 COMPANY VALUE PILLARS (HORIZONTAL ROW) -->
          <div class="value-pillars-row">
            <!-- Pillar 1: Innovation -->
            <div class="value-pillar-item">
              <div class="pillar-icon-box bg-orange-tint text-orange">
                <svg class="pillar-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
                  <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
                  <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
                  <path d="M12 9v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
                </svg>
              </div>
              <div class="pillar-text-group">
                <h4 class="pillar-name">Innovation</h4>
                <p class="pillar-subtext">Modern solutions<br />for real needs</p>
              </div>
            </div>

            <!-- Pillar 2: Reliability -->
            <div class="value-pillar-item">
              <div class="pillar-icon-box bg-blue-tint text-blue">
                <svg class="pillar-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <div class="pillar-text-group">
                <h4 class="pillar-name">Reliability</h4>
                <p class="pillar-subtext">Secure, stable<br />and trusted systems</p>
              </div>
            </div>

            <!-- Pillar 3: Client Success -->
            <div class="value-pillar-item">
              <div class="pillar-icon-box bg-orange-tint text-orange">
                <svg class="pillar-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </div>
              <div class="pillar-text-group">
                <h4 class="pillar-name">Client Success</h4>
                <p class="pillar-subtext">Your growth<br />is our priority</p>
              </div>
            </div>

            <!-- Pillar 4: Long-Term Partnership -->
            <div class="value-pillar-item">
              <div class="pillar-icon-box bg-blue-tint text-blue">
                <svg class="pillar-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 20V10" />
                  <path d="M12 20V4" />
                  <path d="M6 20v-6" />
                </svg>
              </div>
              <div class="pillar-text-group">
                <h4 class="pillar-name">Long-Term Partnership</h4>
                <p class="pillar-subtext">We build lasting<br />relationships</p>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: Branded Headquarters Building & Floating Cards -->
        <div class="hero-right-visual">
          <!-- Background Dotted Matrix Patterns -->
          <div class="dots-pattern-top-left" aria-hidden="true">
            <div v-for="i in 16" :key="'tl'+i" class="dot-spec"></div>
          </div>
          <div class="dots-pattern-top-right" aria-hidden="true">
            <div v-for="i in 20" :key="'tr'+i" class="dot-spec"></div>
          </div>

          <!-- Building Image Frame with Perspective Glass Signage -->
          <div class="building-image-container">
            <img
              src="/somroyal-hq-building.png"
              alt="Somroyal Technology Solutions Corporate Headquarters"
              class="building-photo"
            />

            <!-- Floating Card Top: "Transforming Businesses Through Technology" -->
            <div class="floating-bubble-top">
              <span class="bubble-text">
                Transforming<br />
                Businesses Through<br />
                Technology
              </span>
              <!-- Curved orange arrow pointing toward the building -->
              <svg class="bubble-arrow-svg" viewBox="0 0 50 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 8 C 25 6, 38 18, 42 34" stroke="#FF6900" stroke-width="2" stroke-linecap="round" />
                <path d="M34 28 L 42 34 L 46 25" stroke="#FF6900" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>

            <!-- Floating Card Center-Left: "Custom Software Development" -->
            <div class="floating-custom-card">
              <div class="custom-card-icon">
                <svg class="w-5 h-5 text-orange" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </div>
              <div class="custom-card-text">
                <h5 class="custom-card-title">Custom Software<br />Development</h5>
                <span class="custom-card-sub">For Every Industry</span>
              </div>
            </div>

            <!-- Vertical Stack of 5 Floating Industry Cards (Right side) -->
            <div class="floating-industries-stack">
              <!-- Item 1: Hospitals -->
              <div class="industry-chip-card">
                <div class="chip-icon-box chip-red">
                  <svg class="chip-svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 4a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v6h6a2 2 0 0 1 2 2h0a2 2 0 0 1-2 2h-6v6a2 2 0 0 1-2 2h0a2 2 0 0 1-2-2v-6H4a2 2 0 0 1-2-2h0a2 2 0 0 1 2-2h6V4z" />
                  </svg>
                </div>
                <span class="chip-title">Hospitals</span>
              </div>

              <!-- Item 2: Retail & Supermarkets -->
              <div class="industry-chip-card">
                <div class="chip-icon-box chip-blue">
                  <svg class="chip-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="8" cy="21" r="1" />
                    <circle cx="19" cy="21" r="1" />
                    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
                  </svg>
                </div>
                <span class="chip-title">Retail &amp; Supermarkets</span>
              </div>

              <!-- Item 3: Gas Stations -->
              <div class="industry-chip-card">
                <div class="chip-icon-box chip-green">
                  <svg class="chip-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18" />
                    <path d="M15 10h2a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0 2-2V9.83a2 2 0 0 0-.59-1.42L19.7 5.7a2 2 0 0 0-1.41-.59H15" />
                    <rect width="6" height="5" x="6" y="6" rx="1" />
                    <path d="M3 22h12" />
                  </svg>
                </div>
                <span class="chip-title">Gas Stations</span>
              </div>

              <!-- Item 4: Schools & Education -->
              <div class="industry-chip-card">
                <div class="chip-icon-box chip-orange">
                  <svg class="chip-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                    <path d="M6 12v5c3 3 9 3 12 0v-5" />
                  </svg>
                </div>
                <span class="chip-title">Schools &amp; Education</span>
              </div>

              <!-- Item 5: And More... -->
              <div class="industry-chip-card">
                <div class="chip-icon-box chip-purple">
                  <svg class="chip-svg" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="5" cy="12" r="2" />
                    <circle cx="12" cy="12" r="2" />
                    <circle cx="19" cy="12" r="2" />
                  </svg>
                </div>
                <span class="chip-title">And More...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. INDUSTRIES WE SERVE PANEL -->
      <div class="industries-panel">
        <div class="panel-header-row">
          <div class="panel-title-group">
            <div class="orange-accent-dash"></div>
            <h3 class="panel-main-heading">Industries We Serve</h3>
            <p class="panel-sub-desc">
              We develop customized software solutions for a wide range of industries, helping them streamline operations, improve efficiency, and achieve their goals.
            </p>
          </div>

          <a href="#contact" class="btn-explore-industries" @click.prevent="scrollToContact">
            <span>Explore All Industries</span>
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" x2="19" y1="12" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </a>
        </div>

        <!-- 8 Industry Cards Grid -->
        <div class="industry-cards-grid">
          <!-- Card 1: Education -->
          <div class="industry-card">
            <div class="card-icon-frame icon-blue">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                <path d="M6 12v5c3 3 9 3 12 0v-5" />
              </svg>
            </div>
            <h4 class="card-industry-title">Education</h4>
            <p class="card-industry-desc">School Management Systems (SEMS)</p>
          </div>

          <!-- Card 2: Healthcare -->
          <div class="industry-card">
            <div class="card-icon-frame icon-red">
              <svg class="card-svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M10 4a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v6h6a2 2 0 0 1 2 2h0a2 2 0 0 1-2 2h-6v6a2 2 0 0 1-2 2h0a2 2 0 0 1-2-2v-6H4a2 2 0 0 1-2-2h0a2 2 0 0 1 2-2h6V4z" />
              </svg>
            </div>
            <h4 class="card-industry-title">Healthcare</h4>
            <p class="card-industry-desc">Hospital Management Systems (HMS)</p>
          </div>

          <!-- Card 3: Retail & Supermarkets -->
          <div class="industry-card">
            <div class="card-icon-frame icon-blue">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="8" cy="21" r="1" />
                <circle cx="19" cy="21" r="1" />
                <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
              </svg>
            </div>
            <h4 class="card-industry-title">Retail &amp; Supermarkets</h4>
            <p class="card-industry-desc">Inventory, Sales &amp; Business Management</p>
          </div>

          <!-- Card 4: Gas Stations -->
          <div class="industry-card">
            <div class="card-icon-frame icon-green">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18" />
                <path d="M15 10h2a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0 2-2V9.83a2 2 0 0 0-.59-1.42L19.7 5.7a2 2 0 0 0-1.41-.59H15" />
                <rect width="6" height="5" x="6" y="6" rx="1" />
                <path d="M3 22h12" />
              </svg>
            </div>
            <h4 class="card-industry-title">Gas Stations</h4>
            <p class="card-industry-desc">Fuel Station Management &amp; POS Systems</p>
          </div>

          <!-- Card 5: Manufacturing -->
          <div class="industry-card">
            <div class="card-icon-frame icon-orange">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z" />
                <path d="M17 18h1" />
                <path d="M12 18h1" />
                <path d="M7 18h1" />
              </svg>
            </div>
            <h4 class="card-industry-title">Manufacturing</h4>
            <p class="card-industry-desc">Production &amp; Inventory Management</p>
          </div>

          <!-- Card 6: Hospitality -->
          <div class="industry-card">
            <div class="card-icon-frame icon-purple">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10 22v-6.57" />
                <path d="M12 11h.01" />
                <path d="M12 7h.01" />
                <path d="M14 15.43V22" />
                <path d="M15 11h.01" />
                <path d="M15 7h.01" />
                <path d="M16 16h3a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h3" />
                <path d="M9 11h.01" />
                <path d="M9 7h.01" />
              </svg>
            </div>
            <h4 class="card-industry-title">Hospitality</h4>
            <p class="card-industry-desc">Hotel &amp; Restaurant Management</p>
          </div>

          <!-- Card 7: Logistics & Transport -->
          <div class="industry-card">
            <div class="card-icon-frame icon-pink">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2" />
                <path d="M15 18H9" />
                <path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14" />
                <circle cx="17" cy="18" r="2" />
                <circle cx="7" cy="18" r="2" />
              </svg>
            </div>
            <h4 class="card-industry-title">Logistics &amp; Transport</h4>
            <p class="card-industry-desc">Fleet &amp; Transport Management</p>
          </div>

          <!-- Card 8: Custom Solutions -->
          <div class="industry-card">
            <div class="card-icon-frame icon-blue">
              <svg class="card-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 18 22 12 16 6" />
                <polyline points="8 6 2 12 8 18" />
              </svg>
            </div>
            <h4 class="card-industry-title">Custom Solutions</h4>
            <p class="card-industry-desc">Tailored Systems for Your Unique Needs</p>
          </div>
        </div>
      </div>

      <!-- 3. COMPANY STATISTICS STRIP -->
      <div class="company-stats-strip">
        <!-- Stat 1: Happy Clients -->
        <div class="stat-unit">
          <div class="stat-icon-circle">
            <svg class="stat-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </div>
          <div class="stat-meta">
            <div class="stat-number">100+</div>
            <div class="stat-title">Happy Clients</div>
            <div class="stat-desc">Across Somalia and beyond</div>
          </div>
        </div>

        <div class="stat-divider" aria-hidden="true"></div>

        <!-- Stat 2: Systems Delivered -->
        <div class="stat-unit">
          <div class="stat-icon-circle">
            <svg class="stat-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </div>
          <div class="stat-meta">
            <div class="stat-number">20+</div>
            <div class="stat-title">Systems Delivered</div>
            <div class="stat-desc">For different industries</div>
          </div>
        </div>

        <div class="stat-divider" aria-hidden="true"></div>

        <!-- Stat 3: Satisfaction Rate -->
        <div class="stat-unit">
          <div class="stat-icon-circle">
            <svg class="stat-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <div class="stat-meta">
            <div class="stat-number">99.9%</div>
            <div class="stat-title">Satisfaction Rate</div>
            <div class="stat-desc">Trusted by our clients</div>
          </div>
        </div>

        <div class="stat-divider" aria-hidden="true"></div>

        <!-- Stat 4: Years of Experience -->
        <div class="stat-unit">
          <div class="stat-icon-circle">
            <svg class="stat-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="8" r="6" />
              <path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" />
            </svg>
          </div>
          <div class="stat-meta">
            <div class="stat-number">5+</div>
            <div class="stat-title">Years of Experience</div>
            <div class="stat-desc">In software development</div>
          </div>
        </div>
      </div>

      <!-- 4. BOTTOM CALL-TO-ACTION BANNER -->
      <div class="about-cta-banner">
        <div class="cta-banner-inner">
          <!-- Left: Target Dart Icon -->
          <div class="cta-target-icon-box">
            <svg class="target-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Outer circle -->
              <circle cx="30" cy="34" r="22" stroke="#FFFFFF" stroke-width="3" stroke-opacity="0.85" />
              <!-- Middle circle -->
              <circle cx="30" cy="34" r="14" stroke="#558ED2" stroke-width="2.5" />
              <!-- Inner bulls eye -->
              <circle cx="30" cy="34" r="6" fill="#FF6900" />
              
              <!-- Dart / Arrow hitting center from top-right -->
              <path d="M54 10 L 32 32" stroke="#FF6900" stroke-width="3.5" stroke-linecap="round" />
              <path d="M54 10 L 46 12 L 44 20 Z" fill="#FF7A00" />
              <path d="M54 10 L 52 18 L 44 20 Z" fill="#FFA500" />
              <path d="M30 34 L 36 28 L 34 36 Z" fill="#FFFFFF" />
            </svg>
          </div>

          <!-- Middle: Headline & Supporting Text -->
          <div class="cta-content-group">
            <h3 class="cta-headline">
              Let's Build the Right Solution for <span class="highlight-orange">Your Business</span>
            </h3>
            <p class="cta-supporting-text">
              Whether you need a school system, hospital system, retail solution, fuel station management, or a fully customized platform — we are ready to bring your vision to life.
            </p>
          </div>

          <!-- Right: Action Buttons -->
          <div class="cta-buttons-group">
            <a href="#contact" class="btn-cta-primary" @click.prevent="scrollToContact">
              <span>Get in Touch</span>
              <svg class="w-4 h-4 ml-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" x2="19" y1="12" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </a>

            <a href="#contact" class="btn-cta-secondary" @click.prevent="scrollToContact">
              <svg class="w-4 h-4 mr-1.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="18" height="18" x="3" y="4" rx="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
              </svg>
              <span>Book a Free Consultation</span>
            </a>
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

function scrollToContact() {
  const el = document.getElementById('contact');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}
</script>

<style scoped>
/* MAIN SECTION WRAPPER */
.about-section {
  position: relative;
  background-color: #F5F8FD;
  padding: 80px 0 95px;
  overflow: hidden;
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #071D49;
}

/* BACKGROUND DECORATIVE BLOBS & WAVES */
.about-bg-decorations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.bg-glow-top-left {
  position: absolute;
  top: -80px;
  left: 10%;
  width: 700px;
  height: 450px;
  background: radial-gradient(circle, rgba(234, 241, 255, 0.9) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
}

.bg-glow-center-right {
  position: absolute;
  top: 100px;
  right: -60px;
  width: 550px;
  height: 550px;
  background: radial-gradient(circle, rgba(255, 105, 0, 0.04) 0%, rgba(255, 245, 235, 0) 70%);
  border-radius: 50%;
}

.bg-curved-arc-svg {
  position: absolute;
  top: 40px;
  right: 5%;
  width: 320px;
  height: 180px;
}

.corner-waves-left {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 340px;
  height: 240px;
  z-index: 1;
}

.corner-waves-right {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 340px;
  height: 260px;
  z-index: 1;
}

.corner-wave-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* CONTENT CONTAINER */
.about-container {
  position: relative;
  z-index: 2;
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* 1. HERO GRID (TWO COLUMNS) */
.about-hero-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 3.5rem;
  align-items: center;
  margin-bottom: 3.5rem;
}

/* LEFT HERO COLUMN */
.hero-left-content {
  display: flex;
  flex-direction: column;
}

.about-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: #FFF8F2;
  border: 1px solid #FFE3D1;
  color: #FF6900;
  padding: 0.35rem 0.95rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  margin-bottom: 1.25rem;
  width: fit-content;
  box-shadow: 0 2px 6px rgba(255, 105, 0, 0.06);
}

.badge-building-icon {
  width: 13px;
  height: 13px;
  color: #FF6900;
}

.about-main-title {
  font-size: clamp(2.1rem, 3.2vw, 2.85rem);
  font-weight: 800;
  color: #071D49;
  line-height: 1.18;
  letter-spacing: -0.025em;
  margin: 0 0 1.25rem;
}

.highlight-orange {
  color: #FF6900;
}

.about-company-desc {
  font-size: 1.025rem;
  line-height: 1.68;
  color: #52678A;
  margin: 0 0 2.25rem;
  max-width: 620px;
}

/* VALUE PILLARS (4 ITEMS HORIZONTAL) */
.value-pillars-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.value-pillar-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.pillar-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.value-pillar-item:hover .pillar-icon-box {
  transform: translateY(-2px);
}

.bg-orange-tint {
  background: #FFF2E8;
}

.bg-blue-tint {
  background: #EAF1FF;
}

.text-orange {
  color: #FF6900;
}

.text-blue {
  color: #1246C5;
}

.pillar-svg {
  width: 22px;
  height: 22px;
}

.pillar-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #071D49;
  margin: 0 0 0.25rem;
  letter-spacing: -0.01em;
}

.pillar-subtext {
  font-size: 0.8rem;
  color: #52678A;
  line-height: 1.45;
  margin: 0;
}

/* RIGHT HERO COLUMN: BUILDING & FLOATING CARDS */
.hero-right-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dots-pattern-top-left {
  position: absolute;
  top: -20px;
  left: 20px;
  display: grid;
  grid-template-columns: repeat(4, 6px);
  gap: 8px;
  z-index: 1;
}

.dots-pattern-top-right {
  position: absolute;
  top: 10px;
  right: 15px;
  display: grid;
  grid-template-columns: repeat(5, 6px);
  gap: 8px;
  z-index: 1;
}

.dot-spec {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #C4D7F8;
  opacity: 0.85;
}

.building-image-container {
  position: relative;
  width: 100%;
  max-width: 560px;
  border-radius: 20px;
  overflow: visible;
}

.building-photo {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 20px;
  filter: drop-shadow(0 12px 32px rgba(7, 29, 73, 0.12));
}

/* FLOATING CARD TOP */
.floating-bubble-top {
  position: absolute;
  top: -30px;
  left: -20px;
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 14px;
  padding: 0.75rem 1.15rem;
  box-shadow: 0 10px 24px -4px rgba(7, 29, 73, 0.12);
  z-index: 10;
  transform: rotate(-3deg);
  transition: transform 0.25s ease;
}

.floating-bubble-top:hover {
  transform: rotate(0deg) scale(1.03);
}

.bubble-text {
  font-size: 0.825rem;
  font-weight: 700;
  color: #071D49;
  line-height: 1.35;
  display: block;
}

.bubble-arrow-svg {
  position: absolute;
  bottom: -22px;
  right: -25px;
  width: 42px;
  height: 32px;
}

/* FLOATING CUSTOM SOFTWARE CARD */
.floating-custom-card {
  position: absolute;
  bottom: 40px;
  left: -35px;
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 16px;
  padding: 0.85rem 1.15rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  box-shadow: 0 12px 28px -4px rgba(7, 29, 73, 0.14);
  z-index: 10;
  transform: rotate(2deg);
  transition: transform 0.25s ease;
}

.floating-custom-card:hover {
  transform: rotate(0deg) scale(1.03);
}

.custom-card-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #FFF2E8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.custom-card-title {
  font-size: 0.86rem;
  font-weight: 700;
  color: #071D49;
  line-height: 1.25;
  margin: 0;
}

.custom-card-sub {
  font-size: 0.72rem;
  color: #52678A;
}

/* VERTICAL FLOATING INDUSTRIES STACK */
.floating-industries-stack {
  position: absolute;
  top: 15px;
  right: -25px;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  z-index: 10;
}

.industry-chip-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 12px;
  padding: 0.45rem 0.85rem;
  box-shadow: 0 6px 18px -2px rgba(7, 29, 73, 0.08);
  white-space: nowrap;
  transition: all 0.2s ease;
}

.industry-chip-card:hover {
  transform: translateX(-4px);
  border-color: #FF6900;
  box-shadow: 0 8px 20px -2px rgba(255, 105, 0, 0.16);
}

.chip-icon-box {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chip-svg {
  width: 15px;
  height: 15px;
}

.chip-red { background: #FEECEF; color: #F20D32; }
.chip-blue { background: #EAF1FF; color: #1246C5; }
.chip-green { background: #E8F9F3; color: #08B981; }
.chip-orange { background: #FFF2E8; color: #FF6900; }
.chip-purple { background: #F3EAFD; color: #6554E8; }

.chip-title {
  font-size: 0.825rem;
  font-weight: 600;
  color: #071D49;
}

/* 2. INDUSTRIES WE SERVE PANEL */
.industries-panel {
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 20px;
  padding: 2.25rem;
  box-shadow: 0 10px 30px rgba(7, 29, 73, 0.05);
  margin-bottom: 2.5rem;
}

.panel-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.panel-title-group {
  max-width: 780px;
}

.orange-accent-dash {
  width: 38px;
  height: 3.5px;
  background: linear-gradient(90deg, #FF6900 0%, #FF7A00 100%);
  border-radius: 2px;
  margin-bottom: 0.65rem;
}

.panel-main-heading {
  font-size: 1.55rem;
  font-weight: 800;
  color: #071D49;
  margin: 0 0 0.5rem;
  letter-spacing: -0.015em;
}

.panel-sub-desc {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #52678A;
  margin: 0;
}

.btn-explore-industries {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.65rem 1.25rem;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 700;
  color: #FF6900;
  background: #FFFFFF;
  border: 1.5px solid #FFDEC9;
  text-decoration: none;
  transition: all 0.22s ease;
  white-space: nowrap;
}

.btn-explore-industries:hover {
  background: #FFF8F2;
  border-color: #FF6900;
  transform: translateX(2px);
}

/* 8 INDUSTRY CARDS GRID */
.industry-cards-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.85rem;
}

.industry-card {
  background: #FFFFFF;
  border: 1px solid #DFE8F7;
  border-radius: 14px;
  padding: 1.15rem 0.85rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(7, 29, 73, 0.03);
}

.industry-card:hover {
  transform: translateY(-4px);
  border-color: #FF6900;
  box-shadow: 0 10px 20px -2px rgba(7, 29, 73, 0.08);
}

.card-icon-frame {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.85rem;
  flex-shrink: 0;
}

.card-svg {
  width: 20px;
  height: 20px;
}

.icon-blue { background: #EAF1FF; color: #1246C5; }
.icon-red { background: #FEECEF; color: #F20D32; }
.icon-green { background: #E8F9F3; color: #08B981; }
.icon-orange { background: #FFF2E8; color: #FF6900; }
.icon-purple { background: #F3EAFD; color: #6554E8; }
.icon-pink { background: #FEECEF; color: #E11D48; }

.card-industry-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: #071D49;
  line-height: 1.25;
  margin: 0 0 0.35rem;
}

.card-industry-desc {
  font-size: 0.74rem;
  color: #52678A;
  line-height: 1.45;
  margin: 0;
}

/* 3. COMPANY STATISTICS STRIP */
.company-stats-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.75rem 2rem;
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 20px;
  box-shadow: 0 6px 20px rgba(7, 29, 73, 0.04);
  margin-bottom: 3.25rem;
}

.stat-unit {
  display: flex;
  align-items: center;
  gap: 1.15rem;
  flex: 1;
  padding: 0 1rem;
}

.stat-icon-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #FFF2E8;
  border: 1.5px solid #FFDEC9;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FF6900;
  flex-shrink: 0;
}

.stat-svg {
  width: 22px;
  height: 22px;
}

.stat-meta {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.65rem;
  font-weight: 800;
  color: #071D49;
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.stat-title {
  font-size: 0.925rem;
  font-weight: 700;
  color: #071D49;
  margin: 0.15rem 0 0.1rem;
}

.stat-desc {
  font-size: 0.78rem;
  color: #52678A;
}

.stat-divider {
  width: 1px;
  height: 48px;
  background: #DFE8F7;
  flex-shrink: 0;
}

/* 4. BOTTOM CALL-TO-ACTION BANNER */
.about-cta-banner {
  background: linear-gradient(135deg, #071D49 0%, #061638 100%);
  border: 1px solid rgba(85, 142, 210, 0.45);
  border-radius: 20px;
  padding: 2rem 2.5rem;
  box-shadow: 0 20px 42px -8px rgba(7, 29, 73, 0.35);
  position: relative;
  z-index: 5;
}

.cta-banner-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.cta-target-icon-box {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.target-svg {
  width: 58px;
  height: 58px;
  filter: drop-shadow(0 4px 12px rgba(255, 105, 0, 0.4));
}

.cta-content-group {
  flex-grow: 1;
}

.cta-headline {
  font-size: 1.45rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0 0 0.35rem;
  letter-spacing: -0.015em;
}

.cta-supporting-text {
  font-size: 0.925rem;
  color: #B8C8E0;
  margin: 0;
  line-height: 1.55;
  max-width: 720px;
}

.cta-buttons-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-shrink: 0;
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: linear-gradient(135deg, #FF6900 0%, #FF7A00 100%);
  color: #FFFFFF;
  font-size: 0.925rem;
  font-weight: 700;
  padding: 0.8rem 1.45rem;
  border-radius: 10px;
  text-decoration: none;
  box-shadow: 0 6px 18px rgba(255, 105, 0, 0.36);
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  white-space: nowrap;
}

.btn-cta-primary:hover {
  background: linear-gradient(135deg, #FF7A00 0%, #FF8D1A 100%);
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(255, 105, 0, 0.48);
}

.btn-cta-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(85, 142, 210, 0.45);
  color: #FFFFFF;
  font-size: 0.925rem;
  font-weight: 600;
  padding: 0.8rem 1.35rem;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.22s ease;
  white-space: nowrap;
}

.btn-cta-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #FF6900;
  color: #FFFFFF;
}

/* RESPONSIVE BREAKPOINTS */
@media (max-width: 1400px) {
  .industry-cards-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 1140px) {
  .about-hero-grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  .value-pillars-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero-right-visual {
    margin: 0 auto;
  }
  .cta-banner-inner {
    flex-direction: column;
    text-align: center;
  }
  .cta-target-icon-box {
    margin: 0 auto;
  }
  .cta-buttons-group {
    justify-content: center;
    width: 100%;
  }
  .company-stats-strip {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
  .stat-divider {
    display: none;
  }
}

@media (max-width: 768px) {
  .about-section {
    padding: 60px 0 75px;
  }
  .value-pillars-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .industry-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .company-stats-strip {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .floating-bubble-top {
    left: 0;
  }
  .floating-custom-card {
    left: 0;
  }
  .floating-industries-stack {
    display: none;
  }
  .cta-buttons-group {
    flex-direction: column;
  }
  .btn-cta-primary,
  .btn-cta-secondary {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .industry-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
