/**
 * Tests for ActiveAlerts component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ActiveAlerts } from '../dashboard/ActiveAlerts';
import * as axiosModule from '@/lib/axios';

vi.mock('@/lib/axios', () => ({
  axiosClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('ActiveAlerts', () => {
  const mockAlerts = [
    {
      id: 'alert-1',
      rule_id: 'high_error_rate',
      rule_name: 'High Error Rate',
      severity: 'critical',
      status: 'active',
      message: 'Error rate exceeds 15% threshold',
      details: {
        conditions: [
          {
            metric: 'error_rate',
            threshold: 0.15,
            current_value: 0.18,
            operator: '>',
          },
        ],
        all_metrics: { error_rate: 0.18 },
        tags: ['error', 'system-health'],
      },
      triggered_at: new Date().toISOString(),
      notification_sent: true,
      notification_channels: ['email', 'slack'],
    },
    {
      id: 'alert-2',
      rule_id: 'low_agent_availability',
      rule_name: 'Low Agent Availability',
      severity: 'warning',
      status: 'acknowledged',
      message: 'Less than 20% agents available',
      details: {
        conditions: [
          {
            metric: 'agent_idle_percentage',
            threshold: 0.20,
            current_value: 0.15,
            operator: '<',
          },
        ],
        all_metrics: { agent_idle_percentage: 0.15 },
        tags: ['capacity', 'agents'],
      },
      triggered_at: new Date(Date.now() - 3600000).toISOString(),
      acknowledged_at: new Date(Date.now() - 1800000).toISOString(),
      acknowledged_by: 'operator1',
      notification_sent: true,
      notification_channels: ['email'],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders empty state when no alerts', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: [],
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText(/no alerts/i)).toBeInTheDocument();
      expect(screen.getByText(/operating normally/i)).toBeInTheDocument();
    });
  });

  it('renders alerts list when alerts exist', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockAlerts,
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('High Error Rate')).toBeInTheDocument();
      expect(screen.getByText('Low Agent Availability')).toBeInTheDocument();
    });
  });

  it('displays severity indicators correctly', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockAlerts,
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('CRITICAL')).toBeInTheDocument();
      expect(screen.getByText('WARNING')).toBeInTheDocument();
    });
  });

  it('displays status badges correctly', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockAlerts,
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('active')).toBeInTheDocument();
      expect(screen.getByText('acknowledged')).toBeInTheDocument();
    });
  });

  it('allows acknowledging active alerts', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: [mockAlerts[0]], // Only active alert
    });

    vi.mocked(axiosModule.axiosClient.post).mockResolvedValueOnce({
      data: { ...mockAlerts[0], status: 'acknowledged' },
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('Acknowledge')).toBeInTheDocument();
    });

    const ackButton = screen.getByText('Acknowledge');
    fireEvent.click(ackButton);

    await waitFor(() => {
      expect(axiosModule.axiosClient.post).toHaveBeenCalledWith(
        '/alerts/alert-1/acknowledge',
        { user: 'operator' }
      );
    });
  });

  it('allows resolving alerts', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: [mockAlerts[0]],
    });

    vi.mocked(axiosModule.axiosClient.post).mockResolvedValueOnce({
      data: { ...mockAlerts[0], status: 'resolved' },
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('Resolve')).toBeInTheDocument();
    });

    const resolveButton = screen.getByText('Resolve');
    fireEvent.click(resolveButton);

    await waitFor(() => {
      expect(axiosModule.axiosClient.post).toHaveBeenCalledWith(
        '/alerts/alert-1/resolve',
        { user: 'operator' }
      );
    });
  });

  it('expands alert details on click', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: [mockAlerts[0]],
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText('High Error Rate')).toBeInTheDocument();
    });

    // Click on alert to expand
    const alert = screen.getByText('High Error Rate').closest('div');
    if (alert) {
      fireEvent.click(alert);
    }

    await waitFor(() => {
      expect(screen.getByText(/triggered conditions/i)).toBeInTheDocument();
    });
  });

  it('filters alerts by severity', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockAlerts,
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      const severityFilter = screen.getByRole('combobox', { name: /severity/i });
      expect(severityFilter).toBeInTheDocument();
    });

    // Change filter
    const severityFilter = screen.getAllByRole('combobox')[1]; // Second select is severity
    fireEvent.change(severityFilter, { target: { value: 'critical' } });

    await waitFor(() => {
      expect(axiosModule.axiosClient.get).toHaveBeenCalledWith(
        '/alerts',
        expect.objectContaining({
          params: expect.objectContaining({ severity: 'critical' }),
        })
      );
    });
  });

  it('filters alerts by status', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockAlerts,
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      const statusFilter = screen.getAllByRole('combobox')[0]; // First select is status
      fireEvent.change(statusFilter, { target: { value: 'acknowledged' } });
    });

    await waitFor(() => {
      expect(axiosModule.axiosClient.get).toHaveBeenCalledWith(
        '/alerts',
        expect.objectContaining({
          params: expect.objectContaining({ status: 'acknowledged' }),
        })
      );
    });
  });

  it('auto-refreshes at specified interval', async () => {
    vi.useFakeTimers();

    vi.mocked(axiosModule.axiosClient.get).mockResolvedValue({
      data: mockAlerts,
    });

    render(<ActiveAlerts refreshInterval={10000} />);

    // Initial call
    expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(1);

    // Advance time
    vi.advanceTimersByTime(10000);

    await waitFor(() => {
      expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(2);
    });

    vi.useRealTimers();
  });

  it('displays relative timestamps', async () => {
    const recentAlert = {
      ...mockAlerts[0],
      triggered_at: new Date(Date.now() - 120000).toISOString(), // 2 minutes ago
    };

    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: [recentAlert],
    });

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText(/2m ago/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    vi.mocked(axiosModule.axiosClient.get).mockRejectedValueOnce(
      new Error('Failed to fetch alerts')
    );

    render(<ActiveAlerts />);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch alerts/i)).toBeInTheDocument();
    });

    consoleError.mockRestore();
  });
});
