<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import StatusBadge from '../common/StatusBadge.vue'
import { feeService } from '../../services/feeService'
import type { StudentFinancialProfile } from '../../types/fee'

interface Props {
  isOpen: boolean
  studentId: number | null
  academicYear?: string | null
  initialProfile?: StudentFinancialProfile | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:isOpen', value: boolean): void
}>()

const profile = ref<StudentFinancialProfile | null>(props.initialProfile || null)
const isLoading = ref(false)
const errorMessage = ref('')

// Watch for modal open and studentId changes
watch(
  () => [props.isOpen, props.studentId, props.academicYear],
  async ([isOpen, studentId]) => {
    if (isOpen && studentId) {
      await fetchProfile(studentId as number)
    } else if (!isOpen) {
      errorMessage.value = ''
    }
  },
  { immediate: true }
)

// Also update profile if initialProfile prop changes
watch(
  () => props.initialProfile,
  (newProfile) => {
    if (newProfile) {
      profile.value = newProfile
    }
  }
)

async function fetchProfile(studentId: number) {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await feeService.getStudentFinancialProfile(
      studentId,
      props.academicYear || undefined
    )
    profile.value = data
  } catch (err: any) {
    console.error('Failed to load student financial profile', err)
    if (err.response?.status === 404) {
      errorMessage.value = 'Student financial profile not found in database.'
    } else if (err.response?.status === 403) {
      errorMessage.value = 'You are not authorized to view this student profile.'
    } else {
      errorMessage.value = 'Unable to load financial profile. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

function handleRetry() {
  if (props.studentId) {
    fetchProfile(props.studentId)
  }
}

function closeModal() {
  emit('close')
  emit('update:isOpen', false)
}

function handleBackdropClick(e: MouseEvent) {
  if (e.target === e.currentTarget) {
    closeModal()
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.isOpen) {
    closeModal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// Calculations & Helpers
const studentInitials = computed(() => {
  const name = profile.value?.student_name || profile.value?.full_name || ''
  if (!name.trim()) return 'ST'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})

const studentFullName = computed(() => {
  return profile.value?.student_name || profile.value?.full_name || 'Student Financial Profile'
})

const totalBilled = computed(() => {
  if (!profile.value) return 0
  return Number(
    profile.value.total_billed ??
    profile.value.financial_summary?.total_billed ??
    0
  )
})

const totalPaid = computed(() => {
  if (!profile.value) return 0
  return Number(
    profile.value.total_paid ??
    profile.value.financial_summary?.total_paid ??
    0
  )
})

const outstandingBalance = computed(() => {
  if (!profile.value) return 0
  return Number(
    profile.value.outstanding_balance ??
    profile.value.financial_summary?.outstanding_balance ??
    0
  )
})

const overdueBalance = computed(() => {
  if (!profile.value) return 0
  return Number(
    profile.value.overdue_balance ??
    profile.value.financial_summary?.overdue_balance ??
    0
  )
})

const invoicesCount = computed(() => {
  return profile.value?.invoices?.length || 0
})

const paymentsCount = computed(() => {
  return profile.value?.payments?.length || 0
})

const paidPercentage = computed(() => {
  if (totalBilled.value <= 0) {
    return totalPaid.value > 0 ? 100 : 0
  }
  return Math.min(100, Math.max(0, Math.round((totalPaid.value / totalBilled.value) * 100)))
})

const outstandingPercentage = computed(() => {
  if (totalBilled.value <= 0) return 0
  return Math.max(0, 100 - paidPercentage.value)
})

const overdueInvoices = computed(() => {
  if (!profile.value?.invoices) return []
  return profile.value.invoices.filter((inv) => {
    const s = (inv.status || '').toUpperCase()
    return s === 'OVERDUE'
  })
})

const lastUpdatedFormatted = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
})

function formatMoney(amount: number | string | null | undefined): string {
  const num = Number(amount ?? 0)
  if (isNaN(num)) return '$0.00'
  return `$${num.toFixed(2)}`
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—'
  try {
    const cleanStr = dateStr.split('T')[0]
    const parts = cleanStr.split('-')
    if (parts.length === 3) {
      const year = parseInt(parts[0], 10)
      const month = parseInt(parts[1], 10) - 1
      const day = parseInt(parts[2], 10)
      const d = new Date(year, month, day)
      return d.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      })
    }
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function formatPaymentMethod(method: string | null | undefined): string {
  if (!method) return '—'
  const m = method.toUpperCase().replace(/\s+/g, '_')
  const map: Record<string, string> = {
    EVC_PLUS: 'EVC Plus',
    EVC: 'EVC Plus',
    EDAHAB: 'eDahab',
    ZAAD: 'ZAAD',
    SAHAL: 'Sahal',
    CASH: 'Cash',
    BANK_TRANSFER: 'Bank Transfer',
    BANK: 'Bank Transfer',
  }
  return map[m] || method
}

function getInvoiceStatusVariant(status: string | null | undefined): 'success' | 'warning' | 'danger' | 'info' | 'neutral' {
  const s = (status || '').toUpperCase()
  if (s === 'PAID') return 'success'
  if (s === 'PARTIALLY_PAID' || s === 'PARTIAL') return 'warning'
  if (s === 'OVERDUE') return 'danger'
  if (s === 'CANCELLED') return 'neutral'
  return 'info' // PENDING / UNPAID
}
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="handleBackdropClick" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-dialog-premium" @click.stop>
      <!-- MODAL HEADER -->
      <div class="modal-header-premium">
        <div class="header-left">
          <div class="header-icon-badge">💰</div>
          <div class="header-titles">
            <h2 id="modal-title" class="header-title">Student Financial Profile</h2>
            <p class="header-subtitle">Complete Financial Ledger & Billing History</p>
          </div>
        </div>
        <button
          type="button"
          class="modal-close-btn"
          @click="closeModal"
          aria-label="Close financial profile modal"
        >
          <span aria-hidden="true">&times;</span>
        </button>
      </div>

      <!-- MODAL BODY -->
      <div class="modal-body-premium">
        <!-- LOADING SKELETON STATE -->
        <div v-if="isLoading" class="skeleton-container" aria-busy="true">
          <div class="skeleton-card skeleton-identity">
            <div class="skeleton-avatar pulse"></div>
            <div class="skeleton-text-group">
              <div class="skeleton-line pulse w-60 h-24"></div>
              <div class="skeleton-line pulse w-40 h-16"></div>
              <div class="skeleton-grid">
                <div class="skeleton-line pulse w-30 h-14"></div>
                <div class="skeleton-line pulse w-30 h-14"></div>
                <div class="skeleton-line pulse w-30 h-14"></div>
              </div>
            </div>
          </div>
          <div class="skeleton-kpis-grid">
            <div v-for="i in 4" :key="i" class="skeleton-card pulse h-100"></div>
          </div>
          <div class="skeleton-card pulse h-200"></div>
        </div>

        <!-- ERROR STATE -->
        <div v-else-if="errorMessage" class="error-container">
          <div class="error-card">
            <div class="error-icon">⚠️</div>
            <h3 class="error-title">Unable to load financial profile</h3>
            <p class="error-desc">{{ errorMessage }}</p>
            <div class="error-actions">
              <button type="button" class="btn btn-primary" @click="handleRetry">
                Retry Loading
              </button>
              <button type="button" class="btn btn-outline" @click="closeModal">
                Close
              </button>
            </div>
          </div>
        </div>

        <!-- REAL DATA LOADED CONTENT -->
        <div v-else-if="profile" class="profile-content-wrap">
          <!-- 1. STUDENT IDENTITY CARD -->
          <div class="student-identity-card">
            <div class="identity-top-row">
              <div class="identity-main">
                <div class="student-avatar" aria-hidden="true">
                  {{ studentInitials }}
                </div>
                <div class="student-names">
                  <div class="name-status-row">
                    <h3 class="student-name">{{ studentFullName }}</h3>
                    <StatusBadge
                      :status="profile.status || 'ACTIVE'"
                      :variant="(profile.status || 'ACTIVE').toUpperCase() === 'ACTIVE' ? 'success' : 'neutral'"
                    />
                  </div>
                  <div class="student-admission">
                    Admission # <strong>{{ profile.admission_number || 'N/A' }}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div class="identity-divider"></div>

            <div class="identity-details-grid">
              <div class="identity-meta-cell">
                <span class="meta-label">CLASS</span>
                <span class="meta-value">{{ profile.class_name || profile.current_class || 'Unassigned' }}</span>
              </div>
              <div class="identity-meta-cell">
                <span class="meta-label">LEVEL</span>
                <span class="meta-badge-level">{{ profile.education_level || 'PRIMARY' }}</span>
              </div>
              <div class="identity-meta-cell">
                <span class="meta-label">ACADEMIC YEAR</span>
                <span class="meta-value">{{ profile.academic_year || '2026/2027' }}</span>
              </div>
              <div class="identity-meta-cell">
                <span class="meta-label">GUARDIAN</span>
                <span class="meta-value">
                  <template v-if="profile.guardian_name || profile.guardian_phone">
                    {{ profile.guardian_name || 'Guardian' }}
                    <span v-if="profile.guardian_phone" class="guardian-sep">• {{ profile.guardian_phone }}</span>
                  </template>
                  <template v-else>
                    <span class="text-muted">Not specified</span>
                  </template>
                </span>
              </div>
            </div>
          </div>

          <!-- 2. FINANCIAL SUMMARY CARDS (4 CARDS) -->
          <div class="financial-cards-grid">
            <!-- TOTAL BILLED -->
            <div class="kpi-card kpi-billed">
              <div class="kpi-top">
                <span class="kpi-icon" aria-hidden="true">💳</span>
                <span class="kpi-label">TOTAL BILLED</span>
              </div>
              <div class="kpi-amount">{{ formatMoney(totalBilled) }}</div>
              <div class="kpi-subtext">{{ invoicesCount }} {{ invoicesCount === 1 ? 'invoice' : 'invoices' }}</div>
            </div>

            <!-- TOTAL PAID -->
            <div class="kpi-card kpi-paid">
              <div class="kpi-top">
                <span class="kpi-icon" aria-hidden="true">💰</span>
                <span class="kpi-label">TOTAL PAID</span>
              </div>
              <div class="kpi-amount text-success">{{ formatMoney(totalPaid) }}</div>
              <div class="kpi-subtext">
                {{ paymentsCount > 0 ? `${paymentsCount} ${paymentsCount === 1 ? 'payment recorded' : 'payments recorded'}` : 'No payments yet' }}
              </div>
            </div>

            <!-- OUTSTANDING -->
            <div class="kpi-card kpi-outstanding">
              <div class="kpi-top">
                <span class="kpi-icon" aria-hidden="true">⏳</span>
                <span class="kpi-label">OUTSTANDING</span>
              </div>
              <div class="kpi-amount text-warning">{{ formatMoney(outstandingBalance) }}</div>
              <div class="kpi-subtext">Current unpaid balance</div>
            </div>

            <!-- OVERDUE -->
            <div :class="['kpi-card', 'kpi-overdue', overdueBalance > 0 ? 'kpi-overdue-alert' : 'kpi-overdue-clean']">
              <div class="kpi-top">
                <span class="kpi-icon" aria-hidden="true">{{ overdueBalance > 0 ? '⚠️' : '✓' }}</span>
                <span class="kpi-label">OVERDUE</span>
              </div>
              <div :class="['kpi-amount', overdueBalance > 0 ? 'text-danger' : 'text-neutral']">
                {{ formatMoney(overdueBalance) }}
              </div>
              <div class="kpi-subtext">
                {{ overdueBalance > 0 ? `${overdueInvoices.length} overdue invoice(s)` : 'No overdue fees' }}
              </div>
            </div>
          </div>

          <!-- 3. FINANCIAL STATUS SUMMARY & PROGRESS BAR -->
          <div class="financial-progress-card">
            <div class="progress-header">
              <div class="progress-title-block">
                <span class="progress-card-title">Financial Status</span>
                <span class="progress-card-subtitle">Collection progress breakdown</span>
              </div>
              <div class="progress-stats-summary">
                <div class="summary-pill">
                  <span class="summary-label">Billed</span>
                  <span class="summary-val">{{ formatMoney(totalBilled) }}</span>
                </div>
                <div class="summary-pill text-success">
                  <span class="summary-label">Paid</span>
                  <span class="summary-val">{{ formatMoney(totalPaid) }} ({{ paidPercentage }}%)</span>
                </div>
                <div class="summary-pill text-warning">
                  <span class="summary-label">Outstanding</span>
                  <span class="summary-val">{{ formatMoney(outstandingBalance) }} ({{ outstandingPercentage }}%)</span>
                </div>
              </div>
            </div>

            <!-- Visual Progress Bar -->
            <div class="progress-bar-track" role="progressbar" :aria-valuenow="paidPercentage" aria-valuemin="0" aria-valuemax="100">
              <div
                class="progress-fill-paid"
                :style="{ width: `${paidPercentage}%` }"
                :title="`Paid: ${paidPercentage}%`"
              ></div>
              <div
                class="progress-fill-outstanding"
                :style="{ width: `${outstandingPercentage}%` }"
                :title="`Outstanding: ${outstandingPercentage}%`"
              ></div>
            </div>

            <div class="progress-legend">
              <div class="legend-item">
                <span class="legend-dot dot-paid"></span>
                <span>Paid: <strong>{{ paidPercentage }}%</strong></span>
              </div>
              <div class="legend-item">
                <span class="legend-dot dot-outstanding"></span>
                <span>Outstanding: <strong>{{ outstandingPercentage }}%</strong></span>
              </div>
            </div>
          </div>

          <!-- 4. OVERDUE NOTICE SECTION (CONDITIONAL) -->
          <div v-if="overdueBalance > 0" class="overdue-notice-card alert-danger">
            <div class="notice-icon">⚠️</div>
            <div class="notice-body">
              <div class="notice-title">
                Overdue Balance: <strong>{{ formatMoney(overdueBalance) }}</strong>
              </div>
              <p class="notice-desc">
                This student has {{ overdueInvoices.length }} past-due fee invoice(s) that have exceeded their official due dates.
              </p>
            </div>
          </div>
          <div v-else class="overdue-notice-card alert-clean">
            <div class="notice-icon text-success">✓</div>
            <div class="notice-body">
              <div class="notice-title text-success">No overdue balance</div>
              <p class="notice-desc">All issued invoices are within their permissible payment terms or fully cleared.</p>
            </div>
          </div>

          <!-- 5. FEE INVOICES SECTION -->
          <div class="ledger-section">
            <div class="section-heading-row">
              <div>
                <h4 class="section-title">Fee Invoices · {{ invoicesCount }}</h4>
                <p class="section-desc">Itemized fee structures assigned and balance calculations</p>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="invoicesCount === 0" class="empty-state-box">
              <div class="empty-icon">📄</div>
              <h5 class="empty-title">No fee invoices</h5>
              <p class="empty-desc">No fee invoices have been created for this student yet.</p>
            </div>

            <!-- Invoices Ledger Content -->
            <div v-else>
              <!-- Desktop Table -->
              <div class="table-responsive desktop-only">
                <table class="premium-table">
                  <thead>
                    <tr>
                      <th class="nowrap">Invoice #</th>
                      <th>Fee Type</th>
                      <th class="text-right">Amount</th>
                      <th class="text-right">Paid</th>
                      <th class="text-right">Balance</th>
                      <th class="nowrap">Due Date</th>
                      <th class="text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="inv in profile.invoices" :key="inv.id">
                      <td class="cell-mono font-bold nowrap">{{ inv.invoice_number }}</td>
                      <td class="font-medium">{{ inv.fee_type || inv.fee_name || 'School Fee' }}</td>
                      <td class="text-right font-medium">{{ formatMoney(inv.net_amount ?? inv.amount_due) }}</td>
                      <td class="text-right font-medium text-success">{{ formatMoney(inv.total_paid ?? inv.paid) }}</td>
                      <td class="text-right font-bold" :class="Number(inv.balance_remaining ?? inv.balance) > 0 ? 'text-danger' : 'text-success'">
                        {{ formatMoney(inv.balance_remaining ?? inv.balance) }}
                      </td>
                      <td class="cell-date nowrap">{{ formatDate(inv.due_date) }}</td>
                      <td class="text-center nowrap">
                        <StatusBadge
                          :status="inv.status"
                          :variant="getInvoiceStatusVariant(inv.status)"
                        />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Mobile Responsive Cards -->
              <div class="mobile-only invoice-card-list">
                <div v-for="inv in profile.invoices" :key="inv.id" class="mobile-record-card">
                  <div class="mobile-card-top">
                    <span class="cell-mono font-bold">{{ inv.invoice_number }}</span>
                    <StatusBadge
                      :status="inv.status"
                      :variant="getInvoiceStatusVariant(inv.status)"
                    />
                  </div>
                  <div class="mobile-card-title">{{ inv.fee_type || inv.fee_name || 'School Fee' }}</div>
                  <div class="mobile-card-grid">
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Amount:</span>
                      <span class="cell-val">{{ formatMoney(inv.net_amount ?? inv.amount_due) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Paid:</span>
                      <span class="cell-val text-success">{{ formatMoney(inv.total_paid ?? inv.paid) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Balance:</span>
                      <span class="cell-val font-bold text-danger">{{ formatMoney(inv.balance_remaining ?? inv.balance) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Due:</span>
                      <span class="cell-val">{{ formatDate(inv.due_date) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. VERIFIED PAYMENT TRANSACTIONS -->
          <div class="ledger-section">
            <div class="section-heading-row">
              <div>
                <h4 class="section-title">Payment Transactions · {{ paymentsCount }}</h4>
                <p class="section-desc">Verified receipts and recorded payment settlements</p>
              </div>
            </div>

            <!-- Empty State for Payments -->
            <div v-if="paymentsCount === 0" class="empty-state-box empty-payments-box">
              <div class="empty-icon">💳</div>
              <h5 class="empty-title">No payment transactions</h5>
              <p class="empty-desc">No verified payments have been recorded for this student yet.</p>
            </div>

            <!-- Payments Table Content -->
            <div v-else>
              <!-- Desktop Table -->
              <div class="table-responsive desktop-only">
                <table class="premium-table">
                  <thead>
                    <tr>
                      <th class="nowrap">Payment #</th>
                      <th class="nowrap">Date</th>
                      <th class="text-right">Amount</th>
                      <th>Payment Method</th>
                      <th>Reference</th>
                      <th>Recorded By</th>
                      <th class="text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pay in profile.payments" :key="pay.id">
                      <td class="cell-mono font-bold nowrap">{{ pay.receipt_number || `PAY-${pay.id}` }}</td>
                      <td class="cell-date nowrap">{{ formatDate(pay.payment_date) }}</td>
                      <td class="text-right font-bold text-success">{{ formatMoney(pay.amount_paid ?? pay.amount) }}</td>
                      <td>
                        <span class="method-tag">{{ formatPaymentMethod(pay.payment_method) }}</span>
                      </td>
                      <td class="cell-mono text-muted">{{ pay.reference_number || pay.reference || '—' }}</td>
                      <td>{{ pay.recorded_by_name || 'Admin' }}</td>
                      <td class="text-center nowrap">
                        <StatusBadge
                          :status="pay.status || 'VERIFIED'"
                          :variant="(pay.status || 'VERIFIED').toUpperCase() === 'VERIFIED' ? 'success' : 'neutral'"
                        />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Mobile Responsive Cards -->
              <div class="mobile-only payment-card-list">
                <div v-for="pay in profile.payments" :key="pay.id" class="mobile-record-card">
                  <div class="mobile-card-top">
                    <span class="cell-mono font-bold">{{ pay.receipt_number || `PAY-${pay.id}` }}</span>
                    <StatusBadge
                      :status="pay.status || 'VERIFIED'"
                      :variant="(pay.status || 'VERIFIED').toUpperCase() === 'VERIFIED' ? 'success' : 'neutral'"
                    />
                  </div>
                  <div class="mobile-card-grid">
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Date:</span>
                      <span class="cell-val">{{ formatDate(pay.payment_date) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Amount:</span>
                      <span class="cell-val text-success font-bold">{{ formatMoney(pay.amount_paid ?? pay.amount) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Method:</span>
                      <span class="cell-val">{{ formatPaymentMethod(pay.payment_method) }}</span>
                    </div>
                    <div class="mobile-grid-cell">
                      <span class="cell-lbl">Ref:</span>
                      <span class="cell-val cell-mono">{{ pay.reference_number || pay.reference || '—' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL FOOTER -->
      <div class="modal-footer-premium">
        <div class="footer-left">
          <span class="footer-timestamp">
            Financial record • Last updated: <strong>{{ lastUpdatedFormatted }}</strong>
          </span>
        </div>
        <div class="footer-right">
          <button type="button" class="btn btn-secondary" @click="closeModal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =========================================================================
   1. BACKDROP & DIALOG ARCHITECTURE
   ========================================================================= */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  overflow-y: auto;
}

.modal-dialog-premium {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25);
  width: 100%;
  max-width: 1150px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  animation: modalFadeIn 200ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.97) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* =========================================================================
   2. HEADER
   ========================================================================= */
.modal-header-premium {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.75rem;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.header-icon-badge {
  font-size: 1.5rem;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 10px;
}

.header-titles {
  display: flex;
  flex-direction: column;
}

.header-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
}

.header-subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: #64748b;
}

.modal-close-btn {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
  transition: all 150ms ease;
}

.modal-close-btn:hover,
.modal-close-btn:focus-visible {
  background: #f1f5f9;
  color: #0f172a;
  outline: 2px solid #3b82f6;
}

/* =========================================================================
   3. BODY & SCROLL REGION
   ========================================================================= */
.modal-body-premium {
  padding: 1.75rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: #f8fafc;
}

/* =========================================================================
   4. STUDENT IDENTITY CARD
   ========================================================================= */
.student-identity-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.identity-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.identity-main {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.student-avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(2, 132, 199, 0.25);
}

.student-names {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.name-status-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.student-name {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.student-admission {
  font-size: 0.9rem;
  color: #64748b;
}

.student-admission strong {
  color: #334155;
  font-family: monospace;
  font-size: 0.95rem;
}

.identity-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 1.25rem 0;
}

.identity-details-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.identity-meta-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.meta-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.meta-value {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e293b;
}

.meta-badge-level {
  display: inline-block;
  align-self: flex-start;
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  font-weight: 700;
  border-radius: 6px;
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #dbeafe;
}

.guardian-sep {
  color: #64748b;
  font-weight: 400;
}

/* =========================================================================
   5. FINANCIAL SUMMARY CARDS (4-GRID)
   ========================================================================= */
.financial-cards-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.kpi-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
}

.kpi-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
}

.kpi-icon {
  font-size: 1.15rem;
}

.kpi-label {
  font-size: 0.725rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.kpi-amount {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
  margin-bottom: 0.35rem;
}

.kpi-subtext {
  font-size: 0.8rem;
  color: #64748b;
}

.kpi-billed {
  border-left: 4px solid #3b82f6;
}

.kpi-paid {
  border-left: 4px solid #10b981;
  background: #fcfdfd;
}

.kpi-outstanding {
  border-left: 4px solid #f59e0b;
}

.kpi-overdue-clean {
  border-left: 4px solid #94a3b8;
}

.kpi-overdue-alert {
  border-left: 4px solid #ef4444;
  background: #fff8f8;
}

/* =========================================================================
   6. FINANCIAL STATUS SUMMARY & PROGRESS BAR
   ========================================================================= */
.financial-progress-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.progress-title-block {
  display: flex;
  flex-direction: column;
}

.progress-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.progress-card-subtitle {
  font-size: 0.8rem;
  color: #64748b;
}

.progress-stats-summary {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.summary-pill {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  background: #f1f5f9;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  font-weight: 600;
}

.summary-label {
  color: #64748b;
  font-weight: 500;
}

.summary-val {
  font-weight: 700;
}

.progress-bar-track {
  width: 100%;
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
}

.progress-fill-paid {
  background: #10b981;
  height: 100%;
  transition: width 400ms cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-fill-outstanding {
  background: #f59e0b;
  height: 100%;
  transition: width 400ms cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-legend {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 0.8rem;
  color: #475569;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-paid {
  background: #10b981;
}

.dot-outstanding {
  background: #f59e0b;
}

/* =========================================================================
   7. OVERDUE NOTICES
   ========================================================================= */
.overdue-notice-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 10px;
}

.overdue-notice-card.alert-danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
}

.overdue-notice-card.alert-clean {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.notice-icon {
  font-size: 1.35rem;
  flex-shrink: 0;
}

.notice-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.notice-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #991b1b;
}

.overdue-notice-card.alert-clean .notice-title {
  color: #166534;
}

.notice-desc {
  margin: 0;
  font-size: 0.85rem;
  color: #7f1d1d;
}

.overdue-notice-card.alert-clean .notice-desc {
  color: #15803d;
}

/* =========================================================================
   8. LEDGER SECTIONS & TABLES
   ========================================================================= */
.ledger-section {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-heading-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.section-desc {
  margin: 0.2rem 0 0 0;
  font-size: 0.8rem;
  color: #64748b;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.premium-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}

.premium-table thead {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.premium-table th {
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
}

.premium-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
}

.premium-table tbody tr:last-child td {
  border-bottom: none;
}

.premium-table tbody tr:hover {
  background: #f8fafc;
}

.cell-mono {
  font-family: monospace;
  font-size: 0.875rem;
  color: #334155;
}

.cell-date {
  color: #475569;
  font-size: 0.85rem;
}

.method-tag {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #334155;
  font-weight: 600;
  font-size: 0.775rem;
}

.nowrap {
  white-space: nowrap;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.text-success {
  color: #10b981;
}

.text-warning {
  color: #d97706;
}

.text-danger {
  color: #dc2626;
}

.text-neutral {
  color: #64748b;
}

.text-muted {
  color: #94a3b8;
}

.font-bold {
  font-weight: 700;
}

.font-medium {
  font-weight: 500;
}

/* =========================================================================
   9. EMPTY STATES
   ========================================================================= */
.empty-state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1.5rem;
  text-align: center;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px dashed #cbd5e1;
}

.empty-icon {
  font-size: 2.2rem;
  margin-bottom: 0.75rem;
}

.empty-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.35rem 0;
}

.empty-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  max-width: 380px;
}

/* =========================================================================
   10. MOBILE CARDS (Hidden on Desktop)
   ========================================================================= */
.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

.mobile-record-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-bottom: 0.75rem;
}

.mobile-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.mobile-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.mobile-card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 8px;
}

.mobile-grid-cell {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.cell-lbl {
  font-size: 0.7rem;
  color: #64748b;
  text-transform: uppercase;
}

.cell-val {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
}

/* =========================================================================
   11. FOOTER
   ========================================================================= */
.modal-footer-premium {
  padding: 1rem 1.75rem;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.footer-timestamp {
  font-size: 0.85rem;
  color: #64748b;
}

.footer-timestamp strong {
  color: #334155;
}

/* =========================================================================
   12. SKELETON & ERROR STATES
   ========================================================================= */
.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.skeleton-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
}

.skeleton-identity {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}

.skeleton-avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: #e2e8f0;
}

.skeleton-text-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 0.5rem;
}

.skeleton-line {
  background: #e2e8f0;
  border-radius: 4px;
}

.skeleton-kpis-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.w-60 { width: 60%; }
.w-40 { width: 40%; }
.w-30 { width: 30%; }
.h-14 { height: 14px; }
.h-16 { height: 16px; }
.h-24 { height: 24px; }
.h-100 { height: 100px; }
.h-200 { height: 200px; }

.pulse {
  animation: skeletonPulse 1.5s ease-in-out infinite;
}

@keyframes skeletonPulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.3; }
  100% { opacity: 0.6; }
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
}

.error-card {
  background: #ffffff;
  border: 1px solid #fecaca;
  border-radius: 14px;
  padding: 2rem;
  max-width: 450px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.error-icon {
  font-size: 2.5rem;
}

.error-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #991b1b;
}

.error-desc {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
}

.error-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

/* =========================================================================
   13. RESPONSIVE BREAKPOINTS
   ========================================================================= */
@media (max-width: 1024px) {
  .financial-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .modal-backdrop {
    padding: 0.5rem;
  }

  .modal-dialog-premium {
    max-height: 96vh;
    border-radius: 12px;
  }

  .modal-header-premium {
    padding: 1rem 1.25rem;
  }

  .header-icon-badge {
    width: 36px;
    height: 36px;
    font-size: 1.25rem;
  }

  .modal-body-premium {
    padding: 1rem;
    gap: 1.25rem;
  }

  .identity-top-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .identity-details-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: block;
  }

  .financial-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .kpi-amount {
    font-size: 1.4rem;
  }

  .progress-stats-summary {
    flex-direction: column;
    align-items: flex-start;
    width: 100%;
  }

  .summary-pill {
    width: 100%;
    justify-content: space-between;
  }

  .modal-footer-premium {
    padding: 0.75rem 1rem;
    flex-direction: column-reverse;
    gap: 0.75rem;
    align-items: stretch;
  }

  .footer-left {
    text-align: center;
  }

  .footer-right .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .identity-details-grid {
    grid-template-columns: 1fr;
  }

  .financial-cards-grid {
    grid-template-columns: 1fr;
  }

  .student-name {
    font-size: 1.1rem;
  }
}
</style>
