import { test, expect } from '@playwright/test';

// Generate a random email for each run
const testEmail = `pw_${Date.now()}@example.com`;
const testPassword = 'Password123!';

test.describe('CareerLens UI End-to-End Regression Suite', () => {
  
  test.beforeEach(async ({ page }) => {
    // Go to the starting page before each test
    await page.goto('http://localhost:5173/');
  });

  test('User can register and login successfully', async ({ page }) => {
    // 1. Navigation to Register
    await page.click('text=Get Started Free');
    await expect(page).toHaveURL(/.*register/);
    
    // 2. Registration Flow
    await page.fill('input[type="text"]', 'Playwright Tester');
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    
    // Capture screenshot before submission
    await page.screenshot({ path: 'tests/screenshots/register-form.png' });
    await page.click('button:has-text("Create Account")');
    
    // Should navigate to login
    await expect(page).toHaveURL(/.*login/);
    
    // 3. Login Flow
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.screenshot({ path: 'tests/screenshots/login-form.png' });
    await page.click('button:has-text("Sign In")');
    
    // Should land on Dashboard
    await expect(page).toHaveURL(/.*app/);
    await expect(page.locator('text=Welcome back')).toBeVisible();
  });

  test('User can search and load more opportunities', async ({ page }) => {
    // Note: Depends on previous state if we don't clear, but let's assume we log in
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button:has-text("Sign In")');
    await expect(page).toHaveURL(/.*app/);

    // Navigate to Opportunities Hub
    await page.click('text=Opportunities');
    await expect(page).toHaveURL(/.*opportunities/);
    
    // Perform Search
    await page.fill('input[placeholder="Job title, company, skill..."]', 'Python');
    await page.keyboard.press('Enter');
    
    // Wait for network idle or for cards to load
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'tests/screenshots/search-results.png' });
    
    // Load More (if available)
    const loadMoreBtn = page.locator('button:has-text("Load More Opportunities")');
    if (await loadMoreBtn.isVisible()) {
      await loadMoreBtn.click();
      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: 'tests/screenshots/search-load-more.png' });
    }
  });

  test('User can access dashboard and logout cleanly', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button:has-text("Sign In")');
    await expect(page).toHaveURL(/.*app/);

    // Open Sidebar Profile Menu
    // We assume the sidebar has a user profile/logout button
    await page.click('text=Sign out'); 
    
    // Verify redirect
    await expect(page).toHaveURL(/.*login/);
    
    // Verify Protected Route bounces back
    await page.goto('http://localhost:5173/app');
    await expect(page).toHaveURL(/.*login/);
  });
});
