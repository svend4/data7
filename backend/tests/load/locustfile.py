"""
Load Testing with Locust for Meta-Orchestrator Switchboard API

Usage:
    locust -f locustfile.py --host=http://localhost:8000

Or with Docker:
    docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust \
        -f /mnt/locust/locustfile.py --host=http://api:8000

Performance Targets:
- API response time (p95): <500ms
- API response time (p99): <1000ms
- Throughput: >100 req/s per endpoint
- Error rate: <1%
"""

from locust import HttpUser, task, between, events
import random
import json


class MetaOrchestratorUser(HttpUser):
    """Simulated user for Meta-Orchestrator Switchboard."""

    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)

    # Store created resources for cleanup
    created_agents = []
    created_tasks = []

    def on_start(self):
        """Called when a user starts."""
        # Create a few agents for the user
        for i in range(2):
            response = self.client.post("/api/agents", json={
                "role": f"load_test_agent_{self.environment.runner.user_count}_{i}",
                "model": random.choice(["gpt-4", "claude-3-sonnet", "gpt-3.5-turbo"]),
                "temperature": 0.7,
                "max_tokens": 2000
            }, name="/api/agents [POST]")

            if response.status_code == 201:
                self.created_agents.append(response.json()["id"])

    def on_stop(self):
        """Called when a user stops."""
        # Cleanup created resources
        for agent_id in self.created_agents:
            self.client.delete(
                f"/api/agents/{agent_id}",
                name="/api/agents/:id [DELETE]"
            )

    # ========================================================================
    # Agent Operations (High Frequency)
    # ========================================================================

    @task(5)
    def list_agents(self):
        """List all agents."""
        self.client.get("/api/agents", name="/api/agents [GET]")

    @task(3)
    def get_agent(self):
        """Get a specific agent."""
        if self.created_agents:
            agent_id = random.choice(self.created_agents)
            self.client.get(
                f"/api/agents/{agent_id}",
                name="/api/agents/:id [GET]"
            )

    @task(2)
    def update_agent_status(self):
        """Update agent status."""
        if self.created_agents:
            agent_id = random.choice(self.created_agents)
            status = random.choice(["idle", "busy", "error"])
            self.client.patch(
                f"/api/agents/{agent_id}/status",
                json={"status": status},
                name="/api/agents/:id/status [PATCH]"
            )

    # ========================================================================
    # Task Operations (Medium Frequency)
    # ========================================================================

    @task(4)
    def create_task(self):
        """Create a new task."""
        if self.created_agents:
            agent_id = random.choice(self.created_agents)
            response = self.client.post("/api/tasks", json={
                "name": f"Load Test Task {random.randint(1, 1000)}",
                "description": "A task created during load testing",
                "agent_id": agent_id,
                "priority": random.randint(1, 3)
            }, name="/api/tasks [POST]")

            if response.status_code == 201:
                self.created_tasks.append(response.json()["id"])

    @task(3)
    def list_tasks(self):
        """List all tasks."""
        self.client.get("/api/tasks", name="/api/tasks [GET]")

    @task(2)
    def get_task(self):
        """Get a specific task."""
        if self.created_tasks:
            task_id = random.choice(self.created_tasks)
            self.client.get(
                f"/api/tasks/{task_id}",
                name="/api/tasks/:id [GET]"
            )

    # ========================================================================
    # Analytics Operations (Medium Frequency)
    # ========================================================================

    @task(4)
    def get_system_health(self):
        """Get system health metrics."""
        self.client.get(
            "/api/analytics/system",
            name="/api/analytics/system [GET]"
        )

    @task(3)
    def get_performance_metrics(self):
        """Get performance metrics."""
        timeframe = random.choice(["1h", "24h", "7d"])
        self.client.get(
            f"/api/analytics/performance?timeframe={timeframe}",
            name="/api/analytics/performance [GET]"
        )

    @task(2)
    def get_agent_analytics(self):
        """Get agent analytics."""
        timeframe = random.choice(["7d", "30d"])
        self.client.get(
            f"/api/analytics/agents?timeframe={timeframe}",
            name="/api/analytics/agents [GET]"
        )

    @task(2)
    def get_execution_analytics(self):
        """Get execution analytics."""
        self.client.get(
            "/api/analytics/executions?timeframe=30d",
            name="/api/analytics/executions [GET]"
        )

    # ========================================================================
    # Alerts Operations (Low Frequency)
    # ========================================================================

    @task(2)
    def list_alerts(self):
        """List alerts."""
        self.client.get("/api/alerts", name="/api/alerts [GET]")

    @task(1)
    def list_alert_rules(self):
        """List alert rules."""
        self.client.get(
            "/api/alerts/rules/list",
            name="/api/alerts/rules/list [GET]"
        )

    @task(1)
    def get_alert_stats(self):
        """Get alert statistics."""
        self.client.get(
            "/api/alerts/stats/summary?timeframe_days=7",
            name="/api/alerts/stats/summary [GET]"
        )

    # ========================================================================
    # Graph Operations (Low Frequency)
    # ========================================================================

    @task(2)
    def list_graphs(self):
        """List graphs."""
        self.client.get("/api/graphs", name="/api/graphs [GET]")

    @task(1)
    def create_graph(self):
        """Create a graph."""
        self.client.post("/api/graphs", json={
            "name": f"Load Test Graph {random.randint(1, 1000)}",
            "description": "A graph created during load testing"
        }, name="/api/graphs [POST]")


