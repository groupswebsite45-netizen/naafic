<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { feeService } from '../../../services/feeService'
import type {
  FeeStructure,
  FeeStructureCreate,
  StudentFeeInvoice,
  FeePayment,
  OfficialReceipt,
  FinancialDashboardSummary,
  ClassFinancialSummary,
  PaymentMethodBreakdown,
  MonthlyFinancialTrend,
  FeeSmsPreviewResponse,
  ClassStudentsFinancial,
  OutstandingStudentsSummary,
  FeeEligibleStudentsResponse,
} from '../../../types/fee'
import StatusBadge from '../../../components/common/StatusBadge.vue'
import StudentFinancialProfileModal from '../../../components/admin/StudentFinancialProfileModal.vue'

// ==========================================
// STATE MANAGEMENT & DATA MODELS
// ==========================================

const activeTab = ref<'students' | 'invoices' | 'structures' | 'payments' | 'classes' | 'outstanding' | 'overdue' | 'reports'>('students')
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Dropdowns & master data
const availableClasses = ref<any[]>([])
const availableStudents = ref<any[]>([])
const academicYears = ref<string[]>(['2026/2027', '2025/2026', '2024/2025'])

// Dedicated Tab 0: Fee-Eligible Students (Single Source of Truth)
const eligibleStudentsData = ref<FeeEligibleStudentsResponse>({
  total_eligible: 0,
  primary_count: 0,
  secondary_count: 0,
  without_class_count: 0,
  invoiced_count: 0,
  uninvoiced_count: 0,
  items: [],
})
const isEligibleStudentsLoading = ref(false)
const eligibleStudentStatusFilter = ref('')
const eligibleStudentSearch = ref('')

// Financial Summary KPIs (PostgreSQL authoritative)
const summary = ref<FinancialDashboardSummary>({
  total_billed: 0,
  total_collected: 0,
  total_outstanding: 0,
  total_overdue: 0,
  this_month_collected: 0,
  total_invoices_count: 0,
  paid_invoices_count: 0,
  partial_invoices_count: 0,
  unpaid_invoices_count: 0,
  overdue_invoices_count: 0,
  currency: 'USD',
  school_name: 'Education Management System',
})

// Tab 1: Invoices Ledger
const invoices = ref<StudentFeeInvoice[]>([])
const totalInvoicesCount = ref(0)
const invoicePage = ref(1)
const invoicePageSize = ref(15)

// Tab 2: Fee Structures
const feeStructures = ref<FeeStructure[]>([])
const structureStatusFilter = ref<'ALL' | 'ACTIVE' | 'ARCHIVED'>('ACTIVE')
const filteredFeeStructures = computed(() => {
  if (structureStatusFilter.value === 'ACTIVE') {
    return feeStructures.value.filter(s => s.status === 'ACTIVE')
  }
  if (structureStatusFilter.value === 'ARCHIVED') {
    return feeStructures.value.filter(s => s.status === 'INACTIVE')
  }
  return feeStructures.value
})

// Tab 3: Payments
const payments = ref<FeePayment[]>([])
const totalPaymentsCount = ref(0)
const paymentPage = ref(1)
const paymentPageSize = ref(15)

// Tab 4: Class Summaries & Enrolled Students
const classSummaries = ref<ClassFinancialSummary[]>([])
const selectedClassFinancial = ref<ClassStudentsFinancial | null>(null)
const isClassStudentsLoading = ref(false)

// Dedicated Tab: Outstanding / Unpaid Students
const outstandingData = ref<OutstandingStudentsSummary>({
  academic_year: '2026/2027',
  education_level: 'PRIMARY',
  class_id: null,
  total_students: 0,
  paid_count: 0,
  partial_count: 0,
  unpaid_count: 0,
  overdue_count: 0,
  total_outstanding_balance: 0,
  items: [],
})
const isOutstandingLoading = ref(false)
const outstandingStatusFilter = ref('ALL_OUTSTANDING')
const outstandingSearch = ref('')

// Tab 5: Overdue Invoices
const overdueInvoices = ref<StudentFeeInvoice[]>([])
const totalOverdueCount = ref(0)

// Tab 6: Reports & Breakdowns
const paymentMethodsBreakdown = ref<PaymentMethodBreakdown[]>([])
const monthlyTrends = ref<MonthlyFinancialTrend[]>([])

// Filters (Level-First Architecture)
const filters = reactive({
  search: '',
  academic_year: '2026/2027',
  education_level: 'PRIMARY' as 'PRIMARY' | 'SECONDARY',
  class_id: '' as string | number,
  status: '',
  fee_structure_id: '' as string | number,
  payment_method: '',
  start_date: '',
  end_date: '',
})

// ==========================================
// MODALS STATE
// ==========================================
const isStructureModalOpen = ref(false)
const isEditingStructure = ref(false)
const editingStructureId = ref<number | null>(null)

const isAssignModalOpen = ref(false)
const isPaymentModalOpen = ref(false)
const isReceiptModalOpen = ref(false)
const isStudentFinanceModalOpen = ref(false)
const isSmsModalOpen = ref(false)

// Delete structure confirm
const deleteConfirmStructure = ref<{ id: number; name: string; assigned_count: number } | null>(null)
const isDeleting = ref(false)

// Active selected records for modals
const selectedInvoiceForPayment = ref<StudentFeeInvoice | null>(null)
const currentReceipt = ref<OfficialReceipt | null>(null)
const selectedStudentIdForProfile = ref<number | null>(null)
const smsPreviewData = ref<FeeSmsPreviewResponse | null>(null)
const isSmsPreviewLoading = ref(false)

// Forms
const structureForm = reactive<FeeStructureCreate>({
  name: '',
  academic_year: '2026/2027',
  education_level: 'PRIMARY',
  class_id: null,
  class_ids: [],
  apply_to_all_in_level: true,
  amount: 20,
  frequency: 'Monthly',
  due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  description: '',
  status: 'ACTIVE',
})

const structureAvailableClasses = ref<any[]>([])
const structureClassSelectionMode = ref<'ALL' | 'SINGLE' | 'MULTIPLE'>('ALL')

const assignForm = reactive({
  target_type: 'CLASS' as 'SINGLE_STUDENT' | 'SELECTED_STUDENTS' | 'CLASS',
  fee_structure_id: 0,
  student_id: null as number | null,
  student_ids: [] as number[],
  class_id: null as number | null,
  academic_year: '2026/2027',
  custom_amount: null as number | null,
  custom_due_date: '',
})

const paymentForm = reactive({
  student_fee_id: 0,
  amount_paid: 0,
  payment_date: new Date().toISOString().split('T')[0],
  payment_method: 'EVC_PLUS' as any,
  reference_number: '',
  notes: '',
})

const smsForm = reactive({
  target_type: 'ALL_OVERDUE' as 'SINGLE_STUDENT' | 'SELECTED_STUDENTS' | 'CLASS' | 'ALL_OUTSTANDING' | 'ALL_OVERDUE',
  template_type: 'OVERDUE_FEE' as 'FEE_REMINDER' | 'OVERDUE_FEE' | 'PAYMENT_CONFIRMATION' | 'CUSTOM',
  class_id: null as number | null,
  student_id: null as number | null,
  custom_template: '',
})

// ==========================================
// COMPUTED CALCULATIONS
// ==========================================

const selectedStructureObj = computed(() => {
  return feeStructures.value.find((s) => s.id === assignForm.fee_structure_id) || null
})

const targetStudentsCount = computed(() => {
  if (assignForm.target_type === 'SINGLE_STUDENT') {
    return assignForm.student_id ? 1 : 0
  }
  if (assignForm.target_type === 'SELECTED_STUDENTS') {
    return assignForm.student_ids.length
  }
  if (assignForm.target_type === 'CLASS') {
    if (!assignForm.class_id) return 0
    const targetClass = availableClasses.value.find((c) => c.id === Number(assignForm.class_id))
    if (targetClass && targetClass.students_count !== undefined) {
      return targetClass.students_count
    }
    const inClass = availableStudents.value.filter((st) => {
      const clsId = st.class_id || st.current_enrollment?.class_id || st.current_class?.id
      return clsId === Number(assignForm.class_id)
    })
    return inClass.length
  }
  return 0
})

const unitFeeAmount = computed(() => {
  if (assignForm.custom_amount && assignForm.custom_amount > 0) {
    return Number(assignForm.custom_amount)
  }
  if (selectedStructureObj.value) {
    return Number(selectedStructureObj.value.amount)
  }
  return 0
})

const totalCalculatedBill = computed(() => {
  return targetStudentsCount.value * unitFeeAmount.value
})

// ==========================================
// DATA LOADING
// ==========================================

async function loadDropdowns() {
  try {
    const [cRes, sRes]: any = await Promise.all([
      feeService.getFeeClasses({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        has_students_only: true,
      }),
      feeService.getEligibleStudents({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        class_id: filters.class_id ? Number(filters.class_id) : undefined,
      }),
    ])
    availableClasses.value = Array.isArray(cRes) ? cRes : cRes?.items || []
    availableStudents.value = sRes?.items || []
  } catch (err) {
    console.error('Failed to load classes and students for fee module', err)
  }
}

async function loadEligibleStudents() {
  isEligibleStudentsLoading.value = true
  try {
    const res = await feeService.getEligibleStudents({
      academic_year: filters.academic_year || undefined,
      education_level: filters.education_level || undefined,
      class_id: filters.class_id ? Number(filters.class_id) : undefined,
      status: eligibleStudentStatusFilter.value || undefined,
      query: eligibleStudentSearch.value || undefined,
    })
    eligibleStudentsData.value = res
  } catch (err: any) {
    console.error('Failed to load eligible students from PostgreSQL', err)
  } finally {
    isEligibleStudentsLoading.value = false
  }
}

async function setEducationLevel(level: 'PRIMARY' | 'SECONDARY') {
  if (filters.education_level === level) return
  filters.education_level = level
  filters.class_id = ''
  selectedClassFinancial.value = null
  await loadDropdowns()
  await loadFinancialData()
}

async function loadClassStudentsFinancial(classId?: number) {
  const targetClassId = classId ?? (filters.class_id ? Number(filters.class_id) : null)
  if (!targetClassId) {
    selectedClassFinancial.value = null
    return
  }
  isClassStudentsLoading.value = true
  try {
    const res = await feeService.getClassStudentsFinancial(targetClassId, filters.academic_year || undefined)
    selectedClassFinancial.value = res
  } catch (err: any) {
    console.error('Failed to load class students financial breakdown', err)
    selectedClassFinancial.value = null
  } finally {
    isClassStudentsLoading.value = false
  }
}

async function loadOutstandingStudents() {
  isOutstandingLoading.value = true
  try {
    const res = await feeService.getOutstandingStudents({
      academic_year: filters.academic_year || undefined,
      education_level: filters.education_level || undefined,
      class_id: filters.class_id ? Number(filters.class_id) : undefined,
      status: outstandingStatusFilter.value === 'ALL_OUTSTANDING' ? undefined : outstandingStatusFilter.value,
      query: outstandingSearch.value || undefined,
    })
    outstandingData.value = res
  } catch (err: any) {
    console.error('Failed to load outstanding students', err)
  } finally {
    isOutstandingLoading.value = false
  }
}

async function onClassSelectedForFinancialView(classId: number | string) {
  filters.class_id = classId
  if (classId) {
    await loadClassStudentsFinancial(Number(classId))
  } else {
    selectedClassFinancial.value = null
  }
}

async function loadFinancialData() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [finSummary, structs] = await Promise.all([
      feeService.getSummary({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        class_id: filters.class_id ? Number(filters.class_id) : undefined,
      }),
      feeService.getFeeStructures({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        class_id: filters.class_id ? Number(filters.class_id) : undefined,
      }),
    ])
    if (finSummary) {
      summary.value = finSummary
    }
    feeStructures.value = Array.isArray(structs) ? structs : []

    // Load active tab data
    if (activeTab.value === 'students') {
      await loadEligibleStudents()
    } else if (activeTab.value === 'invoices') {
      await loadInvoices()
    } else if (activeTab.value === 'payments') {
      await loadPayments()
    } else if (activeTab.value === 'classes') {
      await loadClassSummaries()
      if (filters.class_id) {
        await loadClassStudentsFinancial(Number(filters.class_id))
      }
    } else if (activeTab.value === 'outstanding') {
      await loadOutstandingStudents()
    } else if (activeTab.value === 'overdue') {
      await loadOverdueInvoices()
    } else if (activeTab.value === 'reports') {
      await loadReportsData()
    }
  } catch (err: any) {
    console.error('Failed to load financial records from PostgreSQL', err)
    const detail = err.response?.data?.error?.message || err.response?.data?.detail || err.message
    errorMessage.value = `Unable to connect to school finance service: ${detail}`
  } finally {
    isLoading.value = false
  }
}

async function loadInvoices() {
  try {
    const res = await feeService.getInvoices({
      query: filters.search || undefined,
      class_id: filters.class_id ? Number(filters.class_id) : undefined,
      education_level: filters.education_level || undefined,
      fee_structure_id: filters.fee_structure_id ? Number(filters.fee_structure_id) : undefined,
      status: filters.status || undefined,
      academic_year: filters.academic_year || undefined,
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
      skip: (invoicePage.value - 1) * invoicePageSize.value,
      limit: invoicePageSize.value,
    })
    invoices.value = res.items || []
    totalInvoicesCount.value = res.total || 0
  } catch (err: any) {
    console.error('Failed to fetch invoices', err)
    errorMessage.value = err.response?.data?.error?.message || 'Failed to fetch invoice ledger from PostgreSQL.'
  }
}

async function loadPayments() {
  try {
    const res = await feeService.getPayments({
      class_id: filters.class_id ? Number(filters.class_id) : undefined,
      education_level: filters.education_level || undefined,
      academic_year: filters.academic_year || undefined,
      payment_method: filters.payment_method || undefined,
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
      skip: (paymentPage.value - 1) * paymentPageSize.value,
      limit: paymentPageSize.value,
    })
    payments.value = res.items || []
    totalPaymentsCount.value = res.total || 0
  } catch (err: any) {
    console.error('Failed to load payment history', err)
  }
}

