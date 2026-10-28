import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';

// Layouts
import AuthLayout from '../layouts/AuthLayout.vue';
import AdminLayout from '../layouts/AdminLayout.vue';
import TeacherLayout from '../layouts/TeacherLayout.vue';
import StudentLayout from '../layouts/StudentLayout.vue';
import SuperAdminLayout from '../layouts/SuperAdminLayout.vue';

// Auth & Common Views
import HomeView from '../views/public/HomeView.vue';
import LoginView from '../views/auth/LoginView.vue';
import NotFoundView from '../views/NotFoundView.vue';

// Super Admin Views
import SuperAdminDashboardView from '../views/superadmin/SuperAdminDashboardView.vue';
import InstitutionsView from '../views/superadmin/InstitutionsView.vue';
import SubscriptionsView from '../views/superadmin/SubscriptionsView.vue';
import PaymentsView from '../views/superadmin/PaymentsView.vue';
import CompanyUsersView from '../views/superadmin/CompanyUsersView.vue';
import ReportsView from '../views/superadmin/ReportsView.vue';
import SuperAdminSettingsView from '../views/superadmin/SuperAdminSettingsView.vue';
import SuperAdminInboxView from '../views/superadmin/SuperAdminInboxView.vue';

// Admin Views
import DashboardView from '../views/admin/DashboardView.vue';
import ProfileView from '../views/admin/ProfileView.vue';
import SettingsView from '../views/admin/SettingsView.vue';
import ClassesView from '../views/admin/classes/ClassesView.vue';
import ClassDetailsView from '../views/admin/classes/ClassDetailsView.vue';
import ClassPromotionView from '../views/admin/classes/ClassPromotionView.vue';
import SubjectsView from '../views/admin/subjects/SubjectsView.vue';
import SubjectDetailsView from '../views/admin/subjects/SubjectDetailsView.vue';
import TeachersView from '../views/admin/teachers/TeachersView.vue';
import TeacherDetailsView from '../views/admin/teachers/TeacherDetailsView.vue';
import StudentsView from '../views/admin/students/StudentsView.vue';
import StudentDetailsView from '../views/admin/students/StudentDetailsView.vue';
import TimetableView from '../views/admin/timetable/TimetableView.vue';
import FeesView from '../views/admin/fees/FeesView.vue';
import ExamsView from '../views/admin/exams/ExamsView.vue';
import ExamCreateView from '../views/admin/exams/ExamCreateView.vue';
import ExamProfileView from '../views/admin/exams/ExamProfileView.vue';
import AdminResultsManagementView from '../views/admin/results/AdminResultsManagementView.vue';
import ClassResultDetailView from '../views/admin/exams/results/ClassResultDetailView.vue';
import NotificationsView from '../views/admin/notifications/NotificationsView.vue';


// Teacher Views
import TeacherDashboardView from '../views/teacher/TeacherDashboardView.vue';
import TeacherClassesView from '../views/teacher/TeacherClassesView.vue';
import TeacherStudentsView from '../views/teacher/TeacherStudentsView.vue';
import TeacherAttendanceView from '../views/teacher/TeacherAttendanceView.vue';
import TeacherTimetableView from '../views/teacher/TeacherTimetableView.vue';
import TeacherExamsView from '../views/teacher/TeacherExamsView.vue';

