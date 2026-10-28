<template>
  <section id="benefits" class="benefits-section">
    <div class="benefits-container">
      <div class="section-header">
        <span class="section-badge">{{ t.benefits.badge }}</span>
        <h2 class="section-title">{{ t.benefits.title }}</h2>
        <p class="section-subtitle">{{ t.benefits.subtitle }}</p>
      </div>

      <div class="benefits-grid">
        <div v-for="benefit in benefitsList" :key="benefit.title" class="benefit-card">
          <div class="benefit-icon-wrapper" :class="benefit.color">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="benefit.iconPath" />
            </svg>
          </div>
          <h3 class="benefit-title">{{ benefit.title }}</h3>
          <p class="benefit-desc">{{ benefit.description }}</p>
          <div class="benefit-metric">
            <span class="metric-highlight">{{ benefit.metricValue }}</span>
            <span class="metric-note">{{ benefit.metricLabel }}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { TranslationContent } from '../translations';

defineProps<{
  t: TranslationContent;
}>();

interface BenefitItem {
  title: string;
  description: string;
  metricValue: string;
  metricLabel: string;
  color: string;
  iconPath: string;
}

const benefitsList = computed<BenefitItem[]>(() => [
  {
    title: 'Zero Paperwork & Single Source of Truth',
    description: 'Eliminate chaotic paper forms and conflicting spreadsheets. Every admission, fee payment, and exam mark is synchronized into an authoritative, searchable database.',
    metricValue: '100%',
    metricLabel: 'Paperless Records',
    color: 'bg-blue-50 text-blue-600',
    iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  },
  {
    title: 'Instant Absent Alerts & Guardian Trust',
    description: 'When students are marked absent during morning roll call, parents immediately receive automated SMS alerts via Hormuud, keeping families connected and accountable.',
    metricValue: '< 3s',
    metricLabel: 'SMS Dispatch Speed',
    color: 'bg-emerald-50 text-emerald-600',
    iconPath: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
  },
  {
    title: 'Effortless Examination & Digital Transcripts',
    description: 'Teachers input marks securely within their dedicated portal. Weighted score computations, letter grades, and official report cards are automatically compiled in seconds.',
    metricValue: '10x Faster',
    metricLabel: 'Grading Turnaround',
    color: 'bg-purple-50 text-purple-600',
    iconPath: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
  },
  {
    title: 'Complete Financial Clarity & Fee Tracking',
    description: 'Track outstanding balances, tuition billing, and recorded vouchers (EVC Plus, ZAAD, Sahal, Cash) with real-time balance computation and verified receipts.',
    metricValue: 'Zero Mismatch',
    metricLabel: 'Cashflow Auditing',
    color: 'bg-amber-50 text-amber-600',
    iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    title: 'Cross-Device Portals for Every Role',
    description: 'Administrators, faculty teachers, and students access role-tailored dashboards seamlessly from desktop workstations, classroom laptops, or mobile smartphones.',
    metricValue: 'Any Device',
    metricLabel: 'Desktop, Tablet & Phone',
    color: 'bg-sky-50 text-sky-600',
    iconPath: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  },
  {
    title: 'Bank-Grade Security & Institutional Telemetry',
    description: 'Enforce JWT tokens, session lifecycle expiration, encrypted passwords, and detailed immutable audit trails for every grade change or fee receipt creation.',
    metricValue: '100% Audited',
    metricLabel: 'Tamper-Resistant Security',
    color: 'bg-teal-50 text-teal-600',
    iconPath: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  },
]);
</script>

<style scoped>
.benefits-section {
  padding: 80px 0;
  background-color: #f8fafc;
}

.benefits-container {
  max-width: 1280px;
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
  color: #1d4ed8;
  background: #eff6ff;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: 'Outfit', sans-serif;
  font-size: 2.35rem;
  font-weight: 800;
  color: #0f2b5c;
  line-height: 1.25;
  margin-bottom: 0.75rem;
}

.section-subtitle {
  font-size: 1.05rem;
  color: #64748b;
  line-height: 1.6;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.75rem;
}

.benefit-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.benefit-card:hover {
  transform: translateY(-4px);
  border-color: #cbd5e1;
  box-shadow: 0 16px 32px -4px rgba(15, 43, 92, 0.08);
}

.benefit-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.benefit-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f2b5c;
  margin-bottom: 0.65rem;
  line-height: 1.35;
}

.benefit-desc {
  font-size: 0.925rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

.benefit-metric {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.metric-highlight {
  font-family: 'Outfit', sans-serif;
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f2b5c;
}

.metric-note {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

@media (max-width: 1024px) {
  .benefits-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}
</style>