async function loadClassSummaries() {
  try {
    classSummaries.value = await feeService.getClassSummaries(
      filters.academic_year || undefined,
      filters.education_level || undefined,
    )
  } catch (err: any) {
    console.error('Failed to load class summaries', err)
  }
}

async function loadOverdueInvoices() {
  try {
    const res = await feeService.getInvoices({
      is_overdue_only: true,
      academic_year: filters.academic_year || undefined,
      education_level: filters.education_level || undefined,
      class_id: filters.class_id ? Number(filters.class_id) : undefined,
      limit: 50,
    })
    overdueInvoices.value = res.items || []
    totalOverdueCount.value = res.total || 0
  } catch (err: any) {
    console.error('Failed to load overdue invoices', err)
  }
}

async function loadReportsData() {
  try {
    const [pm, mt] = await Promise.all([
      feeService.getPaymentMethodBreakdown(
        filters.academic_year || undefined,
        filters.education_level || undefined,
      ),
      feeService.getMonthlyTrends(
        filters.academic_year || undefined,
        filters.education_level || undefined,
      ),
    ])
    paymentMethodsBreakdown.value = pm || []
    monthlyTrends.value = mt || []
  } catch (err: any) {
    console.error('Failed to load reports breakdown', err)
  }
}

// ==========================================
// USER ACTIONS & MODAL HANDLERS
// ==========================================

async function updateStructureClasses() {
  try {
    const res = await feeService.getFeeClasses({
      academic_year: structureForm.academic_year || undefined,
      education_level: structureForm.education_level || undefined,
    })
    structureAvailableClasses.value = Array.isArray(res) ? res : []
  } catch (err) {
    structureAvailableClasses.value = []
  }
}

async function openNewStructureModal() {
  isEditingStructure.value = false
  editingStructureId.value = null
  structureForm.name = ''
  structureForm.academic_year = filters.academic_year || '2026/2027'
  structureForm.education_level = filters.education_level || 'PRIMARY'
  structureForm.class_id = null
  structureForm.class_ids = []
  structureForm.apply_to_all_in_level = true
  structureClassSelectionMode.value = 'ALL'
  structureForm.amount = 20
  structureForm.frequency = 'Monthly'
  structureForm.due_date = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  structureForm.description = ''
  structureForm.status = 'ACTIVE'
  await updateStructureClasses()
  isStructureModalOpen.value = true
}

async function openEditStructureModal(struct: FeeStructure) {
  isEditingStructure.value = true
  editingStructureId.value = struct.id
  structureForm.name = struct.name
  structureForm.academic_year = struct.academic_year
  structureForm.education_level = (struct.education_level || filters.education_level || 'PRIMARY') as any
  structureForm.class_id = struct.class_id || null
  structureForm.class_ids = []
  structureForm.apply_to_all_in_level = !struct.class_id
  structureClassSelectionMode.value = struct.class_id ? 'SINGLE' : 'ALL'
  structureForm.amount = Number(struct.amount)
  structureForm.frequency = struct.frequency
  structureForm.due_date = struct.due_date
  structureForm.description = struct.description || ''
  structureForm.status = struct.status
  await updateStructureClasses()
  isStructureModalOpen.value = true
}

async function submitStructureForm() {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const payload: FeeStructureCreate = {
      ...structureForm,
      amount: Number(structureForm.amount),
    }
    if (structureClassSelectionMode.value === 'ALL') {
      payload.apply_to_all_in_level = true
      payload.class_id = null
      payload.class_ids = []
    } else if (structureClassSelectionMode.value === 'SINGLE') {
      payload.apply_to_all_in_level = false
      payload.class_ids = []
    } else if (structureClassSelectionMode.value === 'MULTIPLE') {
      payload.apply_to_all_in_level = false
      payload.class_id = null
    }

    if (isEditingStructure.value && editingStructureId.value) {
      await feeService.updateFeeStructure(editingStructureId.value, payload)
      successMessage.value = 'Fee structure updated successfully.'
    } else {
      await feeService.createFeeStructure(payload)
      successMessage.value = 'Fee structure created successfully.'
    }
    isStructureModalOpen.value = false
    await loadFinancialData()
    setTimeout(() => (successMessage.value = ''), 4000)
  } catch (err: any) {
    const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to save fee structure.'
    errorMessage.value = msg
  } finally {
    isSubmitting.value = false
  }
}

function confirmDeleteStructure(struct: { id: number; name: string; assigned_count?: number }) {
  deleteConfirmStructure.value = { id: struct.id, name: struct.name, assigned_count: struct.assigned_count ?? 0 }
}

async function deleteStructure() {
  if (!deleteConfirmStructure.value) return
  isDeleting.value = true
  errorMessage.value = ''
  try {
    await feeService.deleteFeeStructure(deleteConfirmStructure.value.id)
    successMessage.value = `Fee structure "${deleteConfirmStructure.value.name}" deleted successfully.`
    deleteConfirmStructure.value = null
    // Reload structures and summary
    const [finSummary, structs] = await Promise.all([
      feeService.getSummary({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        class_id: filters.class_id ? Number(filters.class_id) : undefined,
      }),
      feeService.getFeeStructures({
        academic_year: filters.academic_year || undefined,
        education_level: filters.education_level || undefined,
        class_id: filters.class_id ? Number(filters.class_id) : undefined,
      }),
    ])
    if (finSummary) summary.value = finSummary
    feeStructures.value = Array.isArray(structs) ? structs : []
  } catch (err: any) {
    const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to delete fee structure.'
    errorMessage.value = msg
    deleteConfirmStructure.value = null
  } finally {
    isDeleting.value = false
  }
}

function openAssignModal(preselectedStructureId?: number, preselectedStudentId?: number) {
  assignForm.fee_structure_id = preselectedStructureId || (feeStructures.value[0]?.id ?? 0)
  if (preselectedStudentId) {
    assignForm.target_type = 'SINGLE_STUDENT'
    assignForm.student_id = preselectedStudentId
    assignForm.student_ids = []
    assignForm.class_id = null
  } else {
    assignForm.target_type = 'CLASS'
    assignForm.student_id = null
    assignForm.student_ids = []
    assignForm.class_id = availableClasses.value[0]?.id || null
  }
  assignForm.academic_year = filters.academic_year || '2026/2027'
  assignForm.custom_amount = null
  assignForm.custom_due_date = ''
  isAssignModalOpen.value = true
}

async function submitAssignForm() {
  if (!assignForm.fee_structure_id) {
    errorMessage.value = 'Please select a fee structure.'
    return
  }
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const payload: any = {
      target_type: assignForm.target_type,
      fee_structure_id: assignForm.fee_structure_id,
      academic_year: assignForm.academic_year,
      custom_amount: assignForm.custom_amount ? Number(assignForm.custom_amount) : undefined,
      custom_due_date: assignForm.custom_due_date || undefined,
    }
    if (assignForm.target_type === 'SINGLE_STUDENT') {
      payload.student_id = assignForm.student_id
    } else if (assignForm.target_type === 'SELECTED_STUDENTS') {
      payload.student_ids = assignForm.student_ids
    } else if (assignForm.target_type === 'CLASS') {
      payload.class_id = assignForm.class_id
    }

    const res = await feeService.assignFee(payload)
    successMessage.value = `${res.message} (${res.created_count} invoices generated, Total: $${res.total_amount_billed.toFixed(2)})`
    isAssignModalOpen.value = false
    await loadFinancialData()
    setTimeout(() => (successMessage.value = ''), 5000)
  } catch (err: any) {
    const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to assign fee.'
    errorMessage.value = msg
  } finally {
    isSubmitting.value = false
  }
}

function openPaymentModal(inv?: StudentFeeInvoice) {
  if (inv) {
    selectedInvoiceForPayment.value = inv
    paymentForm.student_fee_id = inv.id
    paymentForm.amount_paid = Number(inv.balance_remaining)
  } else {
    selectedInvoiceForPayment.value = invoices.value[0] || null
    paymentForm.student_fee_id = invoices.value[0]?.id || 0
    paymentForm.amount_paid = Number(invoices.value[0]?.balance_remaining || 0)
  }
  paymentForm.payment_date = new Date().toISOString().split('T')[0]
  paymentForm.payment_method = 'EVC_PLUS'
  paymentForm.reference_number = ''
  paymentForm.notes = ''
  isPaymentModalOpen.value = true
}

function onInvoiceSelectInPaymentModal(invId: number) {
  const inv = invoices.value.find((i) => i.id === Number(invId))
  if (inv) {
    selectedInvoiceForPayment.value = inv
    paymentForm.amount_paid = Number(inv.balance_remaining)
  }
}

async function submitPaymentForm() {
  if (paymentForm.amount_paid <= 0) {
    errorMessage.value = 'Payment amount must be greater than zero.'
    return
  }
  if (selectedInvoiceForPayment.value && paymentForm.amount_paid > selectedInvoiceForPayment.value.balance_remaining + 0.001) {
    errorMessage.value = `Payment cannot exceed outstanding balance of $${selectedInvoiceForPayment.value.balance_remaining.toFixed(2)}.`
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const payment = await feeService.recordPayment({
      student_fee_id: Number(paymentForm.student_fee_id),
      amount_paid: Number(paymentForm.amount_paid),
      payment_date: paymentForm.payment_date,
      payment_method: paymentForm.payment_method,
      reference_number: paymentForm.reference_number || undefined,
      notes: paymentForm.notes || undefined,
    })

    successMessage.value = `Payment of $${payment.amount_paid.toFixed(2)} recorded successfully! Receipt: ${payment.receipt_number}`
    isPaymentModalOpen.value = false

    // Auto-open official receipt
    await viewReceipt(payment.id)
    await loadFinancialData()
    setTimeout(() => (successMessage.value = ''), 6000)
  } catch (err: any) {
    const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to record payment transaction.'
    errorMessage.value = msg
  } finally {
    isSubmitting.value = false
  }
}

async function viewReceipt(paymentId: number) {
  try {
    const receipt = await feeService.getReceipt(paymentId)
    currentReceipt.value = receipt
    isReceiptModalOpen.value = true
  } catch (err: any) {
    errorMessage.value = 'Failed to load official receipt.'
  }
}

function printReceipt() {
  window.print()
}

function openStudentFinance(studentId: number) {
  selectedStudentIdForProfile.value = studentId
  isStudentFinanceModalOpen.value = true
}

async function openSmsModal(targetType: 'ALL_OVERDUE' | 'ALL_OUTSTANDING' | 'CLASS' | 'SINGLE_STUDENT', classId?: number, studentId?: number) {
  smsForm.target_type = targetType
  smsForm.template_type = targetType === 'ALL_OVERDUE' ? 'OVERDUE_FEE' : 'FEE_REMINDER'
  smsForm.class_id = classId || null
  smsForm.student_id = studentId || null
  smsForm.custom_template = ''
  isSmsModalOpen.value = true
  await fetchSmsPreview()
}

async function fetchSmsPreview() {
  isSmsPreviewLoading.value = true
  try {
    smsPreviewData.value = await feeService.previewFeeSms({
      target_type: smsForm.target_type,
      template_type: smsForm.template_type,
      class_id: smsForm.class_id || undefined,
      student_id: smsForm.student_id || undefined,
      academic_year: filters.academic_year || undefined,
    })
  } catch (err: any) {
    console.error('Failed to preview SMS recipients', err)
  } finally {
    isSmsPreviewLoading.value = false
  }
}

async function sendFeeSmsBroadcast() {
  if (!smsPreviewData.value || smsPreviewData.value.eligible_count === 0) {
    errorMessage.value = 'No eligible recipients with verified Somali phone numbers found.'
    return
  }
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    const res = await feeService.sendFeeSms({
      target_type: smsForm.target_type,
      template_type: smsForm.template_type,
      class_id: smsForm.class_id || undefined,
      student_id: smsForm.student_id || undefined,
      academic_year: filters.academic_year || undefined,
      custom_message_template: smsForm.custom_template || undefined,
    })
    successMessage.value = `SMS Dispatch: ${res.sent_count} sent via Hormuud Gateway (${res.skipped_count} skipped, ${res.failed_count} failed).`
    isSmsModalOpen.value = false
    setTimeout(() => (successMessage.value = ''), 6000)
  } catch (err: any) {
    const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Failed to dispatch SMS.'
    errorMessage.value = msg
  } finally {
    isSubmitting.value = false
  }
}

function exportData(type: string) {
  const url = feeService.getExportUrl(type, filters.academic_year || undefined, filters.class_id ? Number(filters.class_id) : undefined)
  window.open(url, '_blank')
}

// Watchers
watch(activeTab, () => {
  loadFinancialData()
})

watch(
  () => [filters.academic_year, filters.class_id, filters.status, filters.fee_structure_id, filters.payment_method],
  () => {
    invoicePage.value = 1
    paymentPage.value = 1
    loadFinancialData()
  }
)

onMounted(async () => {
  await loadDropdowns()
  await loadFinancialData()
})
</script>

