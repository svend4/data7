# E2E Testing with Playwright

End-to-end tests for the Meta-Orchestrator Switchboard frontend application.

## Overview

These tests validate critical user journeys across the entire application, ensuring that all features work together correctly from the user's perspective.

## Test Suites

### 1. Agent Management (`01-agent-management.spec.ts`)
Tests the complete agent lifecycle:
- Viewing agent list
- Creating new agents
- Viewing agent details
- Updating agent configuration
- Deleting agents
- Filtering and searching agents
- Agent performance metrics

### 2. Task Execution (`02-task-execution.spec.ts`)
Tests task management and execution:
- Creating tasks
- Assigning tasks to agents
- Monitoring task execution
- Viewing task results
- Filtering tasks by status and priority
- Canceling and retrying tasks

### 3. Monitoring and Alerts (`03-monitoring-alerts.spec.ts`)
Tests monitoring and alerting features:
- System health dashboard
- Auto-refreshing metrics
- Alert management (acknowledge, resolve)
- Alert rules configuration
- Alert statistics and trends
- Anomaly detection

### 4. Graph Optimization (`04-graph-optimization.spec.ts`)
Tests graph optimization workflows:
- Creating task graphs
- Analyzing graphs
- Running optimization
- 3D visualization
- Comparing optimization strategies
- Exporting results

## Running Tests

### Prerequisites

```bash
# Install dependencies
cd frontend
npm install

# Install Playwright browsers
npx playwright install
```

### Run All Tests

```bash
# Run all E2E tests (headless mode)
npm run test:e2e

# Run with UI (headed mode)
npm run test:e2e:headed

# Run in debug mode
npm run test:e2e:debug
```

### Run Specific Tests

```bash
# Run a specific test file
npx playwright test e2e/01-agent-management.spec.ts

# Run tests matching a pattern
npx playwright test -g "should create"

# Run a specific test
npx playwright test -g "should create a new agent"
```

### Run in Different Browsers

```bash
# Run in Chromium only
npx playwright test --project=chromium

# Run in Firefox only
npx playwright test --project=firefox

# Run in WebKit only
npx playwright test --project=webkit

# Run in all browsers
npx playwright test --project=chromium --project=firefox --project=webkit
```

## Test Configuration

The Playwright configuration is in `playwright.config.ts`:

```typescript
{
  testDir: './e2e',
  timeout: 30 * 1000,
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: ['html', 'json', 'junit'],
  use: {
    baseURL: 'http://localhost:80',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
}
```

## Environment Variables

```bash
# Base URL for tests (default: http://localhost:80)
E2E_BASE_URL=http://localhost:80

# Run in CI mode (affects retries and workers)
CI=true
```

## Test Fixtures

### Custom Fixtures

- `authenticatedPage`: Pre-authenticated page (for when auth is implemented)
- `apiHelper`: Helper for creating/deleting test data via API

### Test Data

Predefined test data is available in `fixtures.ts`:

```typescript
testData.agents.codeReviewer
testData.agents.bugFixer
testData.tasks.codeReview
testData.tasks.bugFix
testData.alertRules.highErrorRate
```

## Best Practices

### 1. Use Test IDs

```tsx
// Component
<div data-testid="agent-list">...</div>

// Test
await page.getByTestId('agent-list')
```

### 2. Wait for Network Idle

```typescript
await page.goto('/agents');
await page.waitForLoadState('networkidle');
```

### 3. Clean Up Test Data

```typescript
try {
  const agentId = await apiHelper.createAgent(...);
  // ... test code ...
} finally {
  await apiHelper.deleteAgent(agentId);
}
```

### 4. Use Explicit Waits

```typescript
// Wait for element
await expect(page.getByText('Success')).toBeVisible();

// Wait for condition
await page.waitForTimeout(1000);
```

### 5. Handle Dynamic Content

```typescript
// Wait for loading to finish
await expect(page.getByText(/loading/i)).not.toBeVisible();

// Check for element or empty state
const items = page.locator('[data-testid^="item-"]');
const emptyState = page.getByText(/no items/i);
await expect(items.first().or(emptyState)).toBeVisible();
```

## Debugging Tests

### Visual Debugging

```bash
# Run with UI mode
npx playwright test --ui

# Run with headed browser
npx playwright test --headed

# Run with debug mode (opens inspector)
npx playwright test --debug
```

### Trace Viewer

```bash
# Generate trace on failure (configured by default)
npx playwright test

# View trace
npx playwright show-trace trace.zip
```

### Screenshots and Videos

Configured to capture on failure:
- Screenshots: `playwright-report/screenshots/`
- Videos: `playwright-report/videos/`

### Console Logs

```typescript
// Enable console logging
page.on('console', msg => console.log(msg.text()));

// Enable network logging
page.on('request', request => console.log('>>', request.method(), request.url()));
page.on('response', response => console.log('<<', response.status(), response.url()));
```

## CI/CD Integration

Tests are integrated into the GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

```yaml
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npm run test:e2e

- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Troubleshooting

### Tests Timing Out

```typescript
// Increase timeout for specific test
test('slow test', async ({ page }) => {
  test.setTimeout(60000);
  // ...
});

// Increase global timeout in config
timeout: 60 * 1000,
```

### Element Not Found

```typescript
// Wait for element explicitly
await page.waitForSelector('[data-testid="element"]');

// Use more flexible locators
await page.getByRole('button', { name: /submit/i });
```

### Flaky Tests

```typescript
// Enable retries
retries: 2,

// Use auto-waiting assertions
await expect(page.getByText('Success')).toBeVisible();

// Avoid fixed timeouts
// Bad:
await page.waitForTimeout(1000);

// Good:
await expect(element).toBeVisible();
```

### Backend Not Ready

The global setup waits for the backend to be ready. If tests still fail:

```typescript
// Increase wait time in global-setup.ts
const maxAttempts = 60; // from 30
```

## Performance

### Parallel Execution

```typescript
// Run tests in parallel (default)
fullyParallel: true,
workers: undefined, // Use all cores

// Limit workers for stability
workers: 2,
```

### Test Isolation

Each test runs in a fresh browser context for isolation:

```typescript
test.describe.configure({ mode: 'parallel' });
```

## Reports

### HTML Report

```bash
# Generate and open HTML report
npx playwright show-report
```

### JSON Report

Test results are saved to `playwright-results.json` for analysis.

### JUnit Report

Test results are saved to `playwright-results.xml` for CI integration.

## Coverage

E2E tests complement unit and integration tests:
- **Unit tests**: Component logic in isolation
- **Integration tests**: API endpoints
- **E2E tests**: Complete user workflows

Together they provide comprehensive test coverage.
