<template>
  <div class="public-home-page">
    <!-- Navigation Bar -->
    <PublicNavbar
      :t="currentTranslations"
      :current-lang="currentLanguage"
      @update:language="handleLanguageChange"
    />

    <!-- Main Public Content Sections -->
    <main id="main-content">
      <HeroSection
        :t="currentTranslations"
        @scroll="scrollToSection"
      />

      <FeaturesSection
        :t="currentTranslations"
      />

      <AboutSection
        :t="currentTranslations"
      />

      <BenefitsSection
        :t="currentTranslations"
      />

      <HowItWorksSection
        :t="currentTranslations"
      />

      <PricingSection
        :t="currentTranslations"
        @select-plan="handlePlanSelection"
      />

      <CtaSection
        :t="currentTranslations"
        @scroll="scrollToSection"
      />

      <ContactSection
        :t="currentTranslations"
        :selected-plan="selectedPlanForInquiry"
      />
    </main>

    <!-- Public Footer -->
    <PublicFooter
      :t="currentTranslations"
      @scroll="scrollToSection"
      @open-privacy="isOpenPrivacy = true"
      @open-terms="isOpenTerms = true"
    />

    <!-- Legal Modals -->
    <LegalModals
      :is-open-privacy="isOpenPrivacy"
      :is-open-terms="isOpenTerms"
      @close-privacy="isOpenPrivacy = false"
      @close-terms="isOpenTerms = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { translations, Language } from './translations';

import PublicNavbar from './components/PublicNavbar.vue';
import HeroSection from './components/HeroSection.vue';
import FeaturesSection from './components/FeaturesSection.vue';
import AboutSection from './components/AboutSection.vue';
import BenefitsSection from './components/BenefitsSection.vue';
import HowItWorksSection from './components/HowItWorksSection.vue';
import PricingSection from './components/PricingSection.vue';
import CtaSection from './components/CtaSection.vue';
import ContactSection from './components/ContactSection.vue';
import PublicFooter from './components/PublicFooter.vue';
import LegalModals from './components/LegalModals.vue';

const currentLanguage = ref<Language>('en');
const currentTranslations = computed(() => translations[currentLanguage.value]);

const selectedPlanForInquiry = ref('Professional School');
const isOpenPrivacy = ref(false);
const isOpenTerms = ref(false);

function handleLanguageChange(lang: Language) {
  currentLanguage.value = lang;
}

function scrollToSection(id: string) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
}

function handlePlanSelection(planName: string) {
  selectedPlanForInquiry.value = planName;
  scrollToSection('contact');
}
</script>

<style scoped>
.public-home-page {
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  color: #0f172a;
}

#main-content {
  flex: 1;
  width: 100%;
  overflow-x: hidden;
}
</style>
