"""
TSP API Usage Examples

Demonstrates how to use the TSP API endpoints:
- Multi-depot TSP
- Hierarchical TSP
- Stochastic TSP
- Route optimization
"""

import asyncio
import httpx
from typing import Dict, List


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/tsp"


# ============================================================================
# Example 1: Multi-depot TSP - Multi-Agent Task Allocation
# ============================================================================

async def example_multi_depot_tsp():
    """
    Example: Allocate tasks to multiple AI agents

    Scenario: 3 agents need to handle 8 customer support tickets.
    Find optimal assignment to minimize total response time.
    """
    print("\n" + "="*80)
    print("Example 1: Multi-depot TSP for Agent Task Allocation")
    print("="*80)

    # Define tasks (nodes)
    nodes = [
        {"id": "ticket1", "x": 0.0, "y": 0.0, "demand": 1.0, "service_time": 5.0, "priority": 2},
        {"id": "ticket2", "x": 1.0, "y": 0.0, "demand": 1.0, "service_time": 3.0, "priority": 1},
        {"id": "ticket3", "x": 2.0, "y": 0.0, "demand": 1.0, "service_time": 7.0, "priority": 2},
        {"id": "ticket4", "x": 0.0, "y": 1.0, "demand": 1.0, "service_time": 4.0, "priority": 0},
        {"id": "ticket5", "x": 1.0, "y": 1.0, "demand": 1.0, "service_time": 6.0, "priority": 1},
        {"id": "ticket6", "x": 2.0, "y": 1.0, "demand": 1.0, "service_time": 3.0, "priority": 0},
        {"id": "ticket7", "x": 0.0, "y": 2.0, "demand": 1.0, "service_time": 5.0, "priority": 1},
        {"id": "ticket8", "x": 1.0, "y": 2.0, "demand": 1.0, "service_time": 4.0, "priority": 0},
    ]

    # Define agents (depots)
    depots = [
        {
            "id": "agent1",
            "node": {"id": "agent1", "x": -1.0, "y": 0.0},
            "capacity": 5.0,
            "available_agents": 1
        },
        {
            "id": "agent2",
            "node": {"id": "agent2", "x": 1.0, "y": -1.0},
            "capacity": 5.0,
            "available_agents": 1
        },
        {
            "id": "agent3",
            "node": {"id": "agent3", "x": 3.0, "y": 1.0},
            "capacity": 5.0,
            "available_agents": 1
        },
    ]

    # Build distance matrix (simplified - using Euclidean distance)
    distance_matrix = {}
    all_points = nodes + [d["node"] for d in depots]

    for p1 in all_points:
        for p2 in all_points:
            if p1["id"] != p2["id"]:
                dist = ((p1["x"] - p2["x"])**2 + (p1["y"] - p2["y"])**2)**0.5
                distance_matrix[f"{p1['id']}_{p2['id']}"] = dist

    # Request payload
    payload = {
        "nodes": nodes,
        "depots": depots,
        "distance_matrix": distance_matrix,
        "algorithm": "cluster_first_route_second"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/multi-depot/solve",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully solved Multi-depot TSP!")
            print(f"Total Distance: {result['total_distance']:.2f}")
            print(f"Total Cost: {result['total_cost']:.2f}")
            print(f"Total Time: {result['total_time']:.2f}")
            print(f"\nAgent Assignments:")
            for i, route in enumerate(result['routes']):
                print(f"  Agent {i+1}: {' → '.join(route)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 2: Hierarchical TSP - Dissertation Structure
# ============================================================================

async def example_hierarchical_tsp():
    """
    Example: Optimize dissertation chapter order

    Scenario: PhD dissertation with 3 chapters, each with 2 sections.
    Find optimal reading order considering hierarchy.
    """
    print("\n" + "="*80)
    print("Example 2: Hierarchical TSP for Dissertation Structure")
    print("="*80)

    # Define clusters (chapters with sections)
    clusters = [
        {
            "id": "chapter1",
            "nodes": [
                {"id": "ch1_sec1", "x": 0.0, "y": 0.0, "demand": 1.0, "priority": 2},
                {"id": "ch1_sec2", "x": 1.0, "y": 0.0, "demand": 1.0, "priority": 2},
            ],
            "level": 0,
            "parent_cluster": None
        },
        {
            "id": "chapter2",
            "nodes": [
                {"id": "ch2_sec1", "x": 0.0, "y": 1.0, "demand": 1.0, "priority": 1},
                {"id": "ch2_sec2", "x": 1.0, "y": 1.0, "demand": 1.0, "priority": 1},
            ],
            "level": 0,
            "parent_cluster": None
        },
        {
            "id": "chapter3",
            "nodes": [
                {"id": "ch3_sec1", "x": 0.0, "y": 2.0, "demand": 1.0, "priority": 0},
                {"id": "ch3_sec2", "x": 1.0, "y": 2.0, "demand": 1.0, "priority": 0},
            ],
            "level": 0,
            "parent_cluster": None
        },
    ]

    # Build distance matrix
    distance_matrix = {}
    all_nodes = []
    for cluster in clusters:
        all_nodes.extend(cluster["nodes"])

    for n1 in all_nodes:
        for n2 in all_nodes:
            if n1["id"] != n2["id"]:
                # Semantic distance (lower = more related)
                if n1["id"].split("_")[0] == n2["id"].split("_")[0]:
                    # Same chapter
                    dist = 1.0
                else:
                    # Different chapters
                    dist = 3.0
                distance_matrix[f"{n1['id']}_{n2['id']}"] = dist

    # Request payload
    payload = {
        "clusters": clusters,
        "distance_matrix": distance_matrix,
        "algorithm": "top_down"
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/hierarchical/solve",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully solved Hierarchical TSP!")
            print(f"Total Distance: {result['total_distance']:.2f}")
            print(f"\nOptimal Reading Order:")
            for route in result['routes']:
                print(f"  {' → '.join(route)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 3: Stochastic TSP - Uncertain Task Availability
# ============================================================================

async def example_stochastic_tsp():
    """
    Example: Plan route with uncertain task availability

    Scenario: Service technician with appointments.
    Some customers might cancel (< 100% probability).
    """
    print("\n" + "="*80)
    print("Example 3: Stochastic TSP for Uncertain Scheduling")
    print("="*80)

    # Define appointments
    nodes = [
        {"id": "home", "x": 0.0, "y": 0.0, "demand": 0.0},
        {"id": "client1", "x": 1.0, "y": 0.0, "demand": 1.0},
        {"id": "client2", "x": 2.0, "y": 1.0, "demand": 1.0},
        {"id": "client3", "x": 1.0, "y": 2.0, "demand": 1.0},
        {"id": "client4", "x": 0.0, "y": 1.0, "demand": 1.0},
    ]

    # Presence probabilities (some clients might cancel)
    presence_probabilities = {
        "home": 1.0,      # Always start at home
        "client1": 0.95,  # 95% likely to be there
        "client2": 0.80,  # 80% likely (uncertain)
        "client3": 0.90,  # 90% likely
        "client4": 0.70,  # 70% likely (most uncertain)
    }

    # Build distance matrix
    distance_matrix = {}
    for n1 in nodes:
        for n2 in nodes:
            if n1["id"] != n2["id"]:
                dist = ((n1["x"] - n2["x"])**2 + (n1["y"] - n2["y"])**2)**0.5
                distance_matrix[f"{n1['id']}_{n2['id']}"] = dist

    # Request payload
    payload = {
        "nodes": nodes,
        "presence_probabilities": presence_probabilities,
        "distance_matrix": distance_matrix,
        "start_node_id": "home",
        "algorithm": "expected_value",
        "risk_factor": 0.2
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/stochastic/solve",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully solved Stochastic TSP!")
            print(f"Expected Distance: {result['total_distance']:.2f}")
            print(f"\nOptimal Route (accounting for uncertainty):")
            for route in result['routes']:
                print(f"  {' → '.join(route)}")
            print(f"\nMetadata: {result['metadata']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 4: Route Optimization - 2-opt
# ============================================================================

async def example_2opt_optimization():
    """
    Example: Improve existing route with 2-opt

    Scenario: Have a route, want to optimize it.
    2-opt is fast and typically improves by 15-30%.
    """
    print("\n" + "="*80)
    print("Example 4: 2-opt Route Optimization")
    print("="*80)

    # Initial route (not optimal)
    initial_route = ["city1", "city2", "city4", "city3", "city5", "city1"]

    # Distance matrix
    distance_matrix = {
        "city1_city2": 10.0,
        "city2_city1": 10.0,
        "city1_city3": 15.0,
        "city3_city1": 15.0,
        "city1_city4": 20.0,
        "city4_city1": 20.0,
        "city1_city5": 25.0,
        "city5_city1": 25.0,
        "city2_city3": 12.0,
        "city3_city2": 12.0,
        "city2_city4": 8.0,
        "city4_city2": 8.0,
        "city2_city5": 18.0,
        "city5_city2": 18.0,
        "city3_city4": 14.0,
        "city4_city3": 14.0,
        "city3_city5": 10.0,
        "city5_city3": 10.0,
        "city4_city5": 16.0,
        "city5_city4": 16.0,
    }

    # Request payload
    payload = {
        "route": initial_route,
        "distance_matrix": distance_matrix,
        "algorithm": "2opt",
        "max_iterations": 1000
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/optimize",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully optimized route with 2-opt!")
            print(f"Initial Route: {' → '.join(initial_route)}")
            print(f"Optimized Route: {' → '.join(result['routes'][0])}")
            print(f"Optimized Distance: {result['total_distance']:.2f}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 5: Genetic Algorithm Optimization
# ============================================================================

async def example_genetic_algorithm():
    """
    Example: Optimize route with Genetic Algorithm

    Scenario: Complex route requiring global optimization.
    GA uses population-based search for diverse solutions.
    """
    print("\n" + "="*80)
    print("Example 5: Genetic Algorithm Optimization")
    print("="*80)

    # Initial route
    route = ["node1", "node2", "node3", "node4", "node5", "node6", "node1"]

    # Distance matrix (6-node problem)
    distance_matrix = {}
    nodes = ["node1", "node2", "node3", "node4", "node5", "node6"]

    # Generate distances
    import random
    random.seed(42)
    for i, n1 in enumerate(nodes):
        for j, n2 in enumerate(nodes):
            if i < j:
                dist = random.uniform(10.0, 50.0)
                distance_matrix[f"{n1}_{n2}"] = dist
                distance_matrix[f"{n2}_{n1}"] = dist

    # Request payload
    payload = {
        "route": route,
        "distance_matrix": distance_matrix,
        "algorithm": "genetic",
        "max_iterations": 100
    }

    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/optimize",
            json=payload,
            timeout=60.0
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Successfully optimized with Genetic Algorithm!")
            print(f"Optimized Route: {' → '.join(result['routes'][0])}")
            print(f"Optimized Distance: {result['total_distance']:.2f}")
            print(f"Metadata: {result['metadata']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 6: List Available Algorithms
# ============================================================================

async def example_list_algorithms():
    """List all available TSP algorithms"""
    print("\n" + "="*80)
    print("Example 6: List Available TSP Algorithms")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/algorithms",
            timeout=10.0
        )

        if response.status_code == 200:
            algorithms = response.json()
            print("\n✅ Available Algorithms:")

            for category, info in algorithms.items():
                print(f"\n📂 {info['name']}")
                print(f"   Description: {info['description']}")
                print(f"   Use Case: {info['use_case']}")
                print(f"   Complexity: {info.get('complexity', 'N/A')}")

                if 'algorithms' in info:
                    print(f"   Algorithms: {', '.join(info['algorithms'])}")
        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("TSP API Examples")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")

    try:
        # Run all examples
        await example_list_algorithms()
        await example_multi_depot_tsp()
        await example_hierarchical_tsp()
        await example_stochastic_tsp()
        await example_2opt_optimization()
        await example_genetic_algorithm()

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
