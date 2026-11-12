import { ref, computed, readonly, type App, type Plugin } from 'vue';

export type Locale = 'en' | 'so';

export interface LanguageOption {
  code: Locale;
  label: string;
  nativeLabel: string;
  shortLabel: string;
  flag: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  {
    code: 'en',
    label: 'English',
    nativeLabel: 'English (US)',
    shortLabel: 'EN',
    flag: '🇺🇸',
  },
  {
    code: 'so',
    label: 'Somali',
    nativeLabel: 'Af-Soomaali',
    shortLabel: 'SO',
    flag: '🇸🇴',
  },
];

const STORAGE_KEY = 'somroyal_ems_language';

// Detect initial language: localStorage -> default 'en'
function getInitialLocale(): Locale {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'en' || saved === 'so') {
      return saved;
    }
  }
  return 'en';
}

const currentLocale = ref<Locale>(getInitialLocale());

// Dictionaries
export const messages: Record<Locale, Record<string, any>> = {
  en: {
    nav: {
      dashboard: 'Dashboard',
      students: 'Students',
      teachers: 'Teachers',
      classes: 'Classes',
      classPromotion: 'Class Promotion',
      subjects: 'Subjects',
      timetable: 'Timetable',
      exams: 'Exams',
      resultsManagement: 'Results Management',
      feesPayments: 'Fees & Payments',
      reports: 'Reports',
      usersRoles: 'Users & Roles',
      settings: 'Settings',
      needHelp: 'Need Help?',
      supportDesc: 'Our support team is here to assist you.',
      contactSupport: 'Contact Support',
    },
    header: {
      searchPlaceholder: 'Search students, teachers, classes, subjects, exams...',
      ctrlK: 'Ctrl + K',
      currentLanguage: 'Current Language',
      language: 'Language',
      english: 'English',
      somali: 'Somali (Af-Soomaali)',
      notifications: 'Notifications',
      newNotifications: '{count} New Notifications',
      unreadCountBadge: '{count} new',
      markAllRead: 'Mark all as read',
      markRead: 'Mark as read',
      all: 'All',
      unread: 'Unread',
      read: 'Read',
      allCaughtUp: 'You are all caught up!',
      allCaughtUpDesc: 'There are no unread notifications at this time.',
      noNotifications: 'No notifications found',
      noNotificationsDesc: 'When new alerts or system updates arrive, they will appear here.',
      viewAllNotifications: 'View All Notifications',
      myProfile: 'My Profile',
      systemSettings: 'System Settings',
      signOut: 'Sign Out',
      superAdmin: 'Super Admin',
      schoolAdmin: 'School Admin',
    },
    notifType: {
      ATTENDANCE_ABSENT: 'Attendance Alert',
      RESULT_RELEASED: 'Exam Result Release',
      FEE_REMINDER: 'Fee Payment Reminder',
      GENERAL_ANNOUNCEMENT: 'General Announcement',
      CUSTOM: 'School Notice',
    },
    common: {
      save: 'Save',
      cancel: 'Cancel',
      edit: 'Edit',
      delete: 'Delete',
      add: 'Add',
      create: 'Create',
      update: 'Update',
      search: 'Search',
      filter: 'Filter',
      status: 'Status',
      actions: 'Actions',
      view: 'View',
      refresh: 'Refresh',
      loading: 'Loading...',
      active: 'Active',
      inactive: 'Inactive',
      pending: 'Pending',
      delivered: 'Delivered',
      failed: 'Failed',
      read: 'Read',
      unread: 'Unread',
      all: 'All',
      close: 'Close',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      export: 'Export',
      import: 'Import',
      confirm: 'Confirm',
      yes: 'Yes',
      no: 'No',
      noData: 'No data available',
      justNow: 'Just now',
      minsAgo: '{count}m ago',
      hoursAgo: '{count}h ago',
      yesterday: 'Yesterday',
      daysAgo: '{count}d ago',
    },
    dashboard: {
      title: 'School Admin Dashboard',
      welcomeBack: 'Welcome back',
      totalStudents: 'Total Students',
      totalTeachers: 'Total Teachers',
      totalClasses: 'Total Classes',
      totalSubjects: 'Total Subjects',
      attendanceRate: 'Attendance Rate',
      feeCollection: 'Fee Collections',
      recentActivity: 'Recent Activity',
      quickActions: 'Quick Actions',
      overview: 'Overview',
      viewAll: 'View All',
    },
  },
  so: {
    nav: {
      dashboard: 'Gudiga Guud (Dashboard)',
      students: 'Ardayda',
      teachers: 'Macallimiinta',
      classes: 'Fasalada',
      classPromotion: 'Dalacsiinta Fasalada',
      subjects: 'Maadooyinka',
      timetable: 'Jadwalka Xiisadaha',
      exams: 'Imtixaanaadka',
      resultsManagement: 'Maamulka Natiijooyinka',
      feesPayments: 'Fiiska & Lacag-bixinta',
      reports: 'Warbixinada',
      usersRoles: 'Isticmaalayaasha & Doorka',
      settings: 'Habaynta Nidaamka',
      needHelp: 'Ma u Baahan Tahay Caawin?',
      supportDesc: 'Kooxdayada taageerada ayaa diyaar kuu ah mar kasta.',
      contactSupport: 'La Xiriir Taageerada',
    },
    header: {
      searchPlaceholder: 'Raadi ardayda, macallimiinta, fasalada, maadooyinka, imtixaannada...',
      ctrlK: 'Ctrl + K',
      currentLanguage: 'Luqadda Hadda',
      language: 'Luqadda',
      english: 'Ingiriisi (English)',
      somali: 'Af-Soomaali',
      notifications: 'Ogeysiisyada',
      newNotifications: '{count} Ogeysiis Cusub',
      unreadCountBadge: '{count} cusub',
      markAllRead: 'Dhammaan u calaamadee akhris',
      markRead: 'U calaamadee akhris',
      all: 'Dhammaan',
      unread: 'Aan la akhriyin',
      read: 'La akhriyay',
      allCaughtUp: 'Waa lagusoo wada gaaray!',
      allCaughtUpDesc: 'Ma jiraan ogeysiisho aan la akhriyin xilligan.',
      noNotifications: 'Wax ogeysiis ah lama helin',
      noNotificationsDesc: 'Marka ay soo baxaan fariimo ama ogeysiisyada nidaamka, halkan ayey kasoo muuqan doonaan.',
      viewAllNotifications: 'Eeg Dhammaan Ogeysiisyada',
      myProfile: 'Xogtayda Gaarka ah',
      systemSettings: 'Habaynta Nidaamka',
      signOut: 'Ka Bax',
      superAdmin: 'Maamulaha Guud',
      schoolAdmin: 'Maamulaha Dugsiga',
    },
    notifType: {
      ATTENDANCE_ABSENT: 'Ogeysiis Maqnaansho',
      RESULT_RELEASED: 'Natiijada Imtixaanka',
      FEE_REMINDER: 'Xasuusin Lacag-bixin',
      GENERAL_ANNOUNCEMENT: 'Ogeysiis Guud',
      CUSTOM: 'Fariin Dugsiga',
    },
    common: {
      save: 'Keydi',
      cancel: 'Ka noqo',
      edit: 'Wax ka beddel',
      delete: 'Tirtir',
      add: 'Ku dar',
      create: 'Abuur',
      update: 'Cusbooneysii',
      search: 'Raadi',
      filter: 'Kala shaandhee',
      status: 'Xaaladda',
      actions: 'Ficillo',
      view: 'Eeg',
      refresh: 'Dib u cusbooneysii',
      loading: 'Waa la soo rarayaa...',
      active: 'Firfircoon',
      inactive: 'Aan firfircooneyn',
      pending: 'La sugayo',
      delivered: 'La gaarsiiyay',
      failed: 'Fashilmay',
      read: 'La akhriyay',
      unread: 'Aan la akhriyin',
      all: 'Dhammaan',
      close: 'Xir',
      back: 'Dib u noqo',
      next: 'Horay',
      previous: 'Kii hore',
      export: 'Dhoofi',
      import: 'Soo dhoofi',
      confirm: 'Xaqiiji',
      yes: 'Haa',
      no: 'Maya',
      noData: 'Xog lama helin',
      justNow: 'Hadda',
      minsAgo: '{count}d ka hor',
      hoursAgo: '{count}b ka hor',
      yesterday: 'Shalay',
      daysAgo: '{count} maalmood ka hor',
    },
    dashboard: {
      title: 'Dashboordhka Maamulka Dugsiga',
      welcomeBack: 'Kusoo dhawoow dib',
      totalStudents: 'Wadarta Ardayda',
      totalTeachers: 'Wadarta Macallimiinta',
      totalClasses: 'Wadarta Fasalada',
      totalSubjects: 'Wadarta Maadooyinka',
      attendanceRate: 'Heerka Imaanshaha',
      feeCollection: 'Ururinta Fiiska',
      recentActivity: 'Dhaqdhaqaaqa Dhowaan',
      quickActions: 'Ficillo Degdeg ah',
      overview: 'Guudmar',
      viewAll: 'Eeg Dhammaan',
    },
  },
};

