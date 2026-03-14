/**
 * Playwright Test Fixtures
 *
 * Reusable fixtures for E2E tests
 */
import { test as base, Page } from '@playwright/test';

/**
 * Test data fixtures
 */
export const testData = {
  agents: {
    codeReviewer: {
      role: 'code_reviewer',
      model: 'gpt-4',
      temperature: 0.7,
      max_tokens: 2000,
      system_prompt: 'You are a senior code reviewer',
    },
    bugFixer: {
      role: 'bug_fixer',
      model: 'claude-3-sonnet',
      temperature: 0.5,
      max_tokens: 1500,
      system_prompt: 'You are an expert debugger',
    },
  },
  tasks: {
    codeReview: {
      title: 'Review PR #123',
      description: 'Review the authentication module changes',
      priority: 'high',
      tags: ['code-review', 'security'],
    },
    bugFix: {
      title: 'Fix login timeout issue',
      description: 'Users report timeout after 5 minutes',
      priority: 'critical',
      tags: ['bug', 'authentication'],
    },
  },
  alertRules: {
    highErrorRate: {
      name: 'High Error Rate Alert',
      description: 'Trigger when error rate exceeds 10%',
      conditions: [
        {
          metric: 'error_rate',
          operator: '>',
          threshold: 0.10,
          duration: 60,
        },
      ],
      severity: 'critical',
      notifications: [
        {
          channel: 'email',
          config: { to: 'test@example.com' },
          enabled: true,
        },
      ],
      enabled: true,
    },
  },
};

/**
 * Custom fixtures for authentication and common actions
 */
type CustomFixtures = {
  authenticatedPage: Page;
  apiHelper: {
    createAgent: (agentData: any) => Promise<string>;
    createTask: (taskData: any) => Promise<string>;
    deleteAgent: (agentId: string) => Promise<void>;
    deleteTask: (taskId: string) => Promise<void>;
  };
};

export const test = base.extend<CustomFixtures>({
  // Authenticated page fixture (if authentication is added later)
  authenticatedPage: async ({ page }, use) => {
    // TODO: Implement authentication when auth is added
    // For now, just return the page as-is
    await use(page);
  },

  // API helper fixture for setup/teardown
  apiHelper: async ({ request }, use) => {
    const baseURL = process.env.E2E_BASE_URL?.replace('80', '8000') || 'http://localhost:8000';

    const helper = {
      async createAgent(agentData: any): Promise<string> {
        const response = await request.post(`${baseURL}/api/agents`, {
          data: agentData,
        });
        const data = await response.json();
        return data.id;
      },

      async createTask(taskData: any): Promise<string> {
        const response = await request.post(`${baseURL}/api/tasks`, {
          data: taskData,
        });
        const data = await response.json();
        return data.id;
      },

      async deleteAgent(agentId: string): Promise<void> {
        await request.delete(`${baseURL}/api/agents/${agentId}`);
      },

      async deleteTask(taskId: string): Promise<void> {
        await request.delete(`${baseURL}/api/tasks/${taskId}`);
      },
    };

    await use(helper);
  },
});

export { expect } from '@playwright/test';
