<template>
  <section id="features" class="features-section">
    <!-- Background Decorative Visual Elements -->
    <div class="features-bg-decorations" aria-hidden="true">
      <!-- Soft Pale-Blue Radial Gradients -->
      <div class="bg-radial-glow-top"></div>
      <div class="bg-radial-glow-right"></div>
      
      <!-- Upper Left Curved Translucent Shape -->
      <svg class="bg-swoosh-top-left" viewBox="0 0 500 350" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M-100,-50 C120,60 260,180 320,350 L-100,350 Z" fill="rgba(234, 241, 255, 0.6)" />
        <path d="M-80,-30 C80,80 200,160 250,320 L-80,320 Z" fill="rgba(240, 245, 255, 0.7)" />
      </svg>

      <!-- Bottom-Left Layered Abstract Corner Waves -->
      <div class="corner-waves-bottom-left">
        <svg viewBox="0 0 320 220" fill="none" xmlns="http://www.w3.org/2000/svg" class="corner-wave-svg">
          <!-- Light blue accent wave -->
          <path d="M0 220V120C60 135 120 160 160 220H0Z" fill="rgba(85, 142, 210, 0.25)" />
          <!-- Vibrant Orange swoosh -->
          <path d="M0 220V145C80 140 140 175 190 220H0Z" fill="#FF6900" />
          <!-- Deep Navy base wave -->
          <path d="M0 220V170C60 170 110 190 145 220H0Z" fill="#071D49" />
        </svg>
      </div>

      <!-- Bottom-Right Layered Abstract Corner Waves -->
      <div class="corner-waves-bottom-right">
        <svg viewBox="0 0 320 260" fill="none" xmlns="http://www.w3.org/2000/svg" class="corner-wave-svg">
          <!-- Bright Orange curved swoosh rising up -->
          <path d="M320 260V80C260 120 220 180 150 260H320Z" fill="#FF6900" />
          <!-- Deep Navy massive curved wave -->
          <path d="M320 260V130C270 165 240 210 195 260H320Z" fill="#071D49" />
          <!-- Subtle cyan/blue accent rim -->
          <path d="M150 260C220 180 260 120 320 80" stroke="rgba(85, 142, 210, 0.4)" stroke-width="2" />
        </svg>
      </div>
    </div>

    <div class="features-container">
      <!-- Section Header -->
      <div class="features-header-wrap">
        <!-- Small Pill Badge with Sparkle Icon -->
        <div class="features-badge-pill">
          <svg class="badge-sparkle-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z" />
          </svg>
          <span>POWERFUL FEATURES</span>
        </div>

        <!-- Main Heading with Orange Emphasis -->
        <h2 class="features-main-title">
          Built Specifically for Modern<br />
          <span class="text-orange-gradient">Educational Excellence</span>
        </h2>

        <!-- Supporting Subtitle -->
        <p class="features-subtitle">
          Explore the comprehensive features operational in Somroyal Educational Management System, engineered with single-source-of-truth reliability to simplify school operations and enhance learning outcomes.
        </p>

        <!-- Left Handwritten-style Annotation & Curved Arrow -->
        <div class="handwritten-annotation left-annotation" aria-hidden="true">
          <!-- Dot Grid Matrix (5x5) -->
          <div class="dot-matrix-left">
            <div v-for="i in 25" :key="i" class="dot-cell"></div>
          </div>
          
          <div class="handwritten-content-left">
            <span class="handwritten-text">
              Everything<br />
              your school needs<br />
              in one platform
            </span>
            <!-- Hand-drawn curved arrow with loop pointing to cards -->
            <svg class="handwritten-arrow-svg" viewBox="0 0 100 80" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M15 10 C 25 35, 15 55, 30 50 C 45 45, 55 25, 40 25 C 25 25, 20 60, 65 65"
                stroke="#FF6900"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- Arrow head -->
              <path
                d="M55 58 L 65 65 L 56 73"
                stroke="#FF6900"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
        </div>

        <!-- Right Handwritten-style Annotation & Sunburst -->
        <div class="handwritten-annotation right-annotation" aria-hidden="true">
          <div class="handwritten-content-right">
            <!-- Orange Sunburst Rays above text -->
            <div class="sunburst-rays">
              <span class="ray ray-1"></span>
              <span class="ray ray-2"></span>
              <span class="ray ray-3"></span>
            </div>
            <span class="handwritten-text">
              Simpler<br />
              Smarter<br />
              Stronger Schools
            </span>
            <!-- Faint curved arc swooping to the right -->
            <svg class="handwritten-arc-svg" viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M10 30 C 50 10, 80 15, 115 35"
                stroke="#FF6900"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-dasharray="2 3"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- CATEGORY FILTER PILL BUTTONS -->
      <div class="filter-pill-bar" role="tablist" aria-label="Feature module categories">
        <button
          v-for="cat in categoryFilters"
          :key="cat.id"
          type="button"
          class="category-filter-btn"
          :class="{ 'active': activeCategory === cat.id }"
          @click="setCategory(cat.id)"
          :aria-selected="activeCategory === cat.id"
          role="tab"
        >
          <!-- Category Lucide Icons -->
          <svg v-if="cat.id === 'all'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="7" height="7" x="3" y="3" rx="1" />
            <rect width="7" height="7" x="14" y="3" rx="1" />
            <rect width="7" height="7" x="14" y="14" rx="1" />
            <rect width="7" height="7" x="3" y="14" rx="1" />
          </svg>
          <svg v-else-if="cat.id === 'academics'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
            <path d="M6 12v5c3 3 9 3 12 0v-5" />
          </svg>
          <svg v-else-if="cat.id === 'portals'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <svg v-else-if="cat.id === 'finances'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="20" height="14" x="2" y="5" rx="2" />
            <line x1="2" x2="22" y1="10" y2="10" />
          </svg>
          <svg v-else-if="cat.id === 'exams'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" x2="8" y1="13" y2="13" />
            <line x1="16" x2="8" y1="17" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          <svg v-else-if="cat.id === 'communication'" class="cat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
          </svg>

          <span>{{ cat.label }}</span>
        </button>
      </div>

      <!-- 6 FEATURE CARDS GRID -->
      <div class="features-cards-grid">
        <div
          v-for="card in displayedFeatures"
          :key="card.id"
          class="feature-box-card"
          :class="[card.cardClass, { 'card-highlighted-orange': card.id === 'fees' }]"
        >
          <!-- Card Top Row: Icon Container + Status Badge -->
          <div class="card-top-row">
            <!-- Icon rounded container -->
            <div class="card-icon-wrapper" :class="card.iconWrapperClass">
              <!-- Users Icon -->
              <svg v-if="card.icon === 'users'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>

              <!-- Book Open Icon -->
              <svg v-else-if="card.icon === 'book-open'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>

              <!-- Graduation Cap / Faculty Icon -->
              <svg v-else-if="card.icon === 'graduation'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                <path d="M6 12v5c3 3 9 3 12 0v-5" />
              </svg>

              <!-- Calendar Check Icon -->
              <svg v-else-if="card.icon === 'calendar-check'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="18" height="18" x="3" y="4" rx="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
                <path d="m9 16 2 2 4-4" />
              </svg>

              <!-- File Text Icon -->
              <svg v-else-if="card.icon === 'file-text'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" x2="8" y1="13" y2="13" />
                <line x1="16" x2="8" y1="17" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>

              <!-- Currency / Circle Dollar Icon -->
              <svg v-else-if="card.icon === 'dollar'" class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8" />
                <path d="M12 18V6" />
              </svg>

              <!-- Fallback -->
              <svg v-else class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
              </svg>
            </div>

            <!-- Status Badge Pill -->
            <div class="card-status-badge" :class="card.badgeClass">
              <!-- Verification Check or Colored Dot -->
              <svg v-if="card.badgeIcon === 'check'" class="badge-icon-status" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span v-else class="badge-dot-status" :class="card.badgeDotClass"></span>
              <span class="badge-text">{{ card.statusText }}</span>
            </div>
          </div>

          <!-- Card Title -->
          <h3 class="card-heading">{{ card.title }}</h3>

          <!-- Card Description -->
          <p class="card-summary">{{ card.description }}</p>

          <!-- Capability Tags -->
          <div class="card-capability-tags">
            <span
              v-for="tag in card.tags"
              :key="tag"
              class="capability-tag"
              :class="card.tagClass"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- BOTTOM CALL-TO-ACTION BANNER -->
      <div class="features-cta-banner">
        <div class="cta-inner-layout">
          <!-- Left: 3D Rocket Icon Illustration -->
          <div class="cta-rocket-box">
            <svg class="rocket-svg" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Rocket flame -->
              <path d="M14 46 C12 54, 8 58, 6 60 C12 58, 16 54, 20 48 Z" fill="#FFAA00" />
              <path d="M11 48 C10 52, 7 55, 6 56 C9 55, 12 52, 14 49 Z" fill="#FF3300" />
              <!-- Rocket wings -->
              <path d="M18 42 L10 40 L16 30 Z" fill="#E2E8F0" />
              <path d="M40 50 L42 58 L32 52 Z" fill="#E2E8F0" />
              <!-- Rocket Body -->
              <path d="M22 46 C20 38, 22 28, 30 18 C38 8, 48 4, 52 4 C52 8, 48 18, 38 26 C28 34, 24 44, 22 46 Z" fill="url(#rocketBodyGrad)" />
              <!-- Rocket Nose Cone -->
              <path d="M44 12 C48 8, 52 4, 52 4 C52 4, 48 8, 44 12 Z" fill="#FF5500" />
              <!-- Cabin Window -->
              <circle cx="34" cy="18" r="4.5" fill="#FFFFFF" />
              <circle cx="34" cy="18" r="3" fill="#1E469A" />
              <circle cx="35" cy="17" r="1" fill="#FFFFFF" />
              <!-- Fin accent -->
              <path d="M18 44 C22 46, 26 44, 28 42 L24 38 Z" fill="#FF7A00" />
              <defs>
                <linearGradient id="rocketBodyGrad" x1="20" y1="46" x2="52" y2="4">
                  <stop offset="0%" stop-color="#FF5500" />
                  <stop offset="60%" stop-color="#FF7A00" />
                  <stop offset="100%" stop-color="#FFA834" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <!-- Center Text Content -->
          <div class="cta-text-content">
            <h3 class="cta-headline">
              Ready to Transform Your <span class="cta-orange-highlight">School Operations?</span>
            </h3>
            <p class="cta-description">
              Join schools across Somalia using Somroyal EMS for smarter, simpler, and more efficient management.
            </p>
          </div>

          <!-- Right Action Buttons -->
          <div class="cta-button-group">
            <router-link to="/login" class="btn-cta-primary" id="features-cta-get-started">
              <span>Get Started Today</span>
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" x2="19" y1="12" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </router-link>

            <button
              type="button"
              class="btn-cta-secondary"
              @click="setCategory('all')"
              id="features-cta-view-all"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="7" height="7" x="3" y="3" rx="1" />
                <rect width="7" height="7" x="14" y="3" rx="1" />
                <rect width="7" height="7" x="14" y="14" rx="1" />
                <rect width="7" height="7" x="3" y="14" rx="1" />
              </svg>
              <span>View All Capabilities</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

