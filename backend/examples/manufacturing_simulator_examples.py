"""
Manufacturing Simulator Usage Examples

Demonstrates how to use the Manufacturing Simulator API for:
- Creating manufacturing scenarios
- Simulating production shifts
- Tracking quality control
- Managing machine maintenance
- Analyzing worker performance

Domain: Manufacturing and Production
Maps: MMO Crafter → Assembly Line Worker
"""

import asyncio
import httpx
from typing import Dict, Any

# API Base URL
API_BASE_URL = "http://localhost:8000/api/simulator"


# ============================================================================
# Example 1: Create Electronics Manufacturing Scenario
# ============================================================================

async def example_create_electronics_scenario():
    """
    Create electronics manufacturing scenario

    Scenario:
    - 10 workers across 3 shifts
    - 5 assembly machines
    - Target: 500 units
    - Focus: Circuit board assembly
    """
    print("=" * 80)
    print("Example 1: Create Electronics Manufacturing Scenario")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        payload = {
            "name": "Circuit Board Assembly",
            "description": "Electronics manufacturing plant producing circuit boards",
            "num_workers": 10,
            "num_machines": 5,
            "production_target": 500,
            "factory_type": "electronics"
        }

        response = await client.post(
            f"{API_BASE_URL}/manufacturing/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()

        print(f"\n✅ Scenario Created:")
        print(f"   Scenario ID: {result['scenario_id']}")
        print(f"   Name: {result['name']}")
        print(f"   Workers: {result['num_workers']}")
        print(f"   Machines: {result['num_machines']}")
        print(f"   Production Target: {result['production_target']} units")
        print(f"   Factory Type: {result['factory_type']}")

        return result['scenario_id']


# ============================================================================
# Example 2: Simulate Production Shift
# ============================================================================

async def example_simulate_shift(scenario_id: str):
    """
    Simulate an 8-hour production shift

    During shift:
    - Workers produce units on machines
    - Quality inspectors check products
    - Maintenance techs service machines
    - Track defects and efficiency
    """
    print("\n" + "=" * 80)
    print("Example 2: Simulate Production Shift")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,  # First shift (6 AM - 2 PM)
            "shift_duration": 8  # 8 hours
        }

        response = await client.post(
            f"{API_BASE_URL}/manufacturing/simulate",
            json=payload,
            timeout=60.0
        )

        result = response.json()

        print(f"\n✅ Shift Simulation Complete:")
        print(f"   Shift Number: {result['shift_number']}")
        print(f"   Duration: {result['duration']} hours")
        print(f"   Workers: {result['workers']}")
        print(f"\n📊 Tasks:")
        print(f"   Total: {result['tasks']['total']}")
        print(f"   Completed: {result['tasks']['completed']}")
        print(f"   In Progress: {result['tasks']['in_progress']}")
        print(f"\n🏭 Production:")
        print(f"   Total Units: {result['production']['total_units']}")
        print(f"   Passed QC: {result['production']['passed_units']}")
        print(f"   Failed QC: {result['production']['failed_units']}")
        print(f"   Quality Rate: {result['production']['quality_rate']:.1%}")
        print(f"\n⚙️ Efficiency: {result['efficiency']:.1%}")
        print(f"   Machines Operational: {result['machines_operational']}")
        print(f"   Machines Need Maintenance: {result['machines_needing_maintenance']}")


# ============================================================================
# Example 3: Get Performance Report
# ============================================================================

async def example_get_performance_report(scenario_id: str):
    """
    Get comprehensive manufacturing performance report

    Report includes:
    - Overall production metrics
    - Worker performance by role
    - Machine status
    - Quality rates
    """
    print("\n" + "=" * 80)
    print("Example 3: Get Performance Report")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/manufacturing/report/{scenario_id}",
            timeout=30.0
        )

        result = response.json()

        print(f"\n✅ Performance Report:")
        print(f"   Scenario: {result['scenario_name']}")
        print(f"   Completion Score: {result['completion_score']:.1%}")
        print(f"\n🏭 Production:")
        print(f"   Total Units: {result['production']['total_units']}")
        print(f"   Passed QC: {result['production']['passed_units']}")
        print(f"   Failed QC: {result['production']['failed_units']}")
        print(f"   Target: {result['production']['target_units']}")
        print(f"   Quality Rate: {result['production']['quality_rate']:.1%}")

        print(f"\n👷 Workers ({len(result['workers'])}):")

        # Group by role
        roles = {}
        for worker in result['workers']:
            role = worker['role']
            if role not in roles:
                roles[role] = []
            roles[role].append(worker)

        for role, workers in roles.items():
            print(f"\n   {role.replace('_', ' ').title()}: {len(workers)} workers")
            avg_units = sum(w['units_produced'] for w in workers) / len(workers)
            avg_level = sum(w['level'] for w in workers) / len(workers)
            print(f"      Avg Units Produced: {avg_units:.1f}")
            print(f"      Avg Level: {avg_level:.1f}")

        print(f"\n⚙️ Machines:")
        print(f"   Total: {result['machines']['total']}")
        print(f"   Operational: {result['machines']['operational']}")
        print(f"   Need Maintenance: {result['machines']['needing_maintenance']}")
        print(f"\n📊 Shifts Completed: {result['shifts_completed']}")


