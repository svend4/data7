"""
Professional Simulator API Usage Examples

Demonstrates how to use Professional Simulator API endpoints:
- Create logistics scenarios
- Optimize routes with TSP
- Simulate delivery operations
- Track performance metrics

Paradigm 2: Professional Simulator
Transforms MMO mechanics into professional training.
"""

import asyncio
import httpx
from typing import Dict, List


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/simulator"


# ============================================================================
# Example 1: List Available Domains
# ============================================================================

async def example_list_domains():
    """
    Example: List all available professional simulator domains

    Shows which domains are operational and their completion status.
    """
    print("\n" + "="*80)
    print("Example 1: List Available Domains")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/domains",
            timeout=10.0
        )

        if response.status_code == 200:
            domains = response.json()
            print("\n✅ Available Domains:")

            for domain in domains:
                status_icon = "✅" if domain["status"] == "operational" else "⏳"
                print(f"\n{status_icon} {domain['name']} ({domain['id']})")
                print(f"   Status: {domain['status']}")
                print(f"   Completion: {domain['completion_percentage']}%")
                print(f"   Description: {domain['description']}")
        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Example 2: Create Logistics Scenario
# ============================================================================

async def example_create_logistics_scenario():
    """
    Example: Create logistics scenario with drivers and deliveries

    Scenario: Small delivery company with 3 drivers and 15 deliveries
    """
    print("\n" + "="*80)
    print("Example 2: Create Logistics Scenario")
    print("="*80)

    payload = {
        "name": "Monday Morning Deliveries",
        "description": "Regular Monday delivery route for city zone A",
        "num_drivers": 3,
        "num_deliveries": 15
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/logistics/scenario",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            scenario = response.json()
            print(f"\n✅ Created logistics scenario!")
            print(f"\nScenario ID: {scenario['scenario_id']}")
            print(f"Name: {scenario['name']}")
            print(f"Description: {scenario['description']}")
            print(f"\nSetup:")
            print(f"  Drivers: {scenario['num_drivers']}")
            print(f"  Deliveries: {scenario['num_deliveries']}")
            print(f"  Warehouses: {scenario['num_warehouses']}")
            print(f"  Status: {scenario['status']}")

            print(f"\nObjectives:")
            for obj in scenario['objectives']:
                print(f"  • {obj['description']}")
                if 'target' in obj:
                    print(f"    Target: {obj['target']}")

            return scenario['scenario_id']
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None


# ============================================================================
# Example 3: Optimize Routes with TSP
# ============================================================================

async def example_optimize_routes(scenario_id: str):
    """
    Example: Optimize delivery routes using Multi-depot TSP

    Uses existing TSP algorithms to find optimal routes for all drivers.
    """
    print("\n" + "="*80)
    print("Example 3: Optimize Routes with TSP")
    print("="*80)

    payload = {
        "scenario_id": scenario_id,
        "algorithm": "cluster_first_route_second"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/logistics/optimize",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            optimization = response.json()
            print(f"\n✅ Successfully optimized routes!")

            print(f"\n📊 Summary:")
            print(f"  Total Routes: {optimization['total_routes']}")
            print(f"  Total Distance: {optimization['total_distance']:.2f} km")
            print(f"  Total Time: {optimization['total_time']:.2f} minutes")
            print(f"  Max Route Time: {optimization['max_time']:.2f} minutes")
            print(f"  Avg Route Load: {optimization['avg_route_load']:.2f} deliveries")
            print(f"  Load Variance: {optimization['load_variance']:.2f}")

            print(f"\n🚚 Optimized Routes:")
            for route in optimization['routes']:
                print(f"\n  Route: {route['id']}")
                print(f"    Driver: {route['driver_name']}")
                print(f"    Deliveries: {route['num_deliveries']}")
                print(f"    Distance: {route['total_distance']:.2f} km")
                print(f"    Estimated Time: {route['estimated_time']:.2f} minutes")
                print(f"    Status: {route['status']}")

            # Show suggestions if any
            if optimization['suggestions']:
                print(f"\n💡 Optimization Suggestions:")
                for suggestion in optimization['suggestions']:
                    print(f"\n  ⚠️  {suggestion['type']}:")
                    print(f"     {suggestion['message']}")
                    if 'details' in suggestion:
                        for key, value in suggestion['details'].items():
                            print(f"       {key}: {value}")
            else:
                print(f"\n✅ No optimization issues detected - routes are well balanced!")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 4: Simulate Full Delivery Day
# ============================================================================

async def example_simulate_delivery_day(scenario_id: str):
    """
    Example: Simulate complete delivery day

    Simulates execution of all routes and tracks performance.
    """
    print("\n" + "="*80)
    print("Example 4: Simulate Full Delivery Day")
    print("="*80)

    payload = {
        "scenario_id": scenario_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/logistics/simulate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            results = response.json()
            print(f"\n✅ Simulation completed!")

            print(f"\n📋 Scenario: {results['scenario_name']}")
            print(f"  Completion Score: {results['completion_score']:.2%}")
            print(f"  Total Performance: {results['total_performance']:.2%}")

            print(f"\n📊 Task Results:")
            tasks = results['tasks']
            print(f"  Total: {tasks['total']}")
            print(f"  Completed: {tasks['completed']}")
            print(f"  Failed: {tasks['failed']}")
            print(f"  Pending: {tasks['pending']}")
            print(f"  Success Rate: {tasks['completed']/tasks['total']*100:.1f}%")

            print(f"\n👥 Driver Performance:")
            for prof in results['professionals']:
                print(f"\n  {prof['name']} ({prof['role']})")
                print(f"    Level: {prof['level']}")
                print(f"    Deliveries Completed: {prof['tasks_completed']}")
                print(f"    Efficiency: {prof['efficiency']:.2%}")
                print(f"    Quality: {prof['quality']:.2%}")

            print(f"\n🚚 Logistics Metrics:")
            metrics = results['logistics_metrics']
            print(f"  Total Distance Traveled: {metrics['total_distance_traveled']:.2f} km")
            print(f"  Avg Distance per Route: {metrics['avg_distance_per_route']:.2f} km")
            print(f"  Total Deliveries: {metrics['total_deliveries']}")
            print(f"  Avg Deliveries per Driver: {metrics['avg_deliveries_per_driver']:.2f}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 5: Get Performance Report
# ============================================================================

async def example_get_performance_report(scenario_id: str):
    """
    Example: Get detailed performance report

    Retrieves comprehensive performance metrics for completed scenario.
    """
    print("\n" + "="*80)
    print("Example 5: Get Performance Report")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/logistics/report/{scenario_id}",
            timeout=10.0
        )

        if response.status_code == 200:
            report = response.json()
            print(f"\n✅ Performance Report Retrieved!")

            print(f"\n📄 Report for: {report['scenario_name']}")
            print(f"  Scenario ID: {report['scenario_id']}")
            print(f"  Overall Score: {report['completion_score']:.2%}")

            print(f"\n🎯 Performance Breakdown:")
            print(f"  Tasks Completed: {report['tasks']['completed']}/{report['tasks']['total']}")
            print(f"  Tasks Failed: {report['tasks']['failed']}")
            print(f"  Completion Rate: {report['tasks']['completed']/report['tasks']['total']*100:.1f}%")

            print(f"\n👥 Individual Performance:")
            professionals = report['professionals']

            # Sort by level
            professionals.sort(key=lambda p: p['level'], reverse=True)

            for prof in professionals:
                print(f"\n  🏆 {prof['name']} - Level {prof['level']}")
                print(f"     Role: {prof['role']}")
                print(f"     Efficiency: {prof['efficiency']:.1%}")
                print(f"     Quality: {prof['quality']:.1%}")
                print(f"     Tasks Completed: {prof['tasks_completed']}")

            # Identify top performer
            top_performer = max(professionals, key=lambda p: p['quality'] * p['efficiency'])
            print(f"\n⭐ Top Performer: {top_performer['name']}")
            print(f"   Combined Score: {top_performer['quality'] * top_performer['efficiency']:.2%}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 6: Compare Different Scenarios
# ============================================================================

async def example_compare_scenarios():
    """
    Example: Compare different scenario configurations

    Tests how different numbers of drivers affect performance.
    """
    print("\n" + "="*80)
    print("Example 6: Compare Different Scenarios")
    print("="*80)

    scenarios_to_test = [
        {"name": "2 Drivers", "num_drivers": 2, "num_deliveries": 20},
        {"name": "3 Drivers", "num_drivers": 3, "num_deliveries": 20},
        {"name": "4 Drivers", "num_drivers": 4, "num_deliveries": 20},
    ]

    results_comparison = []

    async with httpx.AsyncClient() as client:
        for config in scenarios_to_test:
            print(f"\n🧪 Testing: {config['name']}")

            # Create scenario
            create_response = await client.post(
                f"{API_BASE_URL}/logistics/scenario",
                json={
                    "name": config['name'],
                    "description": f"Test with {config['num_drivers']} drivers",
                    "num_drivers": config['num_drivers'],
                    "num_deliveries": config['num_deliveries']
                },
                timeout=30.0
            )

            if create_response.status_code == 200:
                scenario = create_response.json()
                scenario_id = scenario['scenario_id']

                # Optimize
                optimize_response = await client.post(
                    f"{API_BASE_URL}/logistics/optimize",
                    json={"scenario_id": scenario_id},
                    timeout=30.0
                )

                if optimize_response.status_code == 200:
                    optimization = optimize_response.json()

                    results_comparison.append({
                        "config": config['name'],
                        "num_drivers": config['num_drivers'],
                        "total_distance": optimization['total_distance'],
                        "total_time": optimization['total_time'],
                        "max_time": optimization['max_time'],
                        "load_variance": optimization['load_variance']
                    })

    # Print comparison
    print("\n" + "="*80)
    print("Scenario Comparison Results")
    print("="*80)

    print(f"\n{'Config':<15} {'Drivers':<10} {'Distance':<12} {'Total Time':<15} {'Max Time':<12} {'Balance':<10}")
    print("-" * 80)

    for result in results_comparison:
        print(
            f"{result['config']:<15} "
            f"{result['num_drivers']:<10} "
            f"{result['total_distance']:<12.2f} "
            f"{result['total_time']:<15.2f} "
            f"{result['max_time']:<12.2f} "
            f"{result['load_variance']:<10.2f}"
        )

    # Find best configuration
    best_config = min(results_comparison, key=lambda r: r['max_time'])
    print(f"\n🏆 Best Configuration: {best_config['config']}")
    print(f"   Reason: Lowest max route time ({best_config['max_time']:.2f} minutes)")


# ============================================================================
# Example 7: Simulator Information
# ============================================================================

async def example_simulator_info():
    """
    Example: Get general simulator information

    Shows capabilities and mappings between MMO and professional domains.
    """
    print("\n" + "="*80)
    print("Example 7: Professional Simulator Information")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/",
            timeout=10.0
        )

        if response.status_code == 200:
            info = response.json()
            print(f"\n✅ {info['name']}")
            print(f"Version: {info['version']}")
            print(f"Paradigm: {info['paradigm']}")
            print(f"\n{info['description']}")

            print(f"\n🎮 MMO → Professional Mappings:")
            for mmo, prof in info['mappings'].items():
                print(f"  {mmo.replace('_', ' ').title():<20} → {prof}")

            print(f"\n🎯 Use Cases:")
            for use_case in info['use_cases']:
                print(f"  • {use_case}")

            print(f"\n🔧 Domains:")
            for domain_name, domain_info in info['domains'].items():
                status_icon = "✅" if domain_info["status"] == "operational" else "⏳"
                print(f"\n  {status_icon} {domain_name.upper()}")
                print(f"     Status: {domain_info['status']}")
                print(f"     Completion: {domain_info['completion']}")

                if 'features' in domain_info:
                    print(f"     Features:")
                    for feature in domain_info['features']:
                        print(f"       - {feature}")

        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Main - Complete Workflow
# ============================================================================

async def main():
    """Run all examples - Complete workflow"""
    print("\n" + "="*80)
    print("Professional Simulator API Examples")
    print("Paradigm 2: Professional Training Simulation")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")

    try:
        # Example 1: Get simulator info
        await example_simulator_info()

        # Example 2: List domains
        await example_list_domains()

        # Example 3: Create logistics scenario
        scenario_id = await example_create_logistics_scenario()

        if scenario_id:
            # Example 4: Optimize routes
            await example_optimize_routes(scenario_id)

            # Example 5: Simulate delivery day
            await example_simulate_delivery_day(scenario_id)

            # Example 6: Get performance report
            await example_get_performance_report(scenario_id)

        # Example 7: Compare scenarios
        await example_compare_scenarios()

        print("\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80)

        print("\n📚 What you learned:")
        print("  1. How to create professional simulation scenarios")
        print("  2. How TSP algorithms optimize real-world routes")
        print("  3. How to simulate and track performance")
        print("  4. How MMO mechanics map to professional training")
        print("  5. How to compare different configurations")

        print("\n🎮 MMO → Professional Mappings Used:")
        print("  • Delivery Driver → MMO Rogue (fast, mobile)")
        print("  • Warehouse → MMO City (quest hub)")
        print("  • Delivery Task → MMO Fetch Quest")
        print("  • Vehicle → MMO Mount")
        print("  • Route → MMO Quest Chain")
        print("  • Performance XP → MMO Experience Points")

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
