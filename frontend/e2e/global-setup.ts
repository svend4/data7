/**
 * Playwright Global Setup
 *
 * Runs before all tests to prepare the test environment
 */
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const baseURL = config.use?.baseURL || 'http://localhost:80';

  console.log('🚀 Starting E2E Test Suite');
  console.log(`📍 Base URL: ${baseURL}`);

  // Wait for backend to be ready
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('⏳ Waiting for backend health check...');

    // Poll health endpoint until ready (max 30 seconds)
    const maxAttempts = 30;
    let attempt = 0;
    let backendReady = false;

    while (attempt < maxAttempts && !backendReady) {
      try {
        const response = await page.goto(`${baseURL.replace('80', '8000')}/health`, {
          waitUntil: 'networkidle',
          timeout: 2000,
        });

        if (response && response.ok()) {
          backendReady = true;
          console.log('✅ Backend is ready');
        }
      } catch (error) {
        attempt++;
        await page.waitForTimeout(1000);
      }
    }

    if (!backendReady) {
      throw new Error('Backend did not become ready in time');
    }

    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend...');
    const frontendResponse = await page.goto(baseURL, {
      waitUntil: 'networkidle',
      timeout: 10000,
    });

    if (!frontendResponse || !frontendResponse.ok()) {
      throw new Error('Frontend is not accessible');
    }

    console.log('✅ Frontend is ready');
    console.log('🎬 Starting tests...\n');

  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
