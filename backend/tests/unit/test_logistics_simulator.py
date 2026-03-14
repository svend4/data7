"""
Unit Tests for Logistics Simulator

Tests logistics-specific functionality:
- LogisticsSimulator
- DeliveryDriver
- DeliveryTask
- Warehouse
- Vehicle
- Route
- TSP Integration

Paradigm 2: Professional Simulator - Logistics Domain
"""

import pytest
from typing import List

from app.simulators.logistics_simulator import (
    LogisticsSimulator,
    DeliveryDriver,
    DeliveryTask,
    Warehouse,
    Vehicle,
    Route
)
from app.simulators.base import (
    TaskStatus,
    TaskPriority,
    Location
)


# ============================================================================
# Test Vehicle
# ============================================================================

class TestVehicle:
    """Test vehicle (MMO mount mapping)"""

    def test_create_vehicle(self):
        """Test creating a vehicle"""
        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        assert vehicle.id == "vehicle_001"
        assert vehicle.name == "Delivery Van"
        assert vehicle.vehicle_type == "van"
        assert vehicle.capacity == 100.0
        assert vehicle.speed == 60.0

    def test_vehicle_load_tracking(self):
        """Test vehicle load tracking"""
        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        vehicle.current_load = 40.0

        assert vehicle.current_load == 40.0
        assert vehicle.available_capacity() == 60.0

    def test_vehicle_can_load(self):
        """Test vehicle capacity checking"""
        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        vehicle.current_load = 70.0

        assert vehicle.can_load(20.0) is True
        assert vehicle.can_load(35.0) is False

    def test_vehicle_add_load(self):
        """Test adding load to vehicle"""
        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        success = vehicle.add_load(40.0)

        assert success is True
        assert vehicle.current_load == 40.0

    def test_vehicle_add_load_exceeds_capacity(self):
        """Test adding load that exceeds capacity"""
        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        vehicle.current_load = 90.0
        success = vehicle.add_load(20.0)

        assert success is False
        assert vehicle.current_load == 90.0  # Unchanged


# ============================================================================
# Test Warehouse
# ============================================================================

class TestWarehouse:
    """Test warehouse (MMO city/hub mapping)"""

    def test_create_warehouse(self):
        """Test creating a warehouse"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main Distribution Center",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        assert warehouse.id == "warehouse_001"
        assert warehouse.name == "Main Distribution Center"
        assert warehouse.capacity == 1000.0
        assert warehouse.current_inventory == 0.0

    def test_warehouse_add_inventory(self):
        """Test adding inventory to warehouse"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        success = warehouse.add_inventory(500.0)

        assert success is True
        assert warehouse.current_inventory == 500.0

    def test_warehouse_remove_inventory(self):
        """Test removing inventory from warehouse"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        warehouse.add_inventory(500.0)
        success = warehouse.remove_inventory(200.0)

        assert success is True
        assert warehouse.current_inventory == 300.0

    def test_warehouse_remove_too_much_inventory(self):
        """Test removing more inventory than available"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        warehouse.add_inventory(100.0)
        success = warehouse.remove_inventory(200.0)

        assert success is False
        assert warehouse.current_inventory == 100.0  # Unchanged


# ============================================================================
# Test DeliveryTask
# ============================================================================

class TestDeliveryTask:
    """Test delivery task (MMO quest mapping)"""

    def test_create_delivery_task(self):
        """Test creating a delivery task"""
        pickup = Location(
            id="loc_001",
            name="Warehouse",
            location_type="warehouse",
            coordinates=(0.0, 0.0)
        )

        dropoff = Location(
            id="loc_002",
            name="Customer Address",
            location_type="delivery_point",
            coordinates=(10.0, 15.0)
        )

        task = DeliveryTask(
            id="task_001",
            description="Deliver electronics package",
            pickup_location=pickup,
            dropoff_location=dropoff,
            package_weight=5.0,
            priority=TaskPriority.HIGH
        )

        assert task.id == "task_001"
        assert task.task_type == "delivery"
        assert task.pickup_location == pickup
        assert task.dropoff_location == dropoff
        assert task.package_weight == 5.0
        assert task.priority == TaskPriority.HIGH

    def test_delivery_task_calculate_distance(self):
        """Test calculating delivery distance"""
        pickup = Location(
            id="loc_001",
            name="Warehouse",
            location_type="warehouse",
            coordinates=(0.0, 0.0)
        )

        dropoff = Location(
            id="loc_002",
            name="Customer Address",
            location_type="delivery_point",
            coordinates=(3.0, 4.0)  # 5.0 units away (3-4-5 triangle)
        )

        task = DeliveryTask(
            id="task_001",
            description="Deliver package",
            pickup_location=pickup,
            dropoff_location=dropoff,
            package_weight=5.0,
            priority=TaskPriority.MEDIUM
        )

        distance = task.calculate_distance()

        assert abs(distance - 5.0) < 0.01  # Euclidean distance

    def test_delivery_task_estimate_time(self):
        """Test estimating delivery time"""
        pickup = Location(
            id="loc_001",
            name="Warehouse",
            location_type="warehouse",
            coordinates=(0.0, 0.0)
        )

        dropoff = Location(
            id="loc_002",
            name="Customer Address",
            location_type="delivery_point",
            coordinates=(60.0, 0.0)  # 60 km away
        )

        task = DeliveryTask(
            id="task_001",
            description="Deliver package",
            pickup_location=pickup,
            dropoff_location=dropoff,
            package_weight=5.0,
            priority=TaskPriority.MEDIUM
        )

        # Average speed 60 km/h = 1 km/min
        estimated_time = task.estimate_time(average_speed=60.0)

        # 60 km at 60 km/h = 60 minutes
        assert abs(estimated_time - 60.0) < 0.1


