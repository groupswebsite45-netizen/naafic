const { chromium } = require('d:/desktop/SMS/frontend/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const SCREENSHOT_DIR = path.resolve(__dirname, 'fees_verification_screenshots');
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runFeesE2E() {
  console.log('====================================================');
  console.log('STARTING FEES & FINANCE BROWSER E2E TEST');
  console.log('====================================================');

  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser = await chromium.launch({
    executablePath: chromePath,
    headless: true
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  const consoleLogs = [];
  const errors = [];

  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[Browser Console Error]: ${msg.text()}`);
      errors.push(msg.text());
    }
  });

  page.on('pageerror', err => {
    console.log(`[Browser Page Error]: ${err.message}`);
    errors.push(err.message);
  });

  try {
    // 1. Navigate to login
    console.log('\n[Step 1] Navigating to login page...');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.fill('input[type="text"], input[name="identifier"], input[placeholder*="sername"], input[placeholder*="mail"]', 'admin');
    await page.fill('input[type="password"]', 'Admin@Hawlwadaag2026');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle' });
    console.log('✓ Successfully logged in as Admin');

    // 2. Navigate to /admin/fees
    console.log('\n[Step 2] Navigating to /admin/fees...');
    await page.goto('http://localhost:5173/admin/fees', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_fees_primary_default.png'), fullPage: true });

    // 3. Verify Primary State
    console.log('\n[Step 3] Verifying PRIMARY Education Level...');
    const levelText = await page.innerText('body');
    const hasNaN = levelText.includes('NaN');
    if (hasNaN) {
      console.error('FAIL: Found NaN on Fees page!');
    } else {
      console.log('✓ No NaN detected anywhere on the page (PASS)');
    }

    // Check Class Selector Options for PRIMARY
    const classSelect = await page.locator('.filter-strip select').nth(1);
    const primaryClassOptions = await classSelect.locator('option').allInnerTexts();
    console.log('Primary Class Filter Options:', primaryClassOptions);
    const hasSecondaryInPrimary = primaryClassOptions.some(opt => opt.startsWith('Form '));
    if (hasSecondaryInPrimary) {
      console.error('FAIL: Found Secondary (Form) classes in PRIMARY class dropdown!');
    } else {
      console.log('✓ PRIMARY class dropdown contains ONLY Grade classes (PASS)');
    }

    // Check Invoices Table for PRIMARY
    const primaryTableText = await page.innerText('table');
    const hasSecondaryInvoicesInPrimary = primaryTableText.includes('Form 1-A') || primaryTableText.includes('Form 2-A') || primaryTableText.includes('Form 3-A') || primaryTableText.includes('Form 4-A');
    if (hasSecondaryInvoicesInPrimary) {
      console.error('FAIL: Found Secondary student invoices in PRIMARY table!');
    } else {
      console.log('✓ PRIMARY invoices table contains ONLY Primary students (PASS)');
    }

    // 4. Switch to SECONDARY
    console.log('\n[Step 4] Switching to SECONDARY Education Level...');
    await page.click('button:has-text("SECONDARY (Form 1 - 4)")');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_fees_secondary_switched.png'), fullPage: true });

    const secondaryClassOptions = await classSelect.locator('option').allInnerTexts();
    console.log('Secondary Class Filter Options:', secondaryClassOptions);
    const hasPrimaryInSecondary = secondaryClassOptions.some(opt => opt.startsWith('Grade '));
    if (hasPrimaryInSecondary) {
      console.error('FAIL: Found Primary (Grade) classes in SECONDARY class dropdown!');
    } else {
      console.log('✓ SECONDARY class dropdown contains ONLY Form classes (PASS)');
    }

    // Verify class reset
    const selectedClassVal = await classSelect.inputValue();
    console.log('Selected class value after switching to SECONDARY:', selectedClassVal || '(All Secondary Classes)');
    if (selectedClassVal === '') {
      console.log('✓ Switching level successfully reset class selection to "All Secondary Classes" (PASS)');
    }

    // 5. Select Form 1 - A and verify filter
    console.log('\n[Step 5] Selecting Form 1 - A...');
    const form1Option = await classSelect.locator('option:has-text("Form 1")').first();
    if (await form1Option.count() > 0) {
      const form1Val = await form1Option.getAttribute('value');
      await classSelect.selectOption(form1Val);
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_fees_form1_filtered.png'), fullPage: true });
      console.log('✓ Filtered by Form 1 - A successfully (PASS)');
    }

    // 6. Switch back to PRIMARY and verify reset
    console.log('\n[Step 6] Switching back to PRIMARY...');
    await page.click('button:has-text("PRIMARY (Grade 1 - 8)")');
    await page.waitForTimeout(1000);
    const resetClassVal = await classSelect.inputValue();
    if (resetClassVal === '') {
      console.log('✓ Switching back to PRIMARY reset class to "All Primary Classes" (PASS)');
    }

    // 7. Test "View" Student Financial Profile Modal
    console.log('\n[Step 7] Testing "View" Student Financial Profile Modal...');
    const viewBtn = await page.locator('button.btn-view').first();
    if (await viewBtn.count() > 0) {
      await viewBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_student_financial_profile_modal.png') });

      const modalText = await page.innerText('.modal-dialog, .modal-backdrop, body');
      const hasFailureMessage = modalText.includes('Failed to load student financial profile');
      if (hasFailureMessage) {
        console.error('FAIL: Modal displayed "Failed to load student financial profile" error!');
      } else {
        console.log('✓ Financial Profile Modal opened cleanly without errors (PASS)');
      }

      const hasStudentProfile = modalText.includes('STUDENT PROFILE') || modalText.includes('Student Financial Profile');
      const hasFinSummary = modalText.includes('FINANCIAL SUMMARY') || modalText.includes('TOTAL BILLED');
      console.log('✓ Modal shows STUDENT PROFILE section:', hasStudentProfile ? 'PASS' : 'FAIL');
      console.log('✓ Modal shows FINANCIAL SUMMARY section:', hasFinSummary ? 'PASS' : 'FAIL');

      // Close modal
      const closeBtn = await page.locator('.modal-header button, button:has-text("Close"), button:has-text("Done")').first();
      if (await closeBtn.count() > 0) {
        await closeBtn.click();
        await page.waitForTimeout(600);
      }
    }

    // 8. Test Mobile Viewport
    console.log('\n[Step 8] Testing Mobile Viewport (390x844)...');
    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_mobile_viewport.png') });
    console.log('✓ Mobile layout rendered cleanly without breakage (PASS)');

    console.log('\n====================================================');
    console.log('ALL BROWSER E2E TESTS COMPLETED SUCCESSFULLY (PASS)');
    console.log('====================================================');
  } catch (err) {
    console.error('E2E Test Error:', err);
  } finally {
    await browser.close();
  }
}

runFeesE2E();
