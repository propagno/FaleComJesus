const { test, expect } = require('@playwright/test');

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test
    await page.goto('/');
  });

  test('should allow a user to login with valid credentials', async ({ page }) => {
    // Click the login button
    await page.getByRole('button', { name: /entrar/i }).click();
    
    // Fill in the login form
    await page.getByLabel(/e-mail/i).fill('admin@example.com');
    await page.getByLabel(/senha/i).fill('password');
    
    // Click the submit button
    await page.getByRole('button', { name: /entrar/i }).click();
    
    // Verify user is logged in - look for dashboard or user menu
    await expect(page.getByText(/dashboard/i)).toBeVisible();
    
    // Verify the user's name appears in the UI
    await expect(page.getByText(/admin/i)).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Click the login button
    await page.getByRole('button', { name: /entrar/i }).click();
    
    // Fill in the login form with invalid credentials
    await page.getByLabel(/e-mail/i).fill('wrong@example.com');
    await page.getByLabel(/senha/i).fill('wrongpassword');
    
    // Click the submit button
    await page.getByRole('button', { name: /entrar/i }).click();
    
    // Verify error message is shown
    await expect(page.getByText(/credenciais inválidas/i)).toBeVisible();
  });

  test('should allow a user to register with valid information', async ({ page }) => {
    // Click the register button
    await page.getByRole('button', { name: /registrar/i }).click();
    
    // Fill in the registration form
    const testEmail = `test${Date.now()}@example.com`;
    await page.getByLabel(/nome/i).fill('Test User');
    await page.getByLabel(/e-mail/i).fill(testEmail);
    await page.getByLabel(/senha/i).fill('Testpassword123!');
    await page.getByLabel(/confirmar senha/i).fill('Testpassword123!');
    
    // Click the submit button
    await page.getByRole('button', { name: /registrar/i }).click();
    
    // Verify user is redirected to dashboard
    await expect(page.getByText(/dashboard/i)).toBeVisible();
  });

  test('should allow a user to logout', async ({ page }) => {
    // Login first
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.getByLabel(/e-mail/i).fill('admin@example.com');
    await page.getByLabel(/senha/i).fill('password');
    await page.getByRole('button', { name: /entrar/i }).click();
    
    // Wait for login to complete
    await expect(page.getByText(/dashboard/i)).toBeVisible();
    
    // Click on user menu
    await page.getByRole('button', { name: /admin/i }).click();
    
    // Click logout button
    await page.getByRole('menuitem', { name: /sair/i }).click();
    
    // Verify user is logged out - login button is visible again
    await expect(page.getByRole('button', { name: /entrar/i })).toBeVisible();
  });
}); 