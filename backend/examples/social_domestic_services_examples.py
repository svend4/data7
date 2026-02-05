"""
Social & Domestic Services Simulator Usage Examples

Demonstrates how to use the Social & Domestic Services Simulator API for:
- Legal services scenarios
- Social work case management
- Domestic services and estate management
- Home care and caregiving

Domain: Social & Domestic Services
Maps: MMO Support NPCs → Service Workers
"""

import asyncio
import httpx

# API Base URL
API_BASE_URL = "http://localhost:8000/api/simulator"


# ============================================================================
# Example 1: Legal Services Center
# ============================================================================

async def example_legal_services():
    """
    Create legal services scenario with lawyers and social law specialists
    """
    print("=" * 80)
    print("Example 1: Legal Services Center")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create legal services scenario
        payload = {
            "name": "Community Legal Aid",
            "description": "Legal services center with social law specialists",
            "service_type": "legal",
            "num_workers": 5,
            "num_clients": 20
        }

        response = await client.post(
            f"{API_BASE_URL}/social_services/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()

        print(f"\n✅ Legal Services Scenario Created:")
        print(f"   Scenario ID: {result['scenario_id']}")
        print(f"   Name: {result['name']}")
        print(f"   Workers: {result['num_workers']} (lawyers, specialists)")
        print(f"   Clients: {result['num_clients']}")

        # Simulate office hours
        shift_payload = {
            "scenario_id": result['scenario_id'],
            "shift_type": "office_hours",
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/social_services/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Office Hours Results:")
        print(f"   Clients Served: {shift_result['clients']['served']}")
        print(f"   Success Rate: {shift_result['outcomes']['success_rate']:.1%}")
        print(f"   Client Satisfaction: {shift_result['average_satisfaction']:.2f}/1.00")

        return result['scenario_id']


# ============================================================================
# Example 2: Social Work Services
# ============================================================================

async def example_social_work():
    """
    Social work and case management scenario
    """
    print("\n" + "=" * 80)
    print("Example 2: Social Work Services")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create social work scenario
        payload = {
            "name": "Family Support Services",
            "description": "Social workers providing family support",
            "service_type": "social_work",
            "num_workers": 4,
            "num_clients": 15
        }

        response = await client.post(
            f"{API_BASE_URL}/social_services/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Social Work Scenario Created")
        print(f"   Social Workers: {result['num_workers']}")
        print(f"   Families/Clients: {result['num_clients']}")

        # Simulate shift
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_type": "office_hours",
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/social_services/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Service Results:")
        print(f"   Cases Served: {shift_result['clients']['served']}")
        print(f"   High Need Cases: {shift_result['clients']['high_need']}")
        print(f"   Urgent Cases: {shift_result['clients']['urgent']}")
        print(f"   Satisfaction: {shift_result['average_satisfaction']:.1%}")


# ============================================================================
# Example 3: Estate Management Services
# ============================================================================

async def example_estate_management():
    """
    Domestic services: housekeeping and estate management
    """
    print("\n" + "=" * 80)
    print("Example 3: Estate Management Services")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create domestic services scenario
        payload = {
            "name": "Premium Estate Services",
            "description": "Full-service estate management",
            "service_type": "domestic",
            "num_workers": 6,
            "num_clients": 10
        }

        response = await client.post(
            f"{API_BASE_URL}/social_services/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Estate Management Scenario Created")
        print(f"   Workers: {result['num_workers']} (housekeepers, managers, groundskeepers)")
        print(f"   Properties: {result['num_clients']}")

        # Simulate home visit shift
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_type": "home_visit",
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/social_services/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Service Results:")
        print(f"   Properties Serviced: {shift_result['clients']['served']}")
        print(f"   Success Rate: {shift_result['outcomes']['success_rate']:.1%}")
        print(f"   Tasks Completed: {shift_result['tasks_completed']}")


# ============================================================================
# Example 4: Home Care Services
# ============================================================================

async def example_home_care():
    """
    Home care and caregiving services
    """
    print("\n" + "=" * 80)
    print("Example 4: Home Care Services (Сиделки)")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create home care scenario
        payload = {
            "name": "Elder Care Services",
            "description": "Home care for elderly and disabled clients",
            "service_type": "home_care",
            "num_workers": 8,
            "num_clients": 25
        }

        response = await client.post(
            f"{API_BASE_URL}/social_services/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Home Care Scenario Created")
        print(f"   Caregivers: {result['num_workers']}")
        print(f"   Clients: {result['num_clients']}")

        # Simulate home visit shift
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_type": "home_visit",
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/social_services/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Caregiving Results:")
        print(f"   Clients Cared For: {shift_result['clients']['served']}")
        print(f"   Success Rate: {shift_result['outcomes']['success_rate']:.1%}")
        print(f"   Client Satisfaction: {shift_result['average_satisfaction']:.1%}")

        # Get detailed report
        report_response = await client.get(
            f"{API_BASE_URL}/social_services/report/{scenario_id}",
            timeout=30.0
        )

        report = report_response.json()

        print(f"\n👥 Caregiver Performance:")
        caregivers = [w for w in report['workers'] if 'caregiver' in w['role'] or 'aide' in w['role']]
        for caregiver in caregivers[:3]:  # Show top 3
            print(f"   {caregiver['name']}: {caregiver['clients_served']} clients, "
                  f"{caregiver['successful_services']} successful services")


# ============================================================================
# Example 5: Mixed Services Center
# ============================================================================

async def example_mixed_services():
    """
    Comprehensive service center with all service types
    """
    print("\n" + "=" * 80)
    print("Example 5: Mixed Services Center")
    print("=" * 80)

    async with httpx.AsyncClient() as client:
        # Create mixed services scenario
        payload = {
            "name": "Community Services Hub",
            "description": "Full-service community center",
            "service_type": "mixed",
            "num_workers": 12,
            "num_clients": 40
        }

        response = await client.post(
            f"{API_BASE_URL}/social_services/scenario",
            json=payload,
            timeout=30.0
        )

        result = response.json()
        scenario_id = result['scenario_id']

        print(f"\n✅ Mixed Services Center Created")
        print(f"   Total Workers: {result['num_workers']}")
        print(f"   Total Clients: {result['num_clients']}")

        # Simulate full day
        shift_payload = {
            "scenario_id": scenario_id,
            "shift_type": "office_hours",
            "shift_duration": 8
        }

        shift_response = await client.post(
            f"{API_BASE_URL}/social_services/simulate",
            json=shift_payload,
            timeout=60.0
        )

        shift_result = shift_response.json()

        print(f"\n📊 Daily Operations:")
        print(f"   Clients Served: {shift_result['clients']['served']}")
        print(f"   Success Rate: {shift_result['outcomes']['success_rate']:.1%}")
        print(f"   Escalations: {shift_result['outcomes']['escalations']}")
        print(f"   Overall Satisfaction: {shift_result['average_satisfaction']:.1%}")

        # Get comprehensive report
        report_response = await client.get(
            f"{API_BASE_URL}/social_services/report/{scenario_id}",
            timeout=30.0
        )

        report = report_response.json()

        print(f"\n👥 Workers by Role:")
        roles = {}
        for worker in report['workers']:
            role = worker['role']
            if role not in roles:
                roles[role] = 0
            roles[role] += 1

        for role, count in roles.items():
            print(f"   {role.replace('_', ' ').title()}: {count}")


# ============================================================================
# Main Runner
# ============================================================================

async def run_all_examples():
    """Run all social & domestic services examples"""
    print("\n" + "=" * 80)
    print("SOCIAL & DOMESTIC SERVICES SIMULATOR - USAGE EXAMPLES")
    print("=" * 80)
    print("\nDemonstrates:")
    print("- Legal services (lawyers, social law specialists)")
    print("- Social work and case management")
    print("- Domestic services (housekeepers, estate managers)")
    print("- Home care services (caregivers, home health aides)")
    print("\n" + "=" * 80)

    try:
        # Example 1: Legal services
        await example_legal_services()

        # Example 2: Social work
        await example_social_work()

        # Example 3: Estate management
        await example_estate_management()

        # Example 4: Home care
        await example_home_care()

        # Example 5: Mixed services
        await example_mixed_services()

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
