/**
 * Playwright Global Teardown
 *
 * Runs after all tests to clean up the test environment
 */
import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('\n🏁 E2E Test Suite Completed');
  console.log('📊 Results available in playwright-report/');

  // Optional: Clean up test data from database
  // This would require API calls or direct database connection

  // Optional: Save artifacts
  // Screenshots and videos are already saved by Playwright config
}

export default globalTeardown;