# ============================================================================
# Test DeliveryDriver
# ============================================================================

class TestDeliveryDriver:
    """Test delivery driver (MMO rogue/character mapping)"""

    def test_create_delivery_driver(self):
        """Test creating a delivery driver"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        assert driver.id == "driver_001"
        assert driver.name == "John Smith"
        assert driver.role_type == "delivery_driver"
        assert driver.vehicle == vehicle
        assert driver.home_warehouse == warehouse
        assert driver.has_skill("driving")
        assert driver.has_skill("navigation")

    def test_driver_current_location(self):
        """Test driver location tracking"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        # Initially at home warehouse
        assert driver.current_location == warehouse.location

        # Move to new location
        new_location = Location(
            id="loc_002",
            name="Customer",
            location_type="delivery_point",
            coordinates=(10.0, 15.0)
        )

        driver.move_to(new_location)

        assert driver.current_location == new_location

    def test_driver_load_vehicle(self):
        """Test driver loading vehicle"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        success = driver.load_vehicle(50.0)

        assert success is True
        assert driver.vehicle.current_load == 50.0


# ============================================================================
# Test Route
# ============================================================================

class TestRoute:
    """Test route (MMO quest chain mapping)"""

    def test_create_route(self):
        """Test creating a route"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        route = Route(
            id="route_001",
            driver=driver,
            start_location=warehouse.location
        )

        assert route.id == "route_001"
        assert route.driver == driver
        assert route.start_location == warehouse.location
        assert route.tasks == []
        assert route.total_distance == 0.0

    def test_route_add_task(self):
        """Test adding task to route"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        route = Route(
            id="route_001",
            driver=driver,
            start_location=warehouse.location
        )

        task = DeliveryTask(
            id="task_001",
            description="Deliver package",
            pickup_location=warehouse.location,
            dropoff_location=Location(
                id="loc_002",
                name="Customer",
                location_type="delivery_point",
                coordinates=(10.0, 15.0)
            ),
            package_weight=5.0,
            priority=TaskPriority.MEDIUM
        )

        route.add_task(task)

        assert len(route.tasks) == 1
        assert route.tasks[0] == task

    def test_route_calculate_total_distance(self):
        """Test calculating total route distance"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        route = Route(
            id="route_001",
            driver=driver,
            start_location=warehouse.location
        )

        # Add tasks
        task1 = DeliveryTask(
            id="task_001",
            description="Delivery 1",
            pickup_location=warehouse.location,
            dropoff_location=Location(
                id="loc_002",
                name="Customer 1",
                location_type="delivery_point",
                coordinates=(3.0, 4.0)  # 5 units away
            ),
            package_weight=5.0,
            priority=TaskPriority.MEDIUM
        )

        task2 = DeliveryTask(
            id="task_002",
            description="Delivery 2",
            pickup_location=Location(
                id="loc_002",
                name="Customer 1",
                location_type="delivery_point",
                coordinates=(3.0, 4.0)
            ),
            dropoff_location=Location(
                id="loc_003",
                name="Customer 2",
                location_type="delivery_point",
                coordinates=(3.0, 8.0)  # 4 units from previous
            ),
            package_weight=3.0,
            priority=TaskPriority.MEDIUM
        )

        route.add_task(task1)
        route.add_task(task2)

        total_distance = route.calculate_total_distance()

        # Warehouse to Customer 1: 5 units
        # Customer 1 to Customer 2: 4 units
        # Total: 9 units
        assert abs(total_distance - 9.0) < 0.1

    def test_route_estimate_time(self):
        """Test estimating route completion time"""
        warehouse = Warehouse(
            id="warehouse_001",
            name="Main DC",
            location=Location(
                id="loc_001",
                name="Main DC",
                location_type="warehouse",
                coordinates=(0.0, 0.0)
            ),
            capacity=1000.0
        )

        vehicle = Vehicle(
            id="vehicle_001",
            name="Delivery Van",
            vehicle_type="van",
            capacity=100.0,
            speed=60.0  # 60 km/h = 1 km/min
        )

        driver = DeliveryDriver(
            id="driver_001",
            name="John Smith",
            vehicle=vehicle,
            home_warehouse=warehouse
        )

        route = Route(
            id="route_001",
            driver=driver,
            start_location=warehouse.location
        )

        task = DeliveryTask(
            id="task_001",
            description="Delivery",
            pickup_location=warehouse.location,
            dropoff_location=Location(
                id="loc_002",
                name="Customer",
                location_type="delivery_point",
                coordinates=(60.0, 0.0)  # 60 km away
            ),
            package_weight=5.0,
            priority=TaskPriority.MEDIUM
        )

        route.add_task(task)

        estimated_time = route.estimate_completion_time()

        # 60 km at 60 km/h = 60 minutes + service time
        assert estimated_time >= 60.0


