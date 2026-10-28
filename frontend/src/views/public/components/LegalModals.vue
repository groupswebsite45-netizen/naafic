<template>
  <div>
    <!-- Privacy Policy Modal -->
    <transition name="modal-fade">
      <div v-if="isOpenPrivacy" class="modal-backdrop" @click="emit('close-privacy')">
        <div class="modal-window" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Institutional Privacy Policy</h3>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close-privacy')">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <h4>1. Data Sovereignty & Confidentiality</h4>
            <p>
              Somroyal Educational Management System (SEMS) is committed to protecting student academic records, teacher bio-data, guardian contact information, and institutional financial ledgers. All data is processed strictly for educational administration and is never shared, sold, or distributed to unauthorized third parties.
            </p>
            <h4>2. Role-Based Access Enforcement</h4>
            <p>
              User access is strictly partitioned according to verified institutional roles (Administrator, Educator, Student). Sensitive operations including grade approvals, tuition payment deletions, and bulk student promotions are logged immutably within the system audit trail.
            </p>
            <h4>3. Communications & SMS Safeguards</h4>
            <p>
              Mobile notifications dispatched via telecom gateways (such as Hormuud SMS) are limited to authorized academic notices including absent alerts, exam release alerts, and fee balance reminders.
            </p>
            <h4>4. Security Encryption</h4>
            <p>
              All portal authentications use industry-standard cryptographic tokenization (HS256 JWT) and HTTPS encrypted transport to prevent session interception or unauthorized access.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="emit('close-privacy')">Close Document</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Terms of Service Modal -->
    <transition name="modal-fade">
      <div v-if="isOpenTerms" class="modal-backdrop" @click="emit('close-terms')">
        <div class="modal-window" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">Terms of Service</h3>
            <button type="button" class="btn-close" aria-label="Close" @click="emit('close-terms')">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <h4>1. Authorized Educational Use</h4>
            <p>
              Access to Somroyal Educational Management System (SEMS) is granted to licensed schools, faculty members, and enrolled students for academic recordkeeping, attendance tracking, and grading administration.
            </p>
            <h4>2. Credential Confidentiality</h4>
            <p>
              Each user is responsible for safeguarding their login credentials. Passwords must adhere to institutional complexity requirements. Account sharing or unauthorized credential distribution is strictly prohibited.
            </p>
            <h4>3. Grade & Assessment Integrity</h4>
            <p>
              Teachers and administrators are responsible for the factual accuracy of assessment scores entered into the system. Official report card generation adheres to verified grading schemes established by the institution.
            </p>
            <h4>4. Service Availability & Support</h4>
            <p>
              Somroyal provides ongoing platform maintenance, secure automated database backups, and customer support according to the institution's active subscription tier.
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="emit('close-terms')">Accept & Close</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isOpenPrivacy: boolean;
  isOpenTerms: boolean;
}>();

const emit = defineEmits<{
  (e: 'close-privacy'): void;
  (e: 'close-terms'): void;
}>();
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-window {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f2b5c;
}

.btn-close {
  background: #f1f5f9;
  border: none;
  padding: 0.35rem;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
}

.modal-body {
  padding: 1.75rem;
  overflow-y: auto;
  font-size: 0.925rem;
  color: #334155;
  line-height: 1.65;
}

.modal-body h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #0f2b5c;
  margin-top: 1rem;
  margin-bottom: 0.35rem;
}

.modal-body h4:first-child {
  margin-top: 0;
}

.modal-body p {
  color: #64748b;
  margin-bottom: 1rem;
}

.modal-footer {
  padding: 1rem 1.75rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  background: #f8fafc;
}

.btn-primary {
  background: #0f2b5c;
  color: #ffffff;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
