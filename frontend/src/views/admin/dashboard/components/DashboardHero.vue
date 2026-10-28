<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  adminName?: string;
  academicYear?: string;
  academicYears?: string[];
  schoolName?: string;
  schoolCode?: string;
}

withDefaults(defineProps<Props>(), {
  adminName: 'Abdikadir Ali Mire',
  academicYear: '2026/2027',
  academicYears: () => ['2026/2027', '2025/2026'],
  schoolName: 'Garasale Primary School',
  schoolCode: 'SOM-SCH-0001',
});

const emit = defineEmits<{
  (e: 'update:academicYear', val: string): void;
}>();

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good Morning,';
  if (hour < 17) return 'Good Afternoon,';
  return 'Good Evening,';
});

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
});
</script>

<template>
  <section class="hero-banner-card" aria-label="Welcome and School Overview Banner">
    <!-- Abstract Wavy Background Vectors -->
    <svg class="wave-bg-overlay" viewBox="0 0 1000 240" fill="none" preserveAspectRatio="none">
      <path d="M0,160 C300,220 500,80 1000,140 L1000,240 L0,240 Z" fill="rgba(255, 255, 255, 0.03)" />
      <path d="M0,190 C400,120 700,240 1000,180 L1000,240 L0,240 Z" fill="rgba(255, 255, 255, 0.04)" />
      <path d="M0,130 C250,90 450,180 750,110 C900,75 950,120 1000,100" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1.5" fill="none" />
      <path d="M0,170 C350,140 600,210 1000,130" stroke="rgba(255, 255, 255, 0.05)" stroke-width="1.5" fill="none" />
    </svg>

    <div class="hero-content-wrap">
      <!-- Left Greeting & Description -->
      <div class="hero-left-col">
        <div class="greeting-pretitle">{{ greeting }}</div>
        <h1 class="admin-headline">
          <span class="admin-name">{{ adminName }}</span>
          <span class="wave-emoji" aria-label="Waving hand">👋</span>
        </h1>
        <p class="hero-subtext">
          Here's what's happening across {{ schoolName }} today.
        </p>

        <!-- School Code Badge & Academic Controls Row -->
        <div class="hero-pills-row">
          <!-- Frosted Glass School Badge -->
          <div class="school-glass-badge">
            <div class="school-icon-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 21h18M3 7v14M21 7v14M6 10h3M6 14h3M6 18h3M15 10h3M15 14h3M15 18h3M12 3L2 7h20L12 3z"/>
              </svg>
            </div>
            <div class="school-meta">
              <span class="school-name-text">{{ schoolName }}</span>
              <span class="school-code-text">{{ schoolCode }}</span>
            </div>
          </div>

          <!-- Date Badge -->
          <div class="glass-pill date-pill">
            <svg class="pill-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <span>{{ formattedDate }}</span>
          </div>

          <!-- Academic Year Selector -->
          <div class="academic-year-box">
            <span class="academic-label">Academic Year</span>
            <div class="year-select-pill">
              <select
                id="hero-academic-year"
                :value="academicYear"
                class="year-dropdown"
                @change="emit('update:academicYear', ($event.target as HTMLSelectElement).value)"
              >
                <option v-for="yr in academicYears" :key="yr" :value="yr">
                  {{ yr }}
                </option>
              </select>
              <svg class="dropdown-arrow" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Right 3D Isometric Miniature School Illustration -->
      <div class="hero-right-col">
        <div class="school-3d-scene">
          <!-- Soft Background Sun Glow & Clouds -->
          <div class="sun-glow" aria-hidden="true" />
          <img
            src="/school-3d-building.png"
            alt="3D Miniature School Building"
            class="school-3d-image"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-banner-card {
  position: relative;
  background: linear-gradient(135deg, #071E46 0%, #0D47A1 45%, #0284C7 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 12px 30px -6px rgba(7, 30, 70, 0.35);
  color: #FFFFFF;
}

.wave-bg-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.8;
}

.hero-content-wrap {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem 2.25rem;
  gap: 1.5rem;
}

/* Left Column */
.hero-left-col {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-width: 680px;
}

.greeting-pretitle {
  font-size: 1.1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.admin-headline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 2.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #FFFFFF;
  line-height: 1.2;
}

.wave-emoji {
  display: inline-block;
  animation: wave-animation 2.2s infinite;
  transform-origin: 70% 70%;
}

@keyframes wave-animation {
  0% { transform: rotate(0deg); }
  10% { transform: rotate(14deg); }
  20% { transform: rotate(-8deg); }
  30% { transform: rotate(14deg); }
  40% { transform: rotate(-4deg); }
  50% { transform: rotate(10deg); }
  60% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); }
}

.hero-subtext {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.85);
  margin: 0.2rem 0 1rem 0;
  font-weight: 400;
}

/* Metadata Row */
.hero-pills-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-top: 0.25rem;
}

/* School Frosted Glass Badge */
.school-glass-badge {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.45rem 0.95rem;
  border-radius: 12px;
}

.school-icon-circle {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
}

.school-icon-circle svg {
  width: 16px;
  height: 16px;
}

.school-meta {
  display: flex;
  flex-direction: column;
}

.school-name-text {
  font-size: 0.82rem;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.2;
}

.school-code-text {
  font-size: 0.68rem;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.05em;
}

/* Date Pill */
.glass-pill {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 0.45rem 0.85rem;
  border-radius: 12px;
  font-size: 0.82rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.95);
}

.pill-icon {
  width: 15px;
  height: 15px;
  color: rgba(255, 255, 255, 0.8);
}

/* Academic Year Controls */
.academic-year-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.academic-label {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.8);
}

.year-select-pill {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  padding: 0.35rem 0.65rem;
  transition: background-color 0.15s ease;
}

.year-select-pill:hover {
  background: rgba(255, 255, 255, 0.22);
}

.year-dropdown {
  appearance: none;
  background: transparent;
  border: none;
  outline: none;
  color: #FFFFFF;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  padding-right: 1.25rem;
}

.year-dropdown option {
  background-color: #0F172A;
  color: #FFFFFF;
}

.dropdown-arrow {
  position: absolute;
  right: 0.45rem;
  width: 14px;
  height: 14px;
  color: rgba(255, 255, 255, 0.8);
  pointer-events: none;
}

/* Right 3D Illustration Scene */
.hero-right-col {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.school-3d-scene {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
}

.sun-glow {
  position: absolute;
  top: -15px;
  right: -10px;
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, rgba(56, 189, 248, 0.15) 45%, rgba(2, 132, 199, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
}

.school-3d-image {
  width: 210px;
  height: auto;
  max-height: 120px;
  object-fit: contain;
  filter: drop-shadow(0 10px 16px rgba(0, 0, 0, 0.25));
  transition: transform 0.3s ease;
}

.school-3d-image:hover {
  transform: scale(1.04) translateY(-2px);
}

/* Responsive */
@media (max-width: 1024px) {
  .hero-content-wrap {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.5rem;
  }
  .hero-right-col {
    align-self: center;
    margin-top: 0.5rem;
  }
  .school-3d-image {
    width: 210px;
  }
}
</style>
