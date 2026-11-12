<template>
  <section id="pricing" class="pricing-section">
    <!-- Top & Corner Background Graphic Shapes -->
    <div class="bg-shape-top-left" aria-hidden="true"></div>
    <div class="bg-shape-top-right" aria-hidden="true"></div>

    <div class="pricing-container">
      <!-- Section Header -->
      <div class="section-header">
        <!-- Floating Left Annotation (Desktop) -->
        <div class="annotation-wrapper left-annotation" aria-hidden="true">
          <div class="dot-grid">
            <span v-for="i in 36" :key="'ldot-' + i" class="dot"></span>
          </div>
          <div class="handwritten-note note-left">
            <span>{{ t.pricing.annotationLeft1 || 'Same Powerful' }}</span>
            <span>{{ t.pricing.annotationLeft2 || 'Features' }}</span>
            <span>{{ t.pricing.annotationLeft3 || 'Different School Sizes' }}</span>
          </div>
          <svg class="handwritten-arrow-left" viewBox="0 0 70 80" fill="none">
            <path
              d="M10 10 C 25 40, 45 60, 60 70"
              stroke="#FF6900"
              stroke-width="2.5"
              stroke-linecap="round"
              fill="none"
            />
            <path
              d="M48 68 L62 71 L60 56"
              stroke="#FF6900"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <!-- Floating Right Annotation (Desktop) -->
        <div class="annotation-wrapper right-annotation" aria-hidden="true">
          <div class="dot-grid">
            <span v-for="i in 36" :key="'rdot-' + i" class="dot"></span>
          </div>
          <div class="sunburst-rays">
            <span class="ray ray-1"></span>
            <span class="ray ray-2"></span>
            <span class="ray ray-3"></span>
            <span class="ray ray-4"></span>
          </div>
          <div class="handwritten-note note-right">
            <span>{{ t.pricing.annotationRight1 || 'Flexible Plans' }}</span>
            <span>{{ t.pricing.annotationRight2 || 'for a Brighter' }}</span>
            <span>{{ t.pricing.annotationRight3 || 'Education Future' }}</span>
          </div>
          <svg class="handwritten-arrow-right" viewBox="0 0 60 80" fill="none">
            <path
              d="M10 15 C 35 30, 45 55, 30 75"
              stroke="#FF6900"
              stroke-width="2"
              stroke-dasharray="4 3"
              stroke-linecap="round"
              fill="none"
            />
          </svg>
        </div>

        <!-- Pill Badge -->
        <div class="pricing-badge-pill">
          <svg class="badge-gem-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 2l7.5 7.5L12 22 4.5 9.5 12 2zM4.5 9.5h15M12 2v20"
            />
          </svg>
          <span>{{ t.pricing.badge }}</span>
        </div>

        <!-- Main Heading -->
        <h2 class="section-title">
          {{ t.pricing.titlePart1 || t.pricing.title }}<br />
          <span class="text-orange">{{ t.pricing.titlePart2 || 'Educational Growth' }}</span>
        </h2>

        <!-- Subtitle -->
        <p class="section-subtitle">{{ t.pricing.subtitle }}</p>

        <!-- Interactive Billing Toggle -->
        <div class="billing-toggle-wrap">
          <div class="billing-toggle">
            <button
              type="button"
              class="cycle-btn"
              :class="{ 'active': !isAnnual }"
              @click="isAnnual = false"
              aria-label="Select Monthly Billing"
            >
              {{ t.pricing.monthly }}
            </button>
            <button
              type="button"
              class="cycle-btn"
              :class="{ 'active': isAnnual }"
              @click="isAnnual = true"
              aria-label="Select Annual Billing"
            >
              {{ t.pricing.annual }}
              <span class="discount-pill">{{ t.pricing.discountTag }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Pricing Cards Grid -->
      <div class="pricing-grid">
        <!-- 1. Starter Academy Card -->
        <div class="pricing-card card-starter">
          <!-- Card Header with Illustration -->
          <div class="card-header-flex">
            <div class="illustration-box">
              <img
                src="/pricing-ill-starter.png"
                alt="Starter Academy Illustration"
                class="card-building-img"
                loading="lazy"
              />
            </div>
            <div class="card-titles">
              <h3 class="plan-name">{{ t.pricing.starterName }}</h3>
              <p class="plan-desc">{{ t.pricing.starterDesc }}</p>
            </div>
          </div>

          <!-- Dual Price Blocks ($70 Setup + $25/mo) -->
          <div class="dual-price-row">
            <!-- Setup Fee Block -->
            <div class="price-box setup-box">
              <div class="price-box-header">
                <div class="box-icon-circle icon-orange">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div class="box-price-wrap">
                  <span class="box-currency">$</span>
                  <span class="box-amount">70</span>
                </div>
              </div>
              <div class="box-label">{{ t.pricing.setupFeeLabel || 'One-Time Setup' }}</div>
            </div>

            <!-- Recurring Subscription Block -->
            <div class="price-box recurring-box">
              <div class="price-box-header">
                <div class="box-icon-circle icon-blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                    <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" stroke-linecap="round" />
                    <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" stroke-linecap="round" />
                    <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                  </svg>
                </div>
                <div class="box-price-wrap">
                  <span class="box-currency">$</span>
                  <span class="box-amount">{{ isAnnual ? '20' : '25' }}</span>
                  <span class="box-period">{{ t.pricing.perMonth }}</span>
                </div>
              </div>
              <div class="box-label">
                {{ isAnnual ? (t.pricing.billedAnnually || 'Billed Annually ($240/yr)') : (t.pricing.billedMonthly || 'Billed Monthly') }}
              </div>
            </div>
          </div>

          <!-- Feature Checklist -->
          <ul class="feature-checklist">
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Up to 350 Enrolled Students</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Student &amp; Guardian Bio-Data</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Class &amp; Stream Management</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Daily Attendance Tracking</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Weekly Timetable Generation</span>
            </li>
            <li class="excluded">
              <span class="cross-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Automated Hormuud SMS</span>
            </li>
            <li class="excluded">
              <span class="cross-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Dedicated Student Portal</span>
            </li>
          </ul>

          <!-- CTA Button -->
          <div class="card-cta-wrap">
            <button
              type="button"
              class="btn-plan btn-starter"
              @click="selectPlan('Starter Academy')"
            >
              <span>{{ t.pricing.choosePlan }}</span>
              <svg class="btn-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 2. Professional School Card (FEATURED / MOST POPULAR) -->
        <div class="pricing-card card-pro featured">
          <!-- Overlapping MOST POPULAR Badge -->
          <div class="popular-badge">
            <svg class="popular-crown-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span>{{ t.pricing.proBadge }}</span>
          </div>

          <!-- Card Header with Illustration -->
          <div class="card-header-flex">
            <div class="illustration-box">
              <img
                src="/pricing-ill-pro.png"
                alt="Professional School Illustration"
                class="card-building-img"
                loading="lazy"
              />
            </div>
            <div class="card-titles">
              <h3 class="plan-name">{{ t.pricing.proName }}</h3>
              <p class="plan-desc">{{ t.pricing.proDesc }}</p>
            </div>
          </div>

          <!-- Dual Price Blocks ($70 Setup + $25/mo) -->
          <div class="dual-price-row">
            <!-- Setup Fee Block -->
            <div class="price-box setup-box">
              <div class="price-box-header">
                <div class="box-icon-circle icon-orange">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div class="box-price-wrap">
                  <span class="box-currency">$</span>
                  <span class="box-amount">70</span>
                </div>
              </div>
              <div class="box-label">{{ t.pricing.setupFeeLabel || 'One-Time Setup' }}</div>
            </div>

            <!-- Recurring Subscription Block -->
            <div class="price-box recurring-box pro-recurring">
              <div class="price-box-header">
                <div class="box-icon-circle icon-orange-light">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                    <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" stroke-linecap="round" />
                    <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" stroke-linecap="round" />
                    <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                  </svg>
                </div>
                <div class="box-price-wrap">
                  <span class="box-currency">$</span>
                  <span class="box-amount">{{ isAnnual ? '20' : '25' }}</span>
                  <span class="box-period">{{ t.pricing.perMonth }}</span>
                </div>
              </div>
              <div class="box-label">
                {{ isAnnual ? (t.pricing.billedAnnually || 'Billed Annually ($240/yr)') : (t.pricing.billedMonthly || 'Billed Monthly') }}
              </div>
            </div>
          </div>

          <!-- Feature Checklist -->
          <ul class="feature-checklist">
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Up to 1,500 Enrolled Students</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Examinations, Marks &amp; Transcripts</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Fee Invoicing &amp; Payment Receipts</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Dedicated Teacher &amp; Student Portals</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Hormuud SMS Absent &amp; Result Alerts</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Bulk Academic Year Promotion</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Priority Email &amp; WhatsApp Support</span>
            </li>
          </ul>

          <!-- CTA Button -->
          <div class="card-cta-wrap">
            <button
              type="button"
              class="btn-plan btn-pro"
              @click="selectPlan('Professional School')"
            >
              <span>{{ t.pricing.choosePlan }}</span>
              <svg class="btn-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 3. Enterprise Institution Card -->
        <div class="pricing-card card-enterprise">
          <!-- Card Header with Illustration -->
          <div class="card-header-flex">
            <div class="illustration-box">
              <img
                src="/pricing-ill-enterprise.png"
                alt="Enterprise Institution Illustration"
                class="card-building-img"
                loading="lazy"
              />
            </div>
            <div class="card-titles">
              <h3 class="plan-name">{{ t.pricing.enterpriseName }}</h3>
              <p class="plan-desc">{{ t.pricing.enterpriseDesc }}</p>
            </div>
          </div>

          <!-- Enterprise Pricing Display: Custom per Acceptance Criteria -->
          <div class="enterprise-custom-row">
            <div class="enterprise-custom-box">
              <div class="enterprise-box-content">
                <div class="enterprise-icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                    />
                  </svg>
                </div>
                <div class="enterprise-texts">
                  <div class="custom-pricing-value">{{ t.pricing.customPrice || 'Custom' }}</div>
                  <div class="custom-pricing-note">{{ t.pricing.customDesc || 'Tailored for large school networks' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Feature Checklist -->
          <ul class="feature-checklist">
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Unlimited Enrolled Students</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Multi-Branch Campus Architecture</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>On-Premise or Dedicated Cloud Deployment</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Custom Hormuud Sender ID &amp; Shortcode</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Custom Grading Curricula &amp; Transcripts</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>Dedicated Technical Account Manager</span>
            </li>
            <li class="included">
              <span class="check-icon-wrap">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span>99.99% Uptime Guarantee (SLA)</span>
            </li>
          </ul>

          <!-- CTA Button -->
          <div class="card-cta-wrap">
            <button
              type="button"
              class="btn-plan btn-enterprise"
              @click="selectPlan('Enterprise Institution')"
            >
              <span>{{ t.pricing.contactSales }}</span>
              <svg class="btn-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Bottom Trust & Benefits Strip -->
      <div class="trust-benefits-strip">
        <!-- Item 1 -->
        <div class="trust-item">
          <div class="trust-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <div class="trust-text">
            <h4 class="trust-title">{{ t.pricing.trust1Title || 'No Hidden Costs' }}</h4>
            <p class="trust-sub">{{ t.pricing.trust1Sub || 'Transparent pricing always' }}</p>
          </div>
        </div>

        <div class="trust-divider" aria-hidden="true"></div>

        <!-- Item 2 -->
        <div class="trust-item">
          <div class="trust-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
          </div>
          <div class="trust-text">
            <h4 class="trust-title">{{ t.pricing.trust2Title || 'Priority Support' }}</h4>
            <p class="trust-sub">{{ t.pricing.trust2Sub || 'We are here to help' }}</p>
          </div>
        </div>

        <div class="trust-divider" aria-hidden="true"></div>

        <!-- Item 3 -->
        <div class="trust-item">
          <div class="trust-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="2" y="3" width="14" height="14" rx="2" stroke-width="2" />
              <rect x="10" y="7" width="12" height="14" rx="2" stroke-width="2" fill="#FFFFFF" />
              <line x1="16" y1="18" x2="16" y2="18.01" stroke-width="2.5" stroke-linecap="round" />
            </svg>
          </div>
          <div class="trust-text">
            <h4 class="trust-title">{{ t.pricing.trust3Title || 'Access Anywhere' }}</h4>
            <p class="trust-sub">{{ t.pricing.trust3Sub || 'Multi-device platform' }}</p>
          </div>
        </div>

        <div class="trust-divider" aria-hidden="true"></div>

        <!-- Item 4 -->
        <div class="trust-item">
          <div class="trust-icon-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </div>
          <div class="trust-text">
            <h4 class="trust-title">{{ t.pricing.trust4Title || 'Trusted by Schools' }}</h4>
            <p class="trust-sub">{{ t.pricing.trust4Sub || 'Across Somalia and beyond' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Decorative Bottom Corner Abstract Waves -->
    <div class="bottom-waves-container" aria-hidden="true">
      <!-- Left Bottom Waves -->
      <svg class="corner-wave wave-left" viewBox="0 0 350 200" preserveAspectRatio="none">
        <!-- Deep Navy Layer -->
        <path
          d="M0 200 L0 100 C 60 70, 150 140, 220 180 C 260 200, 300 200, 350 200 Z"
          fill="#071D49"
        />
        <!-- Brand Orange Layer -->
        <path
          d="M0 200 L0 145 C 80 120, 130 180, 200 195 L0 200 Z"
          fill="#FF6900"
          opacity="0.95"
        />
      </svg>

      <!-- Right Bottom Waves -->
      <svg class="corner-wave wave-right" viewBox="0 0 380 220" preserveAspectRatio="none">
        <!-- Deep Navy Layer -->
        <path
          d="M380 220 L380 90 C 310 70, 220 140, 150 180 C 100 210, 50 220, 0 220 Z"
          fill="#071D49"
        />
        <!-- Brand Orange Layer -->
        <path
          d="M380 220 L380 145 C 290 120, 230 180, 160 205 L380 220 Z"
          fill="#FF6900"
          opacity="0.95"
        />
      </svg>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

const emit = defineEmits<{
  (e: 'select-plan', planName: string): void;
}>();

// Default: Monthly Billing active as shown in the reference screenshot
const isAnnual = ref(false);

function selectPlan(planName: string) {
  emit('select-plan', planName);
}
</script>

<style scoped>
/* ==========================================================================
   SOMROYAL EMS PREMIUM PRICING SECTION STYLES
   Colors:
     Deep Navy: #071D49
     Dark Navy: #061638
     Brand Orange: #FF6900
     Orange Hover: #FF7A00
     Light Background: #F5F8FD
     Border: #DCE7F7
   ========================================================================== */

.pricing-section {
  position: relative;
  padding: 75px 0 110px;
  background: linear-gradient(180deg, #FFFFFF 0%, #F5F8FD 35%, #EDF4FE 100%);
  overflow: hidden;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Subtle background glows */
.bg-shape-top-left {
  position: absolute;
  top: -100px;
  left: -80px;
  width: 420px;
  max-width: 100vw;
  height: 420px;
  background: radial-gradient(circle, rgba(18, 70, 197, 0.07) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.bg-shape-top-right {
  position: absolute;
  top: -80px;
  right: -60px;
  width: 450px;
  max-width: 100vw;
  height: 450px;
  background: radial-gradient(circle, rgba(255, 105, 0, 0.05) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.pricing-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1.5rem;
  position: relative;
  z-index: 5;
}

/* ==========================================================================
   SECTION HEADER & ANNOTATIONS
   ========================================================================== */

.section-header {
  position: relative;
  text-align: center;
  max-width: 840px;
  margin: 0 auto 3rem;
}

/* Badge Pill */
.pricing-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.775rem;
  font-weight: 700;
  color: #FF6900;
  background: #FFF8F2;
  border: 1px solid #FFE4D3;
  padding: 0.35rem 1rem;
  border-radius: 50px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 1.15rem;
  box-shadow: 0 2px 6px rgba(255, 105, 0, 0.08);
}

.badge-gem-icon {
  width: 14px;
  height: 14px;
  stroke-width: 2.2;
}

/* Main Heading */
.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.65rem;
  font-weight: 800;
  color: #071D49;
  line-height: 1.22;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.text-orange {
  color: #FF6900;
}

/* Subtitle */
.section-subtitle {
  font-size: 1.05rem;
  color: #53698C;
  line-height: 1.6;
  max-width: 720px;
  margin: 0 auto;
}

/* ==========================================================================
   HANDWRITTEN ANNOTATIONS (LEFT & RIGHT)
   ========================================================================== */

.annotation-wrapper {
  position: absolute;
  pointer-events: none;
  z-index: 3;
}

.left-annotation {
  top: 10px;
  left: -190px;
  width: 220px;
  text-align: left;
}

.right-annotation {
  top: 15px;
  right: -190px;
  width: 220px;
  text-align: left;
}

/* Dot Grids */
.dot-grid {
  display: grid;
  grid-template-columns: repeat(6, 6px);
  gap: 9px;
  margin-bottom: 0.5rem;
  opacity: 0.45;
}

.dot {
  width: 4px;
  height: 4px;
  background-color: #8BA8D6;
  border-radius: 50%;
}

/* Handwritten Notes */
.handwritten-note {
  font-family: 'Caveat', cursive, sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: #D95305;
  line-height: 1.15;
  display: flex;
  flex-direction: column;
}

.note-left {
  transform: rotate(-5deg);
  margin-left: 10px;
}

.note-right {
  transform: rotate(3deg);
  margin-left: 8px;
}

.handwritten-arrow-left {
  width: 65px;
  height: 75px;
  margin-left: 55px;
  margin-top: -8px;
}

.handwritten-arrow-right {
  width: 60px;
  height: 75px;
  margin-left: 35px;
  margin-top: 2px;
}

/* Sunburst rays */
.sunburst-rays {
  position: absolute;
  top: 2px;
  right: 18px;
  width: 24px;
  height: 24px;
}

.ray {
  position: absolute;
  background: #FF6900;
  border-radius: 2px;
}

.ray-1 {
  width: 8px;
  height: 2px;
  top: 0;
  left: 6px;
  transform: rotate(-30deg);
}

.ray-2 {
  width: 9px;
  height: 2px;
  top: 8px;
  right: 0;
  transform: rotate(20deg);
}

.ray-3 {
  width: 7px;
  height: 2px;
  bottom: 2px;
  right: 4px;
  transform: rotate(50deg);
}

.ray-4 {
  width: 8px;
  height: 2px;
  top: 3px;
  right: 6px;
  transform: rotate(-10deg);
}

/* ==========================================================================
   BILLING TOGGLE
   ========================================================================== */

.billing-toggle-wrap {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.billing-toggle {
  background: #EAF0FA;
  border: 1px solid #D5E2F3;
  border-radius: 50px;
  padding: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(7, 29, 73, 0.05);
}

.cycle-btn {
  font-size: 0.88rem;
  font-weight: 600;
  color: #53698C;
  padding: 0.55rem 1.35rem;
  border-radius: 40px;
  cursor: pointer;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
  background: transparent;
  outline: none;
}

.cycle-btn:hover {
  color: #071D49;
}

.cycle-btn.active {
  background: #071D49;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(7, 29, 73, 0.25);
}

.discount-pill {
  font-size: 0.7rem;
  font-weight: 700;
  background: #FF6900;
  color: #FFFFFF;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
  letter-spacing: 0.02em;
}

/* ==========================================================================
   PRICING CARDS GRID
   ========================================================================== */

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.65rem;
  align-items: stretch;
  margin-bottom: 3.5rem;
}

.pricing-card {
  background: #FFFFFF;
  border: 1.5px solid #DCE7F7;
  border-radius: 22px;
  padding: 2.25rem 1.85rem 2rem;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  box-shadow: 0 8px 24px rgba(18, 70, 197, 0.04);
}

.pricing-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 36px rgba(18, 70, 197, 0.09);
}

/* Professional School Card (Featured / Most Popular) */
.pricing-card.featured {
  border: 2px solid #FF7A00;
  box-shadow: 0 14px 38px rgba(255, 105, 0, 0.12), 0 2px 10px rgba(7, 29, 73, 0.04);
}

.pricing-card.featured:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 46px rgba(255, 105, 0, 0.18);
}

/* Overlapping MOST POPULAR Badge */
.popular-badge {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  background: #FF6900;
  color: #FFFFFF;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  padding: 0.35rem 1.15rem;
  border-radius: 30px;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  box-shadow: 0 4px 14px rgba(255, 105, 0, 0.38);
  white-space: nowrap;
}

.popular-crown-icon {
  width: 14px;
  height: 14px;
}

/* Card Header with Building Illustration */
.card-header-flex {
  display: flex;
  align-items: flex-start;
  gap: 1.15rem;
  margin-bottom: 1.4rem;
}

.illustration-box {
  flex-shrink: 0;
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-building-img {
  width: 100%;
  height: auto;
  max-height: 68px;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(7, 29, 73, 0.08));
}

.card-titles {
  flex: 1;
}

.plan-name {
  font-family: 'Outfit', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: #071D49;
  line-height: 1.25;
  margin-bottom: 0.35rem;
}

.plan-desc {
  font-size: 0.85rem;
  color: #53698C;
  line-height: 1.45;
  margin: 0;
}

/* ==========================================================================
   DUAL PRICING ROW ($70 Setup + $25/mo)
   ========================================================================== */

.dual-price-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
  margin-bottom: 1.65rem;
}

.price-box {
  background: #F7FAFE;
  border: 1px solid #E1EDFA;
  border-radius: 14px;
  padding: 0.85rem 0.75rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.pricing-card.featured .price-box {
  background: #FFFBF8;
  border-color: #FEE7D8;
}

.price-box-header {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-bottom: 0.25rem;
}

.box-icon-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.box-icon-circle svg {
  width: 16px;
  height: 16px;
}

.icon-orange {
  background: #FFF1E6;
  color: #FF6900;
}

.icon-blue {
  background: #EAF2FF;
  color: #1246C5;
}

.icon-orange-light {
  background: #FFF3EB;
  color: #FF7A00;
}

.box-price-wrap {
  display: flex;
  align-items: baseline;
  gap: 1px;
}

.box-currency {
  font-family: 'Outfit', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #071D49;
}

.box-amount {
  font-family: 'Outfit', sans-serif;
  font-size: 1.6rem;
  font-weight: 800;
  color: #071D49;
  line-height: 1;
}

.box-period {
  font-size: 0.72rem;
  color: #64748B;
  font-weight: 500;
  margin-left: 2px;
}

.box-label {
  font-size: 0.74rem;
  color: #53698C;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Enterprise Custom Box Row */
.enterprise-custom-row {
  margin-bottom: 1.65rem;
}

.enterprise-custom-box {
  background: #F7FAFE;
  border: 1px solid #E1EDFA;
  border-radius: 14px;
  padding: 0.95rem 1rem;
  min-height: 78px;
  display: flex;
  align-items: center;
}

.enterprise-box-content {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
}

.enterprise-icon-circle {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #EAF2FF;
  color: #1246C5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.enterprise-icon-circle svg {
  width: 20px;
  height: 20px;
}

.enterprise-texts {
  flex: 1;
}

.custom-pricing-value {
  font-family: 'Outfit', sans-serif;
  font-size: 1.55rem;
  font-weight: 800;
  color: #071D49;
  line-height: 1.1;
}

.custom-pricing-note {
  font-size: 0.75rem;
  color: #53698C;
  font-weight: 500;
  margin-top: 2px;
}

/* ==========================================================================
   FEATURE CHECKLIST
   ========================================================================== */

.feature-checklist {
  list-style: none;
  padding: 0;
  margin: 0 0 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  flex: 1;
}

.feature-checklist li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
  color: #071D49;
  font-weight: 500;
  line-height: 1.35;
}

.check-icon-wrap {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FF6900;
  flex-shrink: 0;
}

.check-icon-wrap svg {
  width: 18px;
  height: 18px;
}

/* Excluded features */
.feature-checklist li.excluded {
  color: #94A3B8;
}

.cross-icon-wrap {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #A0B2C9;
  flex-shrink: 0;
}

.cross-icon-wrap svg {
  width: 16px;
  height: 16px;
}

/* ==========================================================================
   CTA BUTTONS
   ========================================================================== */

.card-cta-wrap {
  margin-top: auto;
}

.btn-plan {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding: 0.85rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.25s ease;
  outline: none;
  text-decoration: none;
}

.btn-arrow {
  width: 16px;
  height: 16px;
  transition: transform 0.25s ease;
}

.btn-plan:hover .btn-arrow {
  transform: translateX(4px);
}

/* Starter & Enterprise Buttons */
.btn-starter,
.btn-enterprise {
  background: #FFFFFF;
  color: #071D49;
  border: 1.5px solid #DCE7F7;
  box-shadow: 0 2px 6px rgba(7, 29, 73, 0.04);
}

.btn-starter:hover,
.btn-enterprise:hover {
  background: #F8FAFD;
  border-color: #FF6900;
  color: #FF6900;
}

/* Professional School Button (Solid Orange) */
.btn-pro {
  background: linear-gradient(135deg, #FF6900 0%, #FF7A00 100%);
  color: #FFFFFF;
  border: 1.5px solid #FF6900;
  box-shadow: 0 6px 18px rgba(255, 105, 0, 0.35);
}

.btn-pro:hover {
  background: linear-gradient(135deg, #FF7A00 0%, #FF8A00 100%);
  box-shadow: 0 8px 24px rgba(255, 105, 0, 0.45);
  transform: translateY(-1px);
}

/* ==========================================================================
   BOTTOM TRUST & BENEFITS STRIP
   ========================================================================== */

.trust-benefits-strip {
  background: #FFFFFF;
  border: 1px solid #DCE7F7;
  border-radius: 20px;
  padding: 1.35rem 2rem;
  box-shadow: 0 10px 32px rgba(7, 29, 73, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  position: relative;
  z-index: 5;
}

.trust-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.trust-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #FFF1E6;
  color: #FF6900;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.trust-icon-box svg {
  width: 22px;
  height: 22px;
}

.trust-text {
  display: flex;
  flex-direction: column;
}

.trust-title {
  font-family: 'Outfit', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #071D49;
  margin: 0;
  line-height: 1.3;
}

.trust-sub {
  font-size: 0.78rem;
  color: #64748B;
  margin: 2px 0 0 0;
}

.trust-divider {
  width: 1px;
  height: 38px;
  background-color: #E2ECF8;
  margin: 0 1.25rem;
  flex-shrink: 0;
}

/* ==========================================================================
   DECORATIVE BOTTOM CORNER WAVES
   ========================================================================== */

.bottom-waves-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 200px;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.corner-wave {
  position: absolute;
  bottom: 0;
  height: 180px;
}

.wave-left {
  left: 0;
  width: 320px;
}

.wave-right {
  right: 0;
  width: 340px;
}

/* ==========================================================================
   RESPONSIVE DESIGN (Desktop, Tablet, Mobile)
   ========================================================================== */

@media (max-width: 1280px) {
  .left-annotation,
  .right-annotation {
    display: none;
  }
}

@media (max-width: 1024px) {
  .pricing-section {
    padding: 60px 0 90px;
  }

  .pricing-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .card-enterprise {
    grid-column: span 2;
    max-width: 600px;
    margin: 0 auto;
    width: 100%;
  }

  .trust-benefits-strip {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .trust-divider {
    display: none;
  }
}

@media (max-width: 768px) {
  .pricing-section {
    padding: 55px 0 75px;
  }

  .pricing-container {
    padding: 0 clamp(0.85rem, 3vw, 1.5rem);
  }

  .section-title {
    font-size: clamp(1.85rem, 5vw, 2.35rem);
  }

  .pricing-grid {
    grid-template-columns: 1fr;
    gap: 1.75rem;
  }

  .card-enterprise {
    grid-column: span 1;
    max-width: 100%;
  }

  .trust-benefits-strip {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  .btn-plan {
    min-height: 48px;
    width: 100%;
    justify-content: center;
  }

  .wave-left,
  .wave-right {
    opacity: 0.35;
    max-width: 40vw;
  }
}

@media (max-width: 480px) {
  .section-badge {
    font-size: 0.72rem;
    padding: 0.35rem 0.85rem;
  }

  .section-title {
    font-size: clamp(1.65rem, 5.5vw, 2.05rem);
  }

  .pricing-card {
    padding: 1.5rem 1.15rem 1.35rem;
    border-radius: 16px;
  }

  .tier-name {
    font-size: 1.25rem;
  }

  .dual-price-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .billing-toggle {
    width: 100%;
    justify-content: center;
  }

  .currency-switch-box {
    margin-top: 0.5rem;
  }

  .cycle-btn {
    padding: 0.5rem 0.85rem;
    font-size: 0.82rem;
    min-height: 42px;
  }
}
</style>
