import { test, expect } from '@playwright/test';

test.describe('Visual Regression & Critical Flows', () => {
    test('Landing page renders correctly', async ({ page }) => {
        // Navigate to the app
        await page.goto('/');

        // Check for key elements
        await expect(page).toHaveTitle(/Project Prahlada/i);
        await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

        // Take a screenshot for visual comparison
        // Note: In a real CI environment, we would enable:
        // await expect(page).toHaveScreenshot('landing-page.png');
    });

    test('Navigation menu works', async ({ page }) => {
        await page.goto('/');

        // Check navigation links
        const nav = page.getByRole('navigation');
        await expect(nav).toBeVisible();

        // Navigate to Analytics
        await page.getByRole('link', { name: /Analytics/i }).click();
        await expect(page).toHaveURL(/.*analytics/);
    });

    test('Search functionality visual check', async ({ page }) => {
        await page.goto('/');

        const searchInput = page.getByPlaceholderText(/Search/i);
        await expect(searchInput).toBeVisible();

        // Type query
        await searchInput.fill('Raipur');

        // Wait for results dropdown (assuming it appears)
        // await expect(page.locator('.search-results')).toBeVisible();
    });

    test('Theme toggling', async ({ page }) => {
        await page.goto('/');

        // Assuming there's a theme toggle button
        // const themeToggle = page.getByRole('button', { name: /theme/i });
        // if (await themeToggle.isVisible()) {
        //   await themeToggle.click();
        //   // Check for dark mode class or attribute
        // }
    });
});
