<template>
  <section id="hero" class="hero-section">
    <!-- Ambient Background Gradients & Grid -->
    <div class="ambient-glow glow-navy" aria-hidden="true"></div>
    <div class="ambient-glow glow-orange" aria-hidden="true"></div>
    <div class="grid-overlay" aria-hidden="true"></div>

    <div class="hero-container">
      <!-- Left Column: Copy & CTAs -->
      <div class="hero-copy">
        <!-- Pill-shaped Badge -->
        <div class="hero-badge">
          <svg class="w-4 h-4 text-orange" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
          </svg>
          <span class="badge-dot"></span>
          <span>{{ t.hero.badge }}</span>
        </div>

        <!-- Main Headline -->
        <h1 class="hero-title">
          {{ t.hero.titlePart1 }}<span class="text-orange">{{ t.hero.titleSmarter }}</span>{{ t.hero.titlePart2 }}<span class="text-orange">{{ t.hero.titleBrand }}</span>
        </h1>

        <!-- Supporting Paragraph -->
        <p class="hero-subtitle">
          {{ t.hero.subtitle }}
        </p>

        <!-- CTA Buttons -->
        <div class="hero-cta-group">
          <a href="#contact" class="btn btn-hero-primary" @click.prevent="emitScroll('contact')">
            <span>{{ t.hero.primaryCta }}</span>
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </a>

          <button type="button" class="btn btn-hero-secondary" @click="isOpenDemoModal = true">
            <span class="play-icon-box">
              <svg class="w-3.5 h-3.5 fill-current text-white" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </span>
            <span>{{ t.hero.secondaryCta }}</span>
          </button>
        </div>

        <!-- Four Compact Benefits with Small Icons -->
        <div class="hero-benefits-grid">
          <div class="benefit-chip">
            <div class="benefit-icon bg-orange-soft text-orange">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span>{{ t.hero.benefits.easy }}</span>
          </div>

          <div class="benefit-chip">
            <div class="benefit-icon bg-navy-soft text-navy">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span>{{ t.hero.benefits.secure }}</span>
          </div>

          <div class="benefit-chip">
            <div class="benefit-icon bg-orange-soft text-orange">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span>{{ t.hero.benefits.multiDevice }}</span>
          </div>

          <div class="benefit-chip">
            <div class="benefit-icon bg-navy-soft text-navy">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span>{{ t.hero.benefits.support }}</span>
          </div>
        </div>
      </div>

      <!-- Right Column: Dual Device Mockup (Laptop + Overlapping Smartphone) -->
      <div class="hero-visual">
        <!-- Laptop / Desktop Mockup Frame -->
        <div class="laptop-wrapper">
          <div class="mockup-frame">
            <!-- Window Title Bar -->
            <div class="mockup-header">
              <div class="mockup-dots">
                <span class="dot dot-red"></span>
                <span class="dot dot-yellow"></span>
                <span class="dot dot-green"></span>
              </div>
              <div class="mockup-search-bar">
                <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span>https://sems.somroyal.com/admin/dashboard</span>
              </div>
              <div class="mockup-badge">{{ t.hero.previewBadge }}</div>
            </div>

            <!-- Laptop Screen Body -->
            <div class="mockup-body">
              <div class="mini-app-layout">
                <!-- Navy Sidebar -->
                <div class="mini-sidebar">
                  <div class="mini-brand">
                    <img src="/somroyal-logo-transparent.png" alt="Somroyal Logo" class="mini-brand-img" />
                  </div>
                  <div class="mini-nav-list">
                    <div class="mini-nav-item active">
                      <span class="mini-nav-dot active"></span> Dashboard
                    </div>
                    <div class="mini-nav-item">
                      <span class="mini-nav-dot"></span> Students
                    </div>
                    <div class="mini-nav-item">
                      <span class="mini-nav-dot"></span> Classes & Streams
                    </div>
                    <div class="mini-nav-item">
                      <span class="mini-nav-dot"></span> Exams & Grading
                    </div>
                    <div class="mini-nav-item">
                      <span class="mini-nav-dot"></span> Fee Invoicing
                    </div>
                    <div class="mini-nav-item">
                      <span class="mini-nav-dot"></span> Hormuud SMS
                    </div>
                  </div>
                </div>

                <!-- Main Content Canvas -->
                <div class="mini-content">
                  <!-- Topbar with Academic Year Selector -->
                  <div class="mini-topbar">
                    <div>
                      <h4 class="mini-welcome">{{ t.hero.previewHeading }}</h4>
                      <p class="mini-sub">Academic Session: <span class="font-bold text-navy">2026/2027</span> &bull; Banadir Central</p>
                    </div>
                    <div class="mini-year-selector">
                      <span class="year-label">Session:</span>
                      <span class="year-val">2026/2027 ▼</span>
                    </div>
                  </div>

                  <!-- 4 Summary KPI Cards -->
                  <div class="mini-kpi-grid">
                    <div class="mini-kpi-card">
                      <div class="kpi-label">Active Students</div>
                      <div class="kpi-value text-navy">1,420</div>
                      <div class="kpi-trend text-orange">↑ 100% verified</div>
                    </div>
                    <div class="mini-kpi-card">
                      <div class="kpi-label">Faculty Staff</div>
                      <div class="kpi-value text-orange">86</div>
                      <div class="kpi-trend text-slate-500">All Depts Assigned</div>
                    </div>
                    <div class="mini-kpi-card">
                      <div class="kpi-label">Active Classes</div>
                      <div class="kpi-value text-navy">21 Streams</div>
                      <div class="kpi-trend text-slate-500">G1-8 & Form 1-4</div>
                    </div>
                    <div class="mini-kpi-card">
                      <div class="kpi-label">Fee Collection</div>
                      <div class="kpi-value text-orange">$42,850</div>
                      <div class="kpi-trend text-slate-500">EVC, ZAAD, Cash</div>
                    </div>
                  </div>

                  <!-- Charts & Recent Activities Grid -->
                  <div class="mini-split-grid">
                    <!-- Chart Box -->
                    <div class="mini-chart-box">
                      <div class="chart-header">
                        <span>Mid-Term Exam Performance</span>
                        <span class="text-xs text-orange font-bold">Passing: 94.2%</span>
                      </div>
                      <div class="bar-chart-preview">
                        <div class="bar-item">
                          <div class="bar-fill bar-orange" style="height: 85%;"></div>
                          <span>Grade A</span>
                        </div>
                        <div class="bar-item">
                          <div class="bar-fill bar-navy" style="height: 65%;"></div>
                          <span>Grade B</span>
                        </div>
                        <div class="bar-item">
                          <div class="bar-fill bar-navy" style="height: 45%;"></div>
                          <span>Grade C</span>
                        </div>
                        <div class="bar-item">
                          <div class="bar-fill bar-muted" style="height: 20%;"></div>
                          <span>Grade D</span>
                        </div>
                      </div>
                    </div>

                    <!-- Activities Stream -->
                    <div class="mini-activity-box">
                      <div class="activity-header">Real-Time Event Stream</div>
                      <div class="activity-stream">
                        <div class="activity-row">
                          <span class="act-dot bg-orange"></span>
                          <div class="act-info">
                            <span class="act-title">Exam Marks Approved</span>
                            <span class="act-time">Form 4 &bull; Mathematics</span>
                          </div>
                        </div>
                        <div class="activity-row">
                          <span class="act-dot bg-navy"></span>
                          <div class="act-info">
                            <span class="act-title">Hormuud SMS Broadcast</span>
                            <span class="act-time">106 Guardians Delivered</span>
                          </div>
                        </div>
                        <div class="activity-row">
                          <span class="act-dot bg-orange"></span>
                          <div class="act-info">
                            <span class="act-title">Fee Payment Logged</span>
                            <span class="act-time">EVC Plus &bull; $210.00</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            </div>
          </div>
          <!-- Laptop Base / Hinge Bar -->
          <div class="laptop-base">
            <div class="laptop-notch"></div>
          </div>
        </div>

        <!-- Realistic Overlapping Smartphone Mockup -->
        <div class="smartphone-mockup" aria-hidden="true">
          <div class="phone-outer-frame">
            <div class="phone-screen">
              <!-- Phone Status Bar -->
              <div class="phone-status-bar">
                <span class="phone-time">9:41</span>
                <div class="phone-island"></div>
                <div class="phone-status-icons">
                  <span class="status-bar-icon">5G</span>
                  <span class="status-bar-icon">100%</span>
                </div>
              </div>

              <!-- Phone Content -->
              <div class="phone-inner-content">
                <!-- App Header -->
                <div class="phone-app-header">
                  <div class="phone-brand-mark">
                    <span class="phone-brand-crown">👑</span>
                    <span class="phone-brand-text">SEMS Mobile</span>
                  </div>
                  <span class="phone-live-dot"></span>
                </div>

                <!-- Today Attendance Card -->
                <div class="phone-card phone-card-accent">
                  <div class="phone-card-label">Today's Attendance</div>
                  <div class="phone-card-val">99.4%</div>
                  <div class="phone-card-sub">SMS Alerts Synced ✓</div>
                </div>

                <!-- Today Schedule -->
                <div class="phone-card">
                  <div class="phone-schedule-title">Today's Timetable</div>
                  <div class="phone-schedule-item">
                    <span class="sched-time">08:30</span>
                    <span class="sched-name">Form 4 • Mathematics</span>
                  </div>
                  <div class="phone-schedule-item">
                    <span class="sched-time">10:15</span>
                    <span class="sched-name">Grade 8 • Biology</span>
                  </div>
                </div>

                <!-- Quick Action Pill -->
                <div class="phone-quick-action">
                  <svg class="w-3.5 h-3.5 text-orange" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span>Hormuud SMS Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Badge: Automated Transcripts -->
        <div class="floating-badge badge-top">
          <div class="badge-icon bg-orange-soft text-orange">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div>
            <div class="font-bold text-navy text-xs">Automated Transcripts</div>
            <div class="text-slate-500 text-2xs">Official School Seal Ready</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Highlights: 4 Compact Cards Strip at Bottom of Hero -->
    <div class="feature-highlights-wrapper">
      <div class="feature-highlights-container">
        <div
          v-for="(card, index) in t.hero.featureCards"
          :key="index"
          class="highlight-card"
        >
          <div class="highlight-icon-box" :class="index % 2 === 0 ? 'bg-orange-soft text-orange' : 'bg-navy-soft text-navy'">
            <!-- Student Management Icon -->
            <svg v-if="index === 0" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <!-- Academic Management Icon -->
            <svg v-else-if="index === 1" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <!-- Fees & Payments Icon -->
            <svg v-else-if="index === 2" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <!-- Guardian Communication Icon -->
            <svg v-else class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <div class="highlight-info">
            <h3 class="highlight-title">{{ card.title }}</h3>
            <p class="highlight-desc">{{ card.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Counter Ribbon -->
    <div class="stats-ribbon">
      <div class="stats-container">
        <div class="stat-card">
          <div class="stat-num text-navy">{{ t.hero.statStudents }}</div>
          <div class="stat-desc">{{ t.hero.statStudentsLabel }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-num text-orange">{{ t.hero.statAttendance }}</div>
          <div class="stat-desc">{{ t.hero.statAttendanceLabel }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-num text-navy">{{ t.hero.statClasses }}</div>
          <div class="stat-desc">{{ t.hero.statClassesLabel }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-num text-orange">{{ t.hero.statUptime }}</div>
          <div class="stat-desc">{{ t.hero.statUptimeLabel }}</div>
        </div>
      </div>
    </div>

    <!-- Interactive Watch Demo Modal -->
    <transition name="modal-fade">
      <div v-if="isOpenDemoModal" class="demo-modal-backdrop" @click="isOpenDemoModal = false">
        <div class="demo-modal-box" @click.stop>
          <div class="demo-modal-header">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-orange"></span>
              <h3 class="text-lg font-bold text-navy">Somroyal EMS Product Walkthrough</h3>
            </div>
            <button type="button" class="modal-close-btn" @click="isOpenDemoModal = false">✕</button>
          </div>

          <div class="demo-modal-body">
            <div class="demo-video-placeholder">
              <div class="video-overlay-content">
                <div class="video-big-play">
                  <svg class="w-8 h-8 fill-current text-white ml-1" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
                <h4 class="text-white font-bold text-lg mt-3">Interactive Guided Tour</h4>
                <p class="text-slate-300 text-sm max-w-md text-center mt-1">
                  Discover how Somroyal EMS automates school attendance, academic grading, fee collection via EVC Plus, and parent notifications.
                </p>
              </div>
            </div>

            <div class="demo-features-pills">
              <span class="demo-pill">✓ Multi-Campus Support</span>
              <span class="demo-pill">✓ Automatic Transcript Generator</span>
              <span class="demo-pill">✓ EVC Plus & ZAAD Billing</span>
              <span class="demo-pill">✓ Real-Time SMS Gateway</span>
            </div>
          </div>

          <div class="demo-modal-footer">
            <button type="button" class="btn btn-secondary-nav" @click="isOpenDemoModal = false">
              Close Preview
            </button>
            <a href="#contact" class="btn btn-hero-primary" @click="isOpenDemoModal = false; emitScroll('contact')">
              Book a Personalized Live Demo →
            </a>
          </div>
        </div>
      </div>
    </transition>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

const emit = defineEmits<{
  (e: 'scroll', target: string): void;
}>();

const isOpenDemoModal = ref(false);

function emitScroll(target: string) {
  emit('scroll', target);
}
</script>

<style scoped>
.hero-section {
  position: relative;
  padding-top: 130px;
  padding-bottom: 40px;
  background: radial-gradient(circle at 50% 0%, #F7F9FC 0%, #FFFFFF 100%);
  overflow: hidden;
}

/* Ambient Glow Accents */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  opacity: 0.35;
  z-index: 0;
}

.glow-navy {
  top: -100px;
  right: -80px;
  width: 520px;
  height: 520px;
  background: #0B1F4B;
}

.glow-orange {
  top: 20%;
  left: -120px;
  width: 420px;
  height: 420px;
  background: #FF6B00;
  opacity: 0.18;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(to right, rgba(11, 31, 75, 0.04) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(11, 31, 75, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.hero-container {
  position: relative;
  z-index: 1;
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 clamp(1rem, 2vw, 1.5rem);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.18fr);
  gap: clamp(1.5rem, 3.2vw, 3.8rem);
  align-items: center;
}

/* Copy Column */
.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #FFF7ED;
  border: 1px solid #FFEDD5;
  color: #FF6B00;
  font-size: 0.775rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.4rem 0.9rem;
  border-radius: 20px;
  width: fit-content;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #FF6B00;
}

.hero-title {
  font-family: 'Outfit', sans-serif;
  font-size: clamp(2.3rem, 3.8vw, 3.35rem);
  font-weight: 800;
  line-height: 1.15;
  color: #071735;
  letter-spacing: -0.025em;
  word-break: normal;
}

.text-orange {
  color: #FF6B00;
}

.text-navy {
  color: #0B1F4B;
}

.bg-orange {
  background-color: #FF6B00;
}

.bg-navy {
  background-color: #0B1F4B;
}

.bg-orange-soft {
  background-color: #FFF7ED;
}

.bg-navy-soft {
  background-color: #F0F4FA;
}

.hero-subtitle {
  font-size: 1.075rem;
  line-height: 1.65;
  color: #586983;
}

/* CTAs */
.hero-cta-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding-top: 0.25rem;
}

.btn-hero-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem clamp(1.2rem, 1.6vw, 1.85rem);
  font-size: clamp(0.9rem, 0.95vw, 1rem);
  font-weight: 700;
  color: #ffffff;
  background: #FF6B00;
  border-radius: 10px;
  box-shadow: 0 8px 24px -4px rgba(255, 107, 0, 0.35);
  transition: all 0.25s ease;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -4px rgba(255, 107, 0, 0.45);
  background: #E85D00;
  color: #ffffff;
}

.btn-hero-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.85rem clamp(1.1rem, 1.4vw, 1.65rem);
  font-size: clamp(0.9rem, 0.95vw, 1rem);
  font-weight: 600;
  color: #0B1F4B;
  background: #ffffff;
  border: 1px solid #D9E2EC;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  cursor: pointer;
}

.btn-hero-secondary:hover {
  background: #F7F9FC;
  border-color: #FF6B00;
  color: #FF6B00;
}

.play-icon-box {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #FF6B00;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Benefits Grid (4 items) */
.hero-benefits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #EAF0F8;
}

.benefit-chip {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #12264A;
}

.benefit-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Right Mockup: Dual Device */
.hero-visual {
  position: relative;
  perspective: 1200px;
  min-width: 0;
  width: 100%;
}

.laptop-wrapper {
  position: relative;
  width: 100%;
}

.mockup-frame {
  background: #ffffff;
  border-radius: 16px 16px 4px 4px;
  border: 1px solid rgba(217, 226, 236, 0.9);
  box-shadow: 0 24px 60px -12px rgba(11, 31, 75, 0.18),
              0 8px 24px -6px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: transform 0.4s ease, box-shadow 0.4s ease;
  width: 100%;
}

.laptop-base {
  height: 12px;
  background: linear-gradient(180deg, #D9E2EC 0%, #9FB3C8 100%);
  border-radius: 0 0 16px 16px;
  box-shadow: 0 10px 24px rgba(11, 31, 75, 0.15);
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.laptop-notch {
  width: 70px;
  height: 4px;
  background: #829AB1;
  border-radius: 0 0 4px 4px;
}

.mockup-header {
  height: 38px;
  background: #F7F9FC;
  border-bottom: 1px solid #EAF0F8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
}

.mockup-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot-red { background: #ef4444; }
.dot-yellow { background: #f59e0b; }
.dot-green { background: #10b981; }

.mockup-search-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #EAF0F8;
  padding: 2px 14px;
  border-radius: 20px;
  font-size: 0.72rem;
  color: #586983;
  width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mockup-badge {
  font-size: 0.68rem;
  font-weight: 700;
  color: #FF6B00;
  background: #FFF7ED;
  padding: 2px 8px;
  border-radius: 10px;
}

/* Mockup Body Layout */
.mini-app-layout {
  display: grid;
  grid-template-columns: 155px 1fr;
  height: 360px;
  background: #F7F9FC;
}

.mini-sidebar {
  background: #071735;
  color: #ffffff;
  padding: 0.85rem 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.mini-brand {
  display: flex;
  align-items: center;
  padding: 0 0.25rem;
}

.mini-brand-img {
  height: 32px;
  width: auto;
  object-fit: contain;
}

.mini-nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.mini-nav-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  padding: 0.35rem 0.45rem;
  border-radius: 6px;
  color: #9FB3C8;
}

.mini-nav-item.active {
  background: rgba(255, 107, 0, 0.18);
  color: #FF6B00;
  font-weight: 700;
}

.mini-nav-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: currentColor;
}

.mini-nav-dot.active {
  background: #FF6B00;
}

/* Mini Content */
.mini-content {
  padding: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow: hidden;
}

.mini-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mini-welcome {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0B1F4B;
}

.mini-sub {
  font-size: 0.65rem;
  color: #586983;
}

.mini-year-selector {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.68rem;
  background: #FFFFFF;
  border: 1px solid #D9E2EC;
  padding: 2px 8px;
  border-radius: 6px;
}

.year-label {
  color: #586983;
}

.year-val {
  font-weight: 700;
  color: #FF6B00;
}

/* Mini KPI Grid */
.mini-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.45rem;
}

.mini-kpi-card {
  background: #ffffff;
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid #EAF0F8;
}

.kpi-label {
  font-size: 0.6rem;
  color: #586983;
  font-weight: 500;
}

.kpi-value {
  font-size: 1rem;
  font-weight: 800;
  margin: 2px 0;
}

.kpi-trend {
  font-size: 0.55rem;
  font-weight: 600;
}

/* Mini Split Grid */
.mini-split-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 0.55rem;
}

.mini-chart-box,
.mini-activity-box {
  background: #ffffff;
  padding: 0.55rem;
  border-radius: 8px;
  border: 1px solid #EAF0F8;
}

.chart-header,
.activity-header {
  font-size: 0.65rem;
  font-weight: 700;
  color: #0B1F4B;
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.bar-chart-preview {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 85px;
  padding-bottom: 2px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}

.bar-fill {
  width: 22px;
  border-radius: 4px 4px 0 0;
}

.bar-orange {
  background: linear-gradient(180deg, #FF8A3D 0%, #FF6B00 100%);
}

.bar-navy {
  background: linear-gradient(180deg, #1E3A8A 0%, #0B1F4B 100%);
}

.bar-muted {
  background: #CBD5E1;
}

.bar-item span {
  font-size: 0.55rem;
  color: #586983;
  font-weight: 600;
}

/* Activities Stream */
.activity-stream {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.activity-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.62rem;
}

.act-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.act-info {
  display: flex;
  flex-direction: column;
}

.act-title {
  font-weight: 600;
  color: #0B1F4B;
}

.act-time {
  font-size: 0.55rem;
  color: #586983;
}

/* Smartphone Mockup */
.smartphone-mockup {
  position: absolute;
  right: -24px;
  bottom: -32px;
  width: 195px;
  z-index: 3;
}

.phone-outer-frame {
  background: #071735;
  border-radius: 28px;
  padding: 7px;
  box-shadow: 0 20px 40px -10px rgba(11, 31, 75, 0.35),
              0 0 0 1px rgba(255, 255, 255, 0.2);
}

.phone-screen {
  background: #FFFFFF;
  border-radius: 22px;
  padding: 8px 10px 12px;
  overflow: hidden;
  box-shadow: inset 0 0 4px rgba(0, 0, 0, 0.05);
}

.phone-status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.55rem;
  font-weight: 700;
  color: #071735;
  margin-bottom: 6px;
}

.phone-island {
  width: 44px;
  height: 10px;
  background: #000000;
  border-radius: 8px;
}

.phone-status-icons {
  display: flex;
  gap: 3px;
  font-size: 0.5rem;
  color: #586983;
}

.phone-inner-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.phone-app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 4px;
  border-bottom: 1px solid #EAF0F8;
}

.phone-brand-mark {
  display: flex;
  align-items: center;
  gap: 4px;
}

.phone-brand-crown {
  font-size: 0.75rem;
}

.phone-brand-text {
  font-size: 0.65rem;
  font-weight: 700;
  color: #0B1F4B;
}

.phone-live-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FF6B00;
}

.phone-card {
  background: #F7F9FC;
  border: 1px solid #EAF0F8;
  border-radius: 8px;
  padding: 6px 8px;
}

.phone-card-accent {
  background: #FFF7ED;
  border-color: #FFEDD5;
}

.phone-card-label {
  font-size: 0.55rem;
  color: #586983;
}

.phone-card-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #FF6B00;
}

.phone-card-sub {
  font-size: 0.5rem;
  font-weight: 600;
  color: #12264A;
}

.phone-schedule-title {
  font-size: 0.55rem;
  font-weight: 700;
  color: #0B1F4B;
  margin-bottom: 3px;
}

.phone-schedule-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.52rem;
  padding: 2px 0;
  border-bottom: 1px dashed #EAF0F8;
  color: #586983;
}

.phone-schedule-item:last-child {
  border-bottom: none;
}

.sched-time {
  font-weight: 600;
  color: #0B1F4B;
}

.phone-quick-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: #071735;
  color: #FFFFFF;
  font-size: 0.55rem;
  font-weight: 600;
  padding: 4px 6px;
  border-radius: 6px;
}

/* Floating Badge */
.floating-badge {
  position: absolute;
  background: #ffffff;
  border: 1px solid #EAF0F8;
  border-radius: 12px;
  padding: 0.65rem 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  box-shadow: 0 12px 24px -4px rgba(11, 31, 75, 0.12);
  z-index: 2;
  animation: float 4s ease-in-out infinite alternate;
  white-space: nowrap;
  pointer-events: none;
}

.badge-top {
  top: -12px;
  right: -6px;
}

@media (max-width: 1240px) {
  .badge-top {
    right: 8px;
    top: -8px;
  }
}

.badge-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.text-2xs { font-size: 0.68rem; }

@keyframes float {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-8px); }
}

