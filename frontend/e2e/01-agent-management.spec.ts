/**
 * E2E Tests: Agent Management Workflow
 *
 * Tests the complete agent lifecycle:
 * - Creating agents
 * - Viewing agent list
 * - Updating agent configuration
 * - Deleting agents
 * - Filtering and searching
 */
import { test, expect, testData } from './fixtures';

test.describe('Agent Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to agents page
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('should display agent list on page load', async ({ page }) => {
    // Wait for agent list to load
    await expect(page.getByTestId('agent-list')).toBeVisible();

    // Should show loading state first, then content
    await expect(page.getByText(/loading/i)).not.toBeVisible();

    // Should display agents or empty state
    const agentCards = page.locator('[data-testid^="agent-card-"]');
    const emptyState = page.getByText(/no agents/i);

    await expect(agentCards.first().or(emptyState)).toBeVisible();
  });

  test('should create a new agent successfully', async ({ page }) => {
    // Click create agent button
    await page.getByRole('button', { name: /create agent/i }).click();

    // Fill in agent form
    await page.getByLabel(/role/i).fill(testData.agents.codeReviewer.role);
    await page.getByLabel(/model/i).selectOption(testData.agents.codeReviewer.model);
    await page.getByLabel(/temperature/i).fill(testData.agents.codeReviewer.temperature.toString());
    await page.getByLabel(/max tokens/i).fill(testData.agents.codeReviewer.max_tokens.toString());
    await page.getByLabel(/system prompt/i).fill(testData.agents.codeReviewer.system_prompt);

    // Submit form
    await page.getByRole('button', { name: /save|create/i }).click();

    // Should show success message
    await expect(page.getByText(/agent created successfully/i)).toBeVisible();

    // Should redirect to agent list or detail page
    await page.waitForURL(/\/agents/);

    // Should display the new agent in the list
    await expect(page.getByText(testData.agents.codeReviewer.role)).toBeVisible();
  });

  test('should display agent details when clicking on an agent', async ({ page, apiHelper }) => {
    // Create a test agent via API
    const agentId = await apiHelper.createAgent(testData.agents.codeReviewer);

    try {
      // Reload page to see new agent
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Click on the agent card
      await page.getByTestId(`agent-card-${agentId}`).click();

      // Should navigate to detail page
      await page.waitForURL(`/agents/${agentId}`);

      // Should display agent details
      await expect(page.getByText(testData.agents.codeReviewer.role)).toBeVisible();
      await expect(page.getByText(testData.agents.codeReviewer.model)).toBeVisible();
      await expect(page.getByText(/temperature.*0\.7/i)).toBeVisible();

      // Should display agent status
      await expect(page.getByText(/status/i)).toBeVisible();

    } finally {
      // Cleanup
      await apiHelper.deleteAgent(agentId);
    }
  });

  test('should update agent configuration', async ({ page, apiHelper }) => {
    // Create a test agent
    const agentId = await apiHelper.createAgent(testData.agents.codeReviewer);

    try {
      // Navigate to agent detail page
      await page.goto(`/agents/${agentId}`);
      await page.waitForLoadState('networkidle');

      // Click edit button
      await page.getByRole('button', { name: /edit/i }).click();

      // Update temperature
      const temperatureInput = page.getByLabel(/temperature/i);
      await temperatureInput.clear();
      await temperatureInput.fill('0.9');

      // Save changes
      await page.getByRole('button', { name: /save|update/i }).click();

      // Should show success message
      await expect(page.getByText(/updated successfully/i)).toBeVisible();

      // Should display updated value
      await expect(page.getByText(/temperature.*0\.9/i)).toBeVisible();

    } finally {
      await apiHelper.deleteAgent(agentId);
    }
  });

  test('should delete agent with confirmation', async ({ page, apiHelper }) => {
    // Create a test agent
    const agentId = await apiHelper.createAgent(testData.agents.bugFixer);

    // Navigate to agent detail page
    await page.goto(`/agents/${agentId}`);
    await page.waitForLoadState('networkidle');

    // Click delete button
    await page.getByRole('button', { name: /delete/i }).click();

    // Should show confirmation dialog
    await expect(page.getByText(/are you sure/i)).toBeVisible();

    // Confirm deletion
    await page.getByRole('button', { name: /confirm|yes/i }).click();

    // Should show success message
    await expect(page.getByText(/deleted successfully/i)).toBeVisible();

    // Should redirect to agent list
    await page.waitForURL('/agents');

    // Agent should no longer be visible
    await expect(page.getByTestId(`agent-card-${agentId}`)).not.toBeVisible();
  });

  test('should filter agents by status', async ({ page, apiHelper }) => {
    // Create test agents
    const agent1Id = await apiHelper.createAgent(testData.agents.codeReviewer);
    const agent2Id = await apiHelper.createAgent(testData.agents.bugFixer);

    try {
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Apply filter
      await page.getByLabel(/filter by status/i).selectOption('idle');

      // Wait for filter to apply
      await page.waitForTimeout(500);

      // Should show only idle agents
      const visibleAgents = await page.locator('[data-testid^="agent-card-"]').count();
      expect(visibleAgents).toBeGreaterThan(0);

      // All visible agents should have idle status
      const statusBadges = page.locator('[data-testid="agent-status"]');
      const count = await statusBadges.count();

      for (let i = 0; i < count; i++) {
        await expect(statusBadges.nth(i)).toHaveText(/idle/i);
      }

    } finally {
      await apiHelper.deleteAgent(agent1Id);
      await apiHelper.deleteAgent(agent2Id);
    }
  });

  test('should search agents by role', async ({ page, apiHelper }) => {
    // Create test agents
    const agent1Id = await apiHelper.createAgent(testData.agents.codeReviewer);

    try {
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Search for code_reviewer
      await page.getByPlaceholder(/search/i).fill('code_reviewer');

      // Wait for search to apply
      await page.waitForTimeout(500);

      // Should show matching agents
      await expect(page.getByText('code_reviewer')).toBeVisible();

      // Should not show non-matching agents
      await expect(page.getByText('bug_fixer')).not.toBeVisible();

    } finally {
      await apiHelper.deleteAgent(agent1Id);
    }
  });

  test('should display agent performance metrics', async ({ page, apiHelper }) => {
    // Create a test agent
    const agentId = await apiHelper.createAgent(testData.agents.codeReviewer);

    try {
      // Navigate to agent detail page
      await page.goto(`/agents/${agentId}`);
      await page.waitForLoadState('networkidle');

      // Should display metrics section
      await expect(page.getByText(/metrics|performance/i)).toBeVisible();

      // Should display key metrics
      await expect(page.getByText(/tasks completed/i)).toBeVisible();
      await expect(page.getByText(/success rate/i)).toBeVisible();
      await expect(page.getByText(/average response time/i)).toBeVisible();

    } finally {
      await apiHelper.deleteAgent(agentId);
    }
  });
});