// CATEGORIES CONFIGURATION (Exact 6 as requested)
const categoryFilters = [
  { id: 'all', label: 'All Modules' },
  { id: 'academics', label: 'Academics & Classes' },
  { id: 'portals', label: 'Dedicated Portals' },
  { id: 'finances', label: 'Fees & Invoicing' },
  { id: 'exams', label: 'Exams & Grading' },
  { id: 'communication', label: 'Communication' },
];

const activeCategory = ref('all');

function setCategory(id: string) {
  activeCategory.value = id;
}

// FEATURE CARDS DATA INTERFACE
interface FeatureCardItem {
  id: string;
  categories: string[];
  categoryLabel: string;
  icon: string;
  iconWrapperClass: string;
  badgeIcon?: 'check' | 'dot';
  badgeDotClass?: string;
  badgeClass: string;
  statusText: string;
  title: string;
  description: string;
  tags: string[];
  tagClass: string;
  circleBtnClass: string;
  cardClass?: string;
}

// 6 PRIMARY FEATURE CARDS FROM REFERENCE SCREENSHOT
const allFeaturesList: FeatureCardItem[] = [
  // CARD 1: Student Bio-Data & Admissions
  {
    id: 'students',
    categories: ['all', 'academics'],
    categoryLabel: 'Academics & Admissions',
    icon: 'users',
    iconWrapperClass: 'icon-wrap-blue',
    badgeIcon: 'check',
    badgeClass: 'badge-verified-green',
    statusText: 'Verified Production',
    title: 'Student Bio-Data & Admissions',
    description: 'Comprehensive student registry with admission numbering, guardian contacts, historical records, transition logs, and Excel batch importing.',
    tags: ['Admissions', 'Guardian Contacts', 'Excel Import'],
    tagClass: 'tag-slate',
    circleBtnClass: 'circle-btn-navy',
  },

  // CARD 2: Class & Section Streaming
  {
    id: 'classes',
    categories: ['all', 'academics'],
    categoryLabel: 'Academic Hierarchy',
    icon: 'book-open',
    iconWrapperClass: 'icon-wrap-orange',
    badgeIcon: 'dot',
    badgeDotClass: 'dot-orange',
    badgeClass: 'badge-operational-orange',
    statusText: 'Active Operational',
    title: 'Class & Section Streaming',
    description: 'Structured Primary (Grade 1-8) and Secondary (Form 1-4) hierarchy with capacity monitoring, subject assignments, and academic promotion.',
    tags: ['Primary & Secondary', 'Capacity Limits', 'Bulk Promotion'],
    tagClass: 'tag-orange',
    circleBtnClass: 'circle-btn-orange',
    cardClass: 'card-warm-tint',
  },

  // CARD 3: Faculty & Teacher Assignments
  {
    id: 'faculty',
    categories: ['all', 'academics', 'portals'],
    categoryLabel: 'Staff Management',
    icon: 'graduation',
    iconWrapperClass: 'icon-wrap-blue',
    badgeIcon: 'dot',
    badgeDotClass: 'dot-blue',
    badgeClass: 'badge-operational-blue',
    statusText: 'Active Operational',
    title: 'Faculty & Teacher Assignments',
    description: 'Centralized teacher profiles, qualifications, and automated class-subject pairing with timetable integration and conflict prevention.',
    tags: ['Faculty Registry', 'Curriculum Pairing', 'Workload Tracking'],
    tagClass: 'tag-blue',
    circleBtnClass: 'circle-btn-navy',
  },

  // CARD 4: Daily Attendance & Absent Alerts
  {
    id: 'attendance',
    categories: ['all', 'academics', 'communication'],
    categoryLabel: 'Attendance & Alerts',
    icon: 'calendar-check',
    iconWrapperClass: 'icon-wrap-green',
    badgeIcon: 'check',
    badgeClass: 'badge-operational-green',
    statusText: 'Active Operational',
    title: 'Daily Attendance & Absent Alerts',
    description: 'Classroom attendance with automated absent alerts sent directly to guardian phones via Hormuud SMS.',
    tags: ['Period Attendance', 'Absent Trigger', 'Attendance Rates'],
    tagClass: 'tag-green',
    circleBtnClass: 'circle-btn-green',
  },

  // CARD 5: Examinations, Grading & Transcripts
  {
    id: 'exams',
    categories: ['all', 'exams', 'academics'],
    categoryLabel: 'Assessment & Grades',
    icon: 'file-text',
    iconWrapperClass: 'icon-wrap-red',
    badgeIcon: 'dot',
    badgeDotClass: 'dot-red',
    badgeClass: 'badge-operational-red',
    statusText: 'Active Operational',
    title: 'Examinations, Grading & Transcripts',
    description: 'Assessment weighting, marks entry with approval workflows, automated letter grades (A-F), and verified printable digital transcripts.',
    tags: ['Weightages', 'Approval Workflow', 'Report Cards'],
    tagClass: 'tag-red',
    circleBtnClass: 'circle-btn-red',
  },

  // CARD 6: Fee Invoicing & Payment Receipts
  {
    id: 'fees',
    categories: ['all', 'finances'],
    categoryLabel: 'Finance & Invoicing',
    icon: 'dollar',
    iconWrapperClass: 'icon-wrap-orange',
    badgeIcon: 'dot',
    badgeDotClass: 'dot-orange',
    badgeClass: 'badge-operational-orange',
    statusText: 'Active Operational',
    title: 'Fee Invoicing & Payment Receipts',
    description: 'Multi-term billing structures, student invoice ledgers, and official receipt vouchers supporting Cash, EVC Plus, ZAAD, and Bank deposits.',
    tags: ['EVC Plus / ZAAD', 'Invoice Ledgers', 'Verified Receipts'],
    tagClass: 'tag-orange',
    circleBtnClass: 'circle-btn-orange',
  },
];