/**
 * Translate a dot-separated key (e.g., 'nav.dashboard') with parameter interpolation.
 */
export function t(key: string, params?: Record<string, any>): string {
  const lang = currentLocale.value;
  const keys = key.split('.');

  let value: any = messages[lang];
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      value = undefined;
      break;
    }
  }

  // Fallback to English if missing in Somali
  if (value === undefined && lang !== 'en') {
    let fallbackValue: any = messages.en;
    for (const k of keys) {
      if (fallbackValue && typeof fallbackValue === 'object' && k in fallbackValue) {
        fallbackValue = fallbackValue[k];
      } else {
        fallbackValue = undefined;
        break;
      }
    }
    value = fallbackValue;
  }

  // Final fallback to the last segment or key itself
  if (value === undefined || typeof value !== 'string') {
    return keys[keys.length - 1] || key;
  }

  // Parameter interpolation: {count}, {name}, etc.
  if (params) {
    return value.replace(/\{(\w+)\}/g, (_, p) => {
      return params[p] !== undefined ? String(params[p]) : `{${p}}`;
    });
  }

  return value;
}

/**
 * Format relative time in current language
 */
export function formatRelativeTime(dateInput: string | Date | null | undefined): string {
  if (!dateInput) return '';
  const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
  if (isNaN(date.getTime())) return '';

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSec < 60) {
    return t('common.justNow');
  }
  if (diffMin < 60) {
    return t('common.minsAgo', { count: diffMin });
  }
  if (diffHours < 24) {
    return t('common.hoursAgo', { count: diffHours });
  }
  if (diffDays === 1) {
    return t('common.yesterday');
  }
  if (diffDays < 7) {
    return t('common.daysAgo', { count: diffDays });
  }

  // Format as readable date (e.g. 12 Nov, 10:02 AM)
  return date.toLocaleDateString(currentLocale.value === 'so' ? 'so-SO' : 'en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Set the current application language, persist to localStorage and sync document element.
 */
export function setLocale(locale: Locale) {
  currentLocale.value = locale;
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, locale);
    document.documentElement.lang = locale;
  }
}

/**
 * Composable for easy use inside Vue components
 */
export function useI18n() {
  const currentLanguage = computed(() => {
    return (
      SUPPORTED_LANGUAGES.find(l => l.code === currentLocale.value) ||
      SUPPORTED_LANGUAGES[0]
    );
  });

  return {
    locale: readonly(currentLocale),
    currentLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
    setLocale,
    t,
    formatRelativeTime,
  };
}

/**
 * Vue Plugin installer for app.use(i18nPlugin)
 */
export const i18nPlugin: Plugin = {
  install(app: App) {
    app.config.globalProperties.$t = t;
    app.config.globalProperties.$formatTime = formatRelativeTime;
    app.provide('i18n', {
      locale: currentLocale,
      setLocale,
      t,
      formatRelativeTime,
    });
  },
};

