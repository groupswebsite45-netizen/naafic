<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import {
  formMasterService,
  type FormMasterClassSummary,
  type FormMasterFeesData,
} from '../../../services/formMasterService';

const loading = ref(false);
const errorMsg = ref('');
const myClasses = ref<FormMasterClassSummary[]>([]);
const selectedClassId = ref<number | null>(null);
const feesData = ref<FormMasterFeesData | null>(null);

// Status filter
const statusFilter = ref<'ALL' | 'OVERDUE' | 'UNPAID' | 'PARTIALLY_PAID' | 'PAID'>('ALL');
const searchQuery = ref('');

// Student Details Modal
const selectedStudent = ref<any | null>(null);
const showStudentModal = ref(false);

onMounted(async () => {
  await loadClasses();
});

watch(selectedClassId, async (newId) => {
  if (newId) {
    await loadFees(newId);
  }
});

async function loadClasses() {
  loading.value = true;
  errorMsg.value = '';
  try {
    const classes = await formMasterService.getMyClasses();
    myClasses.value = classes;
    if (classes.length > 0) {
      selectedClassId.value = classes[0].id;
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load assigned classes.';
  } finally {
    loading.value = false;
  }
}

async function loadFees(classId: number) {
  loading.value = true;
  errorMsg.value = '';
  try {
    const data = await formMasterService.getFees(classId);
    feesData.value = data;
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Failed to load fee records.';
  } finally {
    loading.value = false;
  }
}

const filteredStudents = computed(() => {
  if (!feesData.value) return [];
  return feesData.value.students.filter((s) => {
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase();
      const matchName = s.name.toLowerCase().includes(q);
      const matchAdm = s.admission_number.toLowerCase().includes(q);
      if (!matchName && !matchAdm) return false;
    }

    if (statusFilter.value === 'OVERDUE') {
      return s.is_overdue;
    }
    if (statusFilter.value !== 'ALL' && s.status !== statusFilter.value) {
      return false;
    }

    return true;
  });
});

function openStudentDetails(student: any) {
  selectedStudent.value = student;
  showStudentModal.value = true;
}
</script>