// REACTIVE FILTERING
const displayedFeatures = computed(() => {
  if (activeCategory.value === 'all') {
    return allFeaturesList;
  }
  return allFeaturesList.filter(item => item.categories.includes(activeCategory.value));
});

</script>

<style scoped>
/* MAIN FEATURES SECTION WRAPPER */
.features-section {
  position: relative;
  background-color: #F5F8FD;
  padding: 85px 0 95px;
  overflow: hidden;
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #071D49;
}

/* BACKGROUND DECORATIONS */
.features-bg-decorations {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.bg-radial-glow-top {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 900px;
  max-width: 100vw;
  height: 500px;
  background: radial-gradient(circle, rgba(234, 241, 255, 0.95) 0%, rgba(245, 248, 253, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.bg-radial-glow-right {
  position: absolute;
  top: 120px;
  right: -80px;
  width: 480px;
  max-width: 100vw;
  height: 480px;
  background: radial-gradient(circle, rgba(255, 105, 0, 0.04) 0%, rgba(255, 245, 235, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.bg-swoosh-top-left {
  position: absolute;
  top: 0;
  left: 0;
  width: 420px;
  max-width: 100vw;
  height: auto;
  opacity: 0.8;
  pointer-events: none;
}

/* Overlapping Corner Waves */
.corner-waves-bottom-left {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 320px;
  max-width: 50vw;
  height: 220px;
  z-index: 1;
  pointer-events: none;
}

.corner-waves-bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 340px;
  max-width: 50vw;
  height: 260px;
  z-index: 1;
  pointer-events: none;
}

.corner-wave-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* CONTENT CONTAINER */
.features-container {
  position: relative;
  z-index: 2;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* HEADER WRAP */
.features-header-wrap {
  position: relative;
  text-align: center;
  max-width: 860px;
  margin: 0 auto 3rem;
}

/* SMALL BADGE PILL */
.features-badge-pill {
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
  box-shadow: 0 2px 6px rgba(255, 105, 0, 0.06);
}

.badge-sparkle-icon {
  width: 12px;
  height: 12px;
}

/* MAIN TITLE */
.features-main-title {
  font-size: clamp(2.1rem, 3.2vw, 2.85rem);
  font-weight: 800;
  color: #071D49;
  line-height: 1.18;
  letter-spacing: -0.025em;
  margin: 0 0 1.15rem;
}

.text-orange-gradient {
  color: #FF6900;
}

/* SUBTITLE */
.features-subtitle {
  font-size: 1.025rem;
  line-height: 1.68;
  color: #52678A;
  margin: 0 auto;
  max-width: 800px;
}

/* HANDWRITTEN ANNOTATIONS */
.handwritten-annotation {
  position: absolute;
  z-index: 3;
}

.left-annotation {
  left: 0;
  top: 10px;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.dot-matrix-left {
  display: grid;
  grid-template-columns: repeat(5, 5px);
  gap: 7px;
  padding-top: 1.25rem;
}

.dot-cell {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #C4D7F8;
  opacity: 0.85;
}

.handwritten-content-left {
  position: relative;
  text-align: left;
  transform: rotate(-3deg);
}

.right-annotation {
  right: 0;
  top: 15px;
  transform: rotate(5deg);
}

.handwritten-content-right {
  position: relative;
  text-align: center;
}

.sunburst-rays {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-bottom: -4px;
  margin-right: 15px;
}

.ray {
  display: inline-block;
  width: 2px;
  height: 10px;
  background: #FF6900;
  border-radius: 2px;
}

.ray-1 { transform: rotate(-30deg); height: 8px; }
.ray-2 { transform: rotate(0deg); height: 12px; }
.ray-3 { transform: rotate(30deg); height: 9px; }

.handwritten-text {
  font-family: 'Caveat', 'Comic Sans MS', cursive, sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: #FF6900;
  line-height: 1.22;
  display: inline-block;
  white-space: nowrap;
}

.handwritten-arrow-svg {
  width: 75px;
  height: 60px;
  display: block;
  margin-top: -5px;
  margin-left: 20px;
}

.handwritten-arc-svg {
  width: 100px;
  height: 35px;
  display: block;
  margin-top: 2px;
  margin-left: 10px;
}

/* CATEGORY FILTER PILL BAR */
.filter-pill-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  max-width: 100%;
  box-sizing: border-box;
  margin-bottom: 2.85rem;
}

.category-filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  border-radius: 9999px;
  font-size: 0.88rem;
  font-weight: 600;
  color: #071D49;
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 2px 6px rgba(7, 29, 73, 0.03);
  white-space: nowrap;
}

.cat-icon {
  width: 16px;
  height: 16px;
  color: inherit;
  flex-shrink: 0;
}

.category-filter-btn:hover {
  border-color: #FF6900;
  color: #FF6900;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 105, 0, 0.12);
}

.category-filter-btn.active {
  background: #071D49;
  color: #FFFFFF;
  border-color: #071D49;
  box-shadow: 0 6px 18px rgba(7, 29, 73, 0.22);
}

.category-filter-btn.active .cat-icon {
  color: #FFFFFF;
}

/* 6 FEATURE CARDS GRID */
.features-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.85rem;
  margin-bottom: 3.5rem;
}

/* FEATURE BOX CARD */
.feature-box-card {
  background: #FFFFFF;
  border: 1.5px solid #DFE8F7;
  border-radius: 18px;
  padding: 1.85rem;
  display: flex;
  flex-direction: column;
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 16px rgba(7, 29, 73, 0.04);
  position: relative;
}

.feature-box-card:hover {
  transform: translateY(-4px);
  border-color: #FF6900;
  box-shadow: 0 16px 32px -4px rgba(7, 29, 73, 0.1), 0 4px 12px rgba(0, 0, 0, 0.03);
}

/* CARD 2 Warm Tint */
.card-warm-tint {
  background: linear-gradient(180deg, #FFFFFF 0%, #FFFDFC 100%);
}

/* CARD 6 Orange Highlighted Border */
.card-highlighted-orange {
  border: 1.5px solid #FF8A00;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFFDF9 100%);
  box-shadow: 0 8px 24px -2px rgba(255, 105, 0, 0.12);
}

.card-highlighted-orange:hover {
  border-color: #FF6900;
  box-shadow: 0 18px 36px -4px rgba(255, 105, 0, 0.22);
}

/* CARD TOP ROW */
.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

/* ICON WRAPPER */
.card-icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.8);
  transition: transform 0.2s ease;
}

.feature-box-card:hover .card-icon-wrapper {
  transform: scale(1.05);
}

.icon-wrap-blue {
  background: #EAF1FF;
  color: #1246C5;
  border: 1px solid #D6E4FF;
}

.icon-wrap-orange {
  background: #FFF2E8;
  color: #FF6900;
  border: 1px solid #FFE2CE;
}

.icon-wrap-green {
  background: #E8F9F3;
  color: #08B981;
  border: 1px solid #C8F4E5;
}

.icon-wrap-red {
  background: #FEECEF;
  color: #F20D32;
  border: 1px solid #FDCED6;
}

.card-svg-icon {
  width: 25px;
  height: 25px;
}

/* STATUS BADGE */
.card-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.badge-icon-status {
  width: 11px;
  height: 11px;
}

.badge-dot-status {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-orange { background: #FF6900; }
.dot-blue { background: #1246C5; }
.dot-red { background: #F20D32; }

/* Status Badge Themes */
.badge-verified-green {
  background: #E6F8F0;
  border: 1px solid #A7F3D0;
  color: #059669;
}

.badge-operational-orange {
  background: #FFF3EA;
  border: 1px solid #FFDEC9;
  color: #FF6900;
}

.badge-operational-blue {
  background: #EDF4FF;
  border: 1px solid #CCE0FF;
  color: #1246C5;
}

.badge-operational-green {
  background: #E8F9F3;
  border: 1px solid #B8F2DF;
  color: #08B981;
}

.badge-operational-red {
  background: #FEECEF;
  border: 1px solid #FDC8D1;
  color: #F20D32;
}

/* CARD HEADING & SUMMARY */
.card-heading {
  font-size: 1.18rem;
  font-weight: 700;
  color: #071D49;
  line-height: 1.32;
  margin: 0 0 0.65rem;
}

.card-summary {
  font-size: 0.905rem;
  color: #52678A;
  line-height: 1.62;
  margin: 0 0 1.25rem;
  flex-grow: 1;
}

/* CAPABILITY TAGS */
.card-capability-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 0;
  padding-top: 0.25rem;
}

.capability-tag {
  font-size: 0.735rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background: #F8FAFD;
  color: #52678A;
  border: 1px solid #DFE8F7;
  white-space: nowrap;
}

.tag-orange {
  border-color: #FFDEC9;
}

.tag-blue {
  border-color: #D6E4FF;
}

.tag-green {
  border-color: #B8F2DF;
}

.tag-red {
  border-color: #FDC8D1;
}

/* BOTTOM CALL-TO-ACTION BANNER */
.features-cta-banner {
  background: linear-gradient(135deg, #071D49 0%, #061638 100%);
  border: 1px solid rgba(85, 142, 210, 0.45);
  border-radius: 20px;
  padding: 1.85rem 2.25rem;
  box-shadow: 0 20px 42px -8px rgba(7, 29, 73, 0.35);
  position: relative;
  z-index: 5;
}

.cta-inner-layout {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.cta-rocket-box {
  width: 58px;
  height: 58px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rocket-svg {
  width: 56px;
  height: 56px;
  filter: drop-shadow(0 4px 12px rgba(255, 105, 0, 0.4));
}

.cta-text-content {
  flex-grow: 1;
}

.cta-headline {
  font-size: 1.42rem;
  font-weight: 800;
  color: #FFFFFF;
  margin: 0 0 0.35rem;
  letter-spacing: -0.015em;
}

.cta-orange-highlight {
  color: #FF6900;
}

.cta-description {
  font-size: 0.925rem;
  color: #B8C8E0;
  margin: 0;
  line-height: 1.5;
}

.cta-button-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-shrink: 0;
}

.btn-cta-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #FF6900 0%, #FF7A00 100%);
  color: #FFFFFF;
  font-size: 0.925rem;
  font-weight: 700;
  padding: 0.75rem 1.45rem;
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
  padding: 0.75rem 1.35rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.22s ease;
  white-space: nowrap;
}

.btn-cta-secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #FF6900;
  color: #FFFFFF;
}

/* RESPONSIVE LAYOUT */
@media (max-width: 1024px) {
  .left-annotation,
  .right-annotation {
    display: none;
  }
}

@media (max-width: 1120px) {
  .features-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .cta-inner-layout {
    flex-direction: column;
    text-align: center;
  }
  .cta-rocket-box {
    margin: 0 auto;
  }
  .cta-button-group {
    justify-content: center;
    width: 100%;
  }
}

@media (max-width: 768px) {
  .features-section {
    padding: 55px 0 70px;
  }
  .features-container {
    padding: 0 clamp(0.85rem, 3vw, 1.25rem);
  }
  .features-cards-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .filter-pill-bar {
    justify-content: flex-start;
    overflow-x: auto;
    padding: 0.25rem 0.5rem 0.75rem;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .filter-pill-bar::-webkit-scrollbar {
    display: none;
  }
  .category-filter-btn {
    flex-shrink: 0;
    min-height: 42px;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
  }
  .cta-button-group {
    flex-direction: column;
    gap: 0.65rem;
  }
  .btn-cta-primary,
  .btn-cta-secondary {
    width: 100%;
    justify-content: center;
    min-height: 46px;
  }
}

@media (max-width: 480px) {
  .features-badge-pill {
    font-size: 0.72rem;
    padding: 0.35rem 0.85rem;
  }
  .features-main-title {
    font-size: clamp(1.65rem, 5.5vw, 2.05rem);
    line-height: 1.22;
  }
  .features-subtitle {
    font-size: 0.9rem;
    line-height: 1.55;
    margin-bottom: 2rem;
  }
  .feature-box-card {
    padding: 1.35rem 1.15rem;
    border-radius: 14px;
  }
  .card-feature-title {
    font-size: 1.15rem;
  }
  .card-bullet-text {
    font-size: 0.82rem;
  }
  .corner-waves-bottom-left,
  .corner-waves-bottom-right {
    opacity: 0.3;
    transform: scale(0.65);
    transform-origin: bottom;
  }
}
</style>
