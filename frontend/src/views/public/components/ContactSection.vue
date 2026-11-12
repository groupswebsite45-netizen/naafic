<template>
  <section id="contact" class="contact-section">
    <!-- Top & Corner Background Graphic Shapes -->
    <div class="bg-shape-top-left" aria-hidden="true"></div>
    <div class="bg-shape-top-right" aria-hidden="true"></div>

    <div class="contact-container">
      <!-- Section Header -->
      <div class="section-header">
        <!-- Floating Left Annotation (Desktop) -->
        <div class="annotation-wrapper left-annotation" aria-hidden="true">
          <div class="dot-grid">
            <span v-for="i in 36" :key="'cldot-' + i" class="dot"></span>
          </div>
          <div class="handwritten-note note-left">
            <span>{{ t.contact.leftAnnotation1 || "Let's Build" }}</span>
            <span>{{ t.contact.leftAnnotation2 || "a Smarter Learning" }}</span>
            <span>{{ t.contact.leftAnnotation3 || "Future Together" }}</span>
          </div>
          <svg class="handwritten-arrow-left" viewBox="0 0 70 80" fill="none">
            <path
              d="M10 10 C 25 40, 45 60, 60 70"
              stroke="#FF6500"
              stroke-width="2.5"
              stroke-linecap="round"
              fill="none"
            />
            <path
              d="M48 68 L62 71 L60 56"
              stroke="#FF6500"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <!-- Floating Right Annotation (Desktop) -->
        <div class="annotation-wrapper right-annotation" aria-hidden="true">
          <div class="dot-grid">
            <span v-for="i in 36" :key="'crdot-' + i" class="dot"></span>
          </div>
          <div class="handwritten-note note-right">
            <span>{{ t.contact.rightAnnotation1 || "Your Education" }}</span>
            <span>{{ t.contact.rightAnnotation2 || "Technology Partner" }}</span>
            <span>{{ t.contact.rightAnnotation3 || "in Somalia and Beyond" }}</span>
          </div>
          <svg class="handwritten-arrow-right" viewBox="0 0 60 80" fill="none">
            <path
              d="M10 15 C 35 30, 45 55, 30 75"
              stroke="#FF6500"
              stroke-width="2.5"
              stroke-linecap="round"
              fill="none"
            />
            <path
              d="M38 62 L30 75 L20 66"
              stroke="#FF6500"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <!-- Pill Badge -->
        <div class="contact-badge-pill">
          <svg class="badge-plane-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
          <span>{{ t.contact.badge }}</span>
        </div>

        <!-- Main Heading with Sunburst Rays -->
        <h2 class="section-title">
          Connect with the <span class="text-orange">Somroyal EMS</span> Solutions Team
          <span class="heading-sunburst" aria-hidden="true">
            <span class="ray ray-1"></span>
            <span class="ray ray-2"></span>
            <span class="ray ray-3"></span>
          </span>
        </h2>

        <!-- Subtitle -->
        <p class="section-subtitle">{{ t.contact.subtitle }}</p>
      </div>

      <!-- Main Contact Grid (Two Columns on Desktop) -->
      <div class="contact-grid">
        <!-- LEFT COLUMN: Contact Details & Somroyal HQ Building -->
        <div class="contact-info-card">
          <div class="panel-header-wrap">
            <h3 class="panel-heading">{{ t.contact.leftTitle || 'Institutional Support & Inquiry' }}</h3>
            <p class="panel-desc">
              {{ t.contact.leftDesc || 'Our education platform consultants are available to provide technical demonstrations, custom licensing proposals, and campus onboarding consultations.' }}
            </p>
          </div>

          <!-- Content split: Info items list on left, HQ Building on right -->
          <div class="info-building-layout">
            <!-- 4 Contact Details List -->
            <div class="info-items-column">
              <!-- Item 1: Campus Headquarters -->
              <div class="info-row">
                <div class="info-icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div class="info-text-group">
                  <span class="info-label">{{ t.contact.locationTitle }}</span>
                  <span class="info-val font-semibold">{{ t.contact.locationValue || 'Abudwak, Galgaduud, Somalia' }}</span>
                </div>
              </div>

              <!-- Item 2: Direct Email -->
              <div class="info-row">
                <div class="info-icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div class="info-text-group">
                  <span class="info-label">{{ t.contact.emailTitle }}</span>
                  <a href="mailto:somroyaltech@gmail.com" class="info-val info-link-orange">
                    somroyaltech@gmail.com
                  </a>
                </div>
              </div>

              <!-- Item 3: Support Line -->
              <div class="info-row">
                <div class="info-icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    />
                  </svg>
                </div>
                <div class="info-text-group">
                  <span class="info-label">{{ t.contact.phoneTitle }}</span>
                  <a href="tel:+252612508505" class="info-val font-semibold info-tel">
                    +252 61 250 8505
                  </a>
                </div>
              </div>

              <!-- Item 4: Operating Hours -->
              <div class="info-row">
                <div class="info-icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div class="info-text-group">
                  <span class="info-label">{{ t.contact.hoursTitle }}</span>
                  <span class="info-val font-medium">Sat - Thu: 7:30 AM - 4:30 PM (EAT)</span>
                </div>
              </div>
            </div>

            <!-- Somroyal HQ Building Visual with Floating Card -->
            <div class="building-wrapper">
              <div class="building-image-container">
                <img
                  src="/contact-building.png"
                  alt="Somroyal Technology Solutions Headquarters"
                  class="hq-building-img"
                  loading="lazy"
                />
              </div>

              <!-- Floating Support Card (Tilted with micro-interaction) -->
              <div class="floating-support-card">
                <div class="floating-icon-box">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
                    />
                  </svg>
                </div>
                <div class="floating-texts">
                  <h5 class="floating-title">{{ t.contact.buildingCardTitle || 'Dedicated Support for Your School' }}</h5>
                  <p class="floating-sub">{{ t.contact.buildingCardSub || 'Our team is ready to help' }}</p>
                </div>
                <button type="button" class="floating-arrow-btn" aria-label="Contact support">
                  <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Direct Inquiries Notice Strip -->
          <div class="direct-inquiry-box">
            <div class="direct-check-icon">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="direct-inquiry-text">
              <strong>{{ t.contact.directInquiryLabel || 'Direct Inquiries:' }}</strong>
              {{ t.contact.directInquiryNotice || 'Inquiries are responded to via official institutional channels within one business day.' }}
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: Inquiry Submission Form -->
        <div class="contact-form-card">
          <!-- Card Header with Orange Chat Icon -->
          <div class="form-header-wrap">
            <div class="form-header-icon-box">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <div>
              <h3 class="form-card-title">{{ t.contact.rightHeading || 'Send Us an Inquiry' }}</h3>
              <p class="form-card-sub">{{ t.contact.rightSub || 'Fill out the form below and our team will get back to you shortly.' }}</p>
            </div>
          </div>

          <!-- Success Alert State -->
          <transition name="fade">
            <div v-if="isSubmitted" class="success-banner" role="alert">
              <div class="success-icon">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="success-content">
                <h4 class="success-title">Inquiry Dispatched Successfully</h4>
                <p class="success-desc">{{ t.contact.successMessage }}</p>
                <button type="button" class="btn-reset-form" @click="resetForm">
                  Send Another Inquiry
                </button>
              </div>
            </div>
          </transition>

          <!-- Form Fields Grid -->
          <form v-if="!isSubmitted" class="inquiry-form" @submit.prevent="submitInquiry" novalidate>
            <!-- Row 1: Full Name & School Name -->
            <div class="form-row-2">
              <div class="form-group" :class="{ 'has-error': errors.fullName }">
                <label class="form-label">
                  {{ t.contact.nameLabel }} <span class="required">*</span>
                </label>
                <div class="input-with-icon">
                  <svg class="field-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                  </svg>
                  <input
                    v-model.trim="form.fullName"
                    type="text"
                    placeholder="e.g. Dr. Abdullahi Warsame"
                    class="form-input"
                    required
                  />
                </div>
                <span v-if="errors.fullName" class="error-msg">{{ errors.fullName }}</span>
              </div>

              <div class="form-group" :class="{ 'has-error': errors.schoolName }">
                <label class="form-label">
                  {{ t.contact.schoolLabel }} <span class="required">*</span>
                </label>
                <div class="input-with-icon">
                  <svg class="field-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4zm3 1h2v2H7V5zm4 0h2v2h-2V5zm-4 4h2v2H7V9zm4 0h2v2h-2V9zm-4 4h2v2H7v-2zm4 0h2v2h-2v-2z" clip-rule="evenodd" />
                  </svg>
                  <input
                    v-model.trim="form.schoolName"
                    type="text"
                    placeholder="e.g. Mogadishu Elite Academy"
                    class="form-input"
                    required
                  />
                </div>
                <span v-if="errors.schoolName" class="error-msg">{{ errors.schoolName }}</span>
              </div>
            </div>

            <!-- Row 2: Email & Phone -->
            <div class="form-row-2">
              <div class="form-group" :class="{ 'has-error': errors.email }">
                <label class="form-label">
                  {{ t.contact.emailLabel }} <span class="required">*</span>
                </label>
                <div class="input-with-icon">
                  <svg class="field-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                    <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                  </svg>
                  <input
                    v-model.trim="form.email"
                    type="email"
                    placeholder="name@school.edu.so"
                    class="form-input"
                    required
                  />
                </div>
                <span v-if="errors.email" class="error-msg">{{ errors.email }}</span>
              </div>

              <div class="form-group" :class="{ 'has-error': errors.phone }">
                <label class="form-label">
                  {{ t.contact.phoneLabel }} <span class="required">*</span>
                </label>
                <div class="input-with-icon">
                  <svg class="field-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                  </svg>
                  <input
                    v-model.trim="form.phone"
                    type="tel"
                    placeholder="+252 61 250 8505"
                    class="form-input"
                    required
                  />
                </div>
                <span v-if="errors.phone" class="error-msg">{{ errors.phone }}</span>
              </div>
            </div>

            <!-- Row 3: Interested Plan or Tier -->
            <div class="form-group">
              <label class="form-label">{{ t.contact.planLabel }}</label>
              <div class="select-with-icon">
                <svg class="field-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                </svg>
                <select v-model="form.plan" class="form-select">
                  <optgroup :label="t.contact.optgroupSchool || '🏫 Dugsiyada (Schools)'">
                    <option value="School - Professional School">Dugsi / School — Professional (Full Suite & SMS)</option>
                    <option value="School - Starter Academy">Dugsi / School — Starter Academy (Core Operations)</option>
                    <option value="School - Enterprise Institution">Dugsi / School — Enterprise (Multi-Campus & SLA)</option>
                  </optgroup>
                  <optgroup :label="t.contact.optgroupMachad || '🏛️ Machadyada (Institutes & Academies)'">
                    <option value="Machad - Professional Institute">Machad / Institute — Professional Management & SMS</option>
                    <option value="Machad - Diploma & Short Courses">Machad / Institute — Koorsooyin Gaar ah & Tababarro</option>
                    <option value="Machad - Enterprise Network">Machad / Institute — Kulliyado & Xarumo Badan</option>
                  </optgroup>
                  <optgroup :label="t.contact.optgroupGeneral || '💬 Xog-doon Guud (General)'">
                    <option value="School - General Inquiry">Dugsi / School — Xog-doon Guud & Demo</option>
                    <option value="Machad - General Inquiry">Machad / Institute — Xog-doon Guud & Demo</option>
                  </optgroup>
                </select>
                <svg class="select-chevron" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>

            <!-- Row 4: Requirements / Message -->
            <div class="form-group" :class="{ 'has-error': errors.message }">
              <label class="form-label">
                {{ t.contact.messageLabel }} <span class="required">*</span>
              </label>
              <div class="textarea-with-icon">
                <svg class="textarea-field-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd" />
                </svg>
                <textarea
                  v-model.trim="form.message"
                  rows="3"
                  placeholder="Briefly describe your student capacity, campus requirements, or desired timeline..."
                  class="form-textarea"
                  required
                ></textarea>
              </div>
              <span v-if="errors.message" class="error-msg">{{ errors.message }}</span>
            </div>

            <!-- Submit Button (Orange Gradient with Plane & Arrow) -->
            <button
              type="submit"
              class="btn-send-inquiry"
              :disabled="isSubmitting"
            >
              <svg v-if="isSubmitting" class="spinner-icon animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="btn-lead-plane" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
              <span>{{ isSubmitting ? t.contact.submitting : t.contact.submitBtn }}</span>
              <svg class="btn-trail-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </form>
        </div>
      </div>

      <!-- Bottom Feature / Trust Strip (4 items) -->
      <div class="bottom-trust-strip">
        <!-- Feature 1: Expert Guidance -->
        <div class="trust-cell">
          <div class="trust-icon-container">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <div class="trust-cell-text">
            <h4 class="trust-heading">{{ t.contact.trust1Title || 'Expert Guidance' }}</h4>
            <p class="trust-desc">{{ t.contact.trust1Sub || 'Free consultation with our specialists' }}</p>
          </div>
        </div>

        <div class="trust-separator" aria-hidden="true"></div>

        <!-- Feature 2: Custom Solutions -->
        <div class="trust-cell">
          <div class="trust-icon-container">
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
          <div class="trust-cell-text">
            <h4 class="trust-heading">{{ t.contact.trust2Title || 'Custom Solutions' }}</h4>
            <p class="trust-desc">{{ t.contact.trust2Sub || 'Tailored to your school requirements' }}</p>
          </div>
        </div>

        <div class="trust-separator" aria-hidden="true"></div>

        <!-- Feature 3: Fast Response -->
        <div class="trust-cell">
          <div class="trust-icon-container">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
          </div>
          <div class="trust-cell-text">
            <h4 class="trust-heading">{{ t.contact.trust3Title || 'Fast Response' }}</h4>
            <p class="trust-desc">{{ t.contact.trust3Sub || 'We typically reply within one business day' }}</p>
          </div>
        </div>

        <div class="trust-separator" aria-hidden="true"></div>

        <!-- Feature 4: Trusted Partner -->
        <div class="trust-cell">
          <div class="trust-icon-container">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </div>
          <div class="trust-cell-text">
            <h4 class="trust-heading">{{ t.contact.trust4Title || 'Trusted Partner' }}</h4>
            <p class="trust-desc">{{ t.contact.trust4Sub || 'Supporting schools across Somalia and beyond' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Decorative Bottom Corner Abstract Waves -->
    <div class="bottom-waves-container" aria-hidden="true">
      <!-- Left Bottom Waves -->
      <svg class="corner-wave wave-left" viewBox="0 0 350 200" preserveAspectRatio="none">
        <path
          d="M0 200 L0 100 C 60 70, 150 140, 220 180 C 260 200, 300 200, 350 200 Z"
          fill="#031A3A"
        />
        <path
          d="M0 200 L0 145 C 80 120, 130 180, 200 195 L0 200 Z"
          fill="#FF6500"
          opacity="0.95"
        />
      </svg>

      <!-- Right Bottom Waves -->
      <svg class="corner-wave wave-right" viewBox="0 0 380 220" preserveAspectRatio="none">
        <path
          d="M380 220 L380 90 C 310 70, 220 140, 150 180 C 100 210, 50 220, 0 220 Z"
          fill="#031A3A"
        />
        <path
          d="M380 220 L380 145 C 290 120, 230 180, 160 205 L380 220 Z"
          fill="#FF6500"
          opacity="0.95"
        />
      </svg>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { TranslationContent } from '../translations';
import { inquiryService } from '../../../services/inquiryService';

const props = defineProps<{
  t: TranslationContent;
  selectedPlan?: string;
}>();

const isSubmitting = ref(false);
const isSubmitted = ref(false);

const form = reactive({
  fullName: '',
  schoolName: '',
  email: '',
  phone: '',
  plan: 'School - Professional School',
  message: '',
});

const errors = reactive({
  fullName: '',
  schoolName: '',
  email: '',
  phone: '',
  message: '',
});

watch(() => props.selectedPlan, (newPlan) => {
  if (newPlan) {
    if (newPlan === 'Starter Academy' || newPlan.includes('Starter')) {
      form.plan = 'School - Starter Academy';
    } else if (newPlan === 'Professional School' || newPlan.includes('Professional')) {
      form.plan = 'School - Professional School';
    } else if (newPlan === 'Enterprise Institution' || newPlan.includes('Enterprise')) {
      form.plan = 'School - Enterprise Institution';
    } else {
      form.plan = newPlan;
    }
  }
});

function validateForm(): boolean {
  let valid = true;
  errors.fullName = '';
  errors.schoolName = '';
  errors.email = '';
  errors.phone = '';
  errors.message = '';

  if (!form.fullName || form.fullName.length < 2) {
    errors.fullName = 'Please enter your full name.';
    valid = false;
  }
  if (!form.schoolName || form.schoolName.length < 2) {
    errors.schoolName = 'Please enter the name of your school.';
    valid = false;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!form.email || !emailRegex.test(form.email)) {
    errors.email = 'Please provide a valid email address.';
    valid = false;
  }
  if (!form.phone || form.phone.length < 6) {
    errors.phone = 'Please provide a valid phone or WhatsApp number.';
    valid = false;
  }
  if (!form.message || form.message.length < 5) {
    errors.message = 'Please provide a brief message or question.';
    valid = false;
  }

  return valid;
}

const submitError = ref<string | null>(null);

async function submitInquiry() {
  if (!validateForm()) return;

  isSubmitting.value = true;
  submitError.value = null;

  try {
    await inquiryService.submitPublicInquiry({
      full_name: form.fullName,
      school_name: form.schoolName,
      email: form.email,
      phone: form.phone,
      plan: form.plan,
      message: form.message,
      preferred_channel: 'WhatsApp',
    });
    isSubmitted.value = true;
  } catch (err: any) {
    submitError.value = err?.response?.data?.detail || 'Failed to submit inquiry. Please try again.';
  } finally {
    isSubmitting.value = false;
  }
}

function resetForm() {
  form.fullName = '';
  form.schoolName = '';
  form.email = '';
  form.phone = '';
  form.message = '';
  submitError.value = null;
  isSubmitted.value = false;
}
</script>

<style scoped>
/* ==========================================================================
   SOMROYAL EMS PREMIUM CONTACT PAGE STYLES
   Colors:
     Primary navy: #071F49
     Deep navy: #031A3A
     Brand orange: #FF6500
     Secondary orange: #FF7A1A
     Royal blue: #1264E8
     Light blue bg: #EFF6FF
     Border: #D9E7FB
   ========================================================================== */

.contact-section {
  position: relative;
  padding: 80px 0 120px;
  background: linear-gradient(180deg, #FFFFFF 0%, #F5F8FD 35%, #EDF4FE 100%);
  overflow: hidden;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Subtle background glows */
.bg-shape-top-left {
  position: absolute;
  top: -90px;
  left: -80px;
  width: 440px;
  max-width: 100vw;
  height: 440px;
  background: radial-gradient(circle, rgba(18, 100, 232, 0.08) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.bg-shape-top-right {
  position: absolute;
  top: -80px;
  right: -70px;
  width: 450px;
  max-width: 100vw;
  height: 450px;
  background: radial-gradient(circle, rgba(255, 101, 0, 0.06) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.contact-container {
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
  max-width: 820px;
  margin: 0 auto 3.25rem;
}

/* Badge Pill */
.contact-badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.775rem;
  font-weight: 700;
  color: #FF6500;
  background: #FFF2E8;
  border: 1px solid #FFE3D1;
  padding: 0.35rem 1.15rem;
  border-radius: 50px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 1.15rem;
  box-shadow: 0 2px 6px rgba(255, 101, 0, 0.08);
}

.badge-plane-icon {
  width: 14px;
  height: 14px;
  stroke-width: 2.2;
}

/* Main Heading */
.section-title {
  position: relative;
  display: inline-block;
  font-family: 'Outfit', sans-serif;
  font-size: 2.65rem;
  font-weight: 800;
  color: #071F49;
  line-height: 1.22;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.text-orange {
  color: #FF6500;
}

/* 3 Sunburst rays on top right of "Team" */
.heading-sunburst {
  position: absolute;
  top: -8px;
  right: -22px;
  width: 20px;
  height: 20px;
}

.heading-sunburst .ray {
  position: absolute;
  background: #FF6500;
  border-radius: 2px;
}

.heading-sunburst .ray-1 {
  width: 8px;
  height: 2.5px;
  top: 4px;
  left: 0;
  transform: rotate(-35deg);
}

.heading-sunburst .ray-2 {
  width: 9px;
  height: 2.5px;
  top: 10px;
  left: 4px;
  transform: rotate(5deg);
}

.heading-sunburst .ray-3 {
  width: 8px;
  height: 2.5px;
  top: 17px;
  left: 2px;
  transform: rotate(45deg);
}

/* Subtitle */
.section-subtitle {
  font-size: 1.05rem;
  color: #405D8C;
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
  top: 5px;
  left: -195px;
  width: 220px;
  text-align: left;
}

.right-annotation {
  top: 10px;
  right: -195px;
  width: 220px;
  text-align: left;
}

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
  transform: rotate(4deg);
  margin-left: 8px;
}

.handwritten-arrow-left {
  width: 65px;
  height: 75px;
  margin-left: 55px;
  margin-top: -6px;
}

.handwritten-arrow-right {
  width: 60px;
  height: 75px;
  margin-left: 45px;
  margin-top: 4px;
}

/* ==========================================================================
   MAIN CONTACT GRID (Two Columns on Desktop)
   ========================================================================== */

.contact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.85rem;
  align-items: stretch;
  margin-bottom: 3.5rem;
}

/* Left & Right Card Shared Containers */
.contact-info-card,
.contact-form-card {
  background: #FFFFFF;
  border: 1.5px solid #D9E7FB;
  border-radius: 24px;
  padding: 2.25rem 2rem;
  box-shadow: 0 10px 30px rgba(18, 70, 197, 0.04);
  position: relative;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.contact-info-card:hover,
.contact-form-card:hover {
  box-shadow: 0 16px 40px rgba(18, 70, 197, 0.08);
}

/* ==========================================================================
   LEFT CARD: Institutional Support & HQ Image
   ========================================================================== */

.panel-header-wrap {
  margin-bottom: 1.5rem;
}

.panel-heading {
  font-family: 'Outfit', sans-serif;
  font-size: 1.4rem;
  font-weight: 800;
  color: #071F49;
  line-height: 1.25;
  margin-bottom: 0.5rem;
}

.panel-desc {
  font-size: 0.88rem;
  color: #405D8C;
  line-height: 1.55;
  margin: 0;
}

/* Split content inside left card */
.info-building-layout {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  flex: 1;
}

.info-items-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.info-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #EFF6FF;
  border: 1px solid #DBEAFE;
  color: #1264E8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon-circle svg {
  width: 20px;
  height: 20px;
}

.info-text-group {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: #8495B0;
  margin-bottom: 2px;
}

.info-val {
  font-size: 0.95rem;
  color: #071F49;
  line-height: 1.3;
}

.info-link-orange {
  color: #FF6500;
  font-weight: 700;
  text-decoration: none;
  transition: color 0.2s ease;
}

.info-link-orange:hover {
  color: #FF7A1A;
  text-decoration: underline;
}

.info-tel {
  text-decoration: none;
  transition: color 0.2s ease;
}

.info-tel:hover {
  color: #1264E8;
  text-decoration: underline;
}

/* Building Image & Floating Support Card */
.building-wrapper {
  position: relative;
  width: 220px;
  flex-shrink: 0;
  align-self: stretch;
  min-height: 280px;
  display: flex;
  flex-direction: column;
}

.building-image-container {
  width: 100%;
  height: 240px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(7, 31, 73, 0.12);
  border: 1px solid #D9E7FB;
}

.hq-building-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* Floating Card over the bottom of the building */
.floating-support-card {
  position: absolute;
  bottom: 0;
  left: -35px;
  right: -10px;
  background: #FFFFFF;
  border: 1px solid #D9E7FB;
  border-radius: 16px;
  padding: 0.75rem 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  box-shadow: 0 10px 24px rgba(7, 31, 73, 0.15);
  transform: rotate(-2deg);
  transition: transform 0.3s ease;
}

.floating-support-card:hover {
  transform: rotate(0deg) translateY(-2px);
}

.floating-icon-box {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #FFF2E8;
  color: #FF6500;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.floating-icon-box svg {
  width: 18px;
  height: 18px;
}

.floating-texts {
  flex: 1;
}

.floating-title {
  font-family: 'Outfit', sans-serif;
  font-size: 0.78rem;
  font-weight: 700;
  color: #071F49;
  margin: 0;
  line-height: 1.2;
}

.floating-sub {
  font-size: 0.68rem;
  color: #64748B;
  margin: 2px 0 0 0;
}

.floating-arrow-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #FF6500;
  color: #FFFFFF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.floating-arrow-btn:hover {
  background: #FF7A1A;
  transform: scale(1.08);
}

.floating-arrow-btn svg {
  width: 12px;
  height: 12px;
}

/* Direct Inquiries Notice Strip */
.direct-inquiry-box {
  background: #FFF8F2;
  border: 1px solid #FFE3D1;
  border-radius: 14px;
  padding: 0.85rem 1.15rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-top: 1.75rem;
}

.direct-check-icon {
  width: 26px;
  height: 26px;
  color: #FF6500;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.direct-check-icon svg {
  width: 24px;
  height: 24px;
}

.direct-inquiry-text {
  font-size: 0.8rem;
  color: #405D8C;
  line-height: 1.45;
}

.direct-inquiry-text strong {
  color: #071F49;
}

/* ==========================================================================
   RIGHT CARD: Inquiry Form
   ========================================================================== */

.form-header-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #FFF2E8;
  color: #FF6500;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.form-header-icon-box svg {
  width: 22px;
  height: 22px;
}

.form-card-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.35rem;
  font-weight: 800;
  color: #071F49;
  line-height: 1.25;
  margin: 0 0 0.25rem 0;
}

.form-card-sub {
  font-size: 0.84rem;
  color: #64748B;
  margin: 0;
}

/* Success Banner */
.success-banner {
  background: #ECFDF5;
  border: 1.5px solid #A7F3D0;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.success-icon {
  width: 32px;
  height: 32px;
  color: #059669;
  flex-shrink: 0;
}

.success-icon svg {
  width: 32px;
  height: 32px;
}

.success-content {
  flex: 1;
}

.success-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #065F46;
  margin: 0 0 0.25rem 0;
}

.success-desc {
  font-size: 0.88rem;
  color: #047857;
  line-height: 1.5;
  margin: 0 0 1rem 0;
}

.btn-reset-form {
  background: #059669;
  color: #FFFFFF;
  border: none;
  font-size: 0.84rem;
  font-weight: 600;
  padding: 0.45rem 1rem;
  border-radius: 30px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-reset-form:hover {
  background: #047857;
}

/* Form Layout */
.inquiry-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  flex: 1;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 0.84rem;
  font-weight: 600;
  color: #071F49;
  margin-bottom: 0.4rem;
  display: flex;
  align-items: center;
  gap: 2px;
}

.required {
  color: #FF6500;
}

/* Inputs with Icons */
.input-with-icon,
.select-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #94A3B8;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.65rem;
  font-size: 0.9rem;
  color: #071F49;
  background: #FFFFFF;
  border: 1.5px solid #D9E7FB;
  border-radius: 12px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: #94A3B8;
  font-size: 0.86rem;
}

.form-input:focus {
  border-color: #FF6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.has-error .form-input,
.has-error .form-textarea {
  border-color: #EF4444;
}

.error-msg {
  font-size: 0.75rem;
  color: #EF4444;
  margin-top: 4px;
}

/* Select */
.form-select {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.65rem;
  font-size: 0.9rem;
  color: #071F49;
  background: #FFFFFF;
  border: 1.5px solid #D9E7FB;
  border-radius: 12px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.form-select:focus {
  border-color: #FF6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

.select-chevron {
  position: absolute;
  right: 14px;
  width: 18px;
  height: 18px;
  color: #64748B;
  pointer-events: none;
}

/* Textarea with Icon */
.textarea-with-icon {
  position: relative;
  display: flex;
}

.textarea-field-icon {
  position: absolute;
  top: 13px;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #94A3B8;
  pointer-events: none;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.65rem;
  font-size: 0.9rem;
  color: #071F49;
  background: #FFFFFF;
  border: 1.5px solid #D9E7FB;
  border-radius: 12px;
  outline: none;
  font-family: inherit;
  resize: vertical;
  min-height: 85px;
  transition: all 0.2s ease;
}

.form-textarea::placeholder {
  color: #94A3B8;
  font-size: 0.86rem;
}

.form-textarea:focus {
  border-color: #FF6500;
  box-shadow: 0 0 0 3px rgba(255, 101, 0, 0.12);
}

/* Submit Button */
.btn-send-inquiry {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.95rem 1.75rem;
  font-size: 1rem;
  font-weight: 700;
  color: #FFFFFF;
  background: linear-gradient(135deg, #FF6500 0%, #FF7A1A 100%);
  border: none;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(255, 101, 0, 0.35);
  transition: all 0.25s ease;
  outline: none;
}

.btn-send-inquiry:hover:not(:disabled) {
  background: linear-gradient(135deg, #FF7A1A 0%, #FF8A2E 100%);
  box-shadow: 0 8px 24px rgba(255, 101, 0, 0.45);
  transform: translateY(-2px);
}

.btn-lead-plane {
  width: 18px;
  height: 18px;
  transition: transform 0.25s ease;
}

.btn-trail-arrow {
  width: 18px;
  height: 18px;
  transition: transform 0.25s ease;
}

.btn-send-inquiry:hover .btn-trail-arrow {
  transform: translateX(4px);
}

.spinner-icon {
  width: 20px;
  height: 20px;
}

/* ==========================================================================
   BOTTOM TRUST & BENEFITS STRIP (4 items)
   ========================================================================== */

.bottom-trust-strip {
  background: #FFFFFF;
  border: 1px solid #D9E7FB;
  border-radius: 20px;
  padding: 1.35rem 2rem;
  box-shadow: 0 10px 32px rgba(7, 31, 73, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 5;
}

.trust-cell {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.trust-icon-container {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #FFF2E8;
  color: #FF6500;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.trust-icon-container svg {
  width: 22px;
  height: 22px;
}

.trust-cell-text {
  display: flex;
  flex-direction: column;
}

.trust-heading {
  font-family: 'Outfit', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: #071F49;
  margin: 0;
  line-height: 1.3;
}

.trust-desc {
  font-size: 0.78rem;
  color: #64748B;
  margin: 2px 0 0 0;
}

.trust-separator {
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
  .contact-section {
    padding: 65px 0 95px;
  }

  .contact-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .info-building-layout {
    flex-direction: row;
  }

  .building-wrapper {
    width: 200px;
  }

  .bottom-trust-strip {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .trust-separator {
    display: none;
  }
}

@media (max-width: 768px) {
  .contact-section {
    padding: 55px 0 75px;
  }

  .contact-container {
    padding: 0 clamp(0.85rem, 3vw, 1.5rem);
  }

  .section-title {
    font-size: clamp(1.85rem, 5vw, 2.35rem);
  }

  .info-building-layout {
    flex-direction: column;
  }

  .building-wrapper {
    width: 100%;
    min-height: auto;
  }

  .building-image-container {
    height: 180px;
  }

  .floating-support-card {
    position: static;
    transform: none;
    margin-top: 1rem;
  }

  .form-row-2 {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-input,
  .form-select,
  .form-textarea {
    font-size: 16px;
    min-height: 46px;
  }

  .btn-submit {
    min-height: 48px;
    width: 100%;
    justify-content: center;
    font-size: 1rem;
  }

  .bottom-trust-strip {
    grid-template-columns: 1fr;
    gap: 1.25rem;
    padding: 1.25rem;
  }

  .wave-left,
  .wave-right {
    opacity: 0.35;
    max-width: 40vw;
  }
}

@media (max-width: 480px) {
  .contact-badge-pill {
    font-size: 0.72rem;
    padding: 0.3rem 0.85rem;
  }

  .section-title {
    font-size: clamp(1.65rem, 5.5vw, 2.05rem);
  }

  .contact-info-card,
  .contact-form-card {
    padding: 1.5rem 1.15rem 1.35rem;
    border-radius: 16px;
  }

  .contact-item {
    gap: 0.75rem;
  }

  .contact-icon-box {
    width: 38px;
    height: 38px;
    border-radius: 8px;
  }

  .item-title {
    font-size: 0.85rem;
  }

  .item-detail {
    font-size: 0.82rem;
  }
}
</style>
