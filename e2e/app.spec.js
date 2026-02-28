// End-to-end tests for MasterDataCleaner

import { test, expect } from '@playwright/test';

test.describe('MasterDataCleaner E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('homepage loads correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/MasterDataCleaner/);
  });

  test('can navigate to login page', async ({ page }) => {
    await page.click('text=Sign In');
    await expect(page.locator('input[type="email"]')).toBeVisible();
  });

  test('login form shows register tab', async ({ page }) => {
    await page.click('text=Sign In');
    await expect(page.locator('text=Don\'t have an account?')).toBeVisible();
  });

  test('login form validation', async ({ page }) => {
    await page.click('text=Sign In');
    await page.click('button[type="submit"]');
    // Should show validation errors
    await expect(page.locator('text=This field is required').first()).toBeVisible();
  });

  test('can switch to register tab', async ({ page }) => {
    await page.click('text=Sign In');
    await page.click('text=Sign Up');
    await expect(page.locator('text=Already have an account?')).toBeVisible();
  });

  test('register form fields', async ({ page }) => {
    await page.click('text=Sign In');
    await page.click('text=Sign Up');
    await expect(page.locator('input[placeholder="John Doe"]')).toBeVisible();
  });

  test('forgot password link exists', async ({ page }) => {
    await page.click('text=Sign In');
    await expect(page.locator('text=Forgot your password?')).toBeVisible();
  });

  test('oauth buttons exist', async ({ page }) => {
    await page.click('text=Sign In');
    await expect(page.locator('text=Google')).toBeVisible();
    await expect(page.locator('text=GitHub')).toBeVisible();
  });
});