# ============================================================================
# Test LogisticsSimulator
# ============================================================================

class TestLogisticsSimulator:
    """Test logistics simulator"""

    def test_create_logistics_simulator(self):
        """Test creating logistics simulator"""
        simulator = LogisticsSimulator()

        assert simulator.domain == "logistics"
        assert simulator.scenarios == {}

    def test_create_logistics_scenario(self):
        """Test creating logistics scenario"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Monday Deliveries",
            description="Regular Monday routes",
            num_drivers=3,
            num_deliveries=15,
            num_warehouses=1
        )

        assert scenario.name == "Monday Deliveries"
        assert scenario.description == "Regular Monday routes"
        assert len(scenario.professionals) == 3  # 3 drivers
        assert len(scenario.tasks) == 15  # 15 deliveries
        # At least 1 warehouse location
        warehouses = [loc for loc in scenario.locations if loc.location_type == "warehouse"]
        assert len(warehouses) >= 1

    def test_logistics_scenario_drivers_have_vehicles(self):
        """Test that all drivers are assigned vehicles"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Test Scenario",
            description="Test",
            num_drivers=5,
            num_deliveries=20,
            num_warehouses=2
        )

        for professional in scenario.professionals:
            driver = professional
            assert isinstance(driver, DeliveryDriver)
            assert driver.vehicle is not None
            assert driver.vehicle.capacity > 0

    def test_logistics_scenario_tasks_have_locations(self):
        """Test that all delivery tasks have pickup and dropoff locations"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Test Scenario",
            description="Test",
            num_drivers=3,
            num_deliveries=10,
            num_warehouses=1
        )

        for task in scenario.tasks:
            delivery_task = task
            assert isinstance(delivery_task, DeliveryTask)
            assert delivery_task.pickup_location is not None
            assert delivery_task.dropoff_location is not None

    def test_optimize_assignments(self):
        """Test route optimization"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Optimization Test",
            description="Test route optimization",
            num_drivers=2,
            num_deliveries=10,
            num_warehouses=1
        )

        optimization_result = simulator.optimize_assignments(scenario)

        assert optimization_result is not None
        assert "routes" in optimization_result
        assert "total_distance" in optimization_result
        assert len(optimization_result["routes"]) == 2  # 2 drivers = 2 routes

    def test_simulate_operations(self):
        """Test simulating logistics operations"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Simulation Test",
            description="Test operations simulation",
            num_drivers=2,
            num_deliveries=8,
            num_warehouses=1
        )

        # First optimize
        simulator.optimize_assignments(scenario)

        # Then simulate
        simulation_result = simulator.simulate_operations(scenario)

        assert simulation_result is not None
        assert "completion_score" in simulation_result
        assert "total_performance" in simulation_result

        # Check that some tasks were completed
        completed_tasks = len([t for t in scenario.tasks if t.status == TaskStatus.COMPLETED])
        assert completed_tasks > 0

    def test_get_performance_report(self):
        """Test getting performance report"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Report Test",
            description="Test performance reporting",
            num_drivers=2,
            num_deliveries=6,
            num_warehouses=1
        )

        # Optimize and simulate
        simulator.optimize_assignments(scenario)
        simulator.simulate_operations(scenario)

        # Get report
        report = simulator.get_performance_report(scenario)

        assert report is not None
        assert "scenario_name" in report
        assert "completion_score" in report
        assert "tasks" in report
        assert "professionals" in report


