"""
Healthcare Simulator Usage Examples

Demonstrates how to use the Healthcare Simulator API for:
- Creating healthcare scenarios
- Simulating medical shifts
- Patient diagnosis and treatment
- Monitoring patient outcomes
- Analyzing healthcare worker performance

Domain: Healthcare and Medical
Maps: MMO Healer → Doctor/Nurse
"""

import asyncio
import httpx
from typing import Dict, Any

# API Base URL
API_BASE_URL = "http://localhost:8000/api/simulator"


# ============================================================================
# Example 1: Create General Hospital Scenario
# ============================================================================

async def example_create_general_hospital():
    """
    Create general hospital scenario

    Scenario:
    - 3 doctors
    - 6 nurses
    - 20 patients with various conditions
    - General hospital with multiple specialties
    """
    print("=" * 80)
    print("Example 1: Create General Hospital Scenario")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        payload = {
            "name": "City General Hospital",
            "description": "General hospital with emergency and surgery departments",
            "num_doctors": 3,
            "num_nurses": 6,
            "num_patients": 20,
            "hospital_type": "general"
        }

        response = await client.post(
            f"{API_BASE_URL}/healthcare/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()

        print(f"\n✅ Hospital Scenario Created:")
        print(f"   Scenario ID: {result['scenario_id']}")
        print(f"   Name: {result['name']}")
        print(f"   Healthcare Workers: {result['num_workers']}")
        print(f"   Patients: {result['num_patients']}")
        print(f"   Hospital Type: {result['hospital_type']}")

        return result['scenario_id']


# ============================================================================
# Example 2: Simulate Medical Shift
# ============================================================================

async def example_simulate_shift(scenario_id: str):
    """
    Simulate an 8-hour medical shift

    During shift:
    - Doctors diagnose patients
    - Doctors and nurses treat patients
    - Nurses monitor vital signs
    - Track treatment outcomes
    """
    print("\n" + "=" * 80)
    print("Example 2: Simulate Medical Shift")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,  # First shift (7 AM - 3 PM)
            "shift_duration": 8  # 8 hours
        }

        response = await client.post(
            f"{API_BASE_URL}/healthcare/simulate",
            json=payload,
            timeout=60.0
        )

        result = response.json()

        print(f"\n✅ Shift Simulation Complete:")
        print(f"   Shift Number: {result['shift_number']}")
        print(f"   Duration: {result['duration']} hours")
        print(f"   Healthcare Workers: {result['workers']}")
        print(f"\n👥 Patients:")
        print(f"   Total: {result['patients']['total']}")
        print(f"   Treated: {result['patients']['treated']}")
        print(f"   Critical: {result['patients']['critical']}")
        print(f"   Stable: {result['patients']['stable']}")
        print(f"\n💊 Treatments:")
        print(f"   Successful: {result['treatments']['successful']}")
        print(f"   Complications: {result['treatments']['complications']}")
        print(f"   Success Rate: {result['treatments']['success_rate']:.1%}")
        print(f"\n⭐ Average Quality: {result['average_quality']:.2f}/1.00")
        print(f"   Tasks Completed: {result['tasks_completed']}")


# ============================================================================
# Example 3: Get Performance Report
# ============================================================================

async def example_get_performance_report(scenario_id: str):
    """
    Get comprehensive healthcare performance report

    Report includes:
    - Patient outcomes by condition
    - Healthcare worker performance by role
    - Treatment success rates
    - Equipment status
    """
    print("\n" + "=" * 80)
    print("Example 3: Get Performance Report")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/healthcare/report/{scenario_id}",
            timeout=30.0
        )

        result = response.json()

        print(f"\n✅ Performance Report:")
        print(f"   Scenario: {result['scenario_name']}")
        print(f"   Completion Score: {result['completion_score']:.1%}")
        print(f"   Success Rate: {result['success_rate']:.1%}")

        print(f"\n👥 Patients ({result['patients']['total']}):")
        print(f"   Stable: {result['patients']['stable']}")
        print(f"   Moderate: {result['patients']['moderate']}")
        print(f"   Serious: {result['patients']['serious']}")
        print(f"   Critical: {result['patients']['critical']}")
        print(f"   Diagnosed: {result['patients']['diagnosed']}")
        print(f"   Avg Recovery: {result['patients']['average_recovery']:.1%}")

        print(f"\n👨‍⚕️ Healthcare Workers ({len(result['workers'])}):")

        # Group by role
        roles = {}
        for worker in result['workers']:
            role = worker['role']
            if role not in roles:
                roles[role] = []
            roles[role].append(worker)

        for role, workers in roles.items():
            print(f"\n   {role.title()}: {len(workers)} workers")
            avg_patients = sum(w['patients_treated'] for w in workers) / len(workers)
            avg_success = sum(w['successful_treatments'] for w in workers) / len(workers)
            print(f"      Avg Patients Treated: {avg_patients:.1f}")
            print(f"      Avg Successful Treatments: {avg_success:.1f}")

        print(f"\n⚕️ Equipment:")
        print(f"   Total: {result['equipment']['total']}")
        print(f"   Needs Calibration: {result['equipment']['needs_calibration']}")
        print(f"\n📊 Shifts Completed: {result['shifts_completed']}")


