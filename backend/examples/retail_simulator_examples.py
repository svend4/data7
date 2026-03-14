"""
Retail Simulator API Usage Examples

Demonstrates how to use Retail Simulator API endpoints:
- Create retail scenarios
- Simulate customer service operations
- Track sales and satisfaction metrics
- Analyze employee performance

Paradigm 2: Professional Simulator - Retail Domain
Transforms MMO mechanics into retail training.
"""

import asyncio
import httpx
from typing import Dict, List


# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000/api/simulator"


# ============================================================================
# Example 1: Create Retail Scenario
# ============================================================================

async def example_create_retail_scenario():
    """
    Example: Create retail store scenario

    Scenario: Small retail store with 3 employees and 30 customers
    """
    print("\n" + "="*80)
    print("Example 1: Create Retail Scenario")
    print("="*80)

    payload = {
        "name": "Saturday Shopping Rush",
        "description": "Busy Saturday shift at retail store",
        "num_agents": 3,
        "num_customers": 30,
        "num_products": 20,
        "store_type": "retail"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/retail/scenario",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            scenario = response.json()
            print(f"\n✅ Created retail scenario!")
            print(f"\nScenario ID: {scenario['scenario_id']}")
            print(f"Name: {scenario['name']}")
            print(f"Description: {scenario['description']}")
            print(f"\nSetup:")
            print(f"  Service Agents: {scenario['num_agents']}")
            print(f"  Customers: {scenario['num_customers']}")
            print(f"  Products: {scenario['num_products']}")
            print(f"  Store Type: {scenario['store_type']}")
            print(f"  Status: {scenario['status']}")

            print(f"\nObjectives:")
            for obj in scenario['objectives']:
                print(f"  • {obj['description']}")
                if 'target' in obj:
                    if isinstance(obj['target'], float):
                        print(f"    Target: {obj['target']:.0%}")
                    else:
                        print(f"    Target: {obj['target']}")

            return scenario['scenario_id']
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None


# ============================================================================
# Example 2: Simulate Retail Shift
# ============================================================================

async def example_simulate_retail_shift(scenario_id: str):
    """
    Example: Simulate 8-hour retail shift

    Simulates customer service operations and tracks performance.
    """
    print("\n" + "="*80)
    print("Example 2: Simulate Retail Shift")
    print("="*80)

    payload = {
        "scenario_id": scenario_id,
        "shift_duration": 480  # 8 hours
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/retail/simulate",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 200:
            results = response.json()
            print(f"\n✅ Shift simulation completed!")

            print(f"\n📋 Scenario: {results['scenario_name']}")
            print(f"  Completion Score: {results['completion_score']:.2%}")
            print(f"  Total Performance: {results['total_performance']:.2%}")

            print(f"\n📊 Task Results:")
            tasks = results['tasks']
            print(f"  Total: {tasks['total']}")
            print(f"  Completed: {tasks['completed']}")
            print(f"  Failed: {tasks['failed']}")
            print(f"  Pending: {tasks['pending']}")
            if tasks['total'] > 0:
                print(f"  Success Rate: {tasks['completed']/tasks['total']*100:.1f}%")

            print(f"\n👥 Employee Performance:")
            for prof in results['professionals']:
                print(f"\n  {prof['name']} ({prof['role']})")
                print(f"    Level: {prof['level']}")
                print(f"    Customers Served: {prof['tasks_completed']}")
                print(f"    Efficiency: {prof['efficiency']:.2%}")
                print(f"    Quality: {prof['quality']:.2%}")

            print(f"\n💰 Retail Metrics:")
            metrics = results['retail_metrics']
            print(f"  Total Revenue: ${metrics['total_revenue']:.2f}")
            print(f"  Customers Served: {metrics['total_customers_served']}")
            print(f"  Avg Revenue/Customer: ${metrics['avg_revenue_per_customer']:.2f}")
            print(f"  Avg Customer Satisfaction: {metrics['avg_customer_satisfaction']:.2%}")
            print(f"  Products Sold: {metrics['products_sold']}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 3: Get Performance Report
# ============================================================================

async def example_get_retail_report(scenario_id: str):
    """
    Example: Get detailed retail performance report

    Retrieves comprehensive metrics for completed shift.
    """
    print("\n" + "="*80)
    print("Example 3: Get Retail Performance Report")
    print("="*80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/retail/report/{scenario_id}",
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
            if report['tasks']['total'] > 0:
                print(f"  Completion Rate: {report['tasks']['completed']/report['tasks']['total']*100:.1f}%")

            # Customer metrics
            if 'customer_metrics' in report:
                cust = report['customer_metrics']
                print(f"\n😊 Customer Metrics:")
                print(f"  Total Customers: {cust['total_customers']}")
                print(f"  Average Satisfaction: {cust['avg_satisfaction']:.2%}")
                print(f"  Happy Customers: {cust['happy_customers']}")
                print(f"  Unhappy Customers: {cust['unhappy_customers']}")
                satisfaction_rate = cust['happy_customers'] / cust['total_customers'] * 100
                print(f"  Satisfaction Rate: {satisfaction_rate:.1f}%")

            # Product metrics
            if 'product_metrics' in report:
                prod = report['product_metrics']
                print(f"\n📦 Product Metrics:")
                print(f"  Total Products: {prod['total_products']}")
                print(f"  Products Sold: {prod['products_sold']}")
                print(f"  Total Revenue: ${prod['total_revenue']:.2f}")
                print(f"  Best Seller: {prod['best_seller']}")

            # Individual performance
            print(f"\n👥 Individual Performance:")
            professionals = report['professionals']
            professionals.sort(key=lambda p: p['quality'] * p['efficiency'], reverse=True)

            for prof in professionals:
                combined_score = prof['quality'] * prof['efficiency']
                print(f"\n  {prof['name']} - Level {prof['level']}")
                print(f"     Role: {prof['role']}")
                print(f"     Efficiency: {prof['efficiency']:.1%}")
                print(f"     Quality: {prof['quality']:.1%}")
                print(f"     Combined Score: {combined_score:.1%}")
                print(f"     Customers Served: {prof['tasks_completed']}")

            # Top performer
            if professionals:
                top_performer = professionals[0]
                print(f"\n⭐ Top Performer: {top_performer['name']}")
                print(f"   Role: {top_performer['role']}")
                print(f"   Combined Score: {top_performer['quality'] * top_performer['efficiency']:.2%}")

        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 4: Compare Different Store Types
# ============================================================================

async def example_compare_store_types():
    """
    Example: Compare performance across different store types

    Tests: retail, grocery, electronics stores
    """
    print("\n" + "="*80)
    print("Example 4: Compare Different Store Types")
    print("="*80)

    store_types = ["retail", "grocery", "electronics"]
    results_comparison = []

    async with httpx.AsyncClient() as client:
        for store_type in store_types:
            print(f"\n🧪 Testing: {store_type.title()} Store")

            # Create scenario
            create_response = await client.post(
                f"{API_BASE_URL}/retail/scenario",
                json={
                    "name": f"{store_type.title()} Store Test",
                    "description": f"Test {store_type} operations",
                    "num_agents": 3,
                    "num_customers": 30,
                    "num_products": 20,
                    "store_type": store_type
                },
                timeout=30.0
            )

            if create_response.status_code == 200:
                scenario = create_response.json()
                scenario_id = scenario['scenario_id']

                # Simulate shift
                simulate_response = await client.post(
                    f"{API_BASE_URL}/retail/simulate",
                    json={
                        "scenario_id": scenario_id,
                        "shift_duration": 480
                    },
                    timeout=30.0
                )

                if simulate_response.status_code == 200:
                    simulation = simulate_response.json()
                    metrics = simulation['retail_metrics']

                    results_comparison.append({
                        "store_type": store_type,
                        "revenue": metrics['total_revenue'],
                        "customers": metrics['total_customers_served'],
                        "satisfaction": metrics['avg_customer_satisfaction'],
                        "products_sold": metrics['products_sold']
                    })

    # Print comparison
    print("\n" + "="*80)
    print("Store Type Comparison Results")
    print("="*80)

    print(f"\n{'Store Type':<15} {'Revenue':<12} {'Customers':<12} {'Satisfaction':<15} {'Products':<10}")
    print("-" * 80)

    for result in results_comparison:
        print(
            f"{result['store_type']:<15} "
            f"${result['revenue']:<11.2f} "
            f"{result['customers']:<12} "
            f"{result['satisfaction']:<15.1%} "
            f"{result['products_sold']:<10}"
        )

    # Find best performer
    best_revenue = max(results_comparison, key=lambda r: r['revenue'])
    best_satisfaction = max(results_comparison, key=lambda r: r['satisfaction'])

    print(f"\n🏆 Highest Revenue: {best_revenue['store_type'].title()} (${best_revenue['revenue']:.2f})")
    print(f"😊 Highest Satisfaction: {best_satisfaction['store_type'].title()} ({best_satisfaction['satisfaction']:.1%})")


# ============================================================================
# Example 5: List Available Domains
# ============================================================================

async def example_list_domains():
    """List all available simulator domains"""
    print("\n" + "="*80)
    print("Example 5: Available Simulator Domains")
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

            # Show progress
            operational = sum(1 for d in domains if d['status'] == 'operational')
            total = len(domains)
            print(f"\n📊 Paradigm 2 Progress:")
            print(f"   Operational Domains: {operational}/{total}")
            print(f"   Overall: {operational/total*100:.0f}%")

        else:
            print(f"❌ Error: {response.status_code}")


# ============================================================================
# Example 6: Simulator Information
# ============================================================================

async def example_simulator_info():
    """Get professional simulator information"""
    print("\n" + "="*80)
    print("Example 6: Professional Simulator Information")
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
    print("Retail Simulator API Examples")
    print("Paradigm 2: Professional Training Simulation - Retail Domain")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")

    try:
        # Example 1: Get simulator info
        await example_simulator_info()

        # Example 2: List domains
        await example_list_domains()

        # Example 3: Create retail scenario
        scenario_id = await example_create_retail_scenario()

        if scenario_id:
            # Example 4: Simulate shift
            await example_simulate_retail_shift(scenario_id)

            # Example 5: Get performance report
            await example_get_retail_report(scenario_id)

        # Example 6: Compare store types
        await example_compare_store_types()

        print("\n" + "="*80)
        print("✅ All examples completed!")
        print("="*80)

        print("\n📚 What you learned:")
        print("  1. How to create retail service scenarios")
        print("  2. How to simulate customer service operations")
        print("  3. How to track sales and satisfaction metrics")
        print("  4. How MMO mechanics map to retail training")
        print("  5. How to compare different store configurations")

        print("\n🎮 MMO → Retail Mappings Used:")
        print("  • Service Agent → MMO Bard (persuasion, communication)")
        print("  • Sales Person → MMO Merchant (trading)")
        print("  • Cashier → MMO Crafter (fast processing)")
        print("  • Customer → MMO NPC (quest giver)")
        print("  • Product → MMO Item/Loot")
        print("  • Store → MMO Shop/Market")
        print("  • Shift → MMO Quest Chain")

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
