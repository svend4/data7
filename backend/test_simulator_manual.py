"""
Manual test runner for Professional Simulator
Runs basic tests without pytest to verify functionality
"""

import sys
from app.simulators.base import (
    ProfessionalSimulator,
    SimulationScenario,
    ProfessionalRole,
    Task,
    TaskType,
    Location,
    Resource,
    ResourceType,
    PerformanceMetrics,
    TaskStatus
)
from app.simulators.logistics_simulator import (
    LogisticsSimulator,
    DeliveryDriver,
    DeliveryTask,
    Warehouse,
    Vehicle,
    Route
)
from app.simulators.retail_simulator import (
    RetailSimulator,
    ServiceAgent,
    ServiceTask,
    Customer,
    Product,
    Store,
    Shift,
    CustomerMood,
    ServiceType
)

def test_base_framework():
    """Test base framework classes"""
    print("Testing base framework...")

    # Test Location
    location = Location(
        id="loc_001",
        name="Test Location",
        location_type="test",
        coordinates=(0.0, 0.0)
    )
    assert location.id == "loc_001"
    assert location.name == "Test Location"
    print("  ✓ Location works")

    # Test Resource
    resource = Resource(
        id="res_001",
        name="Test Resource",
        resource_type=ResourceType.TOOL
    )
    assert resource.id == "res_001"
    print("  ✓ Resource works")

    # Test Task
    task = Task(
        id="task_001",
        name="Test Task",
        description="Test task description",
        task_type=TaskType.SERVICE,
        location=location,
        priority=1
    )
    assert task.id == "task_001"
    assert task.status == TaskStatus.PENDING
    task.complete()
    assert task.status == TaskStatus.COMPLETED
    print("  ✓ Task works")

    # Test PerformanceMetrics
    metrics = PerformanceMetrics()
    initial_xp = metrics.experience_points
    metrics.experience_points += 150.0
    assert metrics.experience_points > initial_xp
    print("  ✓ PerformanceMetrics works")

    # Test ProfessionalSimulator
    simulator = ProfessionalSimulator(domain="test")
    assert simulator.domain == "test"
    assert simulator.scenarios == {}
    print("  ✓ ProfessionalSimulator works")

    print("✅ Base framework tests passed!\n")

def test_logistics_simulator():
    """Test logistics simulator"""
    print("Testing logistics simulator...")

    # Test Vehicle
    vehicle = Vehicle(
        id="vehicle_001",
        name="Delivery Van",
        speed=60.0,
        cargo_capacity=100.0
    )
    assert vehicle.id == "vehicle_001"
    assert vehicle.speed == 60.0
    print("  ✓ Vehicle works")

    # Test Warehouse
    warehouse = Warehouse(
        id="warehouse_001",
        name="Main DC",
        coordinates=(0.0, 0.0),
        capacity=1000
    )
    assert warehouse.id == "warehouse_001"
    assert warehouse.location_type == "warehouse"
    print("  ✓ Warehouse works")

    # Test LogisticsSimulator
    simulator = LogisticsSimulator()
    scenario = simulator.create_logistics_scenario(
        name="Test Deliveries",
        description="Test scenario",
        num_drivers=2,
        num_deliveries=10
    )
    assert len(scenario.professionals) == 2
    assert len(scenario.tasks) == 10
    print("  ✓ LogisticsSimulator creates scenarios")

    # Test optimization
    optimization = simulator.optimize_assignments(scenario)
    assert optimization is not None
    assert "routes" in optimization
    assert len(optimization["routes"]) > 0
    print("  ✓ Route optimization works")

    # Test simulation
    simulation = simulator.simulate_day(scenario)
    assert simulation is not None
    assert "completion_score" in simulation
    print("  ✓ Day simulation works")

    print("✅ Logistics simulator tests passed!\n")

def test_retail_simulator():
    """Test retail simulator"""
    print("Testing retail simulator...")

    # Test Customer
    customer = Customer(
        id="customer_001",
        name="Jane Doe"
    )
    assert customer.mood == CustomerMood.NEUTRAL
    assert customer.satisfaction == 0.5
    customer.satisfaction = 0.9
    assert customer.satisfaction == 0.9
    print("  ✓ Customer works")

    # Test Product
    product = Product(
        id="product_001",
        name="Laptop",
        price=999.99,
        stock_quantity=10,
        category="Electronics"
    )
    assert product.id == "product_001"
    assert product.price == 999.99
    print("  ✓ Product works")

    # Test Store
    store = Store(
        id="store_001",
        name="Electronics Plus",
        store_type="electronics",
        coordinates=(0.0, 0.0)
    )
    assert store.id == "store_001"
    assert store.location_type == "electronics"
    print("  ✓ Store works")

    # Test RetailSimulator
    simulator = RetailSimulator()
    scenario = simulator.create_retail_scenario(
        name="Saturday Shopping",
        description="Test scenario",
        num_agents=3,
        num_customers=20,
        num_products=15,
        store_type="retail"
    )
    assert len(scenario.professionals) == 3
    print("  ✓ RetailSimulator creates scenarios")

    # Test shift simulation
    report = simulator.simulate_shift(scenario, shift_duration=480)
    assert report is not None
    assert "completion_score" in report
    assert "tasks" in report
    print("  ✓ Shift simulation works")

    print("✅ Retail simulator tests passed!\n")

def main():
    """Run all tests"""
    print("="*80)
    print("Professional Simulator Manual Tests")
    print("="*80)
    print()

    try:
        test_base_framework()
        test_logistics_simulator()
        test_retail_simulator()

        print("="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