# ============================================================================
# Example 4: Emergency Room Scenario
# ============================================================================

async def example_emergency_room():
    """
    Create emergency room scenario

    High-intensity scenario:
    - Focus on trauma and critical care
    - More doctors and nurses
    - Urgent cases
    """
    print("\n" + "=" * 80)
    print("Example 4: Emergency Room Scenario")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create scenario
        payload = {
            "name": "Emergency Room - Saturday Night",
            "description": "Busy emergency room with trauma cases",
            "num_doctors": 5,
            "num_nurses": 10,
            "num_patients": 30,
            "hospital_type": "emergency"
        }

        response = await client.post(
            f"{API_BASE_URL}/healthcare/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Emergency Room Scenario Created:")
        print(f"   Workers: {result['num_workers']}")
        print(f"   Patients: {result['num_patients']}")

        # Simulate shift
        print(f"\n🔄 Simulating Emergency Shift...")
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/healthcare/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()
        print(f"   Patients Treated: {shift_result['patients']['treated']}")
        print(f"   Critical Cases: {shift_result['patients']['critical']}")
        print(f"   Success Rate: {shift_result['treatments']['success_rate']:.1%}")
        print(f"   Quality Score: {shift_result['average_quality']:.2f}/1.00")

        return scenario_id


# ============================================================================
# Example 5: Multi-Shift Hospital Operations
# ============================================================================

async def example_multi_shift_operations():
    """
    Simulate hospital operations across three 8-hour shifts

    Demonstrates:
    - 24-hour continuous operations
    - Worker performance across shifts
    - Patient outcome tracking
    """
    print("\n" + "=" * 80)
    print("Example 5: Multi-Shift Hospital Operations (24 Hours)")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create scenario
        payload = {
            "name": "24-Hour Hospital Operation",
            "description": "Continuous medical care across three shifts",
            "num_doctors": 6,
            "num_nurses": 12,
            "num_patients": 40,
            "hospital_type": "general"
        }

        response = await client.post(
            f"{API_BASE_URL}/healthcare/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Scenario Created: {result['name']}")
        print(f"   Total Patients: {result['num_patients']}")

        # Simulate all three shifts
        shift_names = ["Morning (7 AM - 3 PM)", "Afternoon (3 PM - 11 PM)", "Night (11 PM - 7 AM)"]
        total_treated = 0
        total_successful = 0

        for shift_num in range(1, 4):
            print(f"\n🔄 Simulating Shift {shift_num}: {shift_names[shift_num - 1]}")

            shift_payload = {
                "scenario_id": scenario_id,
                "shift_number": shift_num,
                "shift_duration": 8
            }

            shift_response = await client.post(
                f"{API_BASE_URL}/healthcare/simulate",
                json=shift_payload,
                timeout=60.0
            )

            shift_result = shift_response.json()
            treated = shift_result['patients']['treated']
            successful = shift_result['treatments']['successful']
            success_rate = shift_result['treatments']['success_rate']
            quality = shift_result['average_quality']

            total_treated += treated
            total_successful += successful

            print(f"   Patients Treated: {treated}")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Quality: {quality:.2f}/1.00")

        print(f"\n📊 24-Hour Summary:")
        print(f"   Total Patients Treated: {total_treated}")
        print(f"   Total Successful Treatments: {total_successful}")
        print(f"   Overall Success Rate: {total_successful / max(1, total_treated):.1%}")


# ============================================================================
# Example 6: Surgical Center
# ============================================================================

