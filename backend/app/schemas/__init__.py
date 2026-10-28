from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    CurrentUserResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserProfileUpdate,
    UserResponse,
)
from app.schemas.role import (
    RoleBase,
    RoleResponse,
)
from app.schemas.admin import (
    SystemHealthResponse,
    ModuleStatus,
    DashboardOverviewResponse,
    AuditLogResponse,
)
from app.schemas.system import (
    SystemSettingBase,
    SystemSettingResponse,
    SystemSettingUpdate,
)
from app.schemas.school_class import (
    SchoolClassBase,
    SchoolClassCreate,
    SchoolClassUpdate,
    SchoolClassResponse,
)
from app.schemas.subject import (
    SubjectBase,
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
)
from app.schemas.teacher import (
    TeacherBase,
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherAssignmentCreate,
    TeacherAssignmentResponse,
)
from app.schemas.student import (
    StudentBase,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentEnrollmentCreate,
    StudentEnrollmentResponse,
)
from app.schemas.timetable import (
    TimetableBase,
    TimetableCreate,
    TimetableUpdate,
    TimetableResponse,
)
from app.schemas.fee import (
    FeeStructureBase,
    FeeStructureCreate,
    FeeStructureResponse,
    StudentFeeResponse,
    FeePaymentCreate,
    FeePaymentResponse,
    FeeFinancialSummaryResponse,
    FeeEligibleStudentItem,
    FeeEligibleStudentsResponse,
)
from app.schemas.exam import (
    ExamBase,
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ExamResultEntry,
    BulkExamResultsCreate,
    ExamResultResponse,
)
from app.schemas.teacher_portal import (
    TeacherDashboardResponse,
    TeacherClassStudentsResponse,
)
from app.schemas.student_portal import (
    StudentDashboardResponse,
    StudentClassDetailsResponse,
)

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    "CurrentUserResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserProfileUpdate",
    "UserResponse",
    "RoleBase",
    "RoleResponse",
    "SystemHealthResponse",
    "ModuleStatus",
    "DashboardOverviewResponse",
    "AuditLogResponse",
    "SystemSettingBase",
    "SystemSettingResponse",
    "SystemSettingUpdate",
    "SchoolClassBase",
    "SchoolClassCreate",
    "SchoolClassUpdate",
    "SchoolClassResponse",
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "TeacherBase",
    "TeacherCreate",
    "TeacherUpdate",
    "TeacherResponse",
    "TeacherAssignmentCreate",
    "TeacherAssignmentResponse",
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentEnrollmentCreate",
    "StudentEnrollmentResponse",
    "TimetableBase",
    "TimetableCreate",
    "TimetableUpdate",
    "TimetableResponse",
    "FeeStructureBase",
    "FeeStructureCreate",
    "FeeStructureResponse",
    "StudentFeeResponse",
    "FeePaymentCreate",
    "FeePaymentResponse",
    "FeeFinancialSummaryResponse",
    "FeeEligibleStudentItem",
    "FeeEligibleStudentsResponse",
    "ExamBase",
    "ExamCreate",
    "ExamUpdate",
    "ExamResponse",
    "ExamResultEntry",
    "BulkExamResultsCreate",
    "ExamResultResponse",
    "TeacherDashboardResponse",
    "TeacherClassStudentsResponse",
    "StudentDashboardResponse",
    "StudentClassDetailsResponse",
]
