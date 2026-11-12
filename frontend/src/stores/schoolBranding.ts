import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

export interface SchoolInfoPayload {
  name?: string;
  code?: string;
  type?: string;
  logo_url?: string | null;
  academic_year?: string;
  city?: string;
  email?: string;
  phone?: string;
}

export const useSchoolBrandingStore = defineStore('schoolBranding', () => {
  const authStore = useAuthStore();
  const liveSchoolInfo = ref<SchoolInfoPayload | null>(null);

  const schoolName = computed(() => {
    return (
      authStore.activeInstitution?.name ||
      liveSchoolInfo.value?.name ||
      'Educational Institution'
    );
  });

  const schoolCode = computed(() => {
    return (
      authStore.activeInstitution?.code ||
      liveSchoolInfo.value?.code ||
      'EMS-001'
    );
  });

  const schoolType = computed(() => {
    return (
      authStore.activeInstitution?.type ||
      liveSchoolInfo.value?.type ||
      'School'
    );
  });

  const schoolLogo = computed(() => {
    return (
      authStore.activeInstitution?.logo_url ||
      liveSchoolInfo.value?.logo_url ||
      null
    );
  });

  const adminName = computed(() => {
    return (
      authStore.user?.full_name ||
      authStore.user?.username ||
      'School Administrator'
    );
  });

  const schoolInitials = computed(() => {
    const name = schoolName.value.trim();
    if (!name || name === 'Educational Institution') return 'EMS';
    const words = name.split(/\s+/).filter(Boolean);
    if (words.length === 1) {
      return words[0].slice(0, 2).toUpperCase();
    }
    return (words[0][0] + words[1][0]).toUpperCase();
  });

  const contactEmail = computed(() => {
    return (
      authStore.activeInstitution?.email ||
      liveSchoolInfo.value?.email ||
      ''
    );
  });

  const contactPhone = computed(() => {
    return (
      authStore.activeInstitution?.phone ||
      liveSchoolInfo.value?.phone ||
      ''
    );
  });

  const city = computed(() => {
    return (
      authStore.activeInstitution?.city ||
      liveSchoolInfo.value?.city ||
      'Mogadishu'
    );
  });

  const academicYear = computed(() => {
    return liveSchoolInfo.value?.academic_year || '2026/2027';
  });

  function setLiveSchoolInfo(info: SchoolInfoPayload) {
    liveSchoolInfo.value = { ...info };
    applyBrandingToDocument();
  }

  function applyBrandingToDocument() {
    if (typeof document === 'undefined') return;

    // 1. Dynamic Page Title
    const baseSuffix = 'Somroyal EMS';
    if (!authStore.isSuperAdmin && schoolName.value) {
      document.title = `${schoolName.value} | ${baseSuffix}`;
    }

    // 2. Dynamic Favicon if custom school logo exists
    if (schoolLogo.value) {
      const link = document.querySelector("link[rel*='icon']") as HTMLLinkElement | null;
      if (link) {
        link.href = schoolLogo.value;
      }
    }
  }

  return {
    schoolName,
    schoolCode,
    schoolType,
    schoolLogo,
    adminName,
    schoolInitials,
    contactEmail,
    contactPhone,
    city,
    academicYear,
    setLiveSchoolInfo,
    applyBrandingToDocument,
  };
});
