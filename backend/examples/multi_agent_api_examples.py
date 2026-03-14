"""
Multi-Agent Coordination API Usage Examples

Demonstrates how to use the Multi-Agent API endpoints:
- Agent coordination with different strategies
- Completion time prediction
- Strategy comparison
"""

import asyncio
import httpx
from typing import Dict, List


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/multi-agent"


# ============================================================================
# Example 1: Minimize Time Strategy
# ============================================================================

async def example_minimize_time():
    """
    Example: Coordinate agents to minimize total completion time

    Scenario: Software development team with urgent deadline.
    Assign tasks to fastest available agents.
    """
    print("\n" + "="*80)
    print("Example 1: Minimize Time Strategy")
    print("="*80)

    # Define agents
    agents = [
        {
            "id": "agent1",
            "name": "Senior Developer",
            "role": "developer",
            "backend_type": "gpt-4",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding", "code_review", "architecture"]
        },
        {
            "id": "agent2",
            "name": "Junior Developer",
            "role": "developer",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding", "testing"]
        },
        {
            "id": "agent3",
            "name": "DevOps Engineer",
            "role": "devops",
            "backend_type": "claude-3-sonnet",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["deployment", "monitoring", "infrastructure"]
        },
    ]

    # Define tasks
    tasks = [
        {
            "id": "task1",
            "name": "Fix Critical Bug",
            "description": "Fix authentication bug",
            "estimated_time": 30.0,
            "estimated_cost": 0.15,
            "required_capabilities": ["coding"],
            "priority": 3,
            "dependencies": []
        },
        {
            "id": "task2",
            "name": "Code Review",
            "description": "Review PR #123",
            "estimated_time": 15.0,
            "estimated_cost": 0.08,
            "required_capabilities": ["code_review"],
            "priority": 2,
            "dependencies": []
        },
        {
            "id": "task3",
            "name": "Write Tests",
            "description": "Add unit tests",
            "estimated_time": 20.0,
            "estimated_cost": 0.05,
            "required_capabilities": ["testing"],
            "priority": 1,
            "dependencies": ["task1"]
        },
        {
            "id": "task4",
            "name": "Deploy to Production",
            "description": "Deploy v2.1",
            "estimated_time": 10.0,
            "estimated_cost": 0.03,
            "required_capabilities": ["deployment"],
            "priority": 3,
            "dependencies": ["task1", "task3"]
        },
    ]

    # Request payload
    payload = {
        "agents": agents,
        "tasks": tasks,
        "strategy": "minimize_time"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/coordinate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully coordinated agents (MINIMIZE_TIME)!")
            print(f"Total Time: {result['total_time']:.2f} minutes")
            print(f"Total Cost: ${result['total_cost']:.2f}")
            print(f"Load Balance Score: {result['load_balance_score']:.2f}")
            print(f"Parallelism Factor: {result['parallelism_factor']:.2f}x")

            print(f"\nTask Assignments:")
            for assignment in result['assignments']:
                agent = next(a for a in agents if a['id'] == assignment['agent_id'])
                print(f"\n  {agent['name']} ({assignment['agent_id']}):")
                print(f"    Tasks: {', '.join(assignment['tasks'])}")
                print(f"    Time: {assignment['total_time']:.2f} min")
                print(f"    Cost: ${assignment['total_cost']:.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 2: Minimize Cost Strategy
# ============================================================================

async def example_minimize_cost():
    """
    Example: Coordinate agents to minimize API costs

    Scenario: Budget-constrained batch processing.
    Use cheaper models where possible.
    """
    print("\n" + "="*80)
    print("Example 2: Minimize Cost Strategy")
    print("="*80)

    # Define agents (different pricing tiers)
    agents = [
        {
            "id": "premium",
            "name": "Premium Agent",
            "role": "executor",
            "backend_type": "gpt-4",  # Expensive
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["analysis", "coding", "writing"]
        },
        {
            "id": "standard",
            "name": "Standard Agent",
            "role": "executor",
            "backend_type": "gpt-3.5-turbo",  # Medium
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["analysis", "coding", "writing"]
        },
        {
            "id": "budget",
            "name": "Budget Agent",
            "role": "executor",
            "backend_type": "claude-3-haiku",  # Cheap
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["analysis", "writing"]
        },
    ]

    # Define tasks with varying costs
    tasks = [
        {
            "id": "task1",
            "name": "Complex Analysis",
            "description": "Analyze architecture",
            "estimated_time": 45.0,
            "estimated_cost": 0.50,  # Expensive task
            "required_capabilities": ["analysis"],
            "priority": 2,
            "dependencies": []
        },
        {
            "id": "task2",
            "name": "Simple Code",
            "description": "Write helper function",
            "estimated_time": 20.0,
            "estimated_cost": 0.10,  # Cheap task
            "required_capabilities": ["coding"],
            "priority": 0,
            "dependencies": []
        },
        {
            "id": "task3",
            "name": "Documentation",
            "description": "Write docs",
            "estimated_time": 30.0,
            "estimated_cost": 0.05,  # Very cheap task
            "required_capabilities": ["writing"],
            "priority": 0,
            "dependencies": []
        },
    ]

    # Request payload
    payload = {
        "agents": agents,
        "tasks": tasks,
        "strategy": "minimize_cost"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/coordinate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully coordinated agents (MINIMIZE_COST)!")
            print(f"Total Time: {result['total_time']:.2f} minutes")
            print(f"Total Cost: ${result['total_cost']:.2f}")
            print(f"Load Balance Score: {result['load_balance_score']:.2f}")

            print(f"\nTask Assignments (optimized for cost):")
            for assignment in result['assignments']:
                agent = next(a for a in agents if a['id'] == assignment['agent_id'])
                print(f"\n  {agent['name']} ({agent['backend_type']}):")
                print(f"    Tasks: {', '.join(assignment['tasks'])}")
                print(f"    Cost: ${assignment['total_cost']:.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 3: Balance Load Strategy
# ============================================================================

async def example_balance_load():
    """
    Example: Distribute tasks evenly across agents

    Scenario: Long-running system with fair resource allocation.
    Ensure no single agent is overloaded.
    """
    print("\n" + "="*80)
    print("Example 3: Balance Load Strategy")
    print("="*80)

    # Define agents
    agents = [
        {
            "id": "agent1",
            "name": "Agent 1",
            "role": "worker",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["general"]
        },
        {
            "id": "agent2",
            "name": "Agent 2",
            "role": "worker",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["general"]
        },
        {
            "id": "agent3",
            "name": "Agent 3",
            "role": "worker",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["general"]
        },
    ]

    # Define many similar tasks
    tasks = [
        {
            "id": f"task{i}",
            "name": f"Task {i}",
            "description": f"Process batch {i}",
            "estimated_time": 15.0,
            "estimated_cost": 0.05,
            "required_capabilities": ["general"],
            "priority": 0,
            "dependencies": []
        }
        for i in range(1, 13)  # 12 tasks for 3 agents = 4 each
    ]

    # Request payload
    payload = {
        "agents": agents,
        "tasks": tasks,
        "strategy": "balance_load"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/coordinate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully coordinated agents (BALANCE_LOAD)!")
            print(f"Load Balance Score: {result['load_balance_score']:.2f} (higher = better balance)")
            print(f"Total Time: {result['total_time']:.2f} minutes")

            print(f"\nTask Distribution:")
            for assignment in result['assignments']:
                print(f"  {assignment['agent_id']}: {len(assignment['tasks'])} tasks")
                print(f"    Time: {assignment['total_time']:.2f} min")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 4: Maximize Throughput Strategy
# ============================================================================

async def example_maximize_throughput():
    """
    Example: Maximize parallel task execution

    Scenario: High-volume processing pipeline.
    Execute as many tasks concurrently as possible.
    """
    print("\n" + "="*80)
    print("Example 4: Maximize Throughput Strategy")
    print("="*80)

    # Define many agents
    agents = [
        {
            "id": f"agent{i}",
            "name": f"Agent {i}",
            "role": "processor",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["processing"]
        }
        for i in range(1, 6)  # 5 agents
    ]

    # Define tasks (some with dependencies)
    tasks = [
        {
            "id": "task1",
            "name": "Ingest Data",
            "description": "Load raw data",
            "estimated_time": 10.0,
            "estimated_cost": 0.05,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": []
        },
        {
            "id": "task2",
            "name": "Clean Data",
            "description": "Clean dataset",
            "estimated_time": 15.0,
            "estimated_cost": 0.07,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": ["task1"]
        },
        {
            "id": "task3",
            "name": "Transform Data",
            "description": "Transform to schema",
            "estimated_time": 20.0,
            "estimated_cost": 0.10,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": ["task2"]
        },
        {
            "id": "task4",
            "name": "Generate Report A",
            "description": "Analytics report A",
            "estimated_time": 12.0,
            "estimated_cost": 0.06,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": ["task3"]
        },
        {
            "id": "task5",
            "name": "Generate Report B",
            "description": "Analytics report B",
            "estimated_time": 12.0,
            "estimated_cost": 0.06,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": ["task3"]
        },
        {
            "id": "task6",
            "name": "Generate Report C",
            "description": "Analytics report C",
            "estimated_time": 12.0,
            "estimated_cost": 0.06,
            "required_capabilities": ["processing"],
            "priority": 0,
            "dependencies": ["task3"]
        },
    ]

    # Request payload
    payload = {
        "agents": agents,
        "tasks": tasks,
        "strategy": "maximize_throughput"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/coordinate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully coordinated agents (MAXIMIZE_THROUGHPUT)!")
            print(f"Parallelism Factor: {result['parallelism_factor']:.2f}x speedup")
            print(f"Total Time: {result['total_time']:.2f} minutes")
            print(f"Total Cost: ${result['total_cost']:.2f}")

            print(f"\nParallel Execution Plan:")
            for assignment in result['assignments']:
                if len(assignment['tasks']) > 0:
                    print(f"  {assignment['agent_id']}: {', '.join(assignment['tasks'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 5: Predict Completion Time
# ============================================================================

async def example_predict_completion():
    """
    Example: Predict completion time before executing

    Scenario: Planning phase - want to estimate completion time
    without actually coordinating agents.
    """
    print("\n" + "="*80)
    print("Example 5: Predict Completion Time")
    print("="*80)

    # Define agents
    agents = [
        {
            "id": "agent1",
            "name": "Fast Agent",
            "role": "executor",
            "backend_type": "gpt-4",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding"]
        },
        {
            "id": "agent2",
            "name": "Slow Agent",
            "role": "executor",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding"]
        },
    ]

    # Define tasks
    tasks = [
        {
            "id": "task1",
            "name": "Feature A",
            "description": "Implement feature A",
            "estimated_time": 30.0,
            "estimated_cost": 0.15,
            "required_capabilities": ["coding"],
            "priority": 0,
            "dependencies": []
        },
        {
            "id": "task2",
            "name": "Feature B",
            "description": "Implement feature B",
            "estimated_time": 40.0,
            "estimated_cost": 0.20,
            "required_capabilities": ["coding"],
            "priority": 0,
            "dependencies": []
        },
    ]

    # Request payload
    payload = {
        "agents": agents,
        "tasks": tasks,
        "strategy": "minimize_time"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully predicted completion time!")
            print(f"\nTime Estimates:")
            print(f"  Best Case:    {result['estimated_time_min']:.2f} minutes")
            print(f"  Average Case: {result['estimated_time_avg']:.2f} minutes")
            print(f"  Worst Case:   {result['estimated_time_max']:.2f} minutes")

            print(f"\nCost Estimates:")
            print(f"  Min: ${result['estimated_cost_min']:.2f}")
            print(f"  Avg: ${result['estimated_cost_avg']:.2f}")
            print(f"  Max: ${result['estimated_cost_max']:.2f}")

            print(f"\nParallelism: {result['parallelism_factor']:.2f}x")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 6: Compare Strategies
# ============================================================================

async def example_compare_strategies():
    """
    Example: Compare all coordination strategies

    Scenario: Same agents and tasks, different strategies.
    See how results differ.
    """
    print("\n" + "="*80)
    print("Example 6: Compare All Strategies")
    print("="*80)

    # Define agents
    agents = [
        {
            "id": "agent1",
            "name": "Premium Agent",
            "role": "executor",
            "backend_type": "gpt-4",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding", "analysis"]
        },
        {
            "id": "agent2",
            "name": "Standard Agent",
            "role": "executor",
            "backend_type": "gpt-3.5-turbo",
            "current_load": 0.0,
            "status": "idle",
            "capabilities": ["coding", "analysis"]
        },
    ]

    # Define tasks
    tasks = [
        {
            "id": "task1",
            "name": "Task 1",
            "description": "Complex analysis",
            "estimated_time": 30.0,
            "estimated_cost": 0.20,
            "required_capabilities": ["analysis"],
            "priority": 1,
            "dependencies": []
        },
        {
            "id": "task2",
            "name": "Task 2",
            "description": "Simple coding",
            "estimated_time": 15.0,
            "estimated_cost": 0.05,
            "required_capabilities": ["coding"],
            "priority": 0,
            "dependencies": []
        },
        {
            "id": "task3",
            "name": "Task 3",
            "description": "More analysis",
            "estimated_time": 25.0,
            "estimated_cost": 0.15,
            "required_capabilities": ["analysis"],
            "priority": 1,
            "dependencies": []
        },
    ]

    strategies = ["minimize_time", "minimize_cost", "balance_load", "maximize_throughput"]
    results = {}

    async with httpx.AsyncClient() as client:
        for strategy in strategies:
            payload = {
                "agents": agents,
                "tasks": tasks,
                "strategy": strategy
            }

            response = await client.post(
                f"{API_BASE_URL}/coordinate",
                json=payload,
                timeout=30.0
            )

            if response.status_code == 200:
                results[strategy] = response.json()

    # Display comparison
    print("\n" + "="*80)
    print("Strategy Comparison Results")
    print("="*80)

    print(f"\n{'Strategy':<25} {'Time':<12} {'Cost':<12} {'Balance':<12} {'Parallel':<12}")
    print("-" * 80)

    for strategy, result in results.items():
        print(
            f"{strategy:<25} "
            f"{result['total_time']:<12.2f} "
            f"${result['total_cost']:<11.2f} "
            f"{result['load_balance_score']:<12.2f} "
            f"{result['parallelism_factor']:<12.2f}x"
        )

    print("\nKey:")
    print("  Time: Total completion time (lower is faster)")
    print("  Cost: Total API cost (lower is cheaper)")
    print("  Balance: Load balance score (higher is more even)")
    print("  Parallel: Speedup factor (higher is more concurrent)")


# ============================================================================
# Example 7: List Available Strategies
# ============================================================================

async def example_list_strategies():
    """List all available coordination strategies"""
    print("\n" + "="*80)
    print("Example 7: Available Coordination Strategies")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/strategies",
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Available Strategies:")

            for strategy in data['strategies']:
                print(f"\n📊 {strategy['name']} ({strategy['id']})")
                print(f"   Description: {strategy['description']}")
                print(f"   Approach: {strategy['approach']}")
                print(f"   Use Case: {strategy['use_case']}")
                print(f"   Trade-offs: {strategy['trade_offs']}")
        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("Multi-Agent Coordination API Examples")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")

    try:
        # Run all examples
        await example_list_strategies()
        await example_minimize_time()
        await example_minimize_cost()
        await example_balance_load()
        await example_maximize_throughput()
        await example_predict_completion()
        await example_compare_strategies()

        print("\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80)

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