<template>
  <div class="fees-container">
    <!-- TOP HEADER -->
    <header class="page-header">
      <div class="header-main">
        <div class="header-title-block">
          <div class="badge-tag">
            <i class="pi pi-shield"></i> Education Management System &bull; System Authoritative
          </div>
          <h1 class="page-title">Fees & Financial Management</h1>
          <p class="page-subtitle">
            Manage school fees, student invoices, payments, outstanding balances and financial records.
          </p>
        </div>

        <!-- QUICK ACTIONS -->
        <div class="quick-actions">
          <button class="btn btn-primary" @click="openNewStructureModal">
            <i class="pi pi-plus"></i> + New Fee Structure
          </button>
          <button class="btn btn-secondary" @click="openAssignModal()">
            <i class="pi pi-user-plus"></i> Assign Fee
          </button>
          <button class="btn btn-success" @click="openPaymentModal()">
            <i class="pi pi-wallet"></i> Record Payment
          </button>
          <button class="btn btn-warning" @click="openSmsModal('ALL_OVERDUE')">
            <i class="pi pi-bell"></i> SMS Reminders
          </button>
          <button class="btn btn-dark" @click="exportData('invoices')">
            <i class="pi pi-download"></i> Export CSV
          </button>
        </div>
      </div>
    </header>

    <!-- ALERTS -->
    <div v-if="errorMessage" class="alert alert-error">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ errorMessage }}</span>
      <button class="alert-close" @click="errorMessage = ''">&times;</button>
    </div>

    <div v-if="successMessage" class="alert alert-success">
      <i class="pi pi-check-circle"></i>
      <span>{{ successMessage }}</span>
      <button class="alert-close" @click="successMessage = ''">&times;</button>
    </div>

    <!-- LEVEL & ACADEMIC YEAR SELECTOR STRIP (HIERARCHY FIRST) -->
    <div class="level-hierarchy-bar">
      <div class="level-selector-group">
        <span class="level-label">EDUCATION LEVEL:</span>
        <div class="level-pill-toggle">
          <button
            type="button"
            :class="['level-btn', { active: filters.education_level === 'PRIMARY' }]"
            @click="setEducationLevel('PRIMARY')"
          >
            <i class="pi pi-book"></i> PRIMARY (Grade 1 - 8)
          </button>
          <button
            type="button"
            :class="['level-btn', { active: filters.education_level === 'SECONDARY' }]"
            @click="setEducationLevel('SECONDARY')"
          >
            <i class="pi pi-graduation-cap"></i> SECONDARY (Form 1 - 4)
          </button>
        </div>
      </div>

      <div class="level-meta-info">
        <span class="active-badge">
          Active Filter: <strong>{{ filters.education_level }}</strong> &bull; {{ filters.academic_year }} &bull; {{ filters.class_id ? (availableClasses.find(c => c.id === Number(filters.class_id))?.name || 'Class ' + filters.class_id) : ('All ' + (filters.education_level === 'PRIMARY' ? 'Primary' : 'Secondary') + ' Classes') }}
        </span>
      </div>
    </div>

    <!-- 5 AUTHORITATIVE FINANCIAL KPI CARDS -->
    <section class="kpi-grid">
      <div class="kpi-card billed">
        <div class="kpi-icon-wrap"><i class="pi pi-users"></i></div>
        <div class="kpi-body">
          <span class="kpi-label">TOTAL STUDENTS</span>
          <h2 class="kpi-value">{{ summary.total_students ?? summary.total_eligible_students ?? eligibleStudentsData.total_eligible }}</h2>
          <span class="kpi-foot">{{ summary.total_students ?? summary.total_eligible_students ?? 0 }} Students &bull; {{ summary.paid_students_count || 0 }} Paid &bull; {{ summary.unpaid_students_count || 0 }} Unpaid</span>
        </div>
      </div>

      <div class="kpi-card rate">
        <div class="kpi-icon-wrap"><i class="pi pi-tag"></i></div>
        <div class="kpi-body">
          <span class="kpi-label">FEE PER STUDENT</span>
          <h2 class="kpi-value">${{ Number(summary.fee_per_student || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</h2>
          <span class="kpi-foot">{{ filters.class_id ? 'Class specific fee rule' : 'Institutional active fee' }}</span>
        </div>
      </div>

      <div class="kpi-card expected">
        <div class="kpi-icon-wrap"><i class="pi pi-calculator"></i></div>
        <div class="kpi-body">
          <span class="kpi-label">EXPECTED</span>
          <h2 class="kpi-value">${{ Number(summary.expected_total ?? summary.total_billed ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</h2>
          <span class="kpi-foot">{{ summary.total_students ?? summary.total_eligible_students ?? 0 }} Students &times; ${{ Number(summary.fee_per_student || 0).toFixed(2) }}</span>
        </div>
      </div>

      <div class="kpi-card collected">
        <div class="kpi-icon-wrap"><i class="pi pi-check-circle"></i></div>
        <div class="kpi-body">
          <span class="kpi-label">PAID</span>
          <h2 class="kpi-value text-success">${{ Number(summary.total_paid ?? summary.total_collected ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</h2>
          <span class="kpi-foot">{{ summary.paid_students_count || 0 }} fully paid students</span>
        </div>
      </div>

      <div class="kpi-card outstanding">
        <div class="kpi-icon-wrap"><i class="pi pi-clock"></i></div>
        <div class="kpi-body">
          <span class="kpi-label">OUTSTANDING</span>
          <h2 class="kpi-value text-warning">${{ Number(summary.total_outstanding || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</h2>
          <span class="kpi-foot">{{ summary.unpaid_students_count || 0 }} unpaid students</span>
        </div>
      </div>
    </section>

    <!-- 20. FINANCIAL & COHORT RECONCILIATION PANEL -->
    <div class="reconciliation-panel" :class="{ 'is-reconciled': summary.is_reconciled !== false, 'is-warning': summary.is_reconciled === false }">
      <div class="recon-header">
        <div class="recon-title">
          <i :class="summary.is_reconciled !== false ? 'pi pi-verified text-success' : 'pi pi-exclamation-triangle text-danger'"></i>
          <strong>Financial Reconciliation Ledger (PostgreSQL Authoritative)</strong>
        </div>
        <span class="recon-badge" :class="summary.is_reconciled !== false ? 'badge-success' : 'badge-danger'">
          {{ summary.is_reconciled !== false ? 'RECONCILED ✓' : 'RECONCILIATION MISMATCH' }}
        </span>
      </div>

      <div class="recon-body">
        <div class="recon-equation">
          <div class="recon-col">
            <span class="r-label">Expected Amount</span>
            <span class="r-val">${{ Number(summary.expected_total ?? summary.total_billed ?? 0).toFixed(2) }}</span>
          </div>
          <span class="r-op">=</span>
          <div class="recon-col">
            <span class="r-label">Paid Amount</span>
            <span class="r-val text-success">${{ Number(summary.total_paid ?? summary.total_collected ?? 0).toFixed(2) }}</span>
          </div>
          <span class="r-op">+</span>
          <div class="recon-col">
            <span class="r-label">Outstanding Amount</span>
            <span class="r-val text-warning">${{ Number(summary.total_outstanding || 0).toFixed(2) }}</span>
          </div>
        </div>

        <div class="recon-check-box" v-if="summary.is_reconciled !== false">
          <div class="recon-badge-line">
            <i class="pi pi-check"></i>
            <span>Check: ${{ Number(summary.total_paid ?? summary.total_collected ?? 0).toFixed(2) }} + ${{ Number(summary.total_outstanding || 0).toFixed(2) }} = ${{ Number(summary.expected_total ?? summary.total_billed ?? 0).toFixed(2) }} ✓</span>
          </div>
          <div class="recon-badge-line student-check">
            <i class="pi pi-users"></i>
            <span>Student Check: {{ summary.paid_students_count || 0 }} paid + {{ summary.unpaid_students_count || 0 }} unpaid = {{ summary.total_students ?? summary.total_eligible_students ?? 0 }} total students ✓</span>
          </div>
        </div>
      </div>

      <div v-if="summary.is_reconciled === false" class="recon-warning-strip">
        <i class="pi pi-exclamation-circle"></i>
        <span>{{ summary.reconciliation_message || 'Financial reconciliation discrepancy detected. Totals do not balance.' }}</span>
      </div>
    </div>


    <!-- NAVIGATION TABS -->
    <div class="tabs-nav-bar">
      <button :class="['tab-nav-btn', { active: activeTab === 'students' }]" @click="activeTab = 'students'">
        <i class="pi pi-users"></i> Fee-Eligible Students ({{ summary.total_eligible_students ?? eligibleStudentsData.total_eligible }})
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'invoices' }]" @click="activeTab = 'invoices'">
        <i class="pi pi-list"></i> Student Fee Invoices ({{ totalInvoicesCount }})
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'outstanding' }]" @click="activeTab = 'outstanding'">
        <i class="pi pi-exclamation-circle"></i> Outstanding / Unpaid ({{ (outstandingData.unpaid_count || 0) + (outstandingData.partial_count || 0) }})
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'structures' }]" @click="activeTab = 'structures'">
        <i class="pi pi-cog"></i> Fee Structures ({{ feeStructures.length }})
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'payments' }]" @click="activeTab = 'payments'">
        <i class="pi pi-receipt"></i> Payment Transactions ({{ totalPaymentsCount }})
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'classes' }]" @click="activeTab = 'classes'">
        <i class="pi pi-building"></i> Class Financial View
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'overdue' }]" @click="activeTab = 'overdue'">
        <i class="pi pi-bell"></i> Overdue & SMS Reminders
      </button>
      <button :class="['tab-nav-btn', { active: activeTab === 'reports' }]" @click="activeTab = 'reports'">
        <i class="pi pi-chart-pie"></i> Financial Reports
      </button>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div class="content-body">
      <!-- GLOBAL FILTER BAR -->
      <div class="filter-strip">
        <div class="filter-group">
          <label>Academic Year:</label>
          <select v-model="filters.academic_year" @change="loadDropdowns(); loadFinancialData()" class="form-select">
            <option v-for="yr in academicYears" :key="yr" :value="yr">{{ yr }}</option>
          </select>
        </div>

        <div v-if="activeTab === 'students' || activeTab === 'invoices' || activeTab === 'overdue' || activeTab === 'classes' || activeTab === 'outstanding' || activeTab === 'payments' || activeTab === 'structures'" class="filter-group">
          <label>Class Filter:</label>
          <select v-model="filters.class_id" @change="onClassSelectedForFinancialView(filters.class_id); loadFinancialData()" class="form-select">
            <option value="">All {{ filters.education_level === 'PRIMARY' ? 'Primary' : 'Secondary' }} Classes</option>
            <option v-for="c in availableClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>

        <div v-if="activeTab === 'invoices'" class="filter-group">
          <label>Status:</label>
          <select v-model="filters.status" class="form-select">
            <option value="">All Statuses</option>
            <option value="PAID">PAID</option>
            <option value="PARTIALLY_PAID">PARTIALLY PAID</option>
            <option value="PENDING">PENDING / UNPAID</option>
            <option value="OVERDUE">OVERDUE</option>
          </select>
        </div>

        <div v-if="activeTab === 'invoices' || activeTab === 'payments'" class="filter-group search-input-group">
          <label>Search:</label>
          <div class="input-icon-wrap">
            <i class="pi pi-search"></i>
            <input
              type="text"
              v-model="filters.search"
              @keyup.enter="loadInvoices"
              placeholder="Student name, admission #, invoice #"
              class="form-input"
            />
          </div>
        </div>

        <button class="btn btn-outline" @click="loadFinancialData" :disabled="isLoading">
          <i :class="['pi pi-refresh', { 'pi-spin': isLoading }]"></i> Refresh
        </button>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 0: FEE-ELIGIBLE STUDENTS (SINGLE SOURCE OF TRUTH) -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'students'" class="tab-pane">
        <div class="pane-header-actions">
          <div>
            <h3>Fee-Eligible Enrolled Students ({{ filters.education_level }})</h3>
            <p class="subtext">
              Authoritative student list derived directly from active enrollment in PostgreSQL. Registering a student automatically establishes fee eligibility.
            </p>
          </div>
          <div class="quick-actions">
            <button class="btn btn-secondary" @click="openAssignModal()">
              <i class="pi pi-user-plus"></i> + Assign Fee
            </button>
            <button class="btn btn-outline" @click="loadEligibleStudents" :disabled="isEligibleStudentsLoading">
              <i :class="['pi pi-refresh', { 'pi-spin': isEligibleStudentsLoading }]"></i> Refresh
            </button>
          </div>
        </div>

        <!-- ELIGIBLE STUDENTS KPI SUMMARY STRIP -->
        <div class="outstanding-kpi-bar">
          <div class="mini-kpi">
            <span class="mini-kpi-label">TOTAL ELIGIBLE</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.total_eligible }}</strong>
          </div>
          <div class="mini-kpi text-info">
            <span class="mini-kpi-label">INVOICED</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.invoiced_count }}</strong>
          </div>
          <div class="mini-kpi text-neutral">
            <span class="mini-kpi-label">UNBILLED</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.uninvoiced_count }}</strong>
          </div>
          <div class="mini-kpi text-primary">
            <span class="mini-kpi-label">PRIMARY ROSTER</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.primary_count }}</strong>
          </div>
          <div class="mini-kpi text-secondary">
            <span class="mini-kpi-label">SECONDARY ROSTER</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.secondary_count }}</strong>
          </div>
          <div class="mini-kpi text-danger" v-if="eligibleStudentsData.without_class_count > 0">
            <span class="mini-kpi-label">WITHOUT CLASS</span>
            <strong class="mini-kpi-val">{{ eligibleStudentsData.without_class_count }}</strong>
          </div>
        </div>

        <!-- FILTERS -->
        <div class="outstanding-filter-strip">
          <div class="filter-group">
            <label>Filter Status:</label>
            <select v-model="eligibleStudentStatusFilter" @change="loadEligibleStudents" class="form-select">
              <option value="">All Eligible Students</option>
              <option value="INVOICED">Invoiced Only</option>
              <option value="UNBILLED">Unbilled / Not Invoiced</option>
              <option value="PAID">Fully Paid</option>
              <option value="UNPAID">Outstanding / Unpaid</option>
              <option value="PARTIAL">Partially Paid</option>
              <option value="OVERDUE">Overdue</option>
            </select>
          </div>

          <div class="filter-group search-input-group">
            <label>Search Student:</label>
            <div class="input-icon-wrap">
              <i class="pi pi-search"></i>
              <input
                type="text"
                v-model="eligibleStudentSearch"
                @keyup.enter="loadEligibleStudents"
                placeholder="Search by student name or admission #"
                class="form-input"
              />
            </div>
          </div>

          <button class="btn btn-outline" @click="loadEligibleStudents" :disabled="isEligibleStudentsLoading">
            <i :class="['pi pi-filter', { 'pi-spin': isEligibleStudentsLoading }]"></i> Filter
          </button>
        </div>

        <div v-if="isEligibleStudentsLoading" class="state-container loading-state">
          <i class="pi pi-spin pi-spinner state-icon"></i>
          <p>Loading fee-eligible students from PostgreSQL database...</p>
        </div>

        <div v-else-if="eligibleStudentsData.items.length === 0" class="state-container empty-state">
          <i class="pi pi-users state-icon"></i>
          <h3>No eligible students found under selected criteria.</h3>
          <p>Enrolled active students will automatically appear here once registered.</p>
        </div>

        <div v-else>
          <div class="table-responsive desktop-finance-table" tabindex="0" role="region" aria-label="Eligible students finance table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Admission #</th>
                  <th>Student Name</th>
                  <th>Current Class</th>
                  <th>Division</th>
                  <th>Invoices</th>
                  <th class="text-right">Total Billed</th>
                  <th class="text-right">Paid</th>
                  <th class="text-right">Balance Due</th>
                  <th>Financial Status</th>
                  <th class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="st in eligibleStudentsData.items" :key="st.student_id">
                  <td class="font-mono font-bold nowrap-cell">{{ st.admission_number }}</td>
                  <td>
                    <a href="javascript:void(0)" class="student-link" @click="openStudentFinance(st.student_id)">
                      <strong>{{ st.full_name }}</strong>
                    </a>
                    <span v-if="st.guardian_name" class="subtext">Guardian: {{ st.guardian_name }}</span>
                  </td>
                  <td><span class="class-pill">{{ st.class_name }}</span></td>
                  <td><span class="badge-tag">{{ st.education_level }}</span></td>
                  <td>
                    <span v-if="st.invoices_count > 0" class="badge-tag">{{ st.invoices_count }} invoice(s)</span>
                    <span v-else class="badge-tag" style="background:#f1f5f9;color:#64748b;">Not Invoiced</span>
                  </td>
                  <td class="text-right font-bold nowrap-cell">${{ Number(st.total_billed).toFixed(2) }}</td>
                  <td class="text-right text-success font-bold nowrap-cell">${{ Number(st.total_paid).toFixed(2) }}</td>
                  <td class="text-right text-danger font-bold nowrap-cell">${{ Number(st.outstanding_balance).toFixed(2) }}</td>
                  <td>
                    <StatusBadge
                      :status="st.financial_status"
                      :variant="st.financial_status === 'PAID' ? 'success' : st.financial_status === 'PARTIAL' ? 'warning' : st.financial_status === 'OVERDUE' ? 'danger' : st.financial_status === 'UNPAID' ? 'info' : 'neutral'"
                    />
                  </td>
                  <td class="text-center">
                    <div class="row-actions">
                      <button
                        class="btn-row-action btn-pay"
                        title="Assign Fee to Student"
                        @click="openAssignModal(undefined, st.student_id)"
                      >
                        <i class="pi pi-plus"></i> Assign Fee
                      </button>
                      <button
                        class="btn-row-action btn-view"
                        title="View Student Ledger"
                        @click="openStudentFinance(st.student_id)"
                      >
                        <i class="pi pi-eye"></i> View
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-finance-cards">
            <article v-for="st in eligibleStudentsData.items" :key="'m-el-' + st.student_id" class="mobile-finance-card">
              <div class="mfc-head">
                <div>
                  <div class="mfc-title" @click="openStudentFinance(st.student_id)">{{ st.full_name }}</div>
                  <div class="mfc-sub font-mono">{{ st.admission_number }} &bull; {{ st.class_name }}</div>
                </div>
                <StatusBadge
                  :status="st.financial_status"
                  :variant="st.financial_status === 'PAID' ? 'success' : st.financial_status === 'PARTIAL' ? 'warning' : st.financial_status === 'OVERDUE' ? 'danger' : st.financial_status === 'UNPAID' ? 'info' : 'neutral'"
                />
              </div>
              <div class="mfc-kv-grid">
                <div class="mfc-kv">
                  <span class="mfc-lbl">Billed</span>
                  <span class="mfc-val">${{ Number(st.total_billed).toFixed(2) }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Paid</span>
                  <span class="mfc-val text-success">${{ Number(st.total_paid).toFixed(2) }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Balance</span>
                  <span class="mfc-val text-danger">${{ Number(st.outstanding_balance).toFixed(2) }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Invoices</span>
                  <span class="mfc-val">{{ st.invoices_count > 0 ? `${st.invoices_count} invoice(s)` : 'Not Invoiced' }}</span>
                </div>
              </div>
              <div class="mfc-actions">
                <button class="btn-row-action btn-pay mfc-btn" @click="openAssignModal(undefined, st.student_id)">
                  <i class="pi pi-plus"></i> Assign Fee
                </button>
                <button class="btn-row-action btn-view mfc-btn" @click="openStudentFinance(st.student_id)">
                  <i class="pi pi-eye"></i> View Ledger
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 1: STUDENT INVOICES LEDGER -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'invoices'" class="tab-pane">
        <div v-if="isLoading" class="state-container loading-state">
          <i class="pi pi-spin pi-spinner state-icon"></i>
          <p>Loading authoritative invoice records from PostgreSQL database...</p>
        </div>

        <div v-else-if="invoices.length === 0" class="state-container empty-state">
          <i class="pi pi-folder-open state-icon"></i>
          <h3>No fee records have been created yet.</h3>
          <p>Assign a fee structure to classes or individual students to generate invoices.</p>
          <button class="btn btn-primary" @click="openAssignModal()">+ Assign First Fee</button>
        </div>

        <div v-else>
          <div class="table-responsive desktop-finance-table" tabindex="0" role="region" aria-label="Fee invoices table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Invoice #</th>
                  <th>Student</th>
                  <th>Class</th>
                  <th>Academic Year</th>
                  <th>Fee Type</th>
                  <th class="text-right">Amount</th>
                  <th class="text-right">Paid</th>
                  <th class="text-right">Balance</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in invoices" :key="inv.id">
                  <td class="font-mono font-bold nowrap-cell">{{ inv.invoice_number }}</td>
                  <td>
                    <a href="javascript:void(0)" class="student-link" @click="openStudentFinance(inv.student_id)">
                      <strong>{{ inv.student_name }}</strong>
                    </a>
                    <span class="subtext">Adm: {{ inv.student_admission_number }}</span>
                  </td>
                  <td>{{ inv.class_name || '—' }}</td>
                  <td class="nowrap-cell">{{ inv.academic_year }}</td>
                  <td>{{ inv.fee_type || 'Tuition' }}</td>
                  <td class="text-right font-bold nowrap-cell">${{ Number(inv.net_amount).toFixed(2) }}</td>
                  <td class="text-right text-success font-bold nowrap-cell">${{ Number(inv.total_paid).toFixed(2) }}</td>
                  <td class="text-right text-danger font-bold nowrap-cell">${{ Number(inv.balance_remaining).toFixed(2) }}</td>
                  <td class="nowrap-cell">{{ inv.due_date }}</td>
                  <td>
                    <StatusBadge
                      :status="inv.status"
                      :variant="inv.status === 'PAID' ? 'success' : inv.status === 'PARTIALLY_PAID' ? 'warning' : inv.status === 'OVERDUE' ? 'danger' : 'info'"
                    />
                  </td>
                  <td class="text-center">
                    <div class="row-actions">
                      <button
                        v-if="inv.balance_remaining > 0"
                        class="btn-row-action btn-pay"
                        title="Record Payment"
                        @click="openPaymentModal(inv)"
                      >
                        <i class="pi pi-wallet"></i> Pay
                      </button>
                      <button
                        class="btn-row-action btn-view"
                        title="View Student Ledger"
                        @click="openStudentFinance(inv.student_id)"
                      >
                        <i class="pi pi-eye"></i> View
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-finance-cards">
            <article v-for="inv in invoices" :key="'m-inv-' + inv.id" class="mobile-finance-card">
              <div class="mfc-head">
                <div>
                  <div class="mfc-title" @click="openStudentFinance(inv.student_id)">{{ inv.student_name }}</div>
                  <div class="mfc-sub font-mono">{{ inv.invoice_number }} &bull; {{ inv.class_name || '—' }}</div>
                </div>
                <StatusBadge
                  :status="inv.status"
                  :variant="inv.status === 'PAID' ? 'success' : inv.status === 'PARTIALLY_PAID' ? 'warning' : inv.status === 'OVERDUE' ? 'danger' : 'info'"
                />
              </div>
              <div class="mfc-kv-grid">
                <div class="mfc-kv">
                  <span class="mfc-lbl">Fee Type</span>
                  <span class="mfc-val">{{ inv.fee_type || 'Tuition' }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Due Date</span>
                  <span class="mfc-val">{{ inv.due_date }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Amount / Paid</span>
                  <span class="mfc-val">${{ Number(inv.net_amount).toFixed(2) }} / <span class="text-success">${{ Number(inv.total_paid).toFixed(2) }}</span></span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Balance</span>
                  <span class="mfc-val text-danger">${{ Number(inv.balance_remaining).toFixed(2) }}</span>
                </div>
              </div>
              <div class="mfc-actions">
                <button v-if="inv.balance_remaining > 0" class="btn-row-action btn-pay mfc-btn" @click="openPaymentModal(inv)">
                  <i class="pi pi-wallet"></i> Pay Now
                </button>
                <button class="btn-row-action btn-view mfc-btn" @click="openStudentFinance(inv.student_id)">
                  <i class="pi pi-eye"></i> View Ledger
                </button>
              </div>
            </article>
          </div>

          <!-- Pagination -->
          <div class="pagination-bar">
            <span>Showing {{ invoices.length }} of {{ totalInvoicesCount }} records</span>
            <div class="page-controls">
              <button
                class="btn-page"
                :disabled="invoicePage <= 1"
                @click="invoicePage--; loadInvoices()"
              >
                Previous
              </button>
              <span class="page-num">Page {{ invoicePage }}</span>
              <button
                class="btn-page"
                :disabled="invoices.length < invoicePageSize"
                @click="invoicePage++; loadInvoices()"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB: OUTSTANDING / UNPAID STUDENTS -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'outstanding'" class="tab-pane">
        <div class="pane-header-actions">
          <div>
            <h3>Outstanding & Unpaid Student Accounts</h3>
            <p class="subtext">Authoritative balances calculated from PostgreSQL invoices and verified payments.</p>
          </div>
          <div class="quick-actions">
            <button class="btn btn-warning" @click="openSmsModal('ALL_OUTSTANDING')">
              <i class="pi pi-bell"></i> Send SMS Reminders
            </button>
          </div>
        </div>

        <!-- OUTSTANDING KPI SUMMARY STRIP -->
        <div class="outstanding-kpi-bar">
          <div class="mini-kpi">
            <span class="mini-kpi-label">TOTAL STUDENTS</span>
            <strong class="mini-kpi-val">{{ outstandingData.total_students }}</strong>
          </div>
          <div class="mini-kpi text-success">
            <span class="mini-kpi-label">PAID</span>
            <strong class="mini-kpi-val">{{ outstandingData.paid_count }}</strong>
          </div>
          <div class="mini-kpi text-warning">
            <span class="mini-kpi-label">PARTIAL</span>
            <strong class="mini-kpi-val">{{ outstandingData.partial_count }}</strong>
          </div>
          <div class="mini-kpi text-danger">
            <span class="mini-kpi-label">UNPAID</span>
            <strong class="mini-kpi-val">{{ outstandingData.unpaid_count }}</strong>
          </div>
          <div class="mini-kpi text-danger font-bold">
            <span class="mini-kpi-label">OVERDUE</span>
            <strong class="mini-kpi-val">{{ outstandingData.overdue_count }}</strong>
          </div>
          <div class="mini-kpi outstanding-total">
            <span class="mini-kpi-label">OUTSTANDING BALANCE</span>
            <strong class="mini-kpi-val text-warning">${{ Number(outstandingData.total_outstanding_balance).toFixed(2) }}</strong>
          </div>
        </div>

        <!-- OUTSTANDING FILTERS -->
        <div class="outstanding-filter-strip">
          <div class="filter-group">
            <label>Filter Status:</label>
            <select v-model="outstandingStatusFilter" @change="loadOutstandingStudents" class="form-select">
              <option value="ALL_OUTSTANDING">All Outstanding (Unpaid & Partial)</option>
              <option value="UNPAID">Unpaid Only</option>
              <option value="PARTIAL">Partial Only</option>
              <option value="OVERDUE">Overdue Only</option>
            </select>
          </div>

          <div class="filter-group search-input-group">
            <label>Search Student:</label>
            <div class="input-icon-wrap">
              <i class="pi pi-search"></i>
              <input
                type="text"
                v-model="outstandingSearch"
                @keyup.enter="loadOutstandingStudents"
                placeholder="Search by student name or admission #"
                class="form-input"
              />
            </div>
          </div>

          <button class="btn btn-outline" @click="loadOutstandingStudents" :disabled="isOutstandingLoading">
            <i :class="['pi pi-refresh', { 'pi-spin': isOutstandingLoading }]"></i> Filter
          </button>
        </div>

        <!-- OUTSTANDING TABLE -->
        <div v-if="isOutstandingLoading" class="state-container loading-state">
          <i class="pi pi-spin pi-spinner state-icon"></i>
          <p>Loading outstanding accounts from PostgreSQL...</p>
        </div>

        <div v-else-if="outstandingData.items.length === 0" class="state-container empty-state">
          <i class="pi pi-check-circle state-icon text-success"></i>
          <h3>No matching outstanding students found.</h3>
          <p>All students under selected filters are fully paid.</p>
        </div>

        <div v-else>
          <div class="table-responsive desktop-finance-table" tabindex="0" role="region" aria-label="Outstanding fee balances table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Admission #</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th>Level</th>
                  <th>Fee Structure</th>
                  <th class="text-right">Total Billed</th>
                  <th class="text-right">Paid</th>
                  <th class="text-right">Balance Due</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="st in outstandingData.items" :key="st.student_id + '-' + (st.invoice_number || 'x')">
                  <td class="font-mono font-bold nowrap-cell">{{ st.admission_number }}</td>
                  <td><strong>{{ st.student_name }}</strong></td>
                  <td><span class="class-pill">{{ st.class_name }}</span></td>
                  <td><span class="badge-tag">{{ st.education_level }}</span></td>
                  <td>{{ st.fee_type || 'Standard Tuition' }}</td>
                  <td class="text-right font-bold nowrap-cell">${{ Number(st.amount_due).toFixed(2) }}</td>
                  <td class="text-right text-success font-bold nowrap-cell">${{ Number(st.paid_amount).toFixed(2) }}</td>
                  <td class="text-right text-danger font-bold nowrap-cell">${{ Number(st.balance).toFixed(2) }}</td>
                  <td class="nowrap-cell" :class="{ 'text-danger font-bold': st.status === 'OVERDUE' }">{{ st.due_date || '—' }}</td>
                  <td>
                    <StatusBadge
                      :status="st.status"
                      :variant="st.status === 'PAID' ? 'success' : st.status === 'PARTIAL' ? 'warning' : 'danger'"
                    />
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm btn-outline ml-1" @click="openStudentFinance(st.student_id)">Profile</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-finance-cards">
            <article v-for="st in outstandingData.items" :key="'m-out-' + st.student_id + '-' + (st.invoice_number || 'x')" class="mobile-finance-card">
              <div class="mfc-head">
                <div>
                  <div class="mfc-title" @click="openStudentFinance(st.student_id)">{{ st.student_name }}</div>
                  <div class="mfc-sub font-mono">{{ st.admission_number }} &bull; {{ st.class_name }}</div>
                </div>
                <StatusBadge
                  :status="st.status"
                  :variant="st.status === 'PAID' ? 'success' : st.status === 'PARTIAL' ? 'warning' : 'danger'"
                />
              </div>
              <div class="mfc-kv-grid">
                <div class="mfc-kv">
                  <span class="mfc-lbl">Billed / Paid</span>
                  <span class="mfc-val">${{ Number(st.amount_due).toFixed(2) }} / <span class="text-success">${{ Number(st.paid_amount).toFixed(2) }}</span></span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Balance Due</span>
                  <span class="mfc-val text-danger">${{ Number(st.balance).toFixed(2) }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Fee Structure</span>
                  <span class="mfc-val">{{ st.fee_type || 'Standard Tuition' }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Due Date</span>
                  <span class="mfc-val">{{ st.due_date || '—' }}</span>
                </div>
              </div>
              <div class="mfc-actions">
                <button class="btn-row-action btn-view mfc-btn" @click="openStudentFinance(st.student_id)">
                  <i class="pi pi-user"></i> View Student Profile
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 2: FEE STRUCTURES (ADMIN CONTROLLED) -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'structures'" class="tab-pane">
        <div class="pane-header-actions">
          <div class="pane-title-group">
            <h3>Configured Institutional Fee Structures</h3>
            <p class="pane-subtitle">Authoritative fee rules explicitly configured by School Administration.</p>
          </div>
          <div class="header-tools-row">
            <div class="status-filter-pills">
              <button
                type="button"
                :class="['filter-pill', { active: structureStatusFilter === 'ACTIVE' }]"
                @click="structureStatusFilter = 'ACTIVE'"
              >
                Active ({{ feeStructures.filter(s => s.status === 'ACTIVE').length }})
              </button>
              <button
                type="button"
                :class="['filter-pill', { active: structureStatusFilter === 'ARCHIVED' }]"
                @click="structureStatusFilter = 'ARCHIVED'"
              >
                Archived ({{ feeStructures.filter(s => s.status !== 'ACTIVE').length }})
              </button>
              <button
                type="button"
                :class="['filter-pill', { active: structureStatusFilter === 'ALL' }]"
                @click="structureStatusFilter = 'ALL'"
              >
                All ({{ feeStructures.length }})
              </button>
            </div>
            <button class="btn btn-primary" @click="openNewStructureModal">
              <i class="pi pi-plus"></i> Add New Fee Structure
            </button>
          </div>
        </div>

        <div v-if="filteredFeeStructures.length === 0" class="state-container empty-state">
          <i class="pi pi-cog state-icon"></i>
          <h3>No {{ structureStatusFilter.toLowerCase() }} fee structures found.</h3>
          <p>Institutional fee structures are created and controlled explicitly by School Admin.</p>
          <button v-if="structureStatusFilter !== 'ALL'" class="btn btn-outline" @click="structureStatusFilter = 'ALL'">View All Structures</button>
          <button v-else class="btn btn-primary" @click="openNewStructureModal">+ Create Fee Structure</button>
        </div>

        <div v-else class="structures-grid">
          <div v-for="struct in filteredFeeStructures" :key="struct.id" class="structure-card">
            <div class="struct-head">
              <div class="struct-title-wrap">
                <h4>{{ struct.name }}</h4>
                <span class="freq-tag">{{ struct.frequency }}</span>
              </div>
              <StatusBadge :status="struct.status" :variant="struct.status === 'ACTIVE' ? 'success' : 'neutral'" />
            </div>

            <div class="struct-body">
              <div class="struct-amount">${{ Number(struct.amount).toFixed(2) }}</div>
              <p v-if="struct.description" class="struct-desc">{{ struct.description }}</p>

              <div class="struct-meta">
                <div><i class="pi pi-bookmark"></i> Education Level: <strong>{{ struct.education_level || 'PRIMARY' }}</strong></div>
                <div><i class="pi pi-calendar"></i> Academic Year: <strong>{{ struct.academic_year }}</strong></div>
                <div><i class="pi pi-building"></i> Class: <strong>{{ struct.class_name || 'All Classes in Level' }}</strong></div>
                <div><i class="pi pi-calendar-plus"></i> Created Date: <strong>{{ struct.created_at ? new Date(struct.created_at).toLocaleDateString() : '—' }}</strong></div>
                <div><i class="pi pi-clock"></i> Due Date: <strong>{{ struct.due_date || '—' }}</strong></div>
                <div><i class="pi pi-users"></i> Assigned Students: <strong>{{ struct.assigned_count ?? 0 }}</strong></div>
              </div>
            </div>

            <div class="struct-actions">
              <button class="btn btn-sm btn-primary" @click="openAssignModal(struct.id)">
                <i class="pi pi-user-plus"></i> Assign Fee
              </button>
              <button class="btn btn-sm btn-outline" @click="openEditStructureModal(struct)">
                <i class="pi pi-pencil"></i> Edit
              </button>
              <button class="btn btn-sm btn-danger" @click="confirmDeleteStructure(struct)" title="Delete Fee Structure">
                <i class="pi pi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 3: PAYMENT TRANSACTIONS & RECEIPTS -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'payments'" class="tab-pane">
        <div class="pane-header-actions">
          <h3>Payment Transaction Ledger & Verified Receipts</h3>
          <button class="btn btn-success" @click="openPaymentModal()">
            <i class="pi pi-wallet"></i> Record New Payment
          </button>
        </div>

        <div v-if="payments.length === 0" class="state-container empty-state">
          <i class="pi pi-receipt state-icon"></i>
          <h3>No payments recorded yet.</h3>
          <p>Payments recorded against invoices will appear here with unique serial receipts.</p>
        </div>

        <div v-else>
          <div class="table-responsive desktop-finance-table" tabindex="0" role="region" aria-label="Payment receipts table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Receipt #</th>
                  <th>Student</th>
                  <th>Invoice #</th>
                  <th class="text-right">Amount Paid</th>
                  <th>Method</th>
                  <th>Reference #</th>
                  <th>Payment Date</th>
                  <th>Received By</th>
                  <th>Status</th>
                  <th class="text-center">Receipt</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pay in payments" :key="pay.id">
                  <td class="font-mono font-bold nowrap-cell">{{ pay.receipt_number }}</td>
                  <td>
                    <strong>{{ pay.student_name }}</strong>
                    <span class="subtext">Adm: {{ pay.student_admission_number }}</span>
                  </td>
                  <td class="font-mono nowrap-cell">{{ pay.invoice_number }}</td>
                  <td class="text-right font-bold text-success nowrap-cell">${{ Number(pay.amount_paid).toFixed(2) }}</td>
                  <td><span class="payment-method-pill">{{ pay.payment_method }}</span></td>
                  <td class="font-mono nowrap-cell">{{ pay.reference_number || '—' }}</td>
                  <td class="nowrap-cell">{{ pay.payment_date }}</td>
                  <td>{{ pay.recorded_by_name || 'Administrator' }}</td>
                  <td>
                    <StatusBadge :status="pay.status" :variant="pay.status === 'VERIFIED' ? 'success' : 'danger'" />
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm btn-outline" @click="viewReceipt(pay.id)">
                      <i class="pi pi-print"></i> View Receipt
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-finance-cards">
            <article v-for="pay in payments" :key="'m-fpay-' + pay.id" class="mobile-finance-card">
              <div class="mfc-head">
                <div>
                  <div class="mfc-title">{{ pay.student_name }}</div>
                  <div class="mfc-sub font-mono">{{ pay.receipt_number }} &bull; {{ pay.invoice_number }}</div>
                </div>
                <StatusBadge :status="pay.status" :variant="pay.status === 'VERIFIED' ? 'success' : 'danger'" />
              </div>
              <div class="mfc-kv-grid">
                <div class="mfc-kv">
                  <span class="mfc-lbl">Amount Paid</span>
                  <span class="mfc-val text-success">${{ Number(pay.amount_paid).toFixed(2) }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Method</span>
                  <span class="mfc-val">{{ pay.payment_method }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Payment Date</span>
                  <span class="mfc-val">{{ pay.payment_date }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Received By</span>
                  <span class="mfc-val">{{ pay.recorded_by_name || 'Administrator' }}</span>
                </div>
              </div>
              <div class="mfc-actions">
                <button class="btn-row-action btn-view mfc-btn" @click="viewReceipt(pay.id)">
                  <i class="pi pi-print"></i> View Receipt
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 4: CLASS FINANCIAL VIEW & ENROLLED STUDENTS -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'classes'" class="tab-pane">
        <div class="pane-header-actions">
          <div>
            <h3>Class-Wise Financial Breakdown & Student Enrolled View</h3>
            <p class="subtext">Authoritative PostgreSQL enrollments for {{ filters.education_level }} &bull; {{ filters.academic_year }}</p>
          </div>
          <div v-if="selectedClassFinancial" class="quick-actions">
            <button class="btn btn-outline" @click="selectedClassFinancial = null; filters.class_id = ''">
              <i class="pi pi-arrow-left"></i> Back to All Classes Overview
            </button>
          </div>
        </div>

        <!-- If a specific class is selected: show authoritative class financial breakdown & students -->
        <div v-if="selectedClassFinancial" class="selected-class-financial-view">
          <div class="class-kpi-summary-strip">
            <div class="class-summary-hero">
              <h4>{{ selectedClassFinancial.class_name }}</h4>
              <span class="badge-tag">{{ filters.education_level }} &bull; {{ selectedClassFinancial.academic_year }}</span>
            </div>
            <div class="class-kpi-cards">
              <div class="mini-kpi">
                <span class="mini-kpi-label">ENROLLED STUDENTS</span>
                <strong class="mini-kpi-val">{{ selectedClassFinancial.total_students }}</strong>
              </div>
              <div class="mini-kpi">
                <span class="mini-kpi-label">TOTAL BILLED</span>
                <strong class="mini-kpi-val">${{ Number(selectedClassFinancial.total_billed).toFixed(2) }}</strong>
              </div>
              <div class="mini-kpi text-success">
                <span class="mini-kpi-label">COLLECTED</span>
                <strong class="mini-kpi-val">${{ Number(selectedClassFinancial.total_collected).toFixed(2) }}</strong>
              </div>
              <div class="mini-kpi text-warning">
                <span class="mini-kpi-label">OUTSTANDING</span>
                <strong class="mini-kpi-val">${{ Number(selectedClassFinancial.total_outstanding).toFixed(2) }}</strong>
              </div>
              <div class="mini-kpi text-danger">
                <span class="mini-kpi-label">OVERDUE</span>
                <strong class="mini-kpi-val">${{ Number(selectedClassFinancial.total_overdue).toFixed(2) }}</strong>
              </div>
            </div>
          </div>

          <div v-if="isClassStudentsLoading" class="state-container loading-state">
            <i class="pi pi-spin pi-spinner state-icon"></i>
            <p>Loading authoritative enrolled students for {{ selectedClassFinancial.class_name }}...</p>
          </div>

          <div v-else-if="selectedClassFinancial.students.length === 0" class="state-container empty-state">
            <i class="pi pi-users state-icon"></i>
            <h3>No enrolled students in this class.</h3>
            <p>Enroll students into this class under Admin Students for academic year {{ selectedClassFinancial.academic_year }}.</p>
          </div>

          <div v-else class="table-responsive mt-3" tabindex="0" role="region" aria-label="Class financial statement table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Admission #</th>
                  <th>Student Name</th>
                  <th>Class</th>
                  <th class="text-right">Total Billed</th>
                  <th class="text-right">Paid</th>
                  <th class="text-right">Balance</th>
                  <th>Status</th>
                  <th class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="st in selectedClassFinancial.students" :key="st.student_id">
                  <td class="font-mono font-bold">{{ st.admission_number }}</td>
                  <td>
                    <strong>{{ st.student_name }}</strong>
                  </td>
                  <td><span class="class-pill">{{ st.class_name }}</span></td>
                  <td class="text-right font-bold">${{ Number(st.fee_amount).toFixed(2) }}</td>
                  <td class="text-right text-success font-bold">${{ Number(st.paid_amount).toFixed(2) }}</td>
                  <td class="text-right font-bold" :class="st.balance > 0 ? 'text-danger' : 'text-success'">
                    ${{ Number(st.balance).toFixed(2) }}
                  </td>
                  <td>
                    <StatusBadge
                      :status="st.status"
                      :variant="st.status === 'PAID' ? 'success' : st.status === 'PARTIAL' ? 'warning' : 'danger'"
                    />
                  </td>
                  <td class="text-center">
                    <button
                      class="btn btn-sm btn-outline ml-1"
                      @click="openStudentFinance(st.student_id)"
                    >
                      Profile
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Otherwise show all classes overview cards -->
        <div v-else class="class-summary-grid">
          <div
            v-for="cls in classSummaries"
            :key="cls.class_id ?? cls.class_name"
            class="class-card clickable-card"
            @click="cls.class_id && onClassSelectedForFinancialView(cls.class_id)"
          >
            <div class="class-card-head">
              <h4>{{ cls.class_name }}</h4>
              <span class="students-badge">{{ cls.students_count }} Enrolled</span>
            </div>
            <div class="class-card-body">
              <div class="metric-row">
                <span>Total Billed:</span>
                <strong>${{ Number(cls.total_billed).toFixed(2) }}</strong>
              </div>
              <div class="metric-row text-success">
                <span>Total Collected:</span>
                <strong>${{ Number(cls.total_collected).toFixed(2) }}</strong>
              </div>
              <div class="metric-row text-danger">
                <span>Outstanding:</span>
                <strong>${{ Number(cls.total_outstanding).toFixed(2) }}</strong>
              </div>

              <div class="progress-bar-wrap">
                <div class="progress-info">
                  <span>Collection Rate</span>
                  <strong>{{ cls.collection_rate_percent.toFixed(1) }}%</strong>
                </div>
                <div class="progress-track">
                  <div class="progress-fill" :style="{ width: `${cls.collection_rate_percent}%` }"></div>
                </div>
              </div>
            </div>
            <div class="class-card-foot">
              <button
                class="btn btn-sm btn-primary btn-block"
                @click.stop="cls.class_id && onClassSelectedForFinancialView(cls.class_id)"
              >
                <i class="pi pi-users"></i> View {{ cls.students_count }} Students & Finance
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 5: OVERDUE & SMS REMINDERS -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'overdue'" class="tab-pane">
        <div class="pane-header-actions">
          <div>
            <h3>Overdue Accounts & Guardian SMS Communication</h3>
            <p class="subtext">Auto-identified accounts past due date with remaining balance.</p>
          </div>
          <button class="btn btn-danger" @click="openSmsModal('ALL_OVERDUE')">
            <i class="pi pi-send"></i> Send Overdue SMS Broadcast
          </button>
        </div>

        <div v-if="overdueInvoices.length === 0" class="state-container empty-state">
          <i class="pi pi-check-circle state-icon text-success"></i>
          <h3>No overdue fees.</h3>
          <p>All student fee accounts are currently up to date.</p>
        </div>

        <div v-else>
          <div class="table-responsive desktop-finance-table" tabindex="0" role="region" aria-label="Overdue fee invoices table">
            <table class="finance-table">
              <thead>
                <tr>
                  <th>Invoice #</th>
                  <th>Student</th>
                  <th>Class</th>
                  <th>Fee Type</th>
                  <th class="text-right">Total Due</th>
                  <th class="text-right">Balance Past Due</th>
                  <th>Due Date</th>
                  <th class="text-center">Guardian Alert</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in overdueInvoices" :key="inv.id">
                  <td class="font-mono font-bold nowrap-cell">{{ inv.invoice_number }}</td>
                  <td>
                    <strong>{{ inv.student_name }}</strong>
                    <span class="subtext">Adm: {{ inv.student_admission_number }}</span>
                  </td>
                  <td>{{ inv.class_name || '—' }}</td>
                  <td>{{ inv.fee_type || 'Tuition' }}</td>
                  <td class="text-right nowrap-cell">${{ Number(inv.net_amount).toFixed(2) }}</td>
                  <td class="text-right text-danger font-bold nowrap-cell">${{ Number(inv.balance_remaining).toFixed(2) }}</td>
                  <td class="text-danger font-bold nowrap-cell">{{ inv.due_date }}</td>
                  <td class="text-center">
                    <button
                      class="btn btn-sm btn-warning"
                      @click="openSmsModal('SINGLE_STUDENT', undefined, inv.student_id)"
                    >
                      <i class="pi pi-envelope"></i> Send SMS
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mobile-finance-cards">
            <article v-for="inv in overdueInvoices" :key="'m-ovd-' + inv.id" class="mobile-finance-card">
              <div class="mfc-head">
                <div>
                  <div class="mfc-title">{{ inv.student_name }}</div>
                  <div class="mfc-sub font-mono">{{ inv.invoice_number }} &bull; {{ inv.class_name || '—' }}</div>
                </div>
                <span class="mfc-due-pill">Due {{ inv.due_date }}</span>
              </div>
              <div class="mfc-kv-grid">
                <div class="mfc-kv">
                  <span class="mfc-lbl">Fee Type</span>
                  <span class="mfc-val">{{ inv.fee_type || 'Tuition' }}</span>
                </div>
                <div class="mfc-kv">
                  <span class="mfc-lbl">Balance Past Due</span>
                  <span class="mfc-val text-danger">${{ Number(inv.balance_remaining).toFixed(2) }}</span>
                </div>
              </div>
              <div class="mfc-actions">
                <button class="btn btn-sm btn-warning mfc-btn" @click="openSmsModal('SINGLE_STUDENT', undefined, inv.student_id)">
                  <i class="pi pi-envelope"></i> Send Guardian SMS
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>

      <!-- ================================================================= -->
      <!-- TAB 6: FINANCIAL REPORTS & TRENDS -->
      <!-- ================================================================= -->
      <div v-if="activeTab === 'reports'" class="tab-pane">
        <div class="pane-header-actions">
          <h3>Institutional Financial Reports & Collections Breakdown</h3>
          <div class="export-btn-group">
            <button class="btn btn-outline" @click="exportData('invoices')">
              <i class="pi pi-file-excel"></i> Export Invoices (CSV)
            </button>
            <button class="btn btn-outline" @click="exportData('payments')">
              <i class="pi pi-file-excel"></i> Export Payments (CSV)
            </button>
          </div>
        </div>

        <div class="reports-grid">
          <!-- Payment Methods Breakdown -->
          <div class="report-card">
            <h4>Payment Method Summary</h4>
            <table class="report-table">
              <thead>
                <tr>
                  <th>Method</th>
                  <th>Transactions</th>
                  <th class="text-right">Total Amount</th>
                  <th class="text-right">Share</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pm in paymentMethodsBreakdown" :key="pm.method">
                  <td><strong>{{ pm.method }}</strong></td>
                  <td>{{ pm.transaction_count }}</td>
                  <td class="text-right font-bold text-success">${{ Number(pm.total_amount).toFixed(2) }}</td>
                  <td class="text-right">{{ pm.percentage.toFixed(1) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Monthly Trends -->
          <div class="report-card">
            <h4>Monthly Collections Trend ({{ filters.academic_year }})</h4>
            <table class="report-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th class="text-right">Total Billed</th>
                  <th class="text-right">Total Collected</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="mt in monthlyTrends" :key="mt.month">
                  <td><strong>{{ mt.month }}</strong></td>
                  <td class="text-right font-bold">${{ Number(mt.billed).toFixed(2) }}</td>
                  <td class="text-right font-bold text-success">${{ Number(mt.collected).toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 1: NEW / EDIT FEE STRUCTURE -->
    <!-- ================================================================= -->
    <div v-if="isStructureModalOpen" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ isEditingStructure ? 'Edit Fee Structure' : 'Create New Fee Structure' }}</h3>
          <button class="modal-close" @click="isStructureModalOpen = false">&times;</button>
        </div>
        <form @submit.prevent="submitStructureForm" class="modal-body">
          <div class="form-group">
            <label class="required">Fee Name:</label>
            <input type="text" v-model="structureForm.name" required placeholder="e.g. Monthly Tuition Fee" class="form-input" />
          </div>

          <!-- EDUCATION LEVEL SELECTOR (PRIMARY / SECONDARY) -->
          <div class="form-group">
            <label class="required">Education Level:</label>
            <div class="radio-cards-group">
              <label class="radio-card">
                <input
                  type="radio"
                  v-model="structureForm.education_level"
                  value="PRIMARY"
                  @change="updateStructureClasses"
                />
                <span><i class="pi pi-book"></i> PRIMARY (Grade 1 - 8)</span>
              </label>
              <label class="radio-card">
                <input
                  type="radio"
                  v-model="structureForm.education_level"
                  value="SECONDARY"
                  @change="updateStructureClasses"
                />
                <span><i class="pi pi-graduation-cap"></i> SECONDARY (Form 1 - 4)</span>
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="required">Academic Year:</label>
              <select v-model="structureForm.academic_year" @change="updateStructureClasses" class="form-select" required>
                <option v-for="yr in academicYears" :key="yr" :value="yr">{{ yr }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="required">Fee Scope / Application:</label>
              <select v-model="structureClassSelectionMode" class="form-select">
                <option value="ALL">All {{ structureForm.education_level }} Classes</option>
                <option value="SINGLE">Single Specific Class</option>
                <option value="MULTIPLE">Multiple Selected Classes</option>
              </select>
            </div>
          </div>

          <!-- Single Class Selector -->
          <div v-if="structureClassSelectionMode === 'SINGLE'" class="form-group">
            <label class="required">Select Specific Class:</label>
            <select v-model="structureForm.class_id" class="form-select" required>
              <option :value="null" disabled>-- Select Class --</option>
              <option v-for="c in structureAvailableClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <!-- Multiple Classes Checkbox Grid -->
          <div v-if="structureClassSelectionMode === 'MULTIPLE'" class="form-group">
            <label class="required">Select Applicable Classes:</label>
            <div class="multi-classes-selector-grid">
              <label v-for="c in structureAvailableClasses" :key="c.id" class="checkbox-pill">
                <input type="checkbox" :value="c.id" v-model="structureForm.class_ids" />
                <span>{{ c.name }}</span>
              </label>
            </div>
            <span v-if="structureForm.class_ids && structureForm.class_ids.length > 0" class="subtext">
              {{ structureForm.class_ids.length }} classes selected
            </span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="required">Amount ($):</label>
              <input type="number" step="0.01" min="0.01" v-model="structureForm.amount" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="required">Frequency:</label>
              <select v-model="structureForm.frequency" class="form-select" required>
                <option value="Monthly">Monthly</option>
                <option value="Term">Term</option>
                <option value="Semester">Semester</option>
                <option value="Annual">Annual</option>
                <option value="One-Time">One-Time</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="required">Due Date:</label>
              <input type="date" v-model="structureForm.due_date" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Status:</label>
              <select v-model="structureForm.status" class="form-select">
                <option value="ACTIVE">ACTIVE</option>
                <option value="INACTIVE">INACTIVE</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Description / Notes:</label>
            <textarea v-model="structureForm.description" rows="2" class="form-input" placeholder="Optional notes about this fee..."></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="isStructureModalOpen = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'Saving...' : 'Save Fee Structure' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 2: ASSIGN FEE TO STUDENTS / CLASS -->
    <!-- ================================================================= -->
    <div v-if="isAssignModalOpen" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Assign Fee Structure to Students</h3>
          <button class="modal-close" @click="isAssignModalOpen = false">&times;</button>
        </div>
        <form @submit.prevent="submitAssignForm" class="modal-body">
          <div class="form-group">
            <label class="required">Select Fee Structure:</label>
            <select v-model="assignForm.fee_structure_id" class="form-select" required>
              <option :value="0" disabled>-- Select Structure --</option>
              <option v-for="s in feeStructures" :key="s.id" :value="s.id">
                {{ s.name }} (${{ Number(s.amount).toFixed(2) }} &bull; {{ s.frequency }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="required">Assignment Target:</label>
            <div class="radio-cards-group">
              <label class="radio-card">
                <input type="radio" v-model="assignForm.target_type" value="CLASS" />
                <span>Entire Class</span>
              </label>
              <label class="radio-card">
                <input type="radio" v-model="assignForm.target_type" value="SINGLE_STUDENT" />
                <span>Single Student</span>
              </label>
            </div>
          </div>

          <div v-if="assignForm.target_type === 'CLASS'" class="form-group">
            <label class="required">Target Class:</label>
            <select v-model="assignForm.class_id" class="form-select" required>
              <option :value="null" disabled>-- Select Class --</option>
              <option v-for="c in availableClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div v-if="assignForm.target_type === 'SINGLE_STUDENT'" class="form-group">
            <label class="required">Target Student:</label>
            <select v-model="assignForm.student_id" class="form-select" required>
              <option :value="null" disabled>-- Select Student --</option>
              <option v-for="st in availableStudents" :key="st.student_id || st.id" :value="st.student_id || st.id">
                {{ st.full_name || (st.first_name + ' ' + st.last_name) }} (Adm: {{ st.admission_number }}) &bull; {{ st.class_name || '' }}
              </option>
            </select>
          </div>

          <!-- Live Total Calculation Preview -->
          <div class="calculation-preview-box">
            <div class="calc-row">
              <span>Target Students:</span>
              <strong>{{ targetStudentsCount }} students</strong>
            </div>
            <div class="calc-row">
              <span>Amount per Student:</span>
              <strong>${{ unitFeeAmount.toFixed(2) }}</strong>
            </div>
            <div class="calc-total-row">
              <span>Total Amount to be Invoiced:</span>
              <strong class="text-success">${{ totalCalculatedBill.toFixed(2) }}</strong>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="isAssignModalOpen = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting || targetStudentsCount === 0">
              {{ isSubmitting ? 'Generating Invoices...' : 'Confirm Assignment' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 3: RECORD PAYMENT -->
    <!-- ================================================================= -->
    <div v-if="isPaymentModalOpen" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Record Verified Student Fee Payment</h3>
          <button class="modal-close" @click="isPaymentModalOpen = false">&times;</button>
        </div>
        <form @submit.prevent="submitPaymentForm" class="modal-body">
          <div class="form-group">
            <label class="required">Select Student Invoice:</label>
            <select
              v-model="paymentForm.student_fee_id"
              class="form-select"
              @change="onInvoiceSelectInPaymentModal(paymentForm.student_fee_id)"
              required
            >
              <option :value="0" disabled>-- Select Invoice --</option>
              <option v-for="inv in invoices" :key="inv.id" :value="inv.id">
                {{ inv.invoice_number }} &bull; {{ inv.student_name }} (Due: ${{ Number(inv.balance_remaining).toFixed(2) }})
              </option>
            </select>
          </div>

          <div v-if="selectedInvoiceForPayment" class="invoice-highlight-card">
            <div>Student: <strong>{{ selectedInvoiceForPayment.student_name }}</strong> ({{ selectedInvoiceForPayment.student_admission_number }})</div>
            <div>Fee: <strong>{{ selectedInvoiceForPayment.fee_type }}</strong> &bull; {{ selectedInvoiceForPayment.academic_year }}</div>
            <div class="balance-line">
              Remaining Balance: <strong class="text-danger">${{ Number(selectedInvoiceForPayment.balance_remaining).toFixed(2) }}</strong>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="required">Amount Paid ($):</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                v-model="paymentForm.amount_paid"
                required
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label class="required">Payment Method:</label>
              <select v-model="paymentForm.payment_method" class="form-select" required>
                <option value="EVC_PLUS">EVC Plus</option>
                <option value="EDAHAB">eDahab</option>
                <option value="ZAAD">ZAAD</option>
                <option value="SAHAL">Sahal</option>
                <option value="CASH">Cash</option>
                <option value="BANK_TRANSFER">Bank Transfer</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="required">Payment Date:</label>
              <input type="date" v-model="paymentForm.payment_date" required class="form-input" />
            </div>
            <div class="form-group">
              <label>Reference # / Gateway Code:</label>
              <input type="text" v-model="paymentForm.reference_number" placeholder="e.g. TXN-998822" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label>Notes / Receipt Comments:</label>
            <textarea v-model="paymentForm.notes" rows="2" class="form-input" placeholder="Optional cashier notes..."></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="isPaymentModalOpen = false">Cancel</button>
            <button type="submit" class="btn btn-success" :disabled="isSubmitting">
              {{ isSubmitting ? 'Recording & Generating Receipt...' : 'Record Payment & Print Receipt' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 4: OFFICIAL SINGLE-PAGE PRINTABLE RECEIPT -->
    <!-- ================================================================= -->
    <div v-if="isReceiptModalOpen && currentReceipt" class="modal-backdrop">
      <div class="modal-dialog receipt-dialog">
        <div class="modal-header no-print">
          <h3>Official Payment Receipt</h3>
          <div class="modal-header-actions">
            <button class="btn btn-primary btn-sm" @click="printReceipt">
              <i class="pi pi-print"></i> Print Receipt / Save PDF
            </button>
            <button class="modal-close" @click="isReceiptModalOpen = false">&times;</button>
          </div>
        </div>

        <div class="receipt-printable-area" id="receipt-print-container">
          <!-- Receipt Header -->
          <div class="receipt-header">
            <div class="school-brand">
              <h2>{{ currentReceipt.school_name }}</h2>
              <p class="school-meta">Mogadishu, Somalia &bull; Email: finance@ems.edu.so &bull; Tel: +252 61 500 0000</p>
            </div>
            <div class="receipt-badge-wrap">
              <div class="receipt-badge">OFFICIAL RECEIPT</div>
              <div class="receipt-no">{{ currentReceipt.receipt_number }}</div>
            </div>
          </div>

          <div class="receipt-divider"></div>

          <!-- Receipt Details Grid -->
          <div class="receipt-details-grid">
            <div class="receipt-col">
              <div class="detail-row"><span>Student Name:</span> <strong>{{ currentReceipt.student_name }}</strong></div>
              <div class="detail-row"><span>Admission No:</span> <strong>{{ currentReceipt.admission_number }}</strong></div>
              <div class="detail-row"><span>Class:</span> <strong>{{ currentReceipt.class_name }}</strong></div>
              <div class="detail-row"><span>Academic Year:</span> <strong>{{ currentReceipt.academic_year }}</strong></div>
              <div class="detail-row" v-if="currentReceipt.guardian_name"><span>Guardian:</span> <strong>{{ currentReceipt.guardian_name }}</strong></div>
            </div>
            <div class="receipt-col">
              <div class="detail-row"><span>Invoice No:</span> <strong>{{ currentReceipt.invoice_number }}</strong></div>
              <div class="detail-row"><span>Fee Type:</span> <strong>{{ currentReceipt.fee_type }}</strong></div>
              <div class="detail-row"><span>Payment Date:</span> <strong>{{ currentReceipt.payment_date }}</strong></div>
              <div class="detail-row"><span>Payment Method:</span> <strong>{{ currentReceipt.payment_method }}</strong></div>
              <div class="detail-row"><span>Reference Code:</span> <strong>{{ currentReceipt.reference_number || 'N/A' }}</strong></div>
            </div>
          </div>

          <!-- Payment Financial Breakdown Table -->
          <table class="receipt-financial-table">
            <thead>
              <tr>
                <th>Description</th>
                <th class="text-right">Total Invoiced</th>
                <th class="text-right">Amount Paid</th>
                <th class="text-right">Remaining Balance</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{{ currentReceipt.fee_type }} ({{ currentReceipt.academic_year }})</td>
                <td class="text-right">${{ Number(currentReceipt.net_amount).toFixed(2) }}</td>
                <td class="text-right text-success font-bold">${{ Number(currentReceipt.amount_paid).toFixed(2) }}</td>
                <td class="text-right font-bold text-danger">${{ Number(currentReceipt.remaining_balance).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Receipt Footer Signatures -->
          <div class="receipt-sign-grid">
            <div class="sign-block">
              <div class="sign-line"></div>
              <span>Received By ({{ currentReceipt.recorded_by }})</span>
            </div>
            <div class="sign-block text-right">
              <div class="stamp-box">OFFICIALLY VERIFIED<br />FINANCE OFFICE</div>
            </div>
          </div>
        </div>

        <div class="modal-footer no-print">
          <button class="btn btn-outline" @click="isReceiptModalOpen = false">Close</button>
          <button class="btn btn-primary" @click="printReceipt">
            <i class="pi pi-print"></i> Print Receipt
          </button>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 5: STUDENT FINANCIAL DETAILS PROFILE (REDESIGNED PREMIUM) -->
    <!-- ================================================================= -->
    <StudentFinancialProfileModal
      :is-open="isStudentFinanceModalOpen"
      :student-id="selectedStudentIdForProfile"
      :academic-year="filters.academic_year"
      @close="isStudentFinanceModalOpen = false"
    />

    <!-- ================================================================= -->
    <!-- MODAL 6: BULK SMS FEE REMINDER -->
    <!-- ================================================================= -->
    <div v-if="isSmsModalOpen" class="modal-backdrop">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Guardian Fee SMS Communication (Hormuud Gateway)</h3>
          <button class="modal-close" @click="isSmsModalOpen = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="required">Template Type:</label>
            <select v-model="smsForm.template_type" @change="fetchSmsPreview" class="form-select">
              <option value="OVERDUE_FEE">Overdue Fee Notice (Somali)</option>
              <option value="FEE_REMINDER">General Fee Reminder</option>
              <option value="PAYMENT_CONFIRMATION">Payment Confirmation</option>
            </select>
          </div>

          <div v-if="isSmsPreviewLoading" class="preview-loading">
            <i class="pi pi-spin pi-spinner"></i> Resolving PostgreSQL guardian contacts...
          </div>

          <div v-else-if="smsPreviewData" class="sms-preview-summary-box">
            <div class="sms-stat-row">
              <span>Total Students Target:</span>
              <strong>{{ smsPreviewData.total_students }}</strong>
            </div>
            <div class="sms-stat-row text-success">
              <span>Eligible Contacts (Somali Mobile #):</span>
              <strong>{{ smsPreviewData.eligible_count }}</strong>
            </div>
            <div class="sms-stat-row text-warning" v-if="smsPreviewData.missing_phone_count > 0">
              <span>Missing Contacts:</span>
              <strong>{{ smsPreviewData.missing_phone_count }}</strong>
            </div>
            <div class="sms-stat-row">
              <span>Total Outstanding Balance:</span>
              <strong class="text-danger">${{ smsPreviewData.total_outstanding_amount.toFixed(2) }}</strong>
            </div>

            <!-- Preview sample SMS -->
            <div class="sample-sms-box" v-if="smsPreviewData.recipients.length > 0">
              <label>Message Preview Sample:</label>
              <p>{{ smsPreviewData.recipients[0].preview_message }}</p>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="isSmsModalOpen = false">Cancel</button>
            <button
              type="button"
              class="btn btn-warning"
              :disabled="isSubmitting || !smsPreviewData || smsPreviewData.eligible_count === 0"
              @click="sendFeeSmsBroadcast"
            >
              {{ isSubmitting ? 'Sending via Hormuud Gateway...' : `Send SMS to ${smsPreviewData?.eligible_count ?? 0} Guardians` }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ================================================================= -->
  <!-- DELETE FEE STRUCTURE CONFIRM MODAL                                -->
  <!-- ================================================================= -->
  <div v-if="deleteConfirmStructure" class="modal-backdrop delete-confirm-backdrop" @click.self="deleteConfirmStructure = null">
    <div class="modal-dialog delete-confirm-dialog">
      <div class="delete-confirm-icon">
        <i class="pi pi-trash"></i>
      </div>
      <h3 class="delete-confirm-title">Delete Fee Structure?</h3>
      <p class="delete-confirm-body">
        You are about to permanently delete:
        <strong>{{ deleteConfirmStructure.name }}</strong>
      </p>
      <p v-if="deleteConfirmStructure.assigned_count > 0" class="delete-confirm-warning">
        <i class="pi pi-exclamation-triangle"></i>
        This structure has <strong>{{ deleteConfirmStructure.assigned_count }}</strong> assigned student invoice(s).
        Deleting it will only remove the structure template — existing invoices will be unaffected.
      </p>
      <p v-else class="delete-confirm-safe">
        <i class="pi pi-check-circle"></i>
        No students are assigned to this structure. It is safe to delete.
      </p>
      <div class="delete-confirm-actions">
        <button class="btn btn-outline" @click="deleteConfirmStructure = null" :disabled="isDeleting">
          Cancel
        </button>
        <button class="btn btn-danger" @click="deleteStructure" :disabled="isDeleting">
          <i :class="['pi', isDeleting ? 'pi-spin pi-spinner' : 'pi-trash']"></i>
          {{ isDeleting ? 'Deleting...' : 'Yes, Delete Structure' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* =========================================================================
   CONTAINER & LAYOUT
   ========================================================================= */
.fees-container {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 1.5rem;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1.25rem;
}

.badge-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* =========================================================================
   BUTTONS & ALERTS
   ========================================================================= */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-primary { background: #2563eb; color: #ffffff; }
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary { background: #475569; color: #ffffff; }
.btn-secondary:hover { background: #334155; }
.btn-success { background: #10b981; color: #ffffff; }
.btn-success:hover { background: #059669; }
.btn-warning { background: #f59e0b; color: #ffffff; }
.btn-warning:hover { background: #d97706; }
.btn-danger { background: #ef4444; color: #ffffff; }
.btn-danger:hover { background: #dc2626; }
.btn-dark { background: #1e293b; color: #ffffff; }
.btn-dark:hover { background: #0f172a; }
.btn-outline { background: #ffffff; border-color: #cbd5e1; color: #334155; }
.btn-outline:hover { background: #f1f5f9; }
.btn-sm { padding: 0.35rem 0.65rem; font-size: 0.8rem; }
.btn-block { width: 100%; justify-content: center; }

.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1.25rem;
  border-radius: 0.5rem;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
}
.alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.alert-close { margin-left: auto; background: none; border: none; font-size: 1.25rem; cursor: pointer; color: inherit; }

/* =========================================================================
   KPI CARDS GRID
   ========================================================================= */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #ffffff;
  padding: 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.kpi-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 0.65rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  flex-shrink: 0;
}

.kpi-card.billed .kpi-icon-wrap { background: #eff6ff; color: #2563eb; }
.kpi-card.rate .kpi-icon-wrap { background: #f3e8ff; color: #9333ea; }
.kpi-card.expected .kpi-icon-wrap { background: #e0e7ff; color: #4338ca; }
.kpi-card.collected .kpi-icon-wrap { background: #ecfdf5; color: #10b981; }
.kpi-card.outstanding .kpi-icon-wrap { background: #fffbeb; color: #f59e0b; }
.kpi-card.overdue .kpi-icon-wrap { background: #fef2f2; color: #ef4444; }
.kpi-card.month .kpi-icon-wrap { background: #f0fdfa; color: #06b6d4; }

/* =========================================================================
   RECONCILIATION PANEL
   ========================================================================= */
.reconciliation-panel {
  background: #ffffff;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  padding: 1.1rem 1.35rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.reconciliation-panel.is-reconciled {
  border-left: 5px solid #10b981;
}
.reconciliation-panel.is-warning {
  border-left: 5px solid #ef4444;
  background: #fffafa;
}
.recon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  margin-bottom: 0.85rem;
}
.recon-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: #1e293b;
  min-width: 0;
}
.recon-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.badge-success {
  background: #dcfce7;
  color: #15803d;
}
.badge-danger {
  background: #fee2e2;
  color: #b91c1c;
}
.recon-body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.recon-equation {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f8fafc;
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}
.recon-col {
  display: flex;
  flex-direction: column;
}
.r-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}
.r-val {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
}
.r-op {
  font-size: 1.25rem;
  font-weight: 700;
  color: #94a3b8;
}
.recon-check-box {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.recon-badge-line {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #166534;
  background: #f0fdf4;
  padding: 0.35rem 0.75rem;
  border-radius: 0.4rem;
  border: 1px solid #bbf7d0;
}
.recon-badge-line.student-check {
  color: #1e40af;
  background: #eff6ff;
  border-color: #bfdbfe;
}
.recon-warning-strip {
  margin-top: 0.75rem;
  padding: 0.6rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.4rem;
  color: #991b1b;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* =========================================================================
   STATUS FILTER PILLS
   ========================================================================= */
.header-tools-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.status-filter-pills {
  display: inline-flex;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 0.5rem;
  gap: 0.25rem;
}
.filter-pill {
  padding: 0.35rem 0.75rem;
  border-radius: 0.35rem;
  border: none;
  background: none;
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}
.filter-pill.active {
  background: #ffffff;
  color: #2563eb;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.pane-subtitle {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.kpi-body {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.05em;
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0.15rem 0;
}

.kpi-foot {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* =========================================================================
   TABS NAV BAR
   ========================================================================= */
.tabs-nav-bar {
  display: flex;
  overflow-x: auto;
  border-bottom: 2px solid #e2e8f0;
  margin-bottom: 1.25rem;
  gap: 0.5rem;
}

.tab-nav-btn {
  padding: 0.75rem 1.1rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.2s ease;
}

.tab-nav-btn:hover {
  color: #2563eb;
}

.tab-nav-btn.active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}

/* =========================================================================
   FILTER BAR & CONTENT
   ========================================================================= */
.filter-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  background: #ffffff;
  padding: 1rem;
  border-radius: 0.65rem;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.25rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.filter-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
}

.search-input-group {
  flex: 1 1 200px;
  min-width: 0;
}

.form-select, .form-input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.4rem;
  border: 1px solid #cbd5e1;
  font-size: 0.85rem;
  background: #ffffff;
  color: #1e293b;
}

.input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon-wrap i {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
}

.input-icon-wrap input {
  padding-left: 2rem;
  width: 100%;
}

/* =========================================================================
   TABLES & STATES
   ========================================================================= */
.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  background: #ffffff;
  border-radius: 0.65rem;
  border: 1px solid #e2e8f0;
}

.finance-table {
  width: 100%;
  min-width: 820px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.85rem;
}

.finance-table th {
  background: #f8fafc;
  padding: 0.75rem 1rem;
  font-weight: 700;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.finance-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}

.finance-table tr:hover {
  background: #f8fafc;
}

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-success { color: #10b981; }
.text-warning { color: #f59e0b; }
.text-danger { color: #ef4444; }
.text-info { color: #06b6d4; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 700; }

.subtext {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
}

.student-link {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  color: #2563eb;
  text-decoration: none;
}
.student-link:hover { text-decoration: underline; }

.row-actions {
  display: inline-flex;
  gap: 0.4rem;
}

.btn-row-action {
  padding: 0.3rem 0.5rem;
  border-radius: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}
.btn-pay { background: #ecfdf5; border-color: #a7f3d0; color: #065f46; }
.btn-view { background: #f1f5f9; color: #334155; }

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  font-size: 0.85rem;
  color: #64748b;
  border-top: 1px solid #e2e8f0;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-page {
  padding: 0.35rem 0.75rem;
  border-radius: 0.35rem;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  cursor: pointer;
}
.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.state-container {
  padding: 3rem 1.5rem;
  text-align: center;
  background: #ffffff;
  border-radius: 0.65rem;
  border: 1px solid #e2e8f0;
}
.state-icon {
  font-size: 2.5rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}
.empty-state h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
}
.empty-state p {
  color: #64748b;
  margin-bottom: 1.25rem;
}

/* =========================================================================
   STRUCTURES & CLASSES GRIDS
   ========================================================================= */
.structures-grid, .class-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.structure-card, .class-card {
  background: #ffffff;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.struct-head, .class-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.struct-title-wrap h4, .class-card-head h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: #0f172a;
}

.freq-tag, .students-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  background: #f1f5f9;
  color: #475569;
  padding: 0.15rem 0.45rem;
  border-radius: 0.25rem;
}

.struct-amount {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2563eb;
  margin-bottom: 0.5rem;
}

.struct-desc {
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.struct-meta {
  font-size: 0.75rem;
  color: #475569;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1.25rem;
}

.struct-actions {
  margin-top: auto;
  display: flex;
  gap: 0.5rem;
}

.class-card-body .metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  padding: 0.3rem 0;
  border-bottom: 1px dashed #f1f5f9;
}

.progress-bar-wrap {
  margin-top: 0.85rem;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}
.progress-track {
  height: 6px;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #10b981;
}

.pane-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

/* =========================================================================
   REPORTS & BREAKDOWN
   ========================================================================= */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
  gap: 1.5rem;
}
.report-card {
  background: #ffffff;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  padding: 1.25rem;
  min-width: 0;
}
.report-card h4 {
  margin: 0 0 1rem 0;
  color: #0f172a;
}
.nowrap-cell {
  white-space: nowrap;
}

.mobile-finance-cards {
  display: none;
  flex-direction: column;
  gap: 0.75rem;
}

.mobile-finance-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.mfc-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mfc-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  cursor: pointer;
}

.mfc-sub {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.1rem;
}

.mfc-due-pill {
  font-size: 0.72rem;
  font-weight: 700;
  color: #dc2626;
  background: #fef2f2;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  white-space: nowrap;
}

.mfc-kv-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem 0.75rem;
  padding: 0.55rem 0;
  border-top: 1px dashed #e2e8f0;
  border-bottom: 1px dashed #e2e8f0;
}

.mfc-kv {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.mfc-lbl {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
}

.mfc-val {
  font-size: 0.84rem;
  font-weight: 700;
  color: #0f172a;
  white-space: nowrap;
}

.mfc-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mfc-btn {
  flex: 1 1 120px;
  min-height: 40px;
  justify-content: center;
}

.report-table {
  width: 100%;
  min-width: 420px;
  font-size: 0.85rem;
  border-collapse: collapse;
}
.report-table th, .report-table td {
  padding: 0.65rem 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

/* =========================================================================
   MODALS & PRINTABLE RECEIPT
   ========================================================================= */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 9999;
}

.modal-dialog {
  background: #ffffff;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 580px;
  max-height: calc(100dvh - 1.5rem);
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.modal-large { max-width: 800px; }
.receipt-dialog { max-width: 680px; }

.modal-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 { margin: 0; font-size: 1.15rem; color: #0f172a; }
.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: #64748b;
  min-width: 40px;
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  background: #f8fafc;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #334155;
}
.required::after { content: ' *'; color: #ef4444; }

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.radio-cards-group {
  display: flex;
  gap: 1rem;
}
.radio-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.calculation-preview-box {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 0.85rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
}
.calc-row {
  display: flex;
  justify-content: space-between;
  color: #166534;
  margin-bottom: 0.25rem;
}
.calc-total-row {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #bbf7d0;
  padding-top: 0.4rem;
  font-size: 0.95rem;
}

.invoice-highlight-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 0.75rem;
  border-radius: 0.4rem;
  font-size: 0.85rem;
}

/* =========================================================================
   OFFICIAL PRINTABLE RECEIPT STYLES
   ========================================================================= */
.receipt-printable-area {
  padding: 2rem;
  background: #ffffff;
  color: #0f172a;
  font-family: inherit;
}

.receipt-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.school-brand h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.3rem;
  color: #1e3a8a;
}
.school-meta {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}
.receipt-badge-wrap { text-align: right; }
.receipt-badge {
  font-size: 0.75rem;
  font-weight: 800;
  background: #10b981;
  color: #ffffff;
  padding: 0.2rem 0.6rem;
  border-radius: 0.25rem;
  display: inline-block;
}
.receipt-no {
  font-family: monospace;
  font-weight: 700;
  font-size: 1rem;
  margin-top: 0.35rem;
}
.receipt-divider {
  height: 2px;
  background: #e2e8f0;
  margin: 1.25rem 0;
}
.receipt-details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}
.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px dotted #e2e8f0;
}
.receipt-financial-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin-bottom: 2rem;
}
.receipt-financial-table th {
  background: #f1f5f9;
  padding: 0.6rem 0.75rem;
  border-top: 1px solid #cbd5e1;
  border-bottom: 1px solid #cbd5e1;
}
.receipt-financial-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}
.receipt-sign-grid {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 3rem;
}
.sign-block { width: 200px; text-align: center; }
.sign-line {
  border-bottom: 1px solid #0f172a;
  margin-bottom: 0.35rem;
}
.stamp-box {
  border: 2px dashed #10b981;
  color: #10b981;
  font-weight: 800;
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  display: inline-block;
  transform: rotate(-5deg);
}

/* =========================================================================
   SMS PREVIEW STYLES
   ========================================================================= */
.sms-preview-summary-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
}
.sms-stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0;
}
.sample-sms-box {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 0.4rem;
}
.sample-sms-box p {
  margin: 0.35rem 0 0 0;
  font-size: 0.8rem;
  color: #334155;
  font-style: italic;
}

/* =========================================================================
   MEDIA QUERIES FOR MOBILE RESPONSIVENESS & PRINT
   ========================================================================= */
@media print {
  body * {
    visibility: hidden;
  }
  .receipt-printable-area, .receipt-printable-area * {
    visibility: visible;
  }
  .receipt-printable-area {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 0;
  }
  .no-print {
    display: none !important;
  }
}

/* =========================================================================
   LEVEL HIERARCHY BAR & TOGGLE
   ========================================================================= */
.level-hierarchy-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
.level-selector-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.level-label {
  color: #94a3b8;
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}
.level-pill-toggle {
  display: inline-flex;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.25rem;
  border-radius: 9999px;
  gap: 0.25rem;
}
.level-btn {
  background: transparent;
  border: none;
  color: #cbd5e1;
  padding: 0.5rem 1.25rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.level-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}
.level-btn.active {
  background: #3b82f6;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.4);
}
.level-meta-info .active-badge {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  padding: 0.4rem 0.85rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
}

/* =========================================================================
   OUTSTANDING TAB & MINI KPIS
   ========================================================================= */
.outstanding-kpi-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  background: #f8fafc;
  padding: 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
}
.mini-kpi {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.mini-kpi-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.05em;
}
.mini-kpi-val {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
}
.mini-kpi.outstanding-total .mini-kpi-val {
  font-size: 1.5rem;
}
.outstanding-filter-strip {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
  background: #ffffff;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}
.class-pill {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 600;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 0.375rem;
}

/* =========================================================================
   CLASS ENROLLED STUDENTS FINANCIAL VIEW
   ========================================================================= */
.selected-class-financial-view {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.class-kpi-summary-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.25rem;
}
.class-summary-hero h4 {
  font-size: 1.4rem;
  margin: 0 0 0.35rem 0;
  color: #0f172a;
}
.class-kpi-cards {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}
.clickable-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.clickable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.1);
}

/* Multi-Class Checkbox Selection */
.multi-classes-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.5rem;
  max-height: 180px;
  overflow-y: auto;
  border: 1px solid #cbd5e1;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: #f8fafc;
}
.checkbox-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  cursor: pointer;
  background: #ffffff;
  padding: 0.35rem 0.6rem;
  border-radius: 0.375rem;
  border: 1px solid #e2e8f0;
}
.checkbox-pill:hover {
  background: #f1f5f9;
}

/* =========================================================================
   MEDIA QUERIES FOR MOBILE RESPONSIVENESS & PRINT
   ========================================================================= */
@media print {
  body * {
    visibility: hidden;
  }
  .receipt-printable-area, .receipt-printable-area * {
    visibility: visible;
  }
  .receipt-printable-area {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 0;
  }
  .no-print {
    display: none !important;
  }
}

@media (max-width: 1024px) {
  .class-kpi-summary-strip { flex-direction: column; align-items: flex-start; }
  .class-kpi-cards { width: 100%; justify-content: space-between; }
}

@media (max-width: 768px) {
  .fees-container { padding: 0.75rem; }
  .header-main { flex-direction: column; }
  .quick-actions { width: 100%; }
  .quick-actions .btn { flex: 1 1 calc(50% - 0.5rem); }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
  .kpi-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 0.85rem;
    gap: 0.55rem;
  }
  .kpi-icon-wrap {
    width: 38px;
    height: 38px;
    font-size: 1.15rem;
  }
  .kpi-value {
    font-size: clamp(1.1rem, 4vw, 1.4rem);
    white-space: nowrap;
  }
  .recon-equation {
    flex-wrap: wrap;
    width: 100%;
    gap: 0.5rem 0.75rem;
  }
  .recon-col {
    flex: 1 1 110px;
  }
  .r-op {
    display: none;
  }
  .desktop-finance-table { display: none; }
  .mobile-finance-cards { display: flex; }
  .form-row { grid-template-columns: 1fr; }
  .receipt-details-grid { grid-template-columns: 1fr; }
  .level-hierarchy-bar { flex-direction: column; align-items: stretch; }
  .level-selector-group { flex-direction: column; align-items: stretch; }
  .level-pill-toggle { width: 100%; justify-content: stretch; }
  .level-btn { flex: 1; justify-content: center; font-size: 0.78rem; padding: 0.5rem 0.5rem; }
  .tabs-nav-bar { overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; }
  .tab-nav-btn { flex-shrink: 0; font-size: 0.8rem; padding: 0.6rem 0.85rem; }
  .outstanding-kpi-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
  .table-responsive { overflow-x: auto; }
}

@media (max-width: 640px) {
  .kpi-grid > .kpi-card:last-child:nth-child(odd) {
    grid-column: 1 / -1;
  }
}

@media (max-width: 430px) {
  .quick-actions .btn { flex: 1 1 100%; }
  .outstanding-kpi-bar { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.65rem; padding: 0.85rem; }
  .mini-kpi-val { font-size: 1.2rem; }
  .level-btn { font-size: 0.75rem; }
}

/* =========================================================================
   DELETE CONFIRM MODAL
   ========================================================================= */
.delete-confirm-backdrop {
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.delete-confirm-dialog {
  background: #1e293b;
  border: 1.5px solid #ef4444;
  border-radius: 1.25rem;
  padding: 2.25rem 2rem 1.75rem;
  max-width: 440px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
  text-align: center;
  box-shadow: 0 0 60px rgba(239, 68, 68, 0.2), 0 20px 50px rgba(0, 0, 0, 0.6);
  animation: deleteConfirmIn 0.22s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes deleteConfirmIn {
  from { transform: scale(0.85); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.delete-confirm-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.15);
  border: 2px solid rgba(239, 68, 68, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.25rem;
}

.delete-confirm-icon .pi {
  font-size: 2rem;
  color: #ef4444;
}

.delete-confirm-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.delete-confirm-body {
  font-size: 0.95rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.6;
}

.delete-confirm-body strong {
  color: #f1f5f9;
  font-weight: 600;
}

.delete-confirm-warning {
  background: rgba(251, 146, 60, 0.1);
  border: 1px solid rgba(251, 146, 60, 0.35);
  border-radius: 0.6rem;
  padding: 0.65rem 0.9rem;
  font-size: 0.87rem;
  color: #fb923c;
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  text-align: left;
}

.delete-confirm-warning .pi { flex-shrink: 0; margin-top: 2px; }

.delete-confirm-safe {
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 0.6rem;
  padding: 0.65rem 0.9rem;
  font-size: 0.87rem;
  color: #4ade80;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.delete-confirm-actions {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  margin-top: 0.5rem;
}

.delete-confirm-actions .btn {
  flex: 1;
  justify-content: center;
}
</style>
