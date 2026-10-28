/**
 * Centralized School Branding & Configuration
 * 
 * Edit this file to update the institution name, logo, colors,
 * motto, and contact details across the entire frontend application.
 */

export interface SchoolBrandingConfig {
  institutionName: string;
  shortName: string;
  motto: string;
  district: string;
  city: string;
  country: string;
  portalSubtitle: string;
  contactEmail: string;
  contactPhone: string;
  logoUrl: string;
  faviconUrl: string;
  theme: {
    primary: string;
    primaryHover: string;
    secondary: string;
    accent: string;
  };
}

export const SCHOOL_BRANDING: SchoolBrandingConfig = {
  institutionName: 'Somroyal Educational Management System',
  shortName: 'Somroyal EMS',
  motto: 'Manage Your School Smarter with Somroyal EMS',
  district: 'Banadir',
  city: 'Mogadishu',
  country: 'Somalia',
  portalSubtitle: 'Official Administrative & Academic Portal',
  contactEmail: 'info@somroyal.com',
  contactPhone: '+252 61 500 0000',
  logoUrl: '/somroyal-logo-transparent.png',
  faviconUrl: '/somroyal-logo-transparent.png',
  theme: {
    primary: '#0B1F4B',      // Navy Blue
    primaryHover: '#071735', // Deep Navy
    secondary: '#FF6B00',    // Brand Orange
    accent: '#FF6B00',       // Brand Orange
  },
};