# ============================================================================
# Integration Tests
# ============================================================================

class TestLogisticsSimulatorIntegration:
    """Integration tests for complete logistics workflow"""

    def test_complete_delivery_workflow(self):
        """Test complete delivery workflow from creation to reporting"""
        # Create simulator
        simulator = LogisticsSimulator()

        # Create scenario
        scenario = simulator.create_logistics_scenario(
            name="Complete Workflow Test",
            description="Full delivery day simulation",
            num_drivers=3,
            num_deliveries=12,
            num_warehouses=2
        )

        # Verify scenario setup
        assert len(scenario.professionals) == 3
        assert len(scenario.tasks) == 12

        # Optimize routes
        optimization = simulator.optimize_assignments(scenario)

        assert optimization is not None
        assert len(optimization["routes"]) == 3
        assert optimization["total_distance"] > 0

        # Simulate operations
        simulation = simulator.simulate_operations(scenario)

        assert simulation is not None
        assert simulation["completion_score"] >= 0
        assert simulation["completion_score"] <= 1.0

        # Get performance report
        report = simulator.get_performance_report(scenario)

        assert report is not None
        assert report["scenario_name"] == "Complete Workflow Test"
        assert "professionals" in report
        assert len(report["professionals"]) == 3

        # Verify drivers gained XP
        for professional_report in report["professionals"]:
            if professional_report["tasks_completed"] > 0:
                # Drivers who completed tasks should have XP
                driver_id = professional_report["id"]
                driver = next(p for p in scenario.professionals if p.id == driver_id)
                assert driver.metrics.experience_points > 0

    def test_tsp_integration(self):
        """Test TSP algorithm integration for route optimization"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="TSP Integration Test",
            description="Test TSP route optimization",
            num_drivers=2,
            num_deliveries=10,
            num_warehouses=1
        )

        # Get unoptimized distance estimate
        total_unoptimized_distance = sum(
            task.calculate_distance()
            for task in scenario.tasks
        )

        # Optimize with TSP
        optimization = simulator.optimize_assignments(scenario)

        # Optimized routes should be more efficient
        optimized_distance = optimization["total_distance"]

        # After optimization, routes should be assigned
        assigned_tasks = sum(len(p.assigned_tasks) for p in scenario.professionals)
        assert assigned_tasks == len(scenario.tasks)

        # Total distance should be reasonable
        assert optimized_distance > 0

    def test_workload_balancing(self):
        """Test that workload is balanced across drivers"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Workload Balance Test",
            description="Test workload distribution",
            num_drivers=3,
            num_deliveries=15,
            num_warehouses=1
        )

        # Optimize
        optimization = simulator.optimize_assignments(scenario)

        # Check task distribution
        task_counts = [len(p.assigned_tasks) for p in scenario.professionals]

        # Each driver should have at least one task
        assert all(count > 0 for count in task_counts)

        # No driver should have more than twice the average
        avg_tasks = sum(task_counts) / len(task_counts)
        assert all(count <= avg_tasks * 2 for count in task_counts)

    def test_multiple_warehouses(self):
        """Test scenario with multiple warehouses"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="Multi-Warehouse Test",
            description="Test with multiple distribution centers",
            num_drivers=4,
            num_deliveries=20,
            num_warehouses=3
        )

        # Should have 3 warehouses
        warehouses = [loc for loc in scenario.locations if loc.location_type == "warehouse"]
        assert len(warehouses) >= 3

        # Each driver should be assigned to a warehouse
        for professional in scenario.professionals:
            driver = professional
            assert driver.home_warehouse is not None

    def test_high_load_scenario(self):
        """Test high-load scenario with many deliveries"""
        simulator = LogisticsSimulator()

        scenario = simulator.create_logistics_scenario(
            name="High Load Test",
            description="Stress test with many deliveries",
            num_drivers=5,
            num_deliveries=50,
            num_warehouses=2
        )

        # Verify all components created
        assert len(scenario.professionals) == 5
        assert len(scenario.tasks) == 50

        # Optimize (should handle large number of tasks)
        optimization = simulator.optimize_assignments(scenario)

        assert optimization is not None
        assert len(optimization["routes"]) == 5

        # All tasks should be assigned
        assigned_tasks = sum(len(p.assigned_tasks) for p in scenario.professionals)
        assert assigned_tasks == 50
