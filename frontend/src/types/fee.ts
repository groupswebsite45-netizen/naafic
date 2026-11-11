export type FeeFrequency = 'Monthly' | 'Term' | 'Semester' | 'Annual' | 'One-Time'

export type InvoiceStatus = 'PENDING' | 'UNPAID' | 'PARTIALLY_PAID' | 'PAID' | 'OVERDUE' | 'CANCELLED'

export type PaymentMethod = 'CASH' | 'EVC_PLUS' | 'EDAHAB' | 'ZAAD' | 'SAHAL' | 'BANK_TRANSFER' | 'CHEQUE' | 'OTHER'

export type PaymentStatus = 'VERIFIED' | 'PENDING' | 'FAILED' | 'CANCELLED'

export interface FeeStructure {
  id: number
  name: string
  academic_year: string
  education_level?: string | null
  class_id?: number | null
  class_name?: string | null
  amount: number
  frequency: FeeFrequency
  due_date: string
  description?: string | null
  status: 'ACTIVE' | 'INACTIVE'
  assigned_count?: number
  created_at?: string
  updated_at?: string
}

export interface FeeStructureCreate {
  name: string
  academic_year: string
  class_id?: number | null
  class_ids?: number[] | null
  education_level?: string | null
  apply_to_all_in_level?: boolean
  amount: number
  frequency?: FeeFrequency
  due_date: string
  description?: string | null
  status?: 'ACTIVE' | 'INACTIVE'
}

export interface FeeStructureUpdate {
  name?: string
  academic_year?: string
  class_id?: number | null
  amount?: number
  frequency?: FeeFrequency
  due_date?: string
  description?: string | null
  status?: 'ACTIVE' | 'INACTIVE'
}

export interface StudentFeeInvoice {
  id: number
  invoice_number: string
  student_id: number
  student_name: string
  student_admission_number: string
  class_id?: number | null
  class_name?: string | null
  fee_structure_id: number
  fee_type?: string | null
  fee_name?: string | null
  academic_year: string
  amount_due: number
  discount_amount: number
  net_amount: number
  total_paid: number
  paid?: number
  balance_remaining: number
  balance?: number
  due_date: string
  status: InvoiceStatus
  created_at: string
  payments?: FeePayment[]
  payment_id?: number
}

export interface PaginatedInvoices {
  items: StudentFeeInvoice[]
  total: number
  skip: number
  limit: number
}

export interface FeeAssignRequest {
  target_type: 'SINGLE_STUDENT' | 'SELECTED_STUDENTS' | 'CLASS'
  fee_structure_id: number
  student_id?: number | null
  student_ids?: number[] | null
  class_id?: number | null
  academic_year?: string | null
  custom_amount?: number | null
  custom_due_date?: string | null
}

export interface FeeAssignResponse {
  success: boolean
  message: string
  created_count: number
  skipped_count: number
  total_amount_billed: number
  created_invoices: StudentFeeInvoice[]
}

export interface FeePayment {
  id: number
  student_fee_id: number
  student_id: number
  student_name: string
  student_admission_number: string
  invoice_number: string
  receipt_number: string
  amount_paid: number
  amount?: number
  payment_date: string
  payment_method: PaymentMethod
  reference_number?: string | null
  reference?: string | null
  recorded_by_name?: string | null
  notes?: string | null
  status: PaymentStatus
  created_at: string
}

export interface PaginatedPayments {
  items: FeePayment[]
  total: number
  skip: number
  limit: number
}

export interface FeePaymentCreate {
  student_fee_id: number
  amount_paid: number
  payment_date: string
  payment_method: PaymentMethod
  reference_number?: string | null
  notes?: string | null
  fee_month?: string | null
}

export interface OfficialReceipt {
  receipt_number: string
  payment_id: number
  payment_date: string
  amount_paid: number
  payment_method: PaymentMethod
  reference_number?: string | null
  recorded_by: string
  notes?: string | null
  fee_month?: string | null
  status: PaymentStatus
  school_name: string
  school_address?: string | null
  school_phone?: string | null
  school_email?: string | null
  student_id: number
  student_name: string
  admission_number: string
  class_name: string
  academic_year: string
  guardian_name?: string | null
  guardian_phone?: string | null
  invoice_number: string
  fee_type: string
  invoice_amount: number
  discount_amount: number
  net_amount: number
  total_paid_to_date: number
  remaining_balance: number
  student_admission_number?: string
  fee_name?: string
  invoice_total_amount?: number
  recorded_by_name?: string
  invoice_status: InvoiceStatus
  invoice_due_date: string
}

export interface FinancialDashboardSummary {
  total_students?: number
  fee_per_student?: number
  expected_total?: number
  total_billed: number
  total_collected: number
  total_paid?: number
  total_outstanding: number
  total_overdue: number
  this_month_collected: number
  collected_this_month?: number
  total_invoices_count: number
  paid_invoices_count: number
  partial_invoices_count: number
  unpaid_invoices_count: number
  pending_invoices_count?: number
  overdue_invoices_count: number
  total_eligible_students?: number
  primary_eligible_students?: number
  secondary_eligible_students?: number
  invoiced_students_count?: number
  unpaid_students_count?: number
  paid_students_count?: number
  unbilled_students_count?: number
  students_without_class_count?: number
  is_reconciled?: boolean
  reconciliation_difference?: number
  reconciliation_message?: string
  currency: string
  school_name: string
  academic_year_filter?: string | null
}

