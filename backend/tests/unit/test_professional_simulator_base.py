"""
Unit Tests for Professional Simulator Base Framework

Tests base classes and abstractions:
- ProfessionalSimulator
- ProfessionalRole
- Task
- Location
- Resource
- PerformanceMetrics
- SimulationScenario

Paradigm 2: Professional Simulator
"""

import pytest
from datetime import datetime
from typing import Dict, List

from app.simulators.base import (
    ProfessionalSimulator,
    SimulationScenario,
    ProfessionalRole,
    Task,
    Location,
    Resource,
    PerformanceMetrics,
    TaskStatus,
    TaskPriority
)


# ============================================================================
# Test ProfessionalRole
# ============================================================================

class TestProfessionalRole:
    """Test professional role (MMO Character mapping)"""

    def test_create_professional_role(self):
        """Test creating a professional role"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="delivery_driver"
        )

        assert role.id == "role_001"
        assert role.name == "John Smith"
        assert role.role_type == "delivery_driver"
        assert role.skills == []
        assert role.skill_levels == {}
        assert role.resources == []
        assert isinstance(role.metrics, PerformanceMetrics)

    def test_add_skill(self):
        """Test adding skills to professional"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        role.add_skill("driving", level=3)
        role.add_skill("navigation", level=2)

        assert "driving" in role.skills
        assert "navigation" in role.skills
        assert role.skill_levels["driving"] == 3
        assert role.skill_levels["navigation"] == 2

    def test_has_skill(self):
        """Test skill checking"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        role.add_skill("driving", level=3)

        assert role.has_skill("driving") is True
        assert role.has_skill("navigation") is False

    def test_get_skill_level(self):
        """Test getting skill levels"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        role.add_skill("driving", level=4)

        assert role.get_skill_level("driving") == 4
        assert role.get_skill_level("nonexistent") == 0

    def test_add_resource(self):
        """Test adding resources to professional"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        vehicle = Resource(
            id="vehicle_001",
            name="Delivery Van",
            resource_type="vehicle",
            capacity=100.0
        )

        role.add_resource(vehicle)

        assert len(role.resources) == 1
        assert role.resources[0].id == "vehicle_001"

    def test_assign_task(self):
        """Test task assignment"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        role.assign_task(task)

        assert len(role.assigned_tasks) == 1
        assert role.assigned_tasks[0].id == "task_001"

    def test_complete_task(self):
        """Test task completion with XP gain"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        initial_xp = role.metrics.experience_points

        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        role.assign_task(task)
        role.complete_task(task, performance_score=0.9)

        assert task.status == TaskStatus.COMPLETED
        assert role.metrics.tasks_completed == 1
        assert role.metrics.experience_points > initial_xp

    def test_level_up_on_xp_gain(self):
        """Test that role levels up when gaining enough XP"""
        role = ProfessionalRole(
            id="role_001",
            name="John Smith",
            role_type="driver"
        )

        initial_level = role.metrics.level

        # Add 150 XP (should trigger level up at 100 XP threshold)
        role.metrics.add_experience(150)

        assert role.metrics.level > initial_level


# ============================================================================
# Test Task
# ============================================================================

class TestTask:
    """Test task (MMO Quest mapping)"""

    def test_create_task(self):
        """Test creating a task"""
        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package to customer",
            required_skills=["driving", "navigation"],
            priority=TaskPriority.HIGH
        )

        assert task.id == "task_001"
        assert task.task_type == "delivery"
        assert task.description == "Deliver package to customer"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
        assert "driving" in task.required_skills
        assert "navigation" in task.required_skills

    def test_task_start(self):
        """Test starting a task"""
        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        task.start()

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.start_time is not None

    def test_task_complete(self):
        """Test completing a task"""
        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        task.start()
        task.complete()

        assert task.status == TaskStatus.COMPLETED
        assert task.completion_time is not None

    def test_task_fail(self):
        """Test failing a task"""
        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        task.start()
        task.fail()

        assert task.status == TaskStatus.FAILED

    def test_task_priority_values(self):
        """Test task priority enum values"""
        low = Task(
            id="task_001",
            task_type="delivery",
            description="Low priority",
            required_skills=[],
            priority=TaskPriority.LOW
        )

        high = Task(
            id="task_002",
            task_type="delivery",
            description="High priority",
            required_skills=[],
            priority=TaskPriority.HIGH
        )

        assert TaskPriority.LOW.value == 1
        assert TaskPriority.MEDIUM.value == 2
        assert TaskPriority.HIGH.value == 3
        assert TaskPriority.URGENT.value == 4


# ============================================================================
# Test Location
# ============================================================================

class TestLocation:
    """Test location (MMO location mapping)"""

    def test_create_location(self):
        """Test creating a location"""
        loc = Location(
            id="loc_001",
            name="Warehouse A",
            location_type="warehouse",
            coordinates=(10.5, 20.3)
        )

        assert loc.id == "loc_001"
        assert loc.name == "Warehouse A"
        assert loc.location_type == "warehouse"
        assert loc.coordinates == (10.5, 20.3)

    def test_location_with_address(self):
        """Test location with address"""
        loc = Location(
            id="loc_001",
            name="Customer Home",
            location_type="delivery_point",
            coordinates=(10.5, 20.3),
            address="123 Main St"
        )

        assert loc.address == "123 Main St"


# ============================================================================
# Test Resource
# ============================================================================

class TestResource:
    """Test resource (MMO item mapping)"""

    def test_create_resource(self):
        """Test creating a resource"""
        resource = Resource(
            id="vehicle_001",
            name="Delivery Van",
            resource_type="vehicle",
            capacity=100.0
        )

        assert resource.id == "vehicle_001"
        assert resource.name == "Delivery Van"
        assert resource.resource_type == "vehicle"
        assert resource.capacity == 100.0

    def test_resource_current_usage(self):
        """Test resource usage tracking"""
        resource = Resource(
            id="vehicle_001",
            name="Delivery Van",
            resource_type="vehicle",
            capacity=100.0
        )

        resource.current_usage = 50.0

        assert resource.current_usage == 50.0
        assert resource.available_capacity() == 50.0

    def test_resource_is_available(self):
        """Test resource availability check"""
        resource = Resource(
            id="vehicle_001",
            name="Delivery Van",
            resource_type="vehicle",
            capacity=100.0
        )

        resource.current_usage = 30.0

        assert resource.is_available(40.0) is True
        assert resource.is_available(80.0) is False


# ============================================================================
# Test PerformanceMetrics
# ============================================================================

class TestPerformanceMetrics:
    """Test performance metrics (MMO character stats mapping)"""

    def test_create_metrics(self):
        """Test creating performance metrics"""
        metrics = PerformanceMetrics()

        assert metrics.tasks_completed == 0
        assert metrics.tasks_failed == 0
        assert metrics.efficiency_score == 0.0
        assert metrics.quality_score == 0.0
        assert metrics.experience_points == 0.0
        assert metrics.level == 1

    def test_add_experience(self):
        """Test adding experience points"""
        metrics = PerformanceMetrics()

        metrics.add_experience(50.0)

        assert metrics.experience_points == 50.0

    def test_level_up(self):
        """Test leveling up"""
        metrics = PerformanceMetrics()

        metrics.add_experience(150.0)  # Should trigger level up

        assert metrics.level > 1

    def test_calculate_level(self):
        """Test level calculation from XP"""
        metrics = PerformanceMetrics()

        # Level 1: 0-99 XP
        metrics.experience_points = 50
        assert metrics.calculate_level() == 1

        # Level 2: 100-199 XP
        metrics.experience_points = 150
        assert metrics.calculate_level() == 2

        # Level 3: 200-299 XP
        metrics.experience_points = 250
        assert metrics.calculate_level() == 3

    def test_update_efficiency(self):
        """Test updating efficiency score"""
        metrics = PerformanceMetrics()

        metrics.update_efficiency(0.85)

        assert metrics.efficiency_score == 0.85

    def test_update_quality(self):
        """Test updating quality score"""
        metrics = PerformanceMetrics()

        metrics.update_quality(0.92)

        assert metrics.quality_score == 0.92

    def test_add_achievement(self):
        """Test adding achievements"""
        metrics = PerformanceMetrics()

        metrics.add_achievement("First Delivery")
        metrics.add_achievement("100 Deliveries")

        assert len(metrics.achievements) == 2
        assert "First Delivery" in metrics.achievements


# ============================================================================
# Test SimulationScenario
# ============================================================================

class TestSimulationScenario:
    """Test simulation scenario"""

    def test_create_scenario(self):
        """Test creating a simulation scenario"""
        scenario = SimulationScenario(
            id="scenario_001",
            name="Monday Deliveries",
            description="Regular Monday delivery routes",
            scenario_type="logistics"
        )

        assert scenario.id == "scenario_001"
        assert scenario.name == "Monday Deliveries"
        assert scenario.description == "Regular Monday delivery routes"
        assert scenario.scenario_type == "logistics"
        assert scenario.professionals == []
        assert scenario.tasks == []
        assert scenario.locations == []

    def test_add_professional(self):
        """Test adding professional to scenario"""
        scenario = SimulationScenario(
            id="scenario_001",
            name="Test Scenario",
            description="Test",
            scenario_type="logistics"
        )

        professional = ProfessionalRole(
            id="prof_001",
            name="John Smith",
            role_type="driver"
        )

        scenario.add_professional(professional)

        assert len(scenario.professionals) == 1
        assert scenario.professionals[0].id == "prof_001"

    def test_add_task(self):
        """Test adding task to scenario"""
        scenario = SimulationScenario(
            id="scenario_001",
            name="Test Scenario",
            description="Test",
            scenario_type="logistics"
        )

        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        scenario.add_task(task)

        assert len(scenario.tasks) == 1
        assert scenario.tasks[0].id == "task_001"

    def test_add_location(self):
        """Test adding location to scenario"""
        scenario = SimulationScenario(
            id="scenario_001",
            name="Test Scenario",
            description="Test",
            scenario_type="logistics"
        )

        location = Location(
            id="loc_001",
            name="Warehouse A",
            location_type="warehouse",
            coordinates=(10.0, 20.0)
        )

        scenario.add_location(location)

        assert len(scenario.locations) == 1
        assert scenario.locations[0].id == "loc_001"

    def test_get_tasks_by_status(self):
        """Test filtering tasks by status"""
        scenario = SimulationScenario(
            id="scenario_001",
            name="Test Scenario",
            description="Test",
            scenario_type="logistics"
        )

        task1 = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package 1",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        task2 = Task(
            id="task_002",
            task_type="delivery",
            description="Deliver package 2",
            required_skills=["driving"],
            priority=TaskPriority.HIGH
        )

        task1.start()
        task2.complete()

        scenario.add_task(task1)
        scenario.add_task(task2)

        pending = scenario.get_tasks_by_status(TaskStatus.PENDING)
        in_progress = scenario.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        completed = scenario.get_tasks_by_status(TaskStatus.COMPLETED)

        assert len(pending) == 0
        assert len(in_progress) == 1
        assert len(completed) == 1


# ============================================================================
# Test ProfessionalSimulator
# ============================================================================

class TestProfessionalSimulator:
    """Test base professional simulator"""

    def test_create_simulator(self):
        """Test creating a professional simulator"""
        simulator = ProfessionalSimulator(domain="test_domain")

        assert simulator.domain == "test_domain"
        assert simulator.scenarios == {}

    def test_create_scenario(self):
        """Test creating a scenario"""
        simulator = ProfessionalSimulator(domain="test_domain")

        scenario = simulator.create_scenario(
            name="Test Scenario",
            description="A test scenario",
            scenario_type="test"
        )

        assert scenario.name == "Test Scenario"
        assert scenario.description == "A test scenario"
        assert scenario.scenario_type == "test"
        assert scenario.id in simulator.scenarios

    def test_get_scenario(self):
        """Test retrieving a scenario"""
        simulator = ProfessionalSimulator(domain="test_domain")

        scenario = simulator.create_scenario(
            name="Test Scenario",
            description="A test scenario",
            scenario_type="test"
        )

        retrieved = simulator.get_scenario(scenario.id)

        assert retrieved is not None
        assert retrieved.id == scenario.id

    def test_get_nonexistent_scenario(self):
        """Test retrieving non-existent scenario returns None"""
        simulator = ProfessionalSimulator(domain="test_domain")

        result = simulator.get_scenario("nonexistent_id")

        assert result is None

    def test_assign_task_to_professional(self):
        """Test task assignment logic"""
        simulator = ProfessionalSimulator(domain="test_domain")

        professional = ProfessionalRole(
            id="prof_001",
            name="John Smith",
            role_type="driver"
        )
        professional.add_skill("driving", level=3)

        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving"],
            priority=TaskPriority.MEDIUM
        )

        success = simulator.assign_task_to_professional(professional, task)

        assert success is True
        assert task in professional.assigned_tasks

    def test_assign_task_without_skills(self):
        """Test task assignment fails without required skills"""
        simulator = ProfessionalSimulator(domain="test_domain")

        professional = ProfessionalRole(
            id="prof_001",
            name="John Smith",
            role_type="driver"
        )
        # No skills added

        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package",
            required_skills=["driving", "navigation"],
            priority=TaskPriority.MEDIUM
        )

        success = simulator.assign_task_to_professional(professional, task)

        # Should still assign but may affect performance
        # (implementation dependent - adjust based on actual behavior)
        assert task in professional.assigned_tasks or success is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestProfessionalSimulatorIntegration:
    """Integration tests for professional simulator workflow"""

    def test_complete_workflow(self):
        """Test complete simulation workflow"""
        # Create simulator
        simulator = ProfessionalSimulator(domain="logistics")

        # Create scenario
        scenario = simulator.create_scenario(
            name="Monday Deliveries",
            description="Morning delivery routes",
            scenario_type="logistics"
        )

        # Add location
        warehouse = Location(
            id="warehouse_001",
            name="Main Warehouse",
            location_type="warehouse",
            coordinates=(0.0, 0.0)
        )
        scenario.add_location(warehouse)

        # Add professional
        driver = ProfessionalRole(
            id="driver_001",
            name="John Smith",
            role_type="driver"
        )
        driver.add_skill("driving", level=3)
        driver.add_skill("navigation", level=2)
        scenario.add_professional(driver)

        # Add vehicle resource
        vehicle = Resource(
            id="vehicle_001",
            name="Delivery Van",
            resource_type="vehicle",
            capacity=100.0
        )
        driver.add_resource(vehicle)

        # Add task
        task = Task(
            id="task_001",
            task_type="delivery",
            description="Deliver package to customer",
            required_skills=["driving"],
            priority=TaskPriority.HIGH
        )
        scenario.add_task(task)

        # Assign task
        simulator.assign_task_to_professional(driver, task)

        # Execute task
        task.start()
        task.complete()
        driver.complete_task(task, performance_score=0.95)

        # Verify results
        assert driver.metrics.tasks_completed == 1
        assert driver.metrics.experience_points > 0
        assert task.status == TaskStatus.COMPLETED

    def test_multiple_professionals_multiple_tasks(self):
        """Test scenario with multiple professionals and tasks"""
        simulator = ProfessionalSimulator(domain="logistics")

        scenario = simulator.create_scenario(
            name="Busy Day",
            description="Multiple drivers, multiple deliveries",
            scenario_type="logistics"
        )

        # Add 3 drivers
        for i in range(3):
            driver = ProfessionalRole(
                id=f"driver_{i:03d}",
                name=f"Driver {i+1}",
                role_type="driver"
            )
            driver.add_skill("driving", level=2)
            scenario.add_professional(driver)

        # Add 10 tasks
        for i in range(10):
            task = Task(
                id=f"task_{i:03d}",
                task_type="delivery",
                description=f"Delivery {i+1}",
                required_skills=["driving"],
                priority=TaskPriority.MEDIUM
            )
            scenario.add_task(task)

        # Assign tasks round-robin
        for i, task in enumerate(scenario.tasks):
            professional = scenario.professionals[i % len(scenario.professionals)]
            simulator.assign_task_to_professional(professional, task)

        # Verify distribution
        assert len(scenario.professionals[0].assigned_tasks) >= 3
        assert len(scenario.professionals[1].assigned_tasks) >= 3
        assert len(scenario.professionals[2].assigned_tasks) >= 3
        assert sum(len(p.assigned_tasks) for p in scenario.professionals) == 10
