import { apiClient } from './api'
import type {
  FeeStructure,
  FeeStructureCreate,
  FeeStructureUpdate,
  StudentFeeInvoice,
  PaginatedInvoices,
  FeeAssignRequest,
  FeeAssignResponse,
  FeePayment,
  PaginatedPayments,
  FeePaymentCreate,
  OfficialReceipt,
  FinancialDashboardSummary,
  ClassFinancialSummary,
  PaymentMethodBreakdown,
  MonthlyFinancialTrend,
  StudentFinancialProfile,
  FeeSmsPreviewResponse,
  FeeSmsSendRequest,
  FeeSmsSendResponse,
  ClassStudentsFinancial,
  OutstandingStudentsSummary,
  FeeEligibleStudentsResponse,
} from '../types/fee'

export const feeService = {
  // 1. Dashboard Financial KPI Summary
  async getSummary(params?: {
    academic_year?: string
    education_level?: string
    class_id?: number
  } | string): Promise<FinancialDashboardSummary> {
    const queryParams = typeof params === 'string' ? { academic_year: params } : (params || {})
    const res = await apiClient.get<FinancialDashboardSummary>('/fees/summary', {
      params: queryParams,
    })
    return res.data
  },

  // 2. Fee Structures
  async getFeeStructures(params?: {
    academic_year?: string
    education_level?: string
    class_id?: number
    status?: string
  }): Promise<FeeStructure[]> {
    const res = await apiClient.get<FeeStructure[]>('/fees/structures', { params })
    return res.data
  },

  async createFeeStructure(payload: FeeStructureCreate): Promise<FeeStructure> {
    const res = await apiClient.post<FeeStructure>('/fees/structures', payload)
    return res.data
  },

  async updateFeeStructure(id: number, payload: FeeStructureUpdate): Promise<FeeStructure> {
    const res = await apiClient.put<FeeStructure>(`/fees/structures/${id}`, payload)
    return res.data
  },

  async deleteFeeStructure(id: number): Promise<{ success: boolean; message: string }> {
    const res = await apiClient.delete<{ success: boolean; message: string }>(`/fees/structures/${id}`)
    return res.data
  },

  // 3. Student Invoices
  async getInvoices(params?: {
    query?: string
    class_id?: number
    education_level?: string
    student_id?: number
    fee_structure_id?: number
    status?: string
    academic_year?: string
    is_overdue_only?: boolean
    start_date?: string
    end_date?: string
    skip?: number
    limit?: number
  }): Promise<PaginatedInvoices> {
    const res = await apiClient.get<PaginatedInvoices>('/fees/invoices', { params })
    return res.data
  },

  async getInvoiceById(id: number): Promise<StudentFeeInvoice> {
    const res = await apiClient.get<StudentFeeInvoice>(`/fees/invoices/${id}`)
    return res.data
  },

  async assignFee(payload: FeeAssignRequest): Promise<FeeAssignResponse> {
    const res = await apiClient.post<FeeAssignResponse>('/fees/invoices/assign', payload)
    return res.data
  },

  // 4. Payments & Receipts
  async recordPayment(payload: FeePaymentCreate): Promise<FeePayment> {
    const res = await apiClient.post<FeePayment>('/fees/payments', payload)
    return res.data
  },

  async getPayments(params?: {
    student_fee_id?: number
    student_id?: number
    class_id?: number
    education_level?: string
    payment_method?: string
    status?: string
    academic_year?: string
    start_date?: string
    end_date?: string
    skip?: number
    limit?: number
  }): Promise<PaginatedPayments> {
    const res = await apiClient.get<PaginatedPayments>('/fees/payments', { params })
    return res.data
  },

  async getReceipt(paymentId: number): Promise<OfficialReceipt> {
    const res = await apiClient.get<OfficialReceipt>(`/fees/payments/${paymentId}/receipt`)
    return res.data
  },

  async cancelPayment(paymentId: number, reason?: string): Promise<FeePayment> {
    const res = await apiClient.post<FeePayment>(`/fees/payments/${paymentId}/cancel`, null, {
      params: reason ? { reason } : {},
    })
    return res.data
  },

  // 5. Student Financial Profile Ledger
  async getStudentFinancialProfile(studentId: number, academic_year?: string): Promise<StudentFinancialProfile> {
    const res = await apiClient.get<StudentFinancialProfile>(`/fees/students/${studentId}/financial-profile`, {
      params: academic_year ? { academic_year } : {},
    })
    return res.data
  },

  // 6. Reports & Aggregates
  async getClassSummaries(academic_year?: string, education_level?: string): Promise<ClassFinancialSummary[]> {
    const res = await apiClient.get<ClassFinancialSummary[]>('/fees/reports/class-summary', {
      params: {
        ...(academic_year ? { academic_year } : {}),
        ...(education_level ? { education_level } : {}),
      },
    })
    return res.data
  },

  async getPaymentMethodBreakdown(academic_year?: string, education_level?: string): Promise<PaymentMethodBreakdown[]> {
    const res = await apiClient.get<PaymentMethodBreakdown[]>('/fees/reports/payment-methods', {
      params: {
        ...(academic_year ? { academic_year } : {}),
        ...(education_level ? { education_level } : {}),
      },
    })
    return res.data
  },

  async getMonthlyTrends(academic_year?: string, education_level?: string): Promise<MonthlyFinancialTrend[]> {
    const res = await apiClient.get<MonthlyFinancialTrend[]>('/fees/reports/monthly-trends', {
      params: {
        ...(academic_year ? { academic_year } : {}),
        ...(education_level ? { education_level } : {}),
      },
    })
    return res.data
  },

  // 7. SMS Guardian Fee Notifications
  async previewFeeSms(params: {
    target_type: string
    template_type: string
    student_id?: number
    class_id?: number
    academic_year?: string
    education_level?: string
  }): Promise<FeeSmsPreviewResponse> {
    const res = await apiClient.get<FeeSmsPreviewResponse>('/fees/notifications/preview', { params })
    return res.data
  },

  async sendFeeSms(payload: FeeSmsSendRequest): Promise<FeeSmsSendResponse> {
    const res = await apiClient.post<FeeSmsSendResponse>('/fees/notifications/send', payload)
    return res.data
  },

  // 8. Financial CSV Export
  getExportUrl(reportType: string, academic_year?: string, class_id?: number): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    const params = new URLSearchParams({
      report_type: reportType,
      format: 'csv',
    })
    if (academic_year) params.append('academic_year', academic_year)
    if (class_id) params.append('class_id', class_id.toString())
    return `${baseUrl}/fees/export?${params.toString()}`
  },

  // 9. Canonical Class & Enrolled Students Integration (Single Source of Truth)
  async getFeeClasses(params?: {
    academic_year?: string
    education_level?: string
    has_students_only?: boolean
  }): Promise<any[]> {
    const res = await apiClient.get<any[]>('/fees/classes', { params })
    return Array.isArray(res.data) ? res.data : []
  },

  async getClassStudentsFinancial(classId: number, academicYear?: string): Promise<ClassStudentsFinancial> {
    const res = await apiClient.get<ClassStudentsFinancial>(`/fees/classes/${classId}/students`, {
      params: academicYear ? { academic_year: academicYear } : {},
    })
    return res.data
  },

  async getOutstandingStudents(params: {
    academic_year?: string
    education_level?: string
    class_id?: number
    status?: string
    query?: string
  }): Promise<OutstandingStudentsSummary> {
    const res = await apiClient.get<OutstandingStudentsSummary>('/fees/outstanding', { params })
    return res.data
  },

  // 10. Authoritative Fee-Eligible Students (Single Source of Truth)
  async getEligibleStudents(params?: {
    academic_year?: string
    education_level?: string
    class_id?: number
    query?: string
    status?: string
    skip?: number
    limit?: number
  }): Promise<FeeEligibleStudentsResponse> {
    const res = await apiClient.get<FeeEligibleStudentsResponse>('/fees/eligible-students', { params })
    return res.data
  },
}
