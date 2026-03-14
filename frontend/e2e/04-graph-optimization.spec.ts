/**
 * E2E Tests: Graph Optimization Workflow
 *
 * Tests graph optimization features:
 * - Creating task graphs
 * - Analyzing graphs
 * - Running optimization
 * - Viewing optimization results
 * - 3D visualization
 */
import { test, expect } from './fixtures';

test.describe('Graph Optimization', () => {
  test('should display graphs list', async ({ page }) => {
    await page.goto('/optimization/graphs');
    await page.waitForLoadState('networkidle');

    // Should display graphs section
    await expect(page.getByTestId('graphs-list')).toBeVisible();

    // Should show graphs or empty state
    const graphCards = page.locator('[data-testid^="graph-card-"]');
    const emptyState = page.getByText(/no graphs/i);

    await expect(graphCards.first().or(emptyState)).toBeVisible();
  });

  test('should create a new task graph', async ({ page }) => {
    await page.goto('/optimization/graphs');
    await page.waitForLoadState('networkidle');

    // Click create graph button
    await page.getByRole('button', { name: /create graph/i }).click();

    // Fill in graph form
    await page.getByLabel(/name/i).fill('Test Optimization Graph');
    await page.getByLabel(/description/i).fill('Graph for E2E testing');

    // Add some nodes
    await page.getByRole('button', { name: /add node/i }).click();
    await page.getByLabel(/task name/i).fill('Task 1');
    await page.getByRole('button', { name: /save node|add/i }).click();

    await page.getByRole('button', { name: /add node/i }).click();
    await page.getByLabel(/task name/i).fill('Task 2');
    await page.getByRole('button', { name: /save node|add/i }).click();

    // Save graph
    await page.getByRole('button', { name: /save graph|create/i }).click();

    // Should show success message
    await expect(page.getByText(/graph created successfully/i)).toBeVisible();

    // Should display new graph in list
    await expect(page.getByText('Test Optimization Graph')).toBeVisible();
  });

  test('should analyze a graph', async ({ page, request }) => {
    // Create a graph via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/optimization/graphs`, {
      data: {
        name: 'Analysis Test Graph',
        description: 'Graph for analysis testing',
        nodes: [
          { id: 'node1', label: 'Task 1', type: 'task' },
          { id: 'node2', label: 'Task 2', type: 'task' },
          { id: 'node3', label: 'Task 3', type: 'task' },
        ],
        edges: [
          { source: 'node1', target: 'node2' },
          { source: 'node2', target: 'node3' },
        ],
      },
    });
    const graphData = await createResponse.json();
    const graphId = graphData.id;

    try {
      // Navigate to graph detail page
      await page.goto(`/optimization/graphs/${graphId}`);
      await page.waitForLoadState('networkidle');

      // Click analyze button
      await page.getByRole('button', { name: /analyze/i }).click();

      // Should show analyzing state
      await expect(page.getByText(/analyzing/i)).toBeVisible();

      // Wait for analysis to complete
      await page.waitForTimeout(2000);

      // Should display analysis results
      await expect(page.getByText(/analysis results/i)).toBeVisible();

      // Should display key metrics
      await expect(page.getByText(/total tasks/i)).toBeVisible();
      await expect(page.getByText(/dependencies/i)).toBeVisible();
      await expect(page.getByText(/parallelism/i)).toBeVisible();
      await expect(page.getByText(/critical path/i)).toBeVisible();

    } finally {
      await request.delete(`${baseURL}/api/optimization/graphs/${graphId}`);
    }
  });

  test('should run optimization on a graph', async ({ page, request }) => {
    // Create a graph via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/optimization/graphs`, {
      data: {
        name: 'Optimization Test Graph',
        description: 'Graph for optimization testing',
        nodes: [
          { id: 'node1', label: 'Task 1', type: 'task', duration: 100 },
          { id: 'node2', label: 'Task 2', type: 'task', duration: 150 },
          { id: 'node3', label: 'Task 3', type: 'task', duration: 80 },
          { id: 'node4', label: 'Task 4', type: 'task', duration: 120 },
        ],
        edges: [
          { source: 'node1', target: 'node3' },
          { source: 'node2', target: 'node4' },
        ],
      },
    });
    const graphData = await createResponse.json();
    const graphId = graphData.id;

    try {
      // Navigate to graph detail page
      await page.goto(`/optimization/graphs/${graphId}`);
      await page.waitForLoadState('networkidle');

      // Click optimize button
      await page.getByRole('button', { name: /optimize/i }).click();

      // Select optimization strategy
      await page.getByLabel(/strategy/i).selectOption('minimize_time');

      // Confirm optimization
      await page.getByRole('button', { name: /start optimization|run/i }).click();

      // Should show optimizing state
      await expect(page.getByText(/optimizing/i)).toBeVisible();

      // Wait for optimization to complete
      await page.waitForTimeout(3000);

      // Should display optimization results
      await expect(page.getByText(/optimization results/i)).toBeVisible();

      // Should display improvements
      await expect(page.getByText(/time saved/i)).toBeVisible();
      await expect(page.getByText(/efficiency gain/i)).toBeVisible();

    } finally {
      await request.delete(`${baseURL}/api/optimization/graphs/${graphId}`);
    }
  });

  test('should visualize graph in 3D', async ({ page, request }) => {
    // Create a graph via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/optimization/graphs`, {
      data: {
        name: '3D Visualization Graph',
        description: 'Graph for 3D testing',
        nodes: [
          { id: 'node1', label: 'Task 1', type: 'task' },
          { id: 'node2', label: 'Task 2', type: 'task' },
        ],
        edges: [
          { source: 'node1', target: 'node2' },
        ],
      },
    });
    const graphData = await createResponse.json();
    const graphId = graphData.id;

    try {
      // Navigate to graph detail page
      await page.goto(`/optimization/graphs/${graphId}`);
      await page.waitForLoadState('networkidle');

      // Should display 3D canvas
      const canvas = page.locator('canvas[data-engine="three.js"]');
      await expect(canvas).toBeVisible();

      // Canvas should have non-zero dimensions
      const boundingBox = await canvas.boundingBox();
      expect(boundingBox).not.toBeNull();
      expect(boundingBox!.width).toBeGreaterThan(0);
      expect(boundingBox!.height).toBeGreaterThan(0);

      // Should have view controls
      await expect(page.getByRole('button', { name: /reset view/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /zoom in/i })).toBeVisible();
      await expect(page.getByRole('button', { name: /zoom out/i })).toBeVisible();

    } finally {
      await request.delete(`${baseURL}/api/optimization/graphs/${graphId}`);
    }
  });

  test('should compare optimization strategies', async ({ page, request }) => {
    // Create a graph via API
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/optimization/graphs`, {
      data: {
        name: 'Strategy Comparison Graph',
        description: 'Graph for comparing strategies',
        nodes: Array.from({ length: 5 }, (_, i) => ({
          id: `node${i + 1}`,
          label: `Task ${i + 1}`,
          type: 'task',
          duration: 100 + i * 20,
        })),
        edges: [
          { source: 'node1', target: 'node2' },
          { source: 'node1', target: 'node3' },
          { source: 'node2', target: 'node4' },
          { source: 'node3', target: 'node5' },
        ],
      },
    });
    const graphData = await createResponse.json();
    const graphId = graphData.id;

    try {
      // Navigate to graph detail page
      await page.goto(`/optimization/graphs/${graphId}`);
      await page.waitForLoadState('networkidle');

      // Click compare strategies button
      await page.getByRole('button', { name: /compare strategies/i }).click();

      // Should show comparison view
      await expect(page.getByText(/strategy comparison/i)).toBeVisible();

      // Should display multiple strategies
      await expect(page.getByText(/minimize time/i)).toBeVisible();
      await expect(page.getByText(/balance load/i)).toBeVisible();
      await expect(page.getByText(/minimize cost/i)).toBeVisible();

      // Should display comparison metrics
      await expect(page.getByText(/estimated time/i)).toBeVisible();
      await expect(page.getByText(/agent utilization/i)).toBeVisible();

    } finally {
      await request.delete(`${baseURL}/api/optimization/graphs/${graphId}`);
    }
  });

  test('should export optimization results', async ({ page, request }) => {
    // Create and optimize a graph
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';
    const createResponse = await request.post(`${baseURL}/api/optimization/graphs`, {
      data: {
        name: 'Export Test Graph',
        description: 'Graph for export testing',
        nodes: [
          { id: 'node1', label: 'Task 1', type: 'task' },
        ],
        edges: [],
      },
    });
    const graphData = await createResponse.json();
    const graphId = graphData.id;

    try {
      // Run optimization
      await request.post(`${baseURL}/api/optimization/graphs/${graphId}/optimize`, {
        data: { strategy: 'minimize_time' },
      });

      // Navigate to results page
      await page.goto(`/optimization/graphs/${graphId}/results`);
      await page.waitForLoadState('networkidle');

      // Set up download listener
      const downloadPromise = page.waitForEvent('download');

      // Click export button
      await page.getByRole('button', { name: /export/i }).click();

      // Select format
      await page.getByLabel(/format/i).selectOption('json');
      await page.getByRole('button', { name: /download|export/i }).click();

      // Should trigger download
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.json$/);

    } finally {
      await request.delete(`${baseURL}/api/optimization/graphs/${graphId}`);
    }
  });
});