# ============================================================================
# Example 4: Automotive Manufacturing Scenario
# ============================================================================

async def example_automotive_manufacturing():
    """
    Create automotive parts manufacturing scenario

    Large-scale production:
    - 20 workers
    - 10 machines
    - High volume target (1000 units)
    """
    print("\n" + "=" * 80)
    print("Example 4: Automotive Manufacturing Scenario")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create scenario
        payload = {
            "name": "Automotive Parts Production",
            "description": "High-volume automotive components manufacturing",
            "num_workers": 20,
            "num_machines": 10,
            "production_target": 1000,
            "factory_type": "automotive"
        }

        response = await client.post(
            f"{API_BASE_URL}/manufacturing/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Automotive Scenario Created:")
        print(f"   Workers: {result['num_workers']}")
        print(f"   Machines: {result['num_machines']}")
        print(f"   Target: {result['production_target']} units")

        # Simulate first shift
        print(f"\n🔄 Simulating Shift 1 (6 AM - 2 PM)...")
        shift1_payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,
            "shift_duration": 8
        }

        shift1_response = await client.post(
            f"{API_BASE_URL}/manufacturing/simulate",
            json=shift1_payload,
            timeout=60.0
        )

        shift1_result = shift1_response.json()
        print(f"   Units Produced: {shift1_result['production']['total_units']}")
        print(f"   Quality Rate: {shift1_result['production']['quality_rate']:.1%}")
        print(f"   Efficiency: {shift1_result['efficiency']:.1%}")

        return scenario_id


# ============================================================================
# Example 5: Multi-Shift Production
# ============================================================================

async def example_multi_shift_production():
    """
    Simulate production across three 8-hour shifts

    Demonstrates:
    - 24-hour continuous production
    - Worker performance across shifts
    - Cumulative production metrics
    """
    print("\n" + "=" * 80)
    print("Example 5: Multi-Shift Production (24 Hours)")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create scenario
        payload = {
            "name": "24-Hour Manufacturing Operation",
            "description": "Continuous production across three shifts",
            "num_workers": 15,
            "num_machines": 6,
            "production_target": 600,
            "factory_type": "electronics"
        }

        response = await client.post(
            f"{API_BASE_URL}/manufacturing/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Scenario Created: {result['name']}")
        print(f"   Production Target: {result['production_target']} units")

        # Simulate all three shifts
        shift_names = ["Morning (6 AM - 2 PM)", "Afternoon (2 PM - 10 PM)", "Night (10 PM - 6 AM)"]
        total_units = 0
        total_passed = 0

        for shift_num in range(1, 4):
            print(f"\n🔄 Simulating Shift {shift_num}: {shift_names[shift_num - 1]}")

            shift_payload = {
                "scenario_id": scenario_id,
                "shift_number": shift_num,
                "shift_duration": 8
            }

            shift_response = await client.post(
                f"{API_BASE_URL}/manufacturing/simulate",
                json=shift_payload,
                timeout=60.0
            )

            shift_result = shift_response.json()
            units = shift_result['production']['total_units']
            passed = shift_result['production']['passed_units']
            quality = shift_result['production']['quality_rate']
            efficiency = shift_result['efficiency']

            total_units += units
            total_passed += passed

            print(f"   Units Produced: {units}")
            print(f"   Quality Rate: {quality:.1%}")
            print(f"   Efficiency: {efficiency:.1%}")

        print(f"\n📊 24-Hour Summary:")
        print(f"   Total Units Produced: {total_units}")
        print(f"   Total Passed QC: {total_passed}")
        print(f"   Overall Quality Rate: {total_passed / total_units:.1%}")
        print(f"   Target Achievement: {total_units / result['production_target']:.1%}")


# ============================================================================
# Example 6: Quality-Focused Manufacturing
# ============================================================================

