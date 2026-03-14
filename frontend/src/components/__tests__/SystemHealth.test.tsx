/**
 * Tests for SystemHealth component
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { SystemHealth } from '../dashboard/SystemHealth';
import * as axiosModule from '@/lib/axios';

// Mock axios
vi.mock('@/lib/axios', () => ({
  axiosClient: {
    get: vi.fn(),
  },
}));

describe('SystemHealth', () => {
  const mockHealthData = {
    timestamp: new Date().toISOString(),
    total_agents: 10,
    agents_idle: 3,
    agents_busy: 5,
    agents_error: 2,
    agents_initializing: 0,
    total_connections: 15,
    active_connections: 12,
    pending_connections: 2,
    failed_connections: 1,
    avg_response_time: 1.5,
    error_rate: 0.05,
    active_executions: 8,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders loading state initially', () => {
    vi.mocked(axiosModule.axiosClient.get).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<SystemHealth />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('renders system health data after loading', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockHealthData,
    });

    render(<SystemHealth />);

    await waitFor(() => {
      expect(screen.getByText(/system health/i)).toBeInTheDocument();
    });

    // Check if agent counts are displayed
    expect(screen.getByText(/10/)).toBeInTheDocument(); // total agents
    expect(screen.getByText(/3/)).toBeInTheDocument(); // idle agents
  });

  it('displays healthy status when error rate is low', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: { ...mockHealthData, error_rate: 0.02 },
    });

    render(<SystemHealth />);

    await waitFor(() => {
      expect(screen.getByText(/healthy/i)).toBeInTheDocument();
    });
  });

  it('displays warning status when error rate is moderate', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: { ...mockHealthData, error_rate: 0.08 },
    });

    render(<SystemHealth />);

    await waitFor(() => {
      expect(screen.getByText(/warning|degraded/i)).toBeInTheDocument();
    });
  });

  it('displays critical status when error rate is high', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: { ...mockHealthData, error_rate: 0.20 },
    });

    render(<SystemHealth />);

    await waitFor(() => {
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    vi.mocked(axiosModule.axiosClient.get).mockRejectedValueOnce(
      new Error('API Error')
    );

    render(<SystemHealth />);

    await waitFor(() => {
      // Should show error state or empty state
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    consoleError.mockRestore();
  });

  it('auto-refreshes data at specified interval', async () => {
    vi.useFakeTimers();

    vi.mocked(axiosModule.axiosClient.get).mockResolvedValue({
      data: mockHealthData,
    });

    render(<SystemHealth refreshInterval={5000} />);

    // Initial call
    expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(1);

    // Advance time by 5 seconds
    vi.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(2);
    });

    // Advance again
    vi.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(3);
    });

    vi.useRealTimers();
  });

  it('cleans up interval on unmount', async () => {
    vi.useFakeTimers();

    vi.mocked(axiosModule.axiosClient.get).mockResolvedValue({
      data: mockHealthData,
    });

    const { unmount } = render(<SystemHealth refreshInterval={5000} />);

    expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(1);

    // Unmount component
    unmount();

    // Advance time - should not call API again
    vi.advanceTimersByTime(10000);

    expect(axiosModule.axiosClient.get).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });

  it('displays connection statistics correctly', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockHealthData,
    });

    render(<SystemHealth />);

    await waitFor(() => {
      // Should show connection counts
      expect(screen.getByText(/15/)).toBeInTheDocument(); // total connections
      expect(screen.getByText(/12/)).toBeInTheDocument(); // active connections
    });
  });

  it('displays performance metrics', async () => {
    vi.mocked(axiosModule.axiosClient.get).mockResolvedValueOnce({
      data: mockHealthData,
    });

    render(<SystemHealth />);

    await waitFor(() => {
      // Should show response time
      expect(screen.getByText(/1.5/)).toBeInTheDocument();
      // Should show error rate as percentage
      expect(screen.getByText(/5%|0.05/)).toBeInTheDocument();
    });
  });
});
