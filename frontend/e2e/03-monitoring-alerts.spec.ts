/**
 * E2E Tests: Monitoring and Alerts Workflow
 *
 * Tests monitoring and alerting features:
 * - System health dashboard
 * - Performance metrics
 * - Alert management
 * - Alert rules configuration
 * - Real-time updates
 */
import { test, expect, testData } from './fixtures';

test.describe('Monitoring and Alerts', () => {
  test('should display system health dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Should display system health section
    await expect(page.getByText(/system health/i)).toBeVisible();

    // Should display key metrics
    await expect(page.getByText(/total agents/i)).toBeVisible();
    await expect(page.getByText(/active tasks/i)).toBeVisible();
    await expect(page.getByText(/success rate/i)).toBeVisible();
    await expect(page.getByText(/error rate/i)).toBeVisible();

    // Should display metrics as numbers
    const metrics = page.locator('[data-testid^="metric-"]');
    expect(await metrics.count()).toBeGreaterThan(0);
  });

  test('should auto-refresh dashboard metrics', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Get initial metric value
    const errorRateMetric = page.getByTestId('metric-error-rate');
    const initialValue = await errorRateMetric.textContent();

    // Wait for auto-refresh (typically 5-10 seconds)
    await page.waitForTimeout(6000);

    // Value should be re-fetched (might be same or different)
    const updatedValue = await errorRateMetric.textContent();

    // At minimum, the element should still exist and be visible
    await expect(errorRateMetric).toBeVisible();
    expect(typeof updatedValue).toBe('string');
  });

  test('should display active alerts', async ({ page }) => {
    await page.goto('/alerts');
    await page.waitForLoadState('networkidle');

    // Should display alerts section
    await expect(page.getByTestId('alerts-list')).toBeVisible();

    // Should show alerts or empty state
    const alertCards = page.locator('[data-testid^="alert-card-"]');
    const emptyState = page.getByText(/no active alerts/i);

    await expect(alertCards.first().or(emptyState)).toBeVisible();
  });

  test('should acknowledge an active alert', async ({ page, request }) => {
    // First, trigger an alert via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const evalResponse = await request.post(`${baseURL}/api/alerts/evaluate`);
    const evalData = await evalResponse.json();

    if (evalData.triggered_alerts && evalData.triggered_alerts.length > 0) {
      const alertId = evalData.triggered_alerts[0].id;

      // Navigate to alerts page
      await page.goto('/alerts');
      await page.waitForLoadState('networkidle');

      // Find the alert card
      const alertCard = page.getByTestId(`alert-card-${alertId}`);

      if (await alertCard.isVisible()) {
        // Click acknowledge button
        await alertCard.getByRole('button', { name: /acknowledge/i }).click();

        // Should show success message
        await expect(page.getByText(/acknowledged/i)).toBeVisible();

        // Alert status should be updated
        await expect(alertCard.getByText(/acknowledged/i)).toBeVisible();
      }
    }
  });

  test('should resolve an acknowledged alert', async ({ page, request }) => {
    // Trigger and acknowledge an alert
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const evalResponse = await request.post(`${baseURL}/api/alerts/evaluate`);
    const evalData = await evalResponse.json();

    if (evalData.triggered_alerts && evalData.triggered_alerts.length > 0) {
      const alertId = evalData.triggered_alerts[0].id;

      // Acknowledge via API
      await request.post(`${baseURL}/api/alerts/${alertId}/acknowledge`, {
        data: { user: 'e2e_test' },
      });

      // Navigate to alerts page
      await page.goto('/alerts');
      await page.waitForLoadState('networkidle');

      // Find the alert card
      const alertCard = page.getByTestId(`alert-card-${alertId}`);

      if (await alertCard.isVisible()) {
        // Click resolve button
        await alertCard.getByRole('button', { name: /resolve/i }).click();

        // Should show success message
        await expect(page.getByText(/resolved/i)).toBeVisible();

        // Alert should be removed from active alerts or marked as resolved
        await page.waitForTimeout(1000);
        const statusText = await alertCard.getByTestId('alert-status').textContent();
        expect(statusText?.toLowerCase()).toMatch(/resolved/);
      }
    }
  });

  test('should filter alerts by severity', async ({ page }) => {
    await page.goto('/alerts');
    await page.waitForLoadState('networkidle');

    // Apply filter
    await page.getByLabel(/filter by severity/i).selectOption('critical');
    await page.waitForTimeout(500);

    // All visible alerts should have critical severity
    const severityBadges = page.locator('[data-testid="alert-severity"]');
    const count = await severityBadges.count();

    if (count > 0) {
      for (let i = 0; i < count; i++) {
        await expect(severityBadges.nth(i)).toHaveText(/critical/i);
      }
    }
  });

  test('should display alert statistics', async ({ page }) => {
    await page.goto('/alerts/stats');
    await page.waitForLoadState('networkidle');

    // Should display statistics section
    await expect(page.getByText(/alert statistics/i)).toBeVisible();

    // Should display key statistics
    await expect(page.getByText(/total alerts/i)).toBeVisible();
    await expect(page.getByText(/active alerts/i)).toBeVisible();
    await expect(page.getByText(/acknowledged alerts/i)).toBeVisible();
    await expect(page.getByText(/resolved alerts/i)).toBeVisible();

    // Should display charts or graphs
    const charts = page.locator('[data-testid^="chart-"]');
    expect(await charts.count()).toBeGreaterThan(0);
  });

  test('should create a new alert rule', async ({ page }) => {
    await page.goto('/alerts/rules');
    await page.waitForLoadState('networkidle');

    // Click create rule button
    await page.getByRole('button', { name: /create rule/i }).click();

    // Fill in rule form
    await page.getByLabel(/name/i).fill(testData.alertRules.highErrorRate.name);
    await page.getByLabel(/description/i).fill(testData.alertRules.highErrorRate.description);
    await page.getByLabel(/severity/i).selectOption(testData.alertRules.highErrorRate.severity);

    // Add condition
    await page.getByRole('button', { name: /add condition/i }).click();
    await page.getByLabel(/metric/i).selectOption('error_rate');
    await page.getByLabel(/operator/i).selectOption('>');
    await page.getByLabel(/threshold/i).fill('0.10');

    // Save rule
    await page.getByRole('button', { name: /save|create/i }).click();

    // Should show success message
    await expect(page.getByText(/rule created successfully/i)).toBeVisible();

    // Should display new rule in list
    await expect(page.getByText(testData.alertRules.highErrorRate.name)).toBeVisible();
  });

  test('should enable/disable alert rule', async ({ page, request }) => {
    // Create a rule via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/alerts/rules`, {
      data: testData.alertRules.highErrorRate,
    });
    const ruleData = await createResponse.json();
    const ruleId = ruleData.id;

    try {
      // Navigate to rules page
      await page.goto('/alerts/rules');
      await page.waitForLoadState('networkidle');

      // Find the rule
      const ruleCard = page.getByTestId(`rule-card-${ruleId}`);
      await expect(ruleCard).toBeVisible();

      // Toggle enabled/disabled
      const toggleSwitch = ruleCard.getByRole('switch', { name: /enabled/i });
      const initialState = await toggleSwitch.isChecked();

      await toggleSwitch.click();

      // Should show success message
      await expect(page.getByText(/updated successfully/i)).toBeVisible();

      // State should be toggled
      const newState = await toggleSwitch.isChecked();
      expect(newState).toBe(!initialState);

    } finally {
      // Cleanup
      await request.delete(`${baseURL}/api/alerts/rules/${ruleId}`);
    }
  });

  test('should display performance trends', async ({ page }) => {
    await page.goto('/analytics/performance');
    await page.waitForLoadState('networkidle');

    // Should display performance section
    await expect(page.getByText(/performance/i)).toBeVisible();

    // Should display trend charts
    await expect(page.getByText(/success rate/i)).toBeVisible();
    await expect(page.getByText(/response time/i)).toBeVisible();
    await expect(page.getByText(/throughput/i)).toBeVisible();

    // Should allow changing timeframe
    await page.getByLabel(/timeframe/i).selectOption('7d');
    await page.waitForTimeout(1000);

    // Charts should update (verified by checking for loading state)
    await expect(page.getByText(/loading/i)).not.toBeVisible();
  });

  test('should detect anomalies in metrics', async ({ page }) => {
    await page.goto('/analytics/trends');
    await page.waitForLoadState('networkidle');

    // Select metric with anomaly detection
    await page.getByLabel(/metric/i).selectOption('error_rate');
    await page.waitForTimeout(1000);

    // Should display anomalies section
    const anomaliesSection = page.getByTestId('anomalies-section');

    if (await anomaliesSection.isVisible()) {
      // Should list detected anomalies or show "no anomalies"
      const anomalyCards = page.locator('[data-testid^="anomaly-"]');
      const noAnomalies = page.getByText(/no anomalies detected/i);

      await expect(anomalyCards.first().or(noAnomalies)).toBeVisible();
    }
  });
});
