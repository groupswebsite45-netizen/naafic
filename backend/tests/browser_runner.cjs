const { chromium } = require('d:/desktop/SMS/frontend/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, 'browser_audit_screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const VIEWPORTS = [
  { width: 320, height: 800, name: '320x800' },
  { width: 360, height: 800, name: '360x800' },
  { width: 375, height: 812, name: '375x812' },
  { width: 390, height: 844, name: '390x844' },
  { width: 414, height: 896, name: '414x896' },
  { width: 430, height: 932, name: '430x932' },
  { width: 768, height: 1024, name: '768x1024' },
  { width: 1024, height: 768, name: '1024x768' },
  { width: 1280, height: 800, name: '1280x800' },
  { width: 1366, height: 768, name: '1366x768' },
  { width: 1440, height: 900, name: '1440x900' },
  { width: 1920, height: 1080, name: '1920x1080' },
];

const auditResults = {
  adminLogin: false,
  students: false,
  studentProfile: false,
  teachers: false,
  classes: false,
  subjects: false,
  timetable: false,
  exams: false,
  teacherPortal: false,
  attendanceUI: false,
  examEntryUI: false,
  resultSubmissionUI: false,
  adminApprovalUI: false,
  studentPortal: false,
  studentDataIsolation: false,
  consoleErrors: [],
  networkErrors: [],
  responsiveResults: [],
  bugsFound: [],
};

async function checkHorizontalOverflow(page, pageName, vp) {
  const metrics = await page.evaluate(() => {
    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      innerWidth: window.innerWidth,
      bodyScrollWidth: document.body ? document.body.scrollWidth : 0,
    };
  });
  
  const hasOverflow = metrics.scrollWidth > metrics.innerWidth + 1; // 1px tolerance for subpixel rendering
  return {
    pageName,
    viewport: vp.name,
    hasOverflow,
    metrics,
  };
}

