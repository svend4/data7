# API Usage Examples

Complete examples for Meta-Orchestrator Switchboard API.

**Base URL**: `http://localhost:8000`

## Table of Contents

1. [Agents](#agents)
2. [Tasks](#tasks)
3. [Connections](#connections)
4. [Graphs](#graphs)
5. [Executions](#executions)
6. [Complete Workflow](#complete-workflow)

---

## Agents

### Create an Agent

```bash
curl -X POST "http://localhost:8000/api/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Budget Analyst",
    "capabilities": [
      {
        "name": "financial_analysis",
        "category": "finance",
        "level": 5,
        "description": "Analyze budgets and financial reports"
      },
      {
        "name": "data_visualization",
        "category": "visualization",
        "level": 3,
        "description": "Create charts and graphs"
      }
    ],
    "position": {
      "x": 10.0,
      "y": 5.0,
      "z": 0.0
    },
    "metadata": {
      "department": "Finance",
      "priority": "high"
    }
  }'
```

### List All Agents

```bash
curl -X GET "http://localhost:8000/api/agents"
```

### Get Agent by ID

```bash
curl -X GET "http://localhost:8000/api/agents/{agent_id}"
```

### Update Agent

```bash
curl -X PUT "http://localhost:8000/api/agents/{agent_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "busy",
    "metadata": {
      "last_task": "financial_report_q4"
    }
  }'
```

### Get Agent Statistics

```bash
curl -X GET "http://localhost:8000/api/agents/stats/summary"
```

**Response:**
```json
{
  "total_agents": 5,
  "idle_agents": 3,
  "busy_agents": 2,
  "offline_agents": 0,
  "avg_success_rate": 0.9523,
  "avg_response_time": 1.234
}
```

---

## Tasks

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Analyze Q4 budget and create summary report",
    "task_type": "financial_analysis",
    "priority": 8,
    "assigned_agent_id": "agent_abc123",
    "metadata": {
      "quarter": "Q4",
      "year": 2026,
      "deadline": "2026-02-15"
    }
  }'
```

### List Tasks with Filters

```bash
# All tasks
curl -X GET "http://localhost:8000/api/tasks"

# Filter by status
curl -X GET "http://localhost:8000/api/tasks?status=running"

# Filter by agent
curl -X GET "http://localhost:8000/api/tasks?assigned_agent_id=agent_abc123"

# Filter by type
curl -X GET "http://localhost:8000/api/tasks?task_type=financial_analysis"
```

### Start Task Execution

```bash
curl -X PUT "http://localhost:8000/api/tasks/{task_id}/start" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Complete Task

```bash
curl -X PUT "http://localhost:8000/api/tasks/{task_id}/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "result": {
      "summary": "Q4 budget analysis completed",
      "total_spend": 1250000,
      "variance": -5.2,
      "recommendations": [
        "Reduce marketing spend by 10%",
        "Increase R&D budget for next quarter"
      ]
    }
  }'
```

### Fail Task

```bash
curl -X PUT "http://localhost:8000/api/tasks/{task_id}/fail" \
  -H "Content-Type: application/json" \
  -d '{
    "error": "Insufficient data: missing expense reports for November"
  }'
```

### Get Task Statistics

```bash
curl -X GET "http://localhost:8000/api/tasks/stats/summary"
```

**Response:**
```json
{
  "total_tasks": 42,
  "pending": 5,
  "queued": 8,
  "running": 12,
  "completed": 15,
  "failed": 2,
  "avg_duration_seconds": 45.67,
  "success_rate": 0.8824
}
```

---

## Connections

### Create Connection

```bash
curl -X POST "http://localhost:8000/api/connections" \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent_id": "agent_abc123",
    "to_agent_id": "agent_def456",
    "bandwidth": 0.8,
    "metadata": {
      "priority": "high",
      "protocol": "json-rpc"
    }
  }'
```

### Establish Connection (Allocate Sockets)

```bash
curl -X PUT "http://localhost:8000/api/connections/{connection_id}/establish" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "id": "conn_xyz789",
  "from_agent_id": "agent_abc123",
  "to_agent_id": "agent_def456",
  "status": "connected",
  "socket_from": 15,
  "socket_to": 42,
  "bandwidth": 0.8,
  "latency_ms": 12.5,
  "established_at": "2026-02-04T23:00:00Z"
}
```

### List Connections

```bash
# All connections
curl -X GET "http://localhost:8000/api/connections"

# Filter by status
curl -X GET "http://localhost:8000/api/connections?status=connected"

# Filter by agent (from or to)
curl -X GET "http://localhost:8000/api/connections?agent_id=agent_abc123"
```

### Disconnect Connection

```bash
curl -X PUT "http://localhost:8000/api/connections/{connection_id}/disconnect"
```

### Get Connection Statistics

```bash
curl -X GET "http://localhost:8000/api/connections/stats/summary"
```

**Response:**
```json
{
  "total_connections": 18,
  "connected": 12,
  "disconnected": 6,
  "transmitting": 5,
  "available_sockets": 76,
  "avg_bandwidth": 0.845,
  "avg_latency_ms": 15.23
}
```

---

## Graphs

### Create Communication Graph

```bash
curl -X POST "http://localhost:8000/api/graphs" \
  -H "Content-Type: application/json" \
  -d '{
    "root_task_id": "task_root_123",
    "nodes": [
      "agent_data_collector",
      "agent_analyzer",
      "agent_reporter"
    ],
    "edges": [
      {
        "from_agent_id": "agent_data_collector",
        "to_agent_id": "agent_analyzer",
        "bandwidth": 1.0
      },
      {
        "from_agent_id": "agent_analyzer",
        "to_agent_id": "agent_reporter",
        "bandwidth": 0.8
      }
    ],
    "execution_plan": [
      "task_collect_data",
      "task_analyze",
      "task_generate_report"
    ],
    "metadata": {
      "workflow": "financial_reporting",
      "priority": "high"
    }
  }'
```

### List All Graphs

```bash
curl -X GET "http://localhost:8000/api/graphs"
```

### Get Graph by ID

```bash
curl -X GET "http://localhost:8000/api/graphs/{graph_id}"
```

### Execute Graph

```bash
curl -X POST "http://localhost:8000/api/graphs/{graph_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "started_by": "user_admin",
      "reason": "quarterly_reporting"
    }
  }'
```

**Response:**
```json
{
  "id": "exec_abc789",
  "graph_id": "graph_123",
  "status": "running",
  "current_step": 0,
  "completed_tasks": [],
  "failed_tasks": [],
  "active_connections": [],
  "results": {},
  "progress": 0.0,
  "started_at": "2026-02-04T23:30:00Z"
}
```

### List Graph Executions

```bash
curl -X GET "http://localhost:8000/api/graphs/{graph_id}/executions"
```

---

## Executions

### Get Execution Status

```bash
curl -X GET "http://localhost:8000/api/executions/{execution_id}"
```

**Response:**
```json
{
  "id": "exec_abc789",
  "graph_id": "graph_123",
  "status": "running",
  "current_step": 2,
  "completed_tasks": ["task_collect_data", "task_analyze"],
  "failed_tasks": [],
  "active_connections": ["conn_1", "conn_2"],
  "results": {
    "task_collect_data": {"records": 1500},
    "task_analyze": {"insights": ["...", "..."]}
  },
  "progress": 0.67,
  "started_at": "2026-02-04T23:30:00Z",
  "completed_at": null
}
```

### Cancel Execution

```bash
curl -X PUT "http://localhost:8000/api/executions/{execution_id}/cancel"
```

---

## Complete Workflow

Complete example: Create agents, connect them, create graph, and execute.

```bash
#!/bin/bash

BASE_URL="http://localhost:8000/api"

echo "=== 1. Create Agents ==="
AGENT1=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Data Collector",
    "capabilities": [{"name": "data_collection", "category": "data", "level": 5}]
  }' | jq -r '.id')

AGENT2=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Data Analyzer",
    "capabilities": [{"name": "analysis", "category": "analytics", "level": 5}]
  }' | jq -r '.id')

AGENT3=$(curl -s -X POST "$BASE_URL/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Report Generator",
    "capabilities": [{"name": "reporting", "category": "output", "level": 5}]
  }' | jq -r '.id')

echo "Created agents: $AGENT1, $AGENT2, $AGENT3"

echo -e "\n=== 2. Create Tasks ==="
TASK1=$(curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Collect financial data\",
    \"task_type\": \"data_collection\",
    \"priority\": 9,
    \"assigned_agent_id\": \"$AGENT1\"
  }" | jq -r '.id')

TASK2=$(curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Analyze collected data\",
    \"task_type\": \"analysis\",
    \"priority\": 8,
    \"assigned_agent_id\": \"$AGENT2\"
  }" | jq -r '.id')

TASK3=$(curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{
    \"description\": \"Generate final report\",
    \"task_type\": \"reporting\",
    \"priority\": 7,
    \"assigned_agent_id\": \"$AGENT3\"
  }" | jq -r '.id')

echo "Created tasks: $TASK1, $TASK2, $TASK3"

echo -e "\n=== 3. Create Communication Graph ==="
GRAPH=$(curl -s -X POST "$BASE_URL/graphs" \
  -H "Content-Type: application/json" \
  -d "{
    \"root_task_id\": \"$TASK1\",
    \"nodes\": [\"$AGENT1\", \"$AGENT2\", \"$AGENT3\"],
    \"edges\": [
      {\"from_agent_id\": \"$AGENT1\", \"to_agent_id\": \"$AGENT2\", \"bandwidth\": 1.0},
      {\"from_agent_id\": \"$AGENT2\", \"to_agent_id\": \"$AGENT3\", \"bandwidth\": 0.8}
    ],
    \"execution_plan\": [\"$TASK1\", \"$TASK2\", \"$TASK3\"]
  }" | jq -r '.id')

echo "Created graph: $GRAPH"

echo -e "\n=== 4. Execute Graph ==="
EXECUTION=$(curl -s -X POST "$BASE_URL/graphs/$GRAPH/execute" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.id')

echo "Started execution: $EXECUTION"

echo -e "\n=== 5. Check Execution Status ==="
curl -s -X GET "$BASE_URL/executions/$EXECUTION" | jq '.'

echo -e "\n=== 6. View Statistics ==="
echo "Agents:"
curl -s -X GET "$BASE_URL/agents/stats/summary" | jq '.'

echo -e "\nTasks:"
curl -s -X GET "$BASE_URL/tasks/stats/summary" | jq '.'

echo -e "\nConnections:"
curl -s -X GET "$BASE_URL/connections/stats/summary" | jq '.'
```

Save as `workflow_example.sh` and run:
```bash
chmod +x workflow_example.sh
./workflow_example.sh
```

---

## Testing with Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Create agent
agent_data = {
    "role": "Budget Analyst",
    "capabilities": [
        {
            "name": "financial_analysis",
            "category": "finance",
            "level": 5,
            "description": "Analyze budgets"
        }
    ]
}

response = requests.post(f"{BASE_URL}/agents", json=agent_data)
agent = response.json()
print(f"Created agent: {agent['id']}")

# Create task
task_data = {
    "description": "Analyze Q4 budget",
    "task_type": "financial_analysis",
    "priority": 8,
    "assigned_agent_id": agent['id']
}

response = requests.post(f"{BASE_URL}/tasks", json=task_data)
task = response.json()
print(f"Created task: {task['id']}")

# Start task
response = requests.put(f"{BASE_URL}/tasks/{task['id']}/start")
print(f"Task started: {response.json()['status']}")

# Get statistics
stats = requests.get(f"{BASE_URL}/agents/stats/summary").json()
print(f"Total agents: {stats['total_agents']}")
print(f"Idle agents: {stats['idle_agents']}")
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `503 Service Unavailable` - No available sockets

**Error Response Format:**
```json
{
  "detail": "Agent agent_123 not found"
}
```

---

## Interactive API Documentation

Visit http://localhost:8000/api/docs for interactive Swagger UI where you can:
- Browse all endpoints
- See request/response schemas
- Try out API calls directly
- View example payloads
