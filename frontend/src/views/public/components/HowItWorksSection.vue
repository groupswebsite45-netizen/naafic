<template>
  <section id="how-it-works" class="how-it-works-section">
    <div class="how-it-works-container">
      <div class="section-header">
        <span class="section-badge">{{ t.howItWorks.badge }}</span>
        <h2 class="section-title">{{ t.howItWorks.title }}</h2>
        <p class="section-subtitle">{{ t.howItWorks.subtitle }}</p>
      </div>

      <div class="steps-grid">
        <div class="step-card">
          <div class="step-badge">STEP 01</div>
          <div class="step-icon-box bg-orange-soft text-orange">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h3 class="step-title">{{ t.howItWorks.step1Title }}</h3>
          <p class="step-desc">{{ t.howItWorks.step1Desc }}</p>
        </div>

        <div class="step-card">
          <div class="step-badge">STEP 02</div>
          <div class="step-icon-box bg-navy-soft text-navy">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 class="step-title">{{ t.howItWorks.step2Title }}</h3>
          <p class="step-desc">{{ t.howItWorks.step2Desc }}</p>
        </div>

        <div class="step-card">
          <div class="step-badge">STEP 03</div>
          <div class="step-icon-box bg-orange-soft text-orange">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h3 class="step-title">{{ t.howItWorks.step3Title }}</h3>
          <p class="step-desc">{{ t.howItWorks.step3Desc }}</p>
        </div>

        <div class="step-card">
          <div class="step-badge">STEP 04</div>
          <div class="step-icon-box bg-navy-soft text-navy">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="step-title">{{ t.howItWorks.step4Title }}</h3>
          <p class="step-desc">{{ t.howItWorks.step4Desc }}</p>
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
</script>

<style scoped>
.how-it-works-section {
  padding: 85px 0;
  background-color: #ffffff;
}

.how-it-works-container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.section-header {
  text-align: center;
  max-width: 740px;
  margin: 0 auto 3.5rem;
}

.section-badge {
  display: inline-block;
  font-size: 0.775rem;
  font-weight: 700;
  color: #FF6B00;
  background: #FFF7ED;
  border: 1px solid #FFEDD5;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.35rem;
  font-weight: 800;
  color: #071735;
  line-height: 1.25;
  margin-bottom: 0.75rem;
}

.section-subtitle {
  font-size: 1.05rem;
  color: #586983;
  line-height: 1.6;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  position: relative;
}

.step-card {
  background: #F7F9FC;
  border: 1px solid #EAF0F8;
  border-radius: 14px;
  padding: 2rem 1.5rem;
  position: relative;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.step-card:hover {
  transform: translateY(-4px);
  border-color: #FF6B00;
  background: #ffffff;
  box-shadow: 0 16px 32px -4px rgba(11, 31, 75, 0.08);
}

.step-badge {
  font-family: 'Outfit', sans-serif;
  font-size: 0.72rem;
  font-weight: 800;
  color: #FF6B00;
  background: #FFF7ED;
  border: 1px solid #FFEDD5;
  padding: 3px 8px;
  border-radius: 6px;
  width: fit-content;
  margin-bottom: 1.25rem;
}

.step-icon-box {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  flex-shrink: 0;
}

.bg-orange-soft {
  background: #FFF7ED;
}

.text-orange {
  color: #FF6B00;
}

.bg-navy-soft {
  background: #F0F4FA;
}

.text-navy {
  color: #0B1F4B;
}

.step-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0B1F4B;
  margin-bottom: 0.65rem;
  line-height: 1.35;
}

.step-desc {
  font-size: 0.88rem;
  color: #586983;
  line-height: 1.6;
}

@media (max-width: 1024px) {
  .steps-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .steps-grid {
    grid-template-columns: 1fr;
  }
}
</style>