/* Feature Highlights (4 Cards Strip) */
.feature-highlights-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1320px;
  margin: 3.5rem auto 0;
  padding: 0 clamp(1rem, 2vw, 1.5rem);
}

.feature-highlights-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.highlight-card {
  background: #ffffff;
  border: 1px solid #EAF0F8;
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 4px 16px -2px rgba(11, 31, 75, 0.05);
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  transition: all 0.25s ease;
}

.highlight-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 24px -4px rgba(11, 31, 75, 0.12);
  border-color: #FF6B00;
}

.highlight-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.highlight-info {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.highlight-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #071735;
}

.highlight-desc {
  font-size: 0.85rem;
  color: #586983;
  line-height: 1.5;
}

/* Stats Ribbon */
.stats-ribbon {
  position: relative;
  z-index: 1;
  margin-top: 3.5rem;
  background: #ffffff;
  border-top: 1px solid #EAF0F8;
  border-bottom: 1px solid #EAF0F8;
  box-shadow: 0 4px 12px rgba(11, 31, 75, 0.03);
}

.stats-container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-num {
  font-family: 'Outfit', sans-serif;
  font-size: 2.35rem;
  font-weight: 800;
  line-height: 1.1;
}

.stat-desc {
  font-size: 0.875rem;
  font-weight: 600;
  color: #586983;
  margin-top: 0.25rem;
}

