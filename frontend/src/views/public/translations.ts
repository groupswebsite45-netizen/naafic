export type Language = 'en' | 'so';

export interface TranslationContent {
  nav: {
    home: string;
    features: string;
    about: string;
    benefits: string;
    howItWorks: string;
    pricing: string;
    contact: string;
    login: string;
    startTrial: string;
    dashboard: string;
  };
  hero: {
    badge: string;
    titlePart1: string;
    titleSmarter: string;
    titlePart2: string;
    titleBrand: string;
    subtitle: string;
    primaryCta: string;
    secondaryCta: string;
    statStudents: string;
    statStudentsLabel: string;
    statAttendance: string;
    statAttendanceLabel: string;
    statClasses: string;
    statClassesLabel: string;
    statUptime: string;
    statUptimeLabel: string;
    previewHeading: string;
    previewBadge: string;
    benefits: {
      easy: string;
      secure: string;
      multiDevice: string;
      support: string;
    };
    featureCards: Array<{
      title: string;
      desc: string;
    }>;
  };
  features: {
    badge: string;
    title: string;
    subtitle: string;
    filterAll: string;
    filterAcademics: string;
    filterPortals: string;
    filterFinances: string;
    filterExams: string;
    viewAll: string;
    viewLess: string;
  };
  about: {
    badge: string;
    title: string;
    subtitle: string;
    leadText: string;
    missionTitle: string;
    missionDesc: string;
    technologyTitle: string;
    technologyDesc: string;
    securityTitle: string;
    securityDesc: string;
  };
  benefits: {
    badge: string;
    title: string;
    subtitle: string;
  };
  howItWorks: {
    badge: string;
    title: string;
    subtitle: string;
    step1Title: string;
    step1Desc: string;
    step2Title: string;
    step2Desc: string;
    step3Title: string;
    step3Desc: string;
    step4Title: string;
    step4Desc: string;
  };
  pricing: {
    badge: string;
    title: string;
    titlePart1?: string;
    titlePart2?: string;
    subtitle: string;
    monthly: string;
    annual: string;
    discountTag: string;
    starterName: string;
    starterDesc: string;
    proName: string;
    proDesc: string;
    proBadge: string;
    enterpriseName: string;
    enterpriseDesc: string;
    perMonth: string;
    contactSales: string;
    choosePlan: string;
    setupFeeLabel?: string;
    billedMonthly?: string;
    billedAnnually?: string;
    customPrice?: string;
    customDesc?: string;
    annotationLeft1?: string;
    annotationLeft2?: string;
    annotationLeft3?: string;
    annotationRight1?: string;
    annotationRight2?: string;
    annotationRight3?: string;
    trust1Title?: string;
    trust1Sub?: string;
    trust2Title?: string;
    trust2Sub?: string;
    trust3Title?: string;
    trust3Sub?: string;
    trust4Title?: string;
    trust4Sub?: string;
  };
  cta: {
    title: string;
    subtitle: string;
    primaryCta: string;
    loginBtn: string;
  };
  contact: {
    badge: string;
    title: string;
    subtitle: string;
    nameLabel: string;
    schoolLabel: string;
    emailLabel: string;
    phoneLabel: string;
    planLabel: string;
    messageLabel: string;
    submitBtn: string;
    submitting: string;
    successMessage: string;
    locationTitle: string;
    emailTitle: string;
    phoneTitle: string;
    hoursTitle: string;
    hoursValue: string;
    locationValue?: string;
    leftTitle?: string;
    leftDesc?: string;
    directInquiryLabel?: string;
    directInquiryNotice?: string;
    buildingCardTitle?: string;
    buildingCardSub?: string;
    rightHeading?: string;
    rightSub?: string;
    leftAnnotation1?: string;
    leftAnnotation2?: string;
    leftAnnotation3?: string;
    rightAnnotation1?: string;
    rightAnnotation2?: string;
    rightAnnotation3?: string;
    trust1Title?: string;
    trust1Sub?: string;
    trust2Title?: string;
    trust2Sub?: string;
    trust3Title?: string;
    trust3Sub?: string;
    trust4Title?: string;
    trust4Sub?: string;
    optgroupSchool?: string;
    optgroupMachad?: string;
    optgroupGeneral?: string;
  };
  footer: {
    brandDesc: string;
    quickLinks: string;
    modules: string;
    contactTitle: string;
    privacy: string;
    terms: string;
    allRightsReserved: string;
  };
}