async def example_quality_focused_manufacturing():
    """
    Scenario emphasizing quality over quantity

    Features:
    - More quality inspectors
    - Stricter quality standards
    - Focus on defect reduction
    """
    print("\n" + "=" * 80)
    print("Example 6: Quality-Focused Manufacturing")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create scenario with emphasis on quality
        payload = {
            "name": "Premium Quality Production",
            "description": "High-quality manufacturing with strict QC",
            "num_workers": 12,
            "num_machines": 4,
            "production_target": 300,  # Lower target, higher quality
            "factory_type": "electronics"
        }

        response = await client.post(
            f"{API_BASE_URL}/manufacturing/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Quality-Focused Scenario Created")
        print(f"   Target: {result['production_target']} units (premium quality)")

        # Simulate production
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/manufacturing/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Quality Metrics:")
        print(f"   Units Produced: {shift_result['production']['total_units']}")
        print(f"   Passed QC: {shift_result['production']['passed_units']}")
        print(f"   Failed QC: {shift_result['production']['failed_units']}")
        print(f"   Quality Rate: {shift_result['production']['quality_rate']:.1%}")

        # Get detailed report
        report_response = await client.get(
            f"{API_BASE_URL}/manufacturing/report/{scenario_id}",
            timeout=30.0
        )

        report = report_response.json()

        # Show inspector performance
        inspectors = [w for w in report['workers'] if w['role'] == 'quality_inspector']
        print(f"\n👁️ Quality Inspectors ({len(inspectors)}):")
        for inspector in inspectors:
            print(f"   {inspector['name']}: {inspector['defects_found']} defects found")


# ============================================================================
# Example 7: Compare Factory Types
# ============================================================================

async def example_compare_factory_types():
    """
    Compare performance across different factory types

    Factory types:
    - Electronics (precision assembly)
    - Automotive (heavy manufacturing)
    - Consumer goods (high volume)
    """
    print("\n" + "=" * 80)
    print("Example 7: Compare Factory Types")
    print("=" * 80)

    factory_types = ["electronics", "automotive", "consumer_goods"]
    results = {}

    async with httpx.AsyncClient() as client:
        for factory_type in factory_types:
            print(f"\n🔄 Testing {factory_type.replace('_', ' ').title()} Factory...")

            # Create scenario
            payload = {
                "name": f"{factory_type.title()} Manufacturing",
                "description": f"Production test for {factory_type}",
                "num_workers": 10,
                "num_machines": 5,
                "production_target": 400,
                "factory_type": factory_type
            }

            response = await client.post(
                f"{API_BASE_URL}/manufacturing/scenario",
                json=payload,
                timeout=30.0
            )

            result = response.json()
            scenario_id = result['scenario_id']

            # Simulate shift
            shift_payload = {
                "scenario_id": scenario_id,
                "shift_number": 1,
                "shift_duration": 8
            }

            shift_response = await client.post(
                f"{API_BASE_URL}/manufacturing/simulate",
                json=shift_payload,
                timeout=60.0
            )

            shift_result = shift_response.json()

            results[factory_type] = {
                "units": shift_result['production']['total_units'],
                "quality": shift_result['production']['quality_rate'],
                "efficiency": shift_result['efficiency']
            }

            print(f"   Units: {results[factory_type]['units']}")
            print(f"   Quality: {results[factory_type]['quality']:.1%}")
            print(f"   Efficiency: {results[factory_type]['efficiency']:.1%}")

        # Compare results
        print(f"\n📊 Factory Type Comparison:")
        print(f"\n{'Factory Type':<20} {'Units':<10} {'Quality':<12} {'Efficiency':<12}")
        print("=" * 56)
        for factory_type, metrics in results.items():
            print(f"{factory_type.replace('_', ' ').title():<20} "
                  f"{metrics['units']:<10} "
                  f"{metrics['quality']:>10.1%}  "
                  f"{metrics['efficiency']:>10.1%}")


# ============================================================================
# Main Runner
# ============================================================================

async def run_all_examples():
    """Run all manufacturing simulator examples"""
    print("\n" + "=" * 80)
    print("MANUFACTURING SIMULATOR - USAGE EXAMPLES")
    print("=" * 80)
    print("\nDemonstrates:")
    print("- Factory scenario creation")
    print("- Production shift simulation")
    print("- Quality control tracking")
    print("- Multi-shift operations")
    print("- Performance reporting")
    print("\n" + "=" * 80)

    try:
        # Example 1: Basic scenario
        scenario_id = await example_create_electronics_scenario()

        # Example 2: Simulate shift
        await example_simulate_shift(scenario_id)

        # Example 3: Get report
        await example_get_performance_report(scenario_id)

        # Example 4: Automotive manufacturing
        await example_automotive_manufacturing()

        # Example 5: Multi-shift production
        await example_multi_shift_production()

        # Example 6: Quality-focused
        await example_quality_focused_manufacturing()

        # Example 7: Compare factories
        await example_compare_factory_types()

        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server")
        print("   Please ensure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_all_examples())