class ReadOnlyUser(HttpUser):
    """Read-only user for monitoring dashboards."""

    wait_time = between(2, 5)

    @task(10)
    def view_system_health(self):
        """View system health (dashboard auto-refresh)."""
        self.client.get("/api/analytics/system")

    @task(5)
    def view_performance(self):
        """View performance metrics."""
        self.client.get("/api/analytics/performance?timeframe=24h")

    @task(3)
    def view_agents(self):
        """View agent list."""
        self.client.get("/api/agents")

    @task(2)
    def view_alerts(self):
        """View alerts."""
        self.client.get("/api/alerts?status=active")


class HeavyOptimizationUser(HttpUser):
    """User performing heavy optimization operations."""

    wait_time = between(5, 10)

    created_graphs = []

    def on_start(self):
        """Create a graph for optimization."""
        response = self.client.post("/api/graphs", json={
            "name": f"Optimization Test Graph {self.environment.runner.user_count}",
            "description": "Graph for optimization testing"
        })

        if response.status_code == 201:
            self.created_graphs.append(response.json()["id"])

    @task(5)
    def analyze_graph(self):
        """Analyze graph structure."""
        if self.created_graphs:
            graph_id = random.choice(self.created_graphs)
            self.client.get(
                f"/api/optimization/graphs/{graph_id}/analyze",
                name="/api/optimization/graphs/:id/analyze [GET]"
            )

    @task(3)
    def optimize_graph(self):
        """Optimize graph."""
        if self.created_graphs:
            graph_id = random.choice(self.created_graphs)
            strategy = random.choice([
                "MINIMIZE_TIME",
                "MINIMIZE_COST",
                "BALANCE_LOAD",
                "MAXIMIZE_PARALLELISM"
            ])

            self.client.post(
                f"/api/optimization/graphs/{graph_id}/optimize",
                json={
                    "strategy": strategy,
                    "constraints": {}
                },
                name="/api/optimization/graphs/:id/optimize [POST]"
            )

    @task(2)
    def predict_execution(self):
        """Predict graph execution."""
        if self.created_graphs:
            graph_id = random.choice(self.created_graphs)
            self.client.post(
                f"/api/optimization/graphs/{graph_id}/predict",
                json={},
                name="/api/optimization/graphs/:id/predict [POST]"
            )


# ============================================================================
# Custom Events for Performance Tracking
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("🚀 Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    print("🏁 Load test completed")

    # Print summary
    stats = environment.stats
    total_rps = stats.total.current_rps
    total_fail_ratio = stats.total.fail_ratio

    print(f"\n📊 Performance Summary:")
    print(f"Total RPS: {total_rps:.2f}")
    print(f"Failure Rate: {total_fail_ratio * 100:.2f}%")
    print(f"Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")

    # Check if performance targets met
    if stats.total.avg_response_time < 500:
        print("✅ Average response time target met (<500ms)")
    else:
        print("❌ Average response time target NOT met (>500ms)")

    if total_fail_ratio < 0.01:
        print("✅ Error rate target met (<1%)")
    else:
        print("❌ Error rate target NOT met (>1%)")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Called when locust is quitting."""
    if environment.stats.total.fail_ratio > 0.05:
        print("⚠️  High failure rate detected!")
        environment.process_exit_code = 1
