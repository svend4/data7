"""
Integration tests for Agents API

Tests cover:
- Agent CRUD operations
- Agent status updates
- Agent task assignment
- Agent filtering and pagination
- Error handling and validation
"""

import pytest
from httpx import AsyncClient


class TestAgentsAPI:
    """Test Agents API endpoints."""

    @pytest.mark.asyncio
    async def test_create_agent(self, async_client: AsyncClient):
        """Test creating a new agent."""
        response = await async_client.post("/api/agents", json={
            "role": "code_reviewer",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000
        })

        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "code_reviewer"
        assert data["model"] == "gpt-4"
        assert data["status"] == "idle"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_agent_validation_error(self, async_client: AsyncClient):
        """Test agent creation with invalid data."""
        response = await async_client.post("/api/agents", json={
            "role": "",  # Empty role
            "model": "invalid-model",
            "temperature": 2.0  # Invalid temperature
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_agents(self, async_client: AsyncClient, sample_agents):
        """Test listing all agents."""
        response = await async_client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(sample_agents)

    @pytest.mark.asyncio
    async def test_get_agent(self, async_client: AsyncClient, sample_agent):
        """Test retrieving a specific agent."""
        response = await async_client.get(f"/api/agents/{sample_agent.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_agent.id
        assert data["role"] == sample_agent.role

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, async_client: AsyncClient):
        """Test retrieving non-existent agent."""
        response = await async_client.get("/api/agents/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_agent(self, async_client: AsyncClient, sample_agent):
        """Test updating an agent."""
        response = await async_client.put(f"/api/agents/{sample_agent.id}", json={
            "role": "updated_role",
            "temperature": 0.9
        })

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "updated_role"
        assert data["temperature"] == 0.9

    @pytest.mark.asyncio
    async def test_update_agent_status(self, async_client: AsyncClient, sample_agent):
        """Test updating agent status."""
        response = await async_client.patch(
            f"/api/agents/{sample_agent.id}/status",
            json={"status": "busy"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "busy"

    @pytest.mark.asyncio
    async def test_delete_agent(self, async_client: AsyncClient, sample_agent):
        """Test deleting an agent."""
        response = await async_client.delete(f"/api/agents/{sample_agent.id}")

        assert response.status_code == 204

        # Verify agent is deleted
        get_response = await async_client.get(f"/api/agents/{sample_agent.id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_filter_agents_by_status(self, async_client: AsyncClient, sample_agents):
        """Test filtering agents by status."""
        response = await async_client.get("/api/agents?status=idle")

        assert response.status_code == 200
        data = response.json()
        assert all(agent["status"] == "idle" for agent in data)

    @pytest.mark.asyncio
    async def test_filter_agents_by_model(self, async_client: AsyncClient, sample_agents):
        """Test filtering agents by model."""
        response = await async_client.get("/api/agents?model=gpt-4")

        assert response.status_code == 200
        data = response.json()
        assert all(agent["model"] == "gpt-4" for agent in data)

    @pytest.mark.asyncio
    async def test_agent_pagination(self, async_client: AsyncClient, sample_agents):
        """Test agent list pagination."""
        response = await async_client.get("/api/agents?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestAgentsIntegration:
    """Test agent integration with other services."""

    @pytest.mark.asyncio
    async def test_agent_with_tasks(self, async_client: AsyncClient, sample_agent):
        """Test agent can be assigned tasks."""
        # Create task for agent
        task_response = await async_client.post("/api/tasks", json={
            "name": "Test Task",
            "description": "A test task",
            "agent_id": sample_agent.id,
            "priority": 2
        })

        assert task_response.status_code == 201

        # Verify agent shows task
        agent_response = await async_client.get(f"/api/agents/{sample_agent.id}")
        assert agent_response.status_code == 200

    @pytest.mark.asyncio
    async def test_agent_workflow(self, async_client: AsyncClient):
        """Test complete agent workflow."""
        # 1. Create agent
        create_response = await async_client.post("/api/agents", json={
            "role": "workflow_tester",
            "model": "gpt-4",
            "temperature": 0.7
        })
        assert create_response.status_code == 201
        agent_id = create_response.json()["id"]

        # 2. Update status to busy
        status_response = await async_client.patch(
            f"/api/agents/{agent_id}/status",
            json={"status": "busy"}
        )
        assert status_response.status_code == 200

        # 3. Create task for agent
        task_response = await async_client.post("/api/tasks", json={
            "name": "Workflow Task",
            "description": "Testing workflow",
            "agent_id": agent_id,
            "priority": 1
        })
        assert task_response.status_code == 201

        # 4. Verify agent state
        agent_response = await async_client.get(f"/api/agents/{agent_id}")
        assert agent_response.status_code == 200
        agent_data = agent_response.json()
        assert agent_data["status"] == "busy"

        # 5. Complete workflow and delete
        delete_response = await async_client.delete(f"/api/agents/{agent_id}")
        assert delete_response.status_code == 204

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, async_client: AsyncClient):
        """Test concurrent agent operations."""
        import asyncio

        # Create multiple agents concurrently
        create_tasks = [
            async_client.post("/api/agents", json={
                "role": f"concurrent_agent_{i}",
                "model": "gpt-4",
                "temperature": 0.7
            })
            for i in range(5)
        ]

        responses = await asyncio.gather(*create_tasks)

        # Verify all created successfully
        assert all(r.status_code == 201 for r in responses)

        # Verify all have unique IDs
        agent_ids = [r.json()["id"] for r in responses]
        assert len(agent_ids) == len(set(agent_ids))