export const translations: Record<Language, TranslationContent> = {
  en: {
    nav: {
      home: 'Home',
      features: 'Features',
      about: 'About Us',
      benefits: 'Benefits',
      howItWorks: 'How It Works',
      pricing: 'Pricing',
      contact: 'Contact',
      login: 'Sign In',
      startTrial: 'Book a Demo',
      dashboard: 'Go to Dashboard',
    },
    hero: {
      badge: 'NEXT-GEN EDUCATIONAL MANAGEMENT PLATFORM',
      titlePart1: 'Manage Your School ',
      titleSmarter: 'Smarter',
      titlePart2: ' with ',
      titleBrand: 'Somroyal EMS',
      subtitle: 'A complete, all-in-one school management system designed to simplify administration, enhance learning, and connect students, teachers, guardians and staff — anytime, anywhere.',
      primaryCta: 'Get Started Today',
      secondaryCta: 'Watch Demo',
      statStudents: '1,420',
      statStudentsLabel: 'Active Student Records',
      statAttendance: '99.4%',
      statAttendanceLabel: 'Attendance Accuracy',
      statClasses: '21 Streams',
      statClassesLabel: 'Grade 1 - Form 4',
      statUptime: '99.98%',
      statUptimeLabel: 'Platform Availability',
      previewHeading: 'Institutional Command Overview',
      previewBadge: 'SEMS v2.4 Live',
      benefits: {
        easy: 'Easy to Use',
        secure: 'Secure & Reliable',
        multiDevice: 'Multi-Device',
        support: '24/7 Support',
      },
      featureCards: [
        {
          title: 'Student Management',
          desc: 'Student registration, records, and academic tracking.',
        },
        {
          title: 'Academic Management',
          desc: 'Classes, subjects, timetable, examinations, and results.',
        },
        {
          title: 'Fees & Payments',
          desc: 'Fee structures, payment tracking, balances, and invoices.',
        },
        {
          title: 'Guardian Communication',
          desc: 'Attendance alerts, SMS notifications, and guardian updates.',
        },
      ],
    },
    features: {
      badge: 'VERIFIED PLATFORM CAPABILITIES',
      title: 'Built Specifically for Modern Educational Excellence',
      subtitle: 'Explore the comprehensive features operational in Somroyal Educational Management System, engineered with single-source-of-truth reliability.',
      filterAll: 'All Modules',
      filterAcademics: 'Academics & Classes',
      filterPortals: 'Dedicated Portals',
      filterFinances: 'Fees & Invoicing',
      filterExams: 'Exams & Grading',
      viewAll: 'View All Capabilities',
      viewLess: 'Show Fewer Modules',
    },
    about: {
      badge: 'ABOUT SOMROYAL SEMS',
      title: 'Empowering Educational Institutions Across the Horn of Africa',
      subtitle: 'Somroyal Educational Management System (SEMS) delivers modern digital infrastructure to eliminate administrative bottlenecks and elevate academic performance.',
      leadText: 'Designed from the ground up for modern educational standards, SEMS replaces disjointed spreadsheets, paper registers, and manual billing with a secure, centralized cloud and on-premise operational hub.',
      missionTitle: 'Our Institutional Mission',
      missionDesc: 'To provide schools, colleges, and educational academies with dependable, user-friendly software that simplifies complex administrative tasks, enables transparent reporting, and fosters educational advancement.',
      technologyTitle: 'Next-Generation Technology',
      technologyDesc: 'Built on high-concurrency FastAPI backends, reactive Vue 3 interfaces, and enterprise database architecture ensuring ultra-fast page speeds, bank-grade encryption, and continuous reliability.',
      securityTitle: 'Localized Compliance & Security',
      securityDesc: 'Complete institutional data sovereignty with role-based permission safeguards, full audit trail logging, and native integration with regional mobile payment networks and SMS gateways.',
    },
    benefits: {
      badge: 'WHY INSTITUTIONS CHOOSE SEMS',
      title: 'Delivering Measurable Impact to Every Stakeholder',
      subtitle: 'From school directors and accountants to teachers, students, and parents, SEMS provides tailored workflows designed for effortless clarity.',
    },
    howItWorks: {
      badge: 'SEAMLESS IMPLEMENTATION JOURNEY',
      title: 'How Somroyal EMS Powers Your Institution',
      subtitle: 'A straightforward, structured 4-step onboarding pathway to digitize your school without administrative disruption.',
      step1Title: 'Institutional Setup & Branding',
      step1Desc: 'Define campus branches, active academic year, grading scales, and institutional contact identity in system settings.',
      step2Title: 'Academic Hierarchy & Staff Allocation',
      step2Desc: 'Configure primary and secondary grade levels, class streams, curriculum subjects, and assign qualified faculty members.',
      step3Title: 'Student Enrollment & Fee Invoicing',
      step3Desc: 'Admit student bio-data, assign guardian contacts, and generate term fee structures with real-time balance computation.',
      step4Title: 'Live Operational Management',
      step4Desc: 'Teachers submit marks and attendance, students monitor report cards in dedicated self-service portals, and admins track telemetry.',
    },
    pricing: {
      badge: 'SIMPLE & TRANSPARENT PRICING',
      title: 'Affordable Plans for Every Stage of',
      titlePart1: 'Affordable Plans for Every Stage of',
      titlePart2: 'Educational Growth',
      subtitle: 'Get started with Somroyal EMS at a low cost. Pay a one-time setup fee and enjoy an affordable monthly subscription with full access to powerful features.',
      monthly: 'Monthly Billing',
      annual: 'Annual Billing',
      discountTag: 'Save 20%',
      starterName: 'Starter Academy',
      starterDesc: 'Ideal for small or emerging primary schools establishing digital student records and attendance.',
      proName: 'Professional School',
      proDesc: 'Our most popular comprehensive tier for primary and secondary schools needing full exam and fee operations.',
      proBadge: 'MOST POPULAR',
      enterpriseName: 'Enterprise Institution',
      enterpriseDesc: 'Tailored for large institutions, multi-branch campuses, and educational networks requiring dedicated support.',
      perMonth: '/ month',
      contactSales: 'Contact Sales Team',
      choosePlan: 'Select Plan & Get Started',
      setupFeeLabel: 'One-Time Setup',
      billedMonthly: 'Billed Monthly',
      billedAnnually: 'Billed Annually ($240/yr)',
      customPrice: 'Custom',
      customDesc: 'Tailored for large school networks',
      annotationLeft1: 'Same Powerful',
      annotationLeft2: 'Features',
      annotationLeft3: 'Different School Sizes',
      annotationRight1: 'Flexible Plans',
      annotationRight2: 'for a Brighter',
      annotationRight3: 'Education Future',
      trust1Title: 'No Hidden Costs',
      trust1Sub: 'Transparent pricing always',
      trust2Title: 'Priority Support',
      trust2Sub: 'We are here to help',
      trust3Title: 'Access Anywhere',
      trust3Sub: 'Multi-device platform',
      trust4Title: 'Trusted by Schools',
      trust4Sub: 'Across Somalia and beyond',
    },
    cta: {
      title: 'Ready to Modernize Your School Administration?',
      subtitle: 'Join leading institutions using Somroyal EMS to streamline attendance, grading, billing, and parent communication.',
      primaryCta: 'Book a Live Demonstration',
      loginBtn: 'Existing User? Sign In to Portal',
    },
    contact: {
      badge: 'GET IN TOUCH',
      title: 'Connect with the Somroyal EMS Solutions Team',
      subtitle: 'Have questions about platform integration, licensing, or custom requirements? Our academic technology specialists are here to assist.',
      nameLabel: 'Your Full Name',
      schoolLabel: 'School / Institution Name',
      emailLabel: 'Official Email Address',
      phoneLabel: 'Phone / WhatsApp Number',
      planLabel: 'Interested Plan or Tier (School / Machad)',
      optgroupSchool: '🏫 Schools (Dugsiyada)',
      optgroupMachad: '🏛️ Institutes & Academies (Machadyada)',
      optgroupGeneral: '💬 General Inquiries (School ama Machad)',
      messageLabel: 'Tell Us About Your School Requirements',
      submitBtn: 'Send Inquiry Message',
      submitting: 'Sending Inquiry Message...',
      successMessage: 'Thank you! Your inquiry has been received. A Somroyal education specialist will contact you within 24 hours.',
      locationTitle: 'Campus Headquarters',
      emailTitle: 'Direct Email',
      phoneTitle: 'Support Line',
      hoursTitle: 'Operating Hours',
      hoursValue: 'Sat - Thu: 7:30 AM - 4:30 PM (EAT)',
      locationValue: 'Abudwak, Galgaduud, Somalia',
      leftTitle: 'Institutional Support & Inquiry',
      leftDesc: 'Our education platform consultants are available to provide technical demonstrations, custom licensing proposals, and campus onboarding consultations.',
      directInquiryLabel: 'Direct Inquiries:',
      directInquiryNotice: 'Inquiries are responded to via official institutional channels within one business day.',
      buildingCardTitle: 'Dedicated Support for Your School',
      buildingCardSub: 'Our team is ready to help',
      rightHeading: 'Send Us an Inquiry',
      rightSub: 'Fill out the form below and our team will get back to you shortly.',
      leftAnnotation1: "Let's Build",
      leftAnnotation2: 'a Smarter Learning',
      leftAnnotation3: 'Future Together',
      rightAnnotation1: 'Your Education',
      rightAnnotation2: 'Technology Partner',
      rightAnnotation3: 'in Somalia and Beyond',
      trust1Title: 'Expert Guidance',
      trust1Sub: 'Free consultation with our specialists',
      trust2Title: 'Custom Solutions',
      trust2Sub: 'Tailored to your school requirements',
      trust3Title: 'Fast Response',
      trust3Sub: 'We typically reply within one business day',
      trust4Title: 'Trusted Partner',
      trust4Sub: 'Supporting schools across Somalia and beyond',
    },
    footer: {
      brandDesc: 'Somroyal Educational Management System (SEMS) is a premier school management platform providing modern administration, examination, and fee tracking solutions.',
      quickLinks: 'Quick Navigation',
      modules: 'Platform Modules',
      contactTitle: 'Official Contact',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service',
      allRightsReserved: 'All rights reserved.',
    },
  },
  so: {
    nav: {
      home: 'Bogga Hore',
      features: 'Astaamaha',
      about: 'Naga Saabsan',
      benefits: 'Faa\'iidooyinka',
      howItWorks: 'Sida uu Shaqeeyo',
      pricing: 'Qiimaha',
      contact: 'Xiriir',
      login: 'Gal System-ka',
      startTrial: 'Codso Demo',
      dashboard: 'Aad Dashboard-ka',
    },
    hero: {
      badge: 'NIDAAMKA CASRIGA AH EE MAAMULKA WAXBARASHADA',
      titlePart1: 'Ku Maamul Dugsigaaga ',
      titleSmarter: 'Si Caqli Badan',
      titlePart2: ' adoo adeegsanaya ',
      titleBrand: 'Somroyal EMS',
      subtitle: 'Nidaam dhameystiran oo isku xiraya maamulka dugsiga, kor u qaadaya tayada waxbarashada, isku xirayana ardayda, macallimiinta, waalidiinta iyo shaqaalaha — meel kasta iyo goor kasta.',
      primaryCta: 'Bilow Maanta',
      secondaryCta: 'Daawo Muuqaal (Demo)',
      statStudents: '1,420',
      statStudentsLabel: 'Xogta Ardayda firfircoon',
      statAttendance: '99.4%',
      statAttendanceLabel: 'Saxnaanta Xaadiriska',
      statClasses: '21 Qaybood',
      statClassesLabel: 'Fasalka 1aad - 12aad',
      statUptime: '99.98%',
      statUptimeLabel: 'Shaqada System-ka',
      previewHeading: 'Xarunta Guud ee Maamulka SEMS',
      previewBadge: 'SEMS v2.4 Toos ah',
      benefits: {
        easy: 'Fududahay Isticmaalka',
        secure: 'Aamin & La Isku Halleyn Karo',
        multiDevice: 'Aaladaha oo Dhan',
        support: 'Taageero 24/7 ah',
      },
      featureCards: [
        {
          title: 'Maamulka Ardayda',
          desc: 'Diiwaangelinta, xogta iyo la-socodka heerka aqooneed ee ardayda.',
        },
        {
          title: 'Maamulka Tacliinta',
          desc: 'Fasallada, maadooyinka, jadwalka, imtixaanaadka iyo natiijooyinka.',
        },
        {
          title: 'Fiiga & Lacagaha',
          desc: 'Qaab-dhismeedka fiiga, la-socodka bixinta, haraaga iyo qaansheegyada.',
        },
        {
          title: 'Xiriirka Waalidiinta',
          desc: 'Farriimaha xaadiriska, digniinaha SMS-ka iyo warbixinnada waalidka.',
        },
      ],
    },
    features: {
      badge: 'ASTAAMAHA LA HUBSADAY',
      title: 'Loo Sameeyay Tayada iyo Horumarka Waxbarashada',
      subtitle: 'Dheegasho ku samee qaybaha muhiimka ah ee Somroyal EMS ku shaqeeyo si hufan oo la isku halleyn karo.',
      filterAll: 'Dhammaan',
      filterAcademics: 'Tacliinta & Fasallada',
      filterPortals: 'Bogagga Gaarka ah',
      filterFinances: 'Fiiga & Biilasha',
      filterExams: 'Imtixaanaadka',
      viewAll: 'Arag Dhammaan Astaamaha',
      viewLess: 'Muuji Qaybo Kooban',
    },
    about: {
      badge: 'KU SAABSAN SOMROYAL SEMS',
      title: 'Awood-siinta Hay\'adaha Waxbarashada ee Geeska Afrika',
      subtitle: 'Somroyal Educational Management System (SEMS) waxay bixisaa adeeg dijitaal ah oo casri ah oo meesha ka saaraya dhibaatooyinka maamul ee dugsiyada.',
      leadText: 'SEMS waxaa loo dhisay si gaar ah si ay u beddesho buugaagta gacanta iyo warqadaha daalan, iyadoo dugsiga siineysa xog mideysan, amni sare, iyo maamul fudud.',
      missionTitle: 'Hadafkayaga Guud',
      missionDesc: 'Inaan dugsiyada iyo machadyada waxbarashada siino software casri ah oo fududeynaya shaqooyinka maalinlaha ah, korna u qaadaya tayada waxbarashada.',
      technologyTitle: 'Farsamo Sare & Xawaare',
      technologyDesc: 'Waxaa lagu dhisay tiknoolajiyadaha ugu dambeeya (FastAPI & Vue 3) oo bixiya xawaare sare, keydin hufan, iyo hab shaqo oo aan kala go\' lahayn.',
      securityTitle: 'Amniga Xogta & Adeegga Maxalliga ah',
      securityDesc: 'Xogta dugsigaaga adaa leh, oo leh xakameyn adag oo ku saleysan shaqooyinka (RBAC), xiriir toos ah oo Hormuud SMS ah, iyo taageeridda lacagaha maxalliga ah.',
    },
    benefits: {
      badge: 'SABABTA LOO DOORTO SEMS',
      title: 'Faa\'iidooyin La Taaban Karo oo Qof Walba U Dan ah',
      subtitle: 'Maamulayaasha, xisaabiyeyaasha, macallimiinta, ardayda iyo waalidiinta waxay helayaan hab sahlan oo hufan.',
    },
    howItWorks: {
      badge: 'SIDUU U SHAQEEYO',
      title: '4 Tallaabo oo Fudud oo Aad Ku Billaabayso',
      subtitle: 'Hab nidaamsan oo sahlan oo aad dugsigaaga ugu wareejin karto nidaamka casriga ah ee Somroyal EMS.',
      step1Title: 'Dejinta Dugsiga & Astaynta',
      step1Desc: 'Gali magaca dugsiga, sanad-dugsiyeedka firfircoon, iyo habka darajooyinka imtixaanka.',
      step2Title: 'Habeynta Fasallada & Macallimiinta',
      step2Desc: 'Diyaari fasallada hoose iyo sare, maadooyinka, una qoondee macallimiinta u qalma.',
      step3Title: 'Diiwaangelinta Ardayda & Fiiga',
      step3Desc: 'Diiwaangeli ardayda, lambarrada waalidiinta, una samee qaab-dhismeedka lacag-bixinta fiiga.',
      step4Title: 'Maamulka Tooska ah & Portallada',
      step4Desc: 'Macallimiintu waxay gelinayaan dhibcaha iyo xaadiriska, ardayduna waxay ka fiirsanayaan natiijooyinkooda.',
    },
    pricing: {
      badge: 'QIIMO CAD & HUSHIIS FUDUD',
      title: 'Qorsheyaal La Awoodi Karo oo Heer Kasta oo',
      titlePart1: 'Qorsheyaal La Awoodi Karo oo Heer Kasta oo',
      titlePart2: 'Kobaca Waxbarashada Ah',
      subtitle: 'Ku bilow Somroyal EMS qiimo jaban. Bixi lacagta diiwaangelinta hal mar oo kaliya oo ku raaxayso rukumo bille ah oo la awoodi karo.',
      monthly: 'Bille',
      annual: 'Sannadle',
      discountTag: 'Dhimis 20%',
      starterName: 'Starter Academy',
      starterDesc: 'Ku habboon dugsiyada yaryar ee doonaya inay si fudud u maamulaan ardayda iyo xaadiriska.',
      proName: 'Professional School',
      proDesc: 'Qorshaha ugu caansan ee dugsiyada u baahan dhammaan qaybaha imtixaanka, fiiga, iyo SMS-ka.',
      proBadge: 'UGU CAANSAN',
      enterpriseName: 'Enterprise Institution',
      enterpriseDesc: 'Loo sameeyay dugsiyada waaweyn ee leh xarumo badan oo u baahan adeeg gaar ah.',
      perMonth: '/ bishii',
      contactSales: 'La Xiriir Kooxda Iibka',
      choosePlan: 'Dooro Qorshahan & Bilow',
      setupFeeLabel: 'Diyaarinta (Hal Mar)',
      billedMonthly: 'Bille ahaan',
      billedAnnually: 'Sannadle ahaan ($240/sano)',
      customPrice: 'Heshiis Gaar ah',
      customDesc: 'Loo habeeyay dugsiyada waaweyn ee xarumaha badan leh',
      annotationLeft1: 'Awood Isku Mid ah',
      annotationLeft2: 'Tilmaamo Sare',
      annotationLeft3: 'Cabirrada Dugsiyada',
      annotationRight1: 'Qorshayaal Fudud',
      annotationRight2: 'Mustaqbal Waxbarasho',
      annotationRight3: 'oo Iftiin Badan',
      trust1Title: 'Kharash Qarsoon Ma Jiro',
      trust1Sub: 'Qiimo cad had iyo jeer',
      trust2Title: 'Taageero Degdeg ah',
      trust2Sub: 'Mar walba diyaar ayaan nahay',
      trust3Title: 'Ka Gal Meel Kasta',
      trust3Sub: 'Kombuyuutar & Mobile',
      trust4Title: 'Dugsiyadu Ku Kalsoon Yihiin',
      trust4Sub: 'Guud ahaan Soomaaliya iyo dibaddeeda',
    },
    cta: {
      title: 'Diyaar ma u tahay inaad casriyeyso maamulka dugsigaaga?',
      subtitle: 'Ku biir dugsiyada ku kalsoon Somroyal EMS si aad u maamusho ardayda, imtixaanaadka, iyo fiiga.',
      primaryCta: 'Dalbo Muuqaal Toos ah (Demo)',
      loginBtn: 'Horay ma u leedahay Koonto? Gal System-ka',
    },
    contact: {
      badge: 'NALA SOO XIRIIR',
      title: 'La Xiriir Kooxda Xalka Somroyal EMS',
      subtitle: 'Su\'aalo ma ka qabtaa isku-xirka nidaamka, shatiga, ama baahiyo gaar ah? Khabiiradayada farsamada waxbarashada ayaa diyaar u ah inay ku caawiyaan.',
      nameLabel: 'Magacaaga oo Dhameystiran',
      schoolLabel: 'Magaca Dugsiga / Machadka',
      emailLabel: 'Email-ka Rasmiga ah',
      phoneLabel: 'Telefoonka / WhatsApp Lambarka',
      planLabel: 'Qorshaha Aad Danaynayso (Dugsi ama Machad)',
      optgroupSchool: '🏫 Dugsiyada (Schools)',
      optgroupMachad: '🏛️ Machadyada & Kulliyadaha (Institutes)',
      optgroupGeneral: '💬 Su\'aalo Guud (Dugsi ama Machad)',
      messageLabel: 'Nooga Waran Baahida Dugsigaaga',
      submitBtn: 'Dir Farriinta Xog-doonka',
      submitting: 'Farriinta waa la dirayaa...',
      successMessage: 'Mahadsanid! Farriintaadii waa la helay. Khubaradayada ayaa kula soo xiriiri doona 24 saac gudahood.',
      locationTitle: 'Xarunta Dhismaha',
      emailTitle: 'Email Toos ah',
      phoneTitle: 'Khadka Taageerada',
      hoursTitle: 'Saacadaha Shaqada',
      hoursValue: 'Sabti - Khamiis: 7:30 AM - 4:30 PM (EAT)',
      locationValue: 'Caabudwaaq, Galgaduud, Soomaaliya',
      leftTitle: 'Taageerada Dugsiyada & Xog-doonka',
      leftDesc: 'Khubaradayada nidaamka waxbarashada waxay diyaar u yihiin inay ku siiyaan bandhig farsamo, soo jeedin shati gaar ah, iyo la-talin ku saabsan hirgelinta.',
      directInquiryLabel: 'Xog-doonka Tooska ah:',
      directInquiryNotice: 'Farriimaha waxaa lagaga jawaabaa marinada rasmiga ah hal maalin shaqo gudaheed.',
      buildingCardTitle: 'Taageero Gaar ah oo Dugsigaaga ah',
      buildingCardSub: 'Kooxdayadu waxay diyaar u tahay inay ku caawiso',
      rightHeading: 'Noo Soo Dir Farriin / Xog-doon',
      rightSub: 'Buuxi foomka hoose oo kooxdayadu waxay kula soo xiriiri doonaan si degdeg ah.',
      leftAnnotation1: 'Aan Wada Dhisno',
      leftAnnotation2: 'Mustaqbal Waxbarasho',
      leftAnnotation3: 'oo Casri ah',
      rightAnnotation1: 'Wehelkaaga Teknoolojiyadda',
      rightAnnotation2: 'Waxbarashada ee',
      rightAnnotation3: 'Soomaaliya iyo Caalamka',
      trust1Title: 'Hagid Khubaro ah',
      trust1Sub: 'La-talin bilaash ah oo khubaro ah',
      trust2Title: 'Xalal Gaar ah',
      trust2Sub: 'Loo habeeyay baahida dugsigaaga',
      trust3Title: 'Jawaab Degdeg ah',
      trust3Sub: 'Waxaan kaga jawaabnaa hal maalin shaqo gudaheed',
      trust4Title: 'Wehel La Isku Halleyn Karo',
      trust4Sub: 'Taageeraya dugsiyada Soomaaliya iyo dibaddeeda',
    },
    footer: {
      brandDesc: 'Somroyal Educational Management System (SEMS) waa nidaam casri ah oo lagu maamulo dugsiyada, bixinayana xalal dhameystiran oo la isku halleyn karo.',
      quickLinks: 'Bogagga Muhiimka ah',
      modules: 'Qaybaha System-ka',
      contactTitle: 'Xiriirka Rasmiga ah',
      privacy: 'Ilaalinta Xogta Gaarka ah',
      terms: 'Shuruudaha Isticmaalka',
      allRightsReserved: 'Xuquuqda oo dhan waa dhowran tahay.',
    },
  },
};