async def example_surgical_center():
    """
    Specialized surgical center scenario

    Features:
    - Focus on surgical procedures
    - Specialized doctors
    - High-complexity cases
    """
    print("\n" + "=" * 80)
    print("Example 6: Surgical Center")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create surgical center scenario
        payload = {
            "name": "Advanced Surgical Center",
            "description": "Specialized facility for complex surgeries",
            "num_doctors": 4,
            "num_nurses": 8,
            "num_patients": 15,  # Fewer patients, more complex cases
            "hospital_type": "surgical"
        }

        response = await client.post(
            f"{API_BASE_URL}/healthcare/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Surgical Center Created")
        print(f"   Focus: Complex surgical procedures")

        # Simulate shift
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_number": 1,
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/healthcare/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Surgical Performance:")
        print(f"   Procedures Performed: {shift_result['patients']['treated']}")
        print(f"   Successful: {shift_result['treatments']['successful']}")
        print(f"   Complications: {shift_result['treatments']['complications']}")
        print(f"   Success Rate: {shift_result['treatments']['success_rate']:.1%}")

        # Get detailed report
        report_response = await client.get(
            f"{API_BASE_URL}/healthcare/report/{scenario_id}",
            timeout=30.0
        )

        report = report_response.json()

        # Show doctor performance
        doctors = [w for w in report['workers'] if w['role'] == 'doctor']
        print(f"\n👨‍⚕️ Surgeon Performance ({len(doctors)} doctors):")
        for doctor in doctors:
            success_rate = doctor['successful_treatments'] / max(1, doctor['patients_treated'])
            print(f"   {doctor['name']} ({doctor['specialty']}): {success_rate:.1%} success rate")


# ============================================================================
# Example 7: Compare Hospital Types
# ============================================================================

async def example_compare_hospital_types():
    """
    Compare performance across different hospital types

    Hospital types:
    - General (diverse cases)
    - Emergency (trauma focus)
    - Surgical (complex procedures)
    """
    print("\n" + "=" * 80)
    print("Example 7: Compare Hospital Types")
    print("=" * 80)

    hospital_types = ["general", "emergency", "surgical"]
    results = {}

    async with httpx.AsyncClient() as client:
        for hospital_type in hospital_types:
            print(f"\n🔄 Testing {hospital_type.title()} Hospital...")

            # Create scenario
            payload = {
                "name": f"{hospital_type.title()} Hospital Test",
                "description": f"Performance test for {hospital_type} hospital",
                "num_doctors": 3,
                "num_nurses": 6,
                "num_patients": 20,
                "hospital_type": hospital_type
            }

            response = await client.post(
                f"{API_BASE_URL}/healthcare/scenario",
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
                f"{API_BASE_URL}/healthcare/simulate",
                json=shift_payload,
                timeout=60.0
            )

            shift_result = shift_response.json()

            results[hospital_type] = {
                "treated": shift_result['patients']['treated'],
                "success_rate": shift_result['treatments']['success_rate'],
                "quality": shift_result['average_quality']
            }

            print(f"   Patients Treated: {results[hospital_type]['treated']}")
            print(f"   Success Rate: {results[hospital_type]['success_rate']:.1%}")
            print(f"   Quality: {results[hospital_type]['quality']:.2f}/1.00")

        # Compare results
        print(f"\n📊 Hospital Type Comparison:")
        print(f"\n{'Hospital Type':<20} {'Treated':<10} {'Success Rate':<15} {'Quality':<10}")
        print("=" * 56)
        for hospital_type, metrics in results.items():
            print(f"{hospital_type.title():<20} "
                  f"{metrics['treated']:<10} "
                  f"{metrics['success_rate']:>13.1%}  "
                  f"{metrics['quality']:>8.2f}")


# ============================================================================
# Main Runner
# ============================================================================

async def run_all_examples():
    """Run all healthcare simulator examples"""
    print("\n" + "=" * 80)
    print("HEALTHCARE SIMULATOR - USAGE EXAMPLES")
    print("=" * 80)
    print("\nDemonstrates:")
    print("- Hospital scenario creation")
    print("- Medical shift simulation")
    print("- Patient diagnosis and treatment")
    print("- Multi-shift operations")
    print("- Performance reporting")
    print("\n" + "=" * 80)

    try:
        # Example 1: Basic scenario
        scenario_id = await example_create_general_hospital()

        # Example 2: Simulate shift
        await example_simulate_shift(scenario_id)

        # Example 3: Get report
        await example_get_performance_report(scenario_id)

        # Example 4: Emergency room
        await example_emergency_room()

        # Example 5: Multi-shift operations
        await example_multi_shift_operations()

        # Example 6: Surgical center
        await example_surgical_center()

        # Example 7: Compare hospitals
        await example_compare_hospital_types()

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