export interface FeeEligibleStudent {
  student_id: number
  admission_number: string
  first_name: string
  last_name: string
  full_name: string
  gender: string
  class_id?: number | null
  class_name?: string | null
  education_level?: string | null
  academic_year: string
  guardian_name?: string | null
  guardian_phone?: string | null
  status: string
  invoices_count: number
  total_billed: number
  total_paid: number
  outstanding_balance: number
  overdue_balance: number
  financial_status: 'UNBILLED' | 'PAID' | 'PARTIAL' | 'UNPAID' | 'OVERDUE'
}

export interface FeeEligibleStudentsResponse {
  total_eligible: number
  primary_count: number
  secondary_count: number
  without_class_count: number
  invoiced_count: number
  uninvoiced_count: number
  academic_year?: string | null
  education_level?: string | null
  class_id?: number | null
  items: FeeEligibleStudent[]
}

export interface ClassFinancialSummary {
  class_id?: number | null
  class_name: string
  students_count: number
  total_billed: number
  total_collected: number
  total_outstanding: number
  total_overdue: number
  collection_rate_percent: number
}

export interface PaymentMethodBreakdown {
  method: string
  total_amount: number
  transaction_count: number
  percentage: number
}

export interface MonthlyFinancialTrend {
  month: string
  billed: number
  collected: number
}

export interface FinancialAuditLog {
  id: number
  user_name: string
  action: string
  entity_type: string
  entity_id?: string | null
  amount?: number | null
  reference?: string | null
  details?: string | null
  created_at: string
}

export interface FeeSmsRecipient {
  student_id: number
  student_name: string
  admission_number: string
  class_name: string
  guardian_name: string
  guardian_phone: string
  fee_balance: number
  invoice_count: number
  is_deliverable: boolean
  preview_message: string
}

export interface FeeSmsPreviewResponse {
  total_students: number
  eligible_count: number
  missing_phone_count: number
  total_outstanding_amount: number
  template_type: string
  recipients: FeeSmsRecipient[]
}

export interface FeeSmsSendRequest {
  target_type: 'SINGLE_STUDENT' | 'SELECTED_STUDENTS' | 'CLASS' | 'ALL_OUTSTANDING' | 'ALL_OVERDUE'
  template_type: 'FEE_REMINDER' | 'OVERDUE_FEE' | 'PAYMENT_CONFIRMATION' | 'CUSTOM'
  student_id?: number | null
  student_ids?: number[] | null
  class_id?: number | null
  custom_message_template?: string | null
  academic_year?: string | null
}

export interface FeeSmsSendResponse {
  success: boolean
  message: string
  sent_count: number
  failed_count: number
  skipped_count: number
  details: Array<{
    student_id: number
    phone: string
    status: string
    message_id?: string | null
    error?: string | null
  }>
}

export interface StudentFinancialProfile {
  student_id: number
  student_name: string
  full_name?: string
  admission_number: string
  class_id?: number | null
  class_name?: string | null
  current_class?: string | null
  education_level?: string | null
  status?: string
  academic_year: string
  guardian_name?: string | null
  guardian_phone?: string | null
  total_billed?: number
  total_paid?: number
  outstanding_balance?: number
  overdue_balance?: number
  financial_summary: {
    total_billed: number
    total_paid: number
    outstanding_balance: number
    overdue_balance: number
    currency: string
  }
  invoices: StudentFeeInvoice[]
  payments: FeePayment[]
}

export interface FeeClassStudentItem {
  student_id: number
  student_name: string
  admission_number: string
  class_id: number
  class_name: string
  academic_year: string
  fee_amount: number
  paid_amount: number
  balance: number
  status: 'PAID' | 'PARTIAL' | 'UNPAID' | 'OVERDUE'
}

export interface ClassStudentsFinancial {
  class_id: number
  class_name: string
  academic_year: string
  total_students: number
  total_billed: number
  total_collected: number
  total_outstanding: number
  total_overdue: number
  students: FeeClassStudentItem[]
}

export interface OutstandingStudentItem {
  student_id: number
  student_name: string
  admission_number: string
  class_id: number
  class_name: string
  education_level: string
  academic_year: string
  fee_type?: string | null
  invoice_number?: string | null
  amount_due: number
  paid_amount: number
  balance: number
  due_date?: string | null
  status: string
}

export interface OutstandingStudentsSummary {
  academic_year?: string
  education_level?: string | null
  class_id?: number | null
  total_students: number
  paid_count: number
  partial_count: number
  unpaid_count: number
  overdue_count: number
  total_outstanding_balance: number
  items: OutstandingStudentItem[]
}