// Student Views
import StudentDashboardView from '../views/student/StudentDashboardView.vue';
import StudentProfileView from '../views/student/StudentProfileView.vue';
import StudentClassView from '../views/student/StudentClassView.vue';
import StudentTimetableView from '../views/student/StudentTimetableView.vue';
import StudentAttendanceView from '../views/student/StudentAttendanceView.vue';
import StudentFeesView from '../views/student/StudentFeesView.vue';
import StudentExamsView from '../views/student/StudentExamsView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: {
      title: 'Somroyal Educational Management System (SEMS)',
      requiresAuth: false,
    },
  },
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'login',
        component: LoginView,
        meta: { guestOnly: true, title: 'Portal Login' },
      },
    ],
  },
  // SUPER ADMIN ROUTES (Somroyal Technology Solutions Platform Management)
  {
    path: '/super-admin',
    component: SuperAdminLayout,
    meta: { requiresAuth: true, requiresSuperAdmin: true },
    children: [
      {
        path: '',
        redirect: '/super-admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'superadmin-dashboard',
        component: SuperAdminDashboardView,
        meta: { title: 'Super Admin Dashboard - Somroyal EMS' },
      },
      {
        path: 'inbox',
        name: 'superadmin-inbox',
        component: SuperAdminInboxView,
        meta: { title: 'Inquiries & Leads Inbox - Somroyal EMS' },
      },
      {
        path: 'institutions',
        name: 'superadmin-institutions',
        component: InstitutionsView,
        meta: { title: 'Institutions Management' },
      },
      {
        path: 'subscriptions',
        name: 'superadmin-subscriptions',
        component: SubscriptionsView,
        meta: { title: 'Subscription Management' },
      },
      {
        path: 'payments',
        name: 'superadmin-payments',
        component: PaymentsView,
        meta: { title: 'Payments & Billing' },
      },
      {
        path: 'users',
        name: 'superadmin-users',
        component: CompanyUsersView,
        meta: { title: 'Users & Roles' },
      },
      {
        path: 'reports',
        name: 'superadmin-reports',
        component: ReportsView,
        meta: { title: 'Platform Reports' },
      },
      {
        path: 'settings',
        name: 'superadmin-settings',
        component: SuperAdminSettingsView,
        meta: { title: 'Platform Settings' },
      },
    ],
  },
  // ADMIN ROUTES
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: DashboardView,
        meta: { title: 'Admin Dashboard' },
      },
      {
        path: 'classes',
        name: 'admin-classes',
        component: ClassesView,
        meta: { title: 'Class Management' },
      },
      {
        path: 'class-promotion',
        name: 'admin-class-promotion',
        component: ClassPromotionView,
        meta: { title: 'Bulk Class Promotion' },
      },
      {
        path: 'classes/promotion',
        name: 'admin-classes-promotion-alias',
        component: ClassPromotionView,
        meta: { title: 'Bulk Class Promotion' },
      },
      {
        path: 'classes/:id',
        name: 'admin-class-details',
        component: ClassDetailsView,
        meta: { title: 'Class Profile' },
      },
      {
        path: 'subjects',
        name: 'admin-subjects',
        component: SubjectsView,
        meta: { title: 'Subject Management' },
      },
      {
        path: 'subjects/:id',
        name: 'admin-subject-details',
        component: SubjectDetailsView,
        meta: { title: 'Subject Profile' },
      },
      {
        path: 'teachers',
        name: 'admin-teachers',
        component: TeachersView,
        meta: { title: 'Teacher Management' },
      },
      {
        path: 'teachers/:id',
        name: 'admin-teacher-details',
        component: TeacherDetailsView,
        meta: { title: 'Teacher Profile' },
      },
      {
        path: 'students',
        name: 'admin-students',
        component: StudentsView,
        meta: { title: 'Student Management' },
      },
      {
        path: 'students/:id',
        name: 'admin-student-details',
        component: StudentDetailsView,
        meta: { title: 'Student Profile' },
      },
      {
        path: 'timetable',
        name: 'admin-timetable',
        component: TimetableView,
        meta: { title: 'Timetable Management' },
      },
      {
        path: 'fees',
        name: 'admin-fees',
        component: FeesView,
        meta: { title: 'Fees & Finance Management' },
      },
      {
        path: 'exams',
        name: 'admin-exams',
        component: ExamsView,
        meta: { title: 'Exam Management' },
      },
      {
        path: 'results',
        name: 'admin-results',
        component: AdminResultsManagementView,
        meta: { title: 'Results Management' },
      },
      {
        path: 'exams/results',
        redirect: '/admin/results',
      },
      {
        path: 'exams/results/classes/:classId',
        name: 'admin-class-result-detail',
        component: ClassResultDetailView,
        meta: { title: 'Class Result Details' },
      },
      {
        path: 'exams/submissions',
        redirect: '/admin/results',
      },
      {
        path: 'exams/create',
        name: 'admin-exam-create',
        component: ExamCreateView,
        meta: { title: 'Schedule Examination' },
      },
      {
        path: 'exams/:id',
        name: 'admin-exam-details',
        component: ExamProfileView,
        meta: { title: 'Examination Profile & Results' },
      },
      {
        path: 'notifications',
        name: 'admin-notifications',
        component: NotificationsView,
        meta: { title: 'Notifications & Guardian Communications' },
      },
      {
        path: 'profile',
        name: 'admin-profile',
        component: ProfileView,
        meta: { title: 'Admin Profile' },
      },
      {
        path: 'settings',
        name: 'admin-settings',
        component: SettingsView,
        meta: { title: 'System Settings' },
      },

    ],
  },
  // TEACHER PORTAL ROUTES
  {
    path: '/teacher',
    component: TeacherLayout,
    meta: { requiresAuth: true, requiresTeacher: true },
    children: [
      {
        path: '',
        redirect: '/teacher/dashboard',
      },
      {
        path: 'dashboard',
        name: 'teacher-dashboard',
        component: TeacherDashboardView,
        meta: { title: 'Teacher Dashboard' },
      },
      {
        path: 'classes',
        name: 'teacher-classes',
        component: TeacherClassesView,
        meta: { title: 'My Classes & Subjects' },
      },
      {
        path: 'students',
        name: 'teacher-students',
        component: TeacherStudentsView,
        meta: { title: 'Assigned Students' },
      },
      {
        path: 'attendance',
        name: 'teacher-attendance',
        component: TeacherAttendanceView,
        meta: { title: 'Class Attendance' },
      },
      {
        path: 'timetable',
        name: 'teacher-timetable',
        component: TeacherTimetableView,
        meta: { title: 'My Timetable' },
      },
      {
        path: 'exams',
        name: 'teacher-exams',
        component: TeacherExamsView,
        meta: { title: 'Exams & Marks Entry' },
      },
    ],
  },
  // STUDENT PORTAL ROUTES
  {
    path: '/student',
    component: StudentLayout,
    meta: { requiresAuth: true, requiresStudent: true },
    children: [
      {
        path: '',
        redirect: '/student/dashboard',
      },
      {
        path: 'dashboard',
        name: 'student-dashboard',
        component: StudentDashboardView,
        meta: { title: 'Student Dashboard' },
      },
      {
        path: 'profile',
        name: 'student-profile',
        component: StudentProfileView,
        meta: { title: 'My Profile' },
      },
      {
        path: 'class',
        name: 'student-class',
        component: StudentClassView,
        meta: { title: 'My Class & Subjects' },
      },
      {
        path: 'timetable',
        name: 'student-timetable',
        component: StudentTimetableView,
        meta: { title: 'My Timetable' },
      },
      {
        path: 'attendance',
        name: 'student-attendance',
        component: StudentAttendanceView,
        meta: { title: 'My Attendance' },
      },
      {
        path: 'fees',
        name: 'student-fees',
        component: StudentFeesView,
        meta: { title: 'My Fees & Payments' },
      },
      {
        path: 'exams',
        name: 'student-exams',
        component: StudentExamsView,
        meta: { title: 'My Exam Results' },
      },
      {
        path: 'results',
        name: 'student-results',
        component: StudentExamsView,
        meta: { title: 'My Official Examination Results' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: { title: '404 Not Found' },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

// Navigation Guards
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  // Set document title
  const pageTitle = to.meta.title ? `${to.meta.title}` : 'Somroyal Educational Management System (SEMS)';
  document.title = pageTitle;

  // Guest-only routes (e.g. /login)
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return next({ path: authStore.defaultRoute });
  }

  // Protected routes
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      return next({
        path: '/login',
        query: { redirect: to.fullPath },
      });
    }

    // Role-restricted routes
    if (to.meta.requiresSuperAdmin && !authStore.isSuperAdmin) {
      return next({ path: authStore.defaultRoute });
    }

    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      return next({ path: authStore.defaultRoute });
    }

    if (to.meta.requiresTeacher && !authStore.isTeacher && !authStore.isAdmin) {
      return next({ path: authStore.defaultRoute });
    }

    if (to.meta.requiresStudent && !authStore.isStudent) {
      return next({ path: authStore.defaultRoute });
    }
  }

  next();
});