<template>
  <div class="fees-monitoring-view">
    <!-- Header -->
    <header class="page-header">
      <div class="header-main">
        <div class="title-wrap">
          <div class="icon-wrap bg-orange-subtle text-orange">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h1 class="page-title">Student Fees Monitoring</h1>
              <span class="badge badge-read-only">READ-ONLY FINANCIAL SUPERVISION</span>
            </div>
            <p class="page-subtitle">
              Monitor student fee payments and outstanding balances for your assigned form class.
            </p>
          </div>
        </div>

        <!-- Class Picker -->
        <div v-if="myClasses.length > 1" class="class-picker">
          <span class="picker-label">Class:</span>
          <select v-model="selectedClassId" class="picker-select">
            <option v-for="c in myClasses" :key="c.id" :value="c.id">
              {{ c.name }} ({{ c.division }})
            </option>
          </select>
        </div>
      </div>

      <!-- Financial Authority Disclaimer -->
      <div class="financial-disclaimer">
        <svg class="h-5 w-5 text-amber flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>
          <strong>Important Financial Policy:</strong> Form Masters have read-only access to fee information to assist in academic coordination. Form Masters must not collect tuition or fee payments, issue receipts, or modify transactions unless separately authorized by School Finance &amp; Administration.
        </span>
      </div>
    </header>

    <!-- Error State -->
    <div v-if="errorMsg" class="alert alert-error">
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>Loading fee balances and invoice records...</p>
    </div>

    <!-- Main Content -->
    <div v-else-if="feesData" class="fees-body">
      <!-- Fee Statistics Cards -->
      <div class="stat-grid">
        <div class="card">
          <span class="card-label">Total Invoiced</span>
          <span class="card-val">${{ feesData.summary.total_invoiced }}</span>
          <span class="card-sub">{{ feesData.summary.total_students }} students</span>
        </div>

        <div class="card">
          <span class="card-label">Total Collected</span>
          <span class="card-val text-green">${{ feesData.summary.total_paid }}</span>
          <span class="card-sub">{{ feesData.summary.paid_students_count }} fully paid</span>
        </div>

        <div class="card">
          <span class="card-label">Outstanding Balance</span>
          <span class="card-val text-orange">${{ feesData.summary.total_outstanding }}</span>
          <span class="card-sub">{{ feesData.summary.partially_paid_students_count + feesData.summary.unpaid_students_count }} students with balance</span>
        </div>

        <div class="card">
          <span class="card-label">Overdue Balances</span>
          <span class="card-val text-red">{{ feesData.summary.overdue_students_count }}</span>
          <span class="card-sub">Students past due date</span>
        </div>
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="toolbar-card">
        <div class="search-wrap">
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Search by student name or admission #..."
          />
        </div>

        <div class="filter-pills">
          <button
            type="button"
            class="pill-btn"
            :class="{ active: statusFilter === 'ALL' }"
            @click="statusFilter = 'ALL'"
          >
            All
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: statusFilter === 'OVERDUE' }"
            @click="statusFilter = 'OVERDUE'"
          >
            Overdue ({{ feesData.summary.overdue_students_count }})
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: statusFilter === 'UNPAID' }"
            @click="statusFilter = 'UNPAID'"
          >
            Unpaid ({{ feesData.summary.unpaid_students_count }})
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: statusFilter === 'PARTIALLY_PAID' }"
            @click="statusFilter = 'PARTIALLY_PAID'"
          >
            Partial ({{ feesData.summary.partially_paid_students_count }})
          </button>
          <button
            type="button"
            class="pill-btn"
            :class="{ active: statusFilter === 'PAID' }"
            @click="statusFilter = 'PAID'"
          >
            Fully Paid ({{ feesData.summary.paid_students_count }})
          </button>
        </div>
      </div>

      <!-- Students Fee Table -->
      <div class="table-card">
        <table class="data-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Admission #</th>
              <th>Guardian Contact</th>
              <th class="text-right">Total Due</th>
              <th class="text-right">Paid</th>
              <th class="text-right">Outstanding</th>
              <th>Status</th>
              <th class="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in filteredStudents"
              :key="s.student_id"
              :class="{ 'row-overdue': s.is_overdue }"
            >
              <td class="font-medium">
                {{ s.name }}
                <span v-if="s.is_overdue" class="badge-overdue ml-1">Overdue</span>
              </td>
              <td class="text-xs text-muted">{{ s.admission_number }}</td>
              <td class="text-xs text-muted">
                {{ s.guardian_name || 'Guardian' }} &bull; {{ s.guardian_phone || 'No phone' }}
              </td>
              <td class="text-right font-medium">${{ s.total_due }}</td>
              <td class="text-right text-green font-medium">${{ s.total_paid }}</td>
              <td class="text-right font-bold" :class="s.balance > 0 ? 'text-red' : 'text-slate-400'">
                ${{ s.balance }}
              </td>
              <td>
                <span
                  class="status-badge"
                  :class="{
                    'status-paid': s.status === 'PAID',
                    'status-partial': s.status === 'PARTIALLY_PAID',
                    'status-unpaid': s.status === 'UNPAID',
                    'status-nofees': s.status === 'NO_FEES',
                  }"
                >
                  {{ s.status }}
                </span>
              </td>
              <td class="text-right">
                <button
                  type="button"
                  class="btn btn-sm btn-outline"
                  @click="openStudentDetails(s)"
                >
                  View Invoices
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Student Invoices & Payment History Modal -->
    <div v-if="showStudentModal && selectedStudent" class="modal-backdrop" @click.self="showStudentModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">{{ selectedStudent.name }} &mdash; Fee Records</h2>
            <p class="modal-subtitle">Admission: {{ selectedStudent.admission_number }} &bull; Class: {{ feesData?.class_name }}</p>
          </div>
          <button type="button" class="close-x-btn" @click="showStudentModal = false">&times;</button>
        </div>

        <div class="modal-body">
          <!-- Summary Banner -->
          <div class="student-fee-banner">
            <div>
              <span class="text-xs text-muted">Total Due:</span>
              <strong class="text-sm block">${{ selectedStudent.total_due }}</strong>
            </div>
            <div>
              <span class="text-xs text-muted">Amount Paid:</span>
              <strong class="text-sm text-green block">${{ selectedStudent.total_paid }}</strong>
            </div>
            <div>
              <span class="text-xs text-muted">Balance:</span>
              <strong class="text-sm text-red block">${{ selectedStudent.balance }}</strong>
            </div>
            <div>
              <span class="text-xs text-muted">Status:</span>
              <span class="status-badge status-paid block">{{ selectedStudent.status }}</span>
            </div>
          </div>

          <!-- Invoices Section -->
          <h3 class="section-heading">Assigned Invoices</h3>
          <div v-if="selectedStudent.invoices.length === 0" class="empty-sub">
            No active invoices assigned.
          </div>
          <table v-else class="modal-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Fee Type</th>
                <th>Due Date</th>
                <th class="text-right">Due</th>
                <th class="text-right">Paid</th>
                <th class="text-right">Balance</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in selectedStudent.invoices" :key="inv.invoice_number">
                <td class="font-mono text-xs">{{ inv.invoice_number }}</td>
                <td>{{ inv.fee_type }}</td>
                <td class="text-xs">{{ inv.due_date || '—' }}</td>
                <td class="text-right font-medium">${{ inv.amount_due }}</td>
                <td class="text-right text-green font-medium">${{ inv.amount_paid }}</td>
                <td class="text-right font-bold text-red">${{ inv.balance }}</td>
                <td><span class="status-badge status-partial">{{ inv.status }}</span></td>
              </tr>
            </tbody>
          </table>

          <!-- Payment History Section -->
          <h3 class="section-heading mt-4">Verified Payment Receipts</h3>
          <div v-if="selectedStudent.payments.length === 0" class="empty-sub">
            No payments recorded yet.
          </div>
          <table v-else class="modal-table">
            <thead>
              <tr>
                <th>Receipt #</th>
                <th>Date</th>
                <th>Method</th>
                <th class="text-right">Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in selectedStudent.payments" :key="p.receipt_number">
                <td class="font-mono text-xs">{{ p.receipt_number }}</td>
                <td>{{ p.payment_date }}</td>
                <td>{{ p.payment_method }}</td>
                <td class="text-right font-bold text-green">${{ p.amount }}</td>
                <td><span class="status-badge status-paid">{{ p.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showStudentModal = false">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fees-monitoring-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-orange-subtle { background: #fff7ed; }
.text-orange { color: #ff6500; }
.text-green { color: #16a34a; }
.text-red { color: #dc2626; }
.text-amber { color: #d97706; }

.page-title {
  font-size: 1.375rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.page-subtitle {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.badge-read-only {
  font-size: 0.6875rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  background: #fff7ed;
  color: #c2410c;
  border: 1px solid #fed7aa;
}

.financial-disclaimer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: 8px;
  font-size: 0.8125rem;
  color: #92400e;
}

.class-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.picker-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
}

.picker-select {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
}

/* Stat Grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.card {
  padding: 1.25rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
}

.card-val {
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0.25rem 0 0.125rem;
}

.card-sub {
  font-size: 0.6875rem;
  color: #94a3b8;
}

/* Toolbar */
.toolbar-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  flex-wrap: wrap;
}

.search-wrap {
  flex: 1 1 240px;
  max-width: 360px;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  outline: none;
}

.search-input:focus {
  border-color: #ff6500;
}

.filter-pills {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.pill-btn {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
}

.pill-btn.active {
  background: #ff6500;
  border-color: #ff6500;
  color: #ffffff;
}

/* Table Card */
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th {
  padding: 0.875rem 1rem;
  background: #f8fafc;
  font-weight: 700;
  font-size: 0.6875rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.data-table tr.row-overdue td {
  background: #fffbfb;
}

.badge-overdue {
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.1rem 0.375rem;
  border-radius: 4px;
  background: #fee2e2;
  color: #b91c1c;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
}

.status-paid { background: #dcfce7; color: #166534; }
.status-partial { background: #fef3c7; color: #92400e; }
.status-unpaid { background: #fee2e2; color: #991b1b; }
.status-nofees { background: #f1f5f9; color: #64748b; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
}

.btn-outline {
  border-color: #cbd5e1;
  background: #ffffff;
  color: #334155;
}

.btn-outline:hover {
  border-color: #ff6500;
  color: #ff6500;
}

.btn-secondary {
  background: #f1f5f9;
  color: #334155;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-box {
  background: #ffffff;
  border-radius: 14px;
  width: 100%;
  max-width: 640px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.close-x-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.student-fee-banner {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  padding: 0.875rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.section-heading {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0.5rem 0 0.25rem;
}

.empty-sub {
  font-size: 0.8125rem;
  color: #94a3b8;
  font-style: italic;
  padding: 0.5rem 0;
}

.modal-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.modal-table th {
  padding: 0.5rem 0.75rem;
  background: #f8fafc;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #e2e8f0;
}

.modal-table td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #64748b;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #ff6500;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.75rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