/* Demo Modal */
.demo-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(7, 23, 53, 0.7);
  backdrop-filter: blur(6px);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.demo-modal-box {
  background: #ffffff;
  border-radius: 18px;
  max-width: 680px;
  width: 100%;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
}

.demo-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #EAF0F8;
}

.modal-close-btn {
  background: #F7F9FC;
  border: none;
  font-size: 1.1rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #586983;
}

.demo-modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.demo-video-placeholder {
  position: relative;
  height: 280px;
  background: linear-gradient(135deg, #071735 0%, #0B1F4B 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.video-overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
}

.video-big-play {
  width: 64px;
  height: 64px;
  background: #FF6B00;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(255, 107, 0, 0.45);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.video-big-play:hover {
  transform: scale(1.08);
}

.demo-features-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.demo-pill {
  font-size: 0.8rem;
  font-weight: 600;
  color: #0B1F4B;
  background: #F0F4FA;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
}

.demo-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #EAF0F8;
  background: #F7F9FC;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Responsive Media Queries */
@media (max-width: 1100px) {
  .hero-container {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 3rem;
  }

  .hero-copy {
    align-items: center;
  }

  .hero-title {
    font-size: 2.6rem;
  }

  .hero-cta-group {
    justify-content: center;
  }

  .hero-benefits-grid {
    justify-content: center;
  }

  .feature-highlights-container {
    grid-template-columns: repeat(2, 1fr);
  }

  .floating-badge {
    display: none;
  }

  .smartphone-mockup {
    right: 10px;
    bottom: -20px;
  }
}

@media (max-width: 640px) {
  .hero-title {
    font-size: 2.15rem;
  }

  .hero-benefits-grid {
    grid-template-columns: 1fr;
  }

  .feature-highlights-container {
    grid-template-columns: 1fr;
  }

  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .smartphone-mockup {
    display: none;
  }

  .mini-app-layout {
    grid-template-columns: 1fr;
  }

  .mini-sidebar {
    display: none;
  }

  .mini-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .mini-split-grid {
    grid-template-columns: 1fr;
  }
}
</style>
