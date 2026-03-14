/**
 * E2E Tests: Task Execution Workflow
 *
 * Tests the complete task lifecycle:
 * - Creating tasks
 * - Assigning tasks to agents
 * - Monitoring task execution
 * - Viewing task results
 * - Task filtering and search
 */
import { test, expect, testData } from './fixtures';

test.describe('Task Execution', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/tasks');
    await page.waitForLoadState('networkidle');
  });

  test('should display task list on page load', async ({ page }) => {
    // Wait for task list to load
    await expect(page.getByTestId('task-list')).toBeVisible();

    // Should show loading state first, then content
    await expect(page.getByText(/loading/i)).not.toBeVisible();

    // Should display tasks or empty state
    const taskCards = page.locator('[data-testid^="task-card-"]');
    const emptyState = page.getByText(/no tasks/i);

    await expect(taskCards.first().or(emptyState)).toBeVisible();
  });

  test('should create a new task successfully', async ({ page }) => {
    // Click create task button
    await page.getByRole('button', { name: /create task/i }).click();

    // Fill in task form
    await page.getByLabel(/title/i).fill(testData.tasks.codeReview.title);
    await page.getByLabel(/description/i).fill(testData.tasks.codeReview.description);
    await page.getByLabel(/priority/i).selectOption(testData.tasks.codeReview.priority);

    // Add tags
    for (const tag of testData.tasks.codeReview.tags) {
      await page.getByLabel(/tags/i).fill(tag);
      await page.keyboard.press('Enter');
    }

    // Submit form
    await page.getByRole('button', { name: /save|create/i }).click();

    // Should show success message
    await expect(page.getByText(/task created successfully/i)).toBeVisible();

    // Should display the new task in the list
    await expect(page.getByText(testData.tasks.codeReview.title)).toBeVisible();
  });

  test('should assign task to an agent', async ({ page, apiHelper }) => {
    // Create a test agent and task
    const agentId = await apiHelper.createAgent(testData.agents.codeReviewer);
    const taskId = await apiHelper.createTask(testData.tasks.codeReview);

    try {
      // Navigate to task detail page
      await page.goto(`/tasks/${taskId}`);
      await page.waitForLoadState('networkidle');

      // Click assign button
      await page.getByRole('button', { name: /assign/i }).click();

      // Select agent from dropdown
      await page.getByLabel(/select agent/i).selectOption(agentId);

      // Confirm assignment
      await page.getByRole('button', { name: /confirm|assign/i }).click();

      // Should show success message
      await expect(page.getByText(/assigned successfully/i)).toBeVisible();

      // Should display assigned agent
      await expect(page.getByText(/assigned to/i)).toBeVisible();
      await expect(page.getByTestId('assigned-agent')).toBeVisible();

    } finally {
      await apiHelper.deleteTask(taskId);
      await apiHelper.deleteAgent(agentId);
    }
  });

  test('should display task execution progress', async ({ page, apiHelper }) => {
    // Create task
    const taskId = await apiHelper.createTask(testData.tasks.codeReview);

    try {
      // Navigate to task detail page
      await page.goto(`/tasks/${taskId}`);
      await page.waitForLoadState('networkidle');

      // Should display status
      await expect(page.getByTestId('task-status')).toBeVisible();

      // Should display progress indicators
      const statusElement = page.getByTestId('task-status');
      const statusText = await statusElement.textContent();

      // Status should be one of the valid states
      expect(statusText?.toLowerCase()).toMatch(/pending|in_progress|completed|failed/);

    } finally {
      await apiHelper.deleteTask(taskId);
    }
  });

  test('should view task result after completion', async ({ page, apiHelper }) => {
    // Create and complete a task (via API)
    const taskId = await apiHelper.createTask({
      ...testData.tasks.bugFix,
      status: 'completed',
      result: 'Task completed successfully. Bug has been fixed.',
    });

    try {
      // Navigate to task detail page
      await page.goto(`/tasks/${taskId}`);
      await page.waitForLoadState('networkidle');

      // Should show completed status
      await expect(page.getByText(/completed/i)).toBeVisible();

      // Should display result section
      await expect(page.getByText(/result|output/i)).toBeVisible();

      // Should display the actual result
      await expect(page.getByText(/bug has been fixed/i)).toBeVisible();

    } finally {
      await apiHelper.deleteTask(taskId);
    }
  });

  test('should filter tasks by status', async ({ page, apiHelper }) => {
    // Create tasks with different statuses
    const task1Id = await apiHelper.createTask({ ...testData.tasks.codeReview, status: 'pending' });
    const task2Id = await apiHelper.createTask({ ...testData.tasks.bugFix, status: 'completed' });

    try {
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Filter by completed status
      await page.getByLabel(/filter by status/i).selectOption('completed');
      await page.waitForTimeout(500);

      // Should show only completed tasks
      await expect(page.getByText(testData.tasks.bugFix.title)).toBeVisible();
      await expect(page.getByText(testData.tasks.codeReview.title)).not.toBeVisible();

    } finally {
      await apiHelper.deleteTask(task1Id);
      await apiHelper.deleteTask(task2Id);
    }
  });

  test('should filter tasks by priority', async ({ page, apiHelper }) => {
    // Create tasks with different priorities
    const task1Id = await apiHelper.createTask({ ...testData.tasks.codeReview, priority: 'high' });
    const task2Id = await apiHelper.createTask({ ...testData.tasks.bugFix, priority: 'critical' });

    try {
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Filter by critical priority
      await page.getByLabel(/filter by priority/i).selectOption('critical');
      await page.waitForTimeout(500);

      // Should show only critical tasks
      await expect(page.getByText(testData.tasks.bugFix.title)).toBeVisible();

      // All visible tasks should have critical badge
      const priorityBadges = page.locator('[data-testid="task-priority"]');
      const count = await priorityBadges.count();

      for (let i = 0; i < count; i++) {
        await expect(priorityBadges.nth(i)).toHaveText(/critical/i);
      }

    } finally {
      await apiHelper.deleteTask(task1Id);
      await apiHelper.deleteTask(task2Id);
    }
  });

  test('should search tasks by title', async ({ page, apiHelper }) => {
    // Create test tasks
    const taskId = await apiHelper.createTask(testData.tasks.codeReview);

    try {
      // Reload page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Search for specific task
      await page.getByPlaceholder(/search/i).fill('Review PR');
      await page.waitForTimeout(500);

      // Should show matching tasks
      await expect(page.getByText(testData.tasks.codeReview.title)).toBeVisible();

    } finally {
      await apiHelper.deleteTask(taskId);
    }
  });

  test('should cancel a pending task', async ({ page, apiHelper }) => {
    // Create a pending task
    const taskId = await apiHelper.createTask({ ...testData.tasks.codeReview, status: 'pending' });

    try {
      // Navigate to task detail page
      await page.goto(`/tasks/${taskId}`);
      await page.waitForLoadState('networkidle');

      // Click cancel button
      await page.getByRole('button', { name: /cancel/i }).click();

      // Confirm cancellation
      await page.getByRole('button', { name: /confirm|yes/i }).click();

      // Should show success message
      await expect(page.getByText(/cancelled successfully/i)).toBeVisible();

      // Status should be updated
      await expect(page.getByText(/cancelled|canceled/i)).toBeVisible();

    } finally {
      await apiHelper.deleteTask(taskId);
    }
  });

  test('should retry a failed task', async ({ page, apiHelper }) => {
    // Create a failed task
    const taskId = await apiHelper.createTask({
      ...testData.tasks.bugFix,
      status: 'failed',
      error: 'Network timeout',
    });

    try {
      // Navigate to task detail page
      await page.goto(`/tasks/${taskId}`);
      await page.waitForLoadState('networkidle');

      // Should show failed status
      await expect(page.getByText(/failed/i)).toBeVisible();

      // Should show error message
      await expect(page.getByText(/network timeout/i)).toBeVisible();

      // Click retry button
      await page.getByRole('button', { name: /retry/i }).click();

      // Should show success message
      await expect(page.getByText(/retrying task/i)).toBeVisible();

      // Status should be updated to pending or in_progress
      await page.waitForTimeout(1000);
      const statusElement = page.getByTestId('task-status');
      const statusText = await statusElement.textContent();
      expect(statusText?.toLowerCase()).toMatch(/pending|in_progress/);

    } finally {
      await apiHelper.deleteTask(taskId);
    }
  });
});