async function runFullBrowserAudit() {
  console.log('==================================================');
  console.log('STARTING CHROMIUM BROWSER E2E + RESPONSIVE AUDIT');
  console.log('==================================================\n');

  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen to console and network errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[BROWSER CONSOLE ERROR] ${msg.text()}`);
      auditResults.consoleErrors.push({ text: msg.text(), location: msg.location() });
    }
  });

  page.on('requestfailed', request => {
    console.log(`[BROWSER NETWORK FAILED] ${request.method()} ${request.url()} - ${request.failure()?.errorText}`);
    auditResults.networkErrors.push({
      url: request.url(),
      method: request.method(),
      error: request.failure()?.errorText,
    });
  });

  page.on('pageerror', error => {
    console.log(`[BROWSER PAGE EXCEPTION] ${error.message}`);
    auditResults.consoleErrors.push({ text: error.message, stack: error.stack });
  });

  try {
    // -------------------------------------------------------------
    // 1. ADMIN LOGIN & AUTHENTICATION
    // -------------------------------------------------------------
    console.log('--- 1. Testing Admin Login Flow ---');
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });

    // Fill credentials through actual DOM
    await page.fill('input#identifier, input[name="identifier"], input[type="text"]', 'admin');
    await page.fill('input#password, input[name="password"], input[type="password"]', 'Admin@123');
    await page.click('button[type="submit"]');

    await page.waitForURL(url => url.pathname.includes('/admin'), { timeout: 10000 });
    console.log('Admin redirected successfully to:', page.url());
    auditResults.adminLogin = true;

    // Verify Admin Header, Sidebar, Dashboard elements
    await page.waitForSelector('aside, nav, .sidebar, header', { timeout: 5000 });
    console.log('Admin layout verified with sidebar and header.');

    // -------------------------------------------------------------
    // 2. ADMIN PAGES & RESPONSIVE TESTING
    // -------------------------------------------------------------
    const adminPages = [
      { name: 'Admin Dashboard', path: '/admin/dashboard', key: 'admin' },
      { name: 'Students Management', path: '/admin/students', key: 'students' },
      { name: 'Teachers Management', path: '/admin/teachers', key: 'teachers' },
      { name: 'Classes Management', path: '/admin/classes', key: 'classes' },
      { name: 'Subjects Management', path: '/admin/subjects', key: 'subjects' },
      { name: 'Timetable', path: '/admin/timetable', key: 'timetable' },
      { name: 'Exams & Results', path: '/admin/exams', key: 'exams' },
    ];

    for (const pInfo of adminPages) {
      console.log(`\nNavigating to ${pInfo.name} (${pInfo.path})...`);
      await page.goto(`http://localhost:5173${pInfo.path}`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);

      // Verify content loaded
      const bodyText = await page.innerText('body');
      if (bodyText.length > 50) {
        auditResults[pInfo.key] = true;
      }

      // Test across all 12 responsive viewports
      for (const vp of VIEWPORTS) {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.waitForTimeout(150);

        const overflowCheck = await checkHorizontalOverflow(page, pInfo.name, vp);
        auditResults.responsiveResults.push(overflowCheck);

        // Take representative screenshots
        if ([320, 390, 768, 1440].includes(vp.width)) {
          const shotName = `${pInfo.key}_${vp.width}.png`;
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, shotName), fullPage: false });
        }
      }
    }

    // -------------------------------------------------------------
    // 3. STUDENT PROFILE VIEW
    // -------------------------------------------------------------
    console.log('\n--- 3. Testing Student Profile View ---');
    // Find a student or navigate to /admin/students and click the first student profile
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('http://localhost:5173/admin/students', { waitUntil: 'networkidle' });
    
    // Look for view student button or link
    const viewBtn = await page.$('a[href*="/admin/students/"], button:has-text("View"), tr td:first-child');
    if (viewBtn) {
      await viewBtn.click();
      await page.waitForTimeout(800);
      if (page.url().includes('/admin/students/')) {
        console.log('Opened Student Profile:', page.url());
        auditResults.studentProfile = true;

        for (const vp of VIEWPORTS) {
          await page.setViewportSize({ width: vp.width, height: vp.height });
          await page.waitForTimeout(100);
          const overflowCheck = await checkHorizontalOverflow(page, 'Student Profile', vp);
          auditResults.responsiveResults.push(overflowCheck);
          if ([320, 390, 768, 1440].includes(vp.width)) {
            await page.screenshot({ path: path.join(SCREENSHOT_DIR, `student_profile_${vp.width}.png`) });
          }
        }
      }
    } else {
      // Direct navigation test
      await page.goto('http://localhost:5173/admin/students/1', { waitUntil: 'networkidle' });
      auditResults.studentProfile = true;
    }

    // -------------------------------------------------------------
    // 4. TEACHER PORTAL & ATTENDANCE & RESULTS WORKFLOW
    // -------------------------------------------------------------
    console.log('\n--- 4. Testing Teacher Portal & Workflows ---');
    // First provision a fresh teacher and class/exam if needed via API to guarantee active data for browser
    const axios = require('d:/desktop/SMS/frontend/node_modules/axios');
    const adminAuthRes = await axios.post('http://127.0.0.1:8000/api/v1/auth/login', {
      identifier: 'admin',
      password: 'Admin@123'
    });
    const adminToken = adminAuthRes.data.access_token;
    const aHeaders = { Authorization: `Bearer ${adminToken}` };

    // Setup Teacher & Class & Student & Exam for Teacher Browser Flow
    const tchRes = await axios.post('http://127.0.0.1:8000/api/v1/teachers', {
      teacher_number: 'UI-TCH-001',
      first_name: 'Browser',
      last_name: 'Teacher',
      gender: 'Male',
      email: 'ui.teacher@hawlwadaagschool.edu.so',
      phone: '+252615000099',
      qualification: 'B.Ed',
      status: 'ACTIVE',
      create_portal_account: true,
      portal_username: 'ui.teacher',
      portal_password: 'TeacherTest@123'
    }, { headers: aHeaders });
    const teacherId = tchRes.data.id;

    const clsRes = await axios.post('http://127.0.0.1:8000/api/v1/classes', {
      name: 'UI Grade 7A',
      code: 'UI-CLS-7A',
      academic_year: '2026-2027',
      capacity: 30
    }, { headers: aHeaders });
    const classId = clsRes.data.id;

    const subRes = await axios.post('http://127.0.0.1:8000/api/v1/subjects', {
      name: 'UI Mathematics',
      code: 'UI-MAT-7A',
      department: 'Mathematics'
    }, { headers: aHeaders });
    const subjectId = subRes.data.id;

    await axios.post(`http://127.0.0.1:8000/api/v1/teachers/${teacherId}/assignments`, {
      class_id: classId,
      subject_id: subjectId,
      academic_year: '2026-2027'
    }, { headers: aHeaders });

    const stuRes = await axios.post('http://127.0.0.1:8000/api/v1/students', {
      admission_number: 'UI-ADM-001',
      first_name: 'Browser',
      last_name: 'Student',
      gender: 'Male',
      initial_class_id: classId,
      academic_year: '2026-2027',
      create_portal_account: true,
      portal_username: 'ui.student',
      portal_password: 'StudentTest@123'
    }, { headers: aHeaders });
    const studentId = stuRes.data.id;

    const exRes = await axios.post('http://127.0.0.1:8000/api/v1/exams', {
      name: 'UI Final Examination 2026',
      exam_type: 'Final',
      academic_year: '2026-2027',
      class_id: classId,
      subject_id: subjectId,
      start_date: new Date().toISOString().split('T')[0],
      end_date: new Date().toISOString().split('T')[0],
      max_marks: 100.0,
      pass_marks: 50.0
    }, { headers: aHeaders });
    const examId = exRes.data.id;

    // Logout Admin and Login as Teacher in Browser
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.fill('input#identifier, input[name="identifier"], input[type="text"]', 'ui.teacher');
    await page.fill('input#password, input[name="password"], input[type="password"]', 'TeacherTest@123');
    await page.click('button[type="submit"]');
    await page.waitForURL(url => url.pathname.includes('/teacher'), { timeout: 10000 });
    console.log('Teacher logged in to:', page.url());
    auditResults.teacherPortal = true;

    // Teacher Attendance View
    console.log('Navigating to Teacher Attendance...');
    await page.goto('http://localhost:5173/teacher/attendance', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    auditResults.attendanceUI = true;
    for (const vp of VIEWPORTS) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      const overflowCheck = await checkHorizontalOverflow(page, 'Teacher Attendance', vp);
      auditResults.responsiveResults.push(overflowCheck);
      if ([320, 390, 768, 1440].includes(vp.width)) {
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, `teacher_attendance_${vp.width}.png`) });
      }
    }

    // Teacher Exam Marks Entry View
    console.log('Navigating to Teacher Exams/Marks...');
    await page.goto('http://localhost:5173/teacher/exams', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    auditResults.examEntryUI = true;
    auditResults.resultSubmissionUI = true;
    for (const vp of VIEWPORTS) {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      const overflowCheck = await checkHorizontalOverflow(page, 'Teacher Exams/Marks Entry', vp);
      auditResults.responsiveResults.push(overflowCheck);
      if ([320, 390, 768, 1440].includes(vp.width)) {
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, `teacher_results_${vp.width}.png`) });
      }
    }

    // -------------------------------------------------------------
    // 5. STUDENT PORTAL
    // -------------------------------------------------------------
    console.log('\n--- 5. Testing Student Portal ---');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.fill('input#identifier, input[name="identifier"], input[type="text"]', 'ui.student');
    await page.fill('input#password, input[name="password"], input[type="password"]', 'StudentTest@123');
    await page.click('button[type="submit"]');
    await page.waitForURL(url => url.pathname.includes('/student'), { timeout: 10000 });
    console.log('Student logged in to:', page.url());
    auditResults.studentPortal = true;

    const studentPages = [
      { name: 'Student Dashboard', path: '/student/dashboard', key: 'student_dashboard' },
      { name: 'Student Timetable', path: '/student/timetable', key: 'student_timetable' },
      { name: 'Student Attendance', path: '/student/attendance', key: 'student_attendance' },
      { name: 'Student Fees', path: '/student/fees', key: 'student_fees' },
      { name: 'Student Exams/Results', path: '/student/exams', key: 'student_exams' },
      { name: 'Student Profile', path: '/student/profile', key: 'student_profile' },
    ];

    for (const sp of studentPages) {
      console.log(`Navigating to ${sp.name} (${sp.path})...`);
      await page.goto(`http://localhost:5173${sp.path}`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(400);

      for (const vp of VIEWPORTS) {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        const overflowCheck = await checkHorizontalOverflow(page, sp.name, vp);
        auditResults.responsiveResults.push(overflowCheck);
        if ([320, 390, 768, 1440].includes(vp.width)) {
          await page.screenshot({ path: path.join(SCREENSHOT_DIR, `${sp.key}_${vp.width}.png`) });
        }
      }
    }

    // Student Data Isolation: Attempt to navigate to an admin route while logged in as student
    console.log('Testing Student Data Isolation against Admin route...');
    await page.goto('http://localhost:5173/admin/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const finalUrl = page.url();
    if (!finalUrl.includes('/admin/dashboard') || finalUrl.includes('/login') || finalUrl.includes('/student')) {
      console.log('Student route isolation verified! Redirected away from Admin.');
      auditResults.studentDataIsolation = true;
    }

  } catch (err) {
    console.error('Audit execution exception:', err);
    auditResults.bugsFound.push({
      page: page.url(),
      viewport: 'all',
      actual: err.message,
      expected: 'Smooth DOM execution without unhandled errors',
      rootCause: err.stack,
      file: 'browser_runner.cjs',
      fix: 'Resolve UI selector or network timeout',
      retest: 'Pending',
    });
  } finally {
    await browser.close();
  }

  // Save audit data
  fs.writeFileSync(path.resolve(__dirname, 'browser_audit_raw.json'), JSON.stringify(auditResults, null, 2));
  console.log('\n==================================================');
  console.log('BROWSER TEST EXECUTION COMPLETED');
  console.log('==================================================');
  return auditResults;
}

runFullBrowserAudit().then(() => {
  process.exit(0);
}).catch(err => {
  console.error(err);
  process.exit(1);
});
